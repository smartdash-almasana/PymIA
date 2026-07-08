# SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_TEST_PLAN_V1

**Project:** PymIA / SmartPyme / Servicio 1  
**Type:** Test Design / DOC ONLY  
**Mode:** TEST DESIGN ONLY / DOC ONLY  
**Base:** `main` / `183c45a`  

## Verdict

```text
VERDICT: PASS_RUNTIME_CATALOG_BINDING_ADAPTER_TEST_PLAN_DOC_CREATED
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
IMPLEMENTATION_STATUS: NOT_STARTED
PRODUCT_READY_STATUS: NOT_READY
```

This document defines the test plan for the future read-only adapter after `SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1`.

It does not authorize adapter implementation, runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching, JSON mutation, Phase 5, or product-ready claims.

## 1. Purpose

Define the tests required before implementing:

```text
SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_IMPLEMENTATION_V1
```

The future adapter must consume only `Service1RuntimeCatalogBindingResultV1` and emit a non-executing adapter context. Tests must prove that the adapter is a governance handoff, not a runtime bridge.

## 2. Source under test

Future module:

```text
PymIA-Live/pymia/smartpyme/service_1_runtime_catalog_binding_adapter_v1.py
```

Future test file:

```text
PymIA-Live/tests/smartpyme/test_service_1_runtime_catalog_binding_adapter_v1.py
```

Allowed upstream input:

```text
Service1RuntimeCatalogBindingResultV1
```

Forbidden inputs:

```text
runtime state
XLSX columns
owner answers
mapper output
engine output
CLI output
CASE_001 traces
```

## 3. Adapter context expected shape

```text
Service1RuntimeCatalogBindingAdapterContextV1
```

Required fields:

```text
schema_version
service_name
pathology_code
upstream_readiness_status
adapter_status
formula_refs
resolved_formula_ids
required_variables
resolved_variables
required_evidence
minimum_semantic_bindings
owner_confirmation_required
semantic_binding_consideration_allowed
semantic_binding_blocking_reasons
runtime_allowed
phase_5_allowed
metadata
```

## 4. Status mapping tests

The test suite must validate exact mapping:

```text
UNKNOWN_PATHOLOGY_CODE -> ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY
MISSING_FORMULA_REFS -> ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS
FORMULA_REF_NOT_FOUND -> ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND
REQUIRED_VARIABLE_NOT_FOUND -> ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND
REQUIRED_EVIDENCE_MISSING -> ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING
OWNER_CONFIRMATION_REQUIRED -> ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED
RUNTIME_BLOCKED_BY_POLICY -> ADAPTER_BLOCKED_BY_POLICY
CATALOG_BINDING_READY_CANDIDATE -> ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION
```

## 5. Required test cases

```text
test_adapter_maps_unknown_pathology_to_blocked_unknown
test_adapter_maps_missing_formula_refs_to_blocked_missing_formula_refs
test_adapter_maps_formula_ref_not_found_to_blocked_formula_ref_not_found
test_adapter_maps_required_variable_not_found_to_blocked_required_variable_not_found
test_adapter_maps_required_evidence_missing_to_blocked_required_evidence_missing
test_adapter_maps_owner_confirmation_required_to_blocked_owner_confirmation
test_adapter_maps_runtime_blocked_by_policy_to_blocked_policy
test_adapter_maps_ready_candidate_to_semantic_binding_consideration_ready
test_adapter_preserves_runtime_allowed_false
test_adapter_preserves_phase_5_allowed_false
test_adapter_allows_semantic_consideration_only_for_ready_candidate
test_adapter_blocks_missing_upstream_result
test_adapter_blocks_unknown_upstream_status
test_adapter_fails_closed_if_upstream_runtime_allowed_true
test_adapter_fails_closed_if_upstream_phase_5_allowed_true
test_adapter_blocks_ready_candidate_with_empty_required_variables
test_adapter_blocks_ready_candidate_with_empty_required_evidence
test_adapter_does_not_import_runtime_mapper_engine_cli
test_adapter_has_no_case_001_dependency
test_adapter_output_shape_is_complete
```

## 6. Invariants to test

```text
I1. runtime_allowed is always false.
I2. phase_5_allowed is always false.
I3. semantic_binding_consideration_allowed can be true only when upstream_readiness_status is CATALOG_BINDING_READY_CANDIDATE.
I4. semantic_binding_consideration_allowed never means runtime_allowed.
I5. Adapter never promotes missing formula_refs.
I6. Adapter never treats hardcoded allowed-computation as catalog authority.
I7. Adapter never forces CASE_001 to pass.
I8. Adapter never declares product-ready.
```

## 7. Forbidden imports guard

Tests must fail if the adapter imports any of:

```text
service_1_xlsx_first_product_entrypoint_v1
service_1_column_semantic_mapper_v1
service_1_semantic_evidence_binding_engine_v1
service_1_pathology_to_allowed_computation_candidate_v1
pymia.cli
```

The adapter may import only the runtime catalog binding contract module and standard-library helpers required for pure dataclasses/typing.

## 8. Fixtures

Tests may build synthetic `Service1RuntimeCatalogBindingResultV1` instances for all eight upstream statuses.

Fixtures must not read or mutate JSON catalogs. Adapter tests are not catalog tests; catalog behavior is already covered by contract tests.

## 9. Certified facts

```text
CF1. Runtime catalog binding contract implementation exists at 2ebdae9.
CF2. Adapter plan exists at 183c45a.
CF3. Adapter implementation does not exist yet.
CF4. Adapter tests do not exist yet.
CF5. Runtime connection remains blocked.
CF6. Phase 5 remains blocked.
CF7. Product-ready remains NOT_READY.
```

## 10. Gaps

```text
G1. Adapter test file not created.
G2. Adapter Python module not created.
G3. No downstream semantic binding integration.
G4. Runtime remains blocked.
G5. Phase 5 remains blocked.
G6. Product-ready remains NOT_READY.
```

## 11. Next methodological step

```text
SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_TESTS_V1
mode: TEST ONLY
```

Next step must create only:

```text
PymIA-Live/tests/smartpyme/test_service_1_runtime_catalog_binding_adapter_v1.py
```

No adapter implementation yet. No runtime, mapper, engine, CLI, CASE_001, JSON mutation, Phase 5, or product-ready claim.

## 12. Conclusion

This test plan defines the required validation envelope before implementing the adapter. The adapter must remain a read-only governance handoff and must not become an execution bridge.
