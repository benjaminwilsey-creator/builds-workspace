"""Report generation for Research Council - Obsidian and Slack outputs."""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import httpx

from council.config import (
    OBSIDIAN_VAULT_PATH,
    REPORT_FORMAT,
    REPORTS_DIR,
    SLACK_WEBHOOK_URL,
)
from council.models import ModelResponse
from council.router import RouteDecision

logger = logging.getLogger(__name__)


@dataclass
class ResearchReport:
    """Research report data structure."""

    query: str
    timestamp: datetime
    routing: RouteDecision
    results: Dict[str, ModelResponse]
    consensus: Optional[str] = None
    metadata: Optional[dict] = None


class ReportGenerator:
    """Generates reports in multiple formats (Markdown, Slack, JSON)."""

    def __init__(self):
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """Create required directories if they don't exist."""
        REPORTS_DIR.mkdir(exist_ok=True, parents=True)

        # Create Obsidian vault directory if configured
        if OBSIDIAN_VAULT_PATH and OBSIDIAN_VAULT_PATH != Path("~/obsidian/vault").expanduser():
            OBSIDIAN_VAULT_PATH.mkdir(exist_ok=True, parents=True)

    def generate(self, report: ResearchReport) -> Dict[str, str]:
        """
        Generate report in all configured formats.

        Args:
            report: ResearchReport to generate from

        Returns:
            Dict mapping format name to output path/URL
        """
        outputs = {}

        # Generate markdown report
        markdown_path = self._generate_markdown(report)
        if markdown_path:
            outputs["markdown"] = str(markdown_path)

        # Generate Obsidian note if vault configured
        obsidian_path = self._generate_obsidian(report)
        if obsidian_path:
            outputs["obsidian"] = str(obsidian_path)

        # Post to Slack if webhook configured
        slack_result = self._post_slack(report)
        if slack_result:
            outputs["slack"] = slack_result

        logger.info(f"Report generated: {list(outputs.keys())}")
        return outputs

    def _generate_markdown(self, report: ResearchReport) -> Optional[Path]:
        """Generate markdown report file."""
        if REPORT_FORMAT != "markdown":
            return None

        timestamp_str = report.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"research_{timestamp_str}.md"
        filepath = REPORTS_DIR / filename

        content = self._format_markdown(report)

        try:
            filepath.write_text(content, encoding="utf-8")
            logger.info(f"Markdown report written to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to write markdown report: {e}")
            return None

    def _generate_obsidian(self, report: ResearchReport) -> Optional[Path]:
        """Generate Obsidian vault note."""
        # Skip if vault path is default placeholder
        if OBSIDIAN_VAULT_PATH == Path("~/obsidian/vault").expanduser():
            return None

        if not OBSIDIAN_VAULT_PATH.exists():
            logger.warning(f"Obsidian vault not found: {OBSIDIAN_VAULT_PATH}")
            return None

        # Create research subfolder
        research_dir = OBSIDIAN_VAULT_PATH / "Research Council"
        research_dir.mkdir(exist_ok=True, parents=True)

        timestamp_str = report.timestamp.strftime("%Y-%m-%d %H%M")
        filename = f"Research {timestamp_str}.md"
        filepath = research_dir / filename

        # Obsidian-specific formatting with frontmatter
        content = self._format_obsidian(report)

        try:
            filepath.write_text(content, encoding="utf-8")
            logger.info(f"Obsidian note written to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to write Obsidian note: {e}")
            return None

    def _post_slack(self, report: ResearchReport) -> Optional[str]:
        """Post report summary to Slack."""
        # Skip if webhook is placeholder
        if SLACK_WEBHOOK_URL == "https://hooks.slack.com/placeholder":
            logger.debug("Slack webhook not configured, skipping")
            return None

        payload = self._format_slack(report)

        try:
            response = httpx.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Report posted to Slack")
            return "slack_posted"
        except httpx.HTTPError as e:
            logger.error(f"Failed to post to Slack: {e}")
            return None

    def _format_markdown(self, report: ResearchReport) -> str:
        """Format report as markdown."""
        lines = [
            f"# Research Report",
            f"",
            f"**Query:** {report.query}",
            f"**Timestamp:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Priority:** {report.routing.priority.value}",
            f"**Escalated:** {'Yes' if report.routing.escalated else 'No'}",
            f"**Models Used:** {', '.join(report.routing.models)}",
            f"",
            f"## Routing Decision",
            f"",
            f"{report.routing.reason}",
            f"",
            f"## Results",
            f"",
        ]

        # Add results from each model
        for model_name, response in report.results.items():
            lines.append(f"### {model_name.upper()}")
            lines.append(f"")

            if response.success:
                lines.append(f"**Status:** ✅ Success")
                if response.tokens_used:
                    lines.append(f"**Tokens:** {response.tokens_used}")
                lines.append(f"")
                lines.append(response.text)
            else:
                lines.append(f"**Status:** ❌ Failed")
                lines.append(f"**Error:** {response.error}")

            lines.append(f"")

        # Add consensus if present
        if report.consensus:
            lines.append(f"## Consensus")
            lines.append(f"")
            lines.append(report.consensus)
            lines.append(f"")

        return "\n".join(lines)

    def _format_obsidian(self, report: ResearchReport) -> str:
        """Format report as Obsidian note with frontmatter."""
        frontmatter = [
            "---",
            f"type: research-report",
            f"query: \"{report.query}\"",
            f"date: {report.timestamp.strftime('%Y-%m-%d')}",
            f"priority: {report.routing.priority.value}",
            f"escalated: {str(report.routing.escalated).lower()}",
            f"models: [{', '.join(report.routing.models)}]",
            "---",
            "",
        ]

        # Rest is similar to markdown but with wiki-links style
        body = self._format_markdown(report).split("\n", 1)[1]  # Skip first header

        return "\n".join(frontmatter) + body

    def _format_slack(self, report: ResearchReport) -> dict:
        """Format report as Slack message payload."""
        # Build summary text
        successful = sum(1 for r in report.results.values() if r.success)
        total = len(report.results)

        summary_text = f"*Research Query Complete*\n\n"
        summary_text += f"*Query:* {report.query}\n"
        summary_text += f"*Results:* {successful}/{total} models succeeded\n"
        summary_text += f"*Priority:* {report.routing.priority.value}"

        if report.routing.escalated:
            summary_text += " (escalated)"

        # Add consensus if present
        if report.consensus:
            consensus_preview = (
                report.consensus[:200] + "..."
                if len(report.consensus) > 200
                else report.consensus
            )
            summary_text += f"\n\n*Consensus:*\n{consensus_preview}"

        return {
            "text": summary_text,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": summary_text,
                    },
                },
            ],
        }


def create_report_generator() -> ReportGenerator:
    """Factory function to create configured report generator."""
    return ReportGenerator()
