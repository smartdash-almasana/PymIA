# SERVICE_1_MICROCYCLE_ANTI_DRIFT_AUDIT_PROTOCOL_V1

**Project:** PymIA / SmartPyme / Servicio 1  
**Type:** Audit Protocol / DOC ONLY  
**Mode:** GOVERNANCE ONLY  
**Base:** post `6adc6be` handoff audit PASS  

## Verdict

```text
VERDICT: PASS_MICROCYCLE_ANTI_DRIFT_AUDIT_PROTOCOL_DOC_CREATED
RUNTIME_CONNECTION_STATUS: BLOCKED
PHASE_5_STATUS: BLOCKED
PRODUCT_READY_STATUS: NOT_READY
```

## 1. Purpose

Define a preventive audit protocol for every Servicio 1 microcycle so that development advances without semantic drift, hidden runtime promotion, layer mixing, or product-ready claims.

## 2. Mandatory microcycle shape

Every microcycle must declare:

```text
MICROCYCLE_NAME:
MODE:
BASE_HEAD:
EXPECTED_FILES_CREATED:
EXPECTED_FILES_MODIFIED:
FORBIDDEN_FILES:
FOCAL_TEST_COMMAND:
FORBIDDEN_IMPORTS:
EXPECTED_NEXT_ACTION:
```

If these fields are missing, the microcycle is not authorized.

## 3. Pre-audit gate

Before work begins, verify:

```text
git status --short is clean
HEAD matches expected base
scope has one objective
allowed files are explicitly listed
forbidden files are explicitly listed
runtime/mapper/engine/CLI/CASE_001 are out of scope
JSON mutation is out of scope unless explicitly authorized
```

## 4. Post-audit gate

After work ends, verify:

```text
git status --short
git diff --name-status or git show --name-status
pytest focal command
forbidden import guard
CASE_001 guard
runtime flag guard
phase_5 flag guard
product-ready guard
```

## 5. Forbidden import guard

Search changed files for:

```text
service_1_xlsx_first_product_entrypoint_v1
service_1_column_semantic_mapper_v1
service_1_semantic_evidence_binding_engine_v1
service_1_pathology_to_allowed_computation_candidate_v1
pymia.cli
```

Any match blocks the commit unless the microcycle explicitly authorized that dependency.

## 6. Forbidden promotion guard

Search changed files for unsafe promotion signals:

```text
CASE_001
runtime_allowed=True
runtime_allowed = True
phase_5_allowed=True
phase_5_allowed = True
product-ready
PRODUCT_READY
Phase 5 allowed
```

Any match requires audit explanation before commit.

## 7. Commit eligibility

A commit is eligible only if:

```text
all changed files match the declared scope
focal tests pass or skip is explicitly expected for TEST ONLY scaffolds
forbidden imports are absent
CASE_001 dependency is absent
runtime_allowed remains false
phase_5_allowed remains false
product-ready remains NOT_READY
next action opens only one microcycle
```

## 8. Automatic rejection rules

Reject the microcycle if any condition appears:

```text
more than one new layer in the same commit
docs + implementation mixed without authorization
runtime, mapper, engine, or CLI imported early
CASE_001 used to force pass
JSON mutated without explicit scope
product-ready declared
Phase 5 opened
tests skipped after implementation exists
next_action opens parallel fronts
```

## 9. Standard audit output

Every audit must output:

```text
VERDICT:
HEAD:
GIT_STATUS:
FILES_CHANGED:
TEST_RESULT:
FORBIDDEN_IMPORTS:
CASE_001_GUARD:
RUNTIME_FLAGS:
PHASE_5_FLAGS:
PRODUCT_READY_GUARD:
CERTIFIED:
GAPS:
NEXT_ACTION:
```

## 10. Current operating rule

The active rule for Servicio 1 remains:

```text
one microcycle
one layer
one commit
one next action
```

No horizontal expansion unless explicitly approved after a pre-audit.
