from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.bill_tracker import Bill, BillStatus
from src.slack_notifier import send_overdue_alert, send_payment_confirmed, send_reminder


@pytest.fixture
def fixed_status() -> BillStatus:
    bill = Bill(
        name="Car Payment",
        due_day=1,
        amount_type="fixed",
        fixed_amount=350.00,
        payee_keywords=["auto loan"],
    )
    return BillStatus(
        bill=bill,
        due_date=date(2026, 5, 1),
        days_until_due=7,
        is_paid=False,
        should_remind=True,
        is_overdue=False,
    )


@pytest.fixture
def variable_status() -> BillStatus:
    bill = Bill(
        name="Electric",
        due_day=15,
        amount_type="variable",
        payee_keywords=["duke energy"],
    )
    return BillStatus(
        bill=bill,
        due_date=date(2026, 4, 15),
        days_until_due=3,
        is_paid=False,
        should_remind=True,
        is_overdue=False,
        last_paid_amount=115.50,
    )


class TestSendReminder:
    def test_sends_fixed_amount(self, fixed_status: BillStatus) -> None:
        mock_client = MagicMock()
        with (
            patch("src.slack_notifier._client", return_value=mock_client),
            patch("src.slack_notifier._channel", return_value="C123"),
            patch("src.slack_notifier.require_env", return_value="dummy"),
        ):
            send_reminder(fixed_status)
            mock_client.chat_postMessage.assert_called_once()
            text = mock_client.chat_postMessage.call_args[1]["text"]
            assert "Car Payment" in text
            assert "$350.00" in text

    def test_sends_variable_amount_with_last_months(self, variable_status: BillStatus) -> None:
        mock_client = MagicMock()
        with (
            patch("src.slack_notifier._client", return_value=mock_client),
            patch("src.slack_notifier._channel", return_value="C123"),
            patch("src.slack_notifier.require_env", return_value="dummy"),
        ):
            send_reminder(variable_status)
            text = mock_client.chat_postMessage.call_args[1]["text"]
            assert "Electric" in text
            assert "115.50" in text


class TestSendOverdueAlert:
    def test_includes_bill_name_and_due_date(self, fixed_status: BillStatus) -> None:
        fixed_status.days_until_due = -3
        fixed_status.is_overdue = True
        mock_client = MagicMock()
        with (
            patch("src.slack_notifier._client", return_value=mock_client),
            patch("src.slack_notifier._channel", return_value="C123"),
            patch("src.slack_notifier.require_env", return_value="dummy"),
        ):
            send_overdue_alert(fixed_status)
            text = mock_client.chat_postMessage.call_args[1]["text"]
            assert "Car Payment" in text
            assert "MISSED" in text


class TestSendPaymentConfirmed:
    def test_confirmation_message(self) -> None:
        mock_client = MagicMock()
        with (
            patch("src.slack_notifier._client", return_value=mock_client),
            patch("src.slack_notifier._channel", return_value="C123"),
            patch("src.slack_notifier.require_env", return_value="dummy"),
        ):
            send_payment_confirmed("Electric", 112.34, date(2026, 4, 13))
            text = mock_client.chat_postMessage.call_args[1]["text"]
            assert "Electric" in text
            assert "112.34" in text
