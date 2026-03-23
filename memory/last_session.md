---
date: 2026-03-22
project: Rapid2 v1.3
---

## What we did
- Deployed v1.3 to EC2 for the first time — paper bot is now running alongside v1.2 live bot on separate systemd services
- Fixed a bug where the sentiment API key wasn't loading, then replaced LunarCrush with the free Fear & Greed Index

## Next up
- Monitor v1.3 paper bot performance — check signals are firing and trades look sensible
- Once paper results look good, flip v1.3 to live trading (update openclaw-paper service)

## Watch out for
- Fear & Greed score is 8 (Extreme Fear) — sentiment gate is blocking all MID_CAP and DUST entries on v1.3 until market recovers above 50
