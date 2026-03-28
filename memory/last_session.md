---
date: 2026-03-28
project: Rapid2
---

## What we did
- Committed all uncommitted v1.3 work (social signals, regime strategy, Quick Flip, TIER_MAP fix)
- Fixed deploy.sh — was restarting wrong service (openclaw instead of openclaw-paper)
- Stopped and disabled rogue `openclaw` service that was causing Telegram conflicts
- Increased CryptoCompare cache TTL from 2h to 4h — combined usage now ~9,360/month (free tier: 11,000)
- Added CryptoCompare API key to both EC2 .env files — social features now active
- Fixed portfolio guard permanently stuck in defensive mode — dust positions (sub-$3.60) were
  being counted as "losing" but can never be sold. Guard now only counts positions >= $3.60 (Kraken minimum)

## Current bot state
- Live bot (openclaw-paper): 6 tradeable positions, 5/6 losing — correctly in defensive mode
- Paper bot (openclaw-paper-v1.3): running, same guard logic applied
- Fear & Greed: 12 (Extreme Fear)
- BTC at ~$66,674 — closest to stop ($64,812), 2.7% buffer remaining
- No stop losses have triggered yet — all positions within range

## Regime strategy tuning — NEXT STEPS (plan after /compact)
Priority order — do NOT implement until planned:

1. **Make guard regime-aware** — during EXTREME_FEAR, raise losing ratio threshold from 60% → 85%
   (or disable it, leaving only drawdown + exposure checks). Guard contradiction: contrarian logic
   says accumulate in fear, but guard blocks all entries when everything is losing in a crash.

2. **Widen stop losses during Extreme Fear** — current 7-12% stops are within volatility noise range.
   During EXTREME_FEAR regime, widen to 15-20% to survive whipsaws before the bounce.

3. **Restrict Extreme Fear entries to ANCHOR + MID_CAP only** — no DUST entries during crashes.
   Meme coins die hardest, recover slowest. BTC/ETH/SOL/LINK lead recoveries.

4. **Reduce volume gate during Extreme Fear** — Gate 4 requires above-average volume. Early
   recoveries start on low volume. Lower requirement from 1.5x → 1.2x during EXTREME_FEAR.

5. **Gate 7 is correct — do not change** — swing low OR capitulation volume OR BTC near 200MA
   is good discipline. Prevents buying a falling knife.

## Watch out for
- BTC stop at $64,812 — watch if BTC drops toward $65k
- Quick Flip mode is local only, NOT deployed, backtest was poor (3 trades, all SL hits) —
  do NOT deploy in current market. Needs a sideways-to-up market with clear momentum.
- v1.3 branch is named `1.3try` on GitHub (not `develop` as memory previously said)
- Both bots now correctly on 4h CryptoCompare cache
