"""Tests for capital.py — 5 cases from spec §7.

All tests are pure — no exchange calls, no mocks needed.
"""
import pytest
from capital import compute_state, CAP_SAT_PAUSE_THRESHOLD, CAP_ALERT_FLOOR, CAP_FLOOR, CAP_MONTHLY_BURN


class TestComputeState:
    """5 cases from spec §7."""

    def test_90_dollars_healthy(self):
        """$90 → satellite enabled, no alert, runway=5.83 months."""
        state = compute_state(90.0)

        assert state.total_value == pytest.approx(90.0)
        assert state.core_value == pytest.approx(63.0)      # 70%
        assert state.satellite_value == pytest.approx(27.0) # 30%
        assert state.satellite_enabled is True
        assert state.alert_floor_breached is False
        # runway = (90 - 20) / 12 = 5.833...
        assert state.runway_months == pytest.approx(5.833, rel=1e-2)

    def test_65_dollars_satellite_paused(self):
        """$65 → satellite disabled (below $70 pause threshold)."""
        state = compute_state(65.0)

        assert state.satellite_enabled is False
        assert state.alert_floor_breached is False  # not below $50 yet

    def test_45_dollars_alert_and_paused(self):
        """$45 → satellite disabled, alert floor breached."""
        state = compute_state(45.0)

        assert state.satellite_enabled is False
        assert state.alert_floor_breached is True

    def test_20_dollars_runway_zero(self):
        """$20 → runway = 0.0 (at the hard floor)."""
        state = compute_state(20.0)

        # (20 - 20) / 12 = 0.0
        assert state.runway_months == pytest.approx(0.0)
        assert state.satellite_enabled is False
        assert state.alert_floor_breached is True

    def test_15_dollars_runway_clamped(self):
        """$15 → runway clamped to 0.0 (below hard floor)."""
        state = compute_state(15.0)

        # max(0, (15 - 20) / 12) = max(0, -0.416) = 0.0
        assert state.runway_months == pytest.approx(0.0)
        assert state.satellite_enabled is False
        assert state.alert_floor_breached is True

    def test_core_and_satellite_fractions(self):
        """Core and satellite values always match their fractions."""
        state = compute_state(100.0)

        assert state.core_value == pytest.approx(70.0)
        assert state.satellite_value == pytest.approx(30.0)

    def test_custom_fractions(self):
        """Custom fractions are respected."""
        state = compute_state(100.0, core_fraction=0.60, sat_fraction=0.40)

        assert state.core_value == pytest.approx(60.0)
        assert state.satellite_value == pytest.approx(40.0)

    def test_exactly_at_pause_threshold(self):
        """Exactly $70 → satellite enabled (>= threshold)."""
        state = compute_state(CAP_SAT_PAUSE_THRESHOLD)

        assert state.satellite_enabled is True

    def test_just_below_pause_threshold(self):
        """$69.99 → satellite paused."""
        state = compute_state(69.99)

        assert state.satellite_enabled is False

    def test_exactly_at_alert_floor(self):
        """Exactly $50 → no alert (alert is < not <=)."""
        state = compute_state(CAP_ALERT_FLOOR)

        assert state.alert_floor_breached is False

    def test_just_below_alert_floor(self):
        """$49.99 → alert breached."""
        state = compute_state(49.99)

        assert state.alert_floor_breached is True
