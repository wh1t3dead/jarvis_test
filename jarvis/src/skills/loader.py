from __future__ import annotations

from typing import Iterable

from shared.types import SkillManifest


class SkillLoader:
    """
    Loads skill manifests from a source (filesystem, package metadata, etc.).

    Stage 1: no IO; returns an empty set.
    """

    def load_manifests(self) -> Iterable[SkillManifest]:
        return []

