# Step 2-2: Deploy the Scorer

**Purpose:** Deploy one Cloud Function (`scorer`) that reads all enriched books and
calculates a score for each one. Books with higher NYT ranks (closer to #1) get higher
scores. The score determines which books get turned into videos.

**Time:** ~15 minutes

**Prerequisites:**
- Step 2-1 complete (nyt-fetcher deployed, books in Supabase with status ENRICHED)
- Same GCP project and service account as Step 2-1

---

## How scoring works

Each book has one or more entries in `book_sources` — one per NYT list it appeared on.
Each entry has a `signal_strength` value already calculated:
- Rank 1 = 19 points
- Rank 2 = 18 points
- ...
- Rank 20 = 0 points

The scorer sums all signal_strength values for a book (a book on two lists gets both).
That total becomes the book's `score`. The full breakdown is saved in `score_breakdown`
so you can see exactly where the points came from.

---

## Step 1 — Deploy the scorer function

From your Booksmut repo root:

```bash
cd "e:/Builds - Copy/Booksmut"

gcloud functions deploy scorer --gen2 --runtime=python311 --region=us-central1 --source=functions/scorer --entry-point=main --trigger-http --no-allow-unauthenticated --service-account=reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com --set-env-vars GCP_PROJECT=YOUR_GCP_PROJECT_ID --timeout=120s --memory=256Mi
```

When done it will show the function URL — **copy it**, you need it for Step 2.

---

## Step 2 — Grant invoke permission

Cloud Run resets IAM bindings on every deploy. Run this after every deployment:

```bash
gcloud run services add-iam-policy-binding scorer --region=us-central1 --member="allUsers" --role="roles/run.invoker"
```

---

## Step 3 — Create the weekly schedule

This runs the scorer every Monday at 8:05am — 5 minutes after the nyt-fetcher,
giving it time to finish before the scorer starts.

Replace `YOUR_SCORER_URL` and `YOUR_GCP_PROJECT_ID`:

```bash
gcloud scheduler jobs create http scorer-weekly --schedule="5 8 * * 1" --uri="YOUR_SCORER_URL" --http-method=POST --oidc-service-account-email=reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com --location=us-central1 --description="Weekly book scorer — runs after nyt-fetcher"
```

---

## Step 4 — Test it manually

Run it now to score the 34 books already in the database:

```bash
gcloud scheduler jobs run scorer-weekly --location=us-central1
```

Check the logs:

```bash
gcloud functions logs read scorer --region=us-central1 --limit=50
```

You should see lines like:
- `Scored book XXXX: 19 points (1 source(s))`
- `Scorer complete. Books scored: 34`

**Then verify in Supabase:**

```sql
-- Should show SCORED status with score > 0
select title, author, score, score_breakdown, status
from books
order by score desc
limit 20;
```

The top books (rank 1 on multiple lists) will have the highest scores.

---

## If something goes wrong

**"Permission denied"** — the service account already has Secret Manager access from
Step 2-1. No new permissions needed.

**"0 books scored"** — all books may already be SCORED from a previous run. The scorer
only processes ENRICHED books. If you want to re-score, run this in Supabase SQL Editor:
```sql
update books set status = 'ENRICHED' where status = 'SCORED';
```
Then re-run the scorer.

**Scorer runs before nyt-fetcher finishes** — increase the Cloud Scheduler offset.
Change `5 8 * * 1` to `10 8 * * 1` (10 minutes after) if needed.

---

## What's Next

**Step 2-3:** Queue selector — picks the top-scoring SCORED books and creates Campaign
rows so they're ready for video generation
