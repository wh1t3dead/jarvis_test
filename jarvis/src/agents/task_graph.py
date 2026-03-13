from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True)
class TaskNode:
    node_id: UUID
    title: str
    depends_on: list[UUID] = field(default_factory=list)


@dataclass(slots=True)
class TaskGraph:
    """
    Minimal task graph scaffolding.

    Stage 1: no scheduling/execution semantics yet; this is a placeholder for future planning.
    """

    nodes: dict[UUID, TaskNode] = field(default_factory=dict)

    def add(self, node: TaskNode) -> None:
        self.nodes[node.node_id] = node

