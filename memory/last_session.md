---
date: 2026-03-28
project: Rapid2
---

## What we did
- Implemented 5 Extreme Fear regime overrides in v1.3 strategy: guard threshold raised to 85%, stop losses widened (ANCHOR 15%, MID_CAP 18%), DUST entries blocked, volume gate lowered to 1.2x
- Deployed all changes to the live bot (openclaw-paper) — guard now passes at 83% losing (was permanently blocked before)
- Fixed deploy.sh — live deploy was missing bot.py; now uploads bot.py, strategy.py, sentiment.py
- Removed Rapid2/ from root .gitignore — documentation files now tracked in builds-workspace on GitHub

## Current bot state
- Live bot: F&G score 12 (Extreme Fear), guard passing at 83% < 85% threshold, actively scanning
- BTC at ~$66,789 — 22.5% below 200MA (deep accumulation zone per Gate 7)
- No stop losses fired — all positions still within range
- Paper bot (v1.3): same regime changes deployed via `bash deploy.sh paper`

## Next up
- Investigate CryptoCompare 0 coin IDs — API key is set but social signals not loading on either bot
- Monitor whether regime changes produce entries during current Extreme Fear period

## Watch out for
- Local `rapid2 v1.2/` folder is NOT what deploys — live bot runs from v1.3 folder only; don't edit v1.2 thinking it'll go live
- deploy.sh live targets `/home/ubuntu/rapid2-v1.2/` but uploads v1.3 code — naming is confusing but correct
