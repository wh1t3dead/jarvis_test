from __future__ import annotations

from abc import ABC, abstractmethod

from shared.types import TaskContext, ToolCall, ToolResult, ToolSpec


class Tool(ABC):
    """
    Strict tool boundary.

    - Called by agents via ToolRegistry.
    - Must be deterministic with respect to provided input/context (as much as the capability allows).
    - Must not call Brain components back.
    """

    @property
    @abstractmethod
    def spec(self) -> ToolSpec:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def run(self, *, call: ToolCall, task: TaskContext) -> ToolResult:  # pragma: no cover
        raise NotImplementedError

