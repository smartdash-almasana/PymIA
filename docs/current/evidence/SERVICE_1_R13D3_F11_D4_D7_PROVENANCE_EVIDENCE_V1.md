# Servicio 1 — R13D3 F11 D4/D7 Provenance Reconciliation

- **Scope:** Reconcile only the seven F11 cafeteria tests with the canonical D4 relationship graph carried by D7.
- **Repository:** `E:\\BuenosPasos\\smartbridge\\PymIA-service1-cafeteria`
- **HEAD at verification:** `8d5708e9becdddaa5aa24387b310972643d1ef86`
- **Runtime changed:** No.
- **Full suite:** Not run.
- **Commit/push/deploy:** None.

## Root cause

The seven F11 tests constructed discovery from the confirmed semantic run but invoked F7 without passing the D7 Workbook Logical Model. F7 therefore correctly failed closed with `D4_RELATIONSHIP_PROVENANCE_REQUIRED` when relationship bindings were present. This was a stale test orchestration path, not a runtime defect.

## Reconciliation

The F11 fixture now builds the canonical D7 model from the existing canonical ingestion output and the owner-confirmed relationship evidence already present in `semantic_run["confirmed_relationships"]`. The same D7 model is passed to discovery and F7. No relationship graph, parser, join, math, semantic engine, or compatibility wrapper was added.

## Verification

Exact bounded command:

```text
python -m pytest -q tests/smartpyme/test_service_1_cafeteria_generalization_f11_v1.py::test_f11_sales_total_atomic_evidence_reaches_f9 tests/smartpyme/test_service_1_cafeteria_generalization_f11_v1.py::test_f11_sales_by_product_uses_same_pipeline tests/smartpyme/test_service_1_cafeteria_generalization_f11_v1.py::test_f11_gross_margin_by_product_uses_confirmed_product_relationship_and_formula tests/smartpyme/test_service_1_cafeteria_generalization_f11_v1.py::test_f11_sales_by_branch_uses_confirmed_branch_relationship tests/smartpyme/test_service_1_cafeteria_generalization_f11_v1.py::test_f11_product_concentration_is_cross_group_canonical_formula tests/smartpyme/test_service_1_cafeteria_generalization_f11_v1.py::test_f11_sales_series_month_uses_same_atomic_sales_basis tests/smartpyme/test_service_1_cafeteria_generalization_f11_v1.py::test_f11_sales_shapes_reconcile_to_one_transactional_total
```

Observed result after reconciliation: **7 passed / 0 failed in 27.03s**.

The pre-reconciliation bounded run observed **7 failed / 0 passed in 21.05s**, all at the F7 preparation assertion because D7 provenance was omitted.

## Changed files

- `tests/smartpyme/test_service_1_cafeteria_generalization_f11_v1.py`
- `docs/current/evidence/SERVICE_1_R13D3_F11_D4_D7_PROVENANCE_EVIDENCE_V1.md`

All other pre-existing worktree changes, including `_audit/`, were preserved and left unstaged.
