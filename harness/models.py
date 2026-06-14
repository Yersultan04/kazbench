"""
Model adapters for KazBench.

Each adapter exposes a single method:
    generate(prompt: str) -> str

Factory:
    build_model(name: str, model_id: str | None = None) -> BaseModel
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Optional


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class BaseModel(ABC):
    """Abstract base for all KazBench model adapters."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response string for the given prompt."""


# ---------------------------------------------------------------------------
# DummyModel
# ---------------------------------------------------------------------------

_DUMMY_CHOICE_PATTERN = r"(\d)"
_DUMMY_SENTIMENT_LABELS = ("ong", "teris", "beitarap")  # ascii placeholders used internally


class DummyModel(BaseModel):
    """
    Offline, deterministic model that requires no API key.

    Behaviour (designed so the harness can be validated end-to-end without
    any network access):
    - Multiple-choice tasks     -> returns "0" (always picks choice 0)
    - Sentiment classification  -> returns "on" (always predicts positive)
    - Translation               -> returns a short ASCII stub sentence so
                                   chrF can be computed (non-zero but low)
    - Instruction-following     -> returns a one-sentence stub response
    """

    # Used by run_eval to detect DummyModel and skip real LLM-judge
    IS_DUMMY: bool = True

    def generate(self, prompt: str) -> str:  # noqa: D401
        """Return a deterministic stub response."""
        p = prompt.lower()
        # Translation tasks ask to "translate" something
        if "аудар" in p or "translate" in p or "translation" in p:
            return "This is a stub translation output for harness testing."
        # Instruction-following tasks contain "rubric" or explicit instructions
        if "нускама" in p or "instruction" in p or "rubric" in p or "тапсырма" in p:
            return "This is a stub instruction-following response."
        # Sentiment tasks ask to classify
        if "сезим" in p or "sentiment" in p or "пiкiр" in p or "кокейтесті" in p:
            # Return the positive Kazakh label so accuracy is 0 when gold is negative/neutral
            return "on"
        # Default: MC answer
        return "0"


# ---------------------------------------------------------------------------
# ClaudeModel
# ---------------------------------------------------------------------------

class ClaudeModel(BaseModel):
    """
    Adapter wrapping the Anthropic Python SDK.

    Reads ANTHROPIC_API_KEY from the environment (lazy import so the SDK is
    not required when only DummyModel is used).

    Args:
        model_id: Anthropic model identifier.
                  Default: "claude-haiku-4-5-20251001"
        max_tokens: Maximum tokens in the response (default 512).
    """

    DEFAULT_MODEL = "claude-haiku-4-5-20251001"

    def __init__(
        self,
        model_id: Optional[str] = None,
        max_tokens: int = 512,
    ) -> None:
        self.model_id = model_id or self.DEFAULT_MODEL
        self.max_tokens = max_tokens
        self._client = None  # lazy init

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    "anthropic SDK not installed. Run: pip install anthropic"
                ) from exc
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "ANTHROPIC_API_KEY is not set. Export it before running."
                )
            self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    def generate(self, prompt: str) -> str:
        """Call the Anthropic Messages API and return the response text."""
        client = self._get_client()
        message = client.messages.create(
            model=self.model_id,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


# ---------------------------------------------------------------------------
# OpenAICompatModel
# ---------------------------------------------------------------------------

class OpenAICompatModel(BaseModel):
    """
    Adapter for any OpenAI-compatible API (OpenAI, local vLLM, Ollama, etc.).

    Reads:
        OPENAI_API_KEY      -- required (use "ollama" / "EMPTY" for local)
        OPENAI_BASE_URL     -- override for vLLM / Ollama (optional)

    Args:
        model_id: Model name as the server expects (e.g. "gpt-4o", "llama3").
        max_tokens: Maximum tokens in the response (default 512).
        base_url: Override base URL (takes precedence over env var).
    """

    def __init__(
        self,
        model_id: str = "gpt-4o-mini",
        max_tokens: int = 512,
        base_url: Optional[str] = None,
    ) -> None:
        self.model_id = model_id
        self.max_tokens = max_tokens
        self._base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        self._client = None  # lazy init

    def _get_client(self):
        if self._client is None:
            try:
                import openai  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    "openai SDK not installed. Run: pip install openai"
                ) from exc
            api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
            kwargs: dict = {"api_key": api_key}
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = openai.OpenAI(**kwargs)
        return self._client

    def generate(self, prompt: str) -> str:
        """Call the OpenAI-compatible chat completion endpoint."""
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model_id,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_model(name: str, model_id: Optional[str] = None) -> BaseModel:
    """
    Construct a model adapter by name.

    Args:
        name:     One of "dummy", "claude", "openai".
        model_id: Optional override for the model identifier.

    Returns:
        A BaseModel instance ready to call .generate().
    """
    name = name.lower().strip()
    if name == "dummy":
        return DummyModel()
    if name == "claude":
        return ClaudeModel(model_id=model_id)
    if name in {"openai", "openai-compat"}:
        return OpenAICompatModel(model_id=model_id or "gpt-4o-mini")
    raise ValueError(
        f"Unknown model name '{name}'. Valid choices: dummy, claude, openai."
    )
