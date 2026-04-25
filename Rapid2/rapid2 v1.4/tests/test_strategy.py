"""Tests for strategy.py — 4 cases from spec §8.

All tests mock exchange calls — no live network calls.
"""
import time
import pytest
from unittest.mock import MagicMock, patch

from strategy import decide, OrchestratorDecision
from agents.base import AgentSignal


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_exchange(btc_price: float = 30_000.0) -> MagicMock:
    """Create a mock exchange. fetch_ohlcv returns 210 flat candles at btc_price."""
    exchange = MagicMock()
    # 210 daily candles — enough for 200MA calc
    candle = [0, btc_price * 0.99, btc_price * 1.01, btc_price * 0.98, btc_price, 100.0]
    exchange.fetch_ohlcv.return_value = [list(candle) for _ in range(210)]
    exchange.fetch_ticker.return_value = {"last": btc_price, "close": btc_price}
    return exchange


def _now() -> float:
    return time.time()


def _week_ago() -> float:
    return _now() - 168 * 3600 - 1   # interval elapsed


def _just_now() -> float:
    return _now() - 60   # interval NOT elapsed


# ── Test cases ────────────────────────────────────────────────────────────────

class TestStrategyAccountBelow70:
    """Case 1: Account=$65 → satellite_signal is None, note mentions pause."""

    def test_satellite_disabled_when_account_low(self):
        exchange = _make_exchange()
        now = _now()

        decision = decide(
            exchange=exchange,
            account_value=65.0,
            fng_score=50.0,
            dca_last_buy_ts={"BTC/USD": _just_now(), "ETH/USD": _just_now()},
            open_sat_position=None,
            now_ts=now,
        )

        assert decision.satellite_signal is None
        # At least one note must mention the pause
        pause_mentioned = any("pause" in n.lower() or "paused" in n.lower() for n in decision.notes)
        assert pause_mentioned, f"No pause note found in: {decision.notes}"
        assert decision.capital_state.satellite_enabled is False


class TestStrategyCoreDCADue:
    """Case 2: Account=$90, DCA due for BTC, F&G=20 → core_decision.should_buy=True, amount=$8."""

    def test_core_dca_buys_when_due(self):
        exchange = _make_exchange()
        now = _now()

        decision = decide(
            exchange=exchange,
            account_value=90.0,
            fng_score=20.0,
            dca_last_buy_ts={
                "BTC/USD": _week_ago(),   # interval elapsed — due
                "ETH/USD": _just_now(),   # not due
            },
            open_sat_position=None,
            now_ts=now,
        )

        assert decision.core_decision is not None
        assert decision.core_decision.should_buy is True
        assert decision.core_decision.symbol == "BTC/USD"
        # F&G=20 (15<=20<25) → multiplier=2.0 → 4.00 * 2.0 = $8.00
        assert decision.core_decision.amount_usd == pytest.approx(8.0)


class TestStrategyNoDCADue:
    """Case 3: Account=$90, no DCA due → core_decision.should_buy=False."""

    def test_no_dca_when_interval_not_elapsed(self):
        exchange = _make_exchange()
        now = _now()

        decision = decide(
            exchange=exchange,
            account_value=90.0,
            fng_score=50.0,
            dca_last_buy_ts={
                "BTC/USD": _just_now(),   # not due
                "ETH/USD": _just_now(),   # not due
            },
            open_sat_position=None,
            now_ts=now,
        )

        # core_decision should be None (no symbol was due)
        assert decision.core_decision is None or decision.core_decision.should_buy is False


class TestStrategySatelliteSellAtTarget:
    """Case 4: Account=$90, sat position open, price at target → satellite_signal.action="sell"."""

    def test_satellite_sell_at_take_profit(self):
        entry_price = 30_000.0
        current_price = entry_price * 1.08   # +8% = take profit

        exchange = _make_exchange(btc_price=current_price)
        now = _now()

        open_position = {
            "entry_price": entry_price,
            "entry_ts": now - 3600,   # held 1 hour
            "size_usd": 27.0,
        }

        decision = decide(
            exchange=exchange,
            account_value=90.0,
            fng_score=50.0,
            dca_last_buy_ts={"BTC/USD": _just_now(), "ETH/USD": _just_now()},
            open_sat_position=open_position,
            now_ts=now,
        )

        assert decision.satellite_signal is not None
        assert decision.satellite_signal.action == "sell"
        # The reason should indicate take profit
        assert (
            "profit" in decision.satellite_signal.reason.lower()
            or "tp" in decision.satellite_signal.reason.lower()
            or "8" in decision.satellite_signal.reason
        )


class TestStrategyCapitalStatePresent:
    """Capital state is always populated in every decision."""

    def test_capital_state_always_returned(self):
        exchange = _make_exchange()
        now = _now()

        decision = decide(
            exchange=exchange,
            account_value=90.0,
            fng_score=50.0,
            dca_last_buy_ts={},
            open_sat_position=None,
            now_ts=now,
        )

        assert decision.capital_state is not None
        assert decision.capital_state.total_value == pytest.approx(90.0)

    def test_notes_always_populated(self):
        exchange = _make_exchange()
        now = _now()

        decision = decide(
            exchange=exchange,
            account_value=90.0,
            fng_score=50.0,
            dca_last_buy_ts={},
            open_sat_position=None,
            now_ts=now,
        )

        assert isinstance(decision.notes, list)
        assert len(decision.notes) > 0
