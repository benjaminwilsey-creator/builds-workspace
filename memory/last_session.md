---
date: 2026-03-26
project: Rapid2
---

## What we did
- Built 3-layer CryptoCompare social signal integration into v1.3 strategy (watchlist ranking, momentum bonus, dead-coin gate) and deployed to both live and paper bots
- Diagnosed historic CryptoCompare API overage as coming from v1.2 era — v1.3 makes zero CryptoCompare calls

## Next up
- Get a fresh CryptoCompare free API key from cryptocompare.com
- Update both EC2 .env files with the new key, then restart both services
- Verify logs show "[Social] Loaded 19000+ CryptoCompare coin IDs" after restart

## Watch out for
- Social features are SILENTLY INACTIVE on both bots — expired API key, not a code bug
- Confirm TIER_MAP fix is live by checking that new entries log correct tiers (not DUST)
