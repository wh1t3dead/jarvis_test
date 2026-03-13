from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from shared.types import TranscriptEvent


@dataclass(slots=True)
class SessionHistory:
    session_id: UUID
    transcript: list[TranscriptEvent] = field(default_factory=list)

    def append(self, event: TranscriptEvent) -> None:
        self.transcript.append(event)

