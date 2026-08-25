# Servicio 1 — R13D2 UI/source legacy reconciliation evidence

## Scope

R13D2 reconciled only the nine stale UI/source assertions identified in
R13C. The affected tests now follow the current SEM-8/Product Root flow:
typed semantic actions, explicit launch review selection, canonical workbook
identity, current result/blocked-state copy, and the current typed Product
Root request guard. No production runtime module was changed.

## Files changed

- `tests/smartpyme/test_service_1_assisted_web_radar_http_v1.py`
- `tests/smartpyme/test_service_1_assisted_web_tenant_persistence_v1.py`
- `tests/smartpyme/test_service_1_assisted_web_vertical_slice_contract_v1.py`
- `tests/smartpyme/test_service_1_cafeteria_semantic_scope_v1.py`
- `tests/smartpyme/test_service_1_ren_001_sellable_vertical_closure_v1.py`

The legacy source assertion for `owner_answers` was replaced with the
canonical `WorkbookSemanticStartRequestV1` delegation assertion. Tenant
fixtures now submit `action_<decision_id>` and compare persisted references
to the canonical `workbook_context.workbook_ref`.

## Verification

The exact nine affected tests were executed together:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_assisted_web_radar_http_v1.py::test_authenticated_assisted_web_owner_can_open_radar_menu_and_persist_policy \
  tests/smartpyme/test_service_1_assisted_web_tenant_persistence_v1.py::test_assisted_web_persists_canonical_owner_events_after_successful_review \
  tests/smartpyme/test_service_1_assisted_web_tenant_persistence_v1.py::test_owner_confirmation_is_persisted_even_when_requested_control_needs_more_evidence \
  tests/smartpyme/test_service_1_assisted_web_tenant_persistence_v1.py::test_required_tenant_persistence_fails_closed_when_backend_rejects_write \
  tests/smartpyme/test_service_1_assisted_web_tenant_persistence_v1.py::test_http_server_accepts_trusted_identity_resolver_and_persists \
  tests/smartpyme/test_service_1_assisted_web_vertical_slice_contract_v1.py::test_vertical_slice_delegates_to_product_root \
  tests/smartpyme/test_service_1_cafeteria_semantic_scope_v1.py::test_cafeteria_margin_asks_only_relevant_columns_and_keeps_case_actionable \
  tests/smartpyme/test_service_1_cafeteria_semantic_scope_v1.py::test_cafeteria_margin_confirms_semantics_then_discount_unit_and_executes_kernel_once_semantics_are_fixed \
  tests/smartpyme/test_service_1_ren_001_sellable_vertical_closure_v1.py::test_ren_001_page_does_not_offer_download_without_delivery
```

Observed result: **9 passed / 0 failed** in **5.28s**.

No full suite, runtime changes, commit, push, or deploy was performed.
