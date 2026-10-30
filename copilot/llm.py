"""Pluggable LLM providers. The pipeline works with none configured (offline mode)."""
from __future__ import annotations

import json
import os
import re

from .config import Settings


def _parse_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


class LLM:
    name = "offline"

    def complete_json(self, system: str, user: str) -> dict | None:  # pragma: no cover - interface
        raise NotImplementedError


class AnthropicLLM(LLM):
    def __init__(self, model: str):
        import anthropic  # lazy import: optional dependency

        self.client, self.model = anthropic.Anthropic(), model
        self.name = f"anthropic:{model}"

    def complete_json(self, system: str, user: str) -> dict | None:
        try:
            resp = self.client.messages.create(model=self.model, max_tokens=1500, temperature=0.2,
                                               system=system, messages=[{"role": "user", "content": user}])
            return _parse_json("".join(b.text for b in resp.content if getattr(b, "type", "") == "text"))
        except Exception:
            return None


class OpenAILLM(LLM):
    def __init__(self, model: str):
        from openai import OpenAI  # lazy import: optional dependency

        self.client, self.model = OpenAI(), model
        self.name = f"openai:{model}"

    def complete_json(self, system: str, user: str) -> dict | None:
        try:
            resp = self.client.chat.completions.create(
                model=self.model, temperature=0.2, response_format={"type": "json_object"},
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
            return _parse_json(resp.choices[0].message.content or "")
        except Exception:
            return None


def get_llm(settings: Settings) -> LLM | None:
    """Return a provider instance or None (offline). Never raises."""
    choice = settings.provider
    try:
        if choice in ("anthropic", "auto") and os.getenv("ANTHROPIC_API_KEY"):
            return AnthropicLLM(settings.anthropic_model)
        if choice in ("openai", "auto") and os.getenv("OPENAI_API_KEY"):
            return OpenAILLM(settings.openai_model)
    except Exception:
        return None
    return None
