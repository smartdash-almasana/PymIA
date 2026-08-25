# Servicio 1 — R13D7 isolated-contract reconciliation

## Scope

R13D7 reconciled only the four isolated stale cases identified by the R13C
diagnosis. Runtime code, Product Root authority, and mathematical engines were
not changed.

## Reconciled cases

- The architecture lexical guard now permits only the documented opaque
  workflow-identity phrase as a precise lexical exception.
- Consorcios radar assertions compare the serialized numeric observations using
  numeric tolerance, preserving the deterministic computed values.
- Cycle 053 now asserts the typed Product Root signature and keeps explicit
  capability selection without a legacy kwargs parameter.
- SEM-5 owner projection now expects the current D5 table-scoped semantic group
  to project its two grouped column events; the isolated cost decision remains
  separate.

## Verification

Exact bounded command:

```text
python -m pytest -q tests/architecture/test_forbidden_terms.py::test_no_forbidden_terms_in_code tests/smartpyme/test_service_1_consorcios_radar_plug_v1.py::test_expense_variance_projection_uses_both_real_deviation_fields tests/smartpyme/test_service_1_cycle_053_global_12_pathology_closure_v1.py::test_cycle_053_preserves_explicit_selection_and_no_automatic_capability_choice tests/smartpyme/test_service_1_owner_semantic_answer_projection_v1.py::test_sem5_group_accept_projects_three_canonical_column_events
```

Observed result: **4 passed / 0 failed in 5.68s**.

No full suite, runtime changes, commit, push, or deploy were performed.


