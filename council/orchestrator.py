"""Orchestrator pipeline for Research Council - parallel multi-model queries."""

import concurrent.futures
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from council.config import MAX_CONCURRENT_MODELS, MAX_RETRIES, TIMEOUT_SECONDS
from council.models import ModelAdapter, ModelResponse, get_adapter
from council.state import ResearchItem, get_state

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """Orchestrates parallel queries across multiple AI models."""

    def __init__(self, model_names: Optional[List[str]] = None):
        """
        Initialize orchestrator with specified models.

        Args:
            model_names: List of model names to use (default: all available)
        """
        if model_names is None:
            model_names = ["gpt4", "gemini", "sonnet"]  # Default council

        self.model_names = model_names
        self._state = get_state()

    def research(
        self,
        query: str,
        image_path: Optional[str] = None,
        models: Optional[List[str]] = None,
    ) -> Dict[str, ModelResponse]:
        """
        Execute research query across multiple models in parallel.

        Args:
            query: Research question or prompt
            image_path: Optional path to image for models that support it
            models: Override default models for this query

        Returns:
            Dict mapping model name to ModelResponse
        """
        query_id = str(uuid.uuid4())
        target_models = models or self.model_names

        # Create research item and add to state
        item = ResearchItem(
            id=query_id,
            query=query,
            timestamp=datetime.now(),
            status="in_progress",
            models_used=target_models,
        )
        self._state.add_query(item)

        logger.info(
            f"Starting research query {query_id} with models: {target_models}"
        )

        results: Dict[str, ModelResponse] = {}

        try:
            # Execute queries in parallel with thread pool
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(len(target_models), MAX_CONCURRENT_MODELS)
            ) as executor:
                # Submit all model queries
                future_to_model = {
                    executor.submit(
                        self._query_with_retry, model_name, query, image_path
                    ): model_name
                    for model_name in target_models
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(
                    future_to_model, timeout=TIMEOUT_SECONDS
                ):
                    model_name = future_to_model[future]
                    try:
                        response = future.result()
                        results[model_name] = response

                        if response.success:
                            logger.info(
                                f"Model {model_name} completed successfully "
                                f"({response.tokens_used or 0} tokens)"
                            )
                        else:
                            logger.warning(
                                f"Model {model_name} failed: {response.error}"
                            )

                    except Exception as e:
                        logger.error(f"Model {model_name} raised exception: {e}")
                        results[model_name] = ModelResponse(
                            model=model_name,
                            text="",
                            success=False,
                            error=f"Executor exception: {str(e)}",
                        )

            # Mark query as complete
            self._state.complete_query(
                query_id, {model: resp.text for model, resp in results.items()}
            )

            return results

        except concurrent.futures.TimeoutError:
            error_msg = f"Research query timed out after {TIMEOUT_SECONDS}s"
            logger.error(error_msg)
            self._state.fail_query(query_id, error_msg)
            return results  # Return partial results

        except Exception as e:
            error_msg = f"Orchestrator error: {str(e)}"
            logger.error(error_msg)
            self._state.fail_query(query_id, error_msg)
            raise

    def _query_with_retry(
        self, model_name: str, query: str, image_path: Optional[str]
    ) -> ModelResponse:
        """Execute model query with retry logic."""
        adapter = get_adapter(model_name)
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                response = adapter.query(query, image_path)

                if response.success:
                    return response

                # Non-success response, retry
                last_error = response.error
                logger.warning(
                    f"Model {model_name} attempt {attempt + 1}/{MAX_RETRIES} "
                    f"failed: {response.error}"
                )

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Model {model_name} attempt {attempt + 1}/{MAX_RETRIES} "
                    f"raised exception: {e}"
                )

        # All retries exhausted
        return ModelResponse(
            model=model_name,
            text="",
            success=False,
            error=f"Failed after {MAX_RETRIES} attempts. Last error: {last_error}",
        )

    def consensus_answer(
        self, results: Dict[str, ModelResponse], min_agreement: int = 2
    ) -> Optional[str]:
        """
        Extract consensus answer from multiple model responses.

        Args:
            results: Dict of model responses
            min_agreement: Minimum number of models that must agree

        Returns:
            Consensus answer or None if no consensus found
        """
        successful = [
            resp.text for resp in results.values() if resp.success and resp.text
        ]

        if len(successful) < min_agreement:
            return None

        # Simple approach: return most common response
        # In production, this would use semantic similarity
        from collections import Counter

        counter = Counter(successful)
        most_common, count = counter.most_common(1)[0]

        if count >= min_agreement:
            return most_common

        return None


def create_orchestrator(models: Optional[List[str]] = None) -> ResearchOrchestrator:
    """Factory function to create configured orchestrator."""
    return ResearchOrchestrator(model_names=models)
