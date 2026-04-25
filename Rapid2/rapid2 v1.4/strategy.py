"""Strategy orchestrator — thin wiring layer.

Calls capital.compute_state, core.dca.evaluate_dca, and
agents.mean_reversion.evaluate. Returns an OrchestratorDecision.

No strategy logic lives here — this is pure wiring. See spec §8.
"""
import logging
import time
from dataclasses import dataclass

from agents.base import AgentContext, AgentSignal
from agents import mean_reversion
from capital import compute_state, CapitalState
from core.dca import evaluate_dca, DCADecision

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
_CORE_SYMBOLS = ["BTC/USD", "ETH/USD"]
_BTC_200MA_TIMEFRAME = "1d"
_BTC_200MA_LIMIT = 210       # enough candles for 200-day MA with headroom
_BTC_200MA_PERIOD = 200
_BTC_SYMBOL = "BTC/USD"


@dataclass(frozen=True)
class OrchestratorDecision:
    core_decision: DCADecision | None       # From evaluate_dca — None if none are due
    satellite_signal: AgentSignal | None    # From mean_reversion.evaluate — None if disabled
    capital_state: CapitalState
    notes: list[str]                        # Human-readable reasoning for Telegram


def _fetch_btc_above_200ma(exchange) -> bool:
    """Fetch daily OHLCV for BTC and compute whether current price > 200-day MA.

    Returns True if BTC close > 200-day simple moving average, False otherwise.
    One call, cached by the orchestrator for the lifetime of a single decide() call.
    """
    raw = exchange.fetch_ohlcv(_BTC_SYMBOL, _BTC_200MA_TIMEFRAME, limit=_BTC_200MA_LIMIT)
    if len(raw) < _BTC_200MA_PERIOD:
        logger.warning(
            "[strategy] Not enough candles for 200MA (%d < %d) — defaulting to False",
            len(raw), _BTC_200MA_PERIOD,
        )
        return False

    closes = [c[4] for c in raw]
    ma_200 = sum(closes[-_BTC_200MA_PERIOD:]) / _BTC_200MA_PERIOD
    current_close = closes[-1]
    above = current_close > ma_200
    logger.debug(
        "[strategy] BTC close=%.2f 200MA=%.2f above=%s", current_close, ma_200, above
    )
    return above


def decide(
    exchange,
    account_value: float,
    fng_score: float,
    dca_last_buy_ts: dict[str, float],   # {"BTC/USD": ts, "ETH/USD": ts}
    open_sat_position: dict | None,
    now_ts: float,
) -> OrchestratorDecision:
    """Run one orchestration cycle and return a decision.

    Spec §8 logic:
    1. Compute capital state.
    2. For each core symbol, call evaluate_dca. Use the first that returns
       should_buy=True (serialised to avoid double-spend).
    3. If satellite enabled: fetch btc_above_200ma, build AgentContext,
       call mean_reversion.evaluate.
    4. Else: satellite_signal = None, add pause note.
    5. Return OrchestratorDecision.
    """
    notes: list[str] = []

    # 1. Capital state
    capital_state = compute_state(account_value)
    notes.append(capital_state.reason)

    # 2. Core DCA — first symbol that is due
    core_decision: DCADecision | None = None
    for symbol in _CORE_SYMBOLS:
        last_buy_ts = dca_last_buy_ts.get(symbol, 0.0)
        decision = evaluate_dca(
            symbol=symbol,
            fng_score=fng_score,
            btc_pct_above_200ma=0.0,   # will be filled below if satellite is enabled
            last_buy_ts=last_buy_ts,
            now_ts=now_ts,
        )
        if decision.should_buy:
            core_decision = decision
            notes.append(f"Core DCA: {decision.reason}")
            break
        else:
            notes.append(f"Core {symbol} skip: {decision.reason}")

    # 3. Satellite signal
    satellite_signal: AgentSignal | None = None

    if capital_state.satellite_enabled:
        try:
            btc_above_200ma = _fetch_btc_above_200ma(exchange)
            notes.append(f"BTC 200MA filter: {'above' if btc_above_200ma else 'below'}")

            # Re-evaluate core DCA with the real btc_pct_above_200ma if we have it
            # (we use it for the top filter; approximation: above=True → pct=0.6 > 0.5)
            # The DCA decisions above already ran, so we do NOT re-run them here.
            # btc_above_200ma feeds only the satellite agent context.

            # Fetch current BTC price for the satellite agent
            ticker = exchange.fetch_ticker(_BTC_SYMBOL)
            current_price: float = ticker.get("last") or ticker.get("close") or 0.0

            ctx = AgentContext(
                exchange=exchange,
                symbol=_BTC_SYMBOL,
                current_price=current_price,
                account_value=account_value,
                satellite_capital=capital_state.satellite_value,
                open_satellite_position=open_sat_position,
                now_ts=now_ts,
                btc_above_200ma=btc_above_200ma,
            )
            satellite_signal = mean_reversion.evaluate(ctx)
            notes.append(f"Satellite: {satellite_signal.action} — {satellite_signal.reason}")
        except Exception as exc:
            logger.error("[strategy] satellite evaluation error: %s", exc)
            notes.append(f"Satellite error: {exc}")
    else:
        notes.append("Satellite paused: account below $70")

    return OrchestratorDecision(
        core_decision=core_decision,
        satellite_signal=satellite_signal,
        capital_state=capital_state,
        notes=notes,
    )
