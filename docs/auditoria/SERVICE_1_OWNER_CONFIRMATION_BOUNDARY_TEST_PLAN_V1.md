# SERVICE_1_OWNER_CONFIRMATION_BOUNDARY_TEST_PLAN_V1

**Project:** PymIA / SmartPyme / Servicio 1  
**Type:** Owner Confirmation Boundary Test Design / DOC ONLY  
**Mode:** TEST DESIGN ONLY / DOC ONLY  
**Base:** `main` / `e40500c`

## Verdict

```text
VERDICT: PASS_OWNER_CONFIRMATION_BOUNDARY_TEST_PLAN_DOC_CREATED
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
PRODUCT_READY_STATUS: NOT_READY
```

This document defines the test plan for the future owner confirmation boundary described in `SERVICE_1_OWNER_CONFIRMATION_BOUNDARY_PLAN_V1`.

It does not authorize boundary implementation, runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching, JSON mutation, Phase 5, or product-ready claims.

## 1. Purpose

Define the tests required before implementing:

```text
SERVICE_1_OWNER_CONFIRMATION_BOUNDARY_IMPLEMENTATION_V1
```

The future boundary must consume an owner confirmation packet plus governed catalog metadata and emit a `Service1OwnerConfirmationResultV1`. Tests must prove the boundary is a pure confirmation recorder, not an execution bridge.

## 2. Non-goals

```text
LLM decision
chatbot interaction
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
PymIA-Live/tests/smartpyme/test_service_1_owner_confirmation_boundary_v1.py
```

Source under test (future module):

```text
PymIA-Live/pymia/smartpyme/service_1_owner_confirmation_boundary_v1.py
```

Allowed upstream input:

```text
owner_confirmation_packet: dict
required_evidence: tuple[str, ...]
minimum_semantic_bindings: tuple[str, ...]
pathology_code: str
```

Forbidden inputs:

```text
runtime state
XLSX columns
mapper output
engine output
CLI output
CASE_001 traces
JSON catalog mutation
```

## 4. Statuses to test

```text
OWNER_CONFIRMED
OWNER_CONFIRMATION_REQUIRED
OWNER_CONFIRMATION_PENDING
OWNER_CONFIRMATION_CONFLICT
OWNER_CONFIRMATION_INSUFFICIENT
OWNER_CONFIRMATION_BLOCKED_BY_POLICY
```

## 5. Required tests

### Confirmed

```text
test_confirmation_all_required_evidence_and_bindings_confirmed -> OWNER_CONFIRMED
```

All `required_evidence` and `minimum_semantic_bindings` present in the confirmation packet must map to OWNER_CONFIRMED.

### Required

```text
test_confirmation_requested_but_incomplete -> OWNER_CONFIRMATION_REQUIRED
```

Confirmation requested but not all required items present must map to OWNER_CONFIRMATION_REQUIRED.

### Pending

```text
test_confirmation_no_packet_available -> OWNER_CONFIRMATION_PENDING
```

Absent or empty confirmation packet must map to OWNER_CONFIRMATION_PENDING.

### Conflict

```text
test_confirmation_conflicting_evidence -> OWNER_CONFIRMATION_CONFLICT
```

Conflicting evidence confirmations (e.g. mutually exclusive values) must map to OWNER_CONFIRMATION_CONFLICT.

### Insufficient

```text
test_confirmation_missing_required_evidence -> OWNER_CONFIRMATION_INSUFFICIENT
```

Missing required evidence confirmations must map to OWNER_CONFIRMATION_INSUFFICIENT.

### Blocked by policy

```text
test_confirmation_policy_violation -> OWNER_CONFIRMATION_BLOCKED_BY_POLICY
```

Any policy violation must map to OWNER_CONFIRMATION_BLOCKED_BY_POLICY.

### Invariants

```text
test_confirmation_preserves_runtime_allowed_false
test_confirmation_preserves_phase_5_allowed_false
test_confirmation_no_llm_decision
test_confirmation_no_chatbot_interaction
test_confirmation_does_not_import_runtime_mapper_engine_cli
test_confirmation_has_no_case_001_dependency
test_confirmation_does_not_mutate_json
test_confirmation_output_shape_is_complete
test_confirmation_blocks_when_upstream_runtime_allowed_true
test_confirmation_blocks_when_upstream_phase_5_allowed_true
```

## 6. Invariants to test

```text
I1.  No LLM decision.
I2.  No chatbot interaction.
I3.  No runtime import.
I4.  No mapper import.
I5.  No engine import.
I6.  No CLI import.
I7.  No CASE_001 dependency.
I8.  No JSON mutation.
I9.  No product-ready claim.
I10. No Phase 5 activation.
I11. runtime_allowed is always false.
I12. phase_5_allowed is always false.
```

## 7. Forbidden imports guard

Tests must fail if the boundary module imports any of:

```text
service_1_xlsx_first_product_entrypoint_v1
service_1_column_semantic_mapper_v1
service_1_semantic_evidence_binding_engine_v1
service_1_pathology_to_allowed_computation_candidate_v1
pymia.cli
```

The boundary may import only standard-library helpers and the governing contract/adapter/handoff modules for status constants.

## 8. Fixtures

Tests may build synthetic owner confirmation packets and required-evidence / minimum-semantic-bindings tuples.

Fixtures must not read or mutate JSON catalogs. Confirmation tests are not catalog tests; catalog behavior is already covered by contract, adapter, and handoff tests.

## 9. Certified facts

```text
CF1.  Runtime catalog binding contract exists.
CF2.  Runtime catalog binding adapter exists.
CF3.  Catalog to semantic binding handoff exists at 6adc6be.
CF4.  Owner confirmation boundary plan exists at e40500c.
CF5.  Boundary implementation does not exist yet.
CF6.  Boundary tests do not exist yet.
CF7.  Runtime remains blocked.
CF8.  Phase 5 remains blocked.
CF9.  Product-ready remains NOT_READY.
```

## 10. Gaps

```text
G1.  Boundary test file not created.
G2.  Boundary Python module not created.
G3.  No integration with semantic evidence binding activation yet.
G4.  Runtime remains blocked.
G5.  Phase 5 remains blocked.
G6.  Product-ready remains NOT_READY.
```

## 11. Next methodological step

```text
SERVICE_1_OWNER_CONFIRMATION_BOUNDARY_TESTS_V1
mode: TEST ONLY
```

Next step must create only:

```text
PymIA-Live/tests/smartpyme/test_service_1_owner_confirmation_boundary_v1.py
```

No boundary implementation yet. No runtime, mapper, engine, CLI, CASE_001, JSON mutation, Phase 5, or product-ready claim.

## 12. Conclusion

This test plan defines the required validation envelope before implementing the owner confirmation boundary. The boundary must remain a pure confirmation recorder and must not become an execution bridge.

```text
contract implementation: present
adapter implementation: present
handoff implementation: present
owner confirmation plan: defined
owner confirmation test plan: defined
owner confirmation tests: not started
owner confirmation implementation: not started
runtime connection: blocked
Phase 5: blocked
product-ready: not ready
```
