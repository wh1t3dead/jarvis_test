from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import jsonschema

from shared.errors import ContractError
from shared.types import TaskContext, ToolCall, ToolResult, ToolSpec
from tools.base import Tool


@dataclass(slots=True)
class ToolRegistry:
    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        name = tool.spec.name
        if name in self._tools:
            raise ContractError(f"Tool already registered: {name}")
        self._tools[name] = tool

    def list_specs(self) -> list[ToolSpec]:
        return [t.spec for t in self._tools.values()]

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as e:
            raise ContractError(f"Unknown tool: {name}") from e

    def call(self, *, call: ToolCall, task: TaskContext) -> ToolResult:
        tool = self.get(call.tool_name)

        self._validate_payload(
            payload=call.arguments,
            schema=tool.spec.input_schema,
            context=f"input for tool '{tool.spec.name}'",
        )

        result = tool.run(call=call, task=task)

        if not isinstance(result, ToolResult):
            raise ContractError(f"Tool '{tool.spec.name}' returned non-ToolResult instance")

        if result.ok:
            self._validate_payload(
                payload=result.data,
                schema=tool.spec.output_schema,
                context=f"output for tool '{tool.spec.name}'",
            )
        else:
            if not result.error:
                raise ContractError(
                    f"Tool '{tool.spec.name}' returned ok=False without a non-empty error message"
                )

        return result

    @staticmethod
    def _validate_payload(*, payload: Any, schema: dict[str, Any], context: str) -> None:
        """
        Centralized schema check for tool inputs/outputs.

        Semantics:
        - input_schema describes ToolCall.arguments
        - output_schema describes ToolResult.data when ok=True
        """

        if not schema:
            return

        try:
            jsonschema.validate(instance=payload, schema=schema)
        except jsonschema.ValidationError as exc:  # pragma: no cover - message formatting only
            msg = exc.message or "schema validation failed"
            raise ContractError(f"{context} does not conform to schema: {msg}") from exc


