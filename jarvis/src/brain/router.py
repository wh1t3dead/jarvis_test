from __future__ import annotations

from dataclasses import dataclass

from shared.types import BrainRequest


@dataclass(slots=True)
class BrainRoute:
    """Routing decision produced by the Brain Router."""

    route_id: str
    target: str  # e.g. "planner", "skill", "direct"


class BrainRouter:
    """
    Separates intent/routing from execution.

    Stage 3 uses simple heuristics; future versions can plug in an intent backend.
    """

    def route(self, request: BrainRequest) -> BrainRoute:
        """
        Minimal heuristic routing for Stage 3:

        - "skill" -> builtin repeat_back skill for echo-like commands
        - "direct" -> lightweight handling for greetings
        - "planner" -> default for everything else
        """

        text = (request.transcript.text or "").strip().lower()

        skill = self._match_skill(text)
        if skill is not None:
            return BrainRoute(route_id=skill, target="skill")

        if self._looks_like_greeting(text):
            return BrainRoute(route_id="direct_greeting", target="direct")

        return BrainRoute(route_id="planner_default", target="planner")

    @staticmethod
    def _match_skill(text: str) -> str | None:
        if any(t in text for t in ("repeat back", "repeat", "echo")):
            return "repeat_back"
        return None

    @staticmethod
    def _looks_like_greeting(text: str) -> bool:
        greetings = {"hi", "hello", "hey", "привет"}
        return text in greetings
