# SERVICE_1_RUNTIME_CATALOG_RECONCILIATION_V1

**Project:** PymIA / SmartPyme / Servicio 1
**Type:** Runtime/catalog reconciliation audit
**Mode:** DOC ONLY
**Branch:** `service-1-semantic-catalog-baseline`
**HEAD:** `fa5c359`

## Verdict

```text
VERDICT: PARTIAL_RECONCILIATION_REQUIRED
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
PRODUCT_READY_STATUS: NOT_READY
TEST_STATUS: CONSISTENCY_TEST_PASSING
```

This document records the current fracture between runtime/code and the semantic catalog baseline. It does not authorize runtime connection, mapper changes, engine changes, CLI changes, CASE_001 patching, or any product-ready claim.

## Baseline Scope

The fixed Servicio 1 semantic baseline contains exactly these pathology codes:

```text
REN_001
LIQ_001
SAL_001
STK_001
CST_001
CSH_001
```

This scope is already decided and is not reopened by this reconciliation audit.

## Current Runtime/Catalog State

The catalog layer now has a controlled semantic baseline:

- `formula_catalog.v1.json` remains the source for formula definitions.
- `pathology_catalog.v1.json` remains the source for the original pathology catalog.
- `pathology_catalog.enriched.v1.json` records the six-code Servicio 1 baseline as catalog-only.
- `service_1_formula_pathology_evidence_matrix.v1.json` records formula refs, required variables, evidence, and runtime blocks.
- `test_service_1_semantic_catalog_consistency_v1.py` verifies the baseline consistency and passes with `9 passed`.

Current code/runtime remains separate from that catalog baseline:

```text
runtime/code
!= formula_catalog.v1.json
!= pathology_catalog.v1.json
!= pathology_catalog.enriched.v1.json
!= service_1_formula_pathology_evidence_matrix.v1.json
```

## Pathology Reconciliation Status

| Pathology | Catalog status | Formula status | Runtime status |
|---|---|---|---|
| `REN_001` | Baseline included | `REN_001_margen_neto_real` | Blocked |
| `LIQ_001` | Baseline included | `LIQ_001_vendido_cobrado` | Blocked |
| `SAL_001` | Baseline semantic initial | No formula associated yet | Blocked |
| `STK_001` | Baseline semantic initial | No formula associated yet | Blocked |
| `CST_001` | Baseline semantic initial | No formula associated yet | Blocked |
| `CSH_001` | Baseline semantic initial | No formula associated yet | Blocked |

`SAL_001`, `STK_001`, `CST_001`, and `CSH_001` must not be removed from the baseline because they represent accepted initial semantic coverage for Servicio 1. Their absence of formula refs is a documented gap, not a reason to erase them.

## Risk

Connecting runtime, mapper, engine, or CLI now would be premature.

Specific risks:

- Runtime could pass cases by partial coincidence rather than governed catalog readiness.
- Mapper behavior could hardcode apparent semantic matches that the catalog has not authorized.
- Engine behavior could compute from insufficient evidence or ambiguous bindings.
- CLI behavior could expose a flow that looks operational while still bypassing catalog governance.
- `CASE_001` could be forced to pass without resolving the underlying semantic evidence binding fracture.

The current consistency test proves catalog integrity only. It does not prove runtime readiness.

## Allowed Next Phase

The next allowed phase is design-only:

```text
design controlled runtime/catalog migration plan
```

That plan should define:

- how runtime reads catalog artifacts without becoming implicitly authorized;
- which gates must remain fail-closed;
- how mapper outputs map to semantic variables;
- how formula refs become computation candidates;
- which tests must exist before any runtime connection;
- what evidence is required before CASE_001 is revisited.

## Prohibited Next Phase

The following remain explicitly prohibited:

```text
runtime connection
mapper changes
engine changes
CLI changes
CASE_001 patch
product-ready claim
Phase 5 promotion
```

## Conclusion

Servicio 1 now has a local semantic catalog baseline and a passing consistency test, but runtime/catalog reconciliation is still incomplete.

The correct state is:

```text
catalog baseline: present
consistency test: passing
runtime connection: blocked
Phase 5: blocked
product-ready claim: forbidden
```
