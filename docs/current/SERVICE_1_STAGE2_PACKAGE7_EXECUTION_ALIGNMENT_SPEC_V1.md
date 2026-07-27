# Service 1 Stage 2 Package 7 — Execution Alignment on Governed Computation Input

**STATUS: CLOSED_PASS**

## Objective

Align all productive execution exclusively on `Service1GovernedComputationInputV1` as the sole governed input authority, superseding legacy `SERVICE_1_COMPUTATION_PLAN_V1` as an execution authority.

## Canonical Architecture

```text
P6 APPROVED
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision + GovernedComputationInput
→ Generic Capability Engine (consumes governed input)
→ Deterministic Execution (LIQ_001, REN_001, PYME_013 composites)
```

## Changes

### Productive nucleus reclassification

| Module | Previous | Current |
|--------|----------|---------|
| `service_1_generic_capability_engine_v1` | SUPPORT_NECESSARY | PRODUCTIVE |
| `service_1_capability_registry_v1` | SUPPORT_NECESSARY | PRODUCTIVE |
| `service_1_capability_contracts_v1` | SUPPORT_NECESSARY | PRODUCTIVE |
| `service_1_liq_002_evaluator_v1` | PRODUCTIVE | SUPPORT_NECESSARY |
| `service_1_liq_002_normalized_evidence_v1` | PRODUCTIVE | SUPPORT_NECESSARY |
| `service_1_liq_002_outcome_v1` | PRODUCTIVE | SUPPORT_NECESSARY |
| `service_1_pyme_011_evaluator_v1` | PRODUCTIVE | SUPPORT_NECESSARY |
| `service_1_pyme_011_normalized_evidence_v1` | PRODUCTIVE | SUPPORT_NECESSARY |
| `service_1_pyme_011_outcome_v1` | PRODUCTIVE | SUPPORT_NECESSARY |

### Registry counts

TOTAL=54, PRODUCTIVE=27, SUPPORT_NECESSARY=27

### Baseline checks added

- `LEGACY_COMPUTATION_PLAN_NOT_EXECUTION_AUTHORITY` — all productive engines consume `Service1GovernedComputationInputV1`
- `GENERIC_KERNEL_IS_IN_PRODUCTIVE_ROOT_CLOSURE` — generic engine is PRODUCTIVE with root_reachable=true
- `NO_PRODUCTIVE_SPECIALIZED_LIQ002_PYME011_PARALLEL_PATH` — LIQ_002/PYME_011 are SUPPORT_NECESSARY

### Key architectural decisions

1. P8 is the sole authority for computability decisions.
2. `Service1GovernedComputationInputV1` is the only governed input for execution.
3. `SERVICE_1_COMPUTATION_PLAN_V1` remains in `service_1_deterministic_semantic_pipeline_v1.py` as compatibility projection/transport, not execution authority.
4. LIQ_001 and REN_001 evaluators consume governed input directly.
5. PYME_013 composite is governed from registry/P8.
6. Generic capability engine has no fallback to legacy plan.
7. LIQ_002 and PYME_011 specialized evaluator paths are degraded to support (not PRODUCTIVE), superseded by governed generic kernel.

## Tests

```text
97 passed, 1 failed
```

The single failure (`test_current_readme_indexes_architecture_lock`) is caused by concurrent worktree changes to `docs/current/README.md`, not by Package 7.

## Invariants verified

- [x] UNAPPROVED_SEMANTICS_NEVER_REACH_COMPUTATION
- [x] P8_IS_REQUIRED_BEFORE_GOVERNED_COMPUTATION_INPUT
- [x] EXECUTION_REJECTS_UNGOVERNED_INPUT
- [x] NO_SEMANTIC_REBIND_AFTER_P6
- [x] LEGACY_PLAN_NEVER_OVERRIDES_P8
- [x] COMPOSITE_EXECUTION_CONSUMES_GOVERNED_RESULTS
- [x] SAME_CANONICAL_INPUT_PRODUCES_SAME_DETERMINISTIC_DECISION
