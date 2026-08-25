# Servicio 1 — R7 implementation evidence

**Node:** `R7 — common math + declarative classification`  
**Repository:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`  
**Baseline:** `8d5708e9becdddaa5aa24387b310972643d1ef86`  
**Branch:** `work/service1-cafeteria-flow-v1`

## Scope completed

- Extended the capability contract with `ClassificationPredicate` and
  `ClassificationRule` supporting `ALL`/`ANY` predicate matching.
- Kept the bounded single-predicate constructor for existing definitions while
  routing classification through one declarative comparison helper.
- Added `MathPrimitiveOperation.DIVIDE` to the existing
  `FormulaEngineService`; no second math engine was introduced.
- Routed generic capability classification and the LIQ/REN/PYME evaluator
  policies through declarative rules.
- Routed LIQ/PYME normalized row reductions through
  `MathPrimitiveOperation.SUM`/`SINGLE_VALUE` and preserved exact-one opening
  balance semantics for `LIQ_002`.
- Kept business formulas in the existing canonical formula catalog/engine and
  did not change downstream P7/P8/F7/F8/F9 authority.
- Updated the stale PYME_011 focal-test import to the canonical P8
  computability module; no runtime compatibility wrapper was added.

## R5 stale-test reference migration

- Baseline test search found **41** references to the removed
  `run_initial_pass` composition root.
- The two test modules whose only subject was the removed semantic composition
  root were retired:
  `test_service_1_deterministic_semantic_pipeline_v1.py` and
  `test_service_1_deterministic_semantic_computation_plan_v1.py`.
- Root-only legacy tests were retired from the capability modules; evaluator
  and generic-kernel coverage was retained. Current SEM-8/Product Root and
  multisheet parity coverage remains in the canonical wiring, product-pipeline,
  computability, and parity suites.
- The retained LIQ-002 semantic-governance fixture now imports the P8 adapter
  and confirmed-bindings constants directly from `service_1_computability_v1`.
- Post-migration search reports **0** test references and **0** runtime
  references. No wrapper or runtime change was introduced by this migration.

## Gate inspection

```text
NO_INLINE_BUSINESS_MATH       = PASS for migrated R7 evaluators/adapters
NO_INLINE_BUSINESS_CLASSIFICATION = PASS for migrated R7 evaluators
CLASSIFIER_ARITHMETIC         = 0
MATH_KERNEL_AUTHORITY_COUNT   = 1 (FormulaEngineService)
SECOND_MATH_ENGINE             = NO
R8_PLUS_IMPLEMENTED            = NO
```

## Prescribed focal verification

Command:

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_generic_capability_kernel_v1.py \
  tests/smartpyme/test_service_1_cycle_044a_generic_capability_kernel_architecture_v1.py \
  tests/smartpyme/test_service_1_liq_001_evaluator_v1.py \
  tests/smartpyme/test_service_1_ren_001_evaluator_v1.py \
  tests/smartpyme/test_service_1_liq_002_productive_root_v1.py \
  tests/smartpyme/test_service_1_pyme_011_productive_root_v1.py \
  tests/smartpyme/test_service_1_analysis_math_execution_f8_v1.py -q
```

Result: **73 passed / 0 failed** (76 collected).

Affected-test migration command (legacy-root references plus the R7 focal
modules): **176 passed / 0 failed**. The SEM-8/Product Root, P8, and
multisheet parity rerun: **42 passed / 0 failed**.

An incidental broader command also included pre-existing F12 catalog/UI files
outside this migration and observed 16 failures there; those files were not
changed for this task and no out-of-scope repair was attempted.

## Repository constraints

```text
FULL_SUITE = NOT RUN
R8_PLUS = NOT IMPLEMENTED
COMMIT = NO
PUSH = NO
DEPLOY = NO
_audit = PRESERVED / NOT TOUCHED
```

```text
PRODUCTIVE_TEST_REFERENCES_TO_REMOVED_run_initial_pass = 0
R7_FOCAL_FAILURES = 0
FULL_SUITE = NOT RUN
R8_PLUS = NOT IMPLEMENTED
COMMIT = NO
PUSH = NO
DEPLOY = NO
```

**FINAL_VERDICT:** `PASS`  
**NEXT_ALLOWED_NODE:** `R8`
