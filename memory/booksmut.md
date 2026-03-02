# Booksmut — ReelForge

## Overview
Automated BookTok affiliate content pipeline. Discovers trending romance/romantasy books,
generates 30-second video reels (FFmpeg + Google TTS + Gemini scripts), delivers download-ready
videos with Amazon affiliate captions for human scheduling in Meta Business Suite.

Two-person project: developer (Benjamin) + non-technical partner (publisher licensing lead).

## Status
Design phase **complete**. Phase 0 (account setup) ready to start.
No code written yet. All architectural decisions locked.

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

## Partner UI Answers (Framework Review)
- **Framework selected:** B — Dashboard + Focus Mode
- **One word for the tool:** Efficient
- **Distraction trigger:** Thinking of other things that need to be done
- **Missing feature:** AI creative partner in the style of top 3 BookTok romance authors
- **Tool that feels good:** Checklists
- **Design implication:** Borrow Framework C mini-checklists into Framework B publisher cards

## Open Items Before Phase 0
- [ ] Agree on "top 3 BookTok romance/romantasy authors" — needed for AI agent system prompt (Phase 6)
- [ ] Confirm Meta accounts (Facebook Page + Instagram Business) are set up and in good standing
- [ ] Apply for Amazon Associates account early — 3 qualifying sales required within 180 days

## Tech Stack (all locked — see Technical Guide v2 for full detail)
Supabase · Cloudflare R2 · AWS Lambda + SQS + SES · Gemini API · Google TTS + Vision ·
FFmpeg · Vercel + Next.js + shadcn/ui · Amazon Associates · Hardcover.app · Reddit API · NYT Books API

## Known Risks (must not be forgotten)
- **Open Library covers are NOT cleared for commercial use** — backdrop fallback only when no licensed cover
- **Supabase free tier pauses after 7 days inactivity** — GitHub Actions keep-alive cron required in Phase 0
- **Lambda /tmp defaults to 512 MB** — compositor Lambda must be set to 2048 MB explicitly
- **EventBridge Scheduled Rules trigger discovery Lambdas** — not SQS (SQS is for inter-stage queuing only)
- **Music library: CC0 and no-attribution tracks only** — CC-BY excluded (attribution not feasible at scale)
- **Amazon Associates: 3 qualifying sales within 180 days** — apply early, get sales before pipeline goes live
