"""
tts-voicer — Cloud Function (HTTP trigger, Gen 2)

Reads all MODERATION_SCRIPT campaigns for the tenant, generates one MP3
audio file per campaign_part using Google Cloud TTS (WaveNet), uploads
each file to Cloudflare R2, marks each part VOICED, and advances the
campaign to VOICED once all parts are done.

Errors are per-campaign — one failure does not stop the rest.

Triggered by: Cloud Scheduler (weekly, Monday 8:20am — after moderation window)
"""

import logging
import os

import boto3
import functions_framework
import psycopg2
from google.cloud import secretmanager, texttospeech

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TTS_VOICE_NAME = "en-US-Wavenet-F"
TTS_LANGUAGE_CODE = "en-US"
AUDIO_FOLDER = "audio"


def _get_secret(project_id: str, secret_name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8").strip()


@functions_framework.http
def main(request):
    project_id = os.environ["GCP_PROJECT"]
    bucket_name = os.environ["R2_BUCKET_NAME"]
    r2_public_url_base = os.environ["R2_PUBLIC_URL_BASE"].rstrip("/")

    try:
        supabase_uri = _get_secret(project_id, "SUPABASE_URI")
        tenant_id = _get_secret(project_id, "TENANT_ID")
        r2_account_id = _get_secret(project_id, "R2_ACCOUNT_ID")
        r2_access_key = _get_secret(project_id, "R2_ACCESS_KEY_ID")
        r2_secret_key = _get_secret(project_id, "R2_SECRET_ACCESS_KEY")
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return ("Secret load failed", 500)

    tts_client = texttospeech.TextToSpeechClient()
    r2_client = boto3.client(
        "s3",
        endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=r2_access_key,
        aws_secret_access_key=r2_secret_key,
        region_name="auto",
    )

    conn = psycopg2.connect(supabase_uri)
    voiced_count = 0
    error_count = 0

    try:
        campaigns = _get_moderation_script_campaigns(conn, tenant_id)
        logger.info(f"Found {len(campaigns)} campaigns in MODERATION_SCRIPT state")

        for (campaign_id,) in campaigns:
            try:
                parts = _get_campaign_parts(conn, campaign_id)
                for part_id, part_number, hook, body, cta in parts:
                    narration = _build_narration(hook, body, cta)
                    audio_bytes = _synthesize_speech(tts_client, narration)
                    r2_key = f"{AUDIO_FOLDER}/{campaign_id}/part_{part_number}.mp3"
                    _upload_to_r2(r2_client, bucket_name, r2_key, audio_bytes)
                    audio_url = f"{r2_public_url_base}/{r2_key}"
                    _mark_part_voiced(conn, part_id, audio_url)
                    logger.info(f"  Part {part_number} voiced → {r2_key}")

                _mark_campaign_voiced(conn, campaign_id)
                conn.commit()
                voiced_count += 1
                logger.info(f"Voiced campaign {campaign_id} — {len(parts)} part(s)")

            except Exception as e:
                conn.rollback()
                error_count += 1
                logger.error(f"Voice failed for campaign {campaign_id}: {e}")
                _mark_campaign_error(conn, campaign_id, str(e))
                conn.commit()
    finally:
        conn.close()

    logger.info(f"TTS voicer complete. Voiced: {voiced_count}, Errors: {error_count}")
    return (f"Done. Voiced: {voiced_count}, Errors: {error_count}", 200)


def _get_moderation_script_campaigns(conn, tenant_id: str) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id
            FROM campaigns c
            JOIN books b ON b.id = c.book_id
            WHERE b.tenant_id = %s
              AND c.status = 'MODERATION_SCRIPT'
            ORDER BY c.created_at ASC
            """,
            (tenant_id,),
        )
        return cur.fetchall()


def _get_campaign_parts(conn, campaign_id: str) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, part_number, hook, body, cta
            FROM campaign_parts
            WHERE campaign_id = %s
            ORDER BY part_number ASC
            """,
            (campaign_id,),
        )
        return cur.fetchall()


def _build_narration(hook: str, body: str, cta: str) -> str:
    """Combine part fields into natural spoken narration."""
    segments = [s.strip() for s in [hook, body, cta] if s and s.strip()]
    return " ".join(segments)


def _synthesize_speech(client: texttospeech.TextToSpeechClient, text: str) -> bytes:
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=TTS_LANGUAGE_CODE,
        name=TTS_VOICE_NAME,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
    )
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )
    return response.audio_content


def _upload_to_r2(r2_client, bucket: str, key: str, audio_bytes: bytes) -> None:
    r2_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=audio_bytes,
        ContentType="audio/mpeg",
    )


def _mark_part_voiced(conn, part_id: str, audio_url: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE campaign_parts SET
              audio_url  = %s,
              status     = 'VOICED'
            WHERE id = %s
            """,
            (audio_url, part_id),
        )


def _mark_campaign_voiced(conn, campaign_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE campaigns SET
              status     = 'VOICED',
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
