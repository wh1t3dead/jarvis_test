from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Speaker(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class TranscriptEvent(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    speaker: Speaker
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    session_id: UUID = Field(default_factory=uuid4)
    user_id: Optional[str] = None
    locale: str = "en-US"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ArtifactRecord(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    artifact_id: UUID = Field(default_factory=uuid4)
    kind: str
    uri: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    task_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    goal: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    artifacts: list[ArtifactRecord] = Field(default_factory=list)


class BrainRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    request_id: UUID = Field(default_factory=uuid4)
    session: SessionContext
    transcript: TranscriptEvent
    task: Optional[TaskContext] = None
    constraints: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _ensure_session_invariants(self) -> "BrainRequest":
        if self.session.session_id != self.transcript.session_id:
            raise ValueError("BrainRequest.session and transcript.session_id must match")

        if self.task is not None and self.task.session_id != self.session.session_id:
            raise ValueError("BrainRequest.task.session_id must match session.session_id")

        return self


class ToolPermission(str, Enum):
    """High-level permission categories (Stage 1)."""

    READ = "read"
    WRITE = "write"
    NETWORK = "network"
    OS = "os"


class ToolSpec(BaseModel):
    """Tool metadata and schema contract for a callable capability."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    permissions: list[ToolPermission] = Field(default_factory=list)


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    call_id: UUID = Field(default_factory=uuid4)
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ToolResult(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    call_id: UUID
    tool_name: str
    ok: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskStep(BaseModel):
    model_config = ConfigDict(extra="allow")

    step_id: UUID = Field(default_factory=uuid4)
    title: str
    tool_call: Optional[ToolCall] = None
    status: TaskStepStatus = TaskStepStatus.PENDING
    notes: Optional[str] = None


class ExecutionPlan(BaseModel):
    model_config = ConfigDict(extra="allow")

    plan_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    steps: list[TaskStep] = Field(default_factory=list)


class BrainDecisionKind(str, Enum):
    DIRECT_ANSWER = "direct_answer"
    PLAN = "plan"


class BrainDecision(BaseModel):
    """
    Result of a Brain orchestration step.

    - kind == DIRECT_ANSWER → final_text is populated, plan is None
    - kind == PLAN → plan is populated, final_text may be None
    """

    model_config = ConfigDict(extra="forbid")

    kind: BrainDecisionKind
    plan: Optional[ExecutionPlan] = None
    final_text: Optional[str] = None

class SkillManifest(BaseModel):
    """Declarative metadata for a skill package (Stage 1 schema)."""

    model_config = ConfigDict(extra="forbid")

    name: str
    version: str
    description: str = ""
    entrypoint: str  # e.g. "skills.example:ExampleSkill"
    tools_required: list[str] = Field(default_factory=list)
    permissions_required: list[ToolPermission] = Field(default_factory=list)

