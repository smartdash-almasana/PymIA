# SERVICE_1_RUNTIME_CATALOG_TO_SEMANTIC_BINDING_HANDOFF_TEST_PLAN_V1

**Project:** PymIA / SmartPyme / Servicio 1  
**Type:** Handoff Test Design / DOC ONLY  
**Mode:** TEST DESIGN ONLY / DOC ONLY  
**Base:** `main` / `193f8bb`

## Verdict

```text
VERDICT: PASS_RUNTIME_CATALOG_TO_SEMANTIC_BINDING_HANDOFF_TEST_PLAN_DOC_CREATED
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
IMPLEMENTATION_STATUS: NOT_STARTED
PRODUCT_READY_STATUS: NOT_READY
```

This document defines the test plan for the future handoff layer between `Service1RuntimeCatalogBindingAdapterContextV1` and a semantic evidence binding consideration context.

It does not authorize handoff implementation, runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching, JSON mutation, Phase 5, or product-ready claims.

## 1. Purpose

Define the tests required before implementing:

```text
SERVICE_1_RUNTIME_CATALOG_TO_SEMANTIC_BINDING_HANDOFF_IMPLEMENTATION_V1
```

The future handoff must consume only `Service1RuntimeCatalogBindingAdapterContextV1` and emit a governed `Service1SemanticBindingConsiderationContextV1`. Tests must prove the handoff is a governance boundary, not an execution bridge.

## 2. Non-goals

```text
runtime execution
runtime authorization
mapper invocation
engine invocation
CLI integration
CASE_001 patching
JSON mutation
formula computation
owner conversation generation
product-ready declaration
Phase 5 activation
```

## 3. Future test file

```text
PymIA-Live/tests/smartpyme/test_service_1_runtime_catalog_to_semantic_binding_handoff_v1.py
```

Source under test (future module):

```text
PymIA-Live/pymia/smartpyme/service_1_runtime_catalog_to_semantic_binding_handoff_v1.py
```

Allowed upstream input:

```text
Service1RuntimeCatalogBindingAdapterContextV1
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
JSON catalog mutation
```

## 4. Expected handoff statuses

```text
HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING
HANDOFF_BLOCKED_BY_ADAPTER_STATUS
HANDOFF_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED
HANDOFF_BLOCKED_BY_MISSING_FORMULA_REFS
HANDOFF_BLOCKED_BY_MISSING_REQUIRED_VARIABLES
HANDOFF_BLOCKED_BY_MISSING_REQUIRED_EVIDENCE
HANDOFF_BLOCKED_BY_POLICY
```

## 5. Required tests

### Blocked adapter status

```text
test_handoff_blocks_when_adapter_status_not_ready
```

Upstream adapter_status != ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION must map to HANDOFF_BLOCKED_BY_ADAPTER_STATUS.

### Owner confirmation

```text
test_handoff_blocks_when_owner_confirmation_required
```

owner_confirmation_required true must map to HANDOFF_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED regardless of other fields.

### Missing formula_refs

```text
test_handoff_blocks_when_empty_formula_refs
```

empty formula_refs must map to HANDOFF_BLOCKED_BY_MISSING_FORMULA_REFS.

### Missing required variables

```text
test_handoff_blocks_when_empty_required_variables
```

empty required_variables must map to HANDOFF_BLOCKED_BY_MISSING_REQUIRED_VARIABLES.

### Missing required evidence

```text
test_handoff_blocks_when_empty_required_evidence
```

empty required_evidence must map to HANDOFF_BLOCKED_BY_MISSING_REQUIRED_EVIDENCE.

### Ready handoff

```text
test_handoff_ready_when_adapter_ready_and_complete
```

ready adapter_status + non-empty formula_refs + non-empty required_variables + non-empty required_evidence + owner_confirmation_required false must map to HANDOFF_READY_FOR_SEMANTIC_EVIDENCE_BINDING.

### Policy fail-closed

```text
test_handoff_blocks_on_policy_violation
```

any policy violation must map to HANDOFF_BLOCKED_BY_POLICY.

### Invariants

```text
test_handoff_preserves_runtime_allowed_false
test_handoff_preserves_phase_5_allowed_false
test_handoff_allows_semantic_binding_does_not_mean_runtime
test_handoff_does_not_import_runtime_mapper_engine_cli
test_handoff_has_no_case_001_dependency
test_handoff_does_not_mutate_json
test_handoff_output_shape_is_complete
test_handoff_blocks_when_upstream_runtime_allowed_true
test_handoff_blocks_when_upstream_phase_5_allowed_true
```

## 6. Invariants to test

```text
I1.  runtime_allowed is always false.
I2.  phase_5_allowed is always false.
I3.  semantic_evidence_binding_allowed does not mean runtime_allowed.
I4.  No runtime import.
I5.  No mapper import.
I6.  No engine import.
I7.  No CLI import.
I8.  No CASE_001 dependency.
I9.  No JSON mutation.
I10. No owner answer interpretation.
I11. No LLM decision.
I12. No product-ready claim.
I13. No Phase 5 activation.
```

## 7. Forbidden imports guard

Tests must fail if the handoff module imports any of:

```text
service_1_xlsx_first_product_entrypoint_v1
service_1_column_semantic_mapper_v1
service_1_semantic_evidence_binding_engine_v1
service_1_pathology_to_allowed_computation_candidate_v1
pymia.cli
```

The handoff may import only the adapter module, the semantic evidence binding contracts module (for status constants), and standard-library helpers.

## 8. Fixtures

Tests may build synthetic `Service1RuntimeCatalogBindingAdapterContextV1` instances for all adapter statuses and owner_confirmation flag combinations.

Fixtures must not read or mutate JSON catalogs. Handoff tests are not catalog tests; catalog behavior is already covered by contract and adapter tests.

## 9. Certified facts

```text
CF1.  Runtime catalog binding contract exists.
CF2.  Runtime catalog binding adapter exists.
CF3.  Adapter tests passed: 20 passed.
CF4.  Forbidden imports guard passed: 0 results.
CF5.  Handoff plan exists at 193f8bb.
CF6.  Handoff implementation does not exist yet.
CF7.  Handoff tests do not exist yet.
CF8.  Runtime remains blocked.
CF9.  Phase 5 remains blocked.
CF10. Product-ready remains NOT_READY.
```

## 10. Gaps

```text
G1.  Handoff test file not created.
G2.  Handoff Python module not created.
G3.  No integration with semantic evidence binding yet.
G4.  Runtime remains blocked.
G5.  Phase 5 remains blocked.
G6.  Product-ready remains NOT_READY.
```

## 11. Next methodological step

```text
SERVICE_1_RUNTIME_CATALOG_TO_SEMANTIC_BINDING_HANDOFF_TESTS_V1
mode: TEST ONLY
```

Next step must create only:

```text
PymIA-Live/tests/smartpyme/test_service_1_runtime_catalog_to_semantic_binding_handoff_v1.py
```

No handoff implementation yet. No runtime, mapper, engine, CLI, CASE_001, JSON mutation, Phase 5, or product-ready claim.

## 12. Conclusion

This test plan defines the required validation envelope before implementing the handoff. The handoff must remain a read-only governance boundary and must not become an execution bridge.

```text
contract implementation: present
adapter implementation: present
adapter tests: 20 passed
handoff plan: defined
handoff test plan: defined
handoff tests: not started
handoff implementation: not started
runtime connection: blocked
Phase 5: blocked
product-ready: not ready
```
