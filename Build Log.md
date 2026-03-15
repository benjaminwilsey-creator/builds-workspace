# Builds — Session Log
*Most recent session at the top. Plain English reference for what has been built and why.*
---
## Session: 15 March 2026
**Projects touched:** Booksmut (ReelForge)
**Session type:** Planning / Phase 0 completion

### What was built or changed
- Committed all Phase 0 infrastructure setup guides to the Booksmut repo (Cloudflare R2, domain, AWS→GCP steps, Gmail OAuth, Supabase keepalive workflow)
- Caught and blocked a Google credentials file from being committed — added patterns to .gitignore
- Recorded that the backend was switched from AWS (Lambda + SQS) to Google Cloud (Functions + Pub/Sub + Cloud Scheduler) set up via gcloud CLI — consolidating on one cloud provider since GCP was already required for TTS, Vision, and Gemini
- Workspace permanently moved from OneDrive to E:\Builds - Copy — updated all memory references

### Current state
| | Status |
|---|---|
| Booksmut | Phase 0 nearly complete — 10 of 12 items done |
| Remaining Phase 0 | Music library seed + Google app verification |
| Phase 1 | Not started — waiting on Phase 0 completion |
| Rapid2 production bot | Active — live trading on Kraken (unchanged) |

### Decisions made this session
- Switched from AWS to Google Cloud for all backend infrastructure (ADR 0004) — one cloud provider instead of two
- Reddit API dropped for this build — API access process changed, no replacement in v1

### Outstanding / next steps
- Confirm Google app verification submitted (1–4 week wait, blocks Phase 6 Gmail outreach)
- Seed music library with 20+ tracks
- Begin Phase 1 (Supabase schema) once above are done

---
## Session: 11 March 2026
**Projects touched:** Rapid2 (OpenClaw v1.2)
**Session type:** Strategy overhaul — feature build

### What was built or changed
- Flipped the allocation pyramid: most capital now sits in the safest tier (50% stable / 30% mid-cap / 20% micro-cap), instead of the riskiest (was 15/35/50). This means a bad run on volatile coins can no longer wipe out the majority of the account.
- Added RSI as a 5th entry signal — confirms a coin's price is actually moving up, not just being talked about. Requires at least 3 out of 5 signals to enter a T3 trade (was 2 out of 4).
- Replaced the fixed 25% trailing stop with ATR-based stops — each coin's stop is now sized to its own historical volatility. Calm coins get tighter stops; volatile coins get more room to breathe. Falls back to a fixed 15% stop if the coin is too new to have enough price history.
- Tightened social signal thresholds (4x more Reddit activity required) to filter out noise.
- Reduced T3 to a maximum of 3 open positions (was 6) — forces the bot to be pickier, concentrating on higher-conviction bets.
- Reduced position sizes to $3.60/$5/$8 (was $4/$7/$12).
- Updated project CLAUDE.md and memory files to reflect all of the above.

### Current state
| | Status |
|---|---|
| Production bot (Rapid2 v1.2) | Active — live trading on Kraken |
| T3 positions | ~10 open (above new 3-position cap — will drain naturally, no force-sell) |
| Last deploy | 11 March 2026 — commit 11957e0 |

### Decisions made this session
- Let existing over-cap T3 positions exit naturally via their ATR stops rather than force-selling — avoids locking in losses or triggering tax events unnecessarily
- Option B (RSI + ATR, keep momentum strategy for T3) chosen over Option C (mean reversion rewrite) — mean reversion is a bigger conceptual change that needs its own backtesting period before going live

### Outstanding / next steps
- Monitor in logs: T3 cap message "Position cap reached (10/3)" should gradually reduce as positions close out
- Cleanup items (non-blocking): refactor scan_and_enter() into smaller functions, add logging to 4 bare except:pass blocks, move magic numbers to CONFIG
- If T3 entries dry up completely (RSI + stricter thresholds may be too tight together), relax RSI threshold from 60 → 55
---
## Session: 7 March 2026 (late evening)
**Projects touched:** 3DPrint concept (new, unnamed)
**Session type:** Concept exploration — domain research and architecture thinking

### What was built or changed
- Explored a new project idea: a tool that lets Ricky describe a 3D shape in plain conversational English and receive a clean, printable STL file for his Bambu A1 printer
- Identified the core problem with existing AI + 3D printing approaches: AI-generated CAD code bloats quickly and produces messy, over-complicated geometry that is hard to print and hard to modify
- Proposed a better architecture: skip code generation entirely and build the 3D geometry directly in Python, producing a clean STL with no intermediate code layer

### Current state
| | Status |
|---|---|
| 3DPrint project | Concept only — not scaffolded |
| Sportsball | Scaffolded, architecture planned, not yet built |
| Paper bot (Rapid2) | Active — 11 open positions |
| Production bot | TERMINATED |

### Decisions made this session
- Direct mesh generation (trimesh/numpy-stl) preferred over OpenSCAD/CadQuery code generation — eliminates AI code bloat at the source

### Outstanding / next steps
- Answer 3 open questions before scaffolding: (1) standalone objects or multi-part? (2) preview image before STL? (3) personal use or product for others?
- Confirm project name, then scaffold and run /think
---
## Session: 7 March 2026 (evening)
**Projects touched:** Sportsball (new)
**Session type:** New project kickoff — business strategy + architecture planning

### What was built or changed
- Created the Sportsball project — a new college football content pipeline designed to grow Ricky's brand to $150k+/year
- Scaffolded the full project folder with Python toolchain: linter, test runner, CI pipeline, secret detection, VS Code config
- Researched the college football creator economy — confirmed that YouTube + paid newsletter + sportsbook affiliates is the right three-layer revenue model
- Mapped Ricky's content angle: college football, focusing on fantasy analysis, scheme breakdowns, statistics, and transfer portal/current events
- Planned the pipeline architecture: a four-stage system (Fetch news → Generate drafts with AI → Ricky reviews → Publish) with a local web UI for review and SQLite to track draft status

### Current state
| | Status |
|---|---|
| Sportsball | Scaffolded — architecture planned, no code written yet |
| Paper bot (Rapid2) | Active — 11 open positions, $42 cash |
| Production bot | TERMINATED |
| Last deploy | N/A this session |

### Decisions made this session
- Revenue model: YouTube builds the audience, paid newsletter (Substack/Beehiiv) is the primary income, sportsbook affiliate links layer on top once audience is established
- Pipeline approach: human-in-the-loop is non-negotiable — Ricky approves every piece before it publishes; AI assists, it doesn't author

### Outstanding / next steps
- Confirm how Ricky wants to review content (local web page proposed, alternatives: email, Telegram)
- Confirm publishing method (Twitter auto-post assumed; Substack copy-paste assumed)
- Confirm college football data source (ESPN unofficial API is candidate)
- Get /think sign-off, then build Phase 1 (the news fetcher)
---
## Session: 7 March 2026 (afternoon)
**Projects touched:** .qwen/ folder (new), qwen-developer-setup repo
**Session type:** Qwen Code workflow adaptation

### What was built or changed
- Created `.qwen/` folder — complete Qwen Code developer workflow system (separate from Claude Code skills)
- Created qwen-developer-setup GitHub repo — https://github.com/benjaminwilsey-creator/qwen-developer-setup
- Consolidated 11 Claude skill files into single `Workflow.md` — optimized for Qwen's execution pattern
- Wrote Qwen Optimization Guide — 10 quality rules specific to Qwen (explicit steps, confirmation gates, format enforcement, etc.)
- Adapted Developer Quick Reference — decision tree, session types, expected outputs, anti-patterns, troubleshooting
- Created booksmut/ mirror — ReelForge project docs with ADRs and technical guide
- Removed skills/ folder — consolidated into Workflow.md (11 files → 1 file)
- Updated QWEN.md — workflow summary table, workflow rules, quality constraints

### Current state
| | Status |
|---|---|
| Claude Code workflow | Active — Architect/ skills in builds-workspace |
| Qwen Code workflow | Active — .qwen/ folder, separate repo |
| Booksmut/ReelForge | Design complete, Phase 0 ready |
| Rapid2 v1.2 | Production bot running on EC2 |

### Decisions made this session
- Qwen workflow optimized for Qwen's strengths — explicit numbered steps, consolidated references, no slash commands
- Skills consolidated into Workflow.md — less file hopping, faster context loading for Qwen
- Separate GitHub repo for qwen-developer-setup — clean separation from Claude Code workspace

### Outstanding / next steps
- None — Qwen workflow complete and pushed to GitHub
---
## Session: 7 March 2026
**Projects touched:** Root workspace config, memory files
**Session type:** Workspace refocus — developer tools only

### What was built or changed
- Refocused the workspace on **developer workflow and skills** — removed trading bot-specific content from global config files
- Updated root CLAUDE.md — removed "live trading credentials" warnings, changed communication style to reference "production systems" generically, reordered project index (Architect first, Rapid2 archived)
- Updated Developer Quick Reference — changed "bot is healthy" to "service is healthy", "real money" to "production systems"
- Updated MEMORY.md — changed project ordering (Architect primary, Rapid2 archived reference)

### Current state
| | Status |
|---|---|
| Workspace focus | Developer workflow system (Architect skills) |
| Rapid2 trading bot | Archived — reference only, not actively developed |
| Booksmut/ReelForge | Design complete, Phase 0 ready |

### Decisions made this session
- Workspace is now **developer-first** — the skills system (/catchup, /think, /review, /deploy, etc.) is the primary tool, not the trading bot
- Rapid2 remains in the workspace as archived reference — useful for deployment patterns and skill examples
- Future development sessions will use the developer workflow for any new projects

### Outstanding / next steps
- None — clean slate for new development work
---
## Session: 6 March 2026 (late evening)
**Projects touched:** Architect (skills), Root workspace config, Rapid2 v1.2 (bot.py)
**Session type:** Developer agent optimization (Sonnet 4.6)

### What was built or changed
- Analyzed the full developer agent workflow against Claude Sonnet 4.6's strengths and weaknesses -- identified 8 improvements
- Removed dead references to the retired v1 server from /status and /decide skills -- prevents wasted SSH timeouts
- Converted /status and /impact skills to the sub-agent pattern -- SSH output and grep results now stay isolated from the main conversation
- Added "Behaviour Guardrails" section to root CLAUDE.md -- 5 rules that prevent Sonnet from adding unsolicited improvements or refactoring working code
- Added DO NOT SKIP / REQUIRED emphasis markers to critical steps in /think, /review, /deploy, and /rollback -- prevents Sonnet from skipping confirmation steps
- Refactored bot.py -- split two oversized functions (scan_and_enter at 95 lines, load_existing_positions at 50 lines) into focused helpers under 40 lines each
- Fixed a bug in all 5 sub-agent skills -- they used the wrong Agent tool parameter (subagent_type="general" instead of "general-purpose"), which caused every sub-agent spawn to fail on first try
- Identified 4 strategic improvements for future sessions: /test skill, S3 state backup, watchlist config file, /performance skill -- saved to memory backlog

### Current state
| | Status |
|---|---|
| Paper bot | active, 11 open positions (3 T2 + 8 T3), ~$120 total, $42 cash |
| Production bot | same server -- v1.2 is the live bot |
| Last deploy | none this session (bot.py refactored but not yet deployed) |

### Decisions made this session
- Sonnet 4.6 guardrails added to CLAUDE.md -- explicit "don't" rules prevent over-helping
- All context-heavy skills now use sub-agent pattern (5 of 13 total)
- bot.py refactor reviewed and approved but NOT deployed -- deploy next session after fresh /review

### Outstanding / next steps
- Deploy bot.py refactor to EC2 (reviewed, approved, syntax verified -- just needs /deploy)
- Four planned improvements saved to memory backlog: /test, S3 backup, watchlist config, /performance

---
## Session: 6 March 2026 (evening)
**Projects touched:** Architect (skills), Root workspace config
**Session type:** Developer agent optimization

### What was built or changed
- Analyzed the full developer agent workflow against 2026 community best practices (HumanLayer, Morph, awesome-claude-code) and identified 7 improvements
- Converted 3 skills to sub-agent pattern — /review, /catchup, and /spike now run in isolated contexts so raw data (code files, SSH logs, web search results) never enters the main session
- Trimmed root CLAUDE.md from 120 lines to 75 — removed deployment details and skills tables that duplicated other files
- Cleaned the /deploy skill — removed all references to the retired v1 server (terminated 2026-03-04)
- Added Context Hygiene section to the Developer Quick Reference — /clear, /compact, two-correction rule
- Created .claudeignore at workspace root — prevents Claude from accidentally loading state/, .venv/, .env, .pem, and other junk into context
- Updated MEMORY.md — added sub-agent pattern docs, context hygiene notes, Write tool gotcha

### Current state
| | Status |
|---|---|
| Paper bot | active, 11 open positions (3 T2 + 8 T3), ~$120 total, $42 cash |
| Production bot | same server — v1.2 is the live bot |
| Last deploy | none this session (config-only changes) |

### Decisions made this session
- Sub-agent pattern adopted for context-heavy skills (/review, /catchup, /spike) — keeps main session clean
- Root CLAUDE.md trimmed to <100 lines — deployment details belong in project CLAUDE.md and skill files, not the root
- .claudeignore added as a standard part of the workspace setup

### Outstanding / next steps
- None — clean slate

## Session: 6 March 2026
**Projects touched:** Rapid2 v1.2 (production)
**Session type:** Bug fix + Strategy tuning

### What was built or changed
- Found and killed a ghost: the old v1 bot code was still running on the v1.2 server alongside the live bot, and both were fighting over the same Telegram connection — causing constant errors every 30 seconds. Stopped and permanently disabled it.
- Added a per-coin concentration cap: the bot now checks your actual Kraken balance before buying any Tier 2 coin — if you already hold more than 20% of your account in that coin (even if the bot lost track of it), the buy is blocked. This directly fixed the HBAR loop where the bot kept failing to buy more HBAR it didn't know you already held.
- Blocked consolidation from feeding an over-concentrated coin: the bot will no longer sell your other holdings to fund a coin you already hold too much of, even if the signal is strong.
- Reduced position sizes from $5/$10/$18 to $4/$7/$12 — the old sizing meant a single high-confidence trade could consume 15% of the account; the new sizing caps any single trade at ~10%, leaving room for 6–8 simultaneous positions.
- Fixed a crash in the /portfolio Telegram command — if Kraken was briefly unreachable, the command would silently fail; it now returns a friendly error message instead.
- Fixed repeated ETH error noise — the bot holds a tiny dust ETH position worth fractions of a cent that it kept trying and failing to sell every 5 minutes. It now detects positions too small to sell and skips them gracefully.

### Current state
| | Status |
|---|---|
| Production bot (v1.2) | Active — $116.54 account, 14 positions loaded |
| Last deploy | 6 March 2026 (tag: deploy-2026-03-06-0339) |

### Decisions made this session
- Concentration cap checks live Kraken balance rather than just bot-tracked positions — this catches coins the bot holds but lost track of (e.g. after a restart where position loading silently failed for one coin).
- Position sizing reduced to match a ~10% max single-trade rule — leaves more room for diversification and avoids single coins dominating the portfolio.

### Outstanding / next steps
- Elastic IP 3.131.96.193 may still exist in AWS unattached — worth releasing to avoid charges
- HBAR at $0.10 is classified as Tier 3 (not Tier 2) because of its low price — it is now managed by the trailing stop, not the Tier 2 take-profit/stop-loss rules
- Service still named openclaw-paper.service despite running live trading — low priority rename
---
## Session: 5 March 2026
**Projects touched:** Rapid2 v1.2 (now production), Rapid2 v1 (retired)
**Session type:** Infrastructure emergency + Feature swap + Production deploy

### What was built or changed
- Discovered the production v1 EC2 server was terminated (not just stopped) — the instance is permanently gone, but the Elastic IP and the unmanaged LINK/USD position it bought at 4:59am survived.
- Replaced the paid LunarCrush social signal ($72/month) with CryptoCompare (free tier) — the bot now checks a coin's Reddit activity (posts per hour and active users) using CryptoCompare's API instead. Added a smart cache so the full coin list is only fetched once per bot restart.
- Raised the Tier 3 entry requirement from 1 signal to 2 — CoinGecko trending alone was enough to trigger a buy, which was never the intent since trending is used both as a pre-filter and as a signal.
- Fixed a missing load call in bot.py — the live bot was silently reading placeholder values instead of the real credentials because systemd does not pass shell environment variables to services. Bot would start but immediately fail to connect.
- Promoted v1.2 bot from paper trading to live production on the existing paper server (3.138.144.246) — updated the systemd service to run bot.py instead of paper_bot.py.
- Resolved Kraken API IP whitelist block — the API key was whitelisted to the old (now-dead) server IP; updated in Kraken dashboard to allow the paper server's IP.

### Current state
| | Status |
|---|---|
| Production bot (v1.2) | Active on 3.138.144.246 — $119.99 account, 14 positions loaded, scheduler running |
| Paper bot | Inactive (paper_bot.py still on server but service now runs bot.py) |
| Last deploy | 5 March 2026 (tag: deploy-2026-03-05-0038) |

### Decisions made this session
- Chose CryptoCompare over other LunarCrush alternatives — free tier with email registration, 100k calls/month, covers Reddit social stats which is the most useful signal layer.
- Promoted v1.2 directly to production rather than spinning up a new EC2 instance — the paper server is already configured, monitored, and has all credentials in place.

### Outstanding / next steps
- Service is still named openclaw-paper.service even though it now runs live trading — low priority rename
- Elastic IP 3.131.96.193 may still exist in AWS but is unattached — worth releasing to avoid charges
- Entry prices for all 14 loaded positions are set to current market price, not actual cost basis — P&L tracking starts from the restart date only
---
## Session: 4 March 2026
**Projects touched:** Rapid2 v1.2 (paper bot)
**Session type:** Bug investigation, Feature build

### What was built or changed
- Investigated why no trades had fired in 2+ days — discovered signals WERE firing (DOGE repeatedly) but the bot was silently skipping buys because the T2 tier's allocation cap was almost full ($3.62 headroom vs $18 minimum trade size). Added a log line so the bot now explains why it skipped, e.g. "cap full (need $18.00, have $3.62)".
- Expanded T3 micro-cap watchlist from 10 coins to 29, adding PENGU, FARTCOIN, POPCAT, PNUT, MOODENG, GOAT, GIGA, and others confirmed available on Kraken. Removed BABYDOGE which was never listed on Kraken.
- Replaced the entire static T3 watchlist with dynamic Kraken discovery: the bot now fetches all Kraken USD pairs in one bulk call once per hour, filters to the T3 price range automatically, and scans every qualifying coin — so no coin on Kraken can ever be missed due to a gap in a hand-maintained list. Added a CoinGecko trending pre-filter to keep API costs low.

### Current state
| | Status |
|---|---|
| Paper bot | Active — 6 positions open, ~$67 cash remaining |
| Production bot | Unreachable via SSH (likely stopped in AWS console) |
| Last deploy | 4 March 2026 (paper bot only) |

### Decisions made this session
- Dynamic T3 discovery preferred over maintaining a static watchlist — one bulk API call per hour gives complete Kraken coverage at lower cost than many individual fetches per scan cycle.
- CoinGecko trending used as a pre-filter before running expensive Reddit and volume checks — acceptable tradeoff since coins with real momentum almost always appear on CoinGecko trending first.

### Outstanding / next steps
- Production v1 EC2 unreachable — worth checking AWS console to confirm instance state
- `TIER3_PRICE_MIN` not enforced in strategy code — minor bug to fix
- Telegram bot token leaking into systemd logs via httpx debug URLs — low risk, worth cleaning up

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