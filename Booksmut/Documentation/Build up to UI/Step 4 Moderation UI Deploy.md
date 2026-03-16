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

## Step 2 — Enable Row Level Security (RLS)

RLS controls what the page can read and write. Run this in Supabase SQL Editor:

```sql
-- Enable RLS on both tables
ALTER TABLE campaigns      ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_parts ENABLE ROW LEVEL SECURITY;

-- Allow the moderation UI to read and update campaigns
CREATE POLICY "moderation_read"   ON campaigns      FOR SELECT USING (true);
CREATE POLICY "moderation_update" ON campaigns      FOR UPDATE USING (true);
CREATE POLICY "parts_read"        ON campaign_parts FOR SELECT USING (true);
CREATE POLICY "parts_update"      ON campaign_parts FOR UPDATE USING (true);
```

> **Why this matters:** With RLS enabled and these policies in place, the anon key used
> in the page can only read and update — it cannot delete rows or access other tables.

---

## Step 3 — Get your Supabase credentials

You need two values from the Supabase dashboard:

**Project URL:**
- Supabase dashboard → Settings → API
- Copy the "Project URL" — looks like `https://xxxx.supabase.co`

**Anon key:**
- Same page → Project API keys → `anon` / `public`
- Copy the full key — it's a long string starting with `eyJ...`

> **Do not use the `service_role` key here.** That key bypasses all security and gives
> full database access. The `anon` key is designed for client-side use — it respects the
> RLS policies you set above.

---

## Step 4 — Add your credentials to the HTML file

Open `web/index.html` and find these two lines near the top of the `<script>` block:

```js
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_KEY = 'YOUR_ANON_KEY';
```

Replace both placeholders with your real values. Save the file.

---

## Step 5 — Deploy to GitHub Pages

Cloudflare Pages hosts the file for free and auto-deploys whenever you push to GitHub.

1. Go to your repo on GitHub → **Settings** → **Pages** (left sidebar)
2. Under "Source" → select **Deploy from a branch**
3. Branch: `master` · Folder: `/Booksmut/web`
4. Click **Save**

GitHub will give you a URL like
`https://benjaminwilsey-creator.github.io/builds-workspace/Booksmut/web/`
in about 60 seconds — bookmark it.

---

## Step 6 — Test it

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

**"Failed to load: Invalid API key"** — the anon key in the HTML is wrong or has extra
whitespace. Copy it again from Supabase Settings → API → anon / public.

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
