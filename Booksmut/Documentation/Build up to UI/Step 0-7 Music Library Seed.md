# Step 0-7: Music Library Seed

**Purpose:** Source 20+ royalty-free background music tracks for the video pipeline.
Every track must have a no-attribution commercial license — the pipeline cannot credit
artists in captions at scale.

**Time:** 30–60 minutes
**Target:** 4 tracks per mood × 5 moods = 20 tracks minimum

**Record every track in:** `Step 0-7 Music Library Tracker.csv`

---

## License Rules — Read Before Downloading

Only these three license types are permitted:

| License Code | What It Means | Source |
|---|---|---|
| `CC0` | Public domain. No restrictions, no attribution, ever. | Various |
| `PIXABAY_COMMERCIAL` | Pixabay's own license — commercial use, no attribution required | Pixabay Music |
| `YAL_NO_ATTRIBUTION` | YouTube Audio Library tracks explicitly marked "Free to use, even commercially" | YouTube Audio Library |

**Reject any track marked CC-BY** — even if it sounds perfect. CC-BY requires crediting
the artist in every use. The pipeline cannot do this at scale.

---

## Mood Categories

You need tracks that feel right for each mood. These map to the book's aesthetic tags
and drive which music plays under each video.

| Mood | What It Should Feel Like | Example Book Vibes |
|---|---|---|
| `romantic` | Soft piano, strings, emotional warmth | Contemporary romance, slow burn |
| `dreamy` | Ethereal synths, gentle, floaty | Fantasy romance, fae worlds |
| `intense` | Dramatic strings, tension, dark undertones | Dark romance, enemies to lovers |
| `cozy` | Acoustic guitar, warm, comfort | Cozy mystery, small town romance |
| `epic` | Orchestral, big stakes, sweeping | Romantasy, chosen one, war romance |

---

## Source 1: Pixabay Music

**How to get there:** Search "Pixabay Music" in your browser.

**How to filter:**
1. Use the genre/mood filters on the left sidebar
2. Useful categories to browse: Cinematic, Romance, Ambient, Classical
3. Every track on Pixabay Music uses the `PIXABAY_COMMERCIAL` license — no need to check individually
4. BPM and duration are shown on each track card

**Search terms that work well:**
- romantic → search "romantic piano", "love theme", "soft strings"
- dreamy → search "ethereal", "fantasy ambient", "magical"
- intense → search "dramatic", "dark cinematic", "tension"
- cozy → search "acoustic", "warm", "cozy coffee"
- epic → search "epic orchestral", "heroic", "adventure"

**To download:**
1. Click the track
2. Click **Download** — no account required for music
3. File downloads as MP3
4. Rename immediately to something descriptive: `romantic-soft-piano-01.mp3`

---

## Source 2: YouTube Audio Library

**How to get there:** YouTube Studio → Audio Library (left sidebar), or search
"YouTube Audio Library" in your browser and sign in with your Google account.

**Critical filter — do this first:**
1. Click the **Free Music** tab
2. Click the filter icon
3. Under **Attribution**, select **No attribution required**
4. This filters to only `YAL_NO_ATTRIBUTION` tracks — safe to use

**How to find moods:**
- Use the **Genre** filter: Cinematic, Classical, Ambient, Folk & Acoustic
- Use the **Mood** filter: Romantic, Happy, Inspiring, Dark, Calm

**To download:**
1. Click the download arrow next to the track name
2. Note the BPM — shown in the track details when you expand it
3. Rename the file immediately after downloading

**Do not download anything with an attribution icon (person icon) next to it.**
Only download tracks that show the "Free to use, even commercially" label.

---

## Source 3: CC0 tracks from Free Music Archive

**How to get there:** Search "Free Music Archive" in your browser.

**How to filter:**
1. Browse by genre
2. On each track page, check the license — only download tracks marked **CC0**
3. Reject anything marked CC-BY, CC-BY-SA, or CC-BY-NC

---

## What to Record for Each Track

Open `Step 0-7 Music Library Tracker.csv` and fill in one row per track:

| Field | Where to Find It |
|---|---|
| Title | Track name on the source site |
| Artist | Artist name (record it even though attribution isn't required) |
| Mood | Assign from the 5 categories above — one track can have multiple |
| BPM | Shown on Pixabay and YouTube Audio Library |
| Duration (seconds) | Shown on the track card |
| License | `CC0`, `PIXABAY_COMMERCIAL`, or `YAL_NO_ATTRIBUTION` |
| Source URL | Copy the URL of the track page before downloading |
| File Name | What you renamed the downloaded file to |

---

## Where to Save the Files

Create a folder: `E:\Builds - Copy\Booksmut\Assets\Music\`

Organise by mood:
```
Assets/
  Music/
    romantic/
    dreamy/
    intense/
    cozy/
    epic/
```

These files will be uploaded to Cloudflare R2 in Phase 1.

---

## Checklist

- [ ] 4+ romantic tracks downloaded and recorded
- [ ] 4+ dreamy tracks downloaded and recorded
- [ ] 4+ intense tracks downloaded and recorded
- [ ] 4+ cozy tracks downloaded and recorded
- [ ] 4+ epic tracks downloaded and recorded
- [ ] All tracks recorded in tracker CSV
- [ ] All files renamed descriptively
- [ ] All files saved to correct mood subfolder
- [ ] Zero CC-BY tracks included

---

## What's Next

**Phase 1:** Database and Auth Foundation — deploy Supabase migrations and configure
Row Level Security.
