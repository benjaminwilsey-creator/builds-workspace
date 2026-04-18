---
name: EC2 bot deploy state + pending fixes
description: Current EC2 state as of 2026-04-18 — QF mode active, thresholds tuned, local strategy.py out of sync, BEAM/LINK/USDG lot-minimum fix still pending
type: project
originSessionId: d3f08e11-e9fa-454a-a64e-797cf6b2e776
---
## Current EC2 State (as of 2026-04-18)

**Server:** ubuntu@3.138.144.246 (ssh alias: rapid2)
**Service:** `openclaw-paper.service` (mis-named — this IS the live trading bot)
**Directory:** `/home/ubuntu/rapid2-v1.2/`
**Bot is LIVE and running real money.**
**Mode: Quick Flip (QF)**

### What's deployed:
- `bot.py` — v1.3 code (has `strat.Tier` enum, `ALL_WATCHLISTS`, `execute_sell_partial`)
- `strategy.py` — v1.3 QF mode. Key QF config values (as of 2026-04-18):
  - `QF_MIN_VOLATILITY_PCT = 0.02` (lowered from 0.03 on 2026-04-18)
  - `VOLUME_CONFIRM_MULTIPLIER = 1.2` (lowered from 1.5 on 2026-04-18)
  - `MIN_ORDER_USD = 3.80`

### Local strategy.py is OUT OF SYNC:
- `e:/Builds - Copy/Rapid2/rapid2 v1.3/strategy.py` still has old values (vol=0.03, volume_mult=1.5)
- EC2 is the authoritative source — sync local file before making further edits

### What the `.bak` files are:
- `bot.py.bak` and `strategy.py.bak` in the EC2 directory are OLD v1.2. Do NOT restore.

---

## EC2 Gotchas

**scp key must be specified explicitly:**
- `ssh rapid2` (alias) works fine
- `scp ubuntu@3.138.144.246:...` fails with "Permission denied (publickey)"
- Fix: `scp -i "C:/Users/benja/OneDrive/Documents/KeePass/AWS/rapid2-key.pem" ubuntu@3.138.144.246:...`

**Diagnostic script:**
- `/tmp/qf_diag2.py` on EC2 — shows live gate readings (vol, RSI, volume ratio, trigger) for all QF symbols
- Run: `ssh rapid2 "python3 /tmp/qf_diag2.py"`

---

## Pending Fix — Kraken Lot-Minimum (BEAM/LINK/USDG)

**Problem:** BEAM, LINK, and USDG are rejected by Kraken every cycle:
```
[SELL] BEAM/USD failed: kraken {"error":["EGeneral:Invalid arguments:volume minimum not met"]}
```
Dollar value passes `MIN_ORDER_USD` check, but token *quantity* is below Kraken's per-coin minimum. These can **never** be sold. Bot retries every 180 seconds forever.

**Fix:** In EC2's `/home/ubuntu/rapid2-v1.2/bot.py`, modify both `execute_sell` (~line 293) and `execute_sell_partial` (~line 347) — catch "volume minimum not met" and remove position from tracking.

### execute_sell — change except block to:
```python
    except Exception as e:
        if "volume minimum not met" in str(e):
            logger.warning(f"[SELL] {symbol} — lot minimum not met, removing from tracking")
            if symbol in strat.POSITIONS:
                del strat.POSITIONS[symbol]
                _save_positions()
        else:
            logger.error(f"[SELL] {symbol} failed: {e}")
        return None
```

### execute_sell_partial — change except block to:
```python
    except Exception as e:
        if "volume minimum not met" in str(e):
            logger.warning(f"[SELL-PARTIAL] {symbol} — lot minimum not met, removing from tracking")
            if symbol in strat.POSITIONS:
                del strat.POSITIONS[symbol]
                _save_positions()
        else:
            logger.error(f"[SELL-PARTIAL] {symbol} failed: {e}")
        return None
```

### Workflow:
1. `scp -i "C:/Users/benja/OneDrive/Documents/KeePass/AWS/rapid2-key.pem" ubuntu@3.138.144.246:/home/ubuntu/rapid2-v1.2/bot.py "e:/Builds - Copy/Rapid2/rapid2 v1.3/bot_ec2.py"`
2. Apply the two edits above
3. `scp` it back to `/home/ubuntu/rapid2-v1.2/bot.py`
4. `ssh rapid2 "sudo systemctl restart openclaw-paper.service"`
5. Wait one cycle (180s), check logs — BEAM/LINK/USDG should be gone
