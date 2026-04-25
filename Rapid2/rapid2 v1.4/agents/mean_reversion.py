"""Mean-reversion satellite agent for BTC/USD.

Pure function: evaluate(ctx) -> AgentSignal.
No side effects. OHLCV is fetched via ctx.exchange only.
"""
import math
import logging
from agents.base import AgentContext, AgentSignal

logger = logging.getLogger(__name__)

# ── Constants (single source of truth per spec §12) ──────────────────────────
SAT_RSI_THRESHOLD = 35.0
SAT_RSI_PERIOD = 14
SAT_RSI_TIMEFRAME = "4h"
SAT_BB_PERIOD = 20
SAT_BB_STD = 2.0
SAT_BB_TIMEFRAME = "4h"
SAT_TP_PCT = 0.08
SAT_SL_PCT = 0.04
SAT_MAX_HOLD_HOURS = 72.0

_OHLCV_LIMIT = 100   # candles to fetch — enough for RSI(14) + BB(20) with headroom


# ── Internal helpers ──────────────────────────────────────────────────────────

def _compute_rsi(closes: list[float], period: int) -> float:
    """Compute RSI for the most recent candle using Wilder's smoothing.

    Requires at least period+1 values.  Returns a value in [0, 100].
    """
    if len(closes) < period + 1:
        raise ValueError(f"Need at least {period + 1} closes for RSI({period}); got {len(closes)}")

    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, period + 1):
        delta = closes[i] - closes[i - 1]
        if delta >= 0:
            gains.append(delta)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(delta))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    # Wilder's smoothing over remaining candles
    for i in range(period + 1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gain = delta if delta > 0 else 0.0
        loss = abs(delta) if delta < 0 else 0.0
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    if avg_loss == 0.0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _compute_bollinger(closes: list[float], period: int, num_std: float) -> tuple[float, float, float]:
    """Return (upper_band, middle_band, lower_band) using the last `period` closes."""
    if len(closes) < period:
        raise ValueError(f"Need at least {period} closes for BB({period}); got {len(closes)}")

    window = closes[-period:]
    mean = sum(window) / period
    variance = sum((x - mean) ** 2 for x in window) / period
    std = math.sqrt(variance)
    upper = mean + num_std * std
    lower = mean - num_std * std
    return upper, mean, lower


# ── Public evaluate function ──────────────────────────────────────────────────

def evaluate(ctx: AgentContext) -> AgentSignal:
    """Evaluate mean-reversion conditions and return a trading signal.

    Order of checks (spec §6):
    1. Open-position exit logic (TP / SL / time-stop) — checked first.
    2. Entry logic: trend filter → RSI → BB → confirmation candle.
    """
    # ── 1. Exit logic (position is open) ─────────────────────────────────────
    pos = ctx.open_satellite_position
    if pos is not None:
        entry_price: float = pos["entry_price"]
        entry_ts: float = pos["entry_ts"]
        pnl_pct = (ctx.current_price - entry_price) / entry_price
        hold_hours = (ctx.now_ts - entry_ts) / 3600.0

        if pnl_pct >= SAT_TP_PCT:
            return AgentSignal(
                action="sell",
                confidence=1.0,
                stop_pct=SAT_SL_PCT,
                target_pct=SAT_TP_PCT,
                reason=f"Take profit: PnL {pnl_pct:.2%} >= {SAT_TP_PCT:.0%}",
                expected_hold_hours=hold_hours,
            )
        if pnl_pct <= -SAT_SL_PCT:
            return AgentSignal(
                action="sell",
                confidence=1.0,
                stop_pct=SAT_SL_PCT,
                target_pct=SAT_TP_PCT,
                reason=f"Stop loss: PnL {pnl_pct:.2%} <= -{SAT_SL_PCT:.0%}",
                expected_hold_hours=hold_hours,
            )
        if hold_hours >= SAT_MAX_HOLD_HOURS:
            return AgentSignal(
                action="sell",
                confidence=1.0,
                stop_pct=SAT_SL_PCT,
                target_pct=SAT_TP_PCT,
                reason=f"Time stop: held {hold_hours:.1f}h >= {SAT_MAX_HOLD_HOURS:.0f}h",
                expected_hold_hours=hold_hours,
            )

        # Position open but no exit trigger → hold
        return AgentSignal(
            action="hold",
            confidence=0.0,
            stop_pct=SAT_SL_PCT,
            target_pct=SAT_TP_PCT,
            reason="Position open; no exit condition met",
            expected_hold_hours=36.0,
        )

    # ── 2. Entry logic (no open position) ────────────────────────────────────

    # 2a. Trend filter
    if not ctx.btc_above_200ma:
        return AgentSignal(
            action="hold",
            confidence=0.0,
            stop_pct=SAT_SL_PCT,
            target_pct=SAT_TP_PCT,
            reason="Trend filter: BTC below 200MA",
            expected_hold_hours=36.0,
        )

    # 2b. Fetch OHLCV and compute indicators
    raw: list[list] = ctx.exchange.fetch_ohlcv(ctx.symbol, SAT_RSI_TIMEFRAME, limit=_OHLCV_LIMIT)
    # raw is list of [timestamp, open, high, low, close, volume]

    # Separate the forming (last) candle from the closed candles
    closed_candles = raw[:-1]   # all candles except the still-forming one
    forming_candle = raw[-1]

    closed_closes = [c[4] for c in closed_candles]

    # 2c. RSI(14) check
    rsi = _compute_rsi(closed_closes, SAT_RSI_PERIOD)
    rsi_ok = rsi <= SAT_RSI_THRESHOLD

    if not rsi_ok:
        return AgentSignal(
            action="hold",
            confidence=1 / 3,
            stop_pct=SAT_SL_PCT,
            target_pct=SAT_TP_PCT,
            reason=f"RSI {rsi:.1f} > threshold {SAT_RSI_THRESHOLD}",
            expected_hold_hours=36.0,
        )

    # 2d. Bollinger Band lower-touch check
    # Use the last closed candle's close vs the lower band computed from closed_closes
    _, _, lower_band = _compute_bollinger(closed_closes, SAT_BB_PERIOD, SAT_BB_STD)
    last_closed_close = closed_closes[-1]
    bb_ok = last_closed_close <= lower_band

    if not bb_ok:
        return AgentSignal(
            action="hold",
            confidence=2 / 3,
            stop_pct=SAT_SL_PCT,
            target_pct=SAT_TP_PCT,
            reason=f"No BB touch: close {last_closed_close:.2f} > lower band {lower_band:.2f}",
            expected_hold_hours=36.0,
        )

    # 2e. Confirmation candle check (the still-forming current candle)
    # Green: close > open. Low above prior candle's low.
    forming_open = forming_candle[1]
    forming_low = forming_candle[3]
    forming_close = forming_candle[4]
    prior_low = closed_candles[-1][3]

    candle_green = forming_close > forming_open
    low_above_prior = forming_low > prior_low
    confirmation_ok = candle_green and low_above_prior

    conditions_met = sum([rsi_ok, bb_ok, confirmation_ok])
    confidence = conditions_met / 3

    if not confirmation_ok:
        reason_parts = []
        if not candle_green:
            reason_parts.append("forming candle is red")
        if not low_above_prior:
            reason_parts.append(f"forming low {forming_low:.2f} <= prior low {prior_low:.2f}")
        return AgentSignal(
            action="hold",
            confidence=confidence,
            stop_pct=SAT_SL_PCT,
            target_pct=SAT_TP_PCT,
            reason=f"Confirmation failed: {'; '.join(reason_parts)}",
            expected_hold_hours=36.0,
        )

    # All conditions met → BUY
    return AgentSignal(
        action="buy",
        confidence=1.0,
        stop_pct=SAT_SL_PCT,
        target_pct=SAT_TP_PCT,
        reason=(
            f"All conditions met: RSI={rsi:.1f}, BB touch, green confirmation candle"
        ),
        expected_hold_hours=36.0,
    )
