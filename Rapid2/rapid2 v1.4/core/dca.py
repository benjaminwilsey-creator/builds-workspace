"""Enhanced Fear-DCA logic for Core tier.

Pure function: evaluate_dca(...) -> DCADecision.
No side effects. All config as module constants per spec §5 and §12.
"""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ── Constants (single source of truth per spec §12) ──────────────────────────
CORE_BASE_AMOUNT_USD = 4.00
CORE_INTERVAL_HOURS = 168.0          # Weekly
CORE_FNG_15_MULT = 3.0               # F&G < 15 multiplier
CORE_FNG_25_MULT = 2.0               # 15 <= F&G < 25 multiplier
CORE_TOP_FILTER_PCT = 0.50           # Skip buys when BTC > 50% above 200MA (unless fear)
CORE_MIN_ORDER_USD = 3.80            # Kraken minimum


@dataclass(frozen=True)
class DCADecision:
    should_buy: bool
    symbol: str
    amount_usd: float       # 0.0 if should_buy is False
    reason: str


def evaluate_dca(
    symbol: str,
    fng_score: float,
    btc_pct_above_200ma: float,
    last_buy_ts: float,
    now_ts: float,
    base_amount_usd: float = CORE_BASE_AMOUNT_USD,
    interval_hours: float = CORE_INTERVAL_HOURS,
) -> DCADecision:
    """Evaluate whether a DCA buy should occur and for how much.

    Spec §5 logic (exact):
    1. Interval gate: skip if interval not elapsed.
    2. Top filter: skip if BTC > 50% above 200MA AND F&G >= 25.
    3. F&G multiplier: <15 → 3x, 15–24 → 2x, else 1x.
    4. Enforce Kraken minimum $3.80.
    """
    # 1. Interval gate
    if now_ts - last_buy_ts < interval_hours * 3600:
        return DCADecision(
            should_buy=False,
            symbol=symbol,
            amount_usd=0.0,
            reason="Interval not elapsed",
        )

    # 2. Top filter (fear overrides — only skip in non-fear conditions)
    if btc_pct_above_200ma > CORE_TOP_FILTER_PCT and fng_score >= 25:
        return DCADecision(
            should_buy=False,
            symbol=symbol,
            amount_usd=0.0,
            reason=f"Top filter: BTC {btc_pct_above_200ma:.0%} above 200MA with F&G={fng_score:.0f}",
        )

    # 3. F&G multiplier
    if fng_score < 15:
        multiplier = CORE_FNG_15_MULT
    elif fng_score < 25:
        multiplier = CORE_FNG_25_MULT
    else:
        multiplier = 1.0

    amount_usd = base_amount_usd * multiplier

    # 4. Kraken minimum
    if amount_usd < CORE_MIN_ORDER_USD:
        return DCADecision(
            should_buy=False,
            symbol=symbol,
            amount_usd=0.0,
            reason=f"Amount ${amount_usd:.2f} below Kraken minimum ${CORE_MIN_ORDER_USD:.2f}",
        )

    return DCADecision(
        should_buy=True,
        symbol=symbol,
        amount_usd=amount_usd,
        reason=f"DCA buy: F&G={fng_score:.0f}, multiplier={multiplier:.1f}x, amount=${amount_usd:.2f}",
    )
