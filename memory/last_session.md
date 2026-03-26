---
date: 2026-03-25
project: Rapid2 v1.3 — Regime Strategy + Live Deploy
---

## What we did
- Built a 5-regime trading strategy driven by Fear & Greed Index — flips from "fear blocks entries" to "fear = accumulation opportunity"
- Added BTC 200-day MA distance and capitulation volume as free confirmation signals (no new API keys needed)
- Replaced lunarcrush.py with sentiment.py (free Fear & Greed API, no key required)
- Deployed v1.3 code to BOTH paper bot and live bot on EC2 — live bot is in reset phase, mostly cash
- Discovered and disabled orphaned `openclaw` service that was causing Telegram conflicts

## Next up
- Monitor bot logs over next few scan cycles to see regime-aware entries/exits in action
- Check if existing positions (loaded as tier=dust) trigger regime-aware exit logic correctly
- Consider S3 state backup (still on planned improvements list)

## Watch out for
- All 18 existing positions loaded as tier=dust due to v1.2 state file format — new entries will classify correctly
- F&G was 10 (Extreme Fear) and BTC was -18% below 200MA at deploy time — bot should be evaluating entries
