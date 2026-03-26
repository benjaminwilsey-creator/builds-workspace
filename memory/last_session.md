---
date: 2026-03-26
project: Rapid2 v1.3 — Quick Flip Mode
---

## What we did
- Built Quick Flip mode — a sprint trading strategy (6% TP / 2% SL / 24h max hold) toggled via /mode command
- Discovered Kraken+ zero fees don't cover API trades — bot actually pays 0.16%/0.26% maker/taker
- Ran first backtest — only 3 trades in 8 days, all hit stop loss, kill switch triggered immediately

## Next up
- Run backtest v2 with 30 days of Binance data (script written, not yet executed)
- Analyze gate diagnostics to find which entry filter is too strict and tune it
- Deploy to paper bot only after backtest shows positive edge

## Watch out for
- All Quick Flip code is LOCAL ONLY — nothing deployed to EC2 yet
- Backtest v2 script at C:\Users\benja\AppData\Local\Temp\backtest_qf.py ready to run
