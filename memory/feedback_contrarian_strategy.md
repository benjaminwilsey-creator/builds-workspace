---
name: Contrarian strategy philosophy
description: Rapid2 v1.3 flips fear/greed — Extreme Fear is accumulation, not a blocker. Regime system drives all entry/exit logic.
type: feedback
---

Fear = opportunity, greed = defense. The old approach (sentiment gate blocking entries when F&G < 50) was backwards — it prevented buying during the best accumulation windows.

**Why:** Benjamin wants a contrarian strategy. The bot should lean INTO fear (with confirmation signals) and pull back during greed. This matches his "reset phase, mostly cash" situation where catching fear-driven dips is the priority.

**How to apply:** Never suggest blocking entries during fear periods. Any future strategy tuning should preserve the contrarian philosophy: low F&G = widen entry criteria, high F&G = tighten or block. The 5-regime system (EXTREME_FEAR → EXTREME_GREED) is the mechanism — don't revert to simple threshold gates.
