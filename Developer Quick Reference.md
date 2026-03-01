# Developer Quick Reference
*One-page cheat sheet — what to type and when*

---

## Every Session

| When | Command | What it does |
|------|---------|--------------|
| Start of session | `/catchup` | 60-second briefing — bot state, errors, open items |
| End of session | `/remember` | Saves memory + writes to Build Log + pushes to GitHub |

**Never skip `/remember` at the end.** Without it, the next session starts cold.

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
New session          →  /catchup
Unfamiliar topic     →  /spike
Planning anything    →  /think
Editing existing     →  /impact
Done coding          →  /review
Ship it              →  /deploy
Something broke      →  /rollback
Made a key decision  →  /decide
End of session       →  /remember
```

---

## Quick Rules

1. Always `/think` before building — no surprises halfway through
2. Always `/review` before `/deploy` — never ship unreviewed code
3. Always `/remember` at end of session — never lose context
4. Any change touching real money → confirm twice before proceeding

---

*Full guide: `Document 3 - The Development Agent Guide.md`*
