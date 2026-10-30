"""Runtime settings, read from the environment (a local .env file is supported)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # optional dependency
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
KB_DIR = DATA_DIR / "knowledge"


@dataclass(frozen=True)
class Settings:
    provider: str = "auto"  # auto | anthropic | openai | offline
    anthropic_model: str = "claude-sonnet-5-5"
    openai_model: str = "gpt-4o-mini"
    top_k_cases: int = 3
    top_k_offers: int = 2
    usd_to_inr: float = 85.0  # approximation used only for budget bucketing
    budget_floor_inr: float = 25_000  # below this a lead is capped at COLD

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "auto").lower(),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", cls.anthropic_model),
            openai_model=os.getenv("OPENAI_MODEL", cls.openai_model),
        )
