---
date: 2026-04-17
project: Rapid2 (live bot)
originSessionId: 0ab1bf2a-022f-4db9-ba88-87b31eac5439
---
## What we did
- Applied the Kraken lot-minimum fix to the live bot — BEAM, LINK, and USDG now get silently removed from tracking instead of erroring every 3 minutes forever
- Synced local bot.py to match EC2 (they were out of sync after the fix)

## Next up
- No pending fixes — bot is clean, local files match EC2

## Watch out for
- Local strategy.py may still be out of sync with EC2 QF tuning (vol=0.02, volume_mult=1.2)
