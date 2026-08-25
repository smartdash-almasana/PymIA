# Service 1 — R10B2 ChatGPT Audit V1

**Audit timestamp:** 2026-08-24 14:50 ART (UTC-03:00)  
**Scope:** independent physical audit of R10B2 owner_answers legacy-path migration and reported CLI test blocker.

## Verdict

```text
R10B2_RUNTIME_MIGRATION = PASS
R10B2_FOCAL_EVIDENCE = 89 passed / 0 failed
CLI_TEST_RECONCILIATION_REQUIRED = YES
R10_NEXT_DEBT = BLOCKED_UNTIL_CLI_TEST_RECONCILIATION
```

## Physical findings

### Legacy owner_answers path

In `service_1_owner_confirmation_to_canonical_ingestion_output_v1.py`, remaining `owner_answers` identifiers are the canonical function input and validation/iteration logic. The legacy top-level output key is absent.

In `service_1_canonical_ingestion_output_to_semantic_bridge_v1.py`, `_extract_input_values` reads only `input_values` and `normalized_values`; the former `owner_answers` fallback is absent.

Therefore the target legacy output/fallback path is physically removed while canonical owner-confirmation input remains intact.

### CLI failures

The current CLI runtime `pymia/cli/service_1_product.py` exposes the canonical typed SEM-8/Product Root flow and no `tool_requests` argument or CLI option. It also has no `resolve_service_1_legacy_semantic_run_v1` symbol.

The two stale CLI test modules still contain expectations for removed contracts:

- `tests/cli/test_service_1_product_cli_v1.py`
- `tests/cli/test_service_1_product_liq_001_delivery_flag_v1.py`

Physical search found test references to `tool_requests` and one monkeypatch of `resolve_service_1_legacy_semantic_run_v1`. These are test-to-runtime drift, not justification to restore compatibility wrappers.

## Constraint

Reconcile the stale CLI tests to the current typed Product Root / SEM-8 CLI contract. Do not change runtime merely to satisfy removed legacy expectations. Do not add wrapper, alias, fallback, or resurrect `tool_requests`.

No R10B3/R11/full-suite/commit/push/deploy authorized by this audit.
