---
date: 2026-04-18
project: Rapid2 (live bot)
originSessionId: d3f08e11-e9fa-454a-a64e-797cf6b2e776
---
## What we did
- Diagnosed why Quick Flip mode hadn't triggered any buys in 3 days — the volatility gate (3%) was blocking all 16 coins in the current quiet market
- Lowered two QF thresholds on the live EC2 bot: volatility gate from 3% → 2%, volume multiplier from 1.5x → 1.2x

## Next up
- Apply the BEAM/LINK/USDG lot-minimum fix to EC2's bot.py (full code in rapid2_bot.md)
- Sync local strategy.py with EC2 values (vol=0.02, volume_mult=1.2)

## Watch out for
- Local strategy.py is out of sync with EC2 — don't push it or you'll overwrite the tuned config
- scp requires explicit key path (see rapid2_bot.md gotchas)
