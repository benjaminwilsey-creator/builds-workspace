---
name: Benjamin profile
description: Who Benjamin is — role, background, working style, and how Claude should collaborate with him
type: user
originSessionId: 750951b5-c792-41c6-b018-ddcbeb1a3029
---
## Who I Am

- **Name:** Benjamin Wilsey
- **GitHub:** benjaminwilsey-creator (alias: Rapidcosine)
- **Role:** Non-programmer and novice — thinks in business outcomes and plain English
- **Goal:** Build real, working software products without needing to code himself

## How I Work Best With Claude

- Explain the *why* behind every technical decision — don't assume I know terms
- Write production-grade code on my behalf
- Flag risks and tradeoffs before executing — never guess and ship
- Keep explanations short and plain. No jargon without a definition
- Ask if requirements are ambiguous. Never assume

## Context Optimization Preferences

- Read only the relevant section of a file — not the whole file — unless the task requires broader context
- When the active project is ambiguous, ask "Which project are we working on today?" rather than loading all project files
- Load independent context files in parallel at session start (e.g. MEMORY.md + last_session.md + benjamin.md simultaneously)
- If a file was already read earlier in the session, reference that read — don't re-read unless it may have changed
- When searching for a function or symbol, grep for it rather than reading whole files top to bottom

## Active Projects

- [[Projects/rapid2_bot]] — Live crypto trading bot on EC2 (Kraken exchange, real money)
- [[Projects/busymom_app]] — Family task/chore app for Liz (voice → structured tasks → Skylight + Google Calendar)
- [[Projects/busymom_app]] — BusyMomBrainDump voice app (backend complete, task queue ready for /autonomous)
- [[Projects/financial_manager]] — FinancialManager: Plaid+Slack bill tracker (scaffolded, pending setup)

## Technical Context

- Works on Windows 11, uses VS Code + Claude Code extension
- Primary workspace: `e:\Builds - Copy\`
- EC2 server: `ubuntu@3.138.144.246` (ssh alias: `rapid2`)
- Does not self-deploy — Claude handles all code changes and deployment steps
- Obsidian vault: `E:\Builds - Copy\memory\` — treat as a **live project dashboard**, not just a backup. Git branches, recent changes, and project activity should surface here.
- GitHub backup: `github.com/benjaminwilsey-creator/builds-workspace` — stores skills, memory, and workspace config. Each project gets its own private repo (created by `/new-project`).

## Skill & Memory Architecture Preferences

- Skills must be **project-agnostic** — no hardcoded paths, SSH details, or service names inside skill files
- Project-specific facts (local path, EC2 address, service name, deployed files) belong in the project's memory file under `memory/Projects/`
- Skills read memory at runtime to get project details — this way adding a new project never requires editing a skill
- `/catchup` should be lean: load only user context + MEMORY.md index + last_session. Load individual project memory files only when that project is being worked on that session.
