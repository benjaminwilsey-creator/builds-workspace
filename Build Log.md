# Builds — Session Log
*Most recent session at the top. Plain English reference for what has been built and why.*

---
## Session: 1 March 2026 (continued)
**Projects touched:** Rapid2 v1.2 infrastructure, Builds Workspace docs
**Session type:** Monitoring, Documentation

### What was built or changed

**CloudWatch memory alarm (Rapid2 v1.2 — paper trading server)**
- Installed the CloudWatch agent on the EC2 server — this is a small background process that collects memory usage and sends it to AWS every 60 seconds. AWS does not collect RAM stats by default, so this step was required.
- Added `CloudWatchAgentServerPolicy` to the EC2 IAM role — the agent needs permission to write data to CloudWatch. Fixed a "no metrics found" error caused by this missing permission.
- Created a CloudWatch alarm: `rapid2-memory-high` — triggers an email alert if RAM usage exceeds 85% (about 870MB on the 1GB server).

**Documentation**
- Created `Developer Quick Reference.md` — a one-page cheat sheet of all Claude Code commands and when to use them.

### Current state
| | Status |
|---|---|
| Paper bot (v1.2) | Active — paper trading running |
| Production bot (v1) | Active — live trading on Kraken |
| LunarCrush signal | Off — requires Individual plan (~$19/mo) |
| S3 backup | Live and verified |
| EC2 error alerting | Live — cron every 5 min, Telegrams on error |
| UptimeRobot | TCP port 22 monitor — showing UP |
| CloudWatch RAM alarm | Live — alerts above 85% RAM usage |
| GitHub backup | All 3 repos up to date |

### Outstanding / next steps
- LunarCrush Individual plan — optional upgrade at ~$19/mo to activate the 4th signal
- Booksmut (ReelForge) — still in design/docs phase, no code yet. Stack decision needed before development starts.

---
## Session: 1 March 2026
**Projects touched:** Rapid2 v1.2, Builds Workspace (all projects)
**Session type:** Infrastructure, Tooling, Developer Workflow

### What was built or changed

**Trading bot improvements (Rapid2 v1.2)**
- Added automatic S3 cloud backup — every time the paper bot makes a trade, it saves its portfolio state to Amazon S3. If the server ever crashes or restarts, nothing is lost.
- Wired up the LunarCrush social signal — the API key is now read from the environment file instead of being hardcoded. The signal quietly stays off if no key is present, so the bot never crashes because of a missing credential.
- Confirmed the Reddit signal is working without any login or API key (uses Reddit's public data feed).

**Infrastructure**
- Attached an IAM role (open1-ec2-s3) to the EC2 server — this is what gives the server permission to write to Amazon S3 without needing to store AWS credentials on the machine.
- Verified S3 backup is live: portfolio state file is confirmed at s3://open-state-yourname/paper_state.json.
- Set up an error alerter on the EC2 server — a background task checks the bot logs every 5 minutes and sends a Telegram message if it finds any errors or if the bot goes offline.
- Set up UptimeRobot monitoring — corrected from HTTP to TCP port 22 (SSH) monitoring, which correctly shows the server as up or down.

**Developer workspace (skills and workflow)**
- Built 13 Claude skills that can be triggered with a /command — covering the full lifecycle from research → planning → coding → review → deploy → recovery → memory.
- Full skill list: /catchup, /remember, /spike, /think, /impact, /review, /decide, /deploy, /status, /rollback, /new-project, /hierarchical-claude-md, /hierarchical-md
- Added a Makefile to Rapid2 v1.2 — common commands (test, lint, deploy, logs) are now one word instead of long terminal commands.
- Added a Pull Request template to GitHub — every PR now shows a checklist that must be completed before merging.
- Set up a VSCode workspace file (Builds.code-workspace) — opens all projects in one window with a shared sidebar.
- Backed up the entire workspace to GitHub (private repo: builds-workspace) including all skill files, CLAUDE.md, and memory files.
- Configured /remember to automatically commit and push memory files to GitHub at the end of every session.

**Permissions and settings**
- Simplified the Claude Code permission settings — replaced a long list of specific approved commands with broad wildcards (ssh, scp, git, pip, pytest, ruff) so common operations no longer require manual approval every time.
- Updated the root CLAUDE.md with correct EC2 IPs, both project versions, all deployment commands, and the full skill reference table.

### Current state
| | Status |
|---|---|
| Paper bot (v1.2) | Active — LINK/USD position open, ~$102 cash |
| Production bot (v1) | Active — live trading on Kraken |
| LunarCrush signal | Off — requires Individual plan (~$19/mo) to activate |
| S3 backup | Live and verified |
| EC2 error alerting | Live — cron every 5 min, Telegrams on error |
| UptimeRobot | TCP port 22 monitor — showing UP |
| GitHub backup | All 3 repos up to date |

### Decisions made this session
- Chose TCP port 22 (SSH) for UptimeRobot monitoring instead of HTTP — the server runs a trading bot, not a website, so HTTP port 80/443 is never open and always showed as down.
- Chose S3 + IAM role over storing AWS credentials in the .env file — the IAM role grants permissions automatically without any secrets on disk.
- Kept the Reddit signal on the public JSON API (no credentials) rather than migrating to the praw library — it works without auth and avoids adding another credential to manage. The trade-off is it could break if Reddit changes their API, but that's acceptable for paper trading.
- LunarCrush signal implemented to fail gracefully (returns False silently) when no API key is set, rather than throwing an error — the bot can run on 3 signals without issue.

### Outstanding / next steps
- CloudWatch memory alarm on EC2 — needs 3 minutes in the AWS console to set up a low-memory alert (server has 1GB RAM). Steps: CloudWatch → Create Alarm → EC2 → mem_used_percent → alert above 85%.
- LunarCrush Individual plan — optional upgrade at ~$19/mo to activate the 4th signal.
- Booksmut (ReelForge) — still in design/docs phase, no code yet. Stack decision needed before development starts.

---
