# SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_TEST_PLAN_V1

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
docs/auditoria/SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_PLAN_V1.md
```

It defines the future test matrix for the pure composition layer. It does not create tests or production code.

## Target future files

Future focal test file:

```text
PymIA-Live/tests/smartpyme/test_service_1_runtime_catalog_pipeline_composition_v1.py
```

Future production file:

```text
PymIA-Live/pymia/smartpyme/service_1_runtime_catalog_pipeline_composition_v1.py
```

## Unit under test

Future public API:

```text
build_runtime_catalog_pipeline_composition_result_v1(
    catalog_binding_result,
    adapter_context,
    handoff_context,
    owner_confirmation_result,
    readiness_gate_result,
) -> Service1RuntimeCatalogPipelineCompositionResultV1
```

Future output object:

```text
Service1RuntimeCatalogPipelineCompositionResultV1
```

## Required output fields

The test suite must verify that the result exposes:

```text
schema_version
service_name
pathology_code
composition_status
catalog_binding_status
adapter_status
handoff_status
owner_confirmation_status
gate_status
blocking_layer
blocking_reasons
semantic_binding_consideration_allowed
runtime_allowed
phase_5_allowed
product_ready
metadata
```

## Status vocabulary under test

```text
COMPOSITION_READY_FOR_SEMANTIC_BINDING
COMPOSITION_BLOCKED_BY_CATALOG
COMPOSITION_BLOCKED_BY_ADAPTER
COMPOSITION_BLOCKED_BY_HANDOFF
COMPOSITION_BLOCKED_BY_OWNER_CONFIRMATION
COMPOSITION_BLOCKED_BY_GATE
COMPOSITION_BLOCKED_BY_POLICY
```

## Test matrix

### T1. Blocks when catalog binding is not ready

Expected:

```text
composition_status = COMPOSITION_BLOCKED_BY_CATALOG
blocking_layer = catalog
semantic_binding_consideration_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T2. Blocks when adapter is not ready

Expected:

```text
composition_status = COMPOSITION_BLOCKED_BY_ADAPTER
blocking_layer = adapter
semantic_binding_consideration_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T3. Blocks when handoff is not ready

Expected:

```text
composition_status = COMPOSITION_BLOCKED_BY_HANDOFF
blocking_layer = handoff
semantic_binding_consideration_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T4. Blocks when owner confirmation is missing

Expected:

```text
composition_status = COMPOSITION_BLOCKED_BY_OWNER_CONFIRMATION
blocking_layer = owner_confirmation
semantic_binding_consideration_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T5. Blocks when readiness gate is not ready

Expected:

```text
composition_status = COMPOSITION_BLOCKED_BY_GATE
blocking_layer = readiness_gate
semantic_binding_consideration_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T6. Blocks on policy violation

Given any upstream layer or gate exposes:

```text
metadata.policy_violation = True
```

Expected:

```text
composition_status = COMPOSITION_BLOCKED_BY_POLICY
blocking_layer = policy
semantic_binding_consideration_allowed = False
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

Policy violation must take precedence over normal readiness failures.

### T7. Ready only when all layers and gate are ready

Expected:

```text
composition_status = COMPOSITION_READY_FOR_SEMANTIC_BINDING
blocking_layer = None
blocking_reasons = ()
semantic_binding_consideration_allowed = True
runtime_allowed = False
phase_5_allowed = False
product_ready = False
```

### T8. Runtime remains blocked

For every status path, assert:

```text
runtime_allowed is False
```

### T9. Phase 5 remains blocked

For every status path, assert:

```text
phase_5_allowed is False
```

### T10. Product-ready remains blocked

For every status path, assert:

```text
product_ready is False
```

### T11. Semantic binding consideration allowed only on all-ready path

Assert True only when all upstream layers and gate are ready. All blocked paths must return False.

### T12. Output shape is complete

Assert all required output fields exist.

### T13. Forbidden import guard

The future implementation file must not contain:

```text
service_1_xlsx_first_product_entrypoint_v1
service_1_column_semantic_mapper_v1
service_1_semantic_evidence_binding_engine_v1
service_1_pathology_to_allowed_computation_candidate_v1
pymia.cli
```

### T14. CASE_001 guard

The future implementation file must not contain:

```text
CASE_001
```

### T15. JSON mutation guard

The future implementation commit must not include changes to JSON catalogs unless explicitly authorized in a separate catalog microcycle.

## Test implementation rules

The future test file may use:

```text
pytest.importorskip("pymia.smartpyme.service_1_runtime_catalog_pipeline_composition_v1")
```

until the production file exists.

The test file may import already-closed upstream contracts:

```text
service_1_runtime_catalog_binding_contract_v1
service_1_runtime_catalog_binding_adapter_v1
service_1_runtime_catalog_to_semantic_binding_handoff_v1
service_1_owner_confirmation_boundary_v1
service_1_pipeline_readiness_gate_v1
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
AC4. No runtime, mapper, engine, CLI, or CASE_001 references.
AC5. Test matrix covers all composition statuses.
AC6. Test matrix proves runtime_allowed=False.
AC7. Test matrix proves phase_5_allowed=False.
AC8. Test matrix proves product_ready=False.
AC9. Test matrix proves semantic_binding_consideration_allowed only on all-ready path.
AC10. Focal pytest returns either 1 skipped before implementation or live passes after implementation.
```

## Stop conditions

Stop immediately if the future test draft requires any of:

```text
- runtime execution
- semantic mapper import
- semantic engine import
- CLI import
- CASE_001 dependency
- JSON mutation
- delivery package dependency
- product-ready assertion
- Phase 5 authorization
```

## Next step

The next safe microcycle is:

```text
SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_TESTS_V1
mode: TEST ONLY
```

Create only:

```text
PymIA-Live/tests/smartpyme/test_service_1_runtime_catalog_pipeline_composition_v1.py
```

## Final status

```text
SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_TEST_PLAN_V1:
READY_FOR_TESTS_MICROCYCLE
```
