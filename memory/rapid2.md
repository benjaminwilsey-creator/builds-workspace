# Rapid2 — OpenClaw Trading Bot

## Overview
Multi-tier crypto trading bot for Kraken exchange, controlled via Telegram, running on AWS EC2 under systemd.

## Versions
| Version | Path | Status |
|---------|------|--------|
| v1 (Retired) | `Builds\Rapid2\rapid2 (Program)\` | EC2 instance terminated 2026-03-04 |
| v1.2 (Production) | `Builds\Rapid2\rapid2 v1.2\` | Live on EC2, real money — now runs v1.3 regime code (deployed 2026-03-25) |
| v1.3 (Paper) | `Builds\Rapid2\rapid2 v1.3\` | Paper bot live on EC2 2026-03-22; also deployed to live bot 2026-03-25 |

## Tech Stack
- v1.2: Python 3.12, ccxt, python-telegram-bot, apscheduler, python-dotenv, boto3
- v1.3: Python 3.12, ccxt, python-telegram-bot, apscheduler, python-dotenv, requests (boto3 dropped)

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

## Signal System — v1.2 (score 0–5)
1. **CryptoCompare** — Reddit posts_per_hour (>= 2.0) + active_users (>= 200)
2. **CoinGecko** — trending coins list (no key required)
3. **Reddit** — mention spike ratio, public JSON API, unauthenticated
4. **Volume** — 3x 7-day average daily volume
5. **RSI** — RSI-14 on 1h candles > 60

**T3 entry requires score >= 3 | T2 entry requires score >= 4**
**Position sizing:** 1 signal = $3.60, 2 signals = $5, 3+ signals = $8

## Signal System — v1.3 (price action, no scoring)
**Primary triggers** (either fires an entry candidate):
- EMA 9/21 crossover on 15m chart
- Breakout above consolidation range

**Confirmation layer** (all must pass):
- Volume above average
- RSI-14 not overbought
- MACD crossed above signal on 1h
- Price above 50 EMA (trend filter)
- Swing low bounce check

**Regime system** (market-wide, drives entry/exit behavior):
- Fear & Greed Index (alternative.me, free, no key) — score 0–100
- 5 regimes: EXTREME_FEAR (0-20), FEAR (21-40), NEUTRAL (41-60), GREED (61-80), EXTREME_GREED (81-100)
- Contrarian: fear = accumulation opportunity, greed = defense/block
- EXTREME_GREED blocks all new entries; EXTREME_FEAR widens RSI bands, waives MACD, allows downtrend
- Position sizing scaled by regime: 50% during Extreme Fear, 75% Fear, 100% Neutral, 75% Greed, 0% Extreme Greed

**Additional signals** (free, no API keys):
- BTC 200-day MA distance — % below 200 EMA signals accumulation zone (threshold: -25%)
- Capitulation volume — 3x+ avg volume on red candles = potential bounce
- During EXTREME_FEAR, Gate 7 requires at least one of: swing low bounce, capitulation volume, BTC near 200MA

**Exit adjustments by regime:**
- Trailing stops tighten 50% during GREED/EXTREME_GREED
- Max hold days extend 50% during FEAR/EXTREME_FEAR

**Tiers:** ANCHOR (BTC/ETH) | MID_CAP (SOL/AVAX/LINK etc.) | DUST (memes)
**Exit ladder:** TP1=40% out, TP2=40% out, trailing 20% remainder

## Concentration Rules (added 2026-03-06)
- `TIER2_MAX_SINGLE_PCT = 0.20` — no more than 20% of account in any one T2 coin
- Concentration check uses **live Kraken balance** (not just tracked POSITIONS) — catches coins held but not tracked
- Consolidation is also blocked if the projected post-buy % would exceed the cap
- Coins on TIER2_WATCHLIST priced below $1 get loaded as T3 on startup (e.g. HBAR at $0.10) — managed by trailing stop not TP/SL

## EC2 (shared instance — both versions run here)
- Instance: t2.micro, Ubuntu, us-east-2
- IP: `3.138.144.246` — SSH alias: `rapid2`

### Old `openclaw` service — STOPPED & DISABLED (2026-03-25)
- Was running from `/home/ubuntu/rapid2/` (v1 code) — caused Telegram conflicts
- `sudo systemctl stop openclaw && sudo systemctl disable openclaw`

### v1.2 (live trading — real money, now running v1.3 code)
- Service: `openclaw-paper` → `/home/ubuntu/rapid2-v1.2/bot.py`
- Venv: `/home/ubuntu/rapid2-v1.2/.venv/bin/python`
- Logs: `ssh rapid2 "sudo journalctl -u openclaw-paper -n 50 --no-pager"`

### v1.3 (paper trading — validation)
- Service: `openclaw-paper-v1.3` → `/home/ubuntu/rapid2-v1.3/paper_bot.py`
- Venv: `/home/ubuntu/rapid2-v1.3/.venv/bin/python`
- Logs: `ssh rapid2 "sudo journalctl -u openclaw-paper-v1.3 -n 50 --no-pager"`
- Deploy: `bash deploy.sh paper` (from v1.3 local folder)

## GitHub
- v1.2 (production): https://github.com/benjaminwilsey-creator/openclaw-v1.2
- v1 (retired): https://github.com/benjaminwilsey-creator/openclaw-v1
- Account: benjaminwilsey-creator

## Quick Flip Mode (added 2026-03-26 — LOCAL ONLY, not deployed)
Toggle via `/mode` Telegram command. Sprint strategy to grow $116 → $300 through rapid small wins.

**Status:** Code complete in strategy.py, bot.py, paper_bot.py. Backtest showed entry gates too strict (3 trades in 8 days, all SL hits). Needs tuning before deploy.

**Parameters:**
- TP: +6% (nets ~5.5% after fees) | SL: -2% | Max hold: 24h
- Max 2 positions at 45% account each
- Entry: volatility ≥3% + (pullback to 9 EMA OR EMA 9/21 crossover) + RSI 42-58 + volume ≥1.5x
- Scan interval: 60s (vs 180s regime) | Scans MID_CAP + ANCHOR, ranked by volatility
- Kill switch: 3 consecutive losses or 10% drawdown → auto-revert to regime mode

**New functions in strategy.py:** `qf_reset_tracking()`, `qf_record_trade_result()`, `qf_should_kill_switch()`, `get_recent_volatility()`, `detect_pullback_to_ema()`, `build_quick_flip_signals()`, `evaluate_quick_flip_entry()`, `evaluate_quick_flip_exit()`, `format_quick_flip_entry_alert()` + `QuickFlipSignals`, `QuickFlipDecision` dataclasses

## Telegram Commands (live bot, bot.py)
`/status`, `/positions`, `/portfolio`, `/watchlist`, `/pause`, `/resume`, `/report`, `/mode`, `/help`

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
- `load_dotenv()` must be called BEFORE importing any local module that calls `os.getenv()` at module level — fixed in v1.3 paper_bot.py; verify in bot.py too if issues arise
- LunarCrush fully replaced — `lunarcrush.py` deleted, `sentiment.py` uses free Fear & Greed API (alternative.me). No API key needed.
- Existing positions loaded from v1.2 state file classify as `tier=dust` — new entries use proper tier classification
- Kraken API key has IP whitelist — if server IP changes, must update in Kraken dashboard before bot can connect
- Entry prices on startup are set to current market price (not actual cost basis) — P&L display starts from restart
- Dust positions (sub-penny balances like BONK, FLOKI dust) are silently skipped on sell — harmless, logged as WARNING
- Reddit scraping (unauthenticated, v1.2 only) is best-effort — may break without warning
- EC2 security group SSH rule must allow your current IP — update in AWS console if connection times out
- **Kraken+ zero fees do NOT apply to API trades** — only app/web Buy/Sell/Convert. Bot pays 0.16% maker / 0.26% taker via ccxt. TP targets must account for ~0.4-0.5% round-trip fee drag.
- **MATIC/USD rebranded to POL/USD on Kraken** — update watchlists if MATIC is referenced
- **Kraken OHLCV 15m data capped at ~720 candles (~8 days)** — for backtesting, use Binance (USDT pairs) which paginates properly. Prices are nearly identical for major coins.
