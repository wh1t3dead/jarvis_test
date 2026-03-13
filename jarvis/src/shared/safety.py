from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ApprovalDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class ApprovalRequest(BaseModel):
    """Represents a future approval gate request for potentially dangerous actions."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    reason: str
    policy_id: str = "default"
    risk_level: str = "unknown"
    details: dict[str, object] = Field(default_factory=dict)


class ApprovalResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    decision: ApprovalDecision
    request: Optional[ApprovalRequest] = None


class ApprovalPolicy:
    """Evaluates whether a proposed action should run, be denied, or require approval."""

    def evaluate(self, *, action: object) -> ApprovalResult:
        # Stage 1: no dangerous actions exist yet; default to "allow".
        return ApprovalResult(decision=ApprovalDecision.ALLOW)

