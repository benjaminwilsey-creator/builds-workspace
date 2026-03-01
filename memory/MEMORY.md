# Memory

## Project Overview
Three projects in `c:\Users\benja\OneDrive\Documents\Builds`:

1. **Rapid2** — Production crypto trading bot (OpenClaw) — primary active project
2. **Booksmut** — ReelForge video tool (design/docs phase only, no code yet)
3. **Architect** — Claude skill files for markdown hierarchy processing

See [rapid2.md](rapid2.md) for full Rapid2 details.

## User Preferences
- Platform: Windows with MSYS bash
- IDE: VS Code
- Deployment: AWS EC2 (scp push + systemd restart)
- Communication: plain English, no jargon, explain the "why"

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

## EC2 Monitoring
- Error alerter cron: runs every 5 min on rapid2, Telegrams on ERROR/CRITICAL or service down
- Script path: `/home/ubuntu/error_alert.sh`
