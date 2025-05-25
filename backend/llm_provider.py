"""LLM provider abstraction layer."""

from __future__ import annotations

import os
import httpx
from dataclasses import dataclass
import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    def generate(self, prompt: str) -> str:
        ...


@dataclass
class Settings:
    """Application settings loaded from environment."""

    OPENAI_API_KEY: str | None = None
    HF_API_TOKEN: str | None = None
    MODEL_PROVIDER: str = "local"


def get_settings() -> Settings:
    """Return settings instance (factory for DI)."""

    return Settings(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
        HF_API_TOKEN=os.getenv("HF_API_TOKEN"),
        MODEL_PROVIDER=os.getenv("MODEL_PROVIDER", "local"),
    )


class LocalProvider:
    """Simple local provider stub for tests."""

    def generate(self, prompt: str) -> str:
        """Return a canned response echoing the prompt."""
        return f"pong:{prompt}"


class OpenAIProvider:
    """Call OpenAI API via HTTPX."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def generate(self, prompt: str) -> str:
        api_key = self.settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


class HFAPIProvider:
    """Minimal HuggingFace API provider stub."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def generate(self, prompt: str) -> str:
        token = self.settings.HF_API_TOKEN
        if not token:
            logger.warning("HF_API_TOKEN not configured, returning dummy text")
            return f"hf:{prompt}"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": prompt}
        resp = httpx.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data[0].get("generated_text", "")
        return str(data)


def get_provider(settings: Settings | None = None) -> "LLMProvider":
    """Factory returning provider according to environment."""

    settings = settings or get_settings()
    name = settings.MODEL_PROVIDER.lower()
    if name == "openai":
        return OpenAIProvider(settings)
    if name == "hf_api":
        return HFAPIProvider(settings)
    return LocalProvider()
