from __future__ import annotations

from agents.planner import PlannerAgent
from brain.router import BrainRouter
from shared.types import BrainRequest, ExecutionPlan
from skills.runtime import SkillRuntime


class BrainOrchestrator:
    """
    Central decision point. Produces plans; never executes side effects directly.
    """

    def __init__(self, *, router: BrainRouter, skills: SkillRuntime) -> None:
        self._router = router
        self._skills = skills
        self._planner = PlannerAgent()

    def handle(self, request: BrainRequest) -> ExecutionPlan:
        route = self._router.route(request)

        if route.target == "skill":
            return self._skills.build_plan(skill_name=route.route_id, request=request)

        if route.target == "planner":
            return self._planner.plan(request)

        # "direct" and any unknown routes map to a lightweight empty plan.
        return ExecutionPlan(request_id=request.request_id, steps=[])

