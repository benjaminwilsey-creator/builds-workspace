"""Tests for core/dca.py — 6 cases from spec §5.

All inputs are deterministic — no network calls, no mocking required.
"""
import time
import pytest

from core.dca import evaluate_dca


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> float:
    return time.time()


def _week_ago() -> float:
    """A timestamp far enough in the past that the 168h interval has elapsed."""
    return _now() - 168 * 3600 - 60  # 1 minute past the interval


def _just_now() -> float:
    """A timestamp so recent that the 168h interval has NOT elapsed."""
    return _now() - 60  # only 1 minute ago


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestDCAIntervalNotElapsed:
    """Case 1: Interval not elapsed → should_buy=False."""

    def test_skips_when_interval_not_elapsed(self):
        result = evaluate_dca(
            symbol="BTC/USD",
            fng_score=50.0,
            btc_pct_above_200ma=0.10,
            last_buy_ts=_just_now(),
            now_ts=_now(),
        )
        assert result.should_buy is False
        assert "interval" in result.reason.lower()
        assert result.amount_usd == 0.0


class TestDCAFearBoost3x:
    """Case 2: F&G=10, interval elapsed, BTC +20% above 200MA → amount_usd=12.00."""

    def test_fear_extreme_gives_3x_multiplier(self):
        result = evaluate_dca(
            symbol="BTC/USD",
            fng_score=10.0,
            btc_pct_above_200ma=0.20,   # 20% above 200MA — under the 50% top filter
            last_buy_ts=_week_ago(),
            now_ts=_now(),
        )
        assert result.should_buy is True
        assert result.amount_usd == pytest.approx(12.0)   # 4.00 * 3.0


class TestDCAFearMedium2x:
    """Case 3: F&G=20, interval elapsed → amount_usd=8.00."""

    def test_fear_moderate_gives_2x_multiplier(self):
        result = evaluate_dca(
            symbol="BTC/USD",
            fng_score=20.0,
            btc_pct_above_200ma=0.10,
            last_buy_ts=_week_ago(),
            now_ts=_now(),
        )
        assert result.should_buy is True
        assert result.amount_usd == pytest.approx(8.0)   # 4.00 * 2.0


class TestDCATopFilter:
    """Case 4: F&G=50, BTC +80% above 200MA → skip (top filter fires)."""

    def test_top_filter_skips_euphoria_top(self):
        result = evaluate_dca(
            symbol="BTC/USD",
            fng_score=50.0,
            btc_pct_above_200ma=0.80,   # 80% above 200MA — over the 50% threshold
            last_buy_ts=_week_ago(),
            now_ts=_now(),
        )
        assert result.should_buy is False
        assert "top filter" in result.reason.lower() or "filter" in result.reason.lower()


class TestDCAFearOverridesTopFilter:
    """Case 5: F&G=10, BTC +80% above 200MA → BUY (fear overrides top filter)."""

    def test_extreme_fear_overrides_top_filter(self):
        result = evaluate_dca(
            symbol="BTC/USD",
            fng_score=10.0,
            btc_pct_above_200ma=0.80,   # 80% above 200MA — would normally trigger top filter
            last_buy_ts=_week_ago(),
            now_ts=_now(),
        )
        # F&G=10 < 15, so the top filter condition (fng_score >= 25) is False
        # → fear overrides → should buy with 3x multiplier
        assert result.should_buy is True
        assert result.amount_usd == pytest.approx(12.0)   # 4.00 * 3.0


class TestDCABelowKrakenMinimum:
    """Case 6: base=1.00, F&G=50 → skip (below Kraken minimum $3.80)."""

    def test_skips_when_amount_below_kraken_minimum(self):
        result = evaluate_dca(
            symbol="BTC/USD",
            fng_score=50.0,
            btc_pct_above_200ma=0.10,
            last_buy_ts=_week_ago(),
            now_ts=_now(),
            base_amount_usd=1.00,   # 1.00 * 1.0 = $1.00 — below $3.80 minimum
        )
        assert result.should_buy is False
        assert "minimum" in result.reason.lower() or "kraken" in result.reason.lower()
        assert result.amount_usd == 0.0
