from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from shared.errors import SkillError
from shared.types import BrainRequest, ExecutionPlan, SkillManifest, TaskStep, ToolCall
from skills.loader import SkillLoader
from tools.registry import ToolRegistry


@dataclass(slots=True)
class SkillRuntime:
    """
    Runtime for skill discovery and lightweight builtin skill execution planning.

    Stage 3:
    - still no dynamic import/exec
    - includes builtin skill: "repeat_back"
    """

    loader: SkillLoader
    tools: ToolRegistry
    _manifests: list[SkillManifest] | None = None

    def manifests(self) -> Iterable[SkillManifest]:
        if self._manifests is None:
            self._manifests = list(self.loader.load_manifests())
        return list(self._manifests)

    def build_plan(self, *, skill_name: str, request: BrainRequest) -> ExecutionPlan:
        """
        Translate a skill invocation into an ExecutionPlan.
        """

        if skill_name == "repeat_back":
            call = ToolCall(tool_name="echo", arguments={"text": request.transcript.text})
            step = TaskStep(title="Skill repeat_back via echo", tool_call=call)
            return ExecutionPlan(request_id=request.request_id, steps=[step])

        raise SkillError(f"Unknown skill: {skill_name}")
