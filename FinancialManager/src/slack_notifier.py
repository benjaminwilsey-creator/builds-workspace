from __future__ import annotations

import logging
from datetime import date

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.bill_tracker import BillStatus
from src.config import require_env

logger = logging.getLogger(__name__)


def _client() -> WebClient:
    return WebClient(token=require_env("SLACK_BOT_TOKEN"))


def _channel() -> str:
    return require_env("SLACK_FINANCE_CHANNEL")


def _format_amount(status: BillStatus) -> str:
    if status.bill.amount_type == "fixed" and status.bill.fixed_amount is not None:
        return f"${status.bill.fixed_amount:,.2f}"
    if status.last_paid_amount is not None:
        return f"~${status.last_paid_amount:,.2f} (last month's amount)"
    return "amount TBD (variable bill — check statement)"


def send_reminder(status: BillStatus) -> None:
    days = status.days_until_due
    amount_str = _format_amount(status)

    if days == 1:
        urgency = "⚠️ *DUE TOMORROW*"
    elif days == 0:
        urgency = "🚨 *DUE TODAY*"
    else:
        urgency = f"📅 Due in {days} days"

    text = (
        f"{urgency} — *{status.bill.name}*\n"
        f"Amount: {amount_str}\n"
        f"Due date: {status.due_date.strftime('%A, %B %-d')}\n"
        f"Pay via: Truist app → Bill Pay → {status.bill.name}"
    )

    if status.bill.notes:
        text += f"\nNote: {status.bill.notes}"

    _send(text)


def send_overdue_alert(status: BillStatus) -> None:
    amount_str = _format_amount(status)
    days_overdue = abs(status.days_until_due)

    text = (
        f"🔴 *MISSED PAYMENT?* — *{status.bill.name}*\n"
        f"Was due: {status.due_date.strftime('%B %-d')} ({days_overdue} days ago)\n"
        f"Amount: {amount_str}\n"
        f"No payment detected in your Truist account.\n"
        f"Please check and pay ASAP via the Truist app."
    )

    _send(text)


def send_payment_confirmed(bill_name: str, amount: float, paid_date: date) -> None:
    text = (
        f"✅ *Payment detected* — *{bill_name}*\n"
        f"Amount: ${amount:,.2f}\n"
        f"Date: {paid_date.strftime('%B %-d, %Y')}\n"
        f"All good — logged."
    )
    _send(text)


def send_daily_summary(statuses: list[BillStatus]) -> None:
    upcoming = [s for s in statuses if not s.is_paid and 0 <= s.days_until_due <= 7]
    paid_this_month = [s for s in statuses if s.is_paid]

    if not upcoming:
        return  # Nothing coming up — stay quiet

    lines = ["📊 *Weekly Bill Summary*\n"]
    lines.append("*Coming up (next 7 days):*")
    for s in sorted(upcoming, key=lambda x: x.days_until_due):
        lines.append(
            f"  • {s.bill.name} — {_format_amount(s)} — due {s.due_date.strftime('%b %-d')}"
        )

    if paid_this_month:
        lines.append(f"\n✅ Paid this month: {', '.join(s.bill.name for s in paid_this_month)}")

    _send("\n".join(lines))


def _send(text: str) -> None:
    try:
        _client().chat_postMessage(channel=_channel(), text=text)
        logger.info("Slack message sent to %s.", _channel())
    except SlackApiError as exc:
        logger.error("Failed to send Slack message: %s", exc.response["error"])
        raise
