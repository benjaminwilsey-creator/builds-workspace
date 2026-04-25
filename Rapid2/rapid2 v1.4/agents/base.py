from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class AgentContext:
    """Everything an agent needs to make a decision. Immutable."""
    exchange:                   Any         # ccxt exchange instance (Kraken)
    symbol:                     str         # e.g. "BTC/USD"
    current_price:              float
    account_value:              float       # Total account USD
    satellite_capital:          float       # USD allocated to the satellite tier
    open_satellite_position:    dict | None  # {"entry_price": float, "entry_ts": float, "size_usd": float} or None
    now_ts:                     float       # Unix timestamp (seconds)
    btc_above_200ma:            bool        # Trend gate — supplied by orchestrator


@dataclass(frozen=True)
class AgentSignal:
    """Agent's decision. Pure output — orchestrator decides what to do with it."""
    action:               Literal["buy", "sell", "hold"]
    confidence:           float       # 0.0–1.0 (informational; NOT used for sizing in v1.4)
    stop_pct:             float       # e.g. 0.04 for 4%
    target_pct:           float       # e.g. 0.08 for 8%
    reason:               str         # Human-readable
    expected_hold_hours:  float       # Rough estimate
