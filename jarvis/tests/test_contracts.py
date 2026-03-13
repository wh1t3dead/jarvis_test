from __future__ import annotations

import uuid

import pytest

from shared.errors import ContractError, SessionError
from shared.types import (
    BrainRequest,
    SessionContext,
    SkillManifest,
    Speaker,
    TaskContext,
    ToolCall,
    ToolPermission,
    ToolResult,
    ToolSpec,
    TranscriptEvent,
)
from sessions.manager import SessionManager
from tools.base import Tool
from tools.registry import ToolRegistry


class _EchoTool(Tool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="_echo",
            description="Echoes a string",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
                "additionalProperties": False,
            },
            output_schema={
                "type": "object",
                "properties": {"echo": {"type": "string"}},
                "required": ["echo"],
                "additionalProperties": False,
            },
            permissions=[ToolPermission.READ],
        )

    def run(self, *, call: ToolCall, task: TaskContext) -> ToolResult:  # pragma: no cover - behavior tested via registry
        _ = task
        value = call.arguments["text"]
        return ToolResult(call_id=call.call_id, tool_name=self.spec.name, ok=True, data={"echo": value})


def test_contracts_smoke() -> None:
    session = SessionContext()
    transcript = TranscriptEvent(session_id=session.session_id, speaker=Speaker.USER, text="hi")
    req = BrainRequest(session=session, transcript=transcript)
    assert req.session.session_id == session.session_id

    manifest = SkillManifest(
        name="example-skill",
        version="0.0.0",
        description="example",
        entrypoint="skills.example:ExampleSkill",
    )
    assert manifest.name == "example-skill"


def test_tool_registry_valid_call_passes_validation() -> None:
    registry = ToolRegistry()
    tool = _EchoTool()
    registry.register(tool)

    session = SessionContext()
    task = TaskContext(session_id=session.session_id)
    call = ToolCall(tool_name=tool.spec.name, arguments={"text": "hello"})

    result = registry.call(call=call, task=task)

    assert result.ok is True
    assert result.data == {"echo": "hello"}


def test_tool_registry_invalid_arguments_raise_contract_error_before_run() -> None:
    registry = ToolRegistry()
    tool = _EchoTool()
    registry.register(tool)

    session = SessionContext()
    task = TaskContext(session_id=session.session_id)
    call = ToolCall(tool_name=tool.spec.name, arguments={"wrong": "field"})

    with pytest.raises(ContractError):
        registry.call(call=call, task=task)


def test_tool_registry_invalid_success_output_raises_contract_error() -> None:
    class _BadTool(_EchoTool):
        def run(self, *, call: ToolCall, task: TaskContext) -> ToolResult:  # pragma: no cover
            _ = (call, task)
            # Violates output_schema by returning wrong shape
            return ToolResult(
                call_id=uuid.uuid4(),
                tool_name=self.spec.name,
                ok=True,
                data={"unexpected": "value"},
            )

    registry = ToolRegistry()
    tool = _BadTool()
    registry.register(tool)

    session = SessionContext()
    task = TaskContext(session_id=session.session_id)
    call = ToolCall(tool_name=tool.spec.name, arguments={"text": "hello"})

    with pytest.raises(ContractError):
        registry.call(call=call, task=task)


def test_tool_registry_error_without_message_is_invalid() -> None:
    class _ErrorTool(_EchoTool):
        def run(self, *, call: ToolCall, task: TaskContext) -> ToolResult:  # pragma: no cover
            _ = (call, task)
            return ToolResult(
                call_id=uuid.uuid4(),
                tool_name=self.spec.name,
                ok=False,
                data=None,
                error="",
            )

    registry = ToolRegistry()
    tool = _ErrorTool()
    registry.register(tool)

    session = SessionContext()
    task = TaskContext(session_id=session.session_id)
    call = ToolCall(tool_name=tool.spec.name, arguments={"text": "hello"})

    with pytest.raises(ContractError):
        registry.call(call=call, task=task)


def test_session_manager_rejects_mismatched_transcript_session() -> None:
    manager = SessionManager()
    session = manager.create_session()

    other_session = SessionContext()
    transcript = TranscriptEvent(
        session_id=other_session.session_id,
        speaker=Speaker.USER,
        text="hi",
    )

    with pytest.raises(SessionError):
        manager.make_brain_request(session_id=session.session_id, transcript=transcript)


def test_brain_request_validator_rejects_session_vs_transcript_mismatch() -> None:
    session = SessionContext()
    other_session = SessionContext()

    transcript = TranscriptEvent(
        session_id=other_session.session_id,
        speaker=Speaker.USER,
        text="hi",
    )

    with pytest.raises(Exception):
        BrainRequest(session=session, transcript=transcript)


def test_brain_request_validator_rejects_task_session_mismatch() -> None:
    session = SessionContext()
    transcript = TranscriptEvent(
        session_id=session.session_id,
        speaker=Speaker.USER,
        text="hi",
    )
    task = TaskContext(session_id=uuid.uuid4())

    with pytest.raises(Exception):
        BrainRequest(session=session, transcript=transcript, task=task)

