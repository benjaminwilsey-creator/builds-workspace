"""bot.py — Execution engine for Rapid2 v1.4.

Responsibilities: Kraken API, Telegram bot, position state, main async loop.
No strategy logic lives here — all decisions come from strategy.decide().

Required env vars (.env):
  KRAKEN_API_KEY
  KRAKEN_API_SECRET
  TELEGRAM_TOKEN
  TELEGRAM_CHAT_ID
"""
import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import ccxt
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from capital import compute_state
from strategy import decide, OrchestratorDecision

# ── Logging ───────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/bot.log"),
    ],
)
logger = logging.getLogger(__name__)

# ── Credentials ───────────────────────────────────────────────────────────────
load_dotenv()
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", "")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Config ────────────────────────────────────────────────────────────────────
SCAN_INTERVAL_SECONDS = 900   # 15 minutes — spec §12

# ── Exchange ──────────────────────────────────────────────────────────────────
exchange = ccxt.kraken({
    "apiKey": KRAKEN_API_KEY,
    "secret": KRAKEN_API_SECRET,
    "enableRateLimit": True,
})

# ── State files ───────────────────────────────────────────────────────────────
POSITIONS_FILE = Path("positions.json")
DCA_STATE_FILE = Path("dca_state.json")

# ── In-memory state ───────────────────────────────────────────────────────────
bot_paused: bool = False
last_decision: OrchestratorDecision | None = None   # updated each scan cycle


# ═════════════════════════════════════════════════════════════════════════════
# STATE PERSISTENCE
# ═════════════════════════════════════════════════════════════════════════════

def _load_positions() -> dict | None:
    """Load the open satellite position from disk. Returns None if none saved."""
    try:
        if not POSITIONS_FILE.exists():
            return None
        data = json.loads(POSITIONS_FILE.read_text())
        return data.get("satellite_position")
    except Exception as exc:
        logger.error("[State] positions load error: %s", exc)
        return None


def _save_positions(satellite_position: dict | None) -> None:
    try:
        POSITIONS_FILE.write_text(json.dumps({"satellite_position": satellite_position}, indent=2))
    except Exception as exc:
        logger.error("[State] positions save error: %s", exc)


def _load_dca_state() -> dict[str, float]:
    """Load last DCA buy timestamps per symbol. Returns empty dict if none saved."""
    try:
        if not DCA_STATE_FILE.exists():
            return {}
        return json.loads(DCA_STATE_FILE.read_text())
    except Exception as exc:
        logger.error("[State] dca_state load error: %s", exc)
        return {}


def _save_dca_state(dca_last_buy_ts: dict[str, float]) -> None:
    try:
        DCA_STATE_FILE.write_text(json.dumps(dca_last_buy_ts, indent=2))
    except Exception as exc:
        logger.error("[State] dca_state save error: %s", exc)


# ═════════════════════════════════════════════════════════════════════════════
# ACCOUNT VALUE
# ═════════════════════════════════════════════════════════════════════════════

def get_total_account_value() -> float:
    """Fetch total account value in USD from Kraken."""
    try:
        balance = exchange.fetch_balance()
        total_usd = balance.get("total", {}).get("USD", 0.0)
        for coin, amount in balance.get("total", {}).items():
            if coin == "USD" or amount <= 0:
                continue
            try:
                total_usd += amount * exchange.fetch_ticker(f"{coin}/USD")["last"]
            except Exception:
                pass
        return total_usd
    except Exception as exc:
        logger.error("[Account] value fetch error: %s", exc)
        return 0.0


# ═════════════════════════════════════════════════════════════════════════════
# F&G HELPER
# ═════════════════════════════════════════════════════════════════════════════

def _fetch_fng_score() -> float:
    """Fetch Fear & Greed score from the public API. Returns 50.0 on error."""
    try:
        import urllib.request
        import urllib.error
        url = "https://api.alternative.me/fng/?limit=1"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            return float(data["data"][0]["value"])
    except Exception as exc:
        logger.warning("[F&G] fetch error, defaulting to 50: %s", exc)
        return 50.0


# ═════════════════════════════════════════════════════════════════════════════
# TELEGRAM HELPERS
# ═════════════════════════════════════════════════════════════════════════════

async def _send_alert(app: Application, message: str, parse_mode: str = "HTML") -> None:
    try:
        await app.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=parse_mode
        )
    except Exception as exc:
        logger.error("[Telegram] send error: %s", exc)


# ═════════════════════════════════════════════════════════════════════════════
# TELEGRAM COMMANDS — spec §9
# ═════════════════════════════════════════════════════════════════════════════

async def cmd_runway(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/runway — show runway_months and thresholds."""
    total = get_total_account_value()
    state = compute_state(total)
    text = (
        f"<b>Runway</b>\n"
        f"Account: ${total:.2f}\n"
        f"Runway: <b>{state.runway_months:.2f} months</b>\n\n"
        f"Thresholds:\n"
        f"  Satellite pause: ${70.0:.0f}\n"
        f"  Alert floor:     ${50.0:.0f}\n"
        f"  Hard floor:      ${20.0:.0f}\n"
        f"  Monthly burn:    ${12.0:.0f}"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_survival(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/survival — full CapitalState breakdown."""
    total = get_total_account_value()
    state = compute_state(total)
    sat_status = "ENABLED" if state.satellite_enabled else "PAUSED"
    alert_status = "YES — ALERT" if state.alert_floor_breached else "no"
    text = (
        f"<b>Survival / Capital State</b>\n"
        f"Total:     ${state.total_value:.2f}\n"
        f"Core (70%): ${state.core_value:.2f}\n"
        f"Sat  (30%): ${state.satellite_value:.2f}\n"
        f"Satellite: {sat_status}\n"
        f"Floor alert: {alert_status}\n"
        f"Runway: {state.runway_months:.2f} months\n"
        f"Status: {state.reason}"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_why(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/why — last OrchestratorDecision notes."""
    if last_decision is None:
        await update.message.reply_text("No decision recorded yet. Wait for the next scan cycle.")
        return
    notes_text = "\n".join(f"  • {n}" for n in last_decision.notes)
    text = f"<b>Last Decision Notes</b>\n{notes_text}"
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_core(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/core — Core DCA status."""
    dca_state = _load_dca_state()
    fng = _fetch_fng_score()

    lines = [f"<b>Core DCA Status</b>", f"F&G score: {fng:.0f}"]
    for symbol in ["BTC/USD", "ETH/USD"]:
        last_ts = dca_state.get(symbol, 0.0)
        if last_ts > 0:
            last_dt = datetime.fromtimestamp(last_ts, tz=timezone.utc)
            next_dt = datetime.fromtimestamp(last_ts + 168 * 3600, tz=timezone.utc)
            lines.append(
                f"{symbol.split('/')[0]}:\n"
                f"  Last buy: {last_dt.strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"  Next due: {next_dt.strftime('%Y-%m-%d %H:%M UTC')}"
            )
        else:
            lines.append(f"{symbol.split('/')[0]}: No buy recorded yet (due immediately)")

    if last_decision and last_decision.core_decision:
        cd = last_decision.core_decision
        lines.append(
            f"\nLast core decision: {'BUY' if cd.should_buy else 'skip'} {cd.symbol}\n"
            f"  ${cd.amount_usd:.2f} — {cd.reason}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def cmd_satellite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/satellite — Satellite position status."""
    pos = _load_positions()
    total = get_total_account_value()
    state = compute_state(total)
    sat_status = "ENABLED" if state.satellite_enabled else "PAUSED"

    lines = [f"<b>Satellite Status</b>", f"Circuit breaker: {sat_status}"]

    if pos is None:
        lines.append("Position: None (no open trade)")
    else:
        entry_price: float = pos.get("entry_price", 0.0)
        entry_ts: float = pos.get("entry_ts", 0.0)
        size_usd: float = pos.get("size_usd", 0.0)
        try:
            ticker = exchange.fetch_ticker("BTC/USD")
            current_price: float = ticker.get("last") or 0.0
            pnl_pct = (current_price - entry_price) / entry_price if entry_price else 0.0
            hold_hours = (time.time() - entry_ts) / 3600.0
            lines.append(
                f"Position: OPEN\n"
                f"  Entry: ${entry_price:.2f}\n"
                f"  Current: ${current_price:.2f}\n"
                f"  PnL: {pnl_pct:+.2%}\n"
                f"  Size: ${size_usd:.2f}\n"
                f"  Held: {hold_hours:.1f}h"
            )
        except Exception as exc:
            lines.append(f"Position: OPEN (price fetch error: {exc})")

    if last_decision and last_decision.satellite_signal:
        sig = last_decision.satellite_signal
        lines.append(f"\nLast signal: {sig.action.upper()} — {sig.reason}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/status — bot state and account value."""
    total = get_total_account_value()
    state = compute_state(total)
    pos = _load_positions()
    text = (
        f"<b>Bot Status</b>\n"
        f"{'PAUSED' if bot_paused else 'RUNNING'}\n"
        f"Account: ${total:.2f}\n"
        f"Satellite: {'enabled' if state.satellite_enabled else 'paused'}\n"
        f"Open sat position: {'yes' if pos else 'no'}\n"
        f"Scan interval: {SCAN_INTERVAL_SECONDS}s"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/balance — raw Kraken balance."""
    try:
        balance = exchange.fetch_balance()
        total = balance.get("total", {})
        lines = ["<b>Balance</b>"]
        for coin, amount in sorted(total.items()):
            if amount > 0:
                lines.append(f"  {coin}: {amount:.6f}")
        await update.message.reply_text("\n".join(lines), parse_mode="HTML")
    except Exception as exc:
        await update.message.reply_text(f"Balance fetch error: {exc}")


async def cmd_positions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/positions — open satellite position."""
    pos = _load_positions()
    if pos is None:
        await update.message.reply_text("No open satellite position.")
        return
    text = (
        f"<b>Open Position</b>\n"
        f"Symbol: BTC/USD\n"
        f"Entry: ${pos.get('entry_price', 0):.2f}\n"
        f"Size: ${pos.get('size_usd', 0):.2f}\n"
        f"Entry time: {datetime.fromtimestamp(pos.get('entry_ts', 0), tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/pause — pause trading."""
    global bot_paused
    bot_paused = True
    await update.message.reply_text("Bot paused. Use /resume to restart.")


async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/resume — resume trading."""
    global bot_paused
    bot_paused = False
    await update.message.reply_text("Bot resumed.")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN TRADING LOOP
# ═════════════════════════════════════════════════════════════════════════════

async def trading_loop(app: Application) -> None:
    """Main scan loop — runs every SCAN_INTERVAL_SECONDS."""
    global last_decision, bot_paused

    dca_last_buy_ts = _load_dca_state()

    while True:
        try:
            if not bot_paused:
                total_value = get_total_account_value()
                fng_score = _fetch_fng_score()
                open_sat_position = _load_positions()
                now_ts = time.time()

                decision = decide(
                    exchange=exchange,
                    account_value=total_value,
                    fng_score=fng_score,
                    dca_last_buy_ts=dca_last_buy_ts,
                    open_sat_position=open_sat_position,
                    now_ts=now_ts,
                )
                last_decision = decision

                # Alert on floor breach
                if decision.capital_state.alert_floor_breached:
                    await _send_alert(
                        app,
                        f"<b>ALERT: Account below ${50:.0f}</b>\n"
                        f"Current: ${total_value:.2f}\n"
                        f"Runway: {decision.capital_state.runway_months:.2f} months",
                    )

                # Log the full decision notes
                logger.info("[Loop] Decision notes: %s", " | ".join(decision.notes))

        except Exception as exc:
            logger.error("[Loop] Unhandled error: %s", exc)

        await asyncio.sleep(SCAN_INTERVAL_SECONDS)


# ═════════════════════════════════════════════════════════════════════════════
# STARTUP
# ═════════════════════════════════════════════════════════════════════════════

async def post_init(app: Application) -> None:
    """Called after Telegram event loop starts. Launches trading loop."""
    logger.info("Trading Bot v1.4 starting — Core + Satellite")
    total_value = get_total_account_value()
    state = compute_state(total_value)

    logger.info("[Startup] Account: $%.2f | Satellite: %s", total_value, state.satellite_enabled)

    await _send_alert(
        app,
        f"<b>Bot Online — v1.4</b>\n"
        f"Account: ${total_value:.2f}\n"
        f"Satellite: {'enabled' if state.satellite_enabled else 'paused'}\n"
        f"Runway: {state.runway_months:.2f} months\n"
        f"Scan: every {SCAN_INTERVAL_SECONDS}s",
    )

    asyncio.create_task(trading_loop(app))


def main() -> None:
    if not all([KRAKEN_API_KEY, KRAKEN_API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        raise RuntimeError("Missing required env vars. Check your .env file.")

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("runway",    cmd_runway))
    app.add_handler(CommandHandler("survival",  cmd_survival))
    app.add_handler(CommandHandler("why",       cmd_why))
    app.add_handler(CommandHandler("core",      cmd_core))
    app.add_handler(CommandHandler("satellite", cmd_satellite))
    app.add_handler(CommandHandler("status",    cmd_status))
    app.add_handler(CommandHandler("balance",   cmd_balance))
    app.add_handler(CommandHandler("positions", cmd_positions))
    app.add_handler(CommandHandler("pause",     cmd_pause))
    app.add_handler(CommandHandler("resume",    cmd_resume))

    logger.info("Bot polling started.")
    app.run_polling()


if __name__ == "__main__":
    main()
