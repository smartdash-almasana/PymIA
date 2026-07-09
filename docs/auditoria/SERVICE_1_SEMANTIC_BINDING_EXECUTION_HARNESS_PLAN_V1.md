# SERVICE_1_SEMANTIC_BINDING_EXECUTION_HARNESS_PLAN_V1

## VERDICT

```text
PLAN_READY_FOR_REPO_REVIEW
```

## Mode

```text
DESIGN ONLY / DOC ONLY
```

## Current certified base

The governed Servicio 1 semantic readiness pipeline is closed through activation:

```text
runtime catalog binding contract
-> runtime catalog binding adapter
-> catalog-to-semantic binding handoff
-> owner confirmation boundary
-> pipeline readiness gate
-> runtime catalog pipeline composition
-> semantic binding activation
```

Recent closed implementation layers:

```text
c6f0c84 feat(pymia-live): add service 1 runtime catalog pipeline composition
e13fee7 feat(pymia-live): add service 1 semantic binding activation
```

The last certified audit for activation returned:

```text
PASS
```

## Purpose

This document defines the first safe harness boundary after semantic binding activation.

The purpose of `SERVICE_1_SEMANTIC_BINDING_EXECUTION_HARNESS_V1` is to provide a controlled, fail-closed harness that can accept a ready activation candidate and prepare a bounded request for future semantic evidence binding execution.

It must answer only this question:

```text
Can a semantic binding execution request be prepared under closed governance?
```

It must not answer:

```text
Can runtime execute now?
Can the semantic engine run freely?
Can the mapper infer columns now?
Can Phase 5 open?
Can a delivery package be generated?
Is the product ready?
```

## Architectural position

```text
semantic binding activation
  ↓
semantic binding execution harness
  ↓
FUTURE: bounded semantic evidence binding invocation
```

This layer is a harness boundary, not the engine itself.

## Non-goals

The harness must not perform any of the following:

```text
- XLSX runtime execution
- column semantic mapping
- actual semantic evidence binding engine execution
- formula computation
- pathology reinterpretation
- owner conversation
- CLI orchestration
- case-specific execution
- JSON catalog mutation
- delivery generation
- Phase 5 authorization
- product-ready declaration
```

## Input

The planned harness should consume one primary input:

```text
Service1SemanticBindingActivationResultV1
```

It may read only activation-governed fields:

```text
activation_status
semantic_binding_activation_allowed
semantic_binding_execution_allowed
runtime_allowed
phase_5_allowed
product_ready
blocking_layer
blocking_reasons
metadata
```

It must not re-read catalogs, rebuild composition, or call the mapper/engine.

## Planned output shape

The planned output object should be named:

```text
Service1SemanticBindingExecutionHarnessResultV1
```

Recommended fields:

```text
schema_version: str
service_name: str
pathology_code: str
harness_status: str
activation_status: str
semantic_binding_request_prepared: bool
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

`semantic_binding_request_prepared` may be `True` only for a ready activation candidate with all guards closed.

## Planned status vocabulary

```text
SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_POLICY
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_EXECUTION_GUARD
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_RUNTIME_GUARD
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PHASE_5_GUARD
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PRODUCT_READY_GUARD
```

## Harness rules

### R1. Activation must be ready

Required activation status:

```text
SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE
```

If not ready, return:

```text
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION
```

### R2. Activation must allow activation candidacy

Required field:

```text
semantic_binding_activation_allowed = True
```

If false, return:

```text
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_ACTIVATION
```

### R3. Policy violation blocks first

If activation metadata exposes:

```text
policy_violation = True
```

return:

```text
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_POLICY
```

### R4. Execution guard must remain closed

If activation exposes:

```text
semantic_binding_execution_allowed = True
```

return:

```text
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_EXECUTION_GUARD
```

This prevents a premature switch from request preparation into actual engine execution.

### R5. Runtime guard must remain closed

If activation exposes:

```text
runtime_allowed = True
```

return:

```text
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_RUNTIME_GUARD
```

### R6. Phase 5 guard must remain closed

If activation exposes:

```text
phase_5_allowed = True
```

return:

```text
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PHASE_5_GUARD
```

### R7. Product-ready guard must remain closed

If activation exposes:

```text
product_ready = True
```

return:

```text
SEMANTIC_BINDING_EXECUTION_HARNESS_BLOCKED_BY_PRODUCT_READY_GUARD
```

### R8. Ready request candidate is not execution

When all harness conditions pass, return:

```text
SEMANTIC_BINDING_EXECUTION_HARNESS_READY_REQUEST_CANDIDATE
semantic_binding_request_prepared = True
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

## Drift risk review

### Current drift assessment

```text
DRIFT_RISK: CONTROLLED
```

Reason:

```text
- recent commits are linear and scoped
- each layer has plan/test-plan/tests/implementation/audit closure
- current implementation layers are pure dataclass/function boundaries
- no runtime, mapper, engine, CLI, JSON, or case-specific dependency has entered the chain
```

### Main drift risks ahead

```text
D1. Turning the harness into the semantic engine.
D2. Importing service_1_semantic_evidence_binding_engine_v1 too early.
D3. Importing service_1_column_semantic_mapper_v1 before a bounded invocation contract exists.
D4. Treating request_prepared=True as execution_allowed=True.
D5. Opening runtime_allowed, phase_5_allowed, or product_ready.
D6. Reintroducing case-specific fixtures such as named case traces.
D7. Mutating JSON catalogs to satisfy harness tests.
D8. Combining harness, engine invocation, CLI, and delivery in one commit.
```

### Anti-drift controls required

Future tests and implementation must include guards for:

```text
- no runtime import
- no mapper import
- no engine import
- no CLI import
- no case-specific fixture dependency
- no JSON mutation
- semantic_binding_execution_allowed=False
- runtime_allowed=False
- phase_5_allowed=False
- product_ready=False
```

The harness must remain a request-preparation boundary only.

## Acceptance criteria for future tests

```text
AC1. Blocks when activation_status is not SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE.
AC2. Blocks when semantic_binding_activation_allowed is False.
AC3. Blocks on metadata.policy_violation=True.
AC4. Blocks if semantic_binding_execution_allowed=True upstream.
AC5. Blocks if runtime_allowed=True upstream.
AC6. Blocks if phase_5_allowed=True upstream.
AC7. Blocks if product_ready=True upstream.
AC8. Ready request candidate only when activation is ready and all guards remain closed.
AC9. semantic_binding_request_prepared=True only on ready request candidate path.
AC10. semantic_binding_execution_allowed=False always.
AC11. runtime_allowed=False always.
AC12. phase_5_allowed=False always.
AC13. product_ready=False always.
AC14. Output shape is complete.
AC15. Forbidden import guard is clean.
AC16. Case-specific dependency guard is clean.
AC17. No JSON files are modified.
```

## Explicit stop conditions

Stop future microcycles immediately if any implementation or test requires:

```text
- direct semantic evidence binding engine execution
- mapper import
- runtime import
- CLI import
- case-specific fixture dependency
- JSON mutation
- delivery package generation
- product-ready assertion
- Phase 5 authorization
- owner conversation
```

## Next step

The next safe microcycle is:

```text
SERVICE_1_SEMANTIC_BINDING_EXECUTION_HARNESS_TEST_PLAN_V1
mode: TEST DESIGN ONLY / DOC ONLY
```

No tests or production code should be written before that test plan exists and is committed.

## Final status

```text
SERVICE_1_SEMANTIC_BINDING_EXECUTION_HARNESS_PLAN_V1:
READY_FOR_TEST_PLAN_MICROCYCLE
```
