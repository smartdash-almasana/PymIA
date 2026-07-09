# SERVICE_1_SEMANTIC_BINDING_ACTIVATION_PLAN_V1

## VERDICT

```text
PLAN_READY_FOR_REPO_REVIEW
```

## Mode

```text
DESIGN ONLY / DOC ONLY
```

## Current certified base

The governed Servicio 1 runtime-catalog semantic readiness chain is closed through composition:

```text
runtime catalog binding contract
-> runtime catalog binding adapter
-> catalog-to-semantic binding handoff
-> owner confirmation boundary
-> pipeline readiness gate
-> runtime catalog pipeline composition
```

Latest closed implementation layer before this plan:

```text
SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_IMPLEMENTATION_V1
```

Closed audit status:

```text
PASS
```

## Purpose

This document defines the next safe activation boundary after composition.

The purpose of `SERVICE_1_SEMANTIC_BINDING_ACTIVATION_V1` is to convert a fully ready composition result into a narrow activation candidate for semantic evidence binding consideration.

It must answer only this question:

```text
May the already-governed semantic evidence binding layer be considered for a future bounded invocation?
```

It must not answer:

```text
May runtime execute?
May the mapper run?
May the semantic engine run now?
May Phase 5 open?
May a client delivery be produced?
Is the product ready?
```

## Architectural position

```text
runtime catalog pipeline composition
  ↓
semantic binding activation candidate
  ↓
FUTURE: semantic evidence binding execution harness
```

This layer is still a governance boundary. It is not the semantic engine and not the runtime harness.

## Non-goals

This layer must not perform any of the following:

```text
- runtime execution
- XLSX processing
- column semantic mapping
- semantic evidence binding execution
- formula computation
- pathology reinterpretation
- owner conversation
- CLI orchestration
- CASE_001 execution
- JSON catalog mutation
- delivery package generation
- Phase 5 authorization
- product-ready declaration
```

## Input

The planned activation layer must consume one primary input:

```text
Service1RuntimeCatalogPipelineCompositionResultV1
```

It may read only the governed fields already exposed by composition:

```text
composition_status
semantic_binding_consideration_allowed
runtime_allowed
phase_5_allowed
product_ready
blocking_layer
blocking_reasons
metadata
```

It must not re-read JSON catalogs or recompute upstream states.

## Planned output shape

The planned output object should be named:

```text
Service1SemanticBindingActivationResultV1
```

Recommended fields:

```text
schema_version: str
service_name: str
pathology_code: str
activation_status: str
composition_status: str
semantic_binding_activation_allowed: bool
semantic_binding_execution_allowed: bool
runtime_allowed: bool
phase_5_allowed: bool
product_ready: bool
blocking_layer: str | None
blocking_reasons: tuple[str, ...]
metadata: dict[str, Any]
```

Required invariant values:

```text
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

`semantic_binding_activation_allowed` may be `True` only when the composition result is ready and explicitly allows semantic binding consideration.

## Planned status vocabulary

```text
SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_POLICY
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_RUNTIME_GUARD
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PHASE_5_GUARD
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PRODUCT_READY_GUARD
```

## Activation rules

### R1. Composition must be ready

Required composition status:

```text
COMPOSITION_READY_FOR_SEMANTIC_BINDING
```

If not ready, return:

```text
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION
```

### R2. Semantic binding consideration must be allowed

Required field:

```text
semantic_binding_consideration_allowed = True
```

If false, return:

```text
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION
```

### R3. Policy violations block first

If composition metadata exposes:

```text
policy_violation = True
```

return:

```text
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_POLICY
```

Policy block takes precedence over normal readiness blocks.

### R4. Runtime guard must remain closed

If the composition result exposes:

```text
runtime_allowed = True
```

return:

```text
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_RUNTIME_GUARD
```

### R5. Phase 5 guard must remain closed

If the composition result exposes:

```text
phase_5_allowed = True
```

return:

```text
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PHASE_5_GUARD
```

### R6. Product-ready guard must remain closed

If the composition result exposes:

```text
product_ready = True
```

return:

```text
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PRODUCT_READY_GUARD
```

### R7. Ready candidate is not execution

When all activation conditions pass, return:

```text
SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE
semantic_binding_activation_allowed = True
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

## Invariants

### I1. Pure activation boundary

The layer must be deterministic and side-effect free.

### I2. No semantic execution

The layer must never execute the semantic evidence binding engine.

```text
semantic_binding_execution_allowed = False
```

### I3. No runtime authorization

```text
runtime_allowed = False
```

### I4. No Phase 5 authorization

```text
phase_5_allowed = False
```

### I5. No product-ready declaration

```text
product_ready = False
```

### I6. No mapper / engine / CLI imports

Forbidden imports or textual dependencies:

```text
service_1_xlsx_first_product_entrypoint_v1
service_1_column_semantic_mapper_v1
service_1_semantic_evidence_binding_engine_v1
service_1_pathology_to_allowed_computation_candidate_v1
pymia.cli
```

### I7. No CASE_001 dependency

Forbidden dependency:

```text
CASE_001
```

### I8. No JSON mutation

The activation layer must not read-write or mutate catalog JSON files.

### I9. Fail closed

Any missing, unknown, policy-marked, runtime-open, phase-5-open, product-ready-open, or non-ready composition state must block activation.

## Acceptance criteria for future tests

```text
AC1. Blocks when composition_status is not COMPOSITION_READY_FOR_SEMANTIC_BINDING.
AC2. Blocks when semantic_binding_consideration_allowed is False.
AC3. Blocks on metadata.policy_violation = True.
AC4. Blocks if runtime_allowed is True.
AC5. Blocks if phase_5_allowed is True.
AC6. Blocks if product_ready is True.
AC7. Ready candidate only when composition is ready and all guards remain closed.
AC8. semantic_binding_execution_allowed is always False.
AC9. runtime_allowed is always False.
AC10. phase_5_allowed is always False.
AC11. product_ready is always False.
AC12. Output shape is complete.
AC13. Forbidden import guard is clean.
AC14. CASE_001 guard is clean.
AC15. No JSON files are modified.
```

## Explicit stop conditions

Stop the future microcycle immediately if any implementation or test requires:

```text
- semantic evidence binding engine execution
- mapper import
- runtime import
- CLI import
- CASE_001 dependency
- JSON mutation
- product-ready assertion
- Phase 5 authorization
- delivery file generation
- owner conversation
```

## Next step

The next safe microcycle is:

```text
SERVICE_1_SEMANTIC_BINDING_ACTIVATION_TEST_PLAN_V1
mode: TEST DESIGN ONLY / DOC ONLY
```

No tests or production code should be written before that test plan exists and is committed.

## Final status

```text
SERVICE_1_SEMANTIC_BINDING_ACTIVATION_PLAN_V1:
READY_FOR_TEST_PLAN_MICROCYCLE
```
