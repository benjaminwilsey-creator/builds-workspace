"""paper_bot.py — Paper trading harness for Rapid2 v1.4.

Simulates fills at real Kraken market prices. No auth required for public data.
Logs all simulated trades to logs/paper_trades.csv.

Usage:
  python paper_bot.py --dry-run     # ONE decision cycle, log it, exit cleanly
  python paper_bot.py               # Full paper trading loop (not for CI)

Required env vars (.env):
  PAPER_TELEGRAM_TOKEN     (optional in dev — only needed for full loop)
  TELEGRAM_CHAT_ID         (optional in dev — only needed for full loop)
  PAPER_STARTING_USD=90    (optional, default $90)
"""
import argparse
import asyncio
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import ccxt
from dotenv import load_dotenv

from capital import compute_state
from strategy import decide, OrchestratorDecision

# ── Bootstrap ──────────────────────────────────────────────────────────────────
load_dotenv()

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PAPER] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/paper_bot.log"),
    ],
)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
PAPER_STARTING_USD: float = float(os.getenv("PAPER_STARTING_USD", "90.0"))
PAPER_TRADES_CSV = Path("logs/paper_trades.csv")
PAPER_STATE_FILE = Path("logs/paper_state.json")
PAPER_DCA_STATE_FILE = Path("logs/paper_dca_state.json")
KRAKEN_TAKER_FEE = 0.0026   # 0.26% per spec §10
SLIPPAGE = 0.001             # 0.1% slippage per spec §10
SCAN_INTERVAL_SECONDS = 900  # 15 minutes (matches bot.py)

# ── Exchange (public data only — no API keys for OHLCV) ───────────────────────
exchange = ccxt.kraken({"enableRateLimit": True})

# ── In-memory paper portfolio ─────────────────────────────────────────────────
paper_usd: float = PAPER_STARTING_USD
paper_position: dict | None = None   # {"entry_price", "entry_ts", "size_usd", "qty"}
paper_paused: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
# F&G HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def _fetch_fng_score() -> float:
    """Fetch Fear & Greed score from the public API. Returns 50.0 on error."""
    try:
        import urllib.request
        url = "https://api.alternative.me/fng/?limit=1"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            return float(data["data"][0]["value"])
    except Exception as exc:
        logger.warning("[F&G] fetch error, defaulting to 50: %s", exc)
        return 50.0


# ═══════════════════════════════════════════════════════════════════════════════
# STATE PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════

def _load_paper_state() -> None:
    """Load paper portfolio state from disk into module globals."""
    global paper_usd, paper_position
    if not PAPER_STATE_FILE.exists():
        logger.info("[State] No saved state — starting fresh at $%.2f", PAPER_STARTING_USD)
        return
    try:
        data = json.loads(PAPER_STATE_FILE.read_text())
        paper_usd = data.get("paper_usd", PAPER_STARTING_USD)
        paper_position = data.get("paper_position")
        logger.info("[State] Loaded — cash=$%.2f position=%s", paper_usd, paper_position)
    except Exception as exc:
        logger.error("[State] load error: %s", exc)


def _save_paper_state() -> None:
    try:
        PAPER_STATE_FILE.write_text(
            json.dumps({"paper_usd": paper_usd, "paper_position": paper_position}, indent=2)
        )
    except Exception as exc:
        logger.error("[State] save error: %s", exc)


def _load_dca_state() -> dict[str, float]:
    try:
        if not PAPER_DCA_STATE_FILE.exists():
            return {}
        return json.loads(PAPER_DCA_STATE_FILE.read_text())
    except Exception as exc:
        logger.error("[State] dca_state load error: %s", exc)
        return {}


def _save_dca_state(state: dict[str, float]) -> None:
    try:
        PAPER_DCA_STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception as exc:
        logger.error("[State] dca_state save error: %s", exc)


# ═══════════════════════════════════════════════════════════════════════════════
# TRADE LOG (CSV)
# ═══════════════════════════════════════════════════════════════════════════════

_CSV_HEADER = [
    "timestamp_utc", "action", "symbol",
    "price_raw", "price_with_slippage", "qty_coin", "usd_amount",
    "fee_usd", "paper_cash_after", "reason",
]


def _ensure_csv_header() -> None:
    if not PAPER_TRADES_CSV.exists():
        with PAPER_TRADES_CSV.open("w", newline="") as f:
            csv.writer(f).writerow(_CSV_HEADER)


def _log_trade(
    action: str,
    symbol: str,
    price_raw: float,
    price_filled: float,
    qty: float,
    usd_amount: float,
    fee_usd: float,
    cash_after: float,
    reason: str,
) -> None:
    _ensure_csv_header()
    ts = datetime.now(timezone.utc).isoformat()
    with PAPER_TRADES_CSV.open("a", newline="") as f:
        csv.writer(f).writerow([
            ts, action, symbol,
            f"{price_raw:.6f}", f"{price_filled:.6f}",
            f"{qty:.8f}", f"{usd_amount:.4f}",
            f"{fee_usd:.4f}", f"{cash_after:.4f}", reason,
        ])
    logger.info(
        "[PAPER %s] %s @ $%.4f (filled $%.4f) qty=%.6f fee=$%.4f cash=$%.2f | %s",
        action, symbol, price_raw, price_filled, qty, fee_usd, cash_after, reason,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SIMULATED ORDER EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def _paper_buy(symbol: str, size_usd: float, reason: str) -> dict | None:
    """Simulate a buy: subtract USD from paper_usd, record virtual position."""
    global paper_usd, paper_position

    if paper_position is not None:
        logger.info("[PAPER BUY] Skipped — position already open")
        return None

    if size_usd > paper_usd:
        logger.info(
            "[PAPER BUY] Insufficient funds (need $%.2f, have $%.2f)", size_usd, paper_usd
        )
        return None

    try:
        ticker = exchange.fetch_ticker(symbol)
        price_raw: float = ticker.get("ask") or ticker.get("last") or 0.0
        if price_raw <= 0:
            logger.error("[PAPER BUY] Bad price for %s: %s", symbol, price_raw)
            return None
    except Exception as exc:
        logger.error("[PAPER BUY] Price fetch error: %s", exc)
        return None

    price_filled = price_raw * (1.0 + SLIPPAGE)
    fee_usd = size_usd * KRAKEN_TAKER_FEE
    total_cost = size_usd + fee_usd
    qty = size_usd / price_filled

    paper_usd -= total_cost

    paper_position = {
        "entry_price": price_filled,
        "entry_ts": time.time(),
        "size_usd": size_usd,
        "qty": qty,
    }
    _save_paper_state()
    _log_trade("BUY", symbol, price_raw, price_filled, qty, size_usd, fee_usd, paper_usd, reason)
    return paper_position


def _paper_sell(symbol: str, reason: str) -> dict | None:
    """Simulate a sell: liquidate virtual position, add USD to paper_usd."""
    global paper_usd, paper_position

    if paper_position is None:
        logger.info("[PAPER SELL] No open position to sell")
        return None

    try:
        ticker = exchange.fetch_ticker(symbol)
        price_raw: float = ticker.get("bid") or ticker.get("last") or 0.0
        if price_raw <= 0:
            logger.error("[PAPER SELL] Bad price for %s: %s", symbol, price_raw)
            return None
    except Exception as exc:
        logger.error("[PAPER SELL] Price fetch error: %s", exc)
        return None

    qty = paper_position["qty"]
    price_filled = price_raw * (1.0 - SLIPPAGE)   # sell at slight slippage below ask
    usd_received = qty * price_filled
    fee_usd = usd_received * KRAKEN_TAKER_FEE
    usd_net = usd_received - fee_usd

    pnl_usd = usd_net - paper_position["size_usd"]
    pnl_pct = pnl_usd / paper_position["size_usd"]

    paper_usd += usd_net
    entry_price = paper_position["entry_price"]
    paper_position = None

    _save_paper_state()
    _log_trade("SELL", symbol, price_raw, price_filled, qty, usd_received, fee_usd, paper_usd, reason)
    logger.info("[PAPER SELL] PnL: %+.2f%% ($%+.2f)", pnl_pct * 100, pnl_usd)
    return {"price": price_filled, "qty": qty, "pnl_usd": pnl_usd, "pnl_pct": pnl_pct}


# ═══════════════════════════════════════════════════════════════════════════════
# DECISION EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def _execute_decision(decision: OrchestratorDecision, dca_last_buy_ts: dict[str, float]) -> None:
    """Apply the orchestrator decision to the paper portfolio."""
    cap = decision.capital_state

    # Core DCA fill (simulated — just record and update DCA timestamp)
    if decision.core_decision and decision.core_decision.should_buy:
        cd = decision.core_decision
        logger.info(
            "[PAPER CORE DCA] Would buy $%.2f of %s — %s",
            cd.amount_usd, cd.symbol, cd.reason,
        )
        # Record as a simulated DCA buy in the CSV
        try:
            ticker = exchange.fetch_ticker(cd.symbol)
            price_raw = ticker.get("ask") or ticker.get("last") or 0.0
            price_filled = price_raw * (1.0 + SLIPPAGE)
            fee_usd = cd.amount_usd * KRAKEN_TAKER_FEE
            qty = cd.amount_usd / price_filled if price_filled > 0 else 0.0
            total_cost = cd.amount_usd + fee_usd
            if total_cost <= paper_usd:
                _log_trade(
                    "DCA_BUY", cd.symbol, price_raw, price_filled, qty,
                    cd.amount_usd, fee_usd,
                    paper_usd - total_cost,
                    cd.reason,
                )
                dca_last_buy_ts[cd.symbol] = time.time()
                _save_dca_state(dca_last_buy_ts)
        except Exception as exc:
            logger.error("[PAPER CORE DCA] execution error: %s", exc)

    # Satellite signal execution
    if decision.satellite_signal is not None:
        sig = decision.satellite_signal
        if sig.action == "buy":
            buy_size = cap.satellite_value
            _paper_buy("BTC/USD", buy_size, sig.reason)
        elif sig.action == "sell":
            _paper_sell("BTC/USD", sig.reason)
        else:
            logger.info("[PAPER SAT] Hold — %s", sig.reason)


# ═══════════════════════════════════════════════════════════════════════════════
# DRY-RUN (spec §10 + §15 acceptance check)
# ═══════════════════════════════════════════════════════════════════════════════

def run_dry_run() -> int:
    """Run ONE orchestrator decision, log it, exit cleanly. Returns exit code."""
    logger.info("[PAPER --dry-run] Starting dry-run — one decision cycle then exit")
    logger.info("[PAPER --dry-run] Exchange: Kraken public API (no auth)")
    logger.info("[PAPER --dry-run] Starting virtual USD: $%.2f", PAPER_STARTING_USD)

    dca_last_buy_ts = _load_dca_state()
    fng_score = _fetch_fng_score()
    now_ts = time.time()

    logger.info("[PAPER --dry-run] F&G score: %.0f", fng_score)

    try:
        decision = decide(
            exchange=exchange,
            account_value=PAPER_STARTING_USD,
            fng_score=fng_score,
            dca_last_buy_ts=dca_last_buy_ts,
            open_sat_position=paper_position,
            now_ts=now_ts,
        )
    except Exception as exc:
        logger.error("[PAPER --dry-run] decide() failed: %s", exc)
        return 1

    logger.info("[PAPER --dry-run] Decision notes:")
    for note in decision.notes:
        logger.info("  • %s", note)

    # Log capital state
    cap = decision.capital_state
    logger.info(
        "[PAPER --dry-run] Capital: total=$%.2f core=$%.2f sat=$%.2f "
        "satellite_enabled=%s runway=%.2fm",
        cap.total_value, cap.core_value, cap.satellite_value,
        cap.satellite_enabled, cap.runway_months,
    )

    # Log core decision
    if decision.core_decision:
        cd = decision.core_decision
        logger.info(
            "[PAPER --dry-run] Core DCA: should_buy=%s symbol=%s amount=$%.2f reason=%s",
            cd.should_buy, cd.symbol, cd.amount_usd, cd.reason,
        )
    else:
        logger.info("[PAPER --dry-run] Core DCA: no symbol due this cycle")

    # Log satellite signal
    if decision.satellite_signal:
        sig = decision.satellite_signal
        logger.info(
            "[PAPER --dry-run] Satellite signal: action=%s confidence=%.2f reason=%s",
            sig.action, sig.confidence, sig.reason,
        )
    else:
        logger.info("[PAPER --dry-run] Satellite: disabled (account below threshold)")

    # Write one row to CSV so the file exists and can be checked
    _ensure_csv_header()
    ts = datetime.now(timezone.utc).isoformat()
    with PAPER_TRADES_CSV.open("a", newline="") as f:
        csv.writer(f).writerow([
            ts, "DRY_RUN", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
            f"{PAPER_STARTING_USD:.2f}",
            "dry-run: " + " | ".join(decision.notes),
        ])

    logger.info("[PAPER --dry-run] Complete — trade log written to %s", PAPER_TRADES_CSV)
    logger.info("[PAPER --dry-run] Exiting cleanly (code 0)")
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# FULL PAPER LOOP (not used in CI — requires Telegram token)
# ═══════════════════════════════════════════════════════════════════════════════

async def _paper_loop(app) -> None:
    """Full async paper trading loop (mirrors bot.py trading_loop)."""
    dca_last_buy_ts = _load_dca_state()

    while True:
        try:
            if not paper_paused:
                fng_score = _fetch_fng_score()
                now_ts = time.time()

                decision = decide(
                    exchange=exchange,
                    account_value=paper_usd,
                    fng_score=fng_score,
                    dca_last_buy_ts=dca_last_buy_ts,
                    open_sat_position=paper_position,
                    now_ts=now_ts,
                )
                _execute_decision(decision, dca_last_buy_ts)
                logger.info("[Loop] Notes: %s", " | ".join(decision.notes))
        except Exception as exc:
            logger.error("[Loop] Unhandled error: %s", exc)

        await asyncio.sleep(SCAN_INTERVAL_SECONDS)


async def _post_init_full(app) -> None:
    """Called after Telegram event loop starts (full paper mode)."""
    from telegram.ext import Application
    logger.info("[PAPER] v1.4 paper bot starting — full loop mode")
    _load_paper_state()
    cap = compute_state(paper_usd)

    try:
        await app.bot.send_message(
            chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            text=(
                f"<b>[PAPER] Rapid2 v1.4 Online</b>\n"
                f"Starting balance: ${PAPER_STARTING_USD:.2f}\n"
                f"Cash: ${paper_usd:.2f}\n"
                f"Satellite: {'enabled' if cap.satellite_enabled else 'paused'}\n"
                f"Runway: {cap.runway_months:.2f} months\n"
                f"No real trades will be placed."
            ),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.warning("[PAPER] Startup Telegram message failed: %s", exc)

    asyncio.create_task(_paper_loop(app))


def _run_full_loop() -> None:
    """Start the full paper trading loop (requires PAPER_TELEGRAM_TOKEN)."""
    from telegram.ext import Application

    token = os.getenv("PAPER_TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        logger.error(
            "[PAPER] PAPER_TELEGRAM_TOKEN and TELEGRAM_CHAT_ID required for full loop. "
            "Use --dry-run for testing without Telegram."
        )
        sys.exit(1)

    _load_paper_state()
    app = (
        Application.builder()
        .token(token)
        .post_init(_post_init_full)
        .build()
    )
    logger.info("[PAPER] Polling started.")
    app.run_polling()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(description="Rapid2 v1.4 paper trading harness")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run one orchestrator decision, log it, and exit cleanly (no loop, no Telegram)",
    )
    args = parser.parse_args()

    if args.dry_run:
        sys.exit(run_dry_run())
    else:
        _run_full_loop()


if __name__ == "__main__":
    main()
