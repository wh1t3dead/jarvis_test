from __future__ import annotations

from uuid import UUID

from app.bootstrap import bootstrap_app
from shared.types import Speaker, TranscriptEvent


def main() -> None:
    """
    Stage 3 demo entrypoint.

    Usage:
    - Install in editable mode from `jarvis/`:
      `pip install -e .`
    - Run:
      `jarvis`
      or `python -m app.main`
    """

    app = bootstrap_app()

    # Scenario 1: greeting -> direct answer via LLM router.
    session = app.sessions.create_session(user_id="local-user")
    greeting = TranscriptEvent(
        session_id=session.session_id,
        speaker=Speaker.USER,
        text="hello",
    )
    req_greeting = app.sessions.make_brain_request(session_id=session.session_id, transcript=greeting)
    decision_greeting = app.brain.handle(req_greeting)
    print("=== Scenario 1: greeting (direct answer) ===")
    print(f"Session: {session.session_id}")
    print(f"Request: {UUID(str(req_greeting.request_id))}")
    print(f"Answer: {decision_greeting.final_text}")

    # Scenario 2: builtin repeat_back skill via echo tool.
    repeat = TranscriptEvent(
        session_id=session.session_id,
        speaker=Speaker.USER,
        text="please repeat back: hello jarvis",
    )
    req_repeat = app.sessions.make_brain_request(session_id=session.session_id, transcript=repeat)
    decision_repeat = app.brain.handle(req_repeat)
    if decision_repeat.plan is not None:
        task_repeat = app.sessions.make_task(session_id=session.session_id, goal="repeat_back demo")
        results_repeat = app.executor.execute(plan=decision_repeat.plan, task=task_repeat, tools=app.tools)
    else:
        results_repeat = []
    print("\n=== Scenario 2: repeat_back skill (echo tool) ===")
    print(f"Plan steps: {len(decision_repeat.plan.steps) if decision_repeat.plan else 0}")
    for idx, res in enumerate(results_repeat, start=1):
        print(f"Result {idx}: ok={res.ok}, data={res.data}, error={res.error}")

    # Scenario 3: planner path using uppercase_text.
    planner_req = TranscriptEvent(
        session_id=session.session_id,
        speaker=Speaker.USER,
        text="please uppercase this text",
    )
    req_planner = app.sessions.make_brain_request(session_id=session.session_id, transcript=planner_req)
    decision_planner = app.brain.handle(req_planner)
    task_planner = app.sessions.make_task(session_id=session.session_id, goal="planner uppercase demo")
    results_planner = app.executor.execute(
        plan=decision_planner.plan,
        task=task_planner,
        tools=app.tools,
    )
    print("\n=== Scenario 3: planner (uppercase_text tool) ===")
    print(f"Plan steps: {len(decision_planner.plan.steps) if decision_planner.plan else 0}")
    for idx, res in enumerate(results_planner, start=1):
        print(f"Result {idx}: ok={res.ok}, data={res.data}, error={res.error}")


if __name__ == "__main__":
    main()
