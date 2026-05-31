"""CoS (Council of Sparrows) integration for Research Council."""

import logging
from typing import Dict, Optional

import httpx

from council.config import COS_API_URL, COS_ENABLED, TIMEOUT_SECONDS
from council.models import ModelResponse
from council.reporting import ResearchReport

logger = logging.getLogger(__name__)


class CoSIntegration:
    """Integration with CoS (Council of Sparrows) system."""

    def __init__(self, api_url: str = COS_API_URL, enabled: bool = COS_ENABLED):
        self.api_url = api_url
        self.enabled = enabled
        self._client = httpx.Client(timeout=TIMEOUT_SECONDS)

    def submit_query(self, query: str, context: Optional[dict] = None) -> Optional[str]:
        """
        Submit query to CoS for processing.

        Args:
            query: Research query text
            context: Optional context dict

        Returns:
            CoS query ID if successful, None otherwise
        """
        if not self.enabled:
            logger.debug("CoS integration disabled")
            return None

        payload = {
            "query": query,
            "source": "research_council",
            "context": context or {},
        }

        try:
            response = self._client.post(f"{self.api_url}/query", json=payload)
            response.raise_for_status()
            data = response.json()
            query_id = data.get("query_id")
            logger.info(f"Submitted query to CoS: {query_id}")
            return query_id

        except httpx.HTTPError as e:
            logger.error(f"Failed to submit query to CoS: {e}")
            return None

    def send_results(
        self, cos_query_id: str, results: Dict[str, ModelResponse]
    ) -> bool:
        """
        Send Research Council results back to CoS.

        Args:
            cos_query_id: CoS query ID
            results: Dict of model responses

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        # Format results for CoS
        formatted_results = {
            "query_id": cos_query_id,
            "results": [
                {
                    "model": model_name,
                    "success": response.success,
                    "text": response.text if response.success else None,
                    "error": response.error,
                    "tokens_used": response.tokens_used,
                    "metadata": response.metadata,
                }
                for model_name, response in results.items()
            ],
        }

        try:
            response = self._client.post(
                f"{self.api_url}/results", json=formatted_results
            )
            response.raise_for_status()
            logger.info(f"Sent results to CoS for query {cos_query_id}")
            return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to send results to CoS: {e}")
            return False

    def send_report(self, cos_query_id: str, report: ResearchReport) -> bool:
        """
        Send complete research report to CoS.

        Args:
            cos_query_id: CoS query ID
            report: ResearchReport object

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        payload = {
            "query_id": cos_query_id,
            "query": report.query,
            "timestamp": report.timestamp.isoformat(),
            "priority": report.routing.priority.value,
            "escalated": report.routing.escalated,
            "models_used": report.routing.models,
            "consensus": report.consensus,
            "results_summary": {
                "total": len(report.results),
                "successful": sum(1 for r in report.results.values() if r.success),
                "failed": sum(1 for r in report.results.values() if not r.success),
            },
        }

        try:
            response = self._client.post(f"{self.api_url}/report", json=payload)
            response.raise_for_status()
            logger.info(f"Sent report to CoS for query {cos_query_id}")
            return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to send report to CoS: {e}")
            return False

    def request_escalation(
        self, query: str, reason: str, initial_results: Optional[Dict[str, ModelResponse]] = None
    ) -> Optional[str]:
        """
        Request escalation to CoS for complex queries.

        Args:
            query: Original query
            reason: Escalation reason
            initial_results: Optional initial results that triggered escalation

        Returns:
            Escalation ticket ID if successful, None otherwise
        """
        if not self.enabled:
            return None

        payload = {
            "query": query,
            "reason": reason,
            "source": "research_council_escalation",
        }

        if initial_results:
            payload["initial_results_summary"] = {
                "models": list(initial_results.keys()),
                "all_failed": all(not r.success for r in initial_results.values()),
            }

        try:
            response = self._client.post(f"{self.api_url}/escalate", json=payload)
            response.raise_for_status()
            data = response.json()
            ticket_id = data.get("ticket_id")
            logger.info(f"Escalated query to CoS: {ticket_id}")
            return ticket_id

        except httpx.HTTPError as e:
            logger.error(f"Failed to escalate query to CoS: {e}")
            return None

    def get_status(self, cos_query_id: str) -> Optional[dict]:
        """
        Get status of CoS query.

        Args:
            cos_query_id: CoS query ID

        Returns:
            Status dict if successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            response = self._client.get(f"{self.api_url}/status/{cos_query_id}")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get CoS status: {e}")
            return None

    def close(self) -> None:
        """Close HTTP client."""
        self._client.close()


class CoSBridge:
    """High-level bridge between Research Council and CoS."""

    def __init__(self, integration: Optional[CoSIntegration] = None):
        self.integration = integration or CoSIntegration()

    def process_with_cos(
        self, query: str, results: Dict[str, ModelResponse], report: ResearchReport
    ) -> dict:
        """
        Complete CoS workflow: submit, send results, send report.

        Args:
            query: Original query
            results: Model responses
            report: Research report

        Returns:
            Dict with CoS interaction details
        """
        cos_data = {
            "enabled": self.integration.enabled,
            "query_id": None,
            "results_sent": False,
            "report_sent": False,
        }

        if not self.integration.enabled:
            return cos_data

        # Submit query
        query_id = self.integration.submit_query(query)
        cos_data["query_id"] = query_id

        if not query_id:
            return cos_data

        # Send results
        results_sent = self.integration.send_results(query_id, results)
        cos_data["results_sent"] = results_sent

        # Send report
        report_sent = self.integration.send_report(query_id, report)
        cos_data["report_sent"] = report_sent

        return cos_data

    def handle_escalation(
        self, query: str, reason: str, initial_results: Dict[str, ModelResponse]
    ) -> Optional[str]:
        """
        Handle escalation to CoS.

        Args:
            query: Original query
            reason: Escalation reason
            initial_results: Initial results that triggered escalation

        Returns:
            Escalation ticket ID if successful, None otherwise
        """
        return self.integration.request_escalation(query, reason, initial_results)


def create_cos_integration() -> CoSIntegration:
    """Factory function to create configured CoS integration."""
    return CoSIntegration()


def create_cos_bridge() -> CoSBridge:
    """Factory function to create configured CoS bridge."""
    return CoSBridge()
