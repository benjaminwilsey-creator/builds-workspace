from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

from src.config import require_env

logger = logging.getLogger(__name__)

# How many days back to search for a matching payment transaction
TRANSACTION_LOOKBACK_DAYS = 45


def _build_client() -> plaid_api.PlaidApi:
    environment = require_env("PLAID_ENV")
    client_id = require_env("PLAID_CLIENT_ID")
    secret = require_env("PLAID_SECRET")

    env_map = {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }
    plaid_env = env_map.get(environment.lower())
    if plaid_env is None:
        raise ValueError(
            f"PLAID_ENV must be one of: sandbox, development, production. Got: {environment}"
        )

    configuration = plaid.Configuration(
        host=plaid_env,
        api_key={"clientId": client_id, "secret": secret},
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def get_recent_transactions(days_back: int = TRANSACTION_LOOKBACK_DAYS) -> list[dict[str, Any]]:
    """Fetch recent transactions from Truist via Plaid."""
    client = _build_client()
    access_token = require_env("PLAID_ACCESS_TOKEN")

    start_date = date.today() - timedelta(days=days_back)
    end_date = date.today()

    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=TransactionsGetRequestOptions(count=500),
    )

    try:
        response = client.transactions_get(request)
        transactions = response["transactions"]
        logger.info("Fetched %d transactions from Plaid.", len(transactions))
        return [dict(t) for t in transactions]
    except plaid.ApiException as exc:
        logger.error("Plaid API error fetching transactions: %s", exc)
        raise


def find_payment_in_transactions(
    payee_keywords: list[str],
    transactions: list[dict[str, Any]],
    after_date: date,
) -> dict[str, Any] | None:
    """
    Search transactions for a payment matching any of the payee keywords,
    occurring on or after after_date. Returns the first match or None.
    """
    for txn in transactions:
        txn_date = txn.get("date")
        if txn_date is None or txn_date < after_date:
            continue

        name = (txn.get("name") or "").lower()
        merchant = (txn.get("merchant_name") or "").lower()

        for keyword in payee_keywords:
            if keyword.lower() in name or keyword.lower() in merchant:
                logger.info(
                    "Found matching payment: %s on %s for $%.2f",
                    txn.get("name"),
                    txn_date,
                    txn.get("amount", 0),
                )
                return txn

    return None
