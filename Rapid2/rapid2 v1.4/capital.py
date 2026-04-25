"""Capital module — circuit breaker and account state tracking.

Purpose: prevent the satellite from trading when the account is unhealthy.
NOT used for sizing. See spec §7.
"""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ── Thresholds (module constants, spec §7 and §12) ────────────────────────────
CAP_SAT_PAUSE_THRESHOLD = 70.0   # USD — satellite paused below this
CAP_ALERT_FLOOR = 50.0           # USD — Telegram alert below this
CAP_FLOOR = 20.0                 # USD — hard floor for runway calc
CAP_MONTHLY_BURN = 12.0          # USD — fixed monthly burn estimate


@dataclass(frozen=True)
class CapitalState:
    total_value: float
    core_value: float
    satellite_value: float
    satellite_enabled: bool      # False when below pause threshold
    alert_floor_breached: bool   # True when below $50
    runway_months: float         # (total - floor) / monthly_burn, clamped to >= 0
    reason: str


def compute_state(
    total_value: float,
    core_fraction: float = 0.70,
    sat_fraction: float = 0.30,
) -> CapitalState:
    """Compute the current capital state from total account value.

    Spec §7 logic:
    - core_value = total_value * core_fraction
    - satellite_value = total_value * sat_fraction
    - satellite_enabled = total_value >= CAP_SAT_PAUSE_THRESHOLD
    - alert_floor_breached = total_value < CAP_ALERT_FLOOR
    - runway_months = max(0.0, (total_value - CAP_FLOOR) / CAP_MONTHLY_BURN)
    """
    core_value = total_value * core_fraction
    satellite_value = total_value * sat_fraction
    satellite_enabled = total_value >= CAP_SAT_PAUSE_THRESHOLD
    alert_floor_breached = total_value < CAP_ALERT_FLOOR
    runway_months = max(0.0, (total_value - CAP_FLOOR) / CAP_MONTHLY_BURN)

    if alert_floor_breached:
        reason = f"ALERT: account ${total_value:.2f} below floor ${CAP_ALERT_FLOOR:.2f}"
    elif not satellite_enabled:
        reason = f"Satellite paused: account ${total_value:.2f} below ${CAP_SAT_PAUSE_THRESHOLD:.2f}"
    else:
        reason = f"Account healthy: ${total_value:.2f}, satellite enabled"

    logger.debug(
        "[capital] total=%.2f core=%.2f sat=%.2f enabled=%s alert=%s runway=%.2fm",
        total_value, core_value, satellite_value,
        satellite_enabled, alert_floor_breached, runway_months,
    )

    return CapitalState(
        total_value=total_value,
        core_value=core_value,
        satellite_value=satellite_value,
        satellite_enabled=satellite_enabled,
        alert_floor_breached=alert_floor_breached,
        runway_months=runway_months,
        reason=reason,
    )
