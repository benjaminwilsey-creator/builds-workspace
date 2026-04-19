from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent

logger = logging.getLogger(__name__)

# Reminder schedule — days before due date to send Slack alerts
REMIND_DAYS_BEFORE: list[int] = [7, 3, 1]

# How many days past due before sending a "missed payment?" alert
OVERDUE_GRACE_DAYS: int = 2


def get_env(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    if value is None:
        logger.debug("Environment variable %s is not set.", key)
    return value


def require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{key}' is not set. "
            f"Check your .env file against .env.example."
        )
    return value
