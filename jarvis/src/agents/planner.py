from __future__ import annotations

from shared.types import BrainRequest, ExecutionPlan, TaskStep, ToolCall


class PlannerAgent:
    """
    Produces an ExecutionPlan from a BrainRequest.
    """

    def plan(self, request: BrainRequest) -> ExecutionPlan:
        """
        Minimal planning for Stage 3.

        Chooses between a few safe tools using simple string heuristics.
        """

        text = (request.transcript.text or "").lower()

        if "count words" in text:
            call = ToolCall(tool_name="word_count", arguments={"text": request.transcript.text})
            title = "Planner word_count"
        elif "uppercase" in text or "upper case" in text:
            call = ToolCall(tool_name="uppercase_text", arguments={"text": request.transcript.text})
            title = "Planner uppercase_text"
        else:
            call = ToolCall(tool_name="echo", arguments={"text": request.transcript.text})
            title = "Planner echo"

        step = TaskStep(title=title, tool_call=call)
        return ExecutionPlan(request_id=request.request_id, steps=[step])

