from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from shared.errors import SessionError
from shared.types import BrainRequest, SessionContext, TaskContext, TranscriptEvent
from sessions.history import SessionHistory


@dataclass(slots=True)
class SessionManager:
    _sessions: dict[UUID, SessionContext] = field(default_factory=dict)
    _history: dict[UUID, SessionHistory] = field(default_factory=dict)

    def create_session(self, *, user_id: Optional[str] = None, locale: str = "en-US") -> SessionContext:
        ctx = SessionContext(user_id=user_id, locale=locale)
        self._sessions[ctx.session_id] = ctx
        self._history[ctx.session_id] = SessionHistory(session_id=ctx.session_id)
        return ctx

    def get_session(self, session_id: UUID) -> SessionContext:
        try:
            return self._sessions[session_id]
        except KeyError as e:
            raise SessionError(f"Unknown session: {session_id}") from e

    def history(self, session_id: UUID) -> SessionHistory:
        try:
            return self._history[session_id]
        except KeyError as e:
            raise SessionError(f"No history for session: {session_id}") from e

    def append_transcript(self, event: TranscriptEvent) -> None:
        self.history(event.session_id).append(event)

    def make_task(self, *, session_id: UUID, goal: Optional[str] = None) -> TaskContext:
        session = self.get_session(session_id)
        return TaskContext(session_id=session.session_id, goal=goal)

    def make_brain_request(self, *, session_id: UUID, transcript: TranscriptEvent) -> BrainRequest:
        session = self.get_session(session_id)
        if transcript.session_id != session_id:
            raise SessionError(
                f"Transcript session_id {transcript.session_id} does not match "
                f"session_id {session_id}"
            )
        self.append_transcript(transcript)
        return BrainRequest(session=session, transcript=transcript)

