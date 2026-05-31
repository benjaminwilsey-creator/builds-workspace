# Research Council

Multi-model AI research system that queries multiple AI models in parallel, aggregates results, and generates comprehensive reports.

## Architecture

```
┌─────────────────┐
│  ResearchCouncil │  Main coordinator
└────────┬─────────┘
         │
    ┌────┴────┬────────┬──────────┬──────────┐
    │         │        │          │          │
┌───▼───┐ ┌──▼──┐ ┌───▼───┐ ┌────▼─────┐ ┌──▼──┐
│Router │ │Orch.│ │Report │ │Dashboard │ │ CoS │
└───┬───┘ └──┬──┘ └───┬───┘ └────┬─────┘ └──┬──┘
    │        │        │          │          │
┌───▼────────▼────────▼──────────▼──────────▼───┐
│              State Management                  │
└────────────────────────────────────────────────┘
```

## Components

### Core (`main.py`)
- **ResearchCouncil**: Main coordinator that orchestrates the complete research workflow

### Routing (`router.py`)
- Priority detection (LOW/NORMAL/HIGH/URGENT)
- Auto-escalation based on complexity
- Model tier selection (FAST/STANDARD/PREMIUM)

### Orchestration (`orchestrator.py`)
- Parallel multi-model queries via ThreadPoolExecutor
- Retry logic with exponential backoff
- Consensus extraction from multiple responses

### Models (`models.py`)
- Unified `ModelResponse` interface
- OpenRouter adapter (GPT-4, Gemini, Kimi)
- Anthropic adapter (Claude Sonnet, Claude Opus)
- Lazy API key loading (import-safe)

### Reporting (`reporting.py`)
- Markdown reports to `reports/` directory
- Obsidian vault notes with frontmatter
- Slack webhook integration
- Multi-format output

### Dashboard (`dashboard.py`)
- Live web UI on `localhost:8080`
- Real-time stats (active/total/successful/failed queries)
- Recent queries display with status
- Auto-refresh (5s default)

### State (`state.py`)
- Thread-safe live state management
- ResearchItem tracking (pending/in_progress/completed/failed)
- Statistics aggregation
- 5-item recent history cap

### CoS Integration (`cos_integration.py`)
- Query submission to CoS system
- Results and report forwarding
- Escalation handling
- Status polling

## Usage

### As a Library

```python
from council.main import create_council

council = create_council()
report = council.research("What are the key differences between GPT-4 and Claude?")

print(f"Priority: {report.routing.priority.value}")
print(f"Models: {report.routing.models}")
print(f"Consensus: {report.consensus}")
```

### CLI

```bash
# Basic query
python -m council.main "Explain quantum computing"

# With image
python -m council.main "Describe this image" --image path/to/image.png

# Start dashboard
python -m council.main --dashboard
```

### Dashboard

```bash
python -m council.dashboard
# Visit http://localhost:8080
```

## Configuration

Set environment variables in `.env`:

```bash
# API Keys
OPENROUTER_API_KEY=sk-or-v1-your-key
ANTHROPIC_API_KEY=sk-ant-api03-your-key

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Obsidian
OBSIDIAN_VAULT_PATH=/path/to/vault

# CoS
COS_API_URL=http://localhost:8000
COS_ENABLED=false

# Dashboard
DASHBOARD_PORT=8080
DASHBOARD_HOST=localhost
```

## Model Tiers

- **FAST**: GPT-4, Gemini (quick responses)
- **STANDARD**: Claude Sonnet (balanced)
- **PREMIUM**: Claude Opus (highest quality)

## Routing Logic

| Priority | Trigger | Models |
|----------|---------|--------|
| LOW | Simple queries | Fast models only |
| NORMAL | Standard complexity | Standard + 1 fast |
| HIGH | Complex analysis | Standard + fast |
| URGENT | Urgent keywords | Fast + premium |
| (escalated) | Complexity/quality | Premium + standard |

## Auto-Escalation Triggers

- Urgent keywords: urgent, critical, emergency, immediate
- Long queries (>500 chars)
- Complex patterns: analyze, compare, evaluate, detailed
- High-stakes domains: legal, medical, financial
- Low quality initial results

## Development

```bash
# Install dependencies
pip install -r council/requirements.txt

# Run tests (when implemented)
pytest council/

# Type checking
mypy council/

# Format code
black council/
```

## Files

```
council/
├── __init__.py           Package marker
├── config.py             All constants and config
├── state.py              Thread-safe state management
├── models.py             Model adapters
├── orchestrator.py       Parallel query execution
├── router.py             Query routing and escalation
├── reporting.py          Multi-format report generation
├── dashboard.py          Live web UI
├── cos_integration.py    CoS system integration
├── main.py               Main coordinator and CLI
├── requirements.txt      Dependencies
├── .env.example          Environment variable template
└── README.md             This file
```

## Status

**Build Status**: ✅ Complete (7/7 tasks)

- ✅ COUNCIL-001: Scaffold, config, state
- ✅ COUNCIL-002: Model adapters
- ✅ COUNCIL-003: Orchestrator
- ✅ COUNCIL-004: Router
- ✅ COUNCIL-005: Reporting
- ✅ COUNCIL-006: Dashboard
- ✅ COUNCIL-007: CoS integration

## License

Internal use - Benjamin Wilsey / Rapid Cosine
