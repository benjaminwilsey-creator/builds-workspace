"""
hardcover-enricher — Cloud Function (Pub/Sub trigger, Gen 2)

Receives a book_id from the nyt-fetcher via Pub/Sub.
Looks up the book in Supabase, queries Hardcover's GraphQL API for metadata,
and updates the books row with description, series info, genres, and tags.

Triggered by: Pub/Sub topic "book-discovered"
"""

import base64
import json
import logging
import os

import functions_framework
import psycopg2
import requests
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HARDCOVER_ENDPOINT = "https://api.hardcover.app/v1/graphql"

# GraphQL query — searches Hardcover by title + author, returns enrichment fields
BOOK_QUERY = """
query SearchBook($query: String!) {
  search(query: $query, query_type: BOOK, per_page: 1) {
    results {
      ... on BookResult {
        book {
          title
          description
          contributions {
            author {
              name
            }
          }
          series_books {
            series {
              name
            }
            position
          }
          book_genres {
            genre {
              name
            }
          }
          taggings {
            tag {
              name
            }
          }
        }
      }
    }
  }
}
"""


def _get_secret(project_id: str, secret_name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


@functions_framework.cloud_event
def main(cloud_event):
    raw = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    message = json.loads(raw)
    book_id = message.get("book_id")

    if not book_id:
        logger.error("No book_id in Pub/Sub message")
        return

    project_id = os.environ["GCP_PROJECT"]

    try:
        supabase_uri = _get_secret(project_id, "SUPABASE_URI")
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return

    conn = psycopg2.connect(supabase_uri)
    try:
        _enrich_book(conn, book_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Enrichment failed for book {book_id}: {e}")
    finally:
        conn.close()


def _enrich_book(conn, book_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT title, author FROM books WHERE id = %s", (book_id,))
        row = cur.fetchone()

    if not row:
        logger.error(f"Book {book_id} not found in database")
        return

    title, author = row
    result = _query_hardcover(f"{title} {author}")

    if not result:
        logger.warning(f"Hardcover returned no results for: {title} — {author}")
        return

    description = result.get("description")

    series_books = result.get("series_books") or []
    series_name = series_books[0]["series"]["name"] if series_books else None
    series_position = series_books[0].get("position") if series_books else None

    genres = [
        g["genre"]["name"]
        for g in (result.get("book_genres") or [])
        if g.get("genre")
    ]
    tags = [
        t["tag"]["name"]
        for t in (result.get("taggings") or [])
        if t.get("tag")
    ]

    genre = genres[0] if genres else None
    aesthetic_tags = tags[:10]  # Cap at 10

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


def _query_hardcover(query: str) -> dict | None:
    try:
        resp = requests.post(
            HARDCOVER_ENDPOINT,
            json={"query": BOOK_QUERY, "variables": {"query": query}},
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
        results = (
            resp.json().get("data", {}).get("search", {}).get("results") or []
        )
        if not results:
            return None
        return results[0].get("book")
    except Exception as e:
        logger.error(f"Hardcover query failed for '{query}': {e}")
        return None
