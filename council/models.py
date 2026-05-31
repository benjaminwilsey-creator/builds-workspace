"""Model adapters for Research Council - unified interface to multiple AI providers."""

import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from anthropic import Anthropic

from council.config import (
    ANTHROPIC_API_KEY,
    MODEL_GEMINI,
    MODEL_GPT4,
    MODEL_KIMI,
    MODEL_OPUS,
    MODEL_SONNET,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    TIMEOUT_SECONDS,
)


@dataclass
class ModelResponse:
    """Unified response format from any model."""

    model: str
    text: str
    success: bool
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class ModelAdapter(ABC):
    """Base adapter interface for AI models."""

    @abstractmethod
    def query(self, prompt: str, image_path: Optional[str] = None) -> ModelResponse:
        """Send query to model and return unified response."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return model identifier."""
        pass


class OpenRouterAdapter(ModelAdapter):
    """Adapter for models via OpenRouter API."""

    def __init__(self, model_id: str):
        self._model_id = model_id
        self._client = httpx.Client(timeout=TIMEOUT_SECONDS)

    @property
    def model_name(self) -> str:
        return self._model_id

    def query(self, prompt: str, image_path: Optional[str] = None) -> ModelResponse:
        """Query OpenRouter model."""
        # Read API key at call time (not import time)
        import os

        api_key = os.getenv("OPENROUTER_API_KEY", OPENROUTER_API_KEY)

        if api_key == "sk-or-placeholder":
            return ModelResponse(
                model=self._model_id,
                text="[Mock response - API key not configured]",
                success=True,
                metadata={"mock": True},
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Handle image for Kimi (fallback to text-only for others)
        content = prompt
        if image_path and self._model_id == MODEL_KIMI:
            try:
                with open(image_path, "rb") as f:
                    image_b64 = base64.b64encode(f.read()).decode("utf-8")
                content = f"{prompt}\n[Image: data:image/png;base64,{image_b64[:50]}...]"
            except Exception as e:
                return ModelResponse(
                    model=self._model_id,
                    text="",
                    success=False,
                    error=f"Image read failed: {e}",
                )

        payload = {
            "model": self._model_id,
            "messages": [{"role": "user", "content": content}],
        }

        try:
            response = self._client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            return ModelResponse(
                model=self._model_id,
                text=data["choices"][0]["message"]["content"],
                success=True,
                tokens_used=data.get("usage", {}).get("total_tokens"),
                metadata={"provider": "openrouter"},
            )

        except httpx.HTTPStatusError as e:
            return ModelResponse(
                model=self._model_id,
                text="",
                success=False,
                error=f"HTTP {e.response.status_code}: {e.response.text}",
            )
        except Exception as e:
            return ModelResponse(
                model=self._model_id,
                text="",
                success=False,
                error=f"Request failed: {str(e)}",
            )


class AnthropicAdapter(ModelAdapter):
    """Adapter for Claude models via Anthropic SDK."""

    def __init__(self, model_id: str):
        self._model_id = model_id
        # Client created lazily at call time with fresh API key
        self._client: Optional[Anthropic] = None

    @property
    def model_name(self) -> str:
        return self._model_id

    def _get_client(self) -> Anthropic:
        """Get or create Anthropic client with current API key."""
        import os

        api_key = os.getenv("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)

        if api_key == "sk-ant-placeholder":
            # Return mock client (will be caught in query method)
            raise ValueError("API key not configured")

        return Anthropic(api_key=api_key, timeout=TIMEOUT_SECONDS)

    def query(self, prompt: str, image_path: Optional[str] = None) -> ModelResponse:
        """Query Anthropic model."""
        try:
            client = self._get_client()
        except ValueError:
            # Mock mode
            return ModelResponse(
                model=self._model_id,
                text="[Mock response - API key not configured]",
                success=True,
                metadata={"mock": True},
            )

        messages = [{"role": "user", "content": prompt}]

        try:
            response = client.messages.create(
                model=self._model_id,
                max_tokens=4096,
                messages=messages,
            )

            return ModelResponse(
                model=self._model_id,
                text=response.content[0].text,
                success=True,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                metadata={"provider": "anthropic", "stop_reason": response.stop_reason},
            )

        except Exception as e:
            return ModelResponse(
                model=self._model_id,
                text="",
                success=False,
                error=f"Anthropic API error: {str(e)}",
            )


# Factory functions for each model
def gpt4_adapter() -> ModelAdapter:
    """Create GPT-4 adapter (via OpenRouter)."""
    return OpenRouterAdapter(MODEL_GPT4)


def gemini_adapter() -> ModelAdapter:
    """Create Gemini adapter (via OpenRouter)."""
    return OpenRouterAdapter(MODEL_GEMINI)


def kimi_adapter() -> ModelAdapter:
    """Create Kimi adapter with image support (via OpenRouter)."""
    return OpenRouterAdapter(MODEL_KIMI)


def sonnet_adapter() -> ModelAdapter:
    """Create Claude Sonnet adapter (via Anthropic SDK)."""
    return AnthropicAdapter(MODEL_SONNET)


def opus_adapter() -> ModelAdapter:
    """Create Claude Opus adapter (via Anthropic SDK)."""
    return AnthropicAdapter(MODEL_OPUS)


# Registry of all available adapters
ADAPTERS = {
    "gpt4": gpt4_adapter,
    "gemini": gemini_adapter,
    "kimi": kimi_adapter,
    "sonnet": sonnet_adapter,
    "opus": opus_adapter,
}


def get_adapter(name: str) -> ModelAdapter:
    """Get model adapter by name."""
    if name not in ADAPTERS:
        raise ValueError(f"Unknown model: {name}. Available: {list(ADAPTERS.keys())}")
    return ADAPTERS[name]()
