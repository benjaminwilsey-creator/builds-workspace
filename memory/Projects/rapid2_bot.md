---
name: EC2 bot deploy state
description: v1.3 live on EC2 QF mode (real money) | v1.4 spec written, 6 tracks queued + remote trigger fired overnight
type: project
originSessionId: 0ab1bf2a-022f-4db9-ba88-87b31eac5439
---
## Current EC2 State (v1.3 — LIVE)

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
- `e:/Builds - Copy/Rapid2/rapid2 v1.3/strategy.py` — MAY BE OUT OF SYNC (local may still have old vol=0.03, volume_mult=1.5). Pull from EC2 before editing.

### EC2 Gotchas:
- scp alias works fine: `scp rapid2:/path/to/file local_dest`
- Bare IP `ubuntu@3.138.144.246` fails with "Permission denied (publickey)" — always use `rapid2` alias
- Diagnostic script: `ssh rapid2 "python3 /tmp/qf_diag2.py"` — live gate readings

---

## v1.3 — Tests Added (2026-04-24)

**54 tests now exist** — `pytest tests/ -v` runs green (54/54) with no network calls.
- `tests/test_strategy.py` — 42 unit tests: regime, classify, risk floor, exits, DCA, QF kill switch
- `tests/test_smoke.py` — 12 behavioral tests: full trade lifecycle (entry → TP1 → TP2 → trail → exit)
- Run: `py -3 -m pytest tests/ -v` from inside `rapid2 v1.3/` — use `py -3`, not `python` (venv conflict on this machine)

**Paper trade started: 2026-04-24 — review due 2026-05-08**
- Run `python paper_bot.py` from `rapid2 v1.3/` (uses `PAPER_TELEGRAM_TOKEN` env var)
- Logs: `logs/paper_bot.log` and `state/paper_state.json`
- Review on 2026-05-08: win rate, avg PnL, circuit breaker events, compare vs EC2 live
- If v1.4 tracks complete by then: start v1.4 paper clock

## v1.4 — In Build (as of 2026-04-20)

**Status:** Spec written. 6 tasks queued. Remote trigger fired 2026-04-20.
**Confirmed 2026-04-24: `rapid2 v1.4/` directory does NOT exist** — trigger may not have completed all tracks. Check #claude-agent on Slack and verify before assuming build ran.
**v1.3 is untouched** — v1.4 builds in parallel in a new directory.

### Architecture decided: Core + Satellite
Evidence-based redesign. Multi-agent orchestrator deferred to $300+ account.

**Core (70% of account) — Enhanced Fear-DCA:**
- Weekly buys: $4 BTC/USD + $4 ETH/USD
- F&G < 25 → 2× buy size. F&G < 15 → 3× buy size.
- Top filter: skip buys when BTC > 50% above 200MA AND F&G ≥ 25
- Never sells — accumulation only

**Satellite (30% of account) — Mean-Reversion on BTC only:**
- Entry: RSI(14) on 4h ≤ 35 + price touches lower Bollinger Band (20, 2σ) + green confirmation candle
- Filter: only trade when BTC above 200-day MA
- TP: +8%, SL: −4%, max hold: 72h
- One position at a time, 100% of satellite capital (no conviction sizing)

**Circuit breaker:**
- Account < $70 → pause satellite, Core keeps running
- Account < $50 → Telegram alert, manual decision required

**Scan interval:** 900s (15 min) — not 60s

### Spec file:
`e:/Builds - Copy/Rapid2/v1.4_SPEC.md` — authoritative source of truth for all v1.4 sub-agents

### Task queue:
6 TRACK-R14 tracks in `e:/Builds - Copy/tasks.md` (Lite Conductor format, single-phase).
Remote trigger created and fired 2026-04-20:
- **Trigger ID:** `trig_01JvBvCBLs2qWSBksPRsfj2C`
- **Schedule:** 4am UTC nightly (safety net — disable after tracks complete)
- **Manage at:** https://claude.ai/code/scheduled/trig_01JvBvCBLs2qWSBksPRsfj2C

### After overnight run:
1. Check #claude-agent on Slack for branch names and results
2. `git checkout agent/track-r14-001-phase1-2026-04-20` to review work
3. Merge what looks good, then paper-trade for 2 weeks before live deploy
4. **Disable the nightly trigger** once all 6 tracks are done

### Oracle Cloud migration (not yet done):
Strongly recommended before v1.4 goes live. Oracle Cloud Free Tier = free forever.
Removes the $12/mo AWS burn entirely — the bot no longer needs to earn to survive.
**Why:** How to apply: do this before deploying v1.4 live.
