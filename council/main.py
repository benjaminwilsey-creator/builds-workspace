"""Main entry point for Research Council - ties all components together."""

import logging
from typing import Optional

from council.cos_integration import create_cos_bridge
from council.orchestrator import create_orchestrator
from council.reporting import ResearchReport, create_report_generator
from council.router import create_router

logger = logging.getLogger(__name__)


class ResearchCouncil:
    """
    Main Research Council coordinator.

    Combines router, orchestrator, reporting, and CoS integration
    for end-to-end multi-model research queries.
    """

    def __init__(self):
        self.router = create_router()
        self.orchestrator = create_orchestrator()
        self.report_generator = create_report_generator()
        self.cos_bridge = create_cos_bridge()

    def research(self, query: str, image_path: Optional[str] = None) -> ResearchReport:
        """
        Execute complete research workflow.

        Args:
            query: Research question
            image_path: Optional image path

        Returns:
            ResearchReport with full results
        """
        logger.info(f"Starting research: {query[:100]}...")

        # Route query to appropriate models
        routing = self.router.route(query)
        logger.info(f"Routing: {routing.reason}")

        # Execute parallel queries
        results = self.orchestrator.research(
            query, image_path=image_path, models=routing.models
        )

        # Extract consensus
        consensus = self.orchestrator.consensus_answer(results)

        # Build report
        from datetime import datetime

        report = ResearchReport(
            query=query,
            timestamp=datetime.now(),
            routing=routing,
            results=results,
            consensus=consensus,
        )

        # Generate outputs
        outputs = self.report_generator.generate(report)
        logger.info(f"Generated reports: {list(outputs.keys())}")

        # CoS integration
        cos_data = self.cos_bridge.process_with_cos(query, results, report)
        if cos_data["enabled"]:
            logger.info(f"CoS integration: {cos_data}")

        # Check if escalation needed
        if self.router.suggest_escalation(results):
            logger.warning("Post-query escalation suggested")
            ticket_id = self.cos_bridge.handle_escalation(
                query, "Low quality initial results", results
            )
            if ticket_id:
                logger.info(f"Escalated to CoS: {ticket_id}")

        return report


def create_council() -> ResearchCouncil:
    """Factory function to create configured Research Council."""
    return ResearchCouncil()


def main() -> None:
    """CLI entry point for Research Council."""
    import argparse
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Research Council - Multi-model AI research")
    parser.add_argument("query", help="Research query or question")
    parser.add_argument("--image", help="Path to image file (optional)")
    parser.add_argument("--dashboard", action="store_true", help="Start dashboard server")

    args = parser.parse_args()

    if args.dashboard:
        from council.dashboard import create_dashboard

        dashboard = create_dashboard()
        print("Starting dashboard server...")
        dashboard.start()
        return

    # Execute research
    council = create_council()

    try:
        report = council.research(args.query, image_path=args.image)

        # Print summary to stdout
        print("\n" + "=" * 80)
        print("RESEARCH COUNCIL REPORT")
        print("=" * 80)
        print(f"\nQuery: {report.query}")
        print(f"Priority: {report.routing.priority.value}")
        print(f"Models: {', '.join(report.routing.models)}")
        print(f"\nRouting: {report.routing.reason}")

        print("\n" + "-" * 80)
        print("RESULTS")
        print("-" * 80)

        for model_name, response in report.results.items():
            print(f"\n[{model_name.upper()}]")
            if response.success:
                print(f"✓ Success ({response.tokens_used or 0} tokens)")
                print(response.text[:500])
                if len(response.text) > 500:
                    print("...")
            else:
                print(f"✗ Failed: {response.error}")

        if report.consensus:
            print("\n" + "-" * 80)
            print("CONSENSUS")
            print("-" * 80)
            print(report.consensus)

        print("\n" + "=" * 80)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Research failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
