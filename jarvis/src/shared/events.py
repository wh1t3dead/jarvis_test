from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    TRANSCRIPT = "transcript"
    SYSTEM = "system"


class BaseEvent(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    event_type: EventType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

