from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class AppConfig(BaseModel):
    """Centralized app config with safe defaults (Stage 1)."""

    model_config = ConfigDict(extra="ignore")

    app_name: str = "jarvis"
    log_level: LogLevel = "INFO"

    # Safety-related knobs (future: per-tool/category policies)
    approval_mode: Literal["off", "prompt", "strict"] = "prompt"


def default_config() -> AppConfig:
    return AppConfig()

