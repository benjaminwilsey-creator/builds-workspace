---
name: BusyMomBrainDump app state
description: Current state of the BusyMomBrainDump FastAPI backend as of 2026-04-18 — Phase 1 complete, 4 tasks queued
type: project
originSessionId: ea8f5ab0-e150-41ca-bfe5-04c2bff8464d
---
## What It Does
Liz speaks or types a brain dump into ChatGPT. A Custom GPT parses it and sends structured
items to this FastAPI backend. The backend routes chores to Skylight (kids) and events to
Google Calendar (family).

## Current State (as of 2026-04-18)

**Phase 1 backend is COMPLETE** — the BUILD_PLAN.md is outdated and wrong about this.

### What's fully implemented:
- `POST /brain-dumps` — main endpoint, routes events → Google Calendar, chores → Skylight
- `POST /chores` — chores-only shortcut endpoint
- Auth — bearer token via `GPT_ACTION_API_KEY`
- `backend/calendar_client.py` — Google Calendar OAuth2, event creation, bootstrap flow
- `backend/skylight_client.py` — Skylight chore creation, child category IDs mapped
- `backend/database.py` — Supabase persistence (optional, gracefully skipped if not configured)
- `render.yaml` — basic deploy config exists (but missing env var declarations)
- `custom_gpt_add_chore_openapi.yaml` — OpenAPI schema for /chores GPT action

### What's NOT done (real gaps):
1. `tests/` — completely empty. No tests at all.
2. OpenAPI schema for `/brain-dumps` — only `/chores` has a schema
3. `render.yaml` — missing all env var declarations (secrets not declared)

## Tasks Queued in tasks.md (ready to run with /autonomous)
1. Write pytest tests for POST /brain-dumps
2. Write pytest tests for POST /chores
3. Write OpenAPI schema for POST /brain-dumps
4. Update render.yaml with all env var declarations

## Key Files
- `e:/Builds - Copy/BusyMomBrainDump/` — project root
- `e:/Builds - Copy/BusyMomBrainDump/CLAUDE.md` — project rules for sub-agents
- `e:/Builds - Copy/tasks.md` — task queue for /autonomous

## Deploy Target
- Render free web service
- URL: `https://busy-mom-brain-dump-api.onrender.com`
- Cold starts expected on free tier

## Why
- **How:** `/autonomous` to run the task queue
- **Next:** Run `/autonomous` — it will work through all 4 tasks, one sub-agent per task, Slack updates after each
