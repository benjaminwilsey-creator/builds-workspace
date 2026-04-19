# CLAUDE.md — FinancialManager

## What It Does
Monitors Benjamin's Truist bank account via Plaid, tracks 9 recurring bills, and sends
Slack reminders to Benjamin and Liz when bills are due or missed. Local-only — no cloud deploy.

## Stack
- Python 3.12
- Plaid API — reads Truist transactions (read-only access)
- Slack SDK — sends alerts to #finances channel
- APScheduler — runs daily check at a configured time
- PyYAML — bill definitions in bills.yaml
- python-dotenv — secret management

## Key Files
| File | Purpose |
|---|---|
| `bills.yaml` | Bill schedule — edit this to add/update bills |
| `src/config.py` | Env var loading. Use `require_env()` for required vars, `get_env()` for optional |
| `src/plaid_client.py` | Reads Truist transactions via Plaid API (read-only) |
| `src/bill_tracker.py` | Bill due-date logic, paid/unpaid state, loads bills.yaml |
| `src/slack_notifier.py` | Sends all Slack messages |
| `src/scheduler.py` | APScheduler job — runs daily, orchestrates the full check |
| `data/bill_state.json` | Local state file — tracks what's been paid this month (gitignored) |
| `logs/audit.log` | Audit trail of every alert sent and payment detected (gitignored) |
| `.env` | Secrets — never commit this file |
| `.env.example` | Template — commit this, keep values blank |

## Security Rules — Non-Negotiable
- **Never log, print, or include the value of any env var in output** — not PLAID_SECRET, not SLACK_BOT_TOKEN, not any token or key
- **Never commit .env** — it is gitignored; verify before every commit
- **Plaid access is read-only** — never request write or transfer scopes unless explicitly instructed
- **No payment execution** — this system notifies only; Benjamin pays manually via the Truist app
- **Audit log every alert and action** — use `_audit()` in scheduler.py for all significant events
- **No user data in logs beyond bill name and amount** — no account numbers, routing numbers, or personal info

## Bills Configuration
Bills are defined in `bills.yaml`. Two types:
- `fixed` — same amount every month. Set `fixed_amount`.
- `variable` — amount varies. Plaid detects the amount from the transaction.

`payee_keywords` are matched against Plaid transaction names. Check your Truist statement
for the exact merchant string and add relevant words.

## How to Run
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in your secrets
cp .env.example .env

# Run the scheduler (stays running, checks daily)
python -m src.scheduler

# Test a single check right now (without waiting for schedule)
python -c "from src.scheduler import run_daily_check; run_daily_check()"
```

## Plaid Setup (one-time)
1. Create a free account at https://dashboard.plaid.com
2. Create an app — choose "Personal Finance" category
3. Copy Client ID and Secret into .env
4. Set PLAID_ENV=development for testing, production when ready
5. Run the Plaid Link flow to connect your Truist account and get PLAID_ACCESS_TOKEN
   (A setup script will be built for this step)

## Testing Rules
- Use pytest + pytest-mock
- Mock all external calls: Plaid API, Slack API
- Never make real API calls in tests
- Run: `pytest tests/ -v`

## What NOT to Build
- Bill payment automation (no ACH initiation, no browser automation — security boundary)
- A web dashboard or API — this is a local script, not a server
- Multi-bank support (Truist only for now)
- Budget tracking or spending analysis (out of scope for this project)
