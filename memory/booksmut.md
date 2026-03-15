# Booksmut — ReelForge

## Overview
Automated BookTok affiliate content pipeline. Discovers trending romance/romantasy books,
generates 30-second video reels (FFmpeg + Google TTS + Gemini scripts), delivers download-ready
videos with Amazon affiliate captions for human scheduling in Meta Business Suite.

Two-person project: developer (Benjamin) + non-technical partner (publisher licensing lead).

## Status
Phase 0 (account setup) **nearly complete** as of 2026-03-15.
No code written yet. Phase 1 (Database & Auth) is next.

### Phase 0 Completion
- [x] Amazon Associates — applied
- [x] NYT Books API — approved
- [x] Supabase — project created
- [x] Cloudflare R2 — bucket + CORS configured
- [x] Vercel — project created
- [x] Google Cloud APIs — enabled (Books, TTS, Vision, Gmail) via gcloud CLI
- [x] Gemini API — key created
- [x] Hardcover.app — account created
- [x] Gmail OAuth — consent screen + Client ID configured
- [x] Meta Business Suite — confirmed
- [x] Partner UI framework — Framework B selected (ADR 0001)
- [ ] Music library seed — 20+ tracks needed (Pixabay / YouTube Audio Library, no CC-BY)
- [ ] Google app verification — confirm submitted (1–4 week wait, blocks Phase 6)
- [~] Reddit API — **dropped for this build** (API access process changed)

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

## Open Items Before Phase 0
- [x] Top 3 BookTok romance/romantasy authors confirmed: **Sarah J. Maas, Rebecca Yarros, Colleen Hoover** (2026-03-02)
- [ ] Confirm Meta accounts (Facebook Page + Instagram Business) are set up and in good standing
- [ ] Apply for Amazon Associates account early — 3 qualifying sales required within 180 days
- [ ] Apply for Google app verification early — Gmail OAuth requires approval, takes 1–4 weeks; must be done in Phase 0 to avoid blocking Phase 6

## Tech Stack (updated 2026-03-15 — AWS replaced by Google Cloud)
Supabase · Cloudflare R2 · **Google Cloud Functions + Pub/Sub + Cloud Scheduler** · Gemini API · Google TTS + Vision ·
FFmpeg · Vercel + Next.js + shadcn/ui · Amazon Associates · Hardcover.app · NYT Books API ·
Gmail API (gmail.compose scope only) · Google OAuth 2.0 via next-auth

AWS dropped entirely. Reddit API dropped for this build. See ADR 0004.

## Known Risks (must not be forgotten)
- **Open Library covers are NOT cleared for commercial use** — backdrop fallback only when no licensed cover
- **Supabase free tier pauses after 7 days inactivity** — GitHub Actions keep-alive cron required in Phase 0
- **Cloud Scheduler triggers discovery Cloud Functions** — Pub/Sub is for inter-stage queuing only
- **Music library: CC0 and no-attribution tracks only** — CC-BY excluded (attribution not feasible at scale)
- **Amazon Associates: 3 qualifying sales within 180 days** — apply early, get sales before pipeline goes live
- **Gmail OAuth requires Google app verification** — gmail.compose scope only, but Google must approve the app for production use beyond test users (1–4 week review). Apply in Phase 0.
