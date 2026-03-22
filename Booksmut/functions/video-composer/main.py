"""
video-composer — Cloud Function (HTTP trigger, Gen 2)

Reads VOICED campaigns for the tenant, composes one 30-second MP4 per
campaign_part using FFmpeg, uploads each file to Cloudflare R2, marks
parts COMPOSED, and advances the campaign to COMPOSED.

Background source is resolved per part from background_type:
  user_uploaded  -> custom_video_url on campaign_parts
  cover_only     -> cover_image_url from books table (Ken Burns zoom)
  setting_video  -> custom_video_url (backdrop clip)
  (null/other)   -> solid dark gradient fallback (no file needed)

Text overlays:
  0:00-0:08  Hook text
  0:08-0:20  Tropes (up to 3, stacked)
  0:25-0:30  CTA text
  top-left   Part badge for multipart campaigns

Request body (optional JSON):
  { "campaign_id": "uuid" }  -- compose only this campaign
  (empty)                    -- compose all VOICED campaigns

Triggered by: UI "Compose Now" button or Cloud Scheduler.
"""

import logging
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import boto3
import functions_framework
import psycopg2
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

VIDEO_WIDTH    = 1080
VIDEO_HEIGHT   = 1920
VIDEO_FPS      = 30
VIDEO_DURATION = 30
VIDEO_FOLDER   = "video"

TROPE_Y_POSITIONS = [0.38, 0.47, 0.56]


def _get_secret(project_id: str, secret_name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8").strip()


def _escape_drawtext(text: str) -> str:
    """Escape special characters for FFmpeg drawtext filter."""
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    text = text.replace(":", "\\:")
    text = text.replace(",", "\\,")
    return text


@functions_framework.http
def main(request):
    # Allow CORS preflight from the moderation UI
    if request.method == "OPTIONS":
        return ("", 204, {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET",
            "Access-Control-Allow-Headers": "Content-Type",
        })

    project_id       = os.environ["GCP_PROJECT"]
    bucket_name      = os.environ["R2_BUCKET_NAME"]
    r2_public_url_base = os.environ["R2_PUBLIC_URL_BASE"].rstrip("/")

    # Optional: compose only a specific campaign
    body        = request.get_json(silent=True) or {}
    campaign_id_filter = body.get("campaign_id")

    try:
        supabase_uri = _get_secret(project_id, "SUPABASE_URI")
        tenant_id    = _get_secret(project_id, "TENANT_ID")
        r2_account_id = _get_secret(project_id, "R2_ACCOUNT_ID")
        r2_access_key = _get_secret(project_id, "R2_ACCESS_KEY_ID")
        r2_secret_key = _get_secret(project_id, "R2_SECRET_ACCESS_KEY")
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return ("Secret load failed", 500, {"Access-Control-Allow-Origin": "*"})

    r2_client = boto3.client(
        "s3",
        endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=r2_access_key,
        aws_secret_access_key=r2_secret_key,
        region_name="auto",
    )

    conn = psycopg2.connect(supabase_uri)
    composed_count = 0
    error_count    = 0

    try:
        campaigns = _get_voiced_campaigns(conn, tenant_id, campaign_id_filter)
        logger.info(f"Found {len(campaigns)} campaigns to compose")

        for campaign_id, cover_image_url, tropes in campaigns:
            try:
                parts       = _get_campaign_parts(conn, campaign_id)
                total_parts = len(parts)

                for (part_id, part_number, hook, cta,
                     audio_url, background_type, custom_video_url,
                     music_track_id) in parts:

                    music_url = _get_music_url(conn, music_track_id) if music_track_id else None

                    with tempfile.TemporaryDirectory() as tmpdir:
                        video_path = _compose_part(
                            tmpdir=Path(tmpdir),
                            part_number=part_number,
                            total_parts=total_parts,
                            hook=hook,
                            cta=cta,
                            tropes=tropes or [],
                            audio_url=audio_url,
                            background_type=background_type,
                            custom_video_url=custom_video_url,
                            cover_image_url=cover_image_url,
                            music_url=music_url,
                        )
                        r2_key    = f"{VIDEO_FOLDER}/{campaign_id}/part_{part_number}.mp4"
                        _upload_to_r2(r2_client, bucket_name, r2_key, video_path)
                        video_url = f"{r2_public_url_base}/{r2_key}"
                        _mark_part_composed(conn, part_id, video_url)
                        logger.info(f"  Part {part_number} composed -> {r2_key}")

                _mark_campaign_composed(conn, campaign_id)
                conn.commit()
                composed_count += 1
                logger.info(f"Composed campaign {campaign_id} — {total_parts} part(s)")

            except Exception as e:
                conn.rollback()
                error_count += 1
                logger.error(f"Compose failed for campaign {campaign_id}: {e}")
                _mark_campaign_error(conn, campaign_id, str(e))
                conn.commit()
    finally:
        conn.close()

    msg = f"Done. Composed: {composed_count}, Errors: {error_count}"
    logger.info(msg)
    return (msg, 200, {"Access-Control-Allow-Origin": "*"})


# ── Database helpers ──────────────────────────────────────────────────────────

def _get_voiced_campaigns(
    conn, tenant_id: str, campaign_id_filter: str | None
) -> list[tuple]:
    sql = """
        SELECT c.id, b.cover_image_url, b.tropes
        FROM campaigns c
        JOIN books b ON b.id = c.book_id
        WHERE b.tenant_id = %s
          AND c.status = 'VOICED'
    """
    params: list = [tenant_id]
    if campaign_id_filter:
        sql += " AND c.id = %s"
        params.append(campaign_id_filter)
    sql += " ORDER BY c.created_at ASC"
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def _get_campaign_parts(conn, campaign_id: str) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, part_number, hook, cta,
                   audio_url, background_type, custom_video_url, music_track_id
            FROM campaign_parts
            WHERE campaign_id = %s
            ORDER BY part_number ASC
            """,
            (campaign_id,),
        )
        return cur.fetchall()


def _get_music_url(conn, music_track_id: str) -> str | None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT file_url FROM music_library WHERE id = %s",
            (music_track_id,),
        )
        row = cur.fetchone()
        return row[0] if row else None


def _mark_part_composed(conn, part_id: str, video_url: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE campaign_parts SET
              video_url = %s,
              status    = 'COMPOSED'
            WHERE id = %s
            """,
            (video_url, part_id),
        )


def _mark_campaign_composed(conn, campaign_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE campaigns SET
              status     = 'COMPOSED',
              updated_at = now()
            WHERE id = %s
            """,
            (campaign_id,),
        )


def _mark_campaign_error(conn, campaign_id: str, error: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE campaigns SET
              retry_count = retry_count + 1,
              last_error  = %s,
              updated_at  = now()
            WHERE id = %s
            """,
            (error[:500], campaign_id),
        )


# ── Composition ───────────────────────────────────────────────────────────────

def _compose_part(
    tmpdir: Path,
    part_number: int,
    total_parts: int,
    hook: str,
    cta: str,
    tropes: list[str],
    audio_url: str,
    background_type: str | None,
    custom_video_url: str | None,
    cover_image_url: str | None,
    music_url: str | None,
) -> Path:
    """Download assets, run FFmpeg, return path to rendered MP4."""
    audio_path = tmpdir / "voiceover.mp3"
    _download(audio_url, audio_path)

    music_path = None
    if music_url:
        music_path = tmpdir / "music.mp3"
        _download(music_url, music_path)

    bg_path, is_image = _resolve_background(
        tmpdir, background_type, custom_video_url, cover_image_url
    )

    output_path = tmpdir / "output.mp4"
    _run_ffmpeg(
        bg_path=bg_path,
        is_image=is_image,
        audio_path=audio_path,
        music_path=music_path,
        output_path=output_path,
        hook=hook,
        cta=cta,
        tropes=tropes[:3],
        part_number=part_number,
        total_parts=total_parts,
    )
    return output_path


def _resolve_background(
    tmpdir: Path,
    background_type: str | None,
    custom_video_url: str | None,
    cover_image_url: str | None,
) -> tuple[Path | None, bool]:
    """
    Returns (path_or_None, is_image).
    path_or_None is None when using the gradient fallback (no file needed).
    is_image=True triggers Ken Burns treatment; False means video source.
    """
    if background_type in ("user_uploaded", "setting_video") and custom_video_url:
        bg_path = tmpdir / "background.mp4"
        _download(custom_video_url, bg_path)
        return bg_path, False

    if background_type == "cover_only" and cover_image_url:
        ext = cover_image_url.rsplit(".", 1)[-1].split("?")[0] or "jpg"
        bg_path = tmpdir / f"cover.{ext}"
        _download(cover_image_url, bg_path)
        return bg_path, True

    # Fallback: solid dark gradient — no file needed
    return None, False


def _build_filter_complex(
    is_image: bool,
    has_bg_file: bool,
    vo_index: int,
    mu_index: int | None,
    hook: str,
    cta: str,
    tropes: list[str],
    part_number: int,
    total_parts: int,
) -> tuple[str, str, str]:
    """
    Build the FFmpeg filter_complex string.
    Returns (filter_complex, vout_label, aout_label).
    """
    parts = []

    # ── Background ────────────────────────────────────────────────────────────
    if not has_bg_file:
        # Solid dark gradient
        parts.append(
            f"[0:v] fps={VIDEO_FPS},"
            f"trim=0:{VIDEO_DURATION},setpts=PTS-STARTPTS [bg]"
        )
    elif is_image:
        # Ken Burns slow zoom toward center
        zoom_frames = VIDEO_DURATION * VIDEO_FPS
        parts.append(
            f"[0:v] scale={VIDEO_WIDTH + 200}:{VIDEO_HEIGHT + 400},"
            f"zoompan=z='min(zoom+0.0004\\,1.3)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={zoom_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS},"
            f"setsar=1 [bg]"
        )
    else:
        # Video: scale to fill, crop to exact resolution
        parts.append(
            f"[0:v] scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:"
            f"force_original_aspect_ratio=increase,"
            f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},"
            f"setsar=1,fps={VIDEO_FPS},"
            f"trim=0:{VIDEO_DURATION},setpts=PTS-STARTPTS [bg]"
        )

    # ── Text overlay chain ────────────────────────────────────────────────────
    current  = "bg"
    vi       = 0

    def next_v() -> str:
        nonlocal vi
        label = f"v{vi}"
        vi += 1
        return label

    def add_text(src: str, text: str, font: str, size: int,
                 y_frac: float, t_start: float, t_end: float) -> str:
        escaped = _escape_drawtext(text)
        if not escaped:
            return src
        dst = next_v()
        parts.append(
            f"[{src}] drawtext="
            f"fontfile={font}:"
            f"text='{escaped}':"
            f"fontsize={size}:fontcolor=white:"
            f"x=(w-tw)/2:y=h*{y_frac}:"
            f"enable='between(t\\,{t_start}\\,{t_end})':"
            f"box=1:boxcolor=black@0.55:boxborderw=12 [{dst}]"
        )
        return dst

    # Hook (0–8s)
    current = add_text(current, hook or "", FONT_BOLD, 68, 0.15, 0.0, 8.0)

    # Tropes (8–20s)
    for i, trope in enumerate(tropes):
        y = TROPE_Y_POSITIONS[i] if i < len(TROPE_Y_POSITIONS) else 0.56
        current = add_text(current, trope, FONT_REGULAR, 46, y, 8.0, 20.0)

    # CTA (25–30s)
    current = add_text(current, cta or "", FONT_BOLD, 62, 0.78, 25.0, 30.0)

    # Part badge top-left (always visible, multipart only)
    if total_parts > 1:
        badge   = f"Part {part_number} of {total_parts}"
        escaped = _escape_drawtext(badge)
        dst     = next_v()
        parts.append(
            f"[{current}] drawtext="
            f"fontfile={FONT_REGULAR}:"
            f"text='{escaped}':"
            f"fontsize=38:fontcolor=white:"
            f"x=30:y=50:"
            f"box=1:boxcolor=black@0.5:boxborderw=8 [{dst}]"
        )
        current = dst

    vout_label = current

    # ── Audio ─────────────────────────────────────────────────────────────────
    parts.append(
        f"[{vo_index}:a] volume=1.0,"
        f"atrim=0:{VIDEO_DURATION},asetpts=PTS-STARTPTS [vo]"
    )

    if mu_index is not None:
        parts.append(
            f"[{mu_index}:a] volume=0.12,"
            f"atrim=0:{VIDEO_DURATION},asetpts=PTS-STARTPTS [mu]"
        )
        parts.append("[vo][mu] amix=inputs=2:duration=first [aout]")
        aout_label = "aout"
    else:
        aout_label = "vo"

    return "; ".join(parts), vout_label, aout_label


def _run_ffmpeg(
    bg_path: Path | None,
    is_image: bool,
    audio_path: Path,
    music_path: Path | None,
    output_path: Path,
    hook: str,
    cta: str,
    tropes: list[str],
    part_number: int,
    total_parts: int,
) -> None:
    """Build and execute the FFmpeg command."""
    inputs: list[str] = []

    # Input 0: background
    if bg_path is None:
        inputs += [
            "-f", "lavfi",
            "-i", f"color=c=#1a0a2e:size={VIDEO_WIDTH}x{VIDEO_HEIGHT}:rate={VIDEO_FPS}",
        ]
    elif is_image:
        inputs += ["-loop", "1", "-i", str(bg_path)]
    else:
        inputs += ["-i", str(bg_path)]

    # Input 1: voiceover
    inputs += ["-i", str(audio_path)]
    vo_index = 1

    # Input 2: music (optional)
    mu_index = None
    if music_path:
        inputs += ["-i", str(music_path)]
        mu_index = 2

    filter_complex, vout_label, aout_label = _build_filter_complex(
        is_image=is_image,
        has_bg_file=bg_path is not None,
        vo_index=vo_index,
        mu_index=mu_index,
        hook=hook,
        cta=cta,
        tropes=tropes,
        part_number=part_number,
        total_parts=total_parts,
    )

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", f"[{vout_label}]",
        "-map", f"[{aout_label}]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        "-t", str(VIDEO_DURATION),
        "-movflags", "+faststart",
        str(output_path),
    ]

    logger.info(f"Running FFmpeg for part {part_number}...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=540)

    if result.returncode != 0:
        logger.error(f"FFmpeg stderr: {result.stderr[-3000:]}")
        raise RuntimeError(f"FFmpeg failed (code {result.returncode})")

    size_mb = output_path.stat().st_size / 1_000_000
    logger.info(f"FFmpeg complete — {size_mb:.1f} MB")


# ── File helpers ──────────────────────────────────────────────────────────────

def _download(url: str, dest: Path) -> None:
    urllib.request.urlretrieve(url, dest)


def _upload_to_r2(r2_client, bucket: str, key: str, file_path: Path) -> None:
    with open(file_path, "rb") as f:
        r2_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=f,
            ContentType="video/mp4",
        )
