Step 2 — Deploy r2-presign


cd "c:\Users\benja\OneDrive\Documents\Builds\Booksmut\functions\r2-presign"

gcloud functions deploy r2-presign --gen2 --runtime=python312 --region=us-central1 --source=. --entry-point=main --trigger-http --allow-unauthenticated --timeout=30s

gcloud run services update r2-presign --region=us-central1 --update-env-vars "GCP_PROJECT=project-fa5cd39b-46df-4f2a-808"

gcloud run services update r2-presign --region=us-central1 --update-env-vars "R2_BUCKET_NAME=booksmut-videos"

gcloud run services update r2-presign --region=us-central1 --update-env-vars "R2_PUBLIC_URL_BASE=https://pub-8352f6299ee54879bb0e492bc9e8b662.r2.dev"
Step 3 — Update R2 CORS to allow PUT uploads

Go to Cloudflare dashboard → R2 → booksmut-videos → Settings → CORS Policy. Replace the current policy with:


[
  {
    "AllowedOrigins": ["https://benjaminwilsey-creator.github.io"],
    "AllowedMethods": ["GET", "PUT"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
Step 4 — Fill in the function URLs in index.html

After both deploys complete they'll each print a Service URL. Paste those into docs/index.html at lines:


const COMPOSER_URL = 'PASTE_VIDEO_COMPOSER_URL_HERE';
const PRESIGN_URL  = 'PASTE_R2_PRESIGN_URL_HERE';
Step 5 — Push to GitHub

In Git Bash — from e:\Builds - Copy:


git add docs/index.html && git commit -m "feat: add Video Compose tab with upload and compose now" && git push
Start with Step 1 and paste the output — I'll watch for any deploy errors.