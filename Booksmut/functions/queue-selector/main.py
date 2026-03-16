"""
queue-selector — Cloud Function (HTTP trigger, Gen 2)

Picks the top-scoring SCORED books and creates a Campaign row for each,
ready for script generation.

Books with force_queued=true are always included regardless of score.
Otherwise selects up to TOP_N books by score descending, skipping any
that already have a non-rejected campaign.

Triggered by: Cloud Scheduler (weekly, Monday 8:10am — after scorer)
"""

import logging
import os

import functions_framework
import psycopg2
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Maximum new campaigns to create per weekly run
TOP_N = 5


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
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return ("Secret load failed", 500)

    conn = psycopg2.connect(supabase_uri)
    queued_count = 0

    try:
        books = _select_books(conn, tenant_id)
        for book_id, title in books:
            _create_campaign(conn, book_id)
            _set_book_active(conn, book_id)
            queued_count += 1
            logger.info(f"Queued: {title} (book {book_id})")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Queue selector error: {e}")
        return (f"Queue selector error: {e}", 500)
    finally:
        conn.close()

    logger.info(f"Queue selector complete. Campaigns created: {queued_count}")
    return (f"Done. Campaigns created: {queued_count}", 200)


def _select_books(conn, tenant_id: str) -> list[tuple[str, str]]:
    """Return up to TOP_N books to queue — force_queued first, then top scorers.
    Skips books that already have a non-rejected campaign."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT b.id, b.title
            FROM books b
            WHERE b.tenant_id = %s
              AND b.status = 'SCORED'
              AND NOT EXISTS (
                SELECT 1 FROM campaigns c
                WHERE c.book_id = b.id
                  AND c.status != 'REJECTED'
              )
            ORDER BY b.force_queued DESC, b.score DESC
            LIMIT %s
            """,
            (tenant_id, TOP_N),
        )
        return [(str(row[0]), row[1]) for row in cur.fetchall()]


def _create_campaign(conn, book_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO campaigns
              (book_id, campaign_type, format, total_parts, created_by, trigger_reason)
            VALUES (%s, 'QUICK_TAKE', 'SINGLE', 1, 'SYSTEM', 'auto_queue')
            """,
            (book_id,),
        )


def _set_book_active(conn, book_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE books SET status = 'ACTIVE', updated_at = now() WHERE id = %s",
            (book_id,),
        )
