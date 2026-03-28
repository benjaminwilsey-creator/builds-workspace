# Memory

## Project Overview
Primary workspace: `E:\Builds - Copy` (dedicated dev drive — migration complete 2026-03-22). C drive (`c:\Users\benja\OneDrive\Documents\Builds`) is no longer primary.

1. **Rapid2** — Production crypto trading bot (OpenClaw) — primary active project
2. **Booksmut** — ReelForge BookTok affiliate video pipeline — Full pipeline complete as of 2026-03-23. ENRICHED→SCORED→SCRIPTED→VOICED→COMPOSED→PUBLISHED. Delivery tab + Publisher Licenses tab live. Next: Gmail outreach integration (ADR 0003).
3. **Architect** — Claude skill files for developer workflow — standalone repo
4. **Model Skills** — AI model-specific configs (Gemini, Qwen) — standalone repo
5. **3DPrint** (name TBD) — Plain-language to STL converter for Ricky's Bambu A1 — concept only, not yet scaffolded

See [rapid2.md](rapid2.md) for full Rapid2 details.
See [booksmut.md](booksmut.md) for full Booksmut/ReelForge details.
See [3dprint.md](3dprint.md) for full 3DPrint details.
See [github_restructure_2026-03-22.md](github_restructure_2026-03-22.md) for full repo/branch layout and migration instructions.

## User Preferences
- Platform: Windows with MSYS bash
- IDE: VS Code
- Deployment: AWS EC2 (scp push + systemd restart)
- Communication: plain English, no jargon, explain the "why"
- python-docx and ccxt installed on Python 3.14 (`/c/Users/benja/AppData/Local/Python/pythoncore-3.14-64/python.exe`) — can convert .md -> .docx, run backtests

## Key Credentials Locations
- Rapid2 v1 `.env`: `Builds\Rapid2\rapid2 (Program)\.env` (retired — but still holds working Kraken creds)
- Rapid2 v1.2 `.env`: `Builds\Rapid2\rapid2 v1.2\.env` (live trading creds — production)
- AWS SSH key: `C:\Users\benja\OneDrive\Documents\KeePass\AWS\rapid2-key.pem`

## EC2 Servers
| Server | IP | SSH Alias | Service | Purpose |
|--------|-----|-----------|---------|---------|
| Rapid2 v1 (Retired) | `3.131.96.193` | none | `openclaw` | TERMINATED 2026-03-04 — instance gone |
| Rapid2 v1.2 (Production) | `3.138.144.246` | `rapid2` | `openclaw-paper` | Live trading — real money, runs FULL v1.3 codebase (bot.py + strategy.py + sentiment.py from v1.3 folder) |
| Rapid2 v1.3 (Paper) | `3.138.144.246` | `rapid2` | `openclaw-paper-v1.3` | Paper trading — v1.3 regime strategy |
| Old openclaw (disabled) | `3.138.144.246` | `rapid2` | `openclaw` | Stopped & disabled 2026-03-25 — was causing Telegram conflicts |

## GitHub Repos
| Repo | Branches | What's in it |
|------|----------|--------------|
| builds-workspace | master, develop | CLAUDE.md, Developer Quick Reference. PUBLIC. Architect/, Booksmut/, model-skills/, Sportsball/ all gitignored. |
| openclaw | master, 1.3try, v1.2, v1 | All trading bot versions. 1.3try=active development, v1.2/v1=archived history. |
| architect-skills | master, develop | All Claude Code .skill files |
| reelforge | main, develop | Booksmut/ReelForge BookTok pipeline. |
| model-specific-skills | main, develop, gemini, qwen | Gemini config on gemini branch. Qwen placeholder. |
| openclaw-v1.2 | — | ARCHIVED. Code preserved in openclaw repo v1.2 branch. |
| openclaw-v1 | — | ARCHIVED. Code preserved in openclaw repo v1 branch. |

Note: memory files are backed up to `Builds/memory/` in builds-workspace repo. Update both locations when memory changes.

Note: Booksmut is fully tracked in reelforge repo — no longer in builds-workspace.

## E Drive Layout (primary workspace)
| Folder | Repo | Branch |
|--------|------|--------|
| `E:\Builds - Copy\` | builds-workspace | master |
| `E:\Builds - Copy\Architect\` | architect-skills | master |
| `E:\Builds - Copy\Booksmut\` | reelforge | main |
| `E:\Builds - Copy\Rapid2\rapid2 v1.2\` | openclaw | v1.2 |
| `E:\Builds - Copy\Rapid2\rapid2 v1.3\` | openclaw | 1.3try |
| `E:\Builds - Copy\model-skills\` | model-specific-skills | main |
| `E:\Builds - Copy\Sportsball\` | (gitignored — GitKraken lock, do not delete) | — |

## EC2 Monitoring
| Monitor | What it watches | Alert method |
|---------|----------------|--------------|
| Error alerter cron | Bot logs — errors/crashes (every 5 min) | Telegram |
| UptimeRobot | Server up/down (TCP port 22) | Email |
| CloudWatch | RAM > 85% on paper trading server | Email |

- Error alerter script: `/home/ubuntu/error_alert.sh`
- CloudWatch alarm name: `rapid2-memory-high` (paper server only)

## Sub-Agent Pattern (updated 2026-03-06)
Five skills now run as isolated sub-agents via the Agent tool:
- `/catchup` — SSH output, logs, JSON state stay out of main context
- `/review` — code files read in sub-agent; only the verdict report returns
- `/spike` — web search results stay in sub-agent; only the spike report returns
- `/status` — SSH + state JSON isolated; only formatted health report returns
- `/impact` — grep/read results isolated; only impact report returns

Pattern: main agent spawns Agent tool (subagent_type="general-purpose") with self-contained
task prompt. Sub-agent does all data gathering, returns only the formatted report.

Note: catchup.skill now uses E drive paths and runs git pull at session start.

## Context Hygiene
- `/clear` between unrelated topics — prevents context drift
- `/compact` at ~70% context usage — compresses without losing gist
- Two-correction rule: if you've corrected Claude twice on the same thing, `/clear` and restart with a sharper prompt
- `.claudeignore` at Builds root excludes: state/, .venv/, .env, .pem, __pycache__, Build Log.md, .claude/worktrees/

## Planned Improvements (not yet built)
Priority order for next development session on the agent/bot:
1. S3 state backup — save paper_state.json to S3 after each trade, load on startup if local missing
2. Watchlist config file — move TIER2/TIER3_WATCHLIST from bot.py to JSON config, hot-reload each scan
3. `/performance` skill — parse trade logs, report win rate, P&L, signal accuracy

## Feedback / How to Work With Benjamin
See [feedback_terminal_instructions.md](feedback_terminal_instructions.md) — always specify terminal and directory with every command. PowerShell doesn't support bash for loops — write commands individually.
See [feedback_contrarian_strategy.md](feedback_contrarian_strategy.md) — fear = accumulation, greed = defense. Never block entries during fear.

## Windows Tooling Gotchas
- **Edit tool fails** on paths with spaces in directory name (e.g. `rapid2 v1.2`) — workaround: write Python script to `/c/Users/benja/AppData/Local/Temp/`, execute with `/c/Users/benja/AppData/Local/Python/pythoncore-3.14-64/python.exe`
- **Write tool also fails** with EEXIST error on existing directories — same workaround applies
- **Bash -c inline Python** fails if code contains `${...}` — bash expands them as variables; use the file workaround instead
