# SERVICE_1_RUNTIME_CATALOG_LOADER_AUDIT_V1

**Project:** PymIA / SmartPyme / Servicio 1  
**Type:** Runtime/catalog loader audit  
**Mode:** AUDIT ONLY / DOC ONLY  
**Base:** `main` / `829d857`

## Verdict

```text
VERDICT: PASS_RUNTIME_CATALOG_LOADER_AUDIT_DOC_CREATED
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
IMPLEMENTATION_STATUS: NOT_STARTED
PRODUCT_READY_STATUS: NOT_READY
```

This document audits the current Servicio 1 catalog/runtime loader surface before any binding contract or runtime migration. It does not authorize runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching, JSON mutation, Phase 5, or product-ready claims.

## 1. Pre-flight evidence

### Repository state before writing

```text
git status --short
?? docs/auditoria/SERVICE_1_RUNTIME_CATALOG_MIGRATION_PLAN_V1.md
```

### Recent commits inspected

```text
829d857 docs(smartpyme): add service 1 semantic catalog baseline
fa5c359 feat(pymia-live): add service 1 semantic evidence binding engine
073920d feat(pymia-live): add service 1 column semantic mapper
31add3d feat(pymia-live): add service 1 semantic catalog loader
9a925f2 docs(pymia): document service 1 semantic binding recovery
d3e6c39 feat(pymia-live): add service 1 semantic evidence binding contracts
2b3291a test(pymia-live): characterize service 1 semantic binding gap
a8a0fcd docs(pymia): align service 1 operator principle
b7872e3 docs(pymia): close service 1 operative xlsx first
a71a50f docs(pymia): add service 1 real client operator runbook
ca4726f fix(pymia-live): sanitize service 1 delivery case folder names
ffc62c9 test(pymia-live): add service 1 delivery packet folder smoke
```

### Duplicate check

```text
search_files_by_name SERVICE_1_RUNTIME_CATALOG_LOADER_AUDIT_V1.md -> 0 results
search_text RUNTIME_CATALOG_LOADER_AUDIT under docs -> only migration plan mention
```

Conclusion: no material duplicate audit document exists.

## 2. Sources read

```text
AGENTS.md
ARCHITECTURE_GUARDRAILS.md
docs/current/README.md
docs/auditoria/SERVICE_1_RUNTIME_CATALOG_MIGRATION_PLAN_V1.md
docs/auditoria/SERVICE_1_RUNTIME_CATALOG_RECONCILIATION_V1.md
PymIA-Live/tests/smartpyme/test_service_1_case_001_semantic_binding_gap_v1.py
PymIA-Live/pymia/smartpyme/service_1_semantic_catalog_loader_v1.py
PymIA-Live/pymia/smartpyme/service_1_column_semantic_mapper_v1.py
PymIA-Live/pymia/smartpyme/service_1_semantic_evidence_binding_engine_v1.py
PymIA-Live/pymia/smartpyme/service_1_pathology_to_allowed_computation_candidate_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_first_product_entrypoint_v1.py
```

## 3. Governing constraints certified from sources

From `AGENTS.md` and `ARCHITECTURE_GUARDRAILS.md`:

- Physical code, tests, and repo docs govern over memory.
- Certified facts, hypotheses, gaps, and next methodological step must remain separated.
- If the technical contract is missing, code implementation must not start.
- Runtime, evidence, learning, and architecture are separate layers.
- No product-ready claim is allowed for internal or assisted capabilities without evidence.
- PymIA computes; the LLM communicates.

From `docs/current/README.md`:

- `docs/current/` governs over historical docs.
- Operational authority is in `docs/current/`, `PymIA-Live/pymia/smartpyme/`, and `PymIA-Live/pymia/contracts/`.
- `landing/` does not govern Servicio 1.

From the migration/reconciliation docs:

- Runtime connection is blocked.
- Phase 5 is blocked.
- Product-ready status is not ready.
- The six-code baseline is fixed: `REN_001`, `LIQ_001`, `SAL_001`, `STK_001`, `CST_001`, `CSH_001`.
- Catalog consistency does not prove runtime readiness.
- `SAL_001`, `STK_001`, `CST_001`, and `CSH_001` are governed gaps when formula refs are absent.

## 4. Loader and runtime-surface classification

| Artifact | Classification | Certified behavior | Runtime/catalog implication |
|---|---|---|---|
| `service_1_semantic_catalog_loader_v1.py` | `catalog_reader` | Reads JSON catalog files from explicit paths using `json.loads`; supports formula entries and pathology entries; normalizes to dataclasses; enforces false flags for `runtime_authorized`, `tool_execution_authorized`, `delivery_authorized`, and `diagnosis_generated`. | Safe as read-only catalog reader for source formula/pathology catalogs; not a runtime authorization boundary. |
| `load_service_1_formula_catalog_v1` | `catalog_reader` | Loads entries under `formulas` and returns normalized formula entries. | Reads formula catalog only; does not bind to runtime. |
| `load_service_1_pathology_catalog_v1` | `catalog_reader` | Loads entries under `pathologies` and returns normalized pathology entries. | Reads pathology catalog only; does not bind to runtime. |
| `build_service_1_semantic_catalog_load_result_v1` | `catalog_reader` | Loads formula and pathology catalogs; returns loaded/partial/blocked statuses; fails closed on missing/invalid catalogs; does not authorize execution. | Candidate source for future binding contract input, but currently limited to formula + pathology catalogs. |
| `service_1_column_semantic_mapper_v1.py` | `mapper_dependency` | Imports `ColumnConfirmationEntry`, `ColumnConfirmationMatrix`, and `Service1ColumnSemanticCandidateV1`; maps normalized column names through `_MAPPING_BY_NORMALIZED_COLUMN`; returns candidates with runtime/tool/delivery/diagnosis flags false. | Mapper is hardcoded by column-name map; it does not read semantic catalogs or the formula/pathology matrix. |
| `build_service_1_column_semantic_candidate_v1` | `mapper_dependency` | Converts a confirmed column entry into semantic role and variable candidate. Ambiguous/unknown mappings require owner confirmation. | Useful for future semantic binding, but not catalog-governed yet. |
| `build_service_1_column_semantic_candidates_from_matrix_v1` | `mapper_dependency` | Converts a `ColumnConfirmationMatrix` into semantic candidates. | Adapter from column confirmation to semantic candidates; not wired to XLSX-first runtime in the inspected entrypoint. |
| `service_1_semantic_evidence_binding_engine_v1.py` | `engine_dependency` | Consumes normalized formula/pathology catalog entries and column semantic candidates; creates formula variable bindings, owner questions, pathology formula candidates, and binding result. | Engine exists and is catalog-adjacent, but inspection of XLSX-first entrypoint shows it is not part of the current runtime chain. |
| `build_service_1_semantic_evidence_binding_result_v1` | `engine_dependency` | Iterates formula entries, matches pathology entries by code, binds required variables to column candidates, emits ready formula IDs or owner/missing-input statuses. | Future bridge candidate. Current use does not authorize runtime execution. |
| `service_1_pathology_to_allowed_computation_candidate_v1.py` | `runtime_reader` | Uses `_PATHOLOGY_TO_COMPUTATION` hardcoded dictionary for `REN_001`, `LIQ_001`, `STK_001`, and `CSH_001`; uses `_FIELD_ALIASES`; returns runtime/reexecution/recalculation/delivery flags false. | Runtime-adjacent hardcoded computation selection. Not catalog-driven. Does not support `SAL_001` or `CST_001`. |
| `_PATHOLOGY_TO_COMPUTATION` | `runtime_reader` | Hardcodes computation refs and required fields. | Main catalog/runtime fracture point. Must not be treated as catalog authority. |
| `service_1_xlsx_first_product_entrypoint_v1.py` | `runtime_reader` | Composes triage entrypoint, allowed computation, evidence readiness gate, computation plan, dry run, owner view, policy guard, and package candidate. | Official pure XLSX-first runtime-adjacent entrypoint; it does not import semantic catalog loader, mapper, or semantic binding engine. |
| `build_service_1_xlsx_first_product_entrypoint_v1` | `runtime_reader` | Stops with next owner question, blocked result, or delivery package candidate; flags runtime/reexecution/recalculation/delivery false. | Current runtime chain remains disconnected from semantic catalog/binding engine. |
| `test_service_1_case_001_semantic_binding_gap_v1.py` | `test_only` | Characterizes current CASE_001 behavior: stops at triage, selects `SAL_001`, `allowed_computation_ref` is `None`, no package, trace only `triage_entrypoint_status`, flags false. | Existing test evidence. Do not duplicate characterization. |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_MIGRATION_PLAN_V1.md` | `test_only` / audit input | Defines migration plan and stop gates; still says runtime connection blocked. | Design-only authority, not implementation authority. |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_RECONCILIATION_V1.md` | `test_only` / audit input | Records runtime/catalog fracture and prohibits runtime connection. | Audit evidence only. |
| `formula_catalog.v1.json` | `catalog_reader` input | Referenced by loader and catalog baseline; formula definitions source. | Input artifact only; existence does not authorize execution. |
| `pathology_catalog.v1.json` | `catalog_reader` input | Referenced by loader and source pathology catalog. | Input artifact only. |
| `service_1_semantic_variable_catalog.v1.json` | `unknown` for current loader | Present in baseline, but the inspected loader does not read it. | Needs binding contract or loader extension design; do not connect by implication. |
| `pathology_catalog.enriched.v1.json` | `unknown` for current loader | Present in baseline, but the inspected loader does not read it. | Needs binding contract or loader extension design; do not connect by implication. |
| `service_1_formula_pathology_evidence_matrix.v1.json` | `unknown` for current loader | Present in baseline, but the inspected loader does not read it. | Central future binding artifact; currently not consumed by inspected runtime/loader. |

## 5. Certified facts

1. A semantic catalog loader exists, but it currently reads only formula and pathology catalogs through explicit path parameters.
2. The loader returns fail-closed flags: runtime, tool execution, delivery, and diagnosis remain false.
3. A column semantic mapper exists, but its mapping surface is hardcoded through `_MAPPING_BY_NORMALIZED_COLUMN`.
4. A semantic evidence binding engine exists and consumes normalized formula/pathology entries plus column candidates.
5. The XLSX-first entrypoint does not import or call the semantic catalog loader, column semantic mapper, or semantic evidence binding engine.
6. The XLSX-first entrypoint imports and calls `build_service_1_pathology_to_allowed_computation_candidate_v1`.
7. The allowed-computation boundary is hardcoded through `_PATHOLOGY_TO_COMPUTATION`.
8. `_PATHOLOGY_TO_COMPUTATION` supports `REN_001`, `LIQ_001`, `STK_001`, and `CSH_001` only.
9. `SAL_001` and `CST_001` are not supported by the inspected allowed-computation hardcoded mapping.
10. The existing CASE_001 characterization test already documents the current semantic binding gap and must not be duplicated.
11. Runtime authorization remains false in the inspected loader, mapper, engine-generated objects, allowed-computation candidate, and XLSX-first entrypoint result.
12. Runtime/catalog connection remains blocked by the existing audit and migration docs.

## 6. Hypotheses

1. `service_1_semantic_catalog_loader_v1.py` can become the read-only input boundary for a future binding contract, but only after it covers the enriched catalog, semantic variable catalog, and evidence matrix or after a separate adapter is designed.
2. `service_1_semantic_evidence_binding_engine_v1.py` can eventually bridge column candidates to formula readiness, but it needs a governing contract before being connected to the XLSX-first runtime chain.
3. `service_1_pathology_to_allowed_computation_candidate_v1.py` should likely be wrapped or replaced by a catalog-driven readiness boundary, because it currently hardcodes pathology-to-computation behavior.
4. The current mapper can remain observational/shadow-mode if used without changing runtime decisions.

## 7. Gaps

1. No current inspected loader reads all semantic baseline artifacts.
2. No current inspected runtime path consumes `service_1_formula_pathology_evidence_matrix.v1.json`.
3. No current inspected runtime path consumes `service_1_semantic_variable_catalog.v1.json`.
4. No current inspected runtime path consumes `pathology_catalog.enriched.v1.json`.
5. No binding contract exists for:

```text
pathology_code
-> formula_refs
-> required_variables
-> required_evidence
-> readiness_status
```

6. No explicit fail-closed runtime gate exists for absent formula refs in `SAL_001`, `STK_001`, `CST_001`, and `CSH_001`.
7. `STK_001` and `CSH_001` are hardcoded in allowed-computation despite having no formula refs in the current semantic baseline.
8. `SAL_001` appears in the CASE_001 triage path but does not enter allowed computation in the characterized case.
9. Mapper and engine are not yet wired into the XLSX-first entrypoint chain.

## 8. Stop conditions

Do not implement or modify runtime until all of the following exist:

```text
SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1
contract tests for formula refs and required variables
fail-closed behavior for missing formula refs
explicit handling for SAL_001/STK_001/CST_001/CSH_001 baseline gaps
no-new-hardcoding guard
evidence that mapper/engine connection is observational before runtime promotion
explicit runtime authorization artifact
```

Prohibited in the next cycle unless explicitly reauthorized:

```text
runtime modification
mapper modification
engine modification
CLI modification
CASE_001 patch
JSON mutation
new characterization duplicate
Phase 5 opening
product-ready claim
```

## 9. Next methodological step

```text
SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1
mode: CONTRACT DESIGN ONLY
```

The contract must define a pure, fail-closed, non-executing boundary for:

```text
pathology_code
-> formula_refs
-> formula existence
-> required_variables
-> semantic variable existence
-> required_evidence
-> owner confirmation requirement
-> readiness_status
```

It must explicitly state:

- missing formula refs do not authorize runtime execution;
- catalog consistency does not equal runtime readiness;
- mapper and engine outputs may be observed before they govern runtime;
- allowed-computation hardcoding must not be expanded to make catalog gaps disappear;
- CASE_001 must not be forced to pass by patching runtime behavior.

## 10. Conclusion

Servicio 1 has a partial catalog/binding surface, but the current runtime path remains disconnected from the semantic catalog loader, mapper, and binding engine.

The loader audit result is:

```text
catalog loader exists: yes, partial
mapper exists: yes, hardcoded map, not catalog reader
binding engine exists: yes, not wired into XLSX-first runtime
allowed-computation boundary exists: yes, hardcoded runtime-adjacent map
XLSX-first entrypoint exists: yes, pure chain, not catalog-driven
CASE_001 characterization exists: yes, do not duplicate
runtime connection: blocked
Phase 5: blocked
product-ready: not ready
```
