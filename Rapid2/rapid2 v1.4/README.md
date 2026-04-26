# Rapid2 v1.4 — Core + Satellite

v1.4 replaces v1.3's monolithic regime/QF strategy with a **Core + Satellite** split on a $90 account.

## Architecture

```
bot.py (Execution Engine)
  └── strategy.decide()
        ├── capital.compute_state()    → circuit breaker
        ├── core/dca.evaluate_dca()   → weekly BTC+ETH buys, fear-boosted
        └── agents/mean_reversion.evaluate()  → BTC mean-reversion signal
```

- **Core (70% of account)**: Enhanced Fear-DCA. Buys BTC/USD and ETH/USD weekly. Boosts buy size when Fear & Greed is low. Skips buys when BTC is far above its 200-day MA in greed conditions.
- **Satellite (30% of account)**: Mean-reversion agent on BTC/USD only. Buys when RSI < 35 + Bollinger Band lower touch + green confirmation candle, AND BTC is above its 200-day MA. One position at a time.
- **Capital module**: Pauses the satellite if the total account drops below $70. Alerts below $50.

## Quick Start (Paper Trading)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy env template and fill in values
cp .env.example .env
# Edit .env — only PAPER_TELEGRAM_TOKEN and TELEGRAM_CHAT_ID needed for full paper loop
# No Kraken API key needed for --dry-run

# 3. Dry-run: one decision cycle, log it, exit
python paper_bot.py --dry-run

# 4. Full paper loop (requires PAPER_TELEGRAM_TOKEN + TELEGRAM_CHAT_ID)
python paper_bot.py
```

## Running Tests

```bash
pytest tests/ -v
```

## Status

- v1.3 is **live on EC2** with real money.
- v1.4 is **in development** — paper-trade only until Benjamin approves live deploy.
- Live deploy is **not part of v1.4 scope** — that is v1.4.1 after 2+ weeks of paper validation.

## Key Files

| File | Purpose |
|------|---------|
| `paper_bot.py` | Paper trading harness — start here |
| `bot.py` | Live execution engine — DO NOT run without approval |
| `strategy.py` | Orchestrator — wires capital, DCA, and agent |
| `capital.py` | Circuit breaker and account health |
| `core/dca.py` | Enhanced Fear-DCA logic |
| `agents/mean_reversion.py` | BTC mean-reversion signal logic |
| `tests/` | pytest test suite |
| `logs/paper_trades.csv` | Simulated trade log (created on first run) |
