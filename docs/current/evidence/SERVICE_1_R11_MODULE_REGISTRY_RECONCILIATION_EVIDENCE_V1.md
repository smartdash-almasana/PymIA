# Service 1 — R11 Module Registry Reconciliation Evidence

Date: 2026-08-24

## Physical reconciliation

The registry `docs/service_1_module_disposition.v1.json` was reconciled against every live `pymia/smartpyme/service_1_*.py` module.

Before reconciliation:

- Live modules: 111
- Registry modules: 101
- Missing: 12
- Extra: 2

Missing modules added:

```text
service_1_logical_relationship_graph_v1
service_1_logical_table_candidate_v1
service_1_physical_region_detection_v1
service_1_product_execution_contracts_v1
service_1_region_evidence_v1
service_1_result_read_boundary_v1
service_1_table_scoped_semantic_context_v1
service_1_tenant_memory_artifact_v1
service_1_tenant_schema_family_memory_store_v1
service_1_tenant_schema_family_memory_v1
service_1_workbook_logical_model_v1
service_1_workbook_schema_identity_v1
```

Extra deleted entries removed:

```text
service_1_deterministic_semantic_pipeline_v1
service_1_legacy_semantic_reentry_compat_v1
```

Direct `service_1_*` imports and canonical-root reachability were recalculated from the current Python sources. The resulting registry has 111 modules, 63 `PRODUCTIVE`, 47 `SUPPORT_NECESSARY`, and 1 `EXPERIMENTAL_FROZEN` (`service_1_pipeline_v1`, retained physically but outside the canonical root). No `OBSOLETE_ELIMINABLE` module remains.

## Verification

```text
python -m pytest -q tests/smartpyme/test_service_1_module_disposition_registry_v1.py
```

Result: **6 passed / 0 failed**.

No runtime or test source was modified by R11. Existing worktree changes and `_audit/` were preserved; no full suite, commit, push, or deploy was performed.
