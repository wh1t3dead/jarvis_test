from __future__ import annotations

from shared.types import (
    BrainDecision,
    BrainDecisionKind,
    BrainRequest,
    ExecutionPlan,
    SessionContext,
    Speaker,
    TaskContext,
    TaskStep,
    TaskStepStatus,
    ToolCall,
    ToolSpec,
    TranscriptEvent,
)
from agents.executor import ExecutorAgent
from agents.planner import PlannerAgent
from app.bootstrap import bootstrap_app
from brain.router import BrainRouter
from skills.loader import SkillLoader
from skills.runtime import SkillRuntime
from tools.echo import EchoTool
from tools.registry import ToolRegistry


def _make_request(text: str) -> BrainRequest:
    session = SessionContext()
    transcript = TranscriptEvent(session_id=session.session_id, speaker=Speaker.USER, text=text)
    return BrainRequest(session=session, transcript=transcript)


def test_brain_router_routes_to_skill_direct_and_planner() -> None:
    router = BrainRouter()

    skill_req = _make_request("please repeat back this text")
    direct_req = _make_request("hello")
    ru_direct_req = _make_request("привет")
    uppercase_req = _make_request("please uppercase this text")
    count_req = _make_request("please count words here")
    planner_req = _make_request("do something more complex")
    short_command_req_1 = _make_request("open browser")
    short_command_req_2 = _make_request("list files")

    skill_route = router.route(skill_req)
    direct_route = router.route(direct_req)
    ru_direct_route = router.route(ru_direct_req)
    uppercase_route = router.route(uppercase_req)
    count_route = router.route(count_req)
    planner_route = router.route(planner_req)
    short_command_route_1 = router.route(short_command_req_1)
    short_command_route_2 = router.route(short_command_req_2)

    assert skill_route.target == "skill"
    assert skill_route.route_id == "repeat_back"

    assert direct_route.target == "direct"
    assert ru_direct_route.target == "direct"

    assert uppercase_route.target == "planner"
    assert count_route.target == "planner"
    assert planner_route.target == "planner"
    assert short_command_route_1.target == "planner"
    assert short_command_route_2.target == "planner"


def test_planner_agent_produces_non_empty_plan() -> None:
    planner = PlannerAgent()
    request = _make_request("plan something")

    plan = planner.plan(request)

    assert isinstance(plan, ExecutionPlan)
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_call is not None
    assert plan.steps[0].tool_call.tool_name == "echo"


def test_executor_executes_step_via_tool_registry() -> None:
    tools = ToolRegistry()
    tools.register(EchoTool())

    session = SessionContext()
    task = TaskContext(session_id=session.session_id, goal="executor test")

    request = BrainRequest(
        session=session,
        transcript=TranscriptEvent(
            session_id=session.session_id,
            speaker=Speaker.USER,
            text="hello executor",
        ),
    )

    tool_call = ToolCall(tool_name="echo", arguments={"text": request.transcript.text})
    step = TaskStep(title="executor echo", tool_call=tool_call)
    plan = ExecutionPlan(request_id=request.request_id, steps=[step])

    executor = ExecutorAgent()
    results = executor.execute(plan=plan, task=task, tools=tools)

    assert len(results) == 1
    assert results[0].ok is True
    assert results[0].data == {"echo": "hello executor"}
    assert plan.steps[0].status == TaskStepStatus.DONE


def test_skill_runtime_repeat_back_builds_plan_with_echo_tool() -> None:
    tools = ToolRegistry()
    tools.register(EchoTool())
    skills = SkillRuntime(loader=SkillLoader(), tools=tools)

    request = _make_request("repeat back this")

    plan = skills.build_plan(skill_name="repeat_back", request=request)

    assert len(plan.steps) == 1
    step = plan.steps[0]
    assert step.tool_call is not None
    assert step.tool_call.tool_name == "echo"


def test_end_to_end_demo_flow() -> None:
    app = bootstrap_app()

    session = app.sessions.create_session(user_id="test-user")
    transcript = TranscriptEvent(
        session_id=session.session_id,
        speaker=Speaker.USER,
        text="please repeat back: hello world",
    )

    request = app.sessions.make_brain_request(session_id=session.session_id, transcript=transcript)
    decision = app.brain.handle(request)

    assert isinstance(decision, BrainDecision)
    assert decision.kind == BrainDecisionKind.PLAN
    assert decision.plan is not None

    task = app.sessions.make_task(session_id=session.session_id, goal="end-to-end demo")
    results = app.executor.execute(plan=decision.plan, task=task, tools=app.tools)

    assert len(results) == 1
    assert results[0].data == {"echo": "please repeat back: hello world"}


def test_executor_marks_failed_step_and_continues_on_error() -> None:
    class FailingEcho(EchoTool):
        @property
        def spec(self) -> ToolSpec:  # type: ignore[override]
            base = super().spec
            return ToolSpec(
                name="echo_fail",
                description="Failing echo for tests",
                input_schema=base.input_schema,
                output_schema=base.output_schema,
                permissions=base.permissions,
            )

        def run(self, *, call: ToolCall, task: TaskContext):  # type: ignore[override]
            _ = (call, task)
            raise RuntimeError("tool failure")

    tools = ToolRegistry()
    tools.register(FailingEcho())
    tools.register(EchoTool())

    session = SessionContext()
    task = TaskContext(session_id=session.session_id, goal="executor failure test")

    failing_call = ToolCall(tool_name="echo_fail", arguments={"text": "first"})
    ok_call = ToolCall(tool_name="echo", arguments={"text": "second"})

    failing_step = TaskStep(title="failing step", tool_call=failing_call)
    ok_step = TaskStep(title="ok step", tool_call=ok_call)

    plan = ExecutionPlan(request_id=_make_request("irrelevant").request_id, steps=[failing_step, ok_step])

    executor = ExecutorAgent()
    results = executor.execute(plan=plan, task=task, tools=tools)

    assert len(results) == 2

    first, second = results
    assert first.ok is False
    assert "tool failure" in (first.error or "")
    assert failing_step.status == TaskStepStatus.FAILED

    assert second.ok is True
    assert second.data == {"echo": "second"}
    assert ok_step.status == TaskStepStatus.DONE
