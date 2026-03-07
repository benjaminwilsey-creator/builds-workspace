# Memory

## Project Overview
Three projects in `c:\Users\benja\OneDrive\Documents\Builds`:

1. **Rapid2** — Production crypto trading bot (OpenClaw) — primary active project
2. **Booksmut** — ReelForge BookTok affiliate video pipeline — design complete, Phase 0 ready to start
3. **Architect** — Claude skill files for markdown hierarchy processing

See [rapid2.md](rapid2.md) for full Rapid2 details.
See [booksmut.md](booksmut.md) for full Booksmut/ReelForge details.

## User Preferences
- Platform: Windows with MSYS bash
- IDE: VS Code
- Deployment: AWS EC2 (scp push + systemd restart)
- Communication: plain English, no jargon, explain the "why"
- python-docx installed on Python 3.14 (`/c/Users/benja/AppData/Local/Python/pythoncore-3.14-64/python.exe`) — can convert .md → .docx

## Key Credentials Locations
- Rapid2 v1 `.env`: `Builds\Rapid2\rapid2 (Program)\.env` (retired — but still holds working Kraken creds)
- Rapid2 v1.2 `.env`: `Builds\Rapid2\rapid2 v1.2\.env` (live trading creds — production)
- AWS SSH key: `C:\Users\benja\OneDrive\Documents\KeePass\AWS\rapid2-key.pem`

## EC2 Servers
| Server | IP | SSH Alias | Service | Purpose |
|--------|-----|-----------|---------|---------|
| Rapid2 v1 (Retired) | `3.131.96.193` | none | `openclaw` | TERMINATED 2026-03-04 — instance gone |
| Rapid2 v1.2 (Production) | `3.138.144.246` | `rapid2` | `openclaw-paper` | Live trading — real money |

## GitHub Repos
| Repo | URL | What's in it |
|------|-----|--------------|
| builds-workspace | https://github.com/benjaminwilsey-creator/builds-workspace | CLAUDE.md, all skills, memory backups, workspace config |
| openclaw-v1.2 | https://github.com/benjaminwilsey-creator/openclaw-v1.2 | Production bot source code (v1.2) |
| openclaw-v1 | https://github.com/benjaminwilsey-creator/openclaw-v1 | Retired v1 source code |
| reelforge | https://github.com/benjaminwilsey-creator/reelforge | Booksmut/ReelForge — BookTok pipeline (Codespaces ready) |

Note: memory files are backed up to `Builds/memory/` in builds-workspace repo. Update both locations when memory changes.

## EC2 Monitoring
| Monitor | What it watches | Alert method |
|---------|----------------|--------------|
| Error alerter cron | Bot logs — errors/crashes (every 5 min) | Telegram |
| UptimeRobot | Server up/down (TCP port 22) | Email |
| CloudWatch | RAM > 85% on paper trading server | Email |

- Error alerter script: `/home/ubuntu/error_alert.sh`
- CloudWatch alarm name: `rapid2-memory-high` (paper server only)

## Sub-Agent Pattern (added 2026-03-06)
Three context-heavy skills now run as isolated sub-agents via the Agent tool:
- `/catchup` — SSH output, logs, JSON state stay out of main context
- `/review` — code files read in sub-agent; only the verdict report returns
- `/spike` — web search results stay in sub-agent; only the spike report returns

Pattern: main agent spawns Agent tool (subagent_type="general") with self-contained
task prompt. Sub-agent does all data gathering, returns only the formatted report.

## Context Hygiene
- `/clear` between unrelated topics — prevents context drift
- `/compact` at ~70% context usage — compresses without losing gist
- Two-correction rule: if you've corrected Claude twice on the same thing, `/clear` and restart with a sharper prompt
- `.claudeignore` at Builds root excludes: state/, .venv/, .env, .pem, __pycache__, Build Log.md, .claude/worktrees/

## Windows Tooling Gotchas
- **Edit tool fails** on paths with spaces in directory name (e.g. `rapid2 v1.2`) — workaround: write Python script to `/c/Users/benja/AppData/Local/Temp/`, execute with `/c/Users/benja/AppData/Local/Python/pythoncore-3.14-64/python.exe`
- **Write tool also fails** with EEXIST error on existing directories — same workaround applies
- **Bash -c inline Python** fails if code contains `${...}` — bash expands them as variables; use the file workaround instead
