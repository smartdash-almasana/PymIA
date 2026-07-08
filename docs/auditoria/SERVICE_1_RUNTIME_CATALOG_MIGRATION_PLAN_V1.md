# SERVICE_1_RUNTIME_CATALOG_MIGRATION_PLAN_V1

**Project:** PymIA / SmartPyme / Servicio 1  
**Type:** Runtime/catalog controlled migration plan  
**Mode:** DOC ONLY / DESIGN ONLY  
**Base:** `main` / `829d857`  

## Verdict

```text
VERDICT: MIGRATION_PLAN_ONLY
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
IMPLEMENTATION_STATUS: NOT_STARTED
PRODUCT_READY_STATUS: NOT_READY
```

This document defines a controlled migration path from the current partially hardcoded Servicio 1 runtime toward a catalog-governed runtime. It does not authorize runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching, Phase 5, or any product-ready claim.

## 1. Certified current state

```text
branch: main
HEAD: 829d857
local_main_equals_origin_main: reported/certified by previous synchronization context
semantic_baseline_status: integrated
focal_test: PymIA-Live/tests/smartpyme/test_service_1_semantic_catalog_consistency_v1.py
focal_test_result: 9 passed
runtime_status: blocked
phase_5_status: blocked
product_ready_status: not_ready
```

The semantic baseline exists as catalog and documentation evidence only. It does not change productive runtime behavior.

## 2. Existing pieces

The migration plan is constrained by these existing artifacts:

```text
PymIA-Live/docs/formula_catalog.v1.json
PymIA-Live/docs/pathology_catalog.v1.json
PymIA-Live/docs/service_1_semantic_variable_catalog.v1.json
PymIA-Live/docs/pathology_catalog.enriched.v1.json
PymIA-Live/docs/service_1_formula_pathology_evidence_matrix.v1.json
PymIA-Live/tests/smartpyme/test_service_1_semantic_catalog_consistency_v1.py
docs/auditoria/SERVICE_1_SEMANTIC_CATALOG_COVERAGE_AUDIT_V1.md
docs/auditoria/SERVICE_1_RUNTIME_CATALOG_RECONCILIATION_V1.md
```

Current catalog facts:

- `service_1_semantic_variable_catalog.v1.json` has `43` variables and is marked `CATALOG_ONLY_NOT_RUNTIME`.
- `manual_time` and `automated_time` are semantic variables with `required_data_type: "number"` and `unit: "time"`.
- `pathology_catalog.enriched.v1.json` fixes the Servicio 1 baseline scope and marks runtime connection as not allowed.
- `service_1_formula_pathology_evidence_matrix.v1.json` records formula refs, required variables, required evidence, owner confirmation requirements, and blocked runtime status.

## 3. Fixed pathology baseline

The six base pathologies are not reopened by this migration plan:

```text
REN_001
LIQ_001
SAL_001
STK_001
CST_001
CSH_001
```

Current formula refs:

| Pathology | Formula refs | Status |
|---|---:|---|
| `REN_001` | `REN_001_margen_neto_real` | Cataloged, not runtime-ready |
| `LIQ_001` | `LIQ_001_vendido_cobrado` | Cataloged, not runtime-ready |
| `SAL_001` | none | Governed semantic gap |
| `STK_001` | none | Governed semantic gap |
| `CST_001` | none | Governed semantic gap |
| `CSH_001` | none | Governed semantic gap |

`SAL_001`, `STK_001`, `CST_001`, and `CSH_001` must not be deleted or silently promoted. They remain accepted baseline semantic entries without formula refs. Their current state is a governed gap, not a scope error.

## 4. Current breach / fracture

Servicio 1 still has a runtime/catalog fracture:

```text
XLSX runtime
+ triage behavior
+ formula_catalog
+ pathology_catalog
+ mapper
+ engine
+ dry run
!= governed runtime/catalog authority
```

The missing governed chain remains:

```text
observed XLSX columns
→ semantic meaning
→ formula variables
→ required evidence
→ pathology candidates
→ owner questions
→ consolidated semantic map
→ computation candidate
→ operational finding
```

The current runtime must not be connected yet because catalog consistency does not prove runtime readiness.

## 5. Migration phases

### Phase A — Existing loader audit

**Mode:** AUDIT ONLY  
**Runtime impact:** none

Objective:

```text
Identify every existing loader or reader that touches formula, pathology, semantic variable, evidence matrix, mapper, engine, dry run, or XLSX runtime behavior.
```

Required output:

```text
SERVICE_1_RUNTIME_CATALOG_LOADER_AUDIT_V1
```

Must classify each loader as:

```text
catalog_reader
runtime_reader
mapper_dependency
engine_dependency
test_only
legacy_or_unreferenced
unknown
```

Stop condition:

```text
Any unknown loader that influences runtime must block migration.
```

### Phase B — pathology_code -> formula_refs -> required_variables contract

**Mode:** CONTRACT DESIGN ONLY  
**Runtime impact:** none

Objective:

```text
Define a pure contract that maps pathology_code to formula_refs, formula_refs to required_variables, and required_variables to required_evidence.
```

Required invariants:

- pathology codes must belong to the six-code baseline.
- formula refs must resolve to `formula_catalog.v1.json`.
- required variables must resolve to `service_1_semantic_variable_catalog.v1.json`.
- required evidence must be carried from the evidence matrix or formula catalog.
- missing formula refs must fail closed for runtime authorization.
- no new hardcoding is allowed.

Expected artifact:

```text
SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1
```

### Phase C — Runtime characterization test without changing runtime

**Mode:** TEST ONLY  
**Runtime impact:** none

Objective:

```text
Capture current runtime/catalog behavior as it exists before any migration.
```

The test must prove one of the following states:

```text
PASS_KNOWN_CURRENT_BEHAVIOR
KNOWN_GAP_RUNTIME_NOT_CATALOG_DRIVEN
BLOCKED_UNCLEAR_RUNTIME_BEHAVIOR
```

It must not patch runtime to make behavior pass.

Required output:

```text
SERVICE_1_RUNTIME_CATALOG_CHARACTERIZATION_TEST_V1
```

### Phase D — Read-only catalog adapter

**Mode:** READ-ONLY ADAPTER / NO EXECUTION AUTHORIZATION  
**Runtime impact:** observational only

Objective:

```text
Create an adapter that reads catalog artifacts and returns structured catalog facts without authorizing execution.
```

Adapter rules:

- read catalog data only;
- expose explicit readiness status;
- never compute business findings;
- never authorize formula execution;
- fail closed on missing formula refs;
- preserve `runtime_connection_allowed: false` until an explicit authorization document changes it.

Expected state:

```text
adapter_reads_catalog: yes
adapter_authorizes_runtime: no
adapter_changes_mapper: no
adapter_changes_engine: no
adapter_changes_cli: no
```

### Phase E — Catalog-driven readiness gate

**Mode:** GATE DESIGN / TESTED BOUNDARY  
**Runtime impact:** blocks only

Objective:

```text
Introduce a readiness gate that decides whether a pathology/formula/evidence tuple is eligible for a future computation candidate.
```

The gate must produce explicit statuses such as:

```text
CATALOG_READY_FOR_CHARACTERIZATION
MISSING_FORMULA_REFS
MISSING_REQUIRED_VARIABLES
MISSING_REQUIRED_EVIDENCE
OWNER_CONFIRMATION_REQUIRED
RUNTIME_BLOCKED_BY_POLICY
UNKNOWN_PATHOLOGY_CODE
```

The gate may block. It must not execute.

### Phase F — Later mapper/engine integration evaluation

**Mode:** EVALUATION ONLY until explicitly authorized  
**Runtime impact:** none unless a later document authorizes implementation

Objective:

```text
Evaluate whether mapper and engine can consume catalog-governed readiness outputs without semantic hardcoding or CASE_001 patching.
```

This phase is not opened by the current document. It requires prior evidence from Phases A through E.

## 6. Mandatory gates before touching runtime

Runtime, mapper, engine, CLI, CASE_001, or Phase 5 may not be touched until all of the following are true:

```text
catalog_consistency_test: PASS
runtime_characterization_test: PASS or KNOWN_GAP
explicit_runtime_migration_authorization_document: present
fail_closed_missing_formula_refs: tested
no_new_hardcoding: verified
mapper_contract: defined
engine_contract: defined
owner_confirmation_path: defined
```

Additional required evidence:

- exact files read;
- exact files changed;
- test command output;
- documented known gaps;
- explicit statement that product-ready status remains `NOT_READY`.

## 7. Prohibitions

The following are prohibited during this migration planning stage:

```text
new hardcoding
CASE_001 patch to force pass
engine connection
mapper modification
CLI modification
runtime behavior change
GitHub Actions change
JSON catalog mutation
Phase 5 opening
product-ready claim
```

The runtime must not become catalog-driven by implication. Promotion requires an explicit authorization artifact and tests.

## 8. Certified facts / hypotheses / gaps / next methodological step

### Certified facts

- Baseline semantic catalog artifacts exist on `829d857`.
- The consistency test exists and has certified focal result `9 passed`.
- Runtime connection remains blocked.
- Phase 5 remains blocked.
- Product-ready status remains not ready.
- Six pathology codes govern the current Servicio 1 semantic baseline.

### Hypotheses

- A read-only adapter can reduce runtime/catalog drift without authorizing execution.
- A characterization test can freeze current runtime behavior before migration.
- A catalog-driven readiness gate can safely block incomplete pathology/formula/evidence tuples.

### Gaps

- Runtime behavior has not yet been characterized against the catalog baseline.
- Loader boundaries have not yet been audited.
- No contract yet governs `pathology_code -> formula_refs -> required_variables -> required_evidence` as a runtime-adjacent boundary.
- `SAL_001`, `STK_001`, `CST_001`, and `CSH_001` have no formula refs yet.

### Next methodological step

```text
SERVICE_1_RUNTIME_CATALOG_CHARACTERIZATION_TEST_V1
mode: TEST ONLY
```

The next step should create a characterization test that records current runtime/catalog behavior without changing runtime.

## 9. Conclusion

The correct migration posture is conservative:

```text
catalog baseline: present
catalog consistency: passing
runtime/catalog migration: planned only
runtime connection: blocked
Phase 5: blocked
implementation: not started
product-ready: not ready
```

Servicio 1 may advance only by tested, fail-closed boundaries. The catalog can inform future runtime governance, but it does not currently authorize computation, mapper decisions, engine decisions, CLI behavior, CASE_001 promotion, or product claims.
