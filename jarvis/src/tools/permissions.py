from __future__ import annotations

from dataclasses import dataclass

from shared.types import ToolPermission


@dataclass(frozen=True, slots=True)
class PermissionSet:
    permissions: frozenset[ToolPermission]

    def requires(self, perm: ToolPermission) -> bool:
        return perm in self.permissions

