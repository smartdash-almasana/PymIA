# Service 1 — R12 Integration Checkpoint Evidence V1

- **Verdict:** `PASS`
- **Branch:** `work/service1-cafeteria-flow-v1`
- **HEAD:** `8d5708e refactor(service1): converge workbook logical model d1-d7`
- **Scope:** bounded R4–R11.5 integration checkpoint; no full suite.

## Checkpoint command

The R12 bounded suite combined the recommended R12 boundaries with the new R4 request-contract and R11.5 fitness-harness tests:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_architecture_lock_v1.py \
  tests/smartpyme/test_service_1_architecture_baseline_certifier_v1.py \
  tests/smartpyme/test_service_1_product_pipeline_v1.py \
  tests/smartpyme/test_service_1_request_kind_dispatch_v1.py \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py \
  tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_workbook_schema_identity_d3_v1.py \
  tests/smartpyme/test_service_1_workbook_logical_model_d1_d2_v1.py \
  tests/smartpyme/test_service_1_workbook_logical_model_d7_v1.py \
  tests/smartpyme/test_service_1_logical_relationship_graph_d4_v1.py \
  tests/smartpyme/test_service_1_table_scoped_semantics_d5_v1.py \
  tests/smartpyme/test_service_1_tenant_schema_family_memory_d6_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py \
  tests/smartpyme/test_service_1_owner_semantic_evidence_reentry_v1.py \
  tests/smartpyme/test_service_1_multisheet_parity_guard_v1.py \
  tests/smartpyme/test_service_1_analysis_computability_f5_v1.py \
  tests/smartpyme/test_service_1_computability_v1.py \
  tests/smartpyme/test_service_1_analysis_evidence_preparation_f7_v1.py \
  tests/smartpyme/test_service_1_analysis_math_execution_f8_v1.py \
  tests/smartpyme/test_service_1_analysis_result_projection_f9_v1.py \
  tests/smartpyme/test_service_1_result_memory_f13_v1.py \
  tests/smartpyme/test_service_1_generic_capability_kernel_v1.py \
  tests/smartpyme/test_service_1_cycle_044a_generic_capability_kernel_architecture_v1.py \
  tests/smartpyme/test_service_1_liq_001_evaluator_v1.py \
  tests/smartpyme/test_service_1_ren_001_evaluator_v1.py \
  tests/smartpyme/test_service_1_liq_002_productive_root_v1.py \
  tests/smartpyme/test_service_1_pyme_011_productive_root_v1.py \
  tests/smartpyme/test_service_1_consorcios_expense_variance_v1.py \
  tests/smartpyme/test_service_1_consorcios_collection_aging_v1.py \
  tests/smartpyme/test_service_1_reconciliation_governed_flow_v1.py \
  tests/smartpyme/test_service_1_reconciliation_product_wiring_v1.py \
  tests/smartpyme/test_service_1_module_disposition_registry_v1.py \
  tests/test_service_1_architecture_fitness_harness_v1.py
```

Result after contract correction:

```text
358 passed / 0 failed (242.87s)
```

## Initial failure and bounded correction

The first checkpoint run produced exactly three failures, all in `test_service_1_architecture_lock_v1.py`:

- productive nucleus still listed retired/declassified modules;
- retained-support decisions still classified two root-reachable ingestion boundaries as support;
- registry-frozen `service_1_pipeline_v1` was not accounted for by the lock.

The correction synchronized the architecture lock JSON/current Markdown with the already reconciled R11 registry. No runtime code or tests were changed, and no gates were weakened.

## Architecture gates

```text
python -m pymia.architecture_guard --json
PASS
16 gates PASS / 0 failed
```

The gates cover Product Root, four typed execution commands, canonical XLSX reader, semantic FSM/legacy absence, sheet1 fallbacks, Web bypasses, D4→P8 provenance, F7-only joins, one math engine, declarative classification, LLM authority, post-build envelope mutation, ResultRead isolation, D7 evidence-only, and registry drift.

## Restrictions

- Full suite: not run.
- Playwright/smoke/Cloud Run: not run.
- Runtime code: unchanged by R12.
- Commit/push/deploy: not performed.
- Existing dirty worktree and `_audit/`: preserved.
