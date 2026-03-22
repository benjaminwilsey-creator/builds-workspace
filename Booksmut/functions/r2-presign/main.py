"""
r2-presign — Cloud Function (HTTP trigger, Gen 2)

Generates a short-lived presigned PUT URL so the browser can upload a
background video directly to Cloudflare R2 without routing the file
through this Cloud Function.

Request body (JSON):
  { "campaign_id": "uuid", "filename": "my_video.mp4" }

Response (JSON):
  {
    "presigned_url": "https://...r2.cloudflarestorage.com/...",
    "public_url":    "https://pub-xxx.r2.dev/uploads/...",
    "r2_key":        "uploads/{campaign_id}/{filename}"
  }

The browser uploads with:
  PUT {presigned_url}
  Content-Type: video/mp4
  Body: file bytes

After upload succeeds, the browser updates Supabase:
  campaign_parts.custom_video_url = public_url
  campaign_parts.background_type  = 'user_uploaded'

URL expires after 1 hour.
"""

import json
import logging
import os

import boto3
import functions_framework
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

UPLOAD_FOLDER  = "uploads"
URL_EXPIRY_SEC = 3600


def _get_secret(project_id: str, secret_name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8").strip()


@functions_framework.http
def main(request):
    if request.method == "OPTIONS":
        return ("", 204, CORS_HEADERS)

    if request.method != "POST":
        return (json.dumps({"error": "POST required"}), 405, CORS_HEADERS)

    body = request.get_json(silent=True) or {}
    campaign_id = body.get("campaign_id", "").strip()
    filename    = body.get("filename", "video.mp4").strip()

    if not campaign_id:
        return (json.dumps({"error": "campaign_id required"}), 400, CORS_HEADERS)

    # Sanitise filename — only allow alphanumeric, dash, underscore, dot
    safe_filename = "".join(
        c for c in filename if c.isalnum() or c in "-_."
    ) or "video.mp4"

    project_id = os.environ["GCP_PROJECT"]
    bucket_name = os.environ["R2_BUCKET_NAME"]
    r2_public_url_base = os.environ["R2_PUBLIC_URL_BASE"].rstrip("/")

    try:
        r2_account_id = _get_secret(project_id, "R2_ACCOUNT_ID")
        r2_access_key = _get_secret(project_id, "R2_ACCESS_KEY_ID")
        r2_secret_key = _get_secret(project_id, "R2_SECRET_ACCESS_KEY")
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return (json.dumps({"error": "Secret load failed"}), 500, CORS_HEADERS)

    r2_client = boto3.client(
        "s3",
        endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=r2_access_key,
        aws_secret_access_key=r2_secret_key,
        region_name="auto",
    )

    r2_key = f"{UPLOAD_FOLDER}/{campaign_id}/{safe_filename}"

    try:
        presigned_url = r2_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name,
                "Key": r2_key,
                "ContentType": "video/mp4",
            },
            ExpiresIn=URL_EXPIRY_SEC,
        )
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        return (json.dumps({"error": str(e)}), 500, CORS_HEADERS)

    public_url = f"{r2_public_url_base}/{r2_key}"
    logger.info(f"Presigned URL generated for campaign {campaign_id} -> {r2_key}")

    return (
        json.dumps({
            "presigned_url": presigned_url,
            "public_url": public_url,
            "r2_key": r2_key,
        }),
        200,
        {**CORS_HEADERS, "Content-Type": "application/json"},
    )
