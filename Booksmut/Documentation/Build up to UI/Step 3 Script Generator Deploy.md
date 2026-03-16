# Step 3: Deploy the Script Generator

**Purpose:** Deploy one Cloud Function (`script-generator`) that reads all `CAMPAIGN_DRAFT`
campaigns and writes a short-form video script for each one using Gemini. It creates the
hook, body, and CTA for each video part, plus a caption and hashtags. Once complete, each
campaign advances to `SCRIPTED` status and is ready for voiceover.

**Time:** ~20 minutes

**Prerequisites:**
- Steps 2-1, 2-2, and 2-3 complete (campaigns exist in Supabase with status `CAMPAIGN_DRAFT`)
- A Gemini API key (get one at [aistudio.google.com](https://aistudio.google.com) — free tier works)
- Same GCP project and service account as previous steps

---

## Step 1 — Add your Gemini API key to Secret Manager

```bash
printf "YOUR_GEMINI_API_KEY" | gcloud secrets create GEMINI_API_KEY --data-file=-
```

Then grant the service account permission to read it. Replace `YOUR_GCP_PROJECT_ID`:

```bash
gcloud secrets add-iam-policy-binding GEMINI_API_KEY --member="serviceAccount:reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
```

---

## Step 2 — Deploy the script-generator function

From your repo root (`e:/Builds - Copy`):

```bash
gcloud functions deploy script-generator --gen2 --runtime=python311 --region=us-central1 --source=Booksmut/functions/script-generator --entry-point=main --trigger-http --no-allow-unauthenticated --service-account=reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com --set-env-vars GCP_PROJECT=YOUR_GCP_PROJECT_ID --timeout=300s --memory=256Mi
```

This takes 2–3 minutes. When done it will show the function URL — **copy it**, you need it for Step 4.

> **Note:** `--timeout=300s` gives the function 5 minutes to call Gemini for each campaign.
> This is enough headroom for a normal weekly batch of 5 books.

---

## Step 3 — Grant invoke permission

Cloud Run resets IAM bindings on every deploy. Run this after every deployment:

```bash
gcloud run services add-iam-policy-binding script-generator --region=us-central1 --member="allUsers" --role="roles/run.invoker"
```

---

## Step 4 — Create the weekly schedule

This runs the script generator every Monday at 8:15am — 5 minutes after the queue selector,
giving it time to finish creating campaign rows before scripting begins.

Replace `YOUR_SCRIPT_GENERATOR_URL` and `YOUR_GCP_PROJECT_ID`:

```bash
gcloud scheduler jobs create http script-generator-weekly --schedule="15 8 * * 1" --uri="YOUR_SCRIPT_GENERATOR_URL" --http-method=POST --oidc-service-account-email=reelforge-api-runner@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com --location=us-central1 --description="Weekly script generator — writes Gemini scripts for CAMPAIGN_DRAFT campaigns"
```

---

## Step 5 — Test it manually

Run it now to script the existing campaigns:

```bash
gcloud scheduler jobs run script-generator-weekly --location=us-central1
```

Check the logs:

```bash
gcloud functions logs read script-generator --region=us-central1 --limit=50
```

You should see lines like:
- `Scripted: The Women (campaign XXXX)`
- `Script generator complete. Scripted: 5, Errors: 0`

**Then verify in Supabase:**

```sql
-- Should show 5 rows with status SCRIPTED
select c.id, b.title, c.status, left(c.caption, 80) as caption_start, c.hashtags
from campaigns c
join books b on b.id = c.book_id
where c.status = 'SCRIPTED'
order by c.updated_at desc;
```

```sql
-- Should show campaign_parts rows with hooks and categories
select cp.campaign_id, cp.part_number, cp.hook_category, left(cp.hook, 60) as hook
from campaign_parts cp
order by cp.created_at desc
limit 10;
```

---

## If something goes wrong

**`Scripted: 0, Errors: 0`** — the function ran but found no `CAMPAIGN_DRAFT` campaigns.
Check what status your campaigns are in:
```sql
select status, count(*) from campaigns group by status;
```
If all campaigns are already `SCRIPTED` from a previous run, the function correctly skips them.
To re-run from scratch, reset the campaigns:
```sql
update campaigns set status = 'CAMPAIGN_DRAFT', retry_count = 0, last_error = null
where status = 'SCRIPTED';
```
Then delete the campaign_parts rows and re-run:
```sql
delete from campaign_parts where campaign_id in (select id from campaigns where status = 'CAMPAIGN_DRAFT');
```

**`Scripted: 0, Errors: 5`** — all campaigns failed. Check logs for the error message.
Most common causes:
- GEMINI_API_KEY secret not found or IAM binding missing (Step 1)
- Gemini API quota exceeded (free tier: 10 requests/minute, 250/day)

**`"model not found"` in logs** — the Gemini model name is wrong. The current model is
`gemini-2.5-flash`. Edit `main.py` and redeploy.

**`401 Unauthorized`** — the function URL is correct but the allUsers IAM binding wasn't
applied or was reset by a redeploy. Re-run the `add-iam-policy-binding` command from Step 3.

**Captions missing FTC disclosure** — the Gemini prompt instructs the model to start every
caption with "As an Amazon Associate I earn from qualifying purchases." If captions are
missing this, the prompt may have been modified. Check `_build_prompt` in `main.py`.

---

## What's Next

**Step 4:** Moderation — review each scripted campaign and approve or reject before voiceover

---

## Weekly pipeline timing (full picture)

| Time (Monday) | Function | What it does |
|---|---|---|
| 8:00am | nyt-fetcher | Fetches NYT lists, enriches books via Hardcover |
| 8:05am | scorer | Scores all ENRICHED books |
| 8:10am | queue-selector | Picks top 5, creates Campaign rows |
| 8:15am | script-generator | Writes Gemini scripts for each campaign |
