# Service 1 — R13D5 canonical bridge `sheet_name` reconciliation evidence

Date: 2026-08-25

## Scope

Only the five affected tests were executed:

- `tests/smartpyme/test_service_1_excel_reality_lab_a4_adversarial_matrix_v1.py::test_a4_adversarial_matrix_is_reproducible_and_has_no_unsafe_execution`
- `tests/smartpyme/test_service_1_excel_reality_lab_a4_adversarial_matrix_v1.py::test_a4_safe_cases_keep_expected_terminal_classes`
- `tests/smartpyme/test_service_1_physical_xlsx_product_readiness_corpus_v1.py::test_physical_xlsx_product_readiness_corpus_is_reproducible_and_fail_closed`
- `tests/smartpyme/test_service_1_physical_xlsx_product_readiness_corpus_v1.py::test_physical_corpus_reports_all_outcomes_without_hiding_failures`
- `tests/smartpyme/test_service_1_semantic_bridge_to_controlled_execution_gate_v1.py::test_owner_question_surface_uses_safe_option_ids`

## Reconciliation

The obsolete `sheet_name` keyword was removed from the canonical semantic
bridge calls in the A4 and physical-readiness tools. The bridge now receives
worksheet identity exclusively from canonical `column_refs` and ingestion
evidence. The safe-option test fixture was migrated from the removed top-level
identity shape to canonical `workbook_context`, `provenance`, `column_refs`,
and normalized physical evidence; no fallback sheet was introduced.

No runtime authority, parser, semantic engine, math engine, Product Root, or
downstream contract was changed.

## Verification

```text
python -m pytest -q \
tests/smartpyme/test_service_1_excel_reality_lab_a4_adversarial_matrix_v1.py::test_a4_adversarial_matrix_is_reproducible_and_has_no_unsafe_execution \
tests/smartpyme/test_service_1_excel_reality_lab_a4_adversarial_matrix_v1.py::test_a4_safe_cases_keep_expected_terminal_classes \
tests/smartpyme/test_service_1_physical_xlsx_product_readiness_corpus_v1.py::test_physical_xlsx_product_readiness_corpus_is_reproducible_and_fail_closed \
tests/smartpyme/test_service_1_physical_xlsx_product_readiness_corpus_v1.py::test_physical_corpus_reports_all_outcomes_without_hiding_failures \
tests/smartpyme/test_service_1_semantic_bridge_to_controlled_execution_gate_v1.py::test_owner_question_surface_uses_safe_option_ids
```

Observed result: **5 passed / 0 failed** in **10.31s**.

No full suite, commit, push, or deploy was performed.
