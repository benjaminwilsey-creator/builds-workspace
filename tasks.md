# Agent Task Queue

> Add tasks below before leaving. The autonomous agent works top-to-bottom.
> Do NOT edit tasks marked `[in-progress]` or `[done]` — the agent owns those.
>
> Format: `- [ ] Your task description here`
> Slack channel for updates: #claude-agent

---

## Pending

### BusyMomBrainDump — Phase 1 Gaps

- [ ] BusyMomBrainDump: Write pytest tests for POST /brain-dumps in tests/test_main.py. Cover: happy path (chore + event routed correctly), auth failure returns 401, empty items list returns 422, dry_run=true returns dry_run status without calling external APIs, mixed items where one errors and others succeed. Mock skylight_client.add_chore and GoogleCalendarClient.create_event. Use FastAPI TestClient from httpx.
- [ ] BusyMomBrainDump: Write pytest tests for POST /chores in tests/test_chores.py. Cover: valid chores routed to Skylight, invalid assigned_to (non-child) returns error, auth failure returns 401, dry_run mode. Mock add_chore. Reuse auth patterns from test_main.py.
- [ ] BusyMomBrainDump: Write OpenAPI schema file brain_dumps_openapi.yaml for the POST /brain-dumps endpoint. Model it after custom_gpt_add_chore_openapi.yaml. Include all fields from BrainDumpRequest and BrainDumpItem in main.py. Include all response fields from BrainDumpResponse. Server URL: https://busy-mom-brain-dump-api.onrender.com. Use bearer auth.
- [ ] BusyMomBrainDump: Update render.yaml to declare all required env vars. Non-secret vars (ENV, APP_TIMEZONE) can have inline values. Secret vars (GPT_ACTION_API_KEY, GOOGLE_OAUTH_CREDENTIALS_JSON, GOOGLE_OAUTH_TOKEN_JSON, GOOGLE_FAMILY_CALENDAR_ID, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SKYLIGHT_EMAIL, SKYLIGHT_PASSWORD, SKYLIGHT_FRAME_ID) should use sync: false so Render prompts for them. Do not hardcode any values.

## In Progress

<!-- Agent moves tasks here when it starts them — do not edit -->

## Done

<!-- Agent moves tasks here when complete — includes branch name and PR link -->
