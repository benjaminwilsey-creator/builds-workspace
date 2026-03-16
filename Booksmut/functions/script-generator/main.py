"""
script-generator — Cloud Function (HTTP trigger, Gen 2)

Reads all CAMPAIGN_DRAFT campaigns for the tenant, generates a script
for each using Gemini, writes script_raw + caption + hashtags, creates
campaign_parts rows, and advances status to SCRIPTED.

Errors are per-campaign — one failure does not stop the rest.

Triggered by: Cloud Scheduler (weekly, Monday 8:15am — after queue-selector)
"""

import json
import logging
import os

import functions_framework
from google import genai
from google.genai import types
import psycopg2
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FTC_DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases. "
MAX_CAPTION_CHARS = 2200
GEMINI_MODEL = "gemini-2.5-flash"


def _get_secret(project_id: str, secret_name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8").strip()


@functions_framework.http
def main(request):
    project_id = os.environ["GCP_PROJECT"]

    try:
        supabase_uri = _get_secret(project_id, "SUPABASE_URI")
        tenant_id = _get_secret(project_id, "TENANT_ID")
        gemini_key = _get_secret(project_id, "GEMINI_API_KEY")
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return ("Secret load failed", 500)

    client = genai.Client(api_key=gemini_key)

    conn = psycopg2.connect(supabase_uri)
    scripted_count = 0
    error_count = 0

    try:
        campaigns = _get_draft_campaigns(conn, tenant_id)
        for campaign_id, book_id, campaign_type, fmt, total_parts in campaigns:
            try:
                book = _get_book_data(conn, book_id)
                script_data = _generate_script(client, book, campaign_type, total_parts)
                _save_script(conn, campaign_id, script_data)
                _create_campaign_parts(conn, campaign_id, script_data)
                conn.commit()
                scripted_count += 1
                logger.info(f"Scripted: {book['title']} (campaign {campaign_id})")
            except Exception as e:
                conn.rollback()
                error_count += 1
                logger.error(f"Script failed for campaign {campaign_id}: {e}")
                _mark_error(conn, campaign_id, str(e))
                conn.commit()
    finally:
        conn.close()

    logger.info(f"Script generator complete. Scripted: {scripted_count}, Errors: {error_count}")
    return (f"Done. Scripted: {scripted_count}, Errors: {error_count}", 200)


def _get_draft_campaigns(conn, tenant_id: str) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.book_id, c.campaign_type, c.format, c.total_parts
            FROM campaigns c
            JOIN books b ON b.id = c.book_id
            WHERE b.tenant_id = %s
              AND c.status = 'CAMPAIGN_DRAFT'
            ORDER BY c.created_at ASC
            """,
            (tenant_id,),
        )
        return cur.fetchall()


def _get_book_data(conn, book_id: str) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT title, author, description, tropes, spice_level,
                   genre, series_name, series_position, score
            FROM books WHERE id = %s
            """,
            (book_id,),
        )
        row = cur.fetchone()
    return {
        "title": row[0],
        "author": row[1],
        "description": row[2] or "",
        "tropes": row[3] or [],
        "spice_level": row[4] or 0,
        "genre": row[5] or "",
        "series_name": row[6],
        "series_position": row[7],
        "score": row[8] or 0,
    }


def _build_prompt(book: dict, campaign_type: str, total_parts: int) -> str:
    tropes_str = ", ".join(book["tropes"][:5]) if book["tropes"] else "not specified"
    spice_labels = {0: "clean", 1: "mild", 2: "low", 3: "medium", 4: "spicy", 5: "very spicy"}
    spice_label = spice_labels.get(book["spice_level"], "unknown")

    series_note = ""
    if book["series_name"]:
        series_note = f"Series: {book['series_name']} (book {book['series_position']}). "

    parts_note = "SINGLE video" if total_parts == 1 else f"MULTIPART series ({total_parts} parts — write all parts, include a cliffhanger between each)"

    return f"""You are a BookTok content creator writing a short-form video script.

Book: "{book['title']}" by {book['author']}
Genre: {book['genre']}
{series_note}Tropes: {tropes_str}
Spice level: {spice_label} ({book['spice_level']}/5)
Description: {book['description'][:500] if book['description'] else 'Not available'}

Campaign type: {campaign_type}
Format: {parts_note}

Return ONLY valid JSON matching this exact structure — no markdown, no explanation:
{{
  "parts": [
    {{
      "part_number": 1,
      "hook": "Opening line — max 12 words, creates curiosity or emotional pull",
      "hook_category": "CURIOSITY_GAP",
      "body": "3-4 sentences. Cover tropes, vibe, why readers are obsessed. Conversational, no spoilers.",
      "cta": "Single action line — e.g. Comment TBR below or Save this for your next read"
    }}
  ],
  "caption": "Start with exactly: As an Amazon Associate I earn from qualifying purchases. Then 2-3 sentences about the book. End with a question to drive comments. Max 2200 chars.",
  "hashtags": ["booktok", "romance", "romantasy"]
}}

Rules:
- hook_category must be one of: CURIOSITY_GAP, IDENTITY_SIGNAL, SOCIAL_PROOF, LOSS_AVERSION, CONTRADICTION
- Hook must be 12 words or fewer
- Caption must begin with the exact FTC disclosure text shown above
- Hashtags: 3-5 tags, lowercase, no # symbol, relevant to this book's genre and tropes
- No spoilers
- Body should sound like an excited human, not a book review
- For MULTIPART: write all {total_parts} parts in the parts array"""


def _generate_script(client, book: dict, campaign_type: str, total_parts: int) -> dict:
    prompt = _build_prompt(book, campaign_type, total_parts)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.9,
        ),
    )
    return json.loads(response.text)


def _save_script(conn, campaign_id: str, script_data: dict) -> None:
    caption = script_data.get("caption", "")[:MAX_CAPTION_CHARS]
    hashtags = script_data.get("hashtags", [])
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE campaigns SET
              script_raw = %s,
              caption    = %s,
              hashtags   = %s,
              status     = 'SCRIPTED',
              updated_at = now()
            WHERE id = %s
            """,
            (json.dumps(script_data), caption, hashtags, campaign_id),
        )


def _create_campaign_parts(conn, campaign_id: str, script_data: dict) -> None:
    parts = script_data.get("parts", [])
    total = len(parts)
    with conn.cursor() as cur:
        for part in parts:
            part_num = part.get("part_number", 1)
            # Multipart non-final parts get a "follow for next" CTA instead
            if total > 1 and part_num < total:
                cta = f"Follow for Part {part_num + 1} 👇"
            else:
                cta = part.get("cta", "Comment TBR 👇")
            cur.execute(
                """
                INSERT INTO campaign_parts
                  (campaign_id, part_number, total_parts, hook, body, cta,
                   hook_text, hook_category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    campaign_id,
                    part_num,
                    total,
                    part.get("hook", ""),
                    part.get("body", ""),
                    cta,
                    part.get("hook", ""),
                    part.get("hook_category", "CURIOSITY_GAP"),
                ),
            )


def _mark_error(conn, campaign_id: str, error: str) -> None:
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
