# Service 1 R10B2 CLI reconciliation evidence

## Scope

Only the two stale CLI test modules were reconciled to the current typed
SEM-8/Product Root entrypoint. Runtime code was not changed.

## Test modules

- `tests/cli/test_service_1_product_cli_v1.py`
- `tests/cli/test_service_1_product_liq_001_delivery_flag_v1.py`

## Reconciliation

- Removed assertions and fixtures for the deleted `tool_requests` path.
- Removed the legacy semantic resolver and deleted CLI execution-mode tests.
- Migrated retained entrypoint coverage to `WorkbookSemanticStartRequestV1`,
  explicit `requested_capability`, `deliver_result`, and current SEM-8 grouped
  owner confirmation.
- Preserved sheet-selection, intake blocking, canonical-root routing, UTF-8
  JSON loading, and delivery-flag coverage.
- No compatibility wrapper, alias, fallback, or runtime change was added.

## Verification

Before reconciliation (both CLI modules): **15 failed / 0 passed**.

After reconciliation:

```text
python -m pytest -q tests/cli/test_service_1_product_cli_v1.py tests/cli/test_service_1_product_liq_001_delivery_flag_v1.py
12 passed / 0 failed
```

R10B2 focal (ingestion → semantic bridge → owner/web):

```text
89 passed / 0 failed
```

The targeted CLI modules contain zero references to `tool_requests`,
`--tool-requests`, `resolve_service_1_legacy_semantic_run_v1`, or legacy CLI
execution-mode terminology.

No full suite, commit, push, or deploy was performed.
