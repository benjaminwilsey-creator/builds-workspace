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
- Rapid2 v1 `.env`: `Builds\Rapid2\rapid2 (Program)\.env` (live Kraken + Telegram creds)
- Rapid2 v1.2 `.env`: `Builds\Rapid2\rapid2 v1.2\.env` (paper trading creds)
- AWS SSH key: `C:\Users\benja\OneDrive\Documents\KeePass\AWS\rapid2-key.pem`

## EC2 Servers
| Server | IP | SSH Alias | Service | Purpose |
|--------|-----|-----------|---------|---------|
| Rapid2 v1 (Production) | `3.131.96.193` | none (use full IP) | `openclaw` | Live trading — real money |
| Rapid2 v1.2 (Paper) | `3.138.144.246` | `rapid2` | `openclaw-paper` | Paper trading — dev/test |

## Available Skills (invoke with /skill-name)

**Session bookends:** `/catchup` · `/remember`
**Before coding:** `/spike` · `/think` · `/impact`
**After coding:** `/review` · `/decide` · `/deploy`
**Operations:** `/status` · `/rollback` · `/new-project` · `/hierarchical-claude-md`

## GitHub Repos
| Repo | URL | What's in it |
|------|-----|--------------|
| builds-workspace | https://github.com/benjaminwilsey-creator/builds-workspace | CLAUDE.md, all skills, memory backups, workspace config |
| openclaw-v1.2 | https://github.com/benjaminwilsey-creator/openclaw-v1.2 | Paper bot source code |
| openclaw-v1 | https://github.com/benjaminwilsey-creator/openclaw-v1 | Production bot source code |

Note: memory files are backed up to `Builds/memory/` in builds-workspace repo. Update both locations when memory changes.

## EC2 Monitoring
| Monitor | What it watches | Alert method |
|---------|----------------|--------------|
| Error alerter cron | Bot logs — errors/crashes (every 5 min) | Telegram |
| UptimeRobot | Server up/down (TCP port 22) | Email |
| CloudWatch | RAM > 85% on paper trading server | Email |

- Error alerter script: `/home/ubuntu/error_alert.sh`
- CloudWatch alarm name: `rapid2-memory-high` (paper server only)
