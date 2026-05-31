"""Router for Research Council - query triggers and escalation logic."""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from council.config import AUTO_ESCALATE_KEYWORDS, ESCALATION_THRESHOLD

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Query priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ModelTier(Enum):
    """Model capability tiers."""

    FAST = "fast"  # GPT-4, Gemini
    STANDARD = "standard"  # Sonnet
    PREMIUM = "premium"  # Opus


@dataclass
class RouteDecision:
    """Routing decision for a research query."""

    models: List[str]
    priority: Priority
    escalated: bool
    reason: str


class ResearchRouter:
    """Routes queries to appropriate models based on content and priority."""

    def __init__(self):
        # Model assignments by tier
        self._tier_models = {
            ModelTier.FAST: ["gpt4", "gemini"],
            ModelTier.STANDARD: ["sonnet"],
            ModelTier.PREMIUM: ["opus"],
        }

        # Complexity indicators
        self._complex_patterns = [
            r"\b(analyze|compare|evaluate|assess|critique)\b",
            r"\b(multiple|several|various|different)\b",
            r"\b(detailed|comprehensive|thorough|in-depth)\b",
            r"\b(explain|describe).{30,}",  # Long explanation requests
        ]

    def route(self, query: str, force_priority: Optional[Priority] = None) -> RouteDecision:
        """
        Determine routing for query based on content analysis.

        Args:
            query: Research query text
            force_priority: Override auto-detected priority

        Returns:
            RouteDecision with model selection and metadata
        """
        # Detect priority
        priority = force_priority or self._detect_priority(query)

        # Check for auto-escalation
        escalated = self._should_escalate(query, priority)

        # Select models based on priority and escalation
        models = self._select_models(priority, escalated)

        reason = self._build_reason(query, priority, escalated)

        decision = RouteDecision(
            models=models,
            priority=priority,
            escalated=escalated,
            reason=reason,
        )

        logger.info(
            f"Routed query: priority={priority.value}, escalated={escalated}, "
            f"models={models}"
        )

        return decision

    def _detect_priority(self, query: str) -> Priority:
        """Detect priority from query content."""
        query_lower = query.lower()

        # Check for urgent keywords
        if any(kw in query_lower for kw in AUTO_ESCALATE_KEYWORDS):
            return Priority.URGENT

        # Check for complexity indicators
        complexity_score = sum(
            1 for pattern in self._complex_patterns
            if re.search(pattern, query_lower, re.IGNORECASE)
        )

        if complexity_score >= 3:
            return Priority.HIGH
        elif complexity_score >= 1:
            return Priority.NORMAL
        else:
            return Priority.LOW

    def _should_escalate(self, query: str, priority: Priority) -> bool:
        """Determine if query should escalate to premium models."""
        # Always escalate urgent queries
        if priority == Priority.URGENT:
            return True

        # Escalate high-priority queries
        if priority == Priority.HIGH:
            return True

        # Check query length as complexity proxy
        if len(query) > 500:
            return True

        # Check for specific escalation triggers
        escalation_triggers = [
            r"\bopus\b",  # Explicit model request
            r"\bbest model\b",
            r"\bmost capable\b",
            r"\bhighest quality\b",
            r"\b(legal|medical|financial) advice\b",  # High-stakes domains
        ]

        query_lower = query.lower()
        if any(re.search(pattern, query_lower) for pattern in escalation_triggers):
            return True

        return False

    def _select_models(self, priority: Priority, escalated: bool) -> List[str]:
        """Select models based on priority and escalation status."""
        if escalated:
            # Use premium model plus one standard for comparison
            return self._tier_models[ModelTier.PREMIUM] + self._tier_models[ModelTier.STANDARD]

        if priority == Priority.URGENT:
            # Fast + premium for speed and quality
            return self._tier_models[ModelTier.FAST][0:1] + self._tier_models[ModelTier.PREMIUM]

        if priority == Priority.HIGH:
            # Standard + fast for balanced response
            return self._tier_models[ModelTier.STANDARD] + self._tier_models[ModelTier.FAST][0:1]

        if priority == Priority.NORMAL:
            # Standard model
            return self._tier_models[ModelTier.STANDARD]

        # LOW priority: fast models only
        return self._tier_models[ModelTier.FAST]

    def _build_reason(self, query: str, priority: Priority, escalated: bool) -> str:
        """Build human-readable routing reason."""
        reasons = [f"Priority: {priority.value}"]

        if escalated:
            reasons.append("Escalated to premium models")

        if priority == Priority.URGENT:
            reasons.append("Urgent keywords detected")

        if len(query) > 500:
            reasons.append("Long query (high complexity)")

        complexity_score = sum(
            1 for pattern in self._complex_patterns
            if re.search(pattern, query.lower(), re.IGNORECASE)
        )
        if complexity_score > 0:
            reasons.append(f"Complexity indicators: {complexity_score}")

        return " | ".join(reasons)

    def suggest_escalation(
        self, initial_results: dict, confidence_threshold: float = ESCALATION_THRESHOLD
    ) -> bool:
        """
        Suggest escalation based on initial results quality.

        Args:
            initial_results: Dict of ModelResponse from initial query
            confidence_threshold: Minimum confidence score to avoid escalation

        Returns:
            True if escalation recommended
        """
        # Check if any models failed
        any_failed = any(not resp.success for resp in initial_results.values())
        if any_failed:
            logger.info("Escalation suggested due to model failures")
            return True

        # Check response length as quality proxy (very simple heuristic)
        avg_length = sum(len(resp.text) for resp in initial_results.values()) / len(
            initial_results
        )

        if avg_length < 100:
            logger.info(f"Escalation suggested due to short responses (avg={avg_length})")
            return True

        # In production, this would use more sophisticated quality metrics:
        # - Semantic similarity between responses
        # - Confidence scores from models
        # - Response completeness checks

        return False


def create_router() -> ResearchRouter:
    """Factory function to create configured router."""
    return ResearchRouter()
