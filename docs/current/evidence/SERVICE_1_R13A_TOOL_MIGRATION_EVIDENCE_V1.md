# Servicio 1 — R13A tool migration evidence

## Scope

R13A migrated the three collection-blocking physical-control tools to the
current canonical semantic and Product Root contracts. The retired
`service_1_deterministic_semantic_pipeline_v1` and
`service_1_legacy_semantic_reentry_compat_v1` modules were not recreated and no
compatibility wrapper was added.

## Runtime/tool changes

- `tools/service_1_bounded_six_physical_computable_controls_v1.py`
- `tools/service_1_capability_physical_coverage_gate_v1.py`
- `tools/service_1_physical_computable_positive_controls_v1.py`

The tools now use the canonical SEM-8 initial/reentry functions, deterministic
proposal provider, canonical P8 computability adapter, and typed
`WorkbookSemanticStartRequestV1` / `WorkbookSemanticContinueRequestV1`
commands through `run_service_1_product_pipeline_v1`.

## Verification

Command executed (bounded set only):

```text
python -m pytest -q tests/smartpyme/test_service_1_bounded_six_physical_computable_controls_v1.py tests/smartpyme/test_service_1_capability_physical_coverage_gate_v1.py tests/smartpyme/test_service_1_excel_reality_lab_a2_calculation_matrix_v1.py tests/smartpyme/test_service_1_physical_computable_positive_controls_v1.py tests/smartpyme/test_service_1_physical_p6_p7_p8_capability_readiness_matrix_v1.py
```

Final observed result: **16 passed / 7 failed**. The five modules collect
without the previous legacy-module ImportErrors.

## Remaining blockers

1. The coverage-gate expectation for `adjusted_operating_cash_flow` still
   expects the retired semantic behavior (`CAPABILITY_NOT_GOVERNED`), while
   current SEM-8 correctly fails closed with `BLOCK_SEM8_DIALOGUE_FAILED` when
   no owner-confirmable decision exists.
2. Two coverage-gate safety tests still monkeypatch the old kwargs-shaped root
   call and deep-copy typed Product Root packets containing `mappingproxy`.
3. One coverage-gate test asserts repository-wide `git diff --check`; the
   pre-existing dirty worktree contains unrelated trailing whitespace and
   line-ending warnings.
4. The REN-001 physical test and the P6/P7/P8 readiness tool still pass the
   removed `sheet_name` keyword to the canonical semantic bridge. Those are
   outside the three R13A tools and were not changed.

No full suite, commit, push, deploy, or legacy-module recreation was performed.
