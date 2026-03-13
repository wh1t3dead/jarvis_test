from __future__ import annotations

from shared.types import BrainRequest, ExecutionPlan, TaskStep, ToolCall


class PlannerAgent:
    """
    Produces an ExecutionPlan from a BrainRequest.

    Stage 1: returns an empty plan. Future: LLM-backed planning + skill selection + constraints.
    """

    def plan(self, request: BrainRequest) -> ExecutionPlan:
        """
        Minimal planning for Stage 2.

        For now, produce a single-step plan that calls the safe demo "echo" tool
        with the full user transcript as input.
        """

        call = ToolCall(tool_name="echo", arguments={"text": request.transcript.text})
        step = TaskStep(title="Planner echo", tool_call=call)
        return ExecutionPlan(request_id=request.request_id, steps=[step])

