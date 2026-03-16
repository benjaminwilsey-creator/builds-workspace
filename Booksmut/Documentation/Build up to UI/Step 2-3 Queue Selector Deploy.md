# Step 2-3: Deploy the Queue Selector

**Purpose:** Deploy one Cloud Function (`queue-selector`) that picks the top-scoring books
each week and creates a Campaign row for each one. A Campaign is the record that triggers
video generation — this is the handoff from "book discovery" to "content production."

**Time:** ~15 minutes

**Prerequisites:**
- Step 2-2 complete (scorer deployed, books in Supabase with status SCORED)
- Same GCP project and service account as Steps 2-1 and 2-2

---

## How the queue selector works

Each week it:
1. Finds all books with status `SCORED` that don't already have an active campaign
2. Sorts them: books with `force_queued = true` first, then by score descending
3. Takes the top 5 (`TOP_N = 5`)
4. Creates one `campaigns` row for each (status `CAMPAIGN_DRAFT`, type `QUICK_TAKE`)
5. Sets each book's status to `ACTIVE`

Books are only queued once — if a campaign already exists (and isn't rejected), the book is
skipped. To manually force a specific book to the top of the queue regardless of score, set
`force_queued = true` on that book in Supabase.

---

## Step 1 — Deploy the queue-selector function

From your Booksmut repo root:

```bash
cd "e:/Builds - Copy/Booksmut"

gcloud functions deploy queue-selector --gen2 --runtime=python311 --region=us-central1 --source=functions/queue-selector --entry-point=main --trigger-http --no-allow-unauthenticated --service-account=reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com --set-env-vars GCP_PROJECT=YOUR_GCP_PROJECT_ID --timeout=120s --memory=256Mi
```

This takes 2–3 minutes. When done it will show the function URL — **copy it**, you need it for Step 3.

---

## Step 2 — Grant invoke permission

Cloud Run resets IAM bindings on every deploy. Run this after every deployment:

```bash
gcloud run services add-iam-policy-binding queue-selector --region=us-central1 --member="allUsers" --role="roles/run.invoker"
```

---

## Step 3 — Create the weekly schedule

This runs the queue selector every Monday at 8:10am — 5 minutes after the scorer,
giving it time to finish before the queue selector starts.

Replace `YOUR_QUEUE_SELECTOR_URL` and `YOUR_GCP_PROJECT_ID`:

```bash
gcloud scheduler jobs create http queue-selector-weekly --schedule="10 8 * * 1" --uri="YOUR_QUEUE_SELECTOR_URL" --http-method=POST --oidc-service-account-email=reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com --location=us-central1 --description="Weekly queue selector — picks top books after scorer"
```

---

## Step 4 — Test it manually

Run it now to create the first batch of campaigns:

```bash
gcloud scheduler jobs run queue-selector-weekly --location=us-central1
```

Check the logs:

```bash
gcloud functions logs read queue-selector --region=us-central1 --limit=50
```

You should see lines like:
- `Queued: The Women (book XXXX)`
- `Queue selector complete. Campaigns created: 5`

**Then verify in Supabase:**

```sql
-- Should show 5 new CAMPAIGN_DRAFT rows
select c.id, b.title, c.campaign_type, c.status, c.created_at
from campaigns c
join books b on b.id = c.book_id
order by c.created_at desc
limit 10;

-- Books should now show ACTIVE status
select title, score, status
from books
where status = 'ACTIVE'
order by score desc;
```

---

## If something goes wrong

**"Campaigns created: 0"** — all SCORED books may already have campaigns from a previous
run. The selector skips books with any non-rejected campaign. To re-queue from scratch,
delete the existing campaign rows in Supabase and re-run.

**"401 Unauthorized"** — the allUsers IAM binding from Step 2 was not applied or was reset
by a redeploy. Re-run the `add-iam-policy-binding` command and try again.

**"INVALID_ARGUMENT" when creating the scheduler** — check the service account email format.
It must be `name@project-id.iam.gserviceaccount.com` with the `@` separator. A common mistake
is running the project ID and account name together without the `@`.

**Scorer runs after queue selector** — the timing offset may need adjusting. If the scorer
isn't finishing before 8:10am, change the queue selector schedule to `15 8 * * 1`.

---

## Weekly pipeline timing

| Time (Monday) | Function | What it does |
|---|---|---|
| 8:00am | nyt-fetcher | Fetches NYT lists, enriches books via Hardcover |
| 8:05am | scorer | Scores all ENRICHED books |
| 8:10am | queue-selector | Picks top 5, creates Campaign rows |

Each function runs independently. If one fails, the others still run — they just won't
have fresh data to work with. Check Cloud Scheduler logs if the pipeline seems stalled.

---

## What's Next

**Step 3:** Script generator — reads CAMPAIGN_DRAFT campaigns and uses Gemini to write
a short-form video script for each book
