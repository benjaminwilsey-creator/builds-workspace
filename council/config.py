"""Configuration constants for Research Council."""

import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
COUNCIL_ROOT = Path(__file__).parent
LOGS_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Model configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "sk-or-placeholder")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "sk-ant-placeholder")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model identifiers
MODEL_GPT4 = "openai/gpt-4-turbo"
MODEL_GEMINI = "google/gemini-pro"
MODEL_KIMI = "moonshot/moonshot-v1-8k"
MODEL_SONNET = "anthropic.claude-3-5-sonnet-20241022-v2:0"
MODEL_OPUS = "anthropic.claude-opus-4-20250514"

# Orchestrator settings
MAX_CONCURRENT_MODELS = 3
TIMEOUT_SECONDS = 120
MAX_RETRIES = 3

# State management
MAX_RECENT_ITEMS = 5
STATE_LOCK_TIMEOUT = 5.0

# Router settings
ESCALATION_THRESHOLD = 0.7
AUTO_ESCALATE_KEYWORDS = ["urgent", "critical", "emergency", "immediate"]

# Report settings
REPORT_FORMAT = "markdown"
OBSIDIAN_VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", "~/obsidian/vault")).expanduser()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/placeholder")

# Dashboard settings
DASHBOARD_PORT = 8080
DASHBOARD_HOST = "localhost"
REFRESH_INTERVAL_MS = 5000

# CoS integration
COS_API_URL = os.getenv("COS_API_URL", "http://localhost:8000")
COS_ENABLED = os.getenv("COS_ENABLED", "false").lower() == "true"
