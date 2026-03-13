from __future__ import annotations

from uuid import UUID

from app.bootstrap import bootstrap_app
from shared.types import Speaker, TranscriptEvent


def main() -> None:
    """
    Stage 1 entrypoint.

    Usage:
    - Install in editable mode from `jarvis/`:
      `pip install -e .`
    - Run:
      `jarvis`
      or `python -m app.main`
    """

    app = bootstrap_app()

    session = app.sessions.create_session(user_id="local-user")

    # Demo input that should route through the builtin repeat_back skill.
    transcript = TranscriptEvent(
        session_id=session.session_id,
        speaker=Speaker.USER,
        text="please repeat back: hello jarvis",
    )

    request = app.sessions.make_brain_request(session_id=session.session_id, transcript=transcript)
    plan = app.brain.handle(request)

    task = app.sessions.make_task(session_id=session.session_id, goal="demo execution loop")
    results = app.executor.execute(plan=plan, task=task, tools=app.tools)

    print(f"Session: {session.session_id}")
    print(f"Request: {UUID(str(request.request_id))}")
    print(f"Plan steps: {len(plan.steps)}")
    for idx, res in enumerate(results, start=1):
        print(f"Result {idx}: ok={res.ok}, data={res.data}, error={res.error}")


if __name__ == "__main__":
    main()

