from __future__ import annotations

from shared.types import ExecutionPlan, TaskContext, TaskStepStatus, ToolResult
from tools.registry import ToolRegistry


class ExecutorAgent:
    """
    Executes an ExecutionPlan using only the ToolRegistry.
    """

    def execute(self, *, plan: ExecutionPlan, task: TaskContext, tools: ToolRegistry) -> list[ToolResult]:
        results: list[ToolResult] = []

        for step in plan.steps:
            if step.tool_call is None:
                step.status = TaskStepStatus.SKIPPED
                continue

            step.status = TaskStepStatus.RUNNING

            try:
                result = tools.call(call=step.tool_call, task=task)
            except Exception as exc:  # noqa: BLE001
                step.status = TaskStepStatus.FAILED
                result = ToolResult(
                    call_id=step.tool_call.call_id,
                    tool_name=step.tool_call.tool_name,
                    ok=False,
                    data=None,
                    error=str(exc),
                )
            else:
                if result.ok:
                    step.status = TaskStepStatus.DONE
                else:
                    step.status = TaskStepStatus.FAILED

            results.append(result)

        return results

