# Rapid2 — OpenClaw Trading Bot

## Overview
Multi-tier crypto trading bot for Kraken exchange, controlled via Telegram, running on AWS EC2 under systemd.

## Versions
| Version | Path | Status |
|---------|------|--------|
| v1 (Retired) | `Builds\Rapid2\rapid2 (Program)\` | EC2 instance terminated 2026-03-04 |
| v1.2 (Production) | `Builds\Rapid2\rapid2 v1.2\` | Live on EC2, real money — replaced v1 |
| v1.3 (In progress?) | Unknown — C drive | Branch exists somewhere on C drive; check GitHub (openclaw-v1.2 repo) for v1.3 branch and search `C:\Users\benja\OneDrive\Documents\Builds\Rapid2\` — locate before building new features |

## Tech Stack
- Python 3.12, ccxt, python-telegram-bot v20+ (async), apscheduler, python-dotenv, boto3

## Key Files (v1.2)
- **bot.py** — Live trading infrastructure (Kraken connection, order execution, Telegram, load_dotenv). Refactored 2026-03-06: scan_and_enter split into _scan_tier3 + _scan_tier2; load_existing_positions split into _classify_tier + _build_position
- **paper_bot.py** — Paper trading bot (simulated trades, same signals) — still on server but not running
- **strategy.py** — All signal logic: CryptoCompare, CoinGecko, Reddit, volume; position sizing; exits
- **pyproject.toml** — Ruff + pytest configuration
- **.pre-commit-config.yaml** — detect-secrets, ruff, hygiene hooks
- **tests/test_strategy.py** — Smoke tests (pure unit, no network)

## Architecture Pattern
Clean separation: bot.py = infrastructure only, strategy.py = logic only.
To tune strategy: edit strategy.py only.

## 3-Tier Strategy (updated 2026-03-11 — strategy overhaul commit 11957e0)
| Tier | Target | Assets | Key Logic |
|------|--------|--------|-----------|
| T1 Stable | 50% | BTC/ETH | Hold anchor, no active trading |
| T2 Mid-cap | 30% | $0.10–$15 altcoins | Social + technical signals, TP 15%, SL 7% |
| T3 Micro-cap | 20% | Dust/<$1 coins | ATR-based trailing stop (2x 10-day ATR, fallback 15%) |

Allocation was flipped from 15/35/50 → 50/30/20 — most capital now in safest tier.

## Signal System (5 signals, score 0–5)
1. **CryptoCompare** — Reddit posts_per_hour (>= 2.0) + active_users (>= 200)
   - Two-step lookup: coinId from `/data/all/coinlist` (cached in `_CC_ID_CACHE`), then `/data/social/coin/latest`
   - `_CC_LIST_FETCHED` sentinel prevents retry storms if coin list fetch fails on startup
2. **CoinGecko** — trending coins list (no key required)
3. **Reddit** — mention spike ratio, public JSON API, unauthenticated
4. **Volume** — 3x 7-day average daily volume
5. **RSI** — RSI-14 on 1h candles > 60 (new — momentum confirmation)

**T3 entry requires score >= 3** (was 2 out of 4)
**T2 entry requires score >= 4** (was same out of 4)
**Position sizing:** 1 signal = $3.60, 2 signals = $5, 3+ signals = $8 (reduced from $4/$7/$12)
**T3 max positions: 3** (was 6)
**Social thresholds raised:** posts_per_hour 0.5 → 2.0, active_users 50 → 200

## Concentration Rules (added 2026-03-06)
- `TIER2_MAX_SINGLE_PCT = 0.20` — no more than 20% of account in any one T2 coin
- Concentration check uses **live Kraken balance** (not just tracked POSITIONS) — catches coins held but not tracked
- Consolidation is also blocked if the projected post-buy % would exceed the cap
- Coins on TIER2_WATCHLIST priced below $1 get loaded as T3 on startup (e.g. HBAR at $0.10) — managed by trailing stop not TP/SL

## EC2 — v1.2 (Production)
- Instance: t2.micro, Ubuntu, us-east-2
- IP: `3.138.144.246` — SSH alias: `rapid2`
- Service: `openclaw-paper` (name unchanged even though it now runs bot.py / live trading)
- Deploy path: `/home/ubuntu/rapid2-v1.2/`
- Venv: `/home/ubuntu/rapid2-v1.2/.venv/bin/python`
- Logs: `ssh rapid2 "sudo journalctl -u openclaw-paper.service -n 50 --no-pager"`
- `openclaw.service` (stale v1 code) was found running alongside v1.2 on 2026-03-06 — stopped + disabled

## GitHub
- v1.2 (production): https://github.com/benjaminwilsey-creator/openclaw-v1.2
- v1 (retired): https://github.com/benjaminwilsey-creator/openclaw-v1
- Account: benjaminwilsey-creator

## Telegram Commands (live bot, bot.py)
`/status`, `/positions`, `/portfolio`, `/watchlist`, `/pause`, `/resume`, `/report`, `/help`

## New Functions (strategy overhaul 2026-03-11)
- `get_rsi_signal(exchange, symbol)` — fetches 16 x 1h OHLCV candles, calculates RSI-14 (Wilder's smoothing), returns True if RSI > 60
- `calculate_atr(exchange, symbol)` — fetches 11 x 1d OHLCV candles, calculates 10-day ATR (true range formula)
- `calculate_atr_stop(exchange, symbol, peak_price)` — returns stop price = peak - (2 × ATR); falls back to fixed 15% stop if fewer than 7 daily candles available
- `tier3_update_trailing_stop()` now accepts `exchange` param and calls `calculate_atr_stop()` instead of fixed 25%

## Cleanup TODO (from /review, not blocking)
- `scan_and_enter()` is 130 lines (limit: 40) — extract T2/T3 scan blocks into helpers
- 4 bare `except:pass` blocks in bot.py (lines ~192, 363, 381, 589) — silently swallow errors, should log
- Several magic numbers (0.0001 dust, anti-chase 1.05, score thresholds 3/4) should be CONFIG constants

## Known Issues / Gotchas
- Service still named `openclaw-paper.service` even though it runs `bot.py` (live trading) — low priority rename
- `bot.py` requires `load_dotenv()` before `os.getenv()` calls — systemd does NOT inherit shell env vars, so missing this silently uses fallback placeholders. Already fixed in current code.
- Kraken API key has IP whitelist — if server IP changes, must update in Kraken dashboard before bot can connect
- Entry prices on startup are set to current market price (not actual cost basis) — P&L display starts from restart
- `_CC_LIST_FETCHED` resets on restart — CryptoCompare coin list fetched fresh each boot
- Reddit scraping (unauthenticated) is best-effort — may break without warning
- Dust positions (sub-penny balances like BONK, FLOKI dust) are silently skipped on sell — harmless, logged as WARNING
