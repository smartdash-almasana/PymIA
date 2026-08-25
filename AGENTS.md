# PymIA / SmartPyme — Agent Startup Contract

## Status

Mandatory repository-level startup contract for AI-assisted work.

This file is the first document an assistant, agent, coding model, auditor, or human operator must read before proposing or changing work in this repository.

## Purpose

Prevent methodological drift.

PymIA / SmartPyme must not advance from loose prompts, model enthusiasm, roadmap momentum, or isolated implementation ideas.

All work must preserve the written architecture, methodology, ADR trail, contracts, tests, evidence, and checkpoints.

## Mandatory startup sequence

Before operating, the agent must:

1. Read this `AGENTS.md`.
2. Check repository state:
   - current branch;
   - `git status --short`;
   - recent commits when relevant.
3. Read the latest relevant checkpoint.
4. Read applicable methodology / ADR / source architecture documents.
5. Identify the layer being touched:
   - Architecture;
   - ADR;
   - CapabilitySpec;
   - ModuleContract;
   - TaskSpec;
   - tests;
   - code;
   - evidence;
   - checkpoint;
   - learning candidate.
6. Separate explicitly:
   - certified facts;
   - hypotheses;
   - gaps;
   - next methodological step.
7. State stop conditions before implementation.

If the architectural source is missing, stop.

If the technical contract is missing, do not implement code yet.

If evidence is missing, do not declare PASS.

## Development chain

The only valid development chain is:

```text
Architectural DNA / philosophy / methodology
→ ADR
→ CapabilitySpec
→ ModuleContract
→ TaskSpec
→ acceptance test
→ code
→ evidence
→ checkpoint
→ Learning candidate, only if applicable
```

A roadmap item does not become code by itself.

A conversation does not become policy by itself.

Evidence does not become LearningMemory by itself.

A document does not enter the system as a real capability until it has:

```text
contract + test + evidence
```

## Meaning of “advance”

When the user says “advance”, it means:

```text
advance inside the method
```

It never means:

```text
skip architecture;
skip ADR;
skip contracts;
skip tests;
skip evidence;
open a feature by intuition;
touch production code without authorization.
```

## PASS rules

Do not declare PASS unless there is evidence.

Acceptable evidence includes:

- local command output observed directly by the acting agent;
- external/local command output explicitly reported by the user or another tool, identified as such;
- GitHub/CI evidence, if available;
- documentary gate evidence for documentation-only changes.

If tests were run by Gemini, Codex, local PowerShell, CI, or another actor, say so.

Do not write “I ran tests” unless this agent actually ran them.

## Product language rule

Do not call something “product” if it is still one of:

- service assisted by humans;
- protocol;
- pilot;
- internal capability;
- documentary checkpoint;
- controlled demo;
- technical slice;
- hypothesis.

Prefer accurate language:

- service assisted;
- operational protocol;
- capability under test;
- pilot flow;
- internal module;
- documented checkpoint.

## Role of the PyME owner

The PyME owner is not only an uploader of Excel files.

The owner provides two kinds of input:

1. Data:
   - files;
   - columns;
   - sales;
   - costs;
   - extracts;
   - invoices;
   - stock;
   - operational records.
2. Operational meaning:
   - what worries them;
   - what period matters;
   - what a column means;
   - what real process sits behind a file;
   - what data is missing but exists elsewhere;
   - what decision needs support.

If the system lacks evidence or meaning, the correct state is not silence.

The correct state is a visible GAP, BLOCKED, NEEDS_EVIDENCE, or methodological stop, depending on the implemented contract.

## Service 1 product axis

Servicio 1 is not an operator-assisted service as its product definition.

Servicio 1 is a PyME operational diagnosis system governed by:

```text
owner pain
→ conversation
→ anamnesis
→ pathology candidates
→ required evidence
→ deterministic skills / microservices
→ diagnosis
→ treatment
→ deliverables
```

The operator, CLI, QA, runbooks, manifests, and human review gates are internal infrastructure, development scaffolding, QA support, or exceptional support layers.

They are not the normal product actor and must not govern the product narrative.

Core rules:

- The IA conversa.
- PymIA computa.
- The pathology catalog orients diagnosis.
- Deterministic tools produce evidence.
- The PyME owner provides data and operational meaning.
- No diagnosis may be treated as final without case evidence.

## Service 1 LLM language mediator rule

For Servicio 1, the LLM layer is only a linguistic and semantic mediator between the PyME owner and PymIA.

PymIA remains the deterministic computational authority for case state, gaps, required evidence, questions, skills, tools, structured outputs, diagnoses, treatments, and deliverables.

The LLM may normalize owner language into PymIA-consumable input and may verbalize PymIA-generated outputs in owner-facing language.

The LLM must not change, invent, override, or independently decide case state, evidence requirements, tool selection, diagnosis, treatment, or delivery scope.

Operational rule:

```text
PymIA decides.
The LLM communicates.
```

Default integration method for new observable capabilities:

```text
Feature Flag
+
Shadow Mode
+
Observational artifact
+
Early integration
+
Gradual promotion
```

If a capability can observe without changing runtime decisions, it must enter first in `SHADOW_MODE`.

Only changes that alter critical runtime decisions require isolated implementation before integration.

Every new Service 1 capability must answer:

- What pathology does it help detect?
- What evidence does it require?
- What skills or microservices does it use?
- What diagnosis does it enable?
- What treatment or deliverable does it produce?

Do not change this Service 1 axis unless there is strong technical evidence and an explicit architectural update.

## Layer separation

The following layers must remain separate:

```text
Execution ≠ Evidence ≠ Learning ≠ Architecture
```

Definitions:

- Execution: what was done.
- Evidence: what proves or records what happened.
- Learning: governed candidate or approved learning derived from evidence.
- Architecture: stable identity, constraints, ADRs, contracts, and methodology.

Do not convert one layer into another automatically.

## Stop conditions

Stop before implementation if:

- the architectural source is missing;
- the applicable ADR is missing and the change implies an architectural decision;
- there is no CapabilitySpec for a new capability;
- there is no ModuleContract for a new or changed module boundary;
- there is no TaskSpec for the implementation slice;
- acceptance tests are not defined;
- the user has not authorized productive code changes;
- the work would mix unrelated layers;
- the repo is dirty in unrelated files;
- the branch or remote state is unclear;
- the proposed change would call a protocol, pilot, or internal capability a product.

## Git protocol

Before writing:

```text
git status --short
git branch --show-current
git log -1 --oneline
```

Before commit:

```text
git status --short
git diff -- <planned files>
```

Commit discipline:

- focal commit;
- no unrelated files;
- no productive code without explicit authorization;
- include evidence in the response;
- push only when repo is clean enough, branch is correct, and there is no known divergence.

Recommended commit message for this startup contract family:

```text
docs(pymia): add agent startup and development method
```

## Current methodological warning

`NEEDS_EVIDENCE` can detect missing evidence in existing flows, but guided recovery of evidence or operational meaning is not automatically implemented by this contract.

Do not implement Guided Evidence Recovery unless a future cycle creates the appropriate ADR, CapabilitySpec, ModuleContract, TaskSpec, tests, and evidence requirements.

## Default answer format for agent work

When reporting back, use:

1. Repo state.
2. Sources read.
3. Certified / hypothesis / gap / next methodological step.
4. Files changed.
5. Validation evidence.
6. Commit / push status.
7. Next step.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, invoke the `skill` tool with `skill: "graphify"` before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Documentation Policy

Antes de leer documentación histórica, leer `docs/current/README.md`.

## Servicio 1 — startup override vigente desde 2026-08-23

Para cualquier tarea destinada a **continuar, reconstruir, cerrar o certificar Servicio 1**, el checkpoint de entrada obligatorio es:

```text
docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md
```

Luego debe seguir exactamente el orden de lectura definido allí. La arquitectura objetivo de Servicio 1 está cerrada (`OPEN_ARCHITECTURAL_DECISIONS = 0`); un agente de implementación no está autorizado a rediseñarla durante la reconstrucción.

Las instrucciones operativas obligatorias para agentes están en:

```text
docs/current/SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md
```

Los prompts ejecutables del nodo vigente se toman de `docs/current/prompts/`; no deben reconstruirse desde el chat.

El plan operativo vigente es:

```text
docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md
```

Y el único criterio válido para declarar finalización es:

```text
docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md
```

Los documentos históricos, auditorías, phases y closeouts anteriores pueden aportar evidencia, pero no sustituyen este handoff ni los documentos normativos `SERVICE_1_CANONICAL_AXIS.md` / `SERVICE_1_ARCHITECTURE_LOCK.md`.
