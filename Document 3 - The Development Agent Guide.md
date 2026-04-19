# Document 3: The Development Agent Guide
**How to build software with Claude Code as your senior engineering partner**
*For new projects, starting from scratch*

---

## What Is This?

This is a vibe coding setup — you describe what you want to build in plain English, and Claude Code (your AI development agent) writes the code, manages the infrastructure, and handles the technical details on your behalf.

You do not need to be a programmer. Your job is to:
- Describe the goal clearly
- Review and approve plans before work starts
- Make decisions when options are presented
- Test and give feedback

Claude's job is everything else.

This guide covers how to start a new project, how to work session-by-session, and which commands to use and when.

---

## Prerequisites

Before starting a new project, you need:

1. **Claude Code installed** — the desktop app or CLI tool from Anthropic
2. **VS Code installed** — your code editor (free at code.visualstudio.com)
3. **Git installed** — for saving versions of your code (free at git-scm.com)
4. **A GitHub account** — for cloud backup of your code (free at github.com)
5. **This workspace open** — open `Builds.code-workspace` in VS Code

If any of these are missing, ask Claude to help you install them.

---

## Starting a New Project

### Step 1 — Open a session
Open Claude Code and make sure you are working in the `Builds` workspace folder.

### Step 2 — Run the research command (if the topic is unfamiliar)
```
/spike
```
Tell Claude what you want to build. It will research the best approach, compare your options, and give you a recommendation before any code is written.

**Example:** `/spike — I want to build a tool that converts YouTube videos to blog posts`

### Step 3 — Plan the project
```
/think
```
Once you know the approach, use this command to plan the build. Claude will present three ways to implement it, explain the tradeoffs, and give you a step-by-step checklist. You approve the plan before anything is built.

**You will be asked:** "Does this match what you had in mind? Say yes to proceed."
**Do not skip this step** — it prevents halfway-through surprises.

### Step 4 — Scaffold the project
```
/new-project
```
Claude will ask you five questions (name, language, what it does, where it deploys, whether it handles sensitive data), then automatically create the entire project folder with:
- A git repository (for version history)
- A `CLAUDE.md` file (project-specific rules for the AI)
- Testing infrastructure
- Code quality checks
- A CI pipeline (automated checks that run when you push to GitHub)
- Pre-commit safety hooks (scans for accidentally included passwords or API keys)

This takes about 2 minutes and gives you a production-ready foundation before writing a single line of real code.

---

## The Session Workflow

Every working session follows the same rhythm:

```
Start of session   →   /catchup
  (during session) →   /spike  /think  /impact  /review  /deploy
End of session     →   /remember
```

### Starting a session — /catchup
```
/catchup
```
Run this at the very start of every session. It reads the current state of your project and gives you a 60-second briefing:
- What's running and whether it's healthy
- What was last deployed
- Any errors since your last session
- Open items from last time

This replaces the "okay where were we..." conversation and gets you productive immediately.

### Ending a session — /remember
```
/remember
```
Run this at the very end of every session. It:
1. Reviews what happened and proposes what to save to memory
2. Generates a plain-English summary of the session and adds it to the Build Log
3. Automatically commits and pushes everything to GitHub

**Never close a session without running /remember.** Without it, the AI starts the next session cold and you lose context.

---

## The Full Skill Reference

### Before you write any code

**`/spike` — Research first**
Use this when you're about to build something in a domain you (or Claude) don't know well.
- Input: a topic or technology you want to explore
- Output: a comparison of your options, a recommendation, and the known pitfalls
- Example: `/spike — what's the best way to send automated emails from Python?`

**`/think` — Plan before building**
Use this before any meaningful piece of work.
- Input: what you want to build
- Output: three approaches with pros/cons, a recommendation, a risk list, and an ordered checklist
- You must approve the plan before any code is written
- Example: `/think — I want to add user login to the app`

**`/impact` — Check before changing existing code**
Use this whenever you want to change something that already exists and is working.
- Input: which file or function you want to change
- Output: a report showing everything that depends on it, what could break, and whether it's safe to proceed
- Think of it as: "before I move this wall, check if it's load-bearing"
- Example: `/impact — I want to change how the database connection is opened`

---

### After you write code

**`/review` — Quality check before shipping**
Use this after coding and before deploying.
- Checks the code against all quality rules
- Looks for security issues (hardcoded passwords, exposed credentials, etc.)
- Checks for logic errors and edge cases
- Returns one of three verdicts: Approved / Approved with notes / Blocked
- Example: run `/review` before every `/deploy`

**`/decide` — Record important decisions**
Use this after making any significant choice about how to build something.
- Input: what was decided and why
- Output: a permanent record file saved in the project folder
- This is invaluable 6 months later when you can't remember why something was built a certain way
- Example: `/decide — we chose to use Stripe instead of PayPal because of better developer documentation`

**`/deploy` — Ship to the server**
Use this when you're ready to push code to your live or staging server.
- Shows you exactly what will be deployed before it happens
- Tags the version in git (so you can roll back if needed)
- Restarts the service and confirms it's healthy before declaring success
- Warns you loudly if you're about to touch a production system with real users or real money

---

### Debugging and bulk edits

**`/debug [description]` — Fix a bug**
Use this when something is broken and you have an error message or log to share.
- Input: paste the error, describe what's wrong, or point to a log file
- Output: root cause in plain English, fix applied, instructions for how to verify it worked
- Claude reads the actual code before touching anything — it never guesses
- Example: `/debug — the bot crashed with "KeyError: order_id" when trying to sell`

**`/batch` — Apply one change to many files**
Use this when you need the same edit made in multiple places at once.
- Input: what to change and which files it applies to
- Output: Claude reads every file, makes all edits in parallel, produces a pass/fail report
- Safe: it lists the targets and confirms before touching anything
- Example: `/batch — rename the function get_price to fetch_price across all files in src/`

**`/btw [question]` — Quick side question**
Use this when you have a small question mid-task and don't want to interrupt the flow.
- Claude answers briefly (2–5 sentences) without losing track of what it was doing
- Example: `/btw what does "idempotent" mean in the context of API calls?`

---

### Autonomous development

**`/autonomous` — Work while you're away**
Use this to let Claude work through a task queue while you're away (at an event, in a meeting, etc.).
- Before you leave: add tasks to `tasks.md` under `## Pending` in plain English
- Start the agent with `/autonomous` — it picks up tasks one by one, each in a fresh sub-agent
- Each task gets its own git branch — work is isolated and safe to review
- When done: Slacks you on `#claude-agent` with what was built and which branch to review
- Safety rules: never pushes to master, never deploys to EC2, stops and asks if stuck

**`/remote-control` — Send commands while the agent is running**
Use this to redirect the agent mid-session without sitting at your computer.
- Send a message to `#claude-agent` on Slack from your phone
- Supported commands: `STOP`, `PAUSE`, `SKIP` (current task), `STATUS`, `ADD: new task`
- The agent checks for your commands between every task automatically

**`/doctor` — Diagnose Claude Code itself**
Use this if Claude Code is behaving unexpectedly or a command isn't working.
- Checks: version, config files, MCP servers, environment variables
- Returns a health report with specific items to fix
- Example: run `/doctor` if an MCP integration stops working

---

### Operations

**`/status` — Health check**
Use this any time you want to know if your running services are healthy.
- Shows whether each service is up or down
- Shows recent log output
- Highlights any errors
- Example: run `/status` if something seems wrong, or just to check in

**`/rollback` — Undo a bad deploy**
Use this if a deploy broke something.
- Finds the last known-good version using git tags
- Walks you through restoring it safely
- Does not delete the broken version — it stays available to fix
- Example: run `/rollback` immediately after `/deploy` if the service crashes

**`/new-project` — Start a new project**
Use this at the beginning of any new piece of work.
- Asks 5 questions about the project
- Creates the full folder structure, git repo, CI pipeline, and safety checks
- Adds the project to the workspace index

**`/hierarchical-claude-md` — Update project rules**
Use this when a project's rules or context need updating.
- Generates or updates the `CLAUDE.md` file for a specific project
- Ensures Claude has accurate context when working on that project

---

## Common Scenarios

### "I have an idea and want to start building"
1. `/spike` — research if the approach is sound
2. `/think` — agree on a plan
3. `/new-project` — scaffold the project
4. Start building (Claude writes the code, you review it)
5. `/review` — check before deploying
6. `/deploy` — ship it
7. `/remember` — end the session

### "I want to add a feature to something that already exists"
1. `/catchup` — get the current state
2. `/think` — plan the feature
3. `/impact` — check what the change affects
4. Build the feature
5. `/review` — check before deploying
6. `/deploy` — ship it
7. `/remember` — end the session

### "Something is broken"
1. `/status` — see what's wrong
2. If it broke after a recent deploy: `/rollback`
3. If it's a bug: `/think` to plan the fix, then build and `/deploy`
4. `/remember` — record what happened

### "I'm not sure how to approach something"
1. `/spike` — let Claude research it first
2. Discuss the recommendation
3. `/think` — agree on the plan
4. Proceed from there

### "I want Claude to build while I'm away"
1. `/catchup` — make sure the project state is clean
2. Add tasks to `tasks.md` under `## Pending` — plain English, one task per line
3. `/autonomous` — starts the agent; it will Slack you when each task is done
4. From your phone: send `STATUS` to `#claude-agent` to check progress, `STOP` to halt
5. When back: review the branches it created, merge what looks good

### "Something is broken and I have an error"
1. Copy the error message or log
2. `/debug` — paste the error and describe what you were doing
3. Claude finds the root cause and fixes it — tells you how to verify the fix

### "I haven't worked on this in a while"
1. `/catchup` — catch up on current state
2. Read the Build Log (`Build Log.md` in the Builds folder) for history
3. Check `docs/decisions/` in the project folder for past decisions
4. Proceed as normal

---

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| Build Log | `Builds/Build Log.md` | Plain-English history of every session |
| Global rules | `Builds/CLAUDE.md` | Rules that apply to all projects |
| Project rules | `[Project]/CLAUDE.md` | Rules specific to one project |
| Decision records | `[Project]/docs/decisions/` | Permanent record of key decisions |
| Memory files | `Builds/memory/` | AI context that carries between sessions |
| Skills (global) | `~/.claude/commands/` | All /command skill files — available in every project |
| Workspace file | `Builds/Builds.code-workspace` | Open all projects in VS Code at once |

---

## Safety Rules

These apply to every project, always:

1. **Never commit a `.env` file** — this is where passwords and API keys live. It must never be uploaded to GitHub. The `.gitignore` file prevents this automatically, but be aware.

2. **Always run `/think` before building** — starting without a plan wastes time and creates work to undo.

3. **Always run `/review` before `/deploy`** — deploying unreviewed code to a live system is the most common source of breakage.

4. **Always run `/remember` at the end of a session** — without it, the next session starts cold.

5. **If something touches real users or real money, confirm twice** — Claude will warn you when this is the case. Take the warning seriously.

---

## Backup and Recovery

All code is automatically backed up to GitHub:
- **Workspace config, skills, and memory:** `github.com/benjaminwilsey-creator/builds-workspace`
- **Project code:** each project gets its own private GitHub repo (created by `/new-project`)

If your computer is lost or reset:
1. Install Git, VS Code, and Claude Code
2. Clone `builds-workspace` from GitHub
3. Clone each project repo from GitHub
4. Open `Builds.code-workspace` in VS Code
5. You are back exactly where you left off

---

*This document is part of the Builds workspace documentation series.*
*Document 1: The Build Manual — Document 2: The Operations Manual — Document 3: This guide*
