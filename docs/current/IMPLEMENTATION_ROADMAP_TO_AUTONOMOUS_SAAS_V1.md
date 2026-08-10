# IMPLEMENTATION_ROADMAP_TO_AUTONOMOUS_SAAS_V1

## Status

```text
RECONCILED_TO_CURRENT_SERVICE_1_ARCHITECTURE
```

## Purpose

Define how Service 1 may evolve toward an autonomous SaaS without replacing or bypassing the canonical deterministic architecture already established.

The SaaS objective is an interaction/orchestration layer around the governed Service 1 chain. It is not a second product pipeline.

## Product objective

A PyME owner should be able to interact directly with PymIA while deterministic rules, evidence, owner confirmation, computability checks, execution, QA, and delivery remain under explicit authority boundaries.

Operational source of truth:

```text
PYMIA + DATA + PYME OWNER
```

Conversational AI is not a source of truth and is not runtime authority.

## Current certified Service 1 authority

```text
P0 intake
→ P1 canonical XLSX ingestion
→ P2 profiling / PhysicalEvidence
→ P3 SemanticHypothesis
→ P4 contextual evidence scoring
→ P5 OwnerConfirmationEvent
→ P6 semantic approval
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision
→ Service1GovernedComputationInputV1
→ P9 deterministic execution
→ P10 QA / delivery
```

Canonical productive root:

```text
service_1_product_pipeline_v1
```

P0–P10 is the decision sequence, not a requirement for one module per stage.

## Historical autonomous design — superseded as authority

Earlier roadmap iterations used concepts such as:

```text
case truth integration
auto tool plan candidate
explicit request candidate
pipeline request candidate
autonomous pipeline runner
```

Those records remain historical provenance only. They do not define the current productive architecture and must not be recreated as parallel authorities.

In particular, `service_1_explicit_request_to_pipeline_request_gate_v1` is retired from the current Service 1 architecture.

## Architecture principles for SaaS evolution

1. **One productive root**
   - `service_1_product_pipeline_v1` remains the only productive Service 1 root.

2. **No LLM authority**
   - AI may assist interaction and explanation only; it cannot approve meaning, computability, execution, diagnosis, or delivery.

3. **Owner confirmation is evidence**
   - Owner answers become `OwnerConfirmationEvent` evidence and return through P6; they never grant runtime permission directly.

4. **No semantic rebinding after P6**
   - P7 matches requirements; P8 decides computability. SaaS orchestration cannot reinterpret those decisions.

5. **Governed input before execution**
   - P9 deterministic execution consumes `Service1GovernedComputationInputV1`.

6. **P10 remains delivery authority**
   - SaaS surfaces may present delivery only after the existing QA/delivery boundary passes.

7. **Fail closed**
   - Missing evidence, unresolved owner meaning, incompatible grain/type/unit, unsupported capability, or failed QA must block advancement.

8. **No second parser / no second semantic pipeline**
   - SaaS shell reuses canonical ingestion and governed evidence/semantic decisions.

## Target SaaS layers

### Layer A — Case/session shell

Purpose:
- establish tenant/case identity;
- preserve provenance;
- expose current P0–P10 state;
- never create semantic or execution authority.

### Layer B — File and evidence intake

Purpose:
- transport owner-provided files/evidence into the canonical intake boundary;
- never parse through a second productive parser;
- preserve source provenance.

### Layer C — Owner interaction

Purpose:
- expose requested analysis choices;
- surface only genuinely unresolved owner questions;
- capture owner answers as structured evidence;
- route them through the existing owner confirmation/P6 path.

Canonical interaction:

```text
unresolved canonical context
→ owner-facing projection
→ OwnerConfirmationEvent
→ P6 reevaluation
→ P7
→ P8
```

### Layer D — Orchestration

Purpose:
- coordinate case state and invoke already-authorized canonical transitions;
- never create a second tool plan, pipeline request gate, computability gate, or execution root.

### Layer E — Runtime infrastructure

Potential future components:

```text
API
auth
tenant-aware persistence
upload/storage boundary
worker/queue/scheduler
```

These are infrastructure only. They do not gain business-semantic authority by existing.

### Layer F — Conversational AI under guard

Allowed:
- explain;
- summarize;
- ask approved questions;
- transform owner wording into candidate structured payloads for deterministic validation.

Forbidden:
- approve semantics;
- invent missing evidence;
- select formulas/tools as authority;
- bypass P6/P7/P8;
- execute runtime;
- authorize delivery.

### Layer G — Delivery surface

Purpose:
- expose P10-approved outputs to the owner;
- preserve evidence/provenance and blocking reasons;
- never convert a candidate into an approved delivery by presentation logic.

## Current implementation priority

The SaaS foundation required for a real assisted owner journey is now materially present and physically exercised around the canonical chain:

```text
Supabase Auth
→ tenant identity
→ XLSX intake
→ owner confirmation
→ durable tenant semantic persistence
→ assisted tenant-memory recall without preselection
→ append-only semantic-contract supersession
→ P6/P7/P8
→ deterministic execution
→ P10
→ downloadable XLSX
```

This does not grant the SaaS shell any new domain authority. It remains transport/orchestration around P0–P10.

## Immediate next front

```text
SERVICE_1_REN_001_SELLABLE_VERTICAL_CLOSURE_V1
```

The next implementation work should extend the already-proven product path to `REN_001 / net_margin_real` as a second sellable vertical, reusing the existing web, identity, persistence, semantic, execution and P10 boundaries.

Do not add runner, API, worker, queue, new gate, alternate product route or additional persistence architecture unless a later physical gap requires it.

## Not allowed

```text
second productive root
second XLSX parser
parallel semantic pipeline
reintroduction of retired explicit-request/pipeline-request authority
LLM runtime authority
owner answer = execution permission
hardcoded semantic shortcuts
API/worker logic bypassing P6/P7/P8
presentation layer bypassing P10
operator as mandatory normal path
```

## Definition of a closed SaaS slice

A SaaS slice is closed only when:

- its role relative to P0–P10 is explicit;
- it creates no duplicate authority;
- focal tests pass;
- relevant Service 1 regression passes;
- safety flags remain false unless a canonical downstream authority sets them;
- provenance is preserved;
- fail-closed behavior is tested;
- documentation reflects the actual current architecture.

## Final orientation

```text
AUTONOMOUS_SAAS_GOAL: VALID
PARALLEL_AUTONOMOUS_PIPELINE: NOT_VALID
CURRENT_PRODUCT_AUTHORITY: P0→P10
PRODUCT_ROOT: service_1_product_pipeline_v1
LLM_AUTHORITY: NONE
NEXT_STEP: SERVICE_1_REN_001_SELLABLE_VERTICAL_CLOSURE_V1
```
