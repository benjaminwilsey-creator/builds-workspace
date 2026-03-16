# Step 2-1: Deploy the Discovery Pipeline

**Purpose:** Deploy one Cloud Function (`nyt-fetcher`) that automatically finds and enriches
new BookTok books every week. It fetches the NYT Best Sellers lists, writes new books to
Supabase, then immediately enriches each one via the Hardcover API — all in a single run.
You deploy this once and it runs itself every Monday.

**Time:** ~30 minutes

**Prerequisites:**
- Google Cloud CLI installed on your machine (the `gcloud` command)
- Logged in to `gcloud` (`gcloud auth login` if not)
- Your Supabase Session Pooler URI (from Supabase dashboard → Settings → Database → Session Pooler)
- Your tenant UUID (see lookup query below)
- A Hardcover account and API token (hardcover.app → Settings → API)

---

## Find your values before starting

You need four things. Have them ready before running any commands.

**1. Your GCP Project ID**
Go to [console.cloud.google.com](https://console.cloud.google.com) and look at the top bar —
the project name/ID is shown in the project selector. It looks like `reelforge-XXXXXX`.

**2. Your Supabase Session Pooler URI**
- Supabase dashboard → Settings → Database
- Scroll to "Connection string" → select **Session pooler** tab
- Copy the URI — it looks like:
  `postgresql://postgres.PROJECTREF:PASSWORD@aws-0-us-east-2.pooler.supabase.com:5432/postgres`

**3. Your tenant UUID**
Run this in Supabase SQL Editor:
```sql
select id from tenants where name = 'ReelForge';
```
Copy the UUID that comes back.

**4. Your Hardcover API token**
- Log in at hardcover.app → Settings → API
- Copy the Bearer token shown there (it's a long string starting with `eyJ...`)

---

## Step 1 — Set your project

Open a terminal and run:

```bash
gcloud config set project YOUR_GCP_PROJECT_ID
```

Replace `YOUR_GCP_PROJECT_ID` with the project ID you found above.

---

## Step 2 — Enable required APIs

```bash
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com
```

This may take 1–2 minutes. You'll see "Operation finished successfully" when done.

---

## Step 3 — Store your secrets

These commands save your credentials safely in Google Cloud — never in code files.

Run each command separately. Replace the placeholder values with your real ones.

> **Important (Windows users):** Use `printf` not `echo` — and run these in PowerShell
> or Windows Terminal, not Git Bash. If you use Git Bash, `echo -n` may add invisible
> line endings that break authentication.

**NYT API key:**
```bash
printf "YOUR_NYT_API_KEY" | gcloud secrets create NYT_API_KEY --data-file=-
```

**Supabase connection string:**
```bash
printf "YOUR_SUPABASE_SESSION_POOLER_URI" | gcloud secrets create SUPABASE_URI --data-file=-
```

**Tenant UUID:**
```bash
printf "YOUR_TENANT_UUID" | gcloud secrets create TENANT_ID --data-file=-
```

**Hardcover API token:**
```bash
printf "YOUR_HARDCOVER_TOKEN" | gcloud secrets create HARDCOVER_TOKEN --data-file=-
```

---

## Step 4 — Grant the service account access to secrets

The Cloud Function runs as `reelforge-api-runner`. It needs permission to read the secrets.

Replace `YOUR_GCP_PROJECT_ID` with your project ID:

```bash
gcloud secrets add-iam-policy-binding NYT_API_KEY \
  --member="serviceAccount:reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding SUPABASE_URI \
  --member="serviceAccount:reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding TENANT_ID \
  --member="serviceAccount:reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding HARDCOVER_TOKEN \
  --member="serviceAccount:reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Step 5 — Deploy the nyt-fetcher function

Navigate to the repo root first, then deploy:

```bash
cd "e:/Builds - Copy/Booksmut"

gcloud functions deploy nyt-fetcher \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=functions/nyt-fetcher \
  --entry-point=main \
  --trigger-http \
  --no-allow-unauthenticated \
  --service-account=reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=YOUR_GCP_PROJECT_ID \
  --timeout=300s \
  --memory=256Mi
```

This takes 2–3 minutes. When done it will show the function URL — **copy it**, you need it for Step 6.

> **Note:** `--timeout=300s` gives the function 5 minutes to process all three NYT lists and
> enrich each book via the Hardcover API. This is enough headroom for a normal weekly run.

---

## Step 6 — Create the weekly schedule

This tells Cloud Scheduler to fire the nyt-fetcher every Monday at 8am.

Replace `YOUR_NYT_FETCHER_URL` with the URL from Step 5.

```bash
gcloud scheduler jobs create http nyt-weekly-discovery \
  --schedule="0 8 * * 1" \
  --uri="YOUR_NYT_FETCHER_URL" \
  --http-method=POST \
  --oidc-service-account-email=reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com \
  --location=us-central1 \
  --description="Weekly NYT Best Sellers fetch"
```

---

## Step 7 — Test it manually

Run the fetcher once right now to confirm it works end-to-end.
Don't wait until Monday.

```bash
gcloud scheduler jobs run nyt-weekly-discovery --location=us-central1
```

Then check the logs:

```bash
gcloud functions logs read nyt-fetcher --region=us-central1 --limit=50
```

You should see lines like:
- `Enriched book XXXX: Title`
- `NYT fetch complete. New books discovered and enriched: X`

**Then verify in Supabase:**

```sql
-- Should show rows with status ENRICHED
select title, author, genre, status, aesthetic_tags
from books
order by created_at desc
limit 20;
```

---

## If something goes wrong

**"Permission denied" errors** — check that the service account has the Secret Manager role
for all four secrets from Step 4.

**"Secret not found"** — confirm the secret names are exactly `NYT_API_KEY`, `SUPABASE_URI`,
`TENANT_ID`, `HARDCOVER_TOKEN` (case-sensitive).

**"401 Unauthorized" from Hardcover** — the HARDCOVER_TOKEN secret may have invisible line
endings. Delete and recreate it using `printf` (not `echo`), or add a new version:
```bash
printf "YOUR_HARDCOVER_TOKEN" | gcloud secrets versions add HARDCOVER_TOKEN --data-file=-
```

**Books discovered but status stays DISCOVERED** — the Hardcover API returned no results for
those titles. This is normal for very new or obscure books. The `UPDATE` still runs and sets
status to ENRICHED regardless; if Hardcover has no data, the metadata fields are left NULL.

**Supabase connection refused** — make sure you used the Session Pooler URI (port 5432,
`pooler.supabase.com`), not the direct connection string (the direct one doesn't work from GCP).

**Function times out** — increase `--timeout` to `540s` and redeploy. Only likely if the NYT
lists are unusually large or Hardcover is slow.

---

## What's Next

**Step 2-2:** Scorer function — reads ENRICHED books, calculates a score, sets status to SCORED
**Step 2-3:** Queue selector — picks top-scoring books and creates Campaign rows for video generation
