# Step 4: Deploy the Moderation UI

**Purpose:** A simple web page where you review each generated script before it goes to
voiceover. You can edit the hook, body, CTA, caption, and hashtags inline. Approve sends
it to voicing. Regenerate sends it back for re-scripting with a tone note. Reject sends it
back with no note.

**Time:** ~20 minutes

**Prerequisites:**
- Step 3 complete (campaigns exist in Supabase with status `SCRIPTED`)
- A GitHub account (the repo is already on GitHub)
- A Cloudflare account (free — cloudflare.com)

---

## Step 1 — Add the tone_note column to campaigns

Run this once in Supabase SQL Editor:

```sql
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS tone_note text;
```

---

## Step 2 — Get your Supabase credentials

You need two values from the Supabase dashboard:

**Project URL:**
- Supabase dashboard → Settings → API
- Copy the "Project URL" — looks like `https://xxxx.supabase.co`

**Service role key:**
- Same page → Project API keys → `service_role` (click to reveal)
- Copy the full key — it's a long string starting with `eyJ...`

> **Note:** The service role key bypasses Supabase's row-level security — it gives full
> access to your database. This page is internal-only. Never share the URL publicly.

---

## Step 3 — Add your credentials to the HTML file

Open `web/index.html` and find these two lines near the top of the `<script>` block:

```js
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_KEY = 'YOUR_SERVICE_ROLE_KEY';
```

Replace the placeholder values with your real credentials. Save the file.

---

## Step 4 — Deploy to Cloudflare Pages

Cloudflare Pages hosts the file for free and auto-deploys whenever you push to GitHub.

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** → **Create**
2. Choose **Pages** → **Connect to Git**
3. Authorise Cloudflare to access your GitHub account if prompted
4. Select the `builds-workspace` repository
5. Set these build settings:
   - **Build command:** *(leave blank)*
   - **Build output directory:** `Booksmut/web`
6. Click **Save and Deploy**

Cloudflare will deploy in about 30 seconds. You'll get a URL like
`https://reelforge-moderation.pages.dev` — bookmark it.

---

## Step 5 — Test it

1. Open the Cloudflare Pages URL in your browser
2. You should see your 5 SCRIPTED campaigns as cards
3. Try editing a hook — change a word, then click Approve
4. Check in Supabase that the campaign status changed to `MODERATION_SCRIPT`:

```sql
select b.title, c.status, left(c.caption, 60) as caption
from campaigns c
join books b on b.id = c.book_id
order by c.updated_at desc
limit 5;
```

---

## Using the moderation UI

**Approve** — saves any edits you made to hook/body/CTA/caption/hashtags, then advances
the campaign to `MODERATION_SCRIPT`. The voiceover function will pick it up from there.

**Regenerate** — sends the campaign back to `CAMPAIGN_DRAFT` so the script generator
re-scripts it on the next Monday run. Before clicking Regenerate, either:
- Set a default tone/style in the dropdowns at the top of the page (applies to all regenerations), or
- Type a specific note in the "Tone note for regeneration" field on the card

The tone note is saved to the database and will be used by the script generator in a
future update. For now, it's stored so you can see it when the campaign comes back.

**Reject** — sends the campaign back to `CAMPAIGN_DRAFT` with no tone note.
Use this if the script is completely off and you just want a fresh attempt.

---

## If something goes wrong

**"Failed to load: Invalid API key"** — the service role key in the HTML is wrong or has
extra whitespace. Copy it again from Supabase Settings → API → service_role.

**"Failed to load: relation campaign_parts does not exist"** — the nested select query
requires the foreign key relationship to be set up in Supabase. Check that `campaign_parts`
has a `campaign_id` column with a foreign key to `campaigns.id`.

**"Approve failed: column tone_note does not exist"** — you skipped Step 1. Run the
`ALTER TABLE` from Step 1 in the Supabase SQL Editor.

**Page loads but shows no campaigns** — check that campaigns exist with status `SCRIPTED`:
```sql
select status, count(*) from campaigns group by status;
```
If none are SCRIPTED, run the script generator (see Step 3 deploy guide).

**Changes not deploying** — Cloudflare Pages auto-deploys on every push to the `master`
branch. Check the Pages dashboard for deploy status. If it failed, check the build logs.

---

## What's Next

**Step 5:** Voiceover — reads `MODERATION_SCRIPT` campaigns and generates a TTS voiceover
for each script part using Google Cloud Text-to-Speech
