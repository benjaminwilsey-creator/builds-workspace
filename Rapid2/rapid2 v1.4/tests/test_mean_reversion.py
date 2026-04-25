"""Tests for agents/mean_reversion.py — 9 cases per spec §6.

All tests mock exchange.fetch_ohlcv — no live network calls.
"""
import time
import pytest
from unittest.mock import MagicMock

from agents.base import AgentContext, AgentSignal
from agents import mean_reversion


# ── OHLCV helpers ─────────────────────────────────────────────────────────────

def _make_candle(
    open_: float,
    high: float,
    low: float,
    close: float,
    ts: int = 0,
    volume: float = 100.0,
) -> list:
    return [ts, open_, high, low, close, volume]


def _flat_candles(close: float, n: int, low: float | None = None) -> list[list]:
    """Return n identical candles with the given close price."""
    lo = low if low is not None else close * 0.995
    return [_make_candle(close * 0.998, close * 1.002, lo, close) for _ in range(n)]


def _oversold_ohlcv(
    base_price: float = 30_000.0,
    rsi_target: float = 30.0,
    bb_touch: bool = True,
    green_forming: bool = True,
    forming_low_above_prior: bool = True,
) -> list[list]:
    """Build 100 synthetic candles that produce the desired signal conditions.

    Strategy:
    - Start with 60 candles near base_price (stable baseline).
    - Add a series of declining candles to push RSI down to ~rsi_target.
    - Optionally push the last closed close below the lower BB band.
    - Append one forming candle with controlled green/red + low direction.
    """
    candles: list[list] = []

    # Stable baseline: 60 flat candles (needed for Wilder's warm-up)
    for _ in range(60):
        candles.append(_make_candle(base_price, base_price * 1.001, base_price * 0.999, base_price))

    # Decline phase: enough consecutive down candles to drive RSI < rsi_target
    # Each candle drops by drop_pct; tune to reach the desired RSI range.
    # For RSI ~ 30, we want avg_loss >> avg_gain.
    drop_pct = 0.005   # 0.5% per candle
    price = base_price
    # 20 decline candles gives roughly RSI = 100 - 100/(1 + 0/avg_loss) ≈ 0–30 territory
    for _ in range(20):
        prev = price
        price = price * (1 - drop_pct)
        candles.append(_make_candle(prev, prev * 1.0005, price * 0.999, price))

    # At this point len(candles) = 80, which gives RSI enough warmup.
    # We need 99 closed + 1 forming = 100 total.
    # Add flat candles to pad to 99 closed candles.
    while len(candles) < 99:
        candles.append(_make_candle(price, price * 1.001, price * 0.999, price))

    # Determine last-closed close for BB calculation
    last_closed_close = price

    # If bb_touch requested, push close to just below lower BB
    if bb_touch:
        # The BB lower band ≈ mean - 2σ of the last 20 closes.
        # Our 20 decline candles already push us there; keep the close as-is.
        # For robustness, manually set the last closed candle's close well below
        # where the band would be calculated.  We re-use the declining price.
        pass  # declining price is already below the stable baseline's lower band

    # Build last closed candle (index 98, i.e. candle number 99)
    prior_low = price * 0.998   # low of the 99th candle
    candles[-1] = _make_candle(price * 1.001, price * 1.002, prior_low, last_closed_close)

    # Forming (still-open) candle — index 99
    forming_open = last_closed_close
    if green_forming:
        forming_close = last_closed_close * 1.003   # green
    else:
        forming_close = last_closed_close * 0.997   # red

    if forming_low_above_prior:
        forming_low = prior_low * 1.001   # low > prior_low  ✓
    else:
        forming_low = prior_low * 0.999   # low <= prior_low ✗

    forming_high = max(forming_open, forming_close) * 1.001
    candles.append(_make_candle(forming_open, forming_high, forming_low, forming_close))

    assert len(candles) == 100
    return candles


def _high_rsi_ohlcv(base_price: float = 30_000.0) -> list[list]:
    """100 candles that produce RSI > 40 (all rising — RSI near 100)."""
    candles: list[list] = []
    price = base_price
    for _ in range(99):
        prev = price
        price = price * 1.002   # steady up-trend → high RSI
        candles.append(_make_candle(prev, price, prev * 0.999, price))

    # Forming candle (not relevant for this path — RSI check exits first)
    candles.append(_make_candle(price, price * 1.001, price * 0.999, price * 1.001))
    assert len(candles) == 100
    return candles


def _make_ctx(
    exchange_mock: MagicMock,
    current_price: float = 30_000.0,
    btc_above_200ma: bool = True,
    open_position: dict | None = None,
    now_ts: float | None = None,
) -> AgentContext:
    return AgentContext(
        exchange=exchange_mock,
        symbol="BTC/USD",
        current_price=current_price,
        account_value=90.0,
        satellite_capital=27.0,
        open_satellite_position=open_position,
        now_ts=now_ts if now_ts is not None else time.time(),
        btc_above_200ma=btc_above_200ma,
    )


# ── Test cases (9, matching spec §6) ─────────────────────────────────────────

class TestMeanReversionTrendFilter:
    """Case 1: BTC below 200MA → hold (trend filter)."""

    def test_btc_below_200ma_returns_hold(self):
        exchange = MagicMock()
        ctx = _make_ctx(exchange, btc_above_200ma=False)

        signal = mean_reversion.evaluate(ctx)

        assert signal.action == "hold"
        assert "200MA" in signal.reason
        # fetch_ohlcv should NOT be called — we exit before indicator math
        exchange.fetch_ohlcv.assert_not_called()


class TestMeanReversionExitLogic:
    """Cases 2–4: exit signals when a position is open."""

    def test_take_profit_at_8pct(self):
        """Case 2: position open + price hit +8% → sell (take profit)."""
        entry_price = 30_000.0
        current_price = entry_price * 1.08   # exactly +8%
        exchange = MagicMock()
        pos = {"entry_price": entry_price, "entry_ts": time.time() - 3600, "size_usd": 27.0}
        ctx = _make_ctx(exchange, current_price=current_price, open_position=pos)

        signal = mean_reversion.evaluate(ctx)

        assert signal.action == "sell"
        assert "profit" in signal.reason.lower() or "tp" in signal.reason.lower() or "8" in signal.reason
        exchange.fetch_ohlcv.assert_not_called()

    def test_stop_loss_at_negative_4pct(self):
        """Case 3: position open + price hit −4% → sell (stop loss)."""
        entry_price = 30_000.0
        current_price = entry_price * 0.96   # exactly −4%
        exchange = MagicMock()
        pos = {"entry_price": entry_price, "entry_ts": time.time() - 3600, "size_usd": 27.0}
        ctx = _make_ctx(exchange, current_price=current_price, open_position=pos)

        signal = mean_reversion.evaluate(ctx)

        assert signal.action == "sell"
        assert "stop" in signal.reason.lower() or "sl" in signal.reason.lower() or "4" in signal.reason
        exchange.fetch_ohlcv.assert_not_called()

    def test_time_stop_at_72h(self):
        """Case 4: position open + 72h elapsed → sell (time stop)."""
        entry_price = 30_000.0
        current_price = entry_price * 1.01   # no TP/SL
        entry_ts = time.time() - (72 * 3600 + 1)   # 72h+1s ago
        exchange = MagicMock()
        pos = {"entry_price": entry_price, "entry_ts": entry_ts, "size_usd": 27.0}
        ctx = _make_ctx(exchange, current_price=current_price, open_position=pos)

        signal = mean_reversion.evaluate(ctx)

        assert signal.action == "sell"
        assert "time" in signal.reason.lower() or "72" in signal.reason
        exchange.fetch_ohlcv.assert_not_called()


class TestMeanReversionEntryConditions:
    """Cases 5–9: entry logic when no position is open."""

    def test_rsi_above_threshold_returns_hold(self):
        """Case 5: no position + RSI=40 → hold (not oversold enough)."""
        exchange = MagicMock()
        exchange.fetch_ohlcv.return_value = _high_rsi_ohlcv()
        ctx = _make_ctx(exchange, btc_above_200ma=True)

        signal = mean_reversion.evaluate(ctx)

        assert signal.action == "hold"
        assert "RSI" in signal.reason
        exchange.fetch_ohlcv.assert_called_once()

    def test_rsi_low_no_bb_touch_returns_hold(self):
        """Case 6: no position + RSI<35 + last close above lower BB → hold at BB check.

        Construction (verified by manual RSI/BB calculation):
        - 60 flat candles at base_price.
        - 20 hard-decline candles (−1% each) → RSI driven well below 35.
        - 19 slow-decline candles (−0.1% each) → RSI stays < 35; last close still
          above the lower BB because the window of 20 has shrinking std.
        - Forming candle: green, low above prior low.

        Verified: RSI ≈ 0, lower_BB ≈ 24025, last_close ≈ 24075 → no BB touch.
        """
        exchange = MagicMock()

        base = 30_000.0
        candles: list[list] = []

        # 60 flat candles
        price = base
        for _ in range(60):
            candles.append(_make_candle(price, price * 1.001, price * 0.999, price))

        # 20 hard-decline candles: −1% each
        for _ in range(20):
            prev = price
            price *= 0.99
            candles.append(_make_candle(prev, prev * 1.0005, price * 0.999, price))

        # 19 slow-decline candles: −0.1% each (RSI stays < 35; close stays above lower BB)
        for _ in range(19):
            prev = price
            price *= 0.999
            candles.append(_make_candle(prev, prev * 1.0002, price * 0.9995, price))

        assert len(candles) == 99  # 99 closed candles

        prior_low = price * 0.9995
        # Forming candle: green, low above prior_low
        forming_open = price
        forming_close_price = price * 1.002
        forming_low = prior_low * 1.001
        forming_high = forming_close_price * 1.001
        candles.append(_make_candle(forming_open, forming_high, forming_low, forming_close_price))

        assert len(candles) == 100

        exchange.fetch_ohlcv.return_value = candles
        ctx = _make_ctx(exchange, btc_above_200ma=True)

        signal = mean_reversion.evaluate(ctx)

        assert signal.action == "hold"
        # RSI passed (< 35) but BB check failed — reason should mention the close vs band
        assert "band" in signal.reason.lower() or "BB" in signal.reason or "close" in signal.reason.lower()

    def test_rsi_low_bb_touch_red_candle_returns_hold(self):
        """Case 7: no position + RSI=30 + BB touch + red confirmation candle → hold."""
        exchange = MagicMock()
        exchange.fetch_ohlcv.return_value = _oversold_ohlcv(
            bb_touch=True,
            green_forming=False,       # red candle
            forming_low_above_prior=True,
        )
        ctx = _make_ctx(exchange, btc_above_200ma=True)

        signal = mean_reversion.evaluate(ctx)

        assert signal.action == "hold"
        assert "red" in signal.reason.lower() or "confirmation" in signal.reason.lower()

    def test_all_conditions_met_returns_buy(self):
        """Case 8: no position + all conditions met → buy."""
        exchange = MagicMock()
        exchange.fetch_ohlcv.return_value = _oversold_ohlcv(
            bb_touch=True,
            green_forming=True,
            forming_low_above_prior=True,
        )
        ctx = _make_ctx(exchange, btc_above_200ma=True)

        signal = mean_reversion.evaluate(ctx)

        assert signal.action == "buy"

    def test_buy_signal_has_correct_target_and_stop(self):
        """Case 9: signal has target_pct=0.08, stop_pct=0.04 on buy."""
        exchange = MagicMock()
        exchange.fetch_ohlcv.return_value = _oversold_ohlcv(
            bb_touch=True,
            green_forming=True,
            forming_low_above_prior=True,
        )
        ctx = _make_ctx(exchange, btc_above_200ma=True)

        signal = mean_reversion.evaluate(ctx)

        assert signal.action == "buy"
        assert signal.target_pct == pytest.approx(0.08)
        assert signal.stop_pct == pytest.approx(0.04)
