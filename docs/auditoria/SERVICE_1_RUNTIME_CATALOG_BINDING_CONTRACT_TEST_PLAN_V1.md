# SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_TEST_PLAN_V1

**Project:** PymIA / SmartPyme / Servicio 1  
**Type:** Test Design / DOC ONLY  
**Mode:** TEST DESIGN ONLY / DOC ONLY  
**Base:** `main` / `359bf31`

## Verdict

```text
VERDICT: PASS_RUNTIME_CATALOG_BINDING_CONTRACT_TEST_PLAN_DOC_CREATED
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
IMPLEMENTATION_STATUS: NOT_STARTED
PRODUCT_READY_STATUS: NOT_READY
```

This document defines the test plan for `SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1`. It does not authorize runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching, JSON mutation, Phase 5, or product-ready claims.

## 1. Purpose

Define a comprehensive test plan that validates the contract boundary governing `pathology_code -> formula_refs -> required_variables -> required_evidence -> readiness_status` without implementing runtime execution.

This test plan validates the contract as a pure, fail-closed, non-executing governance boundary.

## 2. Scope

### In scope

```text
- All 8 allowed readiness statuses
- Six-code baseline: REN_001, LIQ_001, SAL_001, STK_001, CST_001, CSH_001
- Fail-closed behavior for missing formula_refs
- Fail-closed behavior for missing required_variables
- Fail-closed behavior for missing required_evidence
- Fail-closed behavior for unavailable input artifacts
- Invariant: runtime_allowed always false
- Invariant: phase_5_allowed always false
- Priority order of status resolution rules
- Owner confirmation requirement enforcement
- Unknown pathology code handling
- Formula ref not found handling
- No new hardcoding validation
```

### Out of scope

```text
- Runtime execution
- Mapper modifications
- Engine modifications
- CLI modifications
- CASE_001 patching
- JSON catalog mutations
- Phase 5 opening
- Product-ready claims
- Column candidate binding (governed by SERVICE_1_SEMANTIC_EVIDENCE_BINDING_CONTRACTS_V1)
- Owner question generation
- Formula candidate selection
```

## 3. Relationship with existing tests

### test_service_1_semantic_catalog_consistency_v1.py

This test validates catalog structure and cross-references:

```text
- Catalog files exist
- Variable catalog has 43 variables with correct shape
- Enriched pathology catalog has 6 pathologies with correct scope
- Matrix has 6 entries with correct scope
- Formula refs match fixed scope
- Non-empty formula refs exist in formula catalog
- Semantic bindings exist in variable catalog
- No _confirmed suffix or uncataloged business_period
- Baseline pathologies do not require source catalog presence
```

This test plan does not duplicate those validations. It focuses on contract behavior.

### Dependency

```text
test_service_1_semantic_catalog_consistency_v1.py validates catalog structure.
This test plan validates contract behavior consuming those catalogs.
```

## 4. Test scenarios

### Scenario 1: Unknown pathology code

**Input:**
```text
pathology_code = "UNKNOWN_999"
```

**Expected output:**
```text
readiness_status = "UNKNOWN_PATHOLOGY_CODE"
blocking_reasons contains "pathology_code_not_in_enriched_catalog"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not invent pathology entry.
Result must not fallback to runtime hardcoding.
```

### Scenario 2: Missing formula refs (SAL_001)

**Input:**
```text
pathology_code = "SAL_001"
```

**Expected output:**
```text
readiness_status = "MISSING_FORMULA_REFS"
formula_refs = []
blocking_reasons contains "formula_refs_empty"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not promote to CATALOG_BINDING_READY_CANDIDATE.
Result must not invent formula ref.
Result must not fallback to runtime hardcoding.
```

### Scenario 3: Missing formula refs (STK_001)

**Input:**
```text
pathology_code = "STK_001"
```

**Expected output:**
```text
readiness_status = "MISSING_FORMULA_REFS"
formula_refs = []
blocking_reasons contains "formula_refs_empty"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not promote to CATALOG_BINDING_READY_CANDIDATE.
Result must not invent formula ref.
Result must not fallback to runtime hardcoding (_PATHOLOGY_TO_COMPUTATION supports STK_001 but contract must not).
```

### Scenario 4: Missing formula refs (CST_001)

**Input:**
```text
pathology_code = "CST_001"
```

**Expected output:**
```text
readiness_status = "MISSING_FORMULA_REFS"
formula_refs = []
blocking_reasons contains "formula_refs_empty"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not promote to CATALOG_BINDING_READY_CANDIDATE.
Result must not invent formula ref.
Result must not fallback to runtime hardcoding.
```

### Scenario 5: Missing formula refs (CSH_001)

**Input:**
```text
pathology_code = "CSH_001"
```

**Expected output:**
```text
readiness_status = "MISSING_FORMULA_REFS"
formula_refs = []
blocking_reasons contains "formula_refs_empty"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not promote to CATALOG_BINDING_READY_CANDIDATE.
Result must not invent formula ref.
Result must not fallback to runtime hardcoding (_PATHOLOGY_TO_COMPUTATION supports CSH_001 but contract must not).
```

### Scenario 6: Formula ref not found

**Input:**
```text
pathology_code = "REN_001"
(but simulate formula_catalog.v1.json missing REN_001_margen_neto_real)
```

**Expected output:**
```text
readiness_status = "FORMULA_REF_NOT_FOUND"
missing_formula_refs contains "REN_001_margen_neto_real"
blocking_reasons contains "formula_ref_not_in_formula_catalog"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not invent formula.
Result must not fallback to runtime hardcoding.
```

### Scenario 7: Required variable not found

**Input:**
```text
pathology_code = "REN_001"
(but simulate service_1_semantic_variable_catalog.v1.json missing sale_price)
```

**Expected output:**
```text
readiness_status = "REQUIRED_VARIABLE_NOT_FOUND"
missing_variables contains "sale_price"
blocking_reasons contains "required_variable_not_in_variable_catalog"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not invent variable.
Result must not fallback to runtime hardcoding.
```

### Scenario 8: Required evidence missing

**Input:**
```text
pathology_code = "REN_001"
(but simulate service_1_formula_pathology_evidence_matrix.v1.json missing required_evidence)
```

**Expected output:**
```text
readiness_status = "REQUIRED_EVIDENCE_MISSING"
blocking_reasons contains "required_evidence_empty_for_pathology_with_formula_refs"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not promote to CATALOG_BINDING_READY_CANDIDATE without evidence.
```

### Scenario 9: Owner confirmation required

**Input:**
```text
pathology_code = "REN_001"
(all formula refs resolve, all variables resolve, evidence present)
(but owner_confirmation_required = true in evidence matrix)
```

**Expected output:**
```text
readiness_status = "OWNER_CONFIRMATION_REQUIRED"
owner_confirmation_required = true
blocking_reasons contains "owner_confirmation_required_by_evidence_matrix"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not bypass owner confirmation.
Result must not promote to CATALOG_BINDING_READY_CANDIDATE.
```

### Scenario 10: Catalog binding ready candidate

**Input:**
```text
pathology_code = "REN_001"
(all formula refs resolve, all variables resolve, evidence present)
(owner_confirmation_required = false or confirmed)
(all input artifacts loaded successfully)
```

**Expected output:**
```text
readiness_status = "CATALOG_BINDING_READY_CANDIDATE"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
CATALOG_BINDING_READY_CANDIDATE does not authorize runtime execution.
Result must preserve runtime_allowed = false.
Result must preserve phase_5_allowed = false.
```

### Scenario 11: Fail-closed when enriched catalog unavailable

**Input:**
```text
pathology_code = "REN_001"
(but pathology_catalog.enriched.v1.json cannot be loaded)
```

**Expected output:**
```text
readiness_status = "UNKNOWN_PATHOLOGY_CODE"
blocking_reasons contains "enriched_catalog_unavailable"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not fallback to runtime hardcoding.
Result must not invent pathology entry.
```

### Scenario 12: Fail-closed when formula catalog unavailable

**Input:**
```text
pathology_code = "REN_001"
(but formula_catalog.v1.json cannot be loaded)
```

**Expected output:**
```text
readiness_status = "FORMULA_REF_NOT_FOUND"
blocking_reasons contains "formula_catalog_unavailable"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not fallback to runtime hardcoding.
Result must not invent formula.
```

### Scenario 13: Fail-closed when variable catalog unavailable

**Input:**
```text
pathology_code = "REN_001"
(but service_1_semantic_variable_catalog.v1.json cannot be loaded)
```

**Expected output:**
```text
readiness_status = "REQUIRED_VARIABLE_NOT_FOUND"
blocking_reasons contains "variable_catalog_unavailable"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not fallback to runtime hardcoding.
Result must not invent variable.
```

### Scenario 14: Fail-closed when evidence matrix unavailable

**Input:**
```text
pathology_code = "REN_001"
(but service_1_formula_pathology_evidence_matrix.v1.json cannot be loaded)
```

**Expected output:**
```text
readiness_status = "RUNTIME_BLOCKED_BY_POLICY"
blocking_reasons contains "evidence_matrix_unavailable"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not fallback to runtime hardcoding.
Result must not bypass policy block.
```

### Scenario 15: Runtime blocked by policy

**Input:**
```text
pathology_code = "REN_001"
(but runtime_connection_allowed = false in any input artifact)
```

**Expected output:**
```text
readiness_status = "RUNTIME_BLOCKED_BY_POLICY"
blocking_reasons contains "runtime_connection_blocked_by_policy"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Result must not promote to CATALOG_BINDING_READY_CANDIDATE.
Result must not authorize runtime execution.
```

### Scenario 16: No new hardcoding validation

**Input:**
```text
pathology_code = "NEW_001"
(not in six-code baseline)
```

**Expected output:**
```text
readiness_status = "UNKNOWN_PATHOLOGY_CODE"
blocking_reasons contains "pathology_code_not_in_enriched_catalog"
runtime_allowed = false
phase_5_allowed = false
```

**Invariant check:**
```text
Contract must not invent new pathology entry.
Contract must not expand _PATHOLOGY_TO_COMPUTATION.
Contract must not fallback to runtime hardcoding.
```

## 5. Test fixtures

### Fixture 1: Valid input artifacts

```text
- pathology_catalog.enriched.v1.json loaded successfully
- formula_catalog.v1.json loaded successfully
- service_1_semantic_variable_catalog.v1.json loaded successfully
- service_1_formula_pathology_evidence_matrix.v1.json loaded successfully
```

### Fixture 2: Missing enriched catalog

```text
- pathology_catalog.enriched.v1.json file does not exist or cannot be read
- Other catalogs loaded successfully
```

### Fixture 3: Missing formula catalog

```text
- formula_catalog.v1.json file does not exist or cannot be read
- Other catalogs loaded successfully
```

### Fixture 4: Missing variable catalog

```text
- service_1_semantic_variable_catalog.v1.json file does not exist or cannot be read
- Other catalogs loaded successfully
```

### Fixture 5: Missing evidence matrix

```text
- service_1_formula_pathology_evidence_matrix.v1.json file does not exist or cannot be read
- Other catalogs loaded successfully
```

### Fixture 6: Invalid formula ref

```text
- pathology_catalog.enriched.v1.json contains formula_ref not in formula_catalog.v1.json
- Other catalogs loaded successfully
```

### Fixture 7: Invalid required variable

```text
- service_1_formula_pathology_evidence_matrix.v1.json contains required_variable not in service_1_semantic_variable_catalog.v1.json
- Other catalogs loaded successfully
```

## 6. Assertions

### Assertion 1: Output shape

Every test scenario must validate the output object shape:

```text
- schema_version = "SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1"
- service_name = "SERVICE_1"
- pathology_code = input pathology_code
- catalog_origin in ("runtime_json_overlap", "runtime_only_candidate", "json_catalog")
- formula_refs is tuple of strings
- resolved_formula_ids is tuple of strings
- missing_formula_refs is tuple of strings
- required_variables is tuple of strings
- resolved_variables is tuple of strings
- missing_variables is tuple of strings
- required_evidence is tuple of strings
- minimum_semantic_bindings is tuple of strings
- owner_confirmation_required is bool
- readiness_status is one of 8 allowed statuses
- blocking_reasons is tuple of strings
- runtime_allowed is false
- phase_5_allowed is false
- metadata is dict
```

### Assertion 2: Invariant compliance

Every test scenario must validate:

```text
- runtime_allowed is always false
- phase_5_allowed is always false
- No new hardcoding introduced
- No fallback to runtime _PATHOLOGY_TO_COMPUTATION
- No invention of missing pathology, formula, or variable
```

### Assertion 3: Status priority

For scenarios where multiple blocking conditions apply, validate priority order:

```text
1. UNKNOWN_PATHOLOGY_CODE (highest priority)
2. MISSING_FORMULA_REFS
3. FORMULA_REF_NOT_FOUND
4. REQUIRED_VARIABLE_NOT_FOUND
5. REQUIRED_EVIDENCE_MISSING
6. OWNER_CONFIRMATION_REQUIRED
7. RUNTIME_BLOCKED_BY_POLICY
8. CATALOG_BINDING_READY_CANDIDATE (lowest priority)
```

## 7. Fail-closed validation rules

### Rule 1: Missing formula refs

```text
If formula_refs is empty tuple:
- readiness_status must be MISSING_FORMULA_REFS
- Result must not promote to CATALOG_BINDING_READY_CANDIDATE
- Result must not fallback to runtime hardcoding
```

### Rule 2: Owner confirmation required

```text
If owner_confirmation_required is true:
- readiness_status must be OWNER_CONFIRMATION_REQUIRED
- Result must not bypass owner confirmation
- Result must not promote to CATALOG_BINDING_READY_CANDIDATE
```

### Rule 3: Invalid formula ref

```text
If any formula_ref does not resolve in formula_catalog.v1.json:
- readiness_status must be FORMULA_REF_NOT_FOUND
- Result must not invent formula
- Result must not fallback to runtime hardcoding
```

### Rule 4: Invalid required variable

```text
If any required_variable does not resolve in service_1_semantic_variable_catalog.v1.json:
- readiness_status must be REQUIRED_VARIABLE_NOT_FOUND
- Result must not invent variable
- Result must not fallback to runtime hardcoding
```

### Rule 5: Unavailable input artifact

```text
If any input artifact cannot be loaded:
- readiness_status must fail closed per contract fail-closed rules
- Result must not fallback to runtime hardcoding
- Result must not invent missing artifact
```

## 8. Prohibited test behaviors

The following test behaviors are prohibited:

```text
P1. Tests that patch runtime to make behavior pass
P2. Tests that mock _PATHOLOGY_TO_COMPUTATION to validate contract
P3. Tests that invent missing pathology, formula, or variable
P4. Tests that bypass owner confirmation requirement
P5. Tests that promote MISSING_FORMULA_REFS to CATALOG_BINDING_READY_CANDIDATE
P6. Tests that authorize runtime execution
P7. Tests that open Phase 5
P8. Tests that declare product-ready status
P9. Tests that modify JSON catalogs
P10. Tests that duplicate test_service_1_semantic_catalog_consistency_v1.py validations
```

## 9. Certified facts

From contract design and input artifacts:

```text
CF1. SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1 exists and defines 8 allowed statuses.
CF2. Contract consumes 4 input artifacts: enriched pathology catalog, formula catalog, variable catalog, evidence matrix.
CF3. Contract output shape is documented with all required fields.
CF4. Contract invariants require runtime_allowed=false and phase_5_allowed=false always.
CF5. Contract fail-closed rules are documented for all input artifact unavailability cases.
CF6. Priority order of status resolution is documented.
CF7. Six-code baseline is fixed: REN_001, LIQ_001, SAL_001, STK_001, CST_001, CSH_001.
CF8. SAL_001, STK_001, CST_001, CSH_001 have empty formula_refs in evidence matrix.
CF9. REN_001 and LIQ_001 have non-empty formula_refs that resolve in formula catalog.
CF10. Runtime connection remains blocked by migration plan and loader audit.
```

## 10. Hypotheses

```text
H1. Test scenarios can validate contract behavior without implementing runtime execution.
H2. Fail-closed behavior can be validated through fixture manipulation without runtime changes.
H3. Status priority order can be validated through multi-condition scenarios.
H4. No-new-hardcoding invariant can be validated through unknown pathology code scenarios.
```

## 11. Gaps

```text
G1. Contract implementation does not exist yet; test plan validates design only.
G2. Test fixtures for unavailable input artifacts require file system manipulation or mocking.
G3. Priority order validation requires multi-condition scenarios that may not exist in current catalog state.
G4. Owner confirmation bypass scenario requires evidence matrix mutation.
G5. Integration with SERVICE_1_SEMANTIC_EVIDENCE_BINDING_CONTRACTS_V1 not yet defined.
```

## 12. Next methodological step

```text
SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_TESTS_V1
mode: TEST ONLY
```

The next step must create tests that validate this test plan's scenarios using:

```text
- Fixture setup for all 16 scenarios
- Output shape validation for all scenarios
- Invariant compliance validation for all scenarios
- Status priority validation for multi-condition scenarios
- Fail-closed behavior validation for unavailable input artifacts
- No-new-hardcoding validation for unknown pathology codes
```

No implementation, no runtime connection, no Phase 5, no product-ready claim.

## 13. Conclusion

This test plan defines comprehensive coverage for `SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1` without authorizing runtime execution, mapper changes, engine changes, CLI changes, CASE_001 patching, JSON mutation, Phase 5, or product-ready claims.

The test plan validates:

```text
- All 8 allowed readiness statuses
- Six-code baseline behavior
- Fail-closed behavior for missing formula_refs, required_variables, required_evidence
- Fail-closed behavior for unavailable input artifacts
- Invariant compliance (runtime_allowed=false, phase_5_allowed=false)
- Status priority order
- No-new-hardcoding validation
```

Servicio 1 may advance only by tested, fail-closed boundaries. This test plan is a governance artifact, not an execution authorization.
