---
date: 2026-03-26
project: Rapid2 v1.3 — Quick Flip Mode + TIER_MAP Bug Fix
---

## What we did
- Built Quick Flip mode (6% TP / 2% SL / 24h hold) with /mode toggle — backtest showed entry gates too strict
- Found critical TIER_MAP bug — bot was classifying ALL coins as dust because the map used Kraken symbols not CCXT symbols. Fixed locally.

## Next up
- Deploy TIER_MAP fix to EC2 (both live and paper bots) — this is the highest priority, it affects real money
- Run backtest v2 with 30 days of Binance data (script ready at Temp\backtest_qf.py)
- Tune Quick Flip entry gates based on backtest diagnostics

## Watch out for
- TIER_MAP fix is LOCAL ONLY — not deployed yet. Live bot is still misclassifying everything as dust.
