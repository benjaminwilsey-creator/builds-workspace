from __future__ import annotations

import json
import logging
from calendar import monthrange
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

import yaml

from src.config import OVERDUE_GRACE_DAYS, PROJECT_ROOT, REMIND_DAYS_BEFORE

logger = logging.getLogger(__name__)

AmountType = Literal["fixed", "variable"]

STATE_FILE = PROJECT_ROOT / "data" / "bill_state.json"
BILLS_FILE = PROJECT_ROOT / "bills.yaml"


@dataclass
class Bill:
    name: str
    due_day: int                        # day of month (1–28)
    amount_type: AmountType
    payee_keywords: list[str]           # strings to match in Plaid transaction names
    fixed_amount: float | None = None   # required if amount_type == "fixed"
    notes: str = ""

    def due_date_this_month(self, ref: date | None = None) -> date:
        today = ref or date.today()
        last_day = monthrange(today.year, today.month)[1]
        day = min(self.due_day, last_day)
        return date(today.year, today.month, day)

    def due_date_next_month(self, ref: date | None = None) -> date:
        today = ref or date.today()
        if today.month == 12:
            year, month = today.year + 1, 1
        else:
            year, month = today.year, today.month + 1
        last_day = monthrange(year, month)[1]
        day = min(self.due_day, last_day)
        return date(year, month, day)

    def next_due_date(self, ref: date | None = None) -> date:
        today = ref or date.today()
        this_month = self.due_date_this_month(today)
        return this_month if this_month >= today else self.due_date_next_month(today)

    def days_until_due(self, ref: date | None = None) -> int:
        today = ref or date.today()
        return (self.next_due_date(today) - today).days


def load_bills() -> list[Bill]:
    if not BILLS_FILE.exists():
        raise FileNotFoundError(f"bills.yaml not found at {BILLS_FILE}")

    with BILLS_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    bills = []
    for entry in data.get("bills", []):
        amount_type: AmountType = entry.get("amount_type", "fixed")
        fixed_amount = entry.get("fixed_amount")

        if amount_type == "fixed" and fixed_amount is None:
            raise ValueError(
                f"Bill '{entry['name']}' has amount_type=fixed but no fixed_amount set."
            )

        bills.append(
            Bill(
                name=entry["name"],
                due_day=int(entry["due_day"]),
                amount_type=amount_type,
                payee_keywords=entry.get("payee_keywords", [entry["name"]]),
                fixed_amount=float(fixed_amount) if fixed_amount is not None else None,
                notes=entry.get("notes", ""),
            )
        )

    logger.info("Loaded %d bills from bills.yaml.", len(bills))
    return bills


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    with STATE_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)


def mark_paid(bill_name: str, amount: float, paid_date: date) -> None:
    state = load_state()
    state[bill_name] = {
        "last_paid_date": paid_date.isoformat(),
        "last_paid_amount": amount,
    }
    save_state(state)
    logger.info("Marked %s as paid: $%.2f on %s", bill_name, amount, paid_date)


def is_paid_this_month(bill: Bill, ref: date | None = None) -> bool:
    today = ref or date.today()
    state = load_state()
    entry = state.get(bill.name)
    if not entry:
        return False

    last_paid = date.fromisoformat(entry["last_paid_date"])
    due_this_month = bill.due_date_this_month(today)

    # Paid within 10 days before the due date or any time after counts as this month
    window_start = due_this_month - timedelta(days=10)
    return window_start <= last_paid <= due_this_month + timedelta(days=OVERDUE_GRACE_DAYS)


@dataclass
class BillStatus:
    bill: Bill
    due_date: date
    days_until_due: int
    is_paid: bool
    should_remind: bool
    is_overdue: bool
    last_paid_amount: float | None = None


def get_bill_statuses(ref: date | None = None) -> list[BillStatus]:
    today = ref or date.today()
    bills = load_bills()
    statuses = []

    for bill in bills:
        due_date = bill.next_due_date(today)
        days_until = bill.days_until_due(today)
        paid = is_paid_this_month(bill, today)

        state = load_state()
        last_paid_amount = None
        entry = state.get(bill.name)
        if entry:
            last_paid_amount = entry.get("last_paid_amount")

        should_remind = not paid and days_until in REMIND_DAYS_BEFORE
        is_overdue = not paid and days_until < -OVERDUE_GRACE_DAYS

        statuses.append(
            BillStatus(
                bill=bill,
                due_date=due_date,
                days_until_due=days_until,
                is_paid=paid,
                should_remind=should_remind,
                is_overdue=is_overdue,
                last_paid_amount=last_paid_amount,
            )
        )

    return statuses
