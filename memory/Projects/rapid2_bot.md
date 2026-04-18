---
name: EC2 bot deploy state
description: Current EC2 state as of 2026-04-17 — v1.3 deployed, lot-minimum fix live, local files in sync
type: project
originSessionId: 0ab1bf2a-022f-4db9-ba88-87b31eac5439
---
## Current EC2 State (as of 2026-04-17)

**Server:** ubuntu@3.138.144.246 (ssh alias: rapid2)
**Service:** `openclaw-paper.service` (mis-named — this IS the live trading bot)
**Directory:** `/home/ubuntu/rapid2-v1.2/`
**Bot is LIVE and running real money.**
**Mode: Quick Flip (QF)**

### What's deployed:
- `bot.py` — v1.3 code. Has `strat.Tier` enum, `ALL_WATCHLISTS`, `execute_sell_partial`, and lot-minimum fix in both `execute_sell` and `execute_sell_partial`
- `strategy.py` — v1.3 QF mode. Key QF config values (as of 2026-04-18):
  - `QF_MIN_VOLATILITY_PCT = 0.02` (lowered from 0.03 on 2026-04-18)
  - `VOLUME_CONFIRM_MULTIPLIER = 1.2` (lowered from 1.5 on 2026-04-18)
  - `MIN_ORDER_USD = 3.80`

### Local files:
- `e:/Builds - Copy/Rapid2/rapid2 v1.3/bot.py` — IN SYNC with EC2
- `e:/Builds - Copy/Rapid2/rapid2 v1.3/strategy.py` — MAY BE OUT OF SYNC (local may still have old vol=0.03, volume_mult=1.5 values). Pull from EC2 before editing.

### What the `.bak` files are:
- `bot.py.bak` and `strategy.py.bak` in the EC2 directory are OLD v1.2. Do NOT restore.

---

## EC2 Gotchas

**scp alias works fine:**
- `scp rapid2:/path/to/file local_dest` — works with no extra flags
- `scp ubuntu@3.138.144.246:...` (bare IP without alias) fails with "Permission denied (publickey)"
- Always use the `rapid2` alias

**Diagnostic script:**
- `/tmp/qf_diag2.py` on EC2 — shows live gate readings (vol, RSI, volume ratio, trigger) for all QF symbols
- Run: `ssh rapid2 "python3 /tmp/qf_diag2.py"`
