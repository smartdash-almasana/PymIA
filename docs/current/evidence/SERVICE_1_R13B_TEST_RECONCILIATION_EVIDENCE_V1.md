# Servicio 1 — R13B test reconciliation evidence

## Scope

R13B reconciled the seven stale assertions/API usages exposed by the bounded
R13A test set. No production runtime module was changed, no legacy module was
recreated, and no compatibility wrapper was added.

## Reconciled surfaces

- Updated the PYME-026 expectation to the current fail-closed P6-blocked
  contract.
- Updated safety monkeypatches to inspect typed Product Root requests and to
  shallow-copy the returned packet without attempting to deepcopy immutable
  mapping proxies.
- Scoped the diff-check assertion to the gate files under test so unrelated
  pre-existing worktree whitespace cannot change its result.
- Removed the retired `sheet_name` keyword from the canonical semantic bridge
  test call and from the non-production P6/P7/P8 readiness helper.

## Verification

Command executed exactly:

```text
python -m pytest -q tests/smartpyme/test_service_1_bounded_six_physical_computable_controls_v1.py tests/smartpyme/test_service_1_capability_physical_coverage_gate_v1.py tests/smartpyme/test_service_1_excel_reality_lab_a2_calculation_matrix_v1.py tests/smartpyme/test_service_1_physical_computable_positive_controls_v1.py tests/smartpyme/test_service_1_physical_p6_p7_p8_capability_readiness_matrix_v1.py
```

Observed result: **23 passed / 0 failed** in **90.62s**.

No full suite, commit, push, or deploy was performed.
