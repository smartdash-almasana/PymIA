# SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1

**Project:** PymIA / SmartPyme / Servicio 1  
**Type:** Contract Design / DOC ONLY  
**Mode:** CONTRACT DESIGN ONLY / DOC ONLY  
**Base:** `main` / `ba29257`  

## Verdict

```text
VERDICT: PASS_RUNTIME_CATALOG_BINDING_CONTRACT_DOC_CREATED
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
IMPLEMENTATION_STATUS: NOT_STARTED
PRODUCT_READY_STATUS: NOT_READY
```

This document defines the contract boundary governing `pathology_code -> formula_refs -> required_variables -> required_evidence -> readiness_status`. It does not authorize runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching, JSON mutation, Phase 5, or product-ready claims.

## 1. Purpose

Define a pure, fail-closed, non-executing contract boundary that resolves whether a given `pathology_code` has sufficient catalog governance to become a runtime candidate in the future.

This contract operates **upstream** of `SERVICE_1_SEMANTIC_EVIDENCE_BINDING_CONTRACTS_V1`.

The governance chain is:

```text
pathology_code
→ formula_refs (from pathology_catalog.enriched.v1.json)
→ formula existence (in formula_catalog.v1.json)
→ required_variables (from formula + variable catalog)
→ variable existence (in service_1_semantic_variable_catalog.v1.json)
→ required_evidence (from formula catalog or evidence matrix)
→ owner_confirmation_required (from evidence matrix)
→ readiness_status (output of this contract)
```

## 2. Non-goals

The following are explicitly out of scope for this contract:

```text
column candidates
variable bindings
owner questions generation
formula candidate selection
mapper modifications
engine modifications
runtime execution authorization
CASE_001 patching
Phase 5 opening
product-ready declaration
allowed-computation hardcoding expansion
JSON catalog mutation
```

This contract does not replace or duplicate `SERVICE_1_SEMANTIC_EVIDENCE_BINDING_CONTRACTS_V1`.

## 3. Relationship with SERVICE_1_SEMANTIC_EVIDENCE_BINDING_CONTRACTS_V1

The two contracts govern different layers:

**This contract (RUNTIME_CATALOG_BINDING):**

```text
pathology_code -> formula_refs -> required_variables -> required_evidence -> readiness_status
```

Governance question: *Does the catalog have sufficient structure to authorize future runtime consideration?*

**Semantic Evidence Binding contract (downstream):**

```text
column candidates -> variable bindings -> owner questions -> formula candidate -> binding status
```

Governance question: *Given a readiness candidate, do observed columns bind to required variables with sufficient evidence?*

Dependency rule:

```text
This contract must emit readiness before the semantic evidence binding contract may consider runtime candidacy.
Catalog consistency does not equal runtime readiness.
Readiness does not equal execution authorization.
```

## 4. Input artifacts

This contract consumes exactly these artifacts as input:

```text
PymIA-Live/docs/pathology_catalog.enriched.v1.json
PymIA-Live/docs/formula_catalog.v1.json
PymIA-Live/docs/service_1_semantic_variable_catalog.v1.json
PymIA-Live/docs/service_1_formula_pathology_evidence_matrix.v1.json
```

No other input is permitted. No runtime state, no observed XLSX columns, no owner answers, no mapper output, no engine output.

## 5. Contract boundary

Input:

```text
pathology_code: str
```

Output:

```text
Service1RuntimeCatalogBindingResultV1 (documental object shape)
```

The contract is a pure function of catalog state. It has no side effects, no I/O beyond reading input artifacts, and no runtime authorization.

## 6. Output object shape (documental)

```text
{
  "schema_version": "SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1",
  "service_name": "SERVICE_1",
  "pathology_code": str,
  "catalog_origin": "runtime_json_overlap" | "runtime_only_candidate" | "json_catalog",
  "formula_refs": tuple[str, ...],
  "resolved_formula_ids": tuple[str, ...],
  "missing_formula_refs": tuple[str, ...],
  "required_variables": tuple[str, ...],
  "resolved_variables": tuple[str, ...],
  "missing_variables": tuple[str, ...],
  "required_evidence": tuple[str, ...],
  "minimum_semantic_bindings": tuple[str, ...],
  "owner_confirmation_required": bool,
  "readiness_status": str,
  "blocking_reasons": tuple[str, ...],
  "runtime_allowed": false,
  "phase_5_allowed": false,
  "metadata": dict
}
```

All authorization flags remain `false` by invariant.

## 7. Allowed statuses

The `readiness_status` field must emit exactly one of:

```text
CATALOG_BINDING_READY_CANDIDATE
MISSING_FORMULA_REFS
UNKNOWN_PATHOLOGY_CODE
FORMULA_REF_NOT_FOUND
REQUIRED_VARIABLE_NOT_FOUND
REQUIRED_EVIDENCE_MISSING
OWNER_CONFIRMATION_REQUIRED
RUNTIME_BLOCKED_BY_POLICY
```

Status resolution rules:

```text
1. If pathology_code is not in pathology_catalog.enriched.v1.json:
   → UNKNOWN_PATHOLOGY_CODE

2. If formula_refs is empty tuple:
   → MISSING_FORMULA_REFS

3. If any formula_ref does not resolve in formula_catalog.v1.json:
   → FORMULA_REF_NOT_FOUND

4. If any required_variable does not resolve in service_1_semantic_variable_catalog.v1.json:
   → REQUIRED_VARIABLE_NOT_FOUND

5. If required_evidence is empty tuple for a pathology with formula refs:
   → REQUIRED_EVIDENCE_MISSING

6. If owner_confirmation_required is true:
   → OWNER_CONFIRMATION_REQUIRED

7. If runtime_connection_allowed is false in any input artifact:
   → RUNTIME_BLOCKED_BY_POLICY

8. Otherwise:
   → CATALOG_BINDING_READY_CANDIDATE
```

Priority order: 1 > 2 > 3 > 4 > 5 > 6 > 7 > 8.

## 8. Invariants

The following invariants must hold for every invocation:

```text
I1. runtime_allowed is always false.
I2. phase_5_allowed is always false.
I3. No new hardcoding of pathology-to-computation mappings.
I4. No expansion of _PATHOLOGY_TO_COMPUTATION to make catalog gaps disappear.
I5. SAL_001, STK_001, CST_001, CSH_001 emit MISSING_FORMULA_REFS unless formula_refs become non-empty in enriched catalog.
I6. Catalog consistency does not imply runtime readiness.
I7. Readiness does not imply execution authorization.
I8. All input artifacts are read-only; no mutation.
I9. No side effects beyond returning the documental result.
I10. Six-code baseline is fixed: REN_001, LIQ_001, SAL_001, STK_001, CST_001, CSH_001.
```

## 9. Fail-closed rules

The contract must fail closed in the following cases:

```text
F1. If pathology_catalog.enriched.v1.json cannot be loaded → UNKNOWN_PATHOLOGY_CODE with blocking_reason "enriched_catalog_unavailable".
F2. If formula_catalog.v1.json cannot be loaded → FORMULA_REF_NOT_FOUND with blocking_reason "formula_catalog_unavailable".
F3. If service_1_semantic_variable_catalog.v1.json cannot be loaded → REQUIRED_VARIABLE_NOT_FOUND with blocking_reason "variable_catalog_unavailable".
F4. If service_1_formula_pathology_evidence_matrix.v1.json cannot be loaded → RUNTIME_BLOCKED_BY_POLICY with blocking_reason "evidence_matrix_unavailable".
F5. If formula_refs is empty → MISSING_FORMULA_REFS, never silently promote to candidate.
F6. If owner_confirmation_required is true → OWNER_CONFIRMATION_REQUIRED, never bypass.
F7. If any required_variable is not in variable catalog → REQUIRED_VARIABLE_NOT_FOUND, never invent variable.
F8. If any formula_ref is not in formula catalog → FORMULA_REF_NOT_FOUND, never invent formula.
```

No fallback to hardcoded runtime behavior is permitted.

## 10. Prohibited uses

The following uses of this contract are prohibited:

```text
P1. Using this contract to authorize runtime execution.
P2. Using this contract to bypass semantic evidence binding.
P3. Using this contract to force CASE_001 to pass.
P4. Using this contract to expand allowed-computation hardcoding.
P5. Using this contract to declare product-ready status.
P6. Using this contract to modify JSON catalogs.
P7. Using this contract to open Phase 5.
P8. Using this contract to connect mapper or engine to XLSX-first entrypoint.
P9. Treating CATALOG_BINDING_READY_CANDIDATE as execution authorization.
P10. Treating readiness as diagnosis.
```

## 11. Certified facts

From input artifacts and prior audits:

```text
CF1. pathology_catalog.enriched.v1.json exists with 6 pathologies and runtime_status="not_allowed" for all.
CF2. formula_catalog.v1.json exists with 18 formulas; REN_001_margen_neto_real and LIQ_001_vendido_cobrado resolve for REN_001 and LIQ_001.
CF3. service_1_semantic_variable_catalog.v1.json exists with 43 variables and status CATALOG_ONLY_NOT_RUNTIME.
CF4. service_1_formula_pathology_evidence_matrix.v1.json exists with 6 entries; SAL_001, STK_001, CST_001, CSH_001 have empty formula_refs.
CF5. Runtime connection remains blocked by SERVICE_1_RUNTIME_CATALOG_MIGRATION_PLAN_V1 and SERVICE_1_RUNTIME_CATALOG_LOADER_AUDIT_V1.
CF6. Phase 5 remains blocked.
CF7. Product-ready status remains NOT_READY.
CF8. _PATHOLOGY_TO_COMPUTATION in runtime hardcodes REN_001, LIQ_001, STK_001, CSH_001; does not support SAL_001 or CST_001.
CF9. SAL_001 exists in runtime triage path but not in allowed-computation and not in JSON pathology catalog.
CF10. STK_001 and CSH_001 are hardcoded in allowed-computation despite having no formula refs in semantic baseline.
```

## 12. Hypotheses

```text
H1. This contract can serve as a pure readiness gate before semantic evidence binding considers runtime candidacy.
H2. Fail-closed behavior for missing formula_refs can prevent silent promotion of SAL_001, STK_001, CST_001, CSH_001.
H3. A future adapter can consume this contract output without authorizing execution.
H4. Explicit OWNER_CONFIRMATION_REQUIRED status can force owner meaning into the binding chain before computation.
```

## 13. Gaps

```text
G1. SAL_001 has no formula refs and no required_variables in evidence matrix; emits MISSING_FORMULA_REFS by invariant.
G2. STK_001 has no formula refs and no required_variables in evidence matrix; emits MISSING_FORMULA_REFS by invariant.
G3. CST_001 has no formula refs and no required_variables in evidence matrix; emits MISSING_FORMULA_REFS by invariant.
G4. CSH_001 has no formula refs and no required_variables in evidence matrix; emits MISSING_FORMULA_REFS by invariant.
G5. Runtime _PATHOLOGY_TO_COMPUTATION still hardcodes STK_001 and CSH_001 despite catalog gap.
G6. No test yet validates this contract boundary against the six-code baseline.
G7. No adapter yet consumes this contract output.
G8. No integration exists between this contract and SERVICE_1_SEMANTIC_EVIDENCE_BINDING_CONTRACTS_V1.
```

## 14. Next methodological step

```text
SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_TEST_PLAN_V1
mode: TEST DESIGN ONLY
```

The test plan must validate:

```text
- UNKNOWN_PATHOLOGY_CODE for codes outside six-code baseline
- MISSING_FORMULA_REFS for SAL_001, STK_001, CST_001, CSH_001
- CATALOG_BINDING_READY_CANDIDATE for REN_001 and LIQ_001 (after owner confirmation path)
- FORMULA_REF_NOT_FOUND for invalid formula refs
- REQUIRED_VARIABLE_NOT_FOUND for invalid variables
- Fail-closed behavior when input artifacts are unavailable
- Invariant: runtime_allowed and phase_5_allowed always false
- Invariant: no new hardcoding
```

No implementation, no runtime connection, no Phase 5, no product-ready claim.

## 15. Conclusion

This contract defines a pure, fail-closed, non-executing boundary for catalog governance. It does not authorize runtime, does not force CASE_001, does not expand hardcoding, and does not declare product-ready.

The correct posture remains:

```text
catalog baseline: present
catalog consistency: passing (for REN_001, LIQ_001)
catalog gaps: governed (SAL_001, STK_001, CST_001, CSH_001)
runtime/catalog binding contract: defined
runtime connection: blocked
Phase 5: blocked
implementation: not started
product-ready: not ready
```

Servicio 1 may advance only by tested, fail-closed boundaries. This contract is a governance artifact, not an execution authorization.
