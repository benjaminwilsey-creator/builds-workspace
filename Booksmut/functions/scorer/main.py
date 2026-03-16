"""
scorer — Cloud Function (HTTP trigger, Gen 2)

Reads all ENRICHED books for the tenant, calculates a score from
NYT signal strength, writes the score back and sets status to SCORED.

Triggered by: Cloud Scheduler (weekly, Monday 8:05am — after nyt-fetcher)
"""

import json
import logging
import os

import functions_framework
import psycopg2
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    scored_count = 0

    try:
        book_ids = _get_enriched_books(conn, tenant_id)
        for book_id in book_ids:
            _score_book(conn, book_id)
            scored_count += 1
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Scorer error: {e}")
        return (f"Scorer error: {e}", 500)
    finally:
        conn.close()

    logger.info(f"Scorer complete. Books scored: {scored_count}")
    return (f"Done. Books scored: {scored_count}", 200)


def _get_enriched_books(conn, tenant_id: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM books WHERE tenant_id = %s AND status = 'ENRICHED'",
            (tenant_id,),
        )
        return [str(row[0]) for row in cur.fetchall()]


def _score_book(conn, book_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT source, rank, signal_strength FROM book_sources WHERE book_id = %s",
            (book_id,),
        )
        sources = cur.fetchall()

    source_details = [
        {"source": row[0], "rank": row[1], "signal": row[2] or 0}
        for row in sources
    ]
    nyt_signal = sum(row[2] or 0 for row in sources)

    score_breakdown = {
        "nyt_signal": nyt_signal,
        "sources": source_details,
    }

    with conn.cursor() as cur:
        cur.execute(
            """UPDATE books SET
                 score           = %s,
                 score_breakdown = %s,
                 status          = 'SCORED',
                 updated_at      = now()
               WHERE id = %s""",
            (nyt_signal, json.dumps(score_breakdown), book_id),
        )

    logger.info(f"Scored book {book_id}: {nyt_signal} points ({len(sources)} source(s))")
