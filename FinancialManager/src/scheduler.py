from __future__ import annotations

import logging
import time
from datetime import date

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.bill_tracker import get_bill_statuses, mark_paid
from src.config import get_env
from src.plaid_client import find_payment_in_transactions, get_recent_transactions
from src.slack_notifier import (
    send_daily_summary,
    send_overdue_alert,
    send_payment_confirmed,
    send_reminder,
)

logger = logging.getLogger(__name__)

AUDIT_LOG_FILE = "logs/audit.log"


def _audit(message: str) -> None:
    timestamp = date.today().isoformat()
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    logger.info("AUDIT: %s", message)


def run_daily_check() -> None:
    """
    Main daily job:
    1. Fetch recent Plaid transactions
    2. For each bill, check if it was paid
    3. Send reminders for upcoming bills
    4. Alert on overdue bills
    5. Confirm any newly detected payments
    """
    logger.info("Running daily bill check.")
    today = date.today()

    try:
        transactions = get_recent_transactions()
    except Exception as exc:
        logger.error("Could not fetch transactions from Plaid: %s", exc)
        _audit(f"ERROR: Plaid transaction fetch failed — {exc}")
        return

    statuses = get_bill_statuses()

    for status in statuses:
        if status.is_paid:
            continue

        # Check if a payment appeared in Plaid since the start of the billing window
        window_start = status.due_date.replace(day=1)  # start of this month
        match = find_payment_in_transactions(
            payee_keywords=status.bill.payee_keywords,
            transactions=transactions,
            after_date=window_start,
        )

        if match:
            amount = abs(float(match.get("amount", 0)))
            paid_date = match.get("date", today)
            mark_paid(status.bill.name, amount, paid_date)
            send_payment_confirmed(status.bill.name, amount, paid_date)
            _audit(f"PAYMENT DETECTED: {status.bill.name} — ${amount:.2f} on {paid_date}")
            continue

        if status.should_remind:
            send_reminder(status)
            _audit(
                f"REMINDER SENT: {status.bill.name} — due {status.due_date} "
                f"({status.days_until_due} days)"
            )

        if status.is_overdue:
            send_overdue_alert(status)
            _audit(f"OVERDUE ALERT: {status.bill.name} — due {status.due_date}")

    # Weekly summary every Monday
    if today.weekday() == 0:
        send_daily_summary(statuses)
        _audit("WEEKLY SUMMARY SENT")


def start() -> None:
    run_hour = int(get_env("CHECK_HOUR", "8") or "8")
    run_minute = int(get_env("CHECK_MINUTE", "0") or "0")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_daily_check,
        trigger=CronTrigger(hour=run_hour, minute=run_minute),
        id="daily_bill_check",
        name="Daily bill check",
        replace_existing=True,
    )

    logger.info("Scheduler started — daily check at %02d:%02d.", run_hour, run_minute)
    _audit(f"SCHEDULER STARTED at {date.today().isoformat()}")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
        _audit("SCHEDULER STOPPED")


if __name__ == "__main__":
    import logging as _logging
    _logging.basicConfig(
        level=_logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    start()
