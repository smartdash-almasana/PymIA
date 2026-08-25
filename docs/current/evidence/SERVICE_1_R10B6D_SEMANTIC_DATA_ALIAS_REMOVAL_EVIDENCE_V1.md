# Service 1 R10B6D — Semantic/Data Alias Removal Evidence

## Scope

R10B6D removed only semantic/data aliases from the inner `CanonicalIngestionOutput` envelope after R10B6C migrated their productive consumers to canonical sources.

Removed envelope keys:

- `available_data_fields`
- `columns`
- `input_values`
- `normalized_values`
- `column_meaning_confirmations`
- `column_evidence`
- `declared_data_sources`

The canonical sources remain intact: `workbook_context`, `normalized_tables`, `column_refs` (including `owner_meaning` after confirmation), `physical_lineage`, `provenance`, and safety/runtime flags. The outer owner-confirmation connector contract and semantic-bridge result fields were not removed.

`_column_evidence` remains a deterministic canonical evidence projection reused by the semantic bridge; it is not emitted as an ingestion-envelope alias.

## Verification

Affected focal command:

```text
python -m pytest -q tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py tests/smartpyme/test_service_1_multisheet_parity_guard_v1.py tests/smartpyme/test_service_1_canonical_ingestion_output_to_semantic_bridge_v1.py tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py tests/smartpyme/test_service_1_assisted_web_http_v1.py tests/smartpyme/test_service_1_result_memory_f13_v1.py
```

Result: **99 passed / 0 failed** in 152.20 seconds.

No full suite, R11, commit, push, or deploy was performed. `_audit/` and unrelated worktree changes were preserved.
