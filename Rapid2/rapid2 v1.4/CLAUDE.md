# CLAUDE.md — Rapid2 v1.4

## Scope
Rules here apply only to Rapid2 v1.4.
Global rules inherited from `e:/Builds - Copy/CLAUDE.md`.
**Status:** in development — not deployed. v1.3 is live.

## Architecture
v1.4 is a Core + Satellite system:
- **Core (70%)**: Enhanced Fear-DCA into BTC+ETH. Weekly. Boosted in fear.
- **Satellite (30%)**: Mean-reversion agent on BTC only. One strategy, one coin.
- **Capital module**: Circuit breaker — pauses satellite below $70.

See `e:/Builds - Copy/Rapid2/v1.4_SPEC.md` for the full authoritative spec.

## Files
| File | Responsibility |
|------|----------------|
| `bot.py` | Kraken, Telegram, execution loop — NO strategy logic |
| `strategy.py` | Orchestrator — calls agents, applies breaker, returns decision |
| `core/dca.py` | Pure function: enhanced Fear-DCA decision |
| `agents/base.py` | AgentContext + AgentSignal dataclasses |
| `agents/mean_reversion.py` | Pure function: mean-reversion agent |
| `capital.py` | CapitalState + circuit breaker thresholds |
| `paper_bot.py` | Paper trading harness |
| `tests/` | pytest — every pure function must have tests |

## Rules specific to v1.4
- **Never deploy to EC2 without Benjamin's explicit approval.** v1.3 is live on EC2.
- **No live money runs during development** — use `paper_bot.py` only.
- **Every agent is a pure function** — `evaluate(ctx) -> AgentSignal`. No I/O except OHLCV via ctx.exchange.
- **No conviction-based sizing** — satellite is 100% of satellite capital, one position at a time.
- **No new agents in v1.4** — mean-reversion only. Revisit at $300+ account.

## Env vars required (.env)
```
KRAKEN_API_KEY
KRAKEN_API_SECRET
TELEGRAM_TOKEN            ← live bot token (not used until deploy — optional in dev)
PAPER_TELEGRAM_TOKEN      ← paper bot — separate from live
TELEGRAM_CHAT_ID
PAPER_STARTING_USD=90     ← paper starting balance (optional)
```
