# Rapid2 — OpenClaw Trading Bot

## Overview
Multi-tier crypto trading bot for Kraken exchange, controlled via Telegram, running on AWS EC2 under systemd.

## Versions
| Version | Path | Status |
|---------|------|--------|
| v1 (Production) | `Builds\Rapid2\rapid2 (Program)\` | Live on EC2, real money |
| v1.2 (Development) | `Builds\Rapid2\rapid2 v1.2\` | Paper trading on EC2 |

## Tech Stack
- Python 3.12, ccxt, pandas, pandas-ta, python-telegram-bot v20+ (async), apscheduler, python-dotenv, boto3

## Key Files (v1.2)
- **bot.py** — Live trading infrastructure (Kraken connection, order execution, Telegram)
- **paper_bot.py** — Paper trading bot (simulated trades, same signals); T3 uses dynamic Kraken discovery via `get_kraken_t3_candidates()` — no static watchlist
- **strategy.py** — All signal logic: LunarCrush, CoinGecko, Reddit, volume; position sizing; exits
- **pyproject.toml** — Ruff + pytest configuration
- **.pre-commit-config.yaml** — detect-secrets, ruff, hygiene hooks
- **tests/test_strategy.py** — 30 smoke tests (all pure unit, no network)
- **.github/workflows/ci.yml** — Ruff lint + pytest on push to master
- **state/paper_state.json** — Persisted paper state (positions, cash, starting_value)

## Architecture Pattern
Clean separation: bot.py/paper_bot.py = infrastructure only, strategy.py = logic only.
To tune strategy: edit strategy.py only.

## 3-Tier Strategy
| Tier | Target | Assets | Key Logic |
|------|--------|--------|-----------|
| T1 Stable | 15% | BTC only | Hold anchor, no active trading |
| T2 Mid-cap | 35% | $0.10–$15 altcoins | Social + technical signals, TP 15%, SL 7% |
| T3 Micro-cap | 50% | Dust/<$1 coins | Ratcheting trailing stop (25% → 15% after +100%) |

## Signal System (4 signals, score 0–4)
1. **LunarCrush** — social score + AltRank improvement (requires paid plan ~$19/mo)
2. **CoinGecko** — trending coins list
3. **Reddit** — mention spike ratio (public API, no auth needed)
4. **Volume** — 24h volume threshold

## EC2 — v1 (Production)
- Instance: t2.micro, Ubuntu, us-east-2
- IP: `3.131.96.193` (Elastic IP)
- SSH: `ssh -i "C:\Users\benja\OneDrive\Documents\KeePass\AWS\rapid2-key.pem" ubuntu@3.131.96.193`
- Service: `openclaw`
- Deploy path: `/home/ubuntu/rapid2/`

## EC2 — v1.2 (Paper Trading)
- Instance: t2.micro, Ubuntu, us-east-2
- IP: `3.138.144.246` — SSH alias: `rapid2`
- Service: `openclaw-paper`
- Deploy path: `/home/ubuntu/rapid2-v1.2/`
- State: `/home/ubuntu/rapid2-v1.2/state/paper_state.json`
- S3 backup: `s3://open-state-yourname/paper_state.json` (IAM role: `open1-ec2-s3`)
- Venv: `/home/ubuntu/rapid2-v1.2/.venv/bin/python`

## GitHub
- v1: https://github.com/benjaminwilsey-creator/openclaw-v1
- v1.2: https://github.com/benjaminwilsey-creator/openclaw-v1.2
- Account: benjaminwilsey-creator

## Telegram Commands (paper bot)
`/status`, `/positions`, `/pause`, `/resume`, `/report`, `/reset`, `/help`

## Known Issues
- LunarCrush signal silently off (returns False) until Individual plan subscribed
- `btc_crash_active` not persisted across restarts
- praw in requirements.txt but not used (Reddit runs via public JSON API instead)
- `TIER3_PRICE_MIN` config value ($0.00001) defined but never enforced in `tier3_entry_signal()` — minor bug
- Production v1 EC2 (3.131.96.193) unreachable via SSH for multiple sessions — likely stopped in AWS console
- Telegram bot token visible in systemd journal logs via httpx debug URL logging — low risk, worth cleaning up
