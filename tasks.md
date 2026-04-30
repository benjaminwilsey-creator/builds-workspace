# Agent Task Queue

> Add tasks below before leaving. The autonomous agent works top-to-bottom.
> Do NOT edit tasks marked `in-progress` or `done` — the agent owns those.
>
> **Format:** Lite Conductor tracks (TRACK-ID + Spec + Acceptance + Phase).
> Tracks without Spec/Acceptance will be skipped by /autonomous.
> Slack channel for updates: #claude-agent

---

## Pending

## [TRACK-R14-001] Scaffold Rapid2 v1.4 directory and CLAUDE.md
**Status:** done
**Branch:** agent/r14-001-phase1-2026-04-20
**Spec:** Create the `rapid2 v1.4/` directory skeleton with all module stubs, CLAUDE.md, README.md, and copy .env.example + requirements.txt from v1.3 — no logic yet, just importable scaffolding.
**Acceptance:** Directory `e:/Builds - Copy/Rapid2/rapid2 v1.4/` exists with the exact file tree in §3 of v1.4_SPEC.md, every .py file has a module docstring and empty stub functions matching the signatures in the spec, `rapid2 v1.4/CLAUDE.md` matches §11 of the spec verbatim, and running `python -c "import bot, strategy, capital; from core import dca; from agents import base, mean_reversion"` from inside the v1.4 dir exits 0 with no ImportError.
**Phase:** 1 of 1

### Phase 1 — Scaffold
- [x] Read `e:/Builds - Copy/Rapid2/v1.4_SPEC.md` in full first — it is the source of truth
- [x] Read `e:/Builds - Copy/Rapid2/rapid2 v1.3/CLAUDE.md` for project conventions
- [x] Create directory tree exactly as in §3 of the spec (do NOT add extra files)
- [x] For every .py file: write the module docstring, imports, and `pass`-body stub functions/dataclasses whose signatures exactly match the spec
- [x] Write `rapid2 v1.4/CLAUDE.md` using the verbatim content from §11 of the spec
- [x] Write a one-page `rapid2 v1.4/README.md` summarizing Core + Satellite architecture and how to run paper_bot.py
- [x] Copy `requirements.txt` and `.env.example` from `rapid2 v1.3/` into `rapid2 v1.4/`
- [x] Remove any LunarCrush or CryptoCompare deps from the v1.4 `requirements.txt`
- [x] Create `deploy.sh` as a blank stub with a comment: `# v1.4 deploy intentionally blank — paper only`
- [x] Verify: `cd "rapid2 v1.4" && python -c "import bot, strategy, capital; from core import dca; from agents import base, mean_reversion"` exits 0

## [TRACK-R14-002] Port execution engine (bot.py) to v1.4
**Status:** done
**Branch:** agent/r14-002-phase1-2026-04-20
**Spec:** Port v1.3's bot.py to v1.4 as a pure execution engine — Kraken client, Telegram setup, async loop, state persistence — with ALL strategy/regime/QF logic stripped out.
**Acceptance:** `rapid2 v1.4/bot.py` contains no references to regime, tier, QF, LunarCrush, or CryptoCompare; imports only `strategy.decide` from the v1.4 strategy module; scan interval is 900s per spec §12; the five new Telegram commands (`/runway`, `/survival`, `/why`, `/core`, `/satellite`) are registered (may return placeholder strings — real content comes in later tracks); `/mode` command is removed; `python bot.py --help` or equivalent startup check runs without ImportError.
**Phase:** 1 of 1

### Phase 1 — Port
- [x] Read `e:/Builds - Copy/Rapid2/v1.4_SPEC.md` §9, §11, §12 first
- [x] Read `e:/Builds - Copy/Rapid2/rapid2 v1.3/bot.py` in full
- [x] Copy bot.py to `rapid2 v1.4/bot.py`
- [x] Strip all imports of regime/tier/QF helpers from strategy.py v1.3
- [x] Strip CryptoCompare + LunarCrush integration completely
- [x] Replace the trading-loop body with a call to `strategy.decide(...)` — handle `OrchestratorDecision` return type
- [x] Set `SCAN_INTERVAL_SECONDS = 900` at module level
- [x] Register Telegram commands `/runway`, `/survival`, `/why`, `/core`, `/satellite` with placeholder handlers that reply "not yet wired (track R14-004)"
- [x] Remove `/mode` command handler entirely
- [x] Add `dca_state.json` persistence (load/save dict of `{symbol: last_buy_ts}`) alongside existing `positions.json`
- [x] Verify: file compiles (`python -m py_compile bot.py`) and imports succeed
- [x] DO NOT run the bot — never start `python bot.py` in full

## [TRACK-R14-003] Implement Core — Enhanced Fear-DCA
**Status:** done
**Branch:** agent/r14-003-phase1-2026-04-20
**Spec:** Implement `core/dca.py` as a pure function per spec §5, with full pytest coverage of every decision branch.
**Acceptance:** `core/dca.py` defines `DCADecision` dataclass and `evaluate_dca(...)` function exactly matching §5 signature; all constants from §12 are defined as module-level; `tests/test_dca.py` contains the 6 test cases listed in §5 (all passing); `pytest tests/test_dca.py -v` exits 0 with 6 passed; the function is pure (no network calls, no file I/O, no imports of ccxt).
**Phase:** 1 of 1

### Phase 1 — Build DCA + tests
- [x] Read `v1.4_SPEC.md` §5 and §12 first
- [x] Implement `rapid2 v1.4/core/dca.py` per spec — constants at top, dataclass, single public `evaluate_dca` function
- [x] Follow the exact logic order: interval gate → top filter → F&G multiplier → min-order check
- [x] Keep function pure — no I/O, no ccxt imports, only stdlib + dataclasses
- [x] Write `rapid2 v1.4/tests/test_dca.py` covering all 6 cases listed in §5
- [x] Run `cd "rapid2 v1.4" && pytest tests/test_dca.py -v` — must exit 0 with 6 passed

## [TRACK-R14-004] Implement Satellite — Mean-Reversion Agent + base interface
**Status:** done
**Branch:** agent/r14-004-phase1-2026-04-20
**Spec:** Implement `agents/base.py` (AgentContext, AgentSignal) and `agents/mean_reversion.py` (pure function) per spec §4 and §6, with full pytest coverage.
**Acceptance:** `agents/base.py` defines both dataclasses exactly as in §4; `agents/mean_reversion.py` exports `evaluate(ctx: AgentContext) -> AgentSignal` following §6 logic; mocks `exchange.fetch_ohlcv` in tests — no live network; `tests/test_mean_reversion.py` contains the 9 test cases listed in §6 (all passing); `pytest tests/test_mean_reversion.py -v` exits 0.
**Phase:** 1 of 1

### Phase 1 — Build agent + tests
- [x] Read `v1.4_SPEC.md` §4 and §6 first
- [x] Implement `rapid2 v1.4/agents/base.py` — frozen dataclasses, type hints, no logic
- [x] Implement `rapid2 v1.4/agents/mean_reversion.py` with constants at top and the `evaluate` function
- [x] Compute RSI(14) and Bollinger Bands from `ctx.exchange.fetch_ohlcv(symbol, "4h", limit=100)` — pure numpy-free stdlib math is fine
- [x] Order of checks: open-position exit logic first (TP/SL/time-stop), then entry logic (trend filter → RSI → BB → confirmation)
- [x] Write `rapid2 v1.4/tests/test_mean_reversion.py` mocking `fetch_ohlcv` — all 9 cases from §6
- [x] Run `cd "rapid2 v1.4" && pytest tests/test_mean_reversion.py -v` — must exit 0 with 9 passed

## [TRACK-R14-005] Implement Capital module + Strategy orchestrator + Telegram wiring
**Status:** in-progress
**Spec:** Implement `capital.py` (circuit breaker) per §7, `strategy.py` (orchestrator) per §8, and replace placeholder Telegram handlers in bot.py with real implementations per §9.
**Acceptance:** `capital.py` defines CapitalState and `compute_state(...)` per §7 with all 4 thresholds as module constants; `strategy.py` defines `OrchestratorDecision` and `decide(...)` per §8; the 5 Telegram commands in bot.py (`/runway`, `/survival`, `/why`, `/core`, `/satellite`) return real data using capital/strategy modules (not placeholders); `tests/test_capital.py` covers the 5 cases in §7 and `tests/test_strategy.py` covers the 4 cases in §8; `pytest tests/test_capital.py tests/test_strategy.py -v` exits 0.
**Phase:** 1 of 1

### Phase 1 — Build capital + orchestrator + wire Telegram
- [ ] Read `v1.4_SPEC.md` §7, §8, §9 first
- [ ] Implement `rapid2 v1.4/capital.py` per §7 — constants at top, dataclass, `compute_state` function
- [ ] Implement `rapid2 v1.4/strategy.py` per §8 — thin orchestrator, calls `core.dca.evaluate_dca` for each core symbol and `agents.mean_reversion.evaluate` when satellite enabled
- [ ] In strategy.py, add a helper to determine `btc_above_200ma` from a fetch_ohlcv call — one call cached for the decision
- [ ] In bot.py, replace the 5 placeholder Telegram handlers with real ones that call `capital.compute_state` and use the last stored `OrchestratorDecision`
- [ ] Write `tests/test_capital.py` — 5 cases from §7
- [ ] Write `tests/test_strategy.py` — 4 cases from §8, mock fetch_ohlcv for the 200MA check
- [ ] Run `cd "rapid2 v1.4" && pytest tests/test_capital.py tests/test_strategy.py -v` — must exit 0

## [TRACK-R14-006] Paper trading harness + full test suite + validation
**Status:** planned
**Spec:** Implement `paper_bot.py` per §10 and run the full test suite + the meta-acceptance checks from §15.
**Acceptance:** `paper_bot.py` starts, connects to Kraken public API (OHLCV only, no auth), runs one orchestrator decision, logs it, and exits cleanly on a `--dry-run` flag (without entering the real async loop); `pytest tests/ -v` passes green with every test collected; `python -c "import bot, strategy, capital; from core import dca; from agents import base, mean_reversion"` exits 0; a `PAPER_VALIDATION.md` file documents the 5 meta-acceptance checks from §15 as run + pass/fail results; NO live run, NO deploy to EC2.
**Phase:** 1 of 1

### Phase 1 — Paper harness + final validation
- [ ] Read `v1.4_SPEC.md` §10 and §15 first
- [ ] Implement `rapid2 v1.4/paper_bot.py` per §10 — simulated fills, taker fee applied, separate Telegram token env var, trade log to `logs/paper_trades.csv`
- [ ] Add a `--dry-run` flag to paper_bot.py that performs ONE orchestrator decision, prints it, writes one row to the log, and exits — no infinite loop
- [ ] Run `cd "rapid2 v1.4" && pytest tests/ -v` — must exit 0 with all tests from earlier tracks passing
- [ ] Run `cd "rapid2 v1.4" && python paper_bot.py --dry-run` — must exit 0 (needs only Kraken public API, no keys)
- [ ] Write `rapid2 v1.4/PAPER_VALIDATION.md` listing each of the 5 checks in §15 with pass/fail status + any blockers
- [ ] DO NOT start bot.py, DO NOT deploy, DO NOT run paper_bot.py without --dry-run

---

## BusyMomBrainDump — Phase 1 Gaps (LEGACY FORMAT — WILL BE SKIPPED)

> ⚠️ These tasks use the flat checkbox format, not Lite Conductor. The /autonomous skill will skip them because they lack `Spec:` and `Acceptance:` lines. Convert them before running /autonomous, or expect them to be flagged.

- [ ] BusyMomBrainDump: Write pytest tests for POST /brain-dumps in tests/test_main.py. Cover: happy path (chore + event routed correctly), auth failure returns 401, empty items list returns 422, dry_run=true returns dry_run status without calling external APIs, mixed items where one errors and others succeed. Mock skylight_client.add_chore and GoogleCalendarClient.create_event. Use FastAPI TestClient from httpx.
- [ ] BusyMomBrainDump: Write pytest tests for POST /chores in tests/test_chores.py. Cover: valid chores routed to Skylight, invalid assigned_to (non-child) returns error, auth failure returns 401, dry_run mode. Mock add_chore. Reuse auth patterns from test_main.py.
- [ ] BusyMomBrainDump: Write OpenAPI schema file brain_dumps_openapi.yaml for the POST /brain-dumps endpoint. Model it after custom_gpt_add_chore_openapi.yaml. Include all fields from BrainDumpRequest and BrainDumpItem in main.py. Include all response fields from BrainDumpResponse. Server URL: https://busy-mom-brain-dump-api.onrender.com. Use bearer auth.
- [ ] BusyMomBrainDump: Update render.yaml to declare all required env vars. Non-secret vars (ENV, APP_TIMEZONE) can have inline values. Secret vars (GPT_ACTION_API_KEY, GOOGLE_OAUTH_CREDENTIALS_JSON, GOOGLE_OAUTH_TOKEN_JSON, GOOGLE_FAMILY_CALENDAR_ID, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SKYLIGHT_EMAIL, SKYLIGHT_PASSWORD, SKYLIGHT_FRAME_ID) should use sync: false so Render prompts for them. Do not hardcode any values.

## In Progress

<!-- Agent moves tasks here when it starts them — do not edit -->

## Done

<!-- Agent moves tasks here when complete — includes branch name and PR link -->
