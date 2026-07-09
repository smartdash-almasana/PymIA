# SERVICE_1_SEMANTIC_BINDING_ACTIVATION_TEST_PLAN_V1

## VERDICT

```text
TEST_PLAN_READY_FOR_REPO_REVIEW
```

## Mode

```text
TEST DESIGN ONLY / DOC ONLY
```

## Base

This test plan follows:

```text
docs/auditoria/SERVICE_1_SEMANTIC_BINDING_ACTIVATION_PLAN_V1.md
```

It defines the future test matrix for the semantic binding activation boundary. It does not create tests or production code.

## Target future files

Future focal test file:

```text
PymIA-Live/tests/smartpyme/test_service_1_semantic_binding_activation_v1.py
```

Future production file:

```text
PymIA-Live/pymia/smartpyme/service_1_semantic_binding_activation_v1.py
```

## Unit under test

Future public API:

```text
build_semantic_binding_activation_result_v1(
    composition_result,
) -> Service1SemanticBindingActivationResultV1
```

Future output object:

```text
Service1SemanticBindingActivationResultV1
```

## Required output fields

The future test suite must verify that the result exposes:

```text
schema_version
service_name
pathology_code
activation_status
composition_status
semantic_binding_activation_allowed
semantic_binding_execution_allowed
runtime_allowed
phase_5_allowed
product_ready
blocking_layer
blocking_reasons
metadata
```

## Status vocabulary under test

```text
SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_POLICY
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_RUNTIME_GUARD
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PHASE_5_GUARD
SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PRODUCT_READY_GUARD
```

## Test matrix

### T1. Blocks when composition status is not ready

Given composition status is not:

```text
COMPOSITION_READY_FOR_SEMANTIC_BINDING
```

Expected:

```text
activation_status = SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION
semantic_binding_activation_allowed = False
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T2. Blocks when semantic binding consideration is not allowed

Given:

```text
semantic_binding_consideration_allowed = False
```

Expected:

```text
activation_status = SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_COMPOSITION
semantic_binding_activation_allowed = False
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T3. Blocks on policy violation

Given composition metadata exposes:

```text
metadata.policy_violation = True
```

Expected:

```text
activation_status = SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_POLICY
blocking_layer = policy
semantic_binding_activation_allowed = False
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

Policy violation must take precedence over normal readiness blocks.

### T4. Blocks if runtime guard is open upstream

Given:

```text
composition_result.runtime_allowed = True
```

Expected:

```text
activation_status = SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_RUNTIME_GUARD
blocking_layer = runtime_guard
semantic_binding_activation_allowed = False
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T5. Blocks if Phase 5 guard is open upstream

Given:

```text
composition_result.phase_5_allowed = True
```

Expected:

```text
activation_status = SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PHASE_5_GUARD
blocking_layer = phase_5_guard
semantic_binding_activation_allowed = False
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T6. Blocks if product-ready guard is open upstream

Given:

```text
composition_result.product_ready = True
```

Expected:

```text
activation_status = SEMANTIC_BINDING_ACTIVATION_BLOCKED_BY_PRODUCT_READY_GUARD
blocking_layer = product_ready_guard
semantic_binding_activation_allowed = False
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T7. Ready candidate only when composition is ready and all guards remain closed

Given:

```text
composition_status = COMPOSITION_READY_FOR_SEMANTIC_BINDING
semantic_binding_consideration_allowed = True
runtime_allowed = False
phase_5_allowed = False
product_ready = False
metadata.policy_violation != True
```

Expected:

```text
activation_status = SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE
semantic_binding_activation_allowed = True
semantic_binding_execution_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
blocking_layer = None
blocking_reasons = ()
```

### T8. Semantic binding execution remains blocked

For every status path, assert:

```text
semantic_binding_execution_allowed is False
```

### T9. Runtime remains blocked

For every status path, assert:

```text
runtime_allowed is False
```

### T10. Phase 5 remains blocked

For every status path, assert:

```text
phase_5_allowed is False
```

### T11. Product-ready remains blocked

For every status path, assert:

```text
product_ready is False
```

### T12. Activation allowed only on ready candidate path

Assert:

```text
semantic_binding_activation_allowed is True
```

only for `SEMANTIC_BINDING_ACTIVATION_READY_CANDIDATE`.

All blocked statuses must return:

```text
semantic_binding_activation_allowed is False
```

### T13. Output shape is complete

Assert all required output fields exist.

### T14. Forbidden import guard

The future implementation file must not contain:

```text
service_1_xlsx_first_product_entrypoint_v1
service_1_column_semantic_mapper_v1
service_1_semantic_evidence_binding_engine_v1
service_1_pathology_to_allowed_computation_candidate_v1
pymia.cli
```

### T15. CASE_001 guard

The future implementation file must not contain:

```text
CASE_001
```

### T16. JSON mutation guard

The future implementation commit must not include JSON catalog changes unless explicitly authorized in a separate catalog microcycle.

## Test implementation rules

The future test file may use:

```text
pytest.importorskip("pymia.smartpyme.service_1_semantic_binding_activation_v1")
```

until the production file exists.

The test file may import the already-closed composition contract:

```text
service_1_runtime_catalog_pipeline_composition_v1
```

It must not import runtime, mapper, engine, CLI, delivery, or CASE fixtures.

## Expected future TDD result

Before implementation exists:

```text
1 skipped
```

After implementation exists:

```text
all tests passed
0 skipped
```

## Acceptance criteria for future TESTS microcycle

```text
AC1. Create only the focal test file.
AC2. No production code.
AC3. No JSON changes.
AC4. No runtime, mapper, engine, CLI, delivery, or CASE_001 references.
AC5. Test matrix covers all activation statuses.
AC6. Test matrix proves semantic_binding_execution_allowed=False.
AC7. Test matrix proves runtime_allowed=False.
AC8. Test matrix proves phase_5_allowed=False.
AC9. Test matrix proves product_ready=False.
AC10. Test matrix proves semantic_binding_activation_allowed only on ready candidate path.
AC11. Focal pytest returns either 1 skipped before implementation or live passes after implementation.
```

## Stop conditions

Stop immediately if the future test draft requires any of:

```text
- semantic evidence binding engine execution
- mapper import
- runtime import
- CLI import
- CASE_001 dependency
- JSON mutation
- delivery package dependency
- product-ready assertion
- Phase 5 authorization
- owner conversation
```

## Next step

The next safe microcycle is:

```text
SERVICE_1_SEMANTIC_BINDING_ACTIVATION_TESTS_V1
mode: TEST ONLY
```

Create only:

```text
PymIA-Live/tests/smartpyme/test_service_1_semantic_binding_activation_v1.py
```

## Final status

```text
SERVICE_1_SEMANTIC_BINDING_ACTIVATION_TEST_PLAN_V1:
READY_FOR_TESTS_MICROCYCLE
```
