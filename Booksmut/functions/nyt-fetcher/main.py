"""
nyt-fetcher — Cloud Function (HTTP trigger, Gen 2)

Fetches the NYT Best Sellers lists, writes new books to Supabase,
then immediately enriches each new book via the Hardcover API.

Triggered by: Cloud Scheduler (weekly, Monday 8am)
"""

import json
import logging
import os

import functions_framework
import psycopg2
import requests
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NYT Best Sellers list slugs to fetch each week
NYT_LISTS = [
    "hardcover-fiction",
    "combined-print-and-e-book-fiction",
    "young-adult-hardcover",
]

# Signal strength: rank 1 = 19 points, rank 20 = 0 points
MAX_RANK_SIGNAL = 20

HARDCOVER_ENDPOINT = "https://api.hardcover.app/v1/graphql"

# results is a JSON scalar — Typesense response with hits[0].document
BOOK_QUERY = """
query SearchBook($query: String!) {
  search(query: $query, query_type: "BOOK", per_page: 1) {
    results
  }
}
"""


def _get_secret(project_id: str, secret_name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8").strip()


@functions_framework.http
def main(request):
    project_id = os.environ["GCP_PROJECT"]

    try:
        nyt_api_key = _get_secret(project_id, "NYT_API_KEY")
        supabase_uri = _get_secret(project_id, "SUPABASE_URI")
        tenant_id = _get_secret(project_id, "TENANT_ID")
        hardcover_token = _get_secret(project_id, "HARDCOVER_TOKEN")
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return ("Secret load failed", 500)

    conn = psycopg2.connect(supabase_uri)
    total_new = 0

    try:
        for list_name in NYT_LISTS:
            new_count = _process_list(
                list_name, nyt_api_key, tenant_id, hardcover_token, conn
            )
            total_new += new_count
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Pipeline error: {e}")
        return (f"Pipeline error: {e}", 500)
    finally:
        conn.close()

    logger.info(f"NYT fetch complete. New books discovered and enriched: {total_new}")
    return (f"Done. New books: {total_new}", 200)


def _process_list(
    list_name: str,
    api_key: str,
    tenant_id: str,
    hardcover_token: str,
    conn,
) -> int:
    url = f"https://api.nytimes.com/svc/books/v3/lists/current/{list_name}.json"
    resp = requests.get(url, params={"api-key": api_key}, timeout=10)
    resp.raise_for_status()

    books = resp.json().get("results", {}).get("books", [])
    new_count = 0

    for book in books:
        isbn = book.get("primary_isbn13") or book.get("primary_isbn10")
        title = book.get("title", "").strip().title()
        author = book.get("author", "").strip()
        rank = book.get("rank")

        if not title or not author:
            continue

        book_id = _upsert_book(conn, tenant_id, title, author, isbn)
        if book_id:
            signal = max(0, MAX_RANK_SIGNAL - (rank or MAX_RANK_SIGNAL))
            _insert_book_source(conn, book_id, list_name, rank, signal)
            _enrich_book(conn, book_id, title, author, hardcover_token)
            new_count += 1

    return new_count


def _upsert_book(
    conn, tenant_id: str, title: str, author: str, isbn: str | None
) -> str | None:
    """Insert book if not already present. Return new book_id, or None if duplicate."""
    with conn.cursor() as cur:
        if isbn:
            cur.execute(
                "SELECT id FROM books WHERE tenant_id = %s AND isbn = %s",
                (tenant_id, isbn),
            )
        else:
            cur.execute(
                """SELECT id FROM books
                   WHERE tenant_id = %s
                     AND lower(title) = lower(%s)
                     AND lower(author) = lower(%s)""",
                (tenant_id, title, author),
            )
        if cur.fetchone():
            return None  # Already in database

        cur.execute(
            """INSERT INTO books (tenant_id, isbn, title, author, status)
               VALUES (%s, %s, %s, %s, 'DISCOVERED')
               RETURNING id""",
            (tenant_id, isbn, title, author),
        )
        return str(cur.fetchone()[0])


def _insert_book_source(
    conn, book_id: str, list_name: str, rank: int | None, signal: int
) -> None:
    source_label = f"NYT_{list_name.upper().replace('-', '_')}"
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO book_sources (book_id, source, rank, signal_strength)
               VALUES (%s, %s, %s, %s)""",
            (book_id, source_label, rank, signal),
        )


def _enrich_book(
    conn, book_id: str, title: str, author: str, hardcover_token: str
) -> None:
    result = _query_hardcover(f"{title} {author}", hardcover_token)

    if not result:
        logger.warning(f"Hardcover returned no results for: {title} — {author}")
        return

    description = result.get("description")

    featured_series = result.get("featured_series")
    series_name = featured_series["series"]["name"] if featured_series else None
    series_position = featured_series.get("position") if featured_series else None

    genres = result.get("genres") or []
    genre = genres[0] if genres else None

    tags = result.get("tags") or []
    aesthetic_tags = tags[:10]

    with conn.cursor() as cur:
        cur.execute(
            """UPDATE books SET
                 description     = COALESCE(description, %s),
                 series_name     = COALESCE(series_name, %s),
                 series_position = COALESCE(series_position, %s),
                 genre           = COALESCE(genre, %s),
                 aesthetic_tags  = COALESCE(aesthetic_tags, %s),
                 status          = 'ENRICHED',
                 updated_at      = now()
               WHERE id = %s""",
            (description, series_name, series_position, genre, aesthetic_tags, book_id),
        )

    logger.info(f"Enriched book {book_id}: {title}")


def _query_hardcover(query: str, token: str) -> dict | None:
    try:
        resp = requests.post(
            HARDCOVER_ENDPOINT,
            json={"query": BOOK_QUERY, "variables": {"query": query}},
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {token}",
            },
            timeout=15,
        )
        resp.raise_for_status()
        results = resp.json().get("data", {}).get("search", {}).get("results") or {}
        hits = results.get("hits") or []
        if not hits:
            return None
        return hits[0].get("document")
    except Exception as e:
        logger.error(f"Hardcover query failed for '{query}': {e}")
        return None
