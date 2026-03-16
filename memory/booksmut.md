# Booksmut — ReelForge

## Overview
Automated BookTok affiliate content pipeline. Discovers trending romance/romantasy books,
generates 30-second video reels (FFmpeg + Google TTS + Gemini scripts), delivers download-ready
videos with Amazon affiliate captions for human scheduling in Meta Business Suite.

Two-person project: developer (Benjamin) + non-technical partner (publisher licensing lead).

## Status
Phase 0 **complete**. Phase 1 database **complete**. Phase 2 discovery pipeline **partially deployed** as of 2026-03-15.
- `nyt-fetcher` Cloud Function deployed and working — fetches NYT Best Sellers + enriches via Hardcover inline
- 34 books confirmed ENRICHED in Supabase (status = ENRICHED, genre/description/tags populated)
- Cleanup pending: delete defunct `hardcover-enricher` Cloud Function + `book-discovered` Pub/Sub topic
Next: Step 2-2 Scorer function (reads ENRICHED books, calculates score, sets status to SCORED)

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

### Phase 2 — In Progress
- [x] `nyt-fetcher` Cloud Function deployed (Gen 2, HTTP trigger, us-central1)
- [x] Enrichment merged inline — no separate enricher function, no Pub/Sub
- [x] 34 books discovered and enriched end-to-end confirmed
- [ ] Delete defunct `hardcover-enricher` Cloud Function
- [ ] Delete defunct `book-discovered` Pub/Sub topic
- [ ] Step 2-2: Scorer function
- [ ] Step 2-3: Queue selector

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

## GCP Secrets (in Secret Manager)
| Secret | Purpose |
|--------|---------|
| `NYT_API_KEY` | NYT Books API |
| `SUPABASE_URI` | Session Pooler connection string |
| `TENANT_ID` | ReelForge tenant UUID |
| `HARDCOVER_TOKEN` | Hardcover.app Bearer token |

Service account: `reelforge-api-runner` — has secretAccessor on all four secrets above.

## GCP Deployment Gotchas
- **allUsers Cloud Run IAM resets on every deploy** — after each `gcloud functions deploy`, must re-run: `gcloud run services add-iam-policy-binding nyt-fetcher --region=us-central1 --member="allUsers" --role="roles/run.invoker"`
- **Windows line endings in secrets** — `echo` and `printf` in PowerShell can add `\r\n` to secrets. Use `printf` in PowerShell/Windows Terminal. `_get_secret()` calls `.strip()` as a defensive fix.
- **Hardcover API**: `search.results` is a JSON scalar (Typesense response), not a typed GraphQL union. Parse `results.hits[0].document` in Python. `query_type` must be `"BOOK"` (string, not enum).
- **PowerShell `curl`** — PowerShell aliases `curl` to `Invoke-WebRequest`. Use `curl.exe` explicitly.

## Known Risks (must not be forgotten)
- **Open Library covers are NOT cleared for commercial use** — backdrop fallback only when no licensed cover
- **Supabase free tier pauses after 7 days inactivity** — GitHub Actions keep-alive cron required in Phase 0
- **Cloud Scheduler triggers discovery Cloud Functions** — Pub/Sub is for inter-stage queuing only
- **Music library: CC0 and no-attribution tracks only** — CC-BY excluded (attribution not feasible at scale)
- **Amazon Associates: 3 qualifying sales within 180 days** — apply early, get sales before pipeline goes live
- **Gmail OAuth requires Google app verification** — gmail.compose scope only, but Google must approve the app for production use beyond test users (1–4 week review). Apply in Phase 0.
