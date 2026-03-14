from __future__ import annotations

from agents.planner import PlannerAgent
from brain.llm_router import LLMRouter
from brain.router import BrainRouter
from shared.types import BrainDecision, BrainDecisionKind, BrainRequest, ExecutionPlan
from skills.runtime import SkillRuntime


class BrainOrchestrator:
    """
    Central decision point. Produces BrainDecision; never executes side effects directly.
    """

    def __init__(self, *, router: BrainRouter, skills: SkillRuntime, llm_router: LLMRouter) -> None:
        self._router = router
        self._skills = skills
        self._planner = PlannerAgent()
        self._llm_router = llm_router

    def handle(self, request: BrainRequest) -> BrainDecision:
        route = self._router.route(request)

        if route.target == "skill":
            plan = self._skills.build_plan(skill_name=route.route_id, request=request)
            return BrainDecision(kind=BrainDecisionKind.PLAN, plan=plan)

        if route.target == "planner":
            plan = self._planner.plan(request)
            return BrainDecision(kind=BrainDecisionKind.PLAN, plan=plan)

        # "direct" and any unknown routes → direct answer via LLM router.
        answer = self._llm_router.direct_answer(request=request)
        return BrainDecision(kind=BrainDecisionKind.DIRECT_ANSWER, final_text=answer)


