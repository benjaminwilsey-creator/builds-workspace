"""Thread-safe live state management for Research Council."""

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Deque, Dict, Optional

from council.config import MAX_RECENT_ITEMS


@dataclass
class ResearchItem:
    """Single research query or result."""

    id: str
    query: str
    timestamp: datetime
    status: str  # "pending", "in_progress", "completed", "failed"
    models_used: list[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class CouncilState:
    """Thread-safe state container for Research Council operations."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._recent: Deque[ResearchItem] = deque(maxlen=MAX_RECENT_ITEMS)
        self._active_queries: Dict[str, ResearchItem] = {}
        self._stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_model_calls": 0,
        }

    def add_query(self, item: ResearchItem) -> None:
        """Add new research query to state."""
        with self._lock:
            self._active_queries[item.id] = item
            self._recent.append(item)
            self._stats["total_queries"] += 1

    def update_query(self, query_id: str, **updates: Any) -> None:
        """Update existing query with new data."""
        with self._lock:
            if query_id in self._active_queries:
                item = self._active_queries[query_id]
                for key, value in updates.items():
                    setattr(item, key, value)

    def complete_query(self, query_id: str, results: Dict[str, Any]) -> None:
        """Mark query as completed with results."""
        with self._lock:
            if query_id in self._active_queries:
                item = self._active_queries[query_id]
                item.status = "completed"
                item.results = results
                self._stats["successful_queries"] += 1
                self._stats["total_model_calls"] += len(item.models_used)
                del self._active_queries[query_id]

    def fail_query(self, query_id: str, error: str) -> None:
        """Mark query as failed with error message."""
        with self._lock:
            if query_id in self._active_queries:
                item = self._active_queries[query_id]
                item.status = "failed"
                item.error = error
                self._stats["failed_queries"] += 1
                del self._active_queries[query_id]

    def get_query(self, query_id: str) -> Optional[ResearchItem]:
        """Retrieve query by ID."""
        with self._lock:
            return self._active_queries.get(query_id)

    def get_recent(self, count: int = MAX_RECENT_ITEMS) -> list[ResearchItem]:
        """Get recent research items (up to count)."""
        with self._lock:
            return list(self._recent)[-count:]

    def get_active_count(self) -> int:
        """Get count of currently active queries."""
        with self._lock:
            return len(self._active_queries)

    def get_stats(self) -> Dict[str, int]:
        """Get current statistics snapshot."""
        with self._lock:
            return self._stats.copy()

    def clear(self) -> None:
        """Clear all state (for testing)."""
        with self._lock:
            self._recent.clear()
            self._active_queries.clear()
            self._stats = {
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "total_model_calls": 0,
            }


# Global state instance
_state = CouncilState()


def get_state() -> CouncilState:
    """Get global council state instance."""
    return _state
