"""LLM provider abstraction layer."""

from __future__ import annotations

import os
import httpx
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings loaded from environment."""

    OPENAI_API_KEY: str | None = None


def get_settings() -> Settings:
    """Return settings instance (factory for DI)."""

    return Settings(OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"))


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
