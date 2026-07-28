# SERVICE_1_POST_P8_EXECUTION_BOUNDARY_AND_LEGACY_PROJECTIONS_AUDIT_V1

Status: AUDIT_COMPLETE

## Verdict

PASS_AUDIT_WITH_CONVERGENCE_WORK_REQUIRED

Package 5 established canonical P8 authority (`Service1ComputabilityDecisionV1` + `Service1GovernedComputationInputV1`) and removed semantic rebinding from `build_computation_plan()`. The remaining architecture debt is now concentrated at the execution boundary and in legacy projections.

## Canonical target

```text
P6 Approval
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision
→ GovernedComputationInput
→ Deterministic Execution
```

Execution must consume `GovernedComputationInput` as its only computation authority.

## Findings

### F1 — Execution still consumes legacy computation plan

Classification: MIXED_RESPONSIBILITY / TEMPORARY_MIGRATION_BOUNDARY

Evidence:
- `service_1_product_pipeline_v1` calls `build_computation_plan()`.
- `service_1_generic_capability_engine_v1` validates `SERVICE_1_COMPUTATION_PLAN_V1` and reads `source_bindings` directly from it.
- specialized evaluators/normalizers also read `computation_plan.source_bindings`.

Impact:
P8 is canonical, but execution still depends on its legacy projection instead of the canonical governed input.

Target:
Executors accept `Service1GovernedComputationInputV1` (or its exact serialized contract) and reject legacy/raw semantic structures as execution authority.

Delete condition:
No productive executor reads `SERVICE_1_COMPUTATION_PLAN_V1` as its authority.

### F2 — `semantic_binding_result` is now compatibility-only and has no productive consumer

Classification: TEMPORARY_MIGRATION_PROJECTION

Evidence:
Search under `pymia/smartpyme` finds `semantic_binding_result` only in `service_1_deterministic_semantic_pipeline_v1`, where it is created and serialized as a compatibility projection.

Impact:
It adds a second representation of already-approved P6/P7 state without productive value.

Target:
Remove after regression audit confirms no external/API contract requires it.

Delete condition:
Zero productive callers/consumers and focal+neighbor tests pass without the field.

### F3 — Canonical ingestion still performs variable-family matching before P6

Classification: LEGACY_PARALLEL_PATH / PREMATURE_P7_PROJECTION

Evidence:
`service_1_canonical_ingestion_output_to_semantic_bridge_v1` calls `build_service_1_variable_family_bindings_v1(column_candidates)` and emits `variable_family_bindings` / `ready_variable_family_ids` before owner confirmation and P6.

Impact:
P7-like conclusions are generated from semantic hypotheses before semantic approval. They are no longer needed for canonical P7/P8 and risk authority drift.

Target:
Canonical ingestion emits physical/semantic evidence only. Requirement matching occurs exclusively after P6 via `Service1RequirementMatchV1`.

Delete condition:
No productive downstream consumer requires pre-P6 family bindings.

### F4 — Gate/reinjection still expose `variable_family_bindings` legacy projection

Classification: TEMPORARY_MIGRATION_PROJECTION

Canonical source:
`Service1RequirementMatchV1`

Impact:
Acceptable only during consumer migration; must not become permanent.

Target:
Consumers move to `requirement_matches`; compatibility projection removed when zero productive callers remain.

### F5 — Product root retains capability-specific execution branching

Classification: MIXED_RESPONSIBILITY / EXTENSIBILITY DEBT

Evidence:
`service_1_product_pipeline_v1` still branches for capability-specific/composite execution paths.

Impact:
A new capability can still require root changes, violating the long-term extensibility test.

Target:
After execution consumes governed input, capability dispatch should be registry/contract driven, not a growing root conditional tree.

This is not the first change in the next package; migrate the execution authority first.

## Event / Decision / Projection map

```text
OwnerConfirmationEvent                 EVENT
P6ApprovalDecision                     DECISION
RequirementMatch                       DECISION
ComputabilityDecision                  DECISION
GovernedComputationInput               GOVERNED VALUE OBJECT
VariableFamilyBinding                  LEGACY PROJECTION
ComputationPlanV1                      LEGACY PROJECTION
semantic_binding_result                LEGACY PROJECTION
pre-P6 variable_family_bindings        LEGACY/PREMATURE PROJECTION
```

## Migration sequence

```text
1. Deepen execution contract to accept GovernedComputationInput
2. Migrate generic capability engine first
3. Migrate specialized evaluators/normalizers that read computation_plan.source_bindings
4. Make product root pass governed input to execution
5. Verify identical deterministic outcomes
6. Remove semantic_binding_result projection
7. Remove pre-P6 variable-family binding from canonical ingestion
8. Remove gate/reentry variable-family projection when remaining consumers reach zero
9. Retire ComputationPlanV1 once no productive executor consumes it
```

## Required certifier checks

```text
EXECUTION_CONSUMES_GOVERNED_COMPUTATION_INPUT
EXECUTION_REJECTS_LEGACY_SEMANTIC_AUTHORITY
NO_PRE_P6_REQUIREMENT_MATCHING
NO_UNUSED_SEMANTIC_BINDING_PROJECTION
NO_PERMANENT_VARIABLE_FAMILY_PROJECTION
NO_SEMANTIC_REBIND_AFTER_P6
```

## Next package

`STAGE2_PACKAGE6_EXECUTION_GOVERNED_INPUT_MIGRATION`

Scope priority:
- execution boundary only;
- canonical P8 input becomes execution authority;
- preserve deterministic results;
- do not simultaneously redesign capability registry/root branching beyond what migration requires.

## Do not change yet

- P6 semantics
- P7 RequirementMatch semantics
- P8 computability rules
- formula/pathology business logic
- delivery behavior
- unrelated concurrent worktree changes
