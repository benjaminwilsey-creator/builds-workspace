---
name: FinancialManager
description: Local Python bill tracker — Plaid reads Truist, Slack sends reminders, scaffolded 2026-04-18
type: project
originSessionId: 38e30724-452d-4497-9805-9aa1f0ab82c7
---
## What It Does
Monitors Benjamin's Truist bank account via Plaid (read-only), tracks 9 recurring bills,
and sends Slack reminders to Benjamin and Liz when bills are coming due or missed.
Benjamin pays manually via the Truist app — no automated payment.

## Location
`e:/Builds - Copy/FinancialManager/`

## Architecture Decision
**Notify + manual pay only** — Truist has no public bill pay API. Browser automation
was considered and rejected: against Truist's ToS, fragile, and risky with real money.

## Stack
- Python 3.12 + Plaid API (read-only) + Slack SDK + APScheduler
- Bills defined in `bills.yaml` — two types: fixed (same amount) and variable (read from Plaid)
- Local state in `data/bill_state.json` (gitignored)
- Audit log in `logs/audit.log` (gitignored)

## 9 Bills Configured
Electric, Gas, Water, Sanitation (variable) + Car Payment, Car Insurance, Cell Phone, Orthodontist, Student Loan (fixed)

## Current State (as of 2026-04-18)
Project scaffolded — **not yet running**. Three setup steps remaining:

1. Fill in `bills.yaml` — add actual due dates, fixed amounts, and provider/payee names
2. Create free Plaid developer account → connect Truist → get `PLAID_ACCESS_TOKEN`
3. Create Slack app → install to workspace → copy bot token → create `#finances` channel

## Key Files
| File | Purpose |
|---|---|
| `bills.yaml` | Bill schedule — fill in before first run |
| `.env.example` | All required env vars documented here |
| `src/scheduler.py` | Entry point — `python -m src.scheduler` |
| `src/plaid_client.py` | Reads Truist transactions |
| `src/bill_tracker.py` | Due date logic, paid/unpaid state |
| `src/slack_notifier.py` | All Slack messages |
