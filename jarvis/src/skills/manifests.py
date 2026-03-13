from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from shared.types import SkillManifest, ToolPermission


class SkillManifestFile(BaseModel):
    """
    Wrapper schema for on-disk manifests.

    Stage 1: keeps the contract explicit; loader decides how/where manifests are stored.
    """

    model_config = ConfigDict(extra="forbid")

    manifest: SkillManifest
    enabled: bool = True
    permissions_granted: list[ToolPermission] = Field(default_factory=list)

