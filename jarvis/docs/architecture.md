## Jarvis architecture (Stage 1 skeleton)

Jarvis is a **brain-centered** personal AI assistant with a modular monolith architecture.
This repository currently provides **contracts + skeleton runtime** only (no real LLM/voice/system actions yet).

### Layer overview

- **Voice Layer** (`src/voice/`)
  - Responsible for capturing/playing audio and producing text transcripts.
  - **Does not make decisions** and does not call OS actions directly.
  - Emits `TranscriptEvent` into the system.

- **Brain Layer** (`src/brain/`)
  - The central decision layer. Converts a `BrainRequest` into an `ExecutionPlan`.
  - **Does not execute OS actions** directly; it produces plans/tool calls only.

- **Agent Runtime** (`src/agents/`)
  - Planning/execution scaffolding that can run multi-step plans.
  - Interacts with the world **only via the Tool Registry**.

- **Tools Layer** (`src/tools/`)
  - Strict execution boundary for capabilities (IO, network, OS, integrations).
  - Tools are invoked by `ToolCall` and return `ToolResult`.
  - **Tools never call the Brain back** (one-way boundary).

- **Skills Layer** (`src/skills/`)
  - Bundles behavior/config/manifests that *use tools* to achieve outcomes.
  - Skills are **not tools** and are **not the brain**; they are a separate extension type.

- **Sessions / Memory / Artifacts** (`src/sessions/` + shared models)
  - Session-centric execution: `SessionContext` is first-class.
  - Task-scoped execution: `TaskContext` is first-class.
  - Artifacts are recorded as `ArtifactRecord` (future: files, logs, external references).

- **Safety / Permissions** (`src/shared/safety.py` + `src/tools/permissions.py`)
  - Future-proofed for explicit approval flows.
  - Dangerous actions should eventually be gated by an `ApprovalPolicy`.

### Execution flow (current skeleton)

1. Voice layer produces a `TranscriptEvent`.
2. App wraps it into a `BrainRequest` with `SessionContext`.
3. Brain Orchestrator routes the request and builds an `ExecutionPlan`.
4. Agent Executor runs plan steps by calling tools via `ToolRegistry`.
5. Session manager records transcript/history and any produced artifacts.

### Non-goals for Stage 1

- No UI.
- No distributed services / control plane.
- No marketplace.
- No multi-channel integrations.
- No real LLM provider integration.
- No real voice implementation.
- No concrete system tools (OS/network/etc.).

