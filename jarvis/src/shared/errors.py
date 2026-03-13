from __future__ import annotations


class JarvisError(Exception):
    """Base error for Jarvis domain failures."""


class ContractError(JarvisError):
    """Raised when a contract/schema invariant is violated."""


class ToolError(JarvisError):
    """Raised for tool execution failures."""


class PermissionError(JarvisError):
    """Raised when a call is not permitted by policy."""


class SkillError(JarvisError):
    """Raised for skill loading/runtime failures."""


class SessionError(JarvisError):
    """Raised for session/memory/history failures."""

