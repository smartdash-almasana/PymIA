# SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_PLAN_V1

**Project:** PymIA / SmartPyme / Servicio 1  
**Type:** Adapter Design / DOC ONLY  
**Mode:** ADAPTER DESIGN ONLY / DOC ONLY  
**Base:** `main` / `2ebdae9`  

## Verdict

```text
VERDICT: PASS_RUNTIME_CATALOG_BINDING_ADAPTER_PLAN_DOC_CREATED
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
IMPLEMENTATION_STATUS: NOT_STARTED
PRODUCT_READY_STATUS: NOT_READY
```

This document defines the design boundary for a future read-only adapter that may consume `Service1RuntimeCatalogBindingResultV1` and prepare governed context for future semantic evidence binding consideration.

It does not authorize runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching, JSON mutation, Phase 5, or product-ready claims.

## 1. Purpose

Define the adapter boundary between:

```text
SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1
```

and a later semantic evidence binding consideration layer.

The adapter exists to translate a catalog-binding result into a safe, non-executing context object. It must preserve fail-closed statuses and must never convert catalog readiness into runtime authorization.

## 2. Non-goals

```text
runtime execution
runtime authorization
mapper invocation
engine invocation
CLI integration
CASE_001 patching
catalog mutation
JSON mutation
formula computation
owner conversation generation
product-ready declaration
Phase 5 activation
```

## 3. Upstream source

The only upstream source is:

```text
Service1RuntimeCatalogBindingResultV1
```

from:

```text
PymIA-Live/pymia/smartpyme/service_1_runtime_catalog_binding_contract_v1.py
```

The adapter must not read runtime state, XLSX columns, owner answers, mapper output, engine output, CLI output, or CASE_001 traces.

## 4. Proposed adapter output shape

```text
Service1RuntimeCatalogBindingAdapterContextV1
```

Documental shape:

```text
{
  "schema_version": "SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_CONTEXT_V1",
  "service_name": "SERVICE_1",
  "pathology_code": str,
  "upstream_readiness_status": str,
  "adapter_status": str,
  "formula_refs": tuple[str, ...],
  "resolved_formula_ids": tuple[str, ...],
  "required_variables": tuple[str, ...],
  "resolved_variables": tuple[str, ...],
  "required_evidence": tuple[str, ...],
  "minimum_semantic_bindings": tuple[str, ...],
  "owner_confirmation_required": bool,
  "semantic_binding_consideration_allowed": bool,
  "semantic_binding_blocking_reasons": tuple[str, ...],
  "runtime_allowed": false,
  "phase_5_allowed": false,
  "metadata": dict
}
```

## 5. Allowed adapter statuses

```text
ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION
ADAPTER_BLOCKED_BY_RUNTIME_CATALOG_STATUS
ADAPTER_BLOCKED_BY_OWNER_CONFIRMATION_REQUIRED
ADAPTER_BLOCKED_BY_POLICY
ADAPTER_BLOCKED_BY_UNKNOWN_PATHOLOGY
ADAPTER_BLOCKED_BY_MISSING_FORMULA_REFS
ADAPTER_BLOCKED_BY_FORMULA_REF_NOT_FOUND
ADAPTER_BLOCKED_BY_REQUIRED_VARIABLE_NOT_FOUND
ADAPTER_BLOCKED_BY_REQUIRED_EVIDENCE_MISSING
```

## 6. Status mapping

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

Even when the adapter emits `ADAPTER_CONTEXT_READY_FOR_SEMANTIC_BINDING_CONSIDERATION`, both authorization flags remain false.

## 7. Invariants

```text
I1. runtime_allowed is always false.
I2. phase_5_allowed is always false.
I3. Adapter never calls runtime.
I4. Adapter never calls mapper.
I5. Adapter never calls engine.
I6. Adapter never calls CLI.
I7. Adapter never mutates catalogs.
I8. Adapter never mutates upstream result.
I9. Adapter never promotes missing formula_refs.
I10. Adapter never treats hardcoded allowed-computation as catalog authority.
I11. Adapter never forces CASE_001 to pass.
I12. Adapter never declares product-ready.
I13. semantic_binding_consideration_allowed can be true only when upstream_readiness_status is CATALOG_BINDING_READY_CANDIDATE.
I14. semantic_binding_consideration_allowed does not equal runtime_allowed.
```

## 8. Fail-closed rules

```text
F1. Missing upstream result -> ADAPTER_BLOCKED_BY_POLICY.
F2. Unknown upstream readiness_status -> ADAPTER_BLOCKED_BY_POLICY.
F3. upstream runtime_allowed not false -> ADAPTER_BLOCKED_BY_POLICY.
F4. upstream phase_5_allowed not false -> ADAPTER_BLOCKED_BY_POLICY.
F5. Empty formula_refs -> block semantic consideration.
F6. Empty required_variables for a ready candidate -> block semantic consideration.
F7. Empty required_evidence for a ready candidate -> block semantic consideration.
F8. owner_confirmation_required true -> block until a later owner-confirmation boundary exists.
```

## 9. Relationship with semantic evidence binding

Semantic evidence binding governs a later layer:

```text
column candidates
variable bindings
owner questions
formula candidate construction
```

This adapter does not perform those functions. It only prepares a governed context stating whether the catalog-bound pathology may be considered by a future semantic evidence binding step.

Correct sequence:

```text
runtime catalog binding contract
-> read-only adapter context
-> future semantic evidence binding boundary
-> later readiness gate
-> later runtime consideration
```

## 10. Certified facts

```text
CF1. Runtime catalog binding contract implementation exists at 2ebdae9.
CF2. Runtime catalog binding tests passed locally: 25 passed in 0.66s.
CF3. Runtime connection remains blocked.
CF4. Phase 5 remains blocked.
CF5. Product-ready status remains NOT_READY.
CF6. Adapter implementation does not exist yet.
CF7. No adapter currently consumes Service1RuntimeCatalogBindingResultV1.
CF8. No integration with SERVICE_1_SEMANTIC_EVIDENCE_BINDING_CONTRACTS_V1 exists yet.
```

## 11. Gaps

```text
G1. No adapter test plan exists yet.
G2. No adapter tests exist yet.
G3. No adapter Python module exists yet.
G4. No downstream semantic evidence binding integration exists yet.
G5. Runtime remains blocked.
G6. Phase 5 remains blocked.
G7. Product-ready remains NOT_READY.
```

## 12. Next methodological step

```text
SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_TEST_PLAN_V1
mode: TEST DESIGN ONLY
```

The next step must define tests for all upstream readiness mappings, authorization invariants, owner confirmation blocking, no forbidden imports, and semantic_binding_consideration_allowed only for `CATALOG_BINDING_READY_CANDIDATE`.

No implementation, no runtime connection, no Phase 5, no product-ready claim.

## 13. Conclusion

This adapter plan defines a read-only, fail-closed handoff boundary after the runtime catalog binding contract. It does not authorize execution and does not connect Servicio 1 to runtime.

```text
contract implementation: present
adapter plan: defined
adapter tests: not started
adapter implementation: not started
runtime connection: blocked
Phase 5: blocked
product-ready: not ready
```
