---
name: EC2 bot deploy state + pending Kraken lot-minimum fix
description: Current EC2 state after 2026-04-14 session — v1.3 strategy.py deployed, pending fix for BEAM/LINK/USDG Kraken lot-minimum errors in bot.py
type: project
originSessionId: 0ab1bf2a-022f-4db9-ba88-87b31eac5439
---
## Current EC2 State (as of 2026-04-14)

**Server:** ubuntu@3.138.144.246 (ssh alias: rapid2)
**Service:** `openclaw-paper.service` (mis-named — this IS the live trading bot)
**Directory:** `/home/ubuntu/rapid2-v1.2/`
**Bot is LIVE and running real money.**

### What's deployed:
- `bot.py` — v1.3 code (has `strat.Tier` enum, `ALL_WATCHLISTS`, `execute_sell_partial`)
- `strategy.py` — v1.3 code, just deployed 2026-04-14. `MIN_ORDER_USD = 3.80` (raised from 3.60)
- The local v1.2 CLAUDE.md is outdated — EC2 was already running v1.3 bot.py before this session

### What the `.bak` files are:
- `bot.py.bak` and `strategy.py.bak` in the EC2 directory are the OLD v1.2 versions. Do NOT restore them.

---

## Pending Fix — Option 2 (next task after compact)

**Problem:** BEAM, LINK, and USDG hit Kraken API every cycle and get rejected:
```
[SELL] BEAM/USD failed: kraken {"error":["EGeneral:Invalid arguments:volume minimum not met"]}
[SELL] LINK/USD failed: kraken {"error":["EGeneral:Invalid arguments:volume minimum not met"]}
[SELL] USDG/USD failed: kraken {"error":["EGeneral:Invalid arguments:volume minimum not met"]}
```
These coins have dollar values above $3.80 (pass MIN_ORDER_USD check) but their token *quantity* is below Kraken's per-coin minimum lot size. They can **never** be sold. The bot retries every 180 seconds forever.

**Fix:** In EC2's `/home/ubuntu/rapid2-v1.2/bot.py`, modify both `execute_sell` (line 251) and `execute_sell_partial` (line 299) — in the `except Exception as e:` block, detect the Kraken error string and remove the position from tracking instead of logging an error.

### Exact code change for `execute_sell` (around line 293):

**Before:**
```python
    except Exception as e:
        logger.error(f"[SELL] {symbol} failed: {e}")
        return None
```

**After:**
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

### Exact code change for `execute_sell_partial` (around line 347):

**Before:**
```python
    except Exception as e:
        logger.error(f"[SELL-PARTIAL] {symbol} failed: {e}")
        return None
```

**After:**
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

### Workflow to apply:
1. `scp ubuntu@3.138.144.246:/home/ubuntu/rapid2-v1.2/bot.py "e:/Builds - Copy/Rapid2/rapid2 v1.3/bot_ec2.py"` — pull EC2 bot.py to a temp local file
2. Apply the two edits above
3. `scp` it back to `/home/ubuntu/rapid2-v1.2/bot.py`
4. `ssh rapid2 "sudo systemctl restart openclaw-paper.service"`
5. Wait one cycle (180s) and check logs — BEAM/LINK/USDG should disappear from logs after first run

**Why:** The position is unexitable (Kraken permanently rejects). Retrying every cycle wastes API calls and pollutes logs. Removing from tracking is correct — the coin stays in the Kraken account as dust, the bot just stops managing it.
