"""Configuration management — API keys, model selection, backend routing."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)


class AnalysisProvider(str, Enum):
    """Which vision LLM to use for watermark analysis."""

    CLAUDE = "claude"
    OPENAI = "openai"


class InpaintBackend(str, Enum):
    """Where inpainting runs — local or remote."""

    LOCAL = "local"
    REPLICATE = "replicate"
    MODAL = "modal"


@dataclass
class Config:
    """Runtime configuration for the unwatermark pipeline."""

    # API keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    replicate_api_token: str = ""

    # Provider selection
    analysis_provider: AnalysisProvider = AnalysisProvider.CLAUDE
    analysis_model: str = "claude-sonnet-4-20250514"
    inpaint_backend: InpaintBackend = InpaintBackend.LOCAL

    # Processing
    use_ai: bool = True
    default_strategy: str | None = None
    blend_margin: int = 20
    lama_model_path: str | None = None

    @property
    def has_anthropic_key(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_replicate_token(self) -> bool:
        return bool(self.replicate_api_token)

    @property
    def can_use_ai(self) -> bool:
        """Check if AI analysis is possible with current config."""
        if not self.use_ai:
            return False
        if self.analysis_provider == AnalysisProvider.CLAUDE:
            return self.has_anthropic_key
        if self.analysis_provider == AnalysisProvider.OPENAI:
            return self.has_openai_key
        return False


def load_config(**overrides) -> Config:
    """Load config from environment variables, with optional overrides."""
    config = Config(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        replicate_api_token=os.getenv("REPLICATE_API_TOKEN", "") or os.getenv("REPLICATE_API", ""),
        analysis_provider=AnalysisProvider(
            os.getenv("UNWATERMARK_ANALYSIS_PROVIDER", "claude")
        ),
        analysis_model=os.getenv(
            "UNWATERMARK_ANALYSIS_MODEL", "claude-sonnet-4-20250514"
        ),
        inpaint_backend=InpaintBackend(
            os.getenv("UNWATERMARK_INPAINT_BACKEND", "local")
        ),
        lama_model_path=os.getenv("UNWATERMARK_LAMA_MODEL_PATH"),
    )

    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return config
