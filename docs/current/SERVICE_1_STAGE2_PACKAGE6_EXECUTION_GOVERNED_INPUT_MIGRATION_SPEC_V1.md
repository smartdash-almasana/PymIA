# SERVICE 1 — Stage 2 Package 6 — Execution Governed Input Migration V1

## Status

CLOSED_PASS

## Purpose

Move the execution boundary from the legacy `SERVICE_1_COMPUTATION_PLAN_V1` projection toward canonical `Service1GovernedComputationInputV1`, without collapsing P8 into execution and without rewriting all legacy evaluators in one step.

Canonical sequence:

```text
P6ApprovalDecision
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision
→ Service1GovernedComputationInputV1
→ deterministic execution
```

## Changes

### 1. Generic execution authority

`service_1_generic_capability_engine_v1` now prefers `Service1GovernedComputationInputV1` (or its serialized mapping) as execution input.

If a legacy computation plan carries `governed_computation_input`, the engine consumes the nested governed input and ignores conflicting legacy `source_bindings` for execution authority.

The legacy plan path remains accepted only for compatibility with tests/callers not yet migrated.

### 2. Remove P7 before P6

`service_1_canonical_ingestion_output_to_semantic_bridge_v1` no longer builds variable-family bindings from semantic candidates.

The semantic bridge terminates at hypotheses/candidates. P7 starts only from P6-approved decisions.

Compatibility fields remain empty:

```text
variable_family_count = 0
variable_family_bindings = ()
ready_variable_family_ids = []
```

### 3. Remove semantic binding compatibility projection

`build_computation_plan()` no longer emits `semantic_binding_result`.

The governed source binding is carried by:

```text
Service1GovernedComputationInputV1.source_bindings
```

### 4. Legacy execution consumers still temporary

The following product routes still consume `SERVICE_1_COMPUTATION_PLAN_V1` directly and are not declared converged by this package:

- LIQ_001 specialized evaluator/normalized evidence route
- REN_001 specialized evaluator/normalized evidence route
- PYME_013 composite capability special plan

They remain temporary legacy consumers and must be migrated before the computation-plan projection can be deleted.

## Authority model

```text
EVENT: OwnerConfirmationEvent
DECISION: P6ApprovalDecision
DECISION: RequirementMatch
DECISION: ComputabilityDecision
VALUE OBJECT: GovernedComputationInput
PROJECTION: ComputationPlanV1 (legacy only)
```

`ComputationPlanV1` must not become an independent source of execution truth.

## Acceptance conditions

- canonical ingestion does not perform P7 matching
- P8 remains the only producer of governed computation input for ordinary P8-backed capabilities
- generic execution consumes governed computation input when available
- conflicting legacy plan bindings cannot override governed input
- semantic_binding_result projection is absent
- existing legacy plan callers remain deterministic and fail closed
- single product root unchanged
- no LLM runtime authority

## Delete conditions

`SERVICE_1_COMPUTATION_PLAN_V1` may be removed after:

1. LIQ_001 consumes governed input directly.
2. REN_001 consumes governed input directly.
3. PYME_013 obtains a governed P8-compatible composite input rather than a hand-built plan.
4. No productive executor validates `COMPUTATION_PLAN_SCHEMA_VERSION` as its authority.
5. Neighbor/product tests and architecture certifier pass.
