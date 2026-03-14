from __future__ import annotations

import logging

from agents.executor import ExecutorAgent
from brain.llm_router import LLMRouter, StubLLMProvider
from brain.orchestrator import BrainOrchestrator
from brain.router import BrainRouter
from sessions.manager import SessionManager
from shared.config import AppConfig, default_config
from skills.loader import SkillLoader
from skills.runtime import SkillRuntime
from tools.echo import EchoTool
from tools.registry import ToolRegistry
from tools.uppercase_text import UppercaseTextTool
from tools.word_count import WordCountTool


class JarvisApp:
    """Dependency container for the modular monolith."""

    def __init__(self, *, config: AppConfig) -> None:
        self.config = config

        self.sessions = SessionManager()
        self.tools = ToolRegistry()

        # Register safe demo tools
        self.tools.register(EchoTool())
        self.tools.register(UppercaseTextTool())
        self.tools.register(WordCountTool())

        self.skills = SkillRuntime(loader=SkillLoader(), tools=self.tools)

        self.brain_router = BrainRouter()
        llm_stub = StubLLMProvider()
        llm_router = LLMRouter(default_provider=llm_stub)
        self.brain = BrainOrchestrator(router=self.brain_router, skills=self.skills, llm_router=llm_router)

        self.executor = ExecutorAgent()


def bootstrap_app(config: AppConfig | None = None) -> JarvisApp:
    cfg = config or default_config()
    logging.basicConfig(level=getattr(logging, cfg.log_level))
    return JarvisApp(config=cfg)

