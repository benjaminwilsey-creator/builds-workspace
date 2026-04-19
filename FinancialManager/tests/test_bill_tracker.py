from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from src.bill_tracker import (
    Bill,
    BillStatus,
    get_bill_statuses,
    is_paid_this_month,
    load_bills,
    mark_paid,
)


@pytest.fixture
def sample_bill() -> Bill:
    return Bill(
        name="Electric",
        due_day=15,
        amount_type="variable",
        payee_keywords=["duke energy"],
    )


@pytest.fixture
def fixed_bill() -> Bill:
    return Bill(
        name="Car Payment",
        due_day=1,
        amount_type="fixed",
        fixed_amount=350.00,
        payee_keywords=["auto loan"],
    )


class TestBillDueDates:
    def test_due_date_this_month(self, sample_bill: Bill) -> None:
        ref = date(2026, 4, 10)
        assert sample_bill.due_date_this_month(ref) == date(2026, 4, 15)

    def test_due_date_next_month(self, sample_bill: Bill) -> None:
        ref = date(2026, 4, 10)
        assert sample_bill.due_date_next_month(ref) == date(2026, 5, 15)

    def test_next_due_date_returns_this_month_when_not_passed(self, sample_bill: Bill) -> None:
        ref = date(2026, 4, 10)  # before the 15th
        assert sample_bill.next_due_date(ref) == date(2026, 4, 15)

    def test_next_due_date_returns_next_month_when_passed(self, sample_bill: Bill) -> None:
        ref = date(2026, 4, 20)  # after the 15th
        assert sample_bill.next_due_date(ref) == date(2026, 5, 15)

    def test_days_until_due(self, sample_bill: Bill) -> None:
        ref = date(2026, 4, 8)
        assert sample_bill.days_until_due(ref) == 7

    def test_due_day_capped_at_month_end(self) -> None:
        bill = Bill(name="Test", due_day=31, amount_type="fixed",
                    fixed_amount=100.0, payee_keywords=["test"])
        ref = date(2026, 2, 1)
        assert bill.due_date_this_month(ref) == date(2026, 2, 28)


class TestPaidState:
    def test_not_paid_when_no_state(self, sample_bill: Bill, tmp_path: Path) -> None:
        state_file = tmp_path / "bill_state.json"
        with patch("src.bill_tracker.STATE_FILE", state_file):
            assert not is_paid_this_month(sample_bill)

    def test_paid_when_paid_before_due(self, sample_bill: Bill, tmp_path: Path) -> None:
        state_file = tmp_path / "bill_state.json"
        state_file.write_text(
            json.dumps({"Electric": {"last_paid_date": "2026-04-12", "last_paid_amount": 120.00}})
        )
        with patch("src.bill_tracker.STATE_FILE", state_file):
            ref = date(2026, 4, 15)
            assert is_paid_this_month(sample_bill, ref)

    def test_not_paid_when_last_payment_was_prior_month(
        self, sample_bill: Bill, tmp_path: Path
    ) -> None:
        state_file = tmp_path / "bill_state.json"
        state_file.write_text(
            json.dumps({"Electric": {"last_paid_date": "2026-03-12", "last_paid_amount": 115.00}})
        )
        with patch("src.bill_tracker.STATE_FILE", state_file):
            ref = date(2026, 4, 15)
            assert not is_paid_this_month(sample_bill, ref)

    def test_mark_paid_writes_state(self, tmp_path: Path) -> None:
        state_file = tmp_path / "bill_state.json"
        with patch("src.bill_tracker.STATE_FILE", state_file):
            mark_paid("Electric", 120.00, date(2026, 4, 13))
            state = json.loads(state_file.read_text())
            assert state["Electric"]["last_paid_amount"] == 120.00
            assert state["Electric"]["last_paid_date"] == "2026-04-13"
