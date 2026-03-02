# Builds — Session Log
*Most recent session at the top. Plain English reference for what has been built and why.*

---
## Session: 2 March 2026 (afternoon)
**Projects touched:** Builds workspace, Booksmut (ReelForge)
**Session type:** Housekeeping, Research

Looked up the Claude Code Remote Control feature (`/rc`) — a recently added capability that lets you share a running Claude Code session to a phone or browser via a URL and QR code. Added `/rc` to the Session skills table in CLAUDE.md and to the memory files so it's visible every session. Also generated a plain-English to-do list for the ReelForge partner drawn from the project documentation.

---
## Session: 2 March 2026
**Projects touched:** Booksmut (ReelForge)
**Session type:** Documentation

Confirmed the top 3 BookTok romance/romantasy authors for the AI creative partner widget — Sarah J. Maas, Rebecca Yarros, Colleen Hoover. Recorded in ADR 0002, Technical Guide v2 Phase 6, and memory. This was the last outstanding content decision. The only remaining blockers before Phase 0 are account setup tasks: Meta accounts, Amazon Associates, and Google app verification for Gmail OAuth.

---
## Session: 1 March 2026 (afternoon — outreach automation)
**Projects touched:** Booksmut (ReelForge)
**Session type:** Feature design, Documentation

### What was built or changed
- Generated a FigJam pipeline diagram of the full ReelForge workflow — a visual overview the partner can use to understand the entire process end-to-end.
- Designed the publisher outreach automation system from scratch: instead of the partner manually finding a publisher's contact email and writing every email by hand, the system now does both. Gemini finds the contact email and writes a personalised draft; the draft is pushed directly to the partner's Gmail inbox; she reviews it and clicks Send herself. The human-in-the-loop is preserved — the system does the research and writing, the partner makes the final call.
- Built in a safety gate for the contact-finding step: the system logs whether each email address it finds is correct. Once it has been right 98% of the time across 50 confirmed attempts, it stops asking for confirmation and runs fully automatically. This prevents automating the step before it's proven reliable.
- Added prompt A/B testing to the outreach design — the system tracks which version of the email template gets replies, so over time the better-performing version becomes the default.
- Updated the Technical Guide v2 with all new schema: three new database tables/fields covering outreach tracking, contact discovery logging, and prompt version tracking. Added Gmail OAuth setup instructions to Phase 0 and the full outreach build plan to Phase 6.
- Wrote ADR 0003 — the permanent decision record for why semi-automated outreach was chosen over fully manual or fully automated alternatives.

### Current state
| | Status |
|---|---|
| Paper bot (v1.2) | Active — 4 open positions |
| Production bot (v1) | Unreachable — EC2 did not respond (non-urgent) |
| Booksmut / ReelForge | Design complete — all architectural decisions locked, Technical Guide v2 final, 3 ADRs written |

### Decisions made this session
- Publisher outreach will be semi-automated: Gemini drafts, Gmail API delivers to inbox, partner sends (ADR 0003)
- Contact discovery accuracy-gated: confirmation required until ≥98% accuracy over 50 runs, then fully automated
- Schema future-proofed for Option C (auto-detect sends from Gmail Sent folder) at zero extra build cost

### Outstanding / next steps
- Apply for Google app verification in Phase 0 — Gmail OAuth requires Google approval, takes 1–4 weeks
- Agree on "top 3 BookTok romance/romantasy authors" before Phase 6 (AI creative partner system prompt)
- Confirm Meta accounts are set up before Phase 0 begins
- Apply for Amazon Associates early (180-day qualifying sales clock)

---
## Session: 1 March 2026 (evening)
**Projects touched:** Booksmut (ReelForge)
**Session type:** Design review, Pre-build spike, Documentation

### What was built or changed
- Conducted a full pre-build assessment of the ReelForge project — read all three design documents (Partner Guide, Technical Guide, UI Framework Review) and ran a spike to find risks and gaps before a single line of code is written.
- Found and corrected 4 errors in the Technical Guide: Open Library was incorrectly labelled a "cleared" cover source (it isn't — publishers own those copyrights); the discovery scheduler was mislabelled as SQS (it should be AWS EventBridge); music tracks were listed as CC-BY compatible (they can't be — attribution is required); and the video composer's disk space wasn't configured (Lambda defaults to 512MB, needs 2GB for HD video rendering).
- Created a corrected v2 of the Technical Guide — both as a Markdown file (the editable master copy) and as a Word document using the python-docx library that was installed this session.
- Read and recorded the partner's UI framework selection: she chose Framework B (a dashboard overview with a one-click Focus Mode). Her answers also revealed she wants an AI creative writing assistant built into the tool — something that writes in the style of the top BookTok romance authors. This was added to the plan.
- Wrote two permanent decision records (ADRs) locking in: the Framework B UI selection (with mini progress checklists borrowed from Framework C), and the AI creative partner feature as a Phase 6 addition.

### Current state
| | Status |
|---|---|
| Paper bot (v1.2) | Active — 4 open positions (LINK, ONDO, PEPE, ADA), ~$120 portfolio, break-even |
| Production bot (v1) | Unreachable — EC2 at 3.131.96.193 did not respond during catchup |
| Booksmut / ReelForge | Design complete — Technical Guide v2 written, ADRs recorded, Phase 0 ready |

### Decisions made this session
- Publisher Licenses screen will use Framework B (dashboard + focus mode toggle + mini-checklists per publisher card)
- AI creative partner chat widget added to Phase 6 — Gemini-powered, styled after top 3 BookTok romance authors (authors to be agreed before Phase 6 build)

### Outstanding / next steps
- Production bot EC2 unreachable — check whether the instance is stopped (not urgent if not actively trading)
- Agree on "top 3 BookTok romance/romantasy authors" for the AI agent system prompt — needed before Phase 6
- Confirm Meta accounts (Facebook Page + Instagram Business) are set up before Phase 0 begins
- Apply for Amazon Associates account early — needs 3 qualifying sales within 180 days of application

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
