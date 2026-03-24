# Booksmut — ReelForge

## Overview
Automated BookTok affiliate content pipeline. Discovers trending romance/romantasy books,
generates 30-second video reels (FFmpeg + Google TTS + Gemini scripts), delivers download-ready
videos with Amazon affiliate captions for human scheduling in Meta Business Suite.

Two-person project: developer (Benjamin) + non-technical partner (publisher licensing lead).

## Status
Phase 0 **complete**. Phase 1 database **complete**. Phase 2 pipeline **complete — all steps** as of 2026-03-23.
- Full pipeline working: ENRICHED → SCORED → CAMPAIGN_DRAFT → SCRIPTED → MODERATION_SCRIPT → VOICED → COMPOSED → PUBLISHED
- Moderation UI live at: `https://benjaminwilsey-creator.github.io/builds-workspace/`
- Tabs: Script Review (SCRIPTED), Video Compose (VOICED), Delivery (COMPOSED), Publishers (publisher_licenses)
- ~10 campaigns in VOICED state need composing (were blocked by bugs now fixed)
- Publisher Licenses tab live as of 2026-03-23: dashboard + focus mode, ADR 0001 Framework B design, RLS policies added
Next: compose VOICED campaigns, then Gmail outreach integration (ADR 0003) — "Generate Draft" button on publisher card

### Known video-composer bugs fixed (2026-03-23)
- Cloudflare 403: switched `urllib` to `requests` with Mozilla User-Agent
- FFmpeg filter crash on single quotes in text: replaced `\'` escaping with Unicode `\u2019`

### Phase 0 — Complete
- [x] Amazon Associates — tag: `thesecretpic-20` (Elizabeth Wilsey account)
- [x] NYT Books API — approved
- [x] Supabase — project created, Session Pooler URI saved (IPv4 compatible)
- [x] Cloudflare R2 — bucket + CORS configured for reelforge-seven.vercel.app
- [x] Vercel — deployed at `reelforge-seven.vercel.app`
- [x] Google Cloud APIs — enabled (Books, TTS, Vision, Gmail)
- [x] Google Cloud Service Account — `reelforge-api-runner` created, key file saved
- [x] Gemini API — key created (Google AI Studio, not Cloud Console)
- [x] Hardcover.app — account created
- [x] Gmail OAuth — consent screen configured, partner added as test user (no Workspace needed)
- [x] Music library seed — 20+ tracks saved to CSV (Pixabay / YouTube Audio Library, CC0/no-attribution only)
- [x] Reddit API — **dropped for this build** (API access process changed)
- [ ] Google app verification — 1–4 week wait, blocks Phase 6 Gmail OAuth in production

### Phase 1 — Complete
- [x] All 16 tables created in Supabase SQL Editor
- [x] Row Level Security enabled on all tenant-scoped tables
- [x] First tenant created: ReelForge / thesecretpic-20
- [x] Owner user linked

### Phase 2 — Complete
- [x] `nyt-fetcher` Cloud Function deployed (Gen 2, HTTP trigger, us-central1)
- [x] Enrichment merged inline — no separate enricher function, no Pub/Sub
- [x] 34 books discovered and enriched end-to-end confirmed
- [ ] Delete defunct `hardcover-enricher` Cloud Function (cleanup — not urgent)
- [ ] Delete defunct `book-discovered` Pub/Sub topic (cleanup — not urgent)
- [x] Step 2-2: Scorer function — deployed, scheduler set (Monday 8:05am)
- [x] Step 2-3: Queue selector — deployed, scheduler set (Monday 8:10am)
- [x] Step 3: Script generator — deployed, Gemini 2.5-flash, scheduler set (Monday 8:15am)
- [x] Step 4: Moderation UI — live on GitHub Pages, anon key + RLS

## GitHub Repo
- URL: https://github.com/benjaminwilsey-creator/reelforge
- Branch: `main`
- Local path: `e:\Builds - Copy\Booksmut\` (moved from OneDrive permanently 2026-03-15)
- Codespaces configured: yes (`.devcontainer/devcontainer.json`, Node.js 20)

## Key File Paths
| File | Purpose |
|------|---------|
| `Booksmut/Documentation/Build up to UI/ReelForge-Technical-Guide-v2.md` | Source-of-truth technical spec (v2, corrected) |
| `Booksmut/Documentation/Build up to UI/ReelForge-Technical-Guide-v2.docx` | Word version of above |
| `Booksmut/Documentation/Build up to UI/ReelForge-Partner-Guide.docx` | Non-technical partner guide (no corrections needed) |
| `Booksmut/Documentation/Build up to UI/ReelForge-UI-Framework-Review.odt` | Partner's framework selection + answers |
| `Booksmut/docs/decisions/` | ADR files |

## ADRs Written
| # | Decision |
|---|----------|
| 0001 | Publisher Licenses UI: Framework B selected (Dashboard + Focus Mode + mini-checklists) |
| 0002 | AI creative partner chat widget added to Phase 6 (Gemini, style of top 3 BookTok authors) |
| 0003 | Semi-automated publisher outreach: Gemini drafts → Gmail API pushes draft → partner clicks Send. Contact discovery accuracy-gated to full auto at ≥98% over 50 confirmed runs. |
| 0004 | Infrastructure: AWS replaced by Google Cloud (Functions + Pub/Sub + Cloud Scheduler), set up via gcloud CLI. Reddit API dropped for this build. |

## Partner UI Answers (Framework Review)
- **Framework selected:** B — Dashboard + Focus Mode
- **One word for the tool:** Efficient
- **Distraction trigger:** Thinking of other things that need to be done
- **Missing feature:** AI creative partner in the style of top 3 BookTok romance authors
- **Tool that feels good:** Checklists
- **Design implication:** Borrow Framework C mini-checklists into Framework B publisher cards


## Tech Stack (updated 2026-03-15 — AWS replaced by Google Cloud)
Supabase · Cloudflare R2 · **Google Cloud Functions + Cloud Scheduler** · Gemini API · Google TTS + Vision ·
FFmpeg · Vercel + Next.js + shadcn/ui · Amazon Associates · Hardcover.app · NYT Books API ·
Gmail API (gmail.compose scope only) · Google OAuth 2.0 via next-auth

AWS dropped entirely. Reddit API dropped for this build. Pub/Sub not used in current pipeline (may be introduced in later phases). See ADR 0004.

## Service Account Map
| Service | Login | Notes |
|---------|-------|-------|
| GitHub | `benjaminwilsey-creator` | Repos: builds-workspace, reelforge |
| Google Cloud Console | `benjaminwilsey@gmail.com` | GCP project, Cloud Functions, Scheduler, Secret Manager |
| Google AI Studio (Gemini) | `benjaminwilsey@gmail.com` | Gemini API key lives here |
| Supabase | `benjaminwilsey@gmail.com` | Database, RLS, anon key |
| Vercel | `benjaminwilsey@gmail.com` | reelforge-seven.vercel.app |
| NYT Books API | `benjaminwilsey@gmail.com` | Trending book discovery |
| Cloudflare R2 | `book.fun.x@gmail.com` | Bucket: booksmut-videos |
| Hardcover.app | `book.fun.x@gmail.com` | Book metadata |
| Amazon Associates | Elizabeth Wilsey account | Tag: thesecretpic-20 |
| GitHub Pages | `benjaminwilsey-creator` | Moderation UI |

## GCP Secrets (in Secret Manager)
| Secret | Purpose |
|--------|---------|
| `NYT_API_KEY` | NYT Books API |
| `SUPABASE_URI` | Session Pooler connection string |
| `TENANT_ID` | ReelForge tenant UUID |
| `HARDCOVER_TOKEN` | Hardcover.app Bearer token |
| `GEMINI_API_KEY` | Gemini API (Google AI Studio) |
| `R2_ACCOUNT_ID` | Cloudflare R2 account ID |
| `R2_ACCESS_KEY_ID` | R2 API token key ID |
| `R2_SECRET_ACCESS_KEY` | R2 API token secret |

Service account: `reelforge-api-runner` — has secretAccessor on all secrets above.

## Cloud Run Env Vars (set via gcloud run services update — not in Secret Manager)
| Function | Var | Value |
|----------|-----|-------|
| tts-voicer | `GCP_PROJECT` | `project-fa5cd39b-46df-4f2a-808` |
| tts-voicer | `R2_BUCKET_NAME` | `booksmut-videos` |
| tts-voicer | `R2_PUBLIC_URL_BASE` | `https://pub-8352f6299ee54879bb0e492bc9e8b662.r2.dev` |

## Deployed Cloud Functions
| Function | URL | Trigger | Schedule |
|----------|-----|---------|----------|
| tts-voicer | `https://tts-voicer-kfxuvvfhqa-uc.a.run.app` | Cloud Scheduler | Monday 8:20am |

## GCP Deployment Gotchas
- **allUsers Cloud Run IAM resets on every deploy** — after each `gcloud functions deploy`, must re-run: `gcloud run services add-iam-policy-binding <function-name> --region=us-central1 --member="allUsers" --role="roles/run.invoker"`
- **Windows line endings in secrets** — `echo` and `printf` in PowerShell can add `\r\n` to secrets. Use `printf` in PowerShell/Windows Terminal. `_get_secret()` calls `.strip()` as a defensive fix.
- **Hardcover API**: `search.results` is a JSON scalar (Typesense response), not a typed GraphQL union. Parse `results.hits[0].document` in Python. `query_type` must be `"BOOK"` (string, not enum).
- **PowerShell `curl`** — PowerShell aliases `curl` to `Invoke-WebRequest`. Use `curl.exe` explicitly, or use `Invoke-WebRequest -UseBasicParsing`.
- **Gemini model**: current working model is `gemini-2.5-flash`. Both `gemini-1.5-flash` and `gemini-2.0-flash` retired March 2026.
- **Gemini SDK**: use `google-genai>=1.0` (`from google import genai`). The `google-generativeai` package is fully deprecated.
- **supabase-js v2 + anon key**: v2 requires the legacy `eyJ...` JWT format. The newer `sb_publishable_...` format only works with v3.
- **campaign_parts has no updated_at column** — omit it from any UPDATE queries on that table.
- **PowerShell --set-env-vars merges comma-separated values** — all values collapse into one corrupted env var. Always use `gcloud run services update --update-env-vars "KEY=VALUE"` one at a time instead.

## Moderation UI
- URL: `https://benjaminwilsey-creator.github.io/builds-workspace/`
- Source: `docs/index.html` in builds-workspace repo — deployed via GitHub Actions on every push to master
- Auth: anon key stored in browser localStorage (never committed). To reset: `localStorage.removeItem('rf-anon-key')` in browser console
- RLS policies: SELECT + UPDATE on `campaigns` and `campaign_parts` for anon role; SELECT + INSERT + UPDATE on `publisher_licenses` for anon role
- `tone_note text` column added to campaigns table — stores regeneration guidance per campaign
- Script Review cards show a collapsible "About this book" description — pulled from `books.description`, collapsed by default

## Known Risks (must not be forgotten)
- **Open Library covers are NOT cleared for commercial use** — backdrop fallback only when no licensed cover
- **Supabase free tier pauses after 7 days inactivity** — GitHub Actions keep-alive cron required in Phase 0
- **Cloud Scheduler triggers discovery Cloud Functions** — Pub/Sub is for inter-stage queuing only
- **Music library: CC0 and no-attribution tracks only** — CC-BY excluded (attribution not feasible at scale)
- **Amazon Associates: 3 qualifying sales within 180 days** — apply early, get sales before pipeline goes live
- **Gmail OAuth requires Google app verification** — gmail.compose scope only, but Google must approve the app for production use beyond test users (1–4 week review). Apply in Phase 0.
