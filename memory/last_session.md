---
date: 2026-04-10
project: HF Agents Course
---

## What we did
- Set up local Python venv for HF Agents Course, installed smolagents, gradio, huggingface_hub
- Got Dummy Agent Library notebook running locally with HF token loaded from .env
- Downloaded First Agent Template from HF Spaces and ran it locally as a Gradio chat UI
- Fixed smolagents 1.24.0 incompatibilities (renamed classes, removed params, encoding bug)
- Added DuckDuckGo search, image generation, timezone, and suggest_menu tools to the agent

## Next up
- Continue HF Agents Course — next lesson is custom tool creation in depth
- Check if HF Space (Rapidcosine/First_agent_template) build ever completed

## Watch out for
- Always run app.py with PYTHONUTF8=1 or Unicode from web search results crashes the UI
- HF token was exposed in chat — already regenerated and updated in .env
