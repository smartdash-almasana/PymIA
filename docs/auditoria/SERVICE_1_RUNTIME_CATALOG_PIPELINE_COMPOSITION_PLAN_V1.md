# SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_PLAN_V1

## VERDICT

```text
PLAN_READY_FOR_REPO_REVIEW
```

## Mode

```text
DESIGN ONLY / DOC ONLY
```

## Scope

This document defines the next safe composition layer for Servicio 1 after the successful closure of the governed readiness chain:

```text
runtime catalog binding contract
-> runtime catalog binding adapter
-> catalog-to-semantic binding handoff
-> owner confirmation boundary
-> pipeline readiness gate
```

The planned composition layer must aggregate these already-governed outputs into one pure composition result. It must not execute runtime behavior, invoke semantic mapping, call engines, touch CLI entrypoints, mutate JSON catalogs, or authorize delivery.

## Purpose

The purpose of `SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_V1` is to provide a single deterministic composition boundary that receives the governed outputs of the current semantic-readiness pipeline and returns one explicit composition decision.

It exists to answer one narrow question:

```text
Is the currently governed runtime-catalog semantic chain ready to be considered for semantic evidence binding?
```

The answer may be positive only in the limited sense of:

```text
READY_FOR_SEMANTIC_BINDING_CONSIDERATION
```

It must not mean:

```text
runtime authorized
product ready
Phase 5 open
semantic engine execution authorized
client delivery authorized
```

## Non-goals

This layer must not perform any of the following:

```text
- runtime execution
- XLSX processing
- column semantic mapping
- semantic evidence binding execution
- pathology reinterpretation
- formula computation
- CLI orchestration
- owner conversation
- CASE_001 execution
- JSON catalog mutation
- product-ready declaration
- Phase 5 activation
- delivery package generation
```

## Architectural Position

The composition layer sits after the readiness gate and before any future semantic evidence binding activation.

```text
catalog binding contract
  ↓
adapter
  ↓
handoff
  ↓
owner confirmation
  ↓
readiness gate
  ↓
runtime catalog pipeline composition
  ↓
FUTURE: semantic evidence binding activation candidate
```

This layer is still governance, not runtime.

## Composition Sequence

The composition sequence must be strictly ordered and fail closed.

### 1. Catalog Binding Contract

Input source:

```text
Service1RuntimeCatalogBindingResultV1
```

Expected ready status:

```text
CATALOG_BINDING_READY_CANDIDATE
```

If not ready, composition must return:

```text
COMPOSITION_BLOCKED_BY_CATALOG
```

### 2. Runtime Catalog Binding Adapter

Input source:

```text
Service1RuntimeCatalogBindingAdapterContextV1
```

Expected ready status:

```text
ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION
```

If not ready, composition must return:

```text
COMPOSITION_BLOCKED_BY_ADAPTER
```

### 3. Catalog-to-Semantic Binding Handoff

Input source:

```text
Service1SemanticBindingConsiderationContextV1
```

Expected ready status:

```text
HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING
```

If not ready, composition must return:

```text
COMPOSITION_BLOCKED_BY_HANDOFF
```

### 4. Owner Confirmation Boundary

Input source:

```text
Service1OwnerConfirmationResultV1
```

Expected ready status:

```text
OWNER_CONFIRMED
```

If not confirmed, composition must return:

```text
COMPOSITION_BLOCKED_BY_OWNER_CONFIRMATION
```

### 5. Pipeline Readiness Gate

Input source:

```text
Service1PipelineReadinessGateResultV1
```

Expected ready status:

```text
PIPELINE_READY_FOR_SEMANTIC_BINDING
```

If not ready, composition must return:

```text
COMPOSITION_BLOCKED_BY_GATE
```

If any layer exposes policy violation metadata, composition must return:

```text
COMPOSITION_BLOCKED_BY_POLICY
```

Policy block takes precedence over normal readiness blocks.

## Planned Output Shape

The planned output object should be named:

```text
Service1RuntimeCatalogPipelineCompositionResultV1
```

Recommended fields:

```text
schema_version: str
service_name: str
pathology_code: str
composition_status: str
catalog_binding_status: str
adapter_status: str
handoff_status: str
owner_confirmation_status: str
gate_status: str
blocking_layer: str | None
blocking_reasons: tuple[str, ...]
semantic_binding_consideration_allowed: bool
runtime_allowed: bool
phase_5_allowed: bool
product_ready: bool
metadata: dict[str, Any]
```

Required invariant values:

```text
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

`semantic_binding_consideration_allowed` may be `True` only when all upstream layers and the readiness gate are ready.

## Planned Status Vocabulary

```text
COMPOSITION_READY_FOR_SEMANTIC_BINDING
COMPOSITION_BLOCKED_BY_CATALOG
COMPOSITION_BLOCKED_BY_ADAPTER
COMPOSITION_BLOCKED_BY_HANDOFF
COMPOSITION_BLOCKED_BY_OWNER_CONFIRMATION
COMPOSITION_BLOCKED_BY_GATE
COMPOSITION_BLOCKED_BY_POLICY
```

## Invariants

### I1. Pure composition only

The composition layer must be deterministic and side-effect free.

### I2. No runtime authorization

The layer must never authorize runtime execution.

```text
runtime_allowed = False
```

### I3. No Phase 5 authorization

The layer must never open Phase 5.

```text
phase_5_allowed = False
```

### I4. No product-ready declaration

The layer must never declare product readiness.

```text
product_ready = False
```

### I5. No mapper / engine / CLI imports

Forbidden imports or textual dependencies:

```text
service_1_xlsx_first_product_entrypoint_v1
service_1_column_semantic_mapper_v1
service_1_semantic_evidence_binding_engine_v1
service_1_pathology_to_allowed_computation_candidate_v1
pymia.cli
```

### I6. No CASE_001 dependency

The layer must not depend on any specific case fixture, especially:

```text
CASE_001
```

### I7. No JSON mutation

The layer must not read-write or mutate catalog JSON files.

### I8. Fail closed

Any unknown, missing, policy-marked, or non-ready upstream state must return a blocking status.

## Acceptance Criteria

A future implementation can be accepted only if all conditions are true:

```text
AC1. One productive file only:
    PymIA-Live/pymia/smartpyme/service_1_runtime_catalog_pipeline_composition_v1.py

AC2. One focal test file only:
    PymIA-Live/tests/smartpyme/test_service_1_runtime_catalog_pipeline_composition_v1.py

AC3. Tests cover all block statuses and ready status.

AC4. Tests prove runtime_allowed is always False.

AC5. Tests prove phase_5_allowed is always False.

AC6. Tests prove product_ready is always False.

AC7. Tests prove semantic_binding_consideration_allowed is True only for all-ready path.

AC8. Forbidden import guard is clean.

AC9. CASE_001 guard is clean.

AC10. No JSON files are modified.
```

## Explicit Stop Conditions

Stop the microcycle immediately if any of these occur:

```text
- implementation tries to call runtime
- implementation imports mapper or engine
- implementation imports CLI
- implementation mentions CASE_001
- implementation changes catalog JSON
- implementation declares product-ready
- implementation opens Phase 5
- implementation combines composition with semantic binding execution
- implementation writes delivery files
```

## Next Step

The next safe microcycle is test-design only:

```text
SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_TEST_PLAN_V1
mode: TEST DESIGN ONLY / DOC ONLY
```

The test plan should define the required test matrix before any productive composition code is written.

## Final Status

```text
SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_PLAN_V1:
READY_FOR_TEST_PLAN_MICROCYCLE
```
