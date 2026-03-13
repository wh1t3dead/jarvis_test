from __future__ import annotations

from shared.types import TaskContext, ToolCall, ToolPermission, ToolResult, ToolSpec
from tools.base import Tool


class EchoTool(Tool):
    """
    Safe demo tool used for Stage 2 execution loop.

    - input:  {"text": string}
    - output: {"echo": string}
    """

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="echo",
            description="Echoes the provided text back to the caller.",
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

    def run(self, *, call: ToolCall, task: TaskContext) -> ToolResult:
        _ = task
        text = str(call.arguments.get("text", ""))
        return ToolResult(
            call_id=call.call_id,
            tool_name=self.spec.name,
            ok=True,
            data={"echo": text},
        )

