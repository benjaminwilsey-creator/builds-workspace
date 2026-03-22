# ReelForge — Technical Project Guide v2

**BookTok Affiliate Content Generation Agent · Builder Reference**

*v2 — Updated 2026-03-01. Four corrections applied from pre-build spike review.
Corrections are marked with `[CORRECTED]` inline. Original .docx (v1) preserved.*

---

This guide is the single source of truth for building ReelForge. It documents every
architectural decision, the complete technical stack, all database schemas, the video pipeline
state machine, and a phased build plan. It also defines every collaboration point with your
non-technical partner so nothing falls through the gap between your respective domains.

| | |
|---|---|
| **Product** | ReelForge |
| **Niche** | BookTok — Romance, Romantasy, YA |
| **Revenue Model** | Amazon Associates affiliate links |
| **Monthly Cost Target** | $0 — 100% free tier infrastructure |
| **Distribution** | Meta (Facebook/Instagram) — native scheduling |
| **Video Format** | 30-second Reels — single or multipart (up to 5) |

---

## 01 — What We Are Building

### Product Definition

ReelForge is an automated BookTok content pipeline. It discovers trending and rising romance
and romantasy books from multiple free data sources, generates short-form video scripts,
produces 30-second video reels using FFmpeg, applies voiceover via Google TTS, and delivers
a download-ready video with a caption and affiliate link — all without spending a dollar on
compute or AI services.

### The Core Value Loop

```
Discover Books → Generate Content → Human Review → Native Schedule → Affiliate Click
```

### Key Decisions Already Locked

Every item below was decided and will not be revisited without a documented reason.

| Decision Area | What Was Decided | Status |
|---|---|---|
| AI Video (Runway) | Dropped. FFmpeg Ken Burns only — deterministic, free, sufficient for book covers | ✅ Locked |
| TTS Voice | Google Cloud TTS — 1M WaveNet chars/month free | ✅ Locked |
| Script Generation | Gemini API free tier — 15 RPM, 1M tokens/day | ✅ Locked |
| Database | Supabase (Postgres) — auth included, 500MB free | ✅ Locked |
| File Storage | Cloudflare R2 — 10GB free, zero egress fees | ✅ Locked |
| Compute | AWS Lambda — FFmpeg processing within 15-min timeout | ✅ Locked |
| Orchestration | SQS + Lambda chaining — no Step Functions needed at MVP | ✅ Locked |
| Frontend | Vercel + shadcn/ui — free hobby tier | ✅ Locked |
| Distribution | Meta native scheduling only — no Graph API posting | ✅ Locked |
| Affiliate | Amazon Associates — raw URL from ISBN + associate tag | ✅ Locked |
| Cover Images | Licensed publishers only + backdrop fallback | ✅ Locked |
| Moderation | Human eyes required on ALL failures — no auto-fix | ✅ Locked |
| FTC Disclosure | Auto-injected in first 100 chars of every caption | ✅ Locked |
| Video Specs | 1080×1920, H.264, AAC, 30fps, MP4 | ✅ Locked |

---

## 02 — Full Technical Stack

Every service, its role, free tier limits, and what breaks if it goes down.

| Service | Role | Free Limit | Failure Impact |
|---|---|---|---|
| Supabase | Database + Auth | 500MB / 50K MAU | No auth, no data access |
| Cloudflare R2 | Video + audio storage | 10GB, 0 egress fees | Videos unreachable for download |
| AWS Lambda | FFmpeg compositor + pipeline runners | 400K GB-sec/mo | Video generation stops |
| AWS SQS | Job queuing between pipeline stages | 1M requests/mo | Pipeline halts between stages |
| AWS SES | Alert emails for failures | 62K emails/mo | Silent failures undetected |
| Gemini API | Script + caption generation | 1M tokens/day, 15 RPM | No scripts generated |
| Google Cloud TTS | Voiceover audio | 1M WaveNet chars/mo | Silent videos only |
| Google Cloud Vision | Video moderation (cover + frames) | 1K units/mo | Moderation gate bypassed |
| Google Books API | Book metadata (NOT cover images) | 1K req/day | Enrichment slows |
| Hardcover.app | Trending book signal + trope tags | Free GraphQL | Scoring signal reduced |
| Open Library | Cover image reference only — **NOT cleared for commercial use** `[CORRECTED]` | Unlimited | N/A — not used in pipeline |
| NYT Books API | Weekly bestseller list seeding | Free with key | Weekly seed signal lost |
| Reddit API | Rising author/book signal | 60 req/min free | Early signal reduced |
| Vercel | Frontend hosting | Unlimited hobby | Dashboard inaccessible |
| Amazon Associates | Affiliate link revenue | Free to join | Revenue generation stops |

> **`[CORRECTED]`** Open Library was previously listed as a "cleared source" for cover images.
> This is incorrect. Open Library does not hold or grant copyright over book covers. Copyright
> belongs to publishers and cover artists. Open Library covers must NOT be used commercially
> without explicit publisher permission. They are removed from the cover fallback chain.
> See Section 03 for the corrected cover source hierarchy.

---

## 03 — Data Source Architecture

### Three-Tier Signal System for Book Discovery

The pipeline uses a layered scoring system. Books appearing across multiple sources receive
higher scores and enter the content queue faster. No single source is sufficient on its own.

#### Tier 1 — Early Signal (Leading Indicators)

These sources tell you what is about to trend — before the mainstream lists catch it.

| Source | Signal | Implementation |
|---|---|---|
| Hardcover.app GraphQL API | Read velocity, trending lists, community shelves, trope tags | Free API — query books_trending, filter by genre |
| Reddit r/RomanceBooks + r/Fantasy | Pre-viral word of mouth, hidden gem discoveries, author mention spikes | Reddit API free tier — keyword + author name search |
| BookTok Trend (booktoktrend.com) | Real-time TikTok-driven velocity with retailer signal | Careful scrape — weekly, respect robots.txt |
| Publisher upcoming release pages | Anticipated releases 3–6 months ahead of publication | Scrape Penguin, Macmillan, Tor upcoming pages weekly |
| StoryGraph | Mood/trope-based trending, diverse reader community signal | Careful scrape — no official API |

#### Tier 2 — Current Signal (Confirmed Trending)

| Source | Signal | Implementation |
|---|---|---|
| NYT Books API | Weekly bestseller lists by category — authoritative confirmation | Official API key — free, pull Sunday nights |
| Google Books API | Metadata only — descriptions, page count, published date, ISBN | 1K req/day — NOT for cover images (licensed content) |
| Barnes & Noble Top 50 | Skews more BookTok-aligned than NYT, updates frequently | Weekly scrape of B&N bestseller page |
| Reese's Book Club | High-conversion list — anything featured drives engagement | Scrape recommendations page monthly |

### Cover Image Source Hierarchy `[CORRECTED]`

> **v1 incorrectly listed Open Library as a "cleared source."** It is not. The correct
> fallback chain is:

1. **Publisher-licensed cover** — `cover_image_source = PUBLISHER_LICENSED`, `cover_cleared_for_use = true`. Requires active record in `publisher_licenses` table with status `LICENSED`.
2. **Author-provided cover** — `cover_image_source = AUTHOR_PROVIDED`, `cover_cleared_for_use = true`. Requires documented permission.
3. **Backdrop fallback** — `use_backdrop_fallback = true`. Setting atmosphere video selected from R2 backdrop library based on `setting_primary` and `setting_mood`. No cover image used.

Open Library covers are NOT included in this chain. If no licensed cover is available, the pipeline must use the backdrop fallback — not an unlicensed third-party image.

### Scoring Algorithm

Books are scored 0–100 on first discovery. Crossing a threshold (default: 40) advances them
to ENRICHED. Force-queue bypasses scoring entirely.

| Source | Points | Rationale |
|---|---|---|
| NYT Bestseller List | 40 pts | Confirmed commercial traction |
| Hardcover trending (top 50) | 30 pts | Reader community velocity |
| Barnes & Noble Top 50 | 20 pts | Retailer confirmation |
| Reddit mention spike | 20 pts | Pre-viral signal |
| BookTok Trend appearance | 15 pts | Direct platform signal |
| Publisher upcoming list | 10 pts | Anticipated release value |
| Cross-source bonus (3+ sources) | +10 pts | Convergence amplifier |

---

## 04 — State Machines

### Book-Level State Machine

| State | What Happens | Transitions To |
|---|---|---|
| DISCOVERED | Book enters system from any data source. ISBN, title, author recorded. No enrichment yet. | SCORED |
| SCORED | Cross-source scoring applied. Score breakdown stored in JSONB. Force-queue flag bypasses threshold. | ENRICHED (pass) / REJECTED (fail) |
| ENRICHED | Google Books metadata pulled. Hardcover trope tags fetched. Licensed cover sourced (or backdrop assigned). | ACTIVE |
| ACTIVE | Book is live. Campaigns can be created against it. Stays active indefinitely. | (campaigns spawn here) |
| REJECTED | Score too low or human rejected. cooldown_until = rejected_at + 30 days. Automatically re-queues when timer expires. | DISCOVERED (after 30 days) |

### Campaign-Level State Machine

One book → many campaigns. Each campaign is independent. Failed campaigns do not affect the
parent book.

| State | What Happens | Transitions To |
|---|---|---|
| CAMPAIGN_DRAFT | Created by system (auto) or user (manual). Campaign type, format (SINGLE/MULTIPART), and total_parts assigned. | SCRIPTED |
| SCRIPTED | Gemini generates full script in one pass. For MULTIPART, all parts scripted together to ensure cliffhanger continuity. | MODERATION_SCRIPT |
| MODERATION_SCRIPT | Gemini checks script for Meta policy violations, FTC issues, misleading claims, explicit language, banned hashtags. | VOICED (pass) / MODERATION_FAILED (fail) |
| VOICED | Google TTS generates one audio file per part. Stored to R2. | COMPOSED |
| COMPOSED | FFmpeg renders each part as standalone 30-second MP4. Part overlays added. 'Follow for Part N' CTAs on all but final part. | MODERATION_VIDEO |
| MODERATION_VIDEO | Cloud Vision API scans final video frames + cover image for nudity, violence, OCR issues. | READY (pass) / MODERATION_FAILED (fail) |
| MODERATION_FAILED | Human review required. Three options: Override (with written reason), Edit (returns to SCRIPTED or COMPOSED), Reject. | SCRIPTED / COMPOSED / REJECTED |
| READY | All parts available for download. Caption + hashtags ready. Music track assigned. Human can approve, edit, or reject. | SCHEDULED / SCRIPTED / COMPOSED / REJECTED |
| SCHEDULED | Human has downloaded video(s) and scheduled natively in Meta Business Suite. No API posting used. | PUBLISHED |
| PUBLISHED | Human marks complete after Meta publishes. Performance tracking begins. | (terminal) |
| REJECTED | Campaign killed. Book stays ACTIVE. New campaign can be created immediately. | (terminal) |

---

## 05 — Database Schema

All Supabase tables with fields, types, and purpose.

### books — core book record

| Field | Type | Purpose |
|---|---|---|
| id | uuid PK | Primary key, auto-generated |
| tenant_id | uuid FK | Multi-tenant isolation |
| isbn / google_books_id / hardcover_id / open_library_id | text | Cross-source identifiers |
| title, author, series_name, series_position | text / int | Core bibliographic data |
| genre, subgenre | text | Used for scoring and campaign type selection |
| cover_image_url | text | R2 URL of cleared cover image |
| cover_image_source | text ENUM | `PUBLISHER_LICENSED` \| `AUTHOR_PROVIDED` \| `NONE` `[CORRECTED]` |
| cover_cleared_for_use | boolean | Must be true for cover to appear in video |
| use_backdrop_fallback | boolean | True when no cleared cover — uses setting atmosphere video |
| description | text | Fed to Gemini for script generation |
| tropes | text[] | Array of trope tags from Hardcover — used in video overlays |
| spice_level | int 0–5 | Drives SPICE_CHECK campaign type and overlay graphics |
| pov_type | text | dual \| single \| multiple — displayed in video overlay |
| setting_primary, setting_mood | text | Used for backdrop selection in FFmpeg |
| aesthetic_tags | text[] | dark academia \| cozy \| romantasy — maps to music mood |
| score, score_breakdown | int / jsonb | Composite score + per-source breakdown |
| force_queued | boolean | Bypasses score threshold for manual priority |
| status | text ENUM | DISCOVERED \| SCORED \| ENRICHED \| ACTIVE \| REJECTED |
| cooldown_until | timestamptz | Rejected books re-enter DISCOVERED after this date |

> **`[CORRECTED]`** `cover_image_source` ENUM previously included `OPEN_LIBRARY`. This value
> has been removed. Open Library covers are not cleared for commercial use. The two valid
> cleared sources are `PUBLISHER_LICENSED` and `AUTHOR_PROVIDED`. When neither is available,
> `cover_cleared_for_use = false` and `use_backdrop_fallback = true`.

### campaigns — one per content run against a book

| Field | Type | Purpose |
|---|---|---|
| id | uuid PK | Primary key |
| book_id | uuid FK | Parent book |
| campaign_type | text ENUM | QUICK_TAKE \| TROPE_BREAKDOWN \| SPICE_CHECK \| AUTHOR_SPOTLIGHT \| HIDDEN_GEM \| BOOK_CLUB_PICK \| SERIES_RANKED \| TROPE_DEEP_DIVE \| AUTHOR_DEEP_DIVE \| WHY_NOT_OVER_IT \| ROMANTASY_STARTER_PACK \| BOOKTOK_DIVIDE |
| format | text ENUM | SINGLE \| MULTIPART |
| total_parts | int 1–5 | Number of 30-second reels in this campaign |
| created_by | text ENUM | SYSTEM \| USER |
| trigger_reason | text | new_active_book \| score_spike \| series_release \| manual |
| status | text ENUM | Full state machine — see Section 04 |
| script_raw | jsonb | Full Gemini output: `{ parts: [{part, hook, body, cta}] }` |
| caption, hashtags | text / text[] | Caption ≤2200 chars, 3–5 hashtags, FTC disclosure in first 100 chars |
| moderation_script_status / moderation_video_status | text ENUM | PENDING \| PASSED \| FAILED \| SKIPPED |
| moderation_script_flags / moderation_video_flags | jsonb | Raw flags from Gemini or Cloud Vision |
| moderation_override | boolean | True if human overrode a failure — requires human_note |
| retry_count, last_error | int / text | Retry tracking for failed Lambda jobs |
| scheduled_at, published_at | timestamptz | Human-confirmed timestamps |

### campaign_parts — one row per 30-second reel

| Field | Type | Purpose |
|---|---|---|
| id | uuid PK | Primary key |
| campaign_id | uuid FK | Parent campaign |
| part_number, total_parts | int | 1 of 5, 2 of 5 etc. |
| hook, body, cta | text | Sliced from campaign script_raw — CTA varies by position |
| hook_text, hook_category | text | Exact opening line + psychological category for performance tracking |
| audio_url, video_url, thumbnail_url | text | R2 URLs of generated assets |
| caption | text | Per-part caption variant |
| background_type | text ENUM | `cover_only` \| `setting_video` \| `ai_mood_image` \| `user_uploaded` \| `ai_generated` |
| custom_video_url | text | R2 URL of user-uploaded or AI-generated background video — used when background_type is `user_uploaded` or `ai_generated` |
| ai_prompt | text | Prompt used to generate the background (Option 3B) — empty for all other background types. Stored from day one for performance tracking. |
| music_track_id | uuid FK | References music_library |
| status | text ENUM | PENDING \| VOICED \| COMPOSED \| READY \| SCHEDULED \| PUBLISHED \| VOICE_FAILED \| COMPOSE_FAILED |

### publisher_licenses — managed by non-technical partner

| Field | Type | Purpose |
|---|---|---|
| id | uuid PK | Primary key |
| publisher_name, publisher_domain | text | Identification |
| contact_name, contact_email | text | Outreach contact |
| status | text ENUM | OUTREACH_PENDING \| IN_DISCUSSION \| LICENSED \| DECLINED \| EXPIRED |
| license_scope | text | all_titles \| specific_titles \| specific_authors |
| outreach_date, response_date, license_start, license_expiry | timestamptz/date | Full timeline tracking |
| asset_portal_url, asset_portal_login | text | Where licensed cover assets are downloaded from |
| contact_discovery_method | text ENUM | `MANUAL` \| `AUTO_CONFIRMED` \| `AUTO_AUTO` — see ADR 0003 |
| partner_corrected_contact | boolean | True if partner changed the auto-found email — feeds accuracy log |
| outreach_draft_id | text | Gmail draft ID — used to link directly to the draft in partner's inbox |
| followup_draft_sent_at | timestamptz | Prevents 7-day follow-up draft from re-firing |
| gmail_thread_id | text | Reserved for Option C — tracks reply conversation thread |
| sent_at_detected | timestamptz | Null in Option B (manual mark); auto-filled in Option C via Sent folder |

### contact_discovery_log — accuracy tracking for auto contact finder

| Field | Type | Purpose |
|---|---|---|
| id | uuid PK | Primary key |
| publisher_domain | text | Publisher being looked up |
| discovered_email | text | Email address the system found |
| was_correct | boolean | Set when partner confirms or corrects — feeds accuracy metric |
| corrected_to | text | What partner changed it to (if wrong) |
| run_number | int | Cumulative counter — accuracy = correct / last 50 runs |
| created_at | timestamptz | |

> When `run_number >= 50` AND rolling accuracy >= 98%, `contact_discovery_method` defaults
> to `AUTO_AUTO` and the partner confirmation step is skipped automatically.

### prompt_versions — outreach email A/B testing

| Field | Type | Purpose |
|---|---|---|
| id | uuid PK | Primary key |
| prompt_text | text | Full Gemini prompt template for outreach email generation |
| send_count | int | Number of emails generated using this version |
| response_count | int | Publishers who replied (partner marked IN_DISCUSSION) |
| response_rate | float | response_count / send_count — used to promote best version |
| active | boolean | Currently the default prompt |
| created_at | timestamptz | |

### affiliate_links — per-book per-tenant link records

| Field | Type | Purpose |
|---|---|---|
| book_id, tenant_id | uuid FK | Book + tenant |
| isbn, asin | text | Source identifiers for link construction |
| raw_url | text | `https://amazon.com/dp/{ASIN}?tag={associate_tag}` |
| geo_url | text | Geniuslink universal URL if configured |
| link_type | text ENUM | AMAZON \| BOOKSHOP \| DIRECT |

### music_library — licensed background tracks `[CORRECTED]`

| Field | Type | Purpose |
|---|---|---|
| title, artist | text | Track identification |
| mood | text[] | romantic \| dreamy \| intense \| cozy \| epic — maps from aesthetic_tags |
| bpm, duration_sec | int | Used for sync timing in FFmpeg |
| license | text ENUM | `CC0` \| `PIXABAY_COMMERCIAL` \| `YAL_NO_ATTRIBUTION` |
| file_url, source_url | text | R2 storage URL + original source for attribution |

> **`[CORRECTED]`** The license ENUM previously included `CC_BY` (Creative Commons Attribution).
> CC-BY requires crediting the artist in any use of the track. In a pipeline that generates
> captions at scale, there is no mechanism to credit music artists per video. Only tracks with
> no attribution requirement are permitted:
>
> - `CC0` — Public domain. No attribution required ever.
> - `PIXABAY_COMMERCIAL` — Pixabay's content license permits commercial use without attribution.
> - `YAL_NO_ATTRIBUTION` — YouTube Audio Library tracks explicitly marked "No attribution required."
>
> When seeding the music_library table (Phase 0), reject any CC-BY track regardless of quality.
> YouTube Audio Library also contains CC-BY tracks — only import those marked "Free to use."

### moderation_log — audit trail for every moderation decision

| Field | Type | Purpose |
|---|---|---|
| campaign_id | uuid FK | Which campaign |
| gate | text ENUM | SCRIPT \| VIDEO |
| result | text ENUM | PASSED \| FAILED \| OVERRIDDEN \| REJECTED \| EDIT_REQUESTED |
| system_flags | jsonb | Raw output from Gemini or Cloud Vision |
| reviewed_by | uuid | User who made the human decision |
| human_decision | text ENUM | OVERRIDE \| EDIT \| REJECT |
| human_note | text | Required when overriding — enforced at application layer |

---

## 06 — Video Pipeline & FFmpeg Specification

### FFmpeg Compositor — Output Requirements

These are locked specifications. Do not deviate — Meta Reels will reject non-compliant
uploads silently.

| | |
|---|---|
| **Resolution** | 1080 × 1920 pixels (9:16 vertical) |
| **Frame Rate** | 30fps |
| **Video Codec** | H.264 (libx264) |
| **Audio Codec** | AAC |
| **Audio Sample Rate** | 44.1 kHz stereo |
| **Max Bitrate** | 8 Mbps |
| **Container** | MP4 |
| **Max File Size** | 1GB (typical 30s output: 80–150MB at quality settings) |
| **Max Duration per Part** | 30 seconds |

### Standard 30-Second Video Structure

| Timestamp | Layer | Content | Data Source |
|---|---|---|---|
| 0:00–0:02 | Hook Frame | Bold text overlay — psychological hook | Gemini (hook_category matched to campaign type) |
| 0:02–0:08 | Book Reveal | Cover sharpens from blur. Ken Burns begins. Title + Author overlay fades in. | cover_image_url / setting video if fallback |
| 0:08–0:18 | Content Sequence | Trope stack OR quote card OR spice meter — voiceover runs | tropes[] / description / spice_level |
| 0:18–0:25 | Identity Moment | Social proof, rating, community signal text overlay | score_breakdown / Hardcover data |
| 0:25–0:30 | CTA Frame | 'Comment TBR 👇' OR 'Follow for Part N' OR affiliate CTA | Part position determines CTA type |

---

## 07 — Campaign Types

### Single-Part Campaigns

| Type | Hook Category | Example Opening Line |
|---|---|---|
| QUICK_TAKE | Curiosity Gap | Why is this book breaking everyone's algorithm right now? |
| TROPE_BREAKDOWN | Identity Signal | If slow burn destroys you, this book is a weapon |
| SPICE_CHECK | Contradiction | Don't let the pretty cover fool you |
| AUTHOR_SPOTLIGHT | Social Proof | She wrote 4 of the top 10 BookTok books this year |
| HIDDEN_GEM | Loss Aversion | This has 800 ratings. It should have 800,000 |
| BOOK_CLUB_PICK | Social Proof | Reese picked it. BookTok agrees. Here's why. |

### Multipart Campaigns (2–5 parts)

| Type | Series Arc | Scripting Note |
|---|---|---|
| SERIES_RANKED | Rank every book worst-to-best — one per part, final part is #1 reveal | All parts written in one Gemini pass — cliffhanger placement intentional |
| TROPE_DEEP_DIVE | Introduce trope → each part features one book that nails it | tropes[] array seeds the series structure |
| AUTHOR_DEEP_DIVE | Part 1: who they are → Parts 2–N: one title each → final: ranked | Author metadata from Hardcover drives part structure |
| WHY_NOT_OVER_IT | Emotional re-read campaign for backlist — unpack moments without spoilers | Targets books with high save/engagement on previous campaigns |
| ROMANTASY_STARTER_PACK | Part 1: what is romantasy → Parts 2–N: one entry-point book each | System auto-creates when genre newcomer signals detected |
| BOOKTOK_DIVIDE | Part 1 frames the debate → Parts argue each side → final: verdict | Requires books with polarised Hardcover reviews — system detects this |

---

## 08 — Phased Build Plan

Ordered by dependency — nothing is built before its foundation exists.

### PHASE 0 — Pre-Build Setup

- Create Supabase project — note connection strings and anon key
- **Set up GitHub Actions keep-alive workflow** — pings Supabase twice per week to prevent
  free-tier project pause (7-day inactivity policy). Wire this before any other build work.
- Create Cloudflare R2 bucket — configure CORS for Vercel frontend. Confirm signed URL
  expiry is set to at least 24h so download links don't expire between generation and partner action.
- Register AWS account — configure Lambda execution role with SQS + SES + R2 permissions
- Apply for NYT Books API key — free, takes 24–48 hours
- Apply for Google Cloud APIs — Books, TTS, Vision — all in same project
- Create Gemini API key — free tier, note rate limits
- **Apply for Amazon Associates account + get associate tag — apply immediately. Account
  requires 3 qualifying sales within 180 days of application.**
- Create Hardcover.app account — required to access GraphQL API
- Create Reddit API app — for r/RomanceBooks and r/Fantasy monitoring
- Set up Vercel project — connect to GitHub repo
- Seed music_library table with 20+ CC0/no-attribution tracks from Pixabay Music and YouTube
  Audio Library. **Only import tracks with confirmed no-attribution commercial licenses.**
- **Enable Gmail API in Google Cloud project** (same project as Books, TTS, Vision):
  - APIs & Services → Library → Gmail API → Enable
  - OAuth consent screen: External, scope `gmail.compose` only (create drafts — cannot read/send/delete)
  - Authorized domain: add Vercel app domain once known
  - Test users: add partner's Gmail address
  - Create OAuth 2.0 Client ID (Web application type)
  - Store `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in Vercel env vars — never commit
  - Add both as blank placeholders in `.env.example`
  - **Note:** Apply for Google app verification early — review can take 1–4 weeks and blocks
    production use beyond test users

### PHASE 1 — Database and Auth Foundation

- Deploy all Supabase migrations in schema order: tenants → users → user_roles → books →
  book_sources → campaigns → campaign_parts → affiliate_links → publisher_licenses →
  contact_discovery_log → prompt_versions → music_library → music_mood_map →
  moderation_log → seed_books → ui_feedback
- Configure Row Level Security on all tables — tenant isolation is the first security layer
- Set up Supabase Auth — email/password provider, role assignment on first login
- Create first tenant record and owner user — smoke test auth flow
- Seed seed_books table with 20 known BookTok titles across romance and romantasy
- Write and test all Supabase queries needed by the pipeline before building Lambda functions

### PHASE 2 — Discovery Pipeline

- Build NYT Books API fetcher Lambda — pulls weekly romance/fantasy lists, upserts to books
  table as DISCOVERED
- Build Hardcover GraphQL fetcher — pulls trending books + trope tags, upserts and updates scores
- Build Reddit mention scanner — searches r/RomanceBooks and r/Fantasy for author/title spikes
- Build scoring engine — applies weights, calculates composite score, stores score_breakdown JSONB
- Build book_sources logger — records each signal detection with source, rank, and strength
- **Configure scheduled triggers using EventBridge Scheduled Rules** `[CORRECTED]`:
  - Weekly EventBridge rule → NYT Lambda
  - Daily EventBridge rule → Hardcover + Reddit Lambda
  - Note: SQS remains correct for *inter-stage queuing* within the pipeline.
    EventBridge is the correct service for *time-based scheduling*.
- Wire SES alerting — email when discovery cron fails or produces zero results. Also alert
  if any scraper returns zero results unexpectedly (StoryGraph, B&N, BookTokTrend).
- Add SQS Dead Letter Queues (DLQs) on all queues — failed messages after N retries send
  an SES alert rather than disappearing silently.
- TEST: Confirm 20+ books enter DISCOVERED state and score to ENRICHED within first full run

### PHASE 3 — Enrichment Pipeline

- Build enrichment Lambda — for each SCORED book above threshold: fetch Google Books metadata,
  fetch licensed cover (from publisher_licenses) or assign backdrop fallback, advance to
  ENRICHED then ACTIVE
- Implement cover_cleared_for_use logic — check publisher_licenses table before storing cover.
  **If no licensed cover exists, set use_backdrop_fallback = true. Do not use Open Library.**
- Build backdrop fallback logic — when no cleared cover, assign setting_primary from description
  parsing (Gemini), select matching stock video from R2 backdrop library
- Build affiliate_links record creation — construct Amazon URL from ASIN + associate tag,
  store to affiliate_links
- Build music auto-selection — query music_mood_map using book aesthetic_tags, assign
  music_track_id to campaign_parts
- TEST: Each ACTIVE book has: licensed cover or backdrop (never Open Library), affiliate link,
  tropes, metadata. Validate no unlicensed covers slip through.

### PHASE 4 — Script and Voice Generation

- Build Gemini script Lambda — takes book + campaign_type, returns structured JSON with all
  parts scripted in one pass
- Implement hook_category selection — map campaign_type to psychological hook type before
  prompting Gemini
- Implement caption generator — 2200 char limit, FTC disclosure injected in first 100 chars,
  3–5 hashtags appended
- Build moderation_script Lambda — Gemini prompt checks for policy violations, flags stored to
  moderation_script_flags
- Implement MODERATION_FAILED routing — park campaign, create alert, do not advance automatically
- Build Google TTS Lambda — per part audio generation, store to R2, update audio_url on
  campaign_parts
- TEST: Generate 5 QUICK_TAKE scripts across different books. Confirm hook categories vary.
  Confirm FTC disclosure present in every caption.

### PHASE 5 — FFmpeg Compositor `[UPDATED — Google Cloud, not AWS]`

> ADR 0004: AWS replaced by Google Cloud. This phase runs as a Google Cloud Function Gen 2,
> not a Lambda. Lambda-specific notes (layer size limits, ephemeral storage config) do not apply.
> Cloud Functions Gen 2 supports up to 32GB memory, 60min timeout, and a static FFmpeg binary
> bundled with the deployment package.

#### Video Background Options

The compositor supports four background sources. The `background_type` field on `campaign_parts`
determines which is used. The compositor resolves the background to a URL first, then passes
that URL to FFmpeg — the FFmpeg command does not change based on source type.

| Option | background_type | Source | Status |
|--------|----------------|--------|--------|
| 1 | `cover_only` | Licensed book cover image (Ken Burns zoom) | Build in Phase 5 |
| 2 | `setting_video` | Pre-uploaded backdrop clip from R2 backdrop library | Build in Phase 5 |
| 3 | `user_uploaded` | Partner uploads their own video via UI — stored to R2 | Build in Phase 5 |
| 4 | `ai_generated` | AI video generation (Google Veo or Runway ML) from `ai_prompt` | Future phase — see below |

#### Build Steps

- Bundle static FFmpeg binary with the Cloud Function deployment package (Linux x86-64 static build)
- Build `video-composer` Cloud Function — takes VOICED campaign_parts, resolves background
  source to a URL, assembles: background video, Ken Burns motion (Option 1 only), text overlays
  (hook, tropes, CTA), voiceover audio, music underlay
- **Build Option 3 — user upload:** Add file upload to moderation UI → R2 upload endpoint →
  store URL in `custom_video_url`, set `background_type = user_uploaded`
- Implement part overlay logic — 'Part 1 of 3' badge, 'Follow for Part 2' end card on
  non-final parts
- Build `moderation-video` Cloud Function — extract 3 frames from rendered video, run Cloud
  Vision on each + on cover image, store flags
- Implement MODERATION_FAILED routing for video gate — same human review requirement as
  script gate
- TEST: Download rendered video, verify Meta spec compliance using ffprobe. Confirm moderation
  gate triggers on a test cover image.

#### Option 4 — AI Video Generation (Future Phase, prep done now)

**Do not build this until the pipeline is fully operational.** The following prep steps are
already in place and make integration a single Cloud Function addition:

- `background_type` ENUM already includes `ai_generated` — no DB migration needed
- `custom_video_url` field already exists — AI-generated clip URL stores here, same as user upload
- `ai_prompt` field already exists — prompt text stored from the moment she types it
- Compositor already reads from `custom_video_url` — no FFmpeg changes needed when 4 ships

**When ready to build Option 4:**
- Create `ai-video-generator` Cloud Function
- Accepts: campaign_part_id + ai_prompt text
- Calls Google Veo API (preferred — already on GCP, likely free tier credits available)
  or Runway ML as fallback
- Stores generated clip to R2 → writes URL to `custom_video_url` → sets `background_type = ai_generated`
- Add prompt input field to UI (Phase 6 dashboard or moderation UI)
- No changes required to compositor, state machine, or R2 structure
- **Cost note:** AI video generation is not free. Budget ~$0.05–0.50 per clip depending on provider
  and clip length. Evaluate Google Veo pricing when the time comes — GCP credits may cover initial volume.

### PHASE 6 — UI Dashboard

- Scaffold Vercel + Next.js + shadcn/ui — configure Supabase client, Supabase Auth provider
- Build component library — status badges, campaign cards, book cards, progress indicators,
  moderation review modal
- Build layout shell — sidebar navigation, breadcrumb, focus mode toggle, feedback annotation
  system
- Build Dashboard screen — pipeline health, queue summary, recent activity, last cron run
  timestamp
- Build Book Queue screen — DISCOVERED through ACTIVE books with scoring detail and
  force-queue action
- Build Campaign Queue screen — all campaign states, filter by status, download action on
  READY campaigns
- Build Campaign Detail screen — full script display, all parts, moderation status, download
  per part
- Build Moderation Review screen — MODERATION_FAILED campaigns, override/edit/reject actions
  with required human_note
- Build Publisher Licenses screen — ADHD-optimised layout per selected framework from
  partner's review
- Build Calendar screen — SCHEDULED content with posting cadence health indicator
- Build Settings screen — tenant config, associate tag, genre preferences, cadence, user role
  management
- **Build semi-automated publisher outreach (ADR 0003):**
  - Install `next-auth` with Google provider, `gmail.compose` scope
  - Partner authorises once on first login — refresh token stored encrypted in Supabase
  - Build contact discovery UI — shows auto-found email with "Confirm" / "Correct it" buttons,
    logs result to `contact_discovery_log`
  - Build accuracy calculator — when rolling accuracy ≥ 98% over last 50 runs, switch to
    `AUTO_AUTO` mode (skip confirmation step)
  - Build Gemini outreach email prompt (Phase 1: base template + dynamic publisher/book fields)
  - Build `/api/outreach/draft` endpoint — generates email via Gemini, creates Gmail draft,
    saves `outreach_draft_id`, returns draft link
  - Add "Generate Draft in Gmail" button to publisher card — shows "Draft ready" link on success
  - Add "Mark as Sent" button — sets `outreach_date`, advances status to `IN_DISCUSSION`
  - Build daily follow-up job — checks `IN_DISCUSSION` records past 7 days, no `followup_draft_sent_at`,
    generates follow-up draft, pushes to Gmail, sets `followup_draft_sent_at`
  - Add `prompt_versions` logging — record which prompt version was used per email sent
  - Add response rate display to Settings screen
- **Build AI creative partner chat widget (ADR 0002):**
  - Add Gemini chat component to Publisher Licenses and Campaign Queue screens
  - System prompt seeds assistant with writing style and voice of confirmed top 3 BookTok
    romance/romantasy authors: **Sarah J. Maas, Rebecca Yarros, Colleen Hoover** (confirmed
    2026-03-02 — review annually as BookTok landscape evolves)
  - Widget is read-only assistance — no database writes, no pipeline triggers
  - Partner copies suggestions manually into emails or captions
- TEST: Full end-to-end — book discovered, enriched, scripted, moderated, rendered, appears
  in queue, downloaded. Also test: contact discovery → confirm → generate draft → verify in
  Gmail → mark sent → verify 7-day follow-up fires.

---

## 09 — Collaboration Map

Every touchpoint between technical and non-technical roles.

ReelForge depends on two distinct domains of work. The pipeline cannot function at full
capacity without both. These are the specific handoff points.

| Collaboration Area | Technical | Partner (Non-Technical) |
|---|---|---|
| Publisher Licensing | Build publisher_licenses UI per selected framework. Wire approved licenses to cover_cleared_for_use flag. | Contact publishers. Log responses. Upload licensed cover assets to the tool. Mark approvals. |
| UI Framework Selection | Build whichever framework she selects from the review document. | Review 3 frameworks, select preferred, provide feedback on what's missing. |
| Content Calendar Review | Build calendar view and cadence health indicator. Expose scheduling recommendations. | Review weekly queue. Confirm posting schedule in Meta Business Suite. Mark as SCHEDULED. |
| Moderation Overrides | Build override workflow with required human_note field. Surface MODERATION_FAILED clearly. | Review flagged content. Make override/edit/reject decision. Write reason note. |
| Music Library Curation | Build music_library schema and auto-selection logic. Create upload workflow. | Listen to candidate tracks. Confirm mood mappings feel right for the content. |
| Performance Feedback | Build manual performance entry screen. Wire data to scoring model over time. | Log video performance from Meta Business Suite weekly. Note what resonates with audience. |
| Seed Book Curation | Build seed_books admin screen. Write import logic. | Suggest known BookTok titles to pre-seed the system before first discovery run. |
| Caption Review | Build caption display in READY state. FTC disclosure auto-injected. | Review generated captions before downloading. Request edits if tone is off. |
| UI Feedback | Build annotation toggle and feedback drawer. Review feedback table. | Leave notes on any screen that is confusing or missing something needed. |

---

## 10 — Compliance and Legal Checklist

Items that must be resolved before public launch.

| Requirement | Owner | Status |
|---|---|---|
| FTC affiliate disclosure in first 100 chars of every caption | System (auto) | Build into Gemini prompt template |
| Amazon Associates terms compliance — no false product claims | Moderation gate | Gemini check + human review |
| Book cover images only from publisher-licensed or author-provided sources | Publisher license workflow | Partner tracks in tool — Open Library NOT a valid source |
| Meta Reels content policy — no explicit content in thumbnails | Cloud Vision gate | Automated + human override |
| At least 1 publisher license secured before launch | Partner | Outreach in progress |
| Amazon Associates account approved and 3 qualifying sales made within 180 days | You | Apply during Phase 0 — apply early |
| Google Cloud APIs — usage within free tier limits | You | Rate limit manager in SQS |
| Music tracks confirmed no-attribution commercial license before adding to library | You | Review each track at Phase 0 seed |
| IP attorney review of cover usage policy before scaling to multiple tenants | Both | Pre-scale milestone |

---

**Next Step:** Phase 0 setup runs in parallel with the UI framework decision. The two blocking
items before Phase 1 begins are: (1) Supabase project created and connection strings documented,
and (2) partner's UI framework selection returned so the Publisher Licenses screen is designed
correctly from the start.
