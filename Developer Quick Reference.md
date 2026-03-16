# Developer Quick Reference
*One-page cheat sheet — what to type and when*

---

## Every Session

| When | Command | What it does |
|------|---------|--------------|
| Start of session | `/catchup` | 60-second briefing — last session note, git state, open PRs, priorities |
| End of session | `/remember` | Saves memory + last session note + Build Log + pushes to GitHub |

**Never skip `/remember` at the end.** Without it, the next session starts cold.

---

## Context Hygiene

Context is the fuel Claude runs on. Let it get polluted and the quality of every response
drops — quietly, without warning. These habits keep it clean.

| When | Action | Why |
|------|--------|-----|
| Switching to a different topic | `/clear` | Wipes the slate — new topic, fresh context |
| Session feels sluggish or confused | `/clear` + restate the goal | Fixes context drift — Claude has lost the thread |
| Context indicator hits ~70% | `/compact` | Compresses history without losing the gist |
| Corrected Claude on the same thing twice | `/clear` + start with a sharper prompt | The context is polluted — keep correcting and it gets worse |

**Rule of thumb:** one session, one topic. If you're switching from debugging the bot to
planning a new feature, clear first.

---

## Before You Build

| Situation | Command | What it does |
|-----------|---------|--------------|
| Unfamiliar topic | `/spike` | Researches options, gives a recommendation, flags gotchas |
| Planning a feature | `/think` | 3 approaches with pros/cons — you approve before any code is written |
| Editing existing code | `/impact` | Shows what depends on it and what could break |

---

## After You Build

| When | Command | What it does |
|------|---------|--------------|
| Before every deploy | `/review` | Code quality + security check — returns Approved / Blocked |
| After a key decision | `/decide` | Saves a permanent record of what was decided and why |
| Ready to ship | `/deploy` | SCP to EC2 + git tag + restart + confirms healthy |

---

## Operations

| Situation | Command | What it does |
|-----------|---------|--------------|
| Check if bot is healthy | `/status` | Shows service status + recent logs + any errors |
| Deploy broke something | `/rollback` | Restores last known-good version |
| Starting a brand new project | `/new-project` | Scaffolds full project (git, CI, tests, rules) |
| Project rules need updating | `/hierarchical-claude-md` | Updates the CLAUDE.md for a project |

---

## The Standard Workflow

```
New session          ->  /catchup
Unfamiliar topic     ->  /spike
Planning anything    ->  /think
Editing existing     ->  /impact
Done coding          ->  /review
Ship it              ->  /deploy
Something broke      ->  /rollback
Made a key decision  ->  /decide
End of session       ->  /remember
```

---

## Quick Rules

1. Always `/think` before building — no surprises halfway through
2. Always `/review` before `/deploy` — never ship unreviewed code
3. Always `/remember` at end of session — never lose context
4. Any change touching real money -> confirm twice before proceeding
5. Corrected Claude twice on the same thing? `/clear` and start fresh

---

*Full guide: `Document 3 - The Development Agent Guide.md`*
