---
name: Autonomous agent system
description: Sub-agent task queue system built 2026-04-18 — tasks.md + /autonomous + Slack reporting
type: project
originSessionId: ea8f5ab0-e150-41ca-bfe5-04c2bff8464d
---
## What It Is
A system that lets Claude work through a task queue independently while Benjamin is away
(e.g. at his kids' sporting events). Tasks are defined in a file, an orchestrator picks
them up one at a time, delegates each to a fresh sub-agent, and reports results via Slack.

## How to Use It

1. Add tracks to the project's `tasks.md` using Lite Conductor format (see below)
2. Run `/autonomous` in Claude Code
3. Watch `#claude-agent` on Slack for updates
4. Send commands from Slack while away: `STOP`, `PAUSE`, `SKIP`, `STATUS`, `ADD: new task`
5. After each phase completes, reply "proceed" in Slack to advance to the next phase
6. When back — review the feature branches, merge what looks good

## Lite Conductor Track Format

```
## [TRACK-001] Task title
**Status:** planned | in-progress | done | blocked
**Spec:** What this does in one plain English sentence
**Acceptance:** Specific, measurable outcome that proves it's done
**Phase:** 1 of N

### Phase 1 — Description
- [ ] subtask
- [ ] subtask

### Phase 2 — Description
- [ ] subtask
```

**Rules:**
- Every track must have `Spec` + `Acceptance` — missing either → skipped and flagged
- `/autonomous` executes only the current phase, then stops and waits for "proceed"
- Track IDs appear in every git commit message: `[TRACK-001] phase 1: description`
- Branches named: `agent/track-001-phase1-YYYY-MM-DD`

## Architecture

```
/autonomous (orchestrator — stays lightweight)
    reads tasks.md → spawns sub-agent per task (isolation: worktree) → Slack report → next task

sub-agent (fresh 200K context per task)
    reads CLAUDE.md → reads relevant files → edits → commits → returns structured summary
```

Tasks run **sequentially** — each sub-agent completes before the next starts, because tasks
may depend on each other's file changes.

## Safety Rules (hardcoded into /autonomous)
- Never pushes to master — all work goes in `agent/[slug]-[date]` branches
- Never deploys to EC2 or runs the live bot
- Stops and Slacks Benjamin if it hits a blocker it can't resolve
- Checks #claude-agent for STOP/PAUSE commands between every task

## Global Skills Built
All saved to `C:/Users/benja/.claude/commands/` — available in every project:

| Skill | Purpose |
|---|---|
| `/autonomous` | Orchestrator — runs the task queue with sub-agents |
| `/remote-control` | Check #claude-agent Slack for mid-session commands |
| `/batch` | Apply one change across many files in parallel |
| `/debug` | Diagnose and fix a bug from an error or log |
| `/btw` | Answer a quick side question without disrupting the current task |
| `/doctor` | Health check on Claude Code install, config, MCP servers, env vars |

## Branch
Built on: `feature/autonomous-agent` (not yet merged to master)

## Slack Channel
All agent communication goes to `#claude-agent`
