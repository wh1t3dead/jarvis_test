## Project map (Stage 1)

This document maps the current code layout and highlights architectural influences.

### Source layout

- `src/app/`: application entrypoints and wiring
- `src/shared/`: common types/contracts, errors, events, config, safety
- `src/voice/`: voice layer skeleton (no audio implementation)
- `src/brain/`: brain orchestrator + routing skeleton
- `src/agents/`: planner/executor scaffolding + task graph/context
- `src/tools/`: tool contracts, registry, permissions boundary
- `src/skills/`: skill manifests + loader/runtime skeleton
- `src/sessions/`: session manager + history scaffolding
- `src/integrations/`: placeholder for future integrations (empty in Stage 1)
- `tests/`: placeholder tests for contracts and wiring

### Reference influences (architecture only, not code copying)

Reference files in `reference/` were used strictly as **architectural ориентиры** (roles, boundaries, contracts, naming ideas).
They were **not** used as a source for literal code copying.

- **`config.rs`**
  - Influence: centralized configuration idea and subsystem boundaries.
  - Outcome: `src/shared/config.py` introduces typed config + defaults and leaves room for per-subsystem settings.

- **`intent.rs`**
  - Influence: separation of intent/routing from raw execution.
  - Outcome: `src/brain/router.py` exists as a separate component from `tools/` and does not execute side effects.

- **`_base.py`**
  - Influence: typed executable contracts with metadata + schema-based validation.
  - Outcome: `ToolSpec`, `ToolCall`, `ToolResult` and strict tool base contract in `src/tools/base.py`.

- **`__init__.py`**
  - Influence: skills as a first-class extension concept distinct from tools/brain.
  - Outcome: `SkillManifest` schema and `src/skills/*` runtime scaffolding.

- **`VISION.md`**
  - Influence: session-centric, security-first, control-plane mindset (without building the control plane now).
  - Outcome: `SessionContext`, `TaskContext`, artifacts models, and explicit safety/permission scaffolding.

- **`core.py`**
  - Influence: a single coordinating runtime loop (central “station”) that orchestrates decisions and execution.
  - Outcome: `BrainOrchestrator` as the central decision point coordinating routing and plan generation.

