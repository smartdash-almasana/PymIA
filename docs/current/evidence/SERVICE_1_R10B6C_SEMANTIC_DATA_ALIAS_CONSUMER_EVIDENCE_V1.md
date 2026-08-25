# Service 1 — R10B6C Semantic/Data Alias Consumer Evidence

## Scope

R10B6C migrates productive consumers of semantic/data aliases from the inner
`CanonicalIngestionOutput` to canonical sources. The aliases remain emitted;
this slice does not remove them.

Scoped aliases:

- `available_data_fields`
- `columns`
- `input_values`
- `normalized_values`
- `column_meaning_confirmations`
- `column_evidence`
- `declared_data_sources`

## Consumer inventory

Before migration, productive consumers were:

- `service_1_canonical_ingestion_output_to_semantic_bridge_v1.py`
  - `_extract_columns` read `available_data_fields`/`columns` fallbacks.
  - `_extract_input_values` read `input_values`/`normalized_values` fallbacks.
  - confirmation-matrix construction read `column_evidence`.
- `service_1_ui_v1.py:_sample_values` read `column_evidence` before its table
  fallback.
- `service_1_assisted_web_v1.py:_unit_column_evidence_preview` read
  `column_evidence` before its table fallback.

No productive consumer was found for `column_meaning_confirmations` or
`declared_data_sources`.

After migration:

- The bridge derives available fields from canonical `column_refs.field_id`.
- Confirmed owner meanings are derived from canonical
  `column_refs.owner_meaning`.
- Column samples/type evidence are regenerated deterministically from
  canonical `normalized_tables` and `column_refs`, reusing the canonical
  ingestion evidence projection.
- UI and assisted Web previews read canonical `normalized_tables` directly.
- Productive runtime scan: **0 direct reads** of the scoped top-level aliases.

The producer continues to emit all scoped aliases for compatibility. They are
not yet removed in R10B6C.

## Verification

Focused affected command:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_canonical_ingestion_output_to_semantic_bridge_v1.py \
  tests/smartpyme/test_service_1_multisheet_parity_guard_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py \
  tests/smartpyme/test_service_1_result_memory_f13_v1.py
```

Result: **99 passed / 0 failed** in 135.92 seconds.

The bridge module alone also passed **18 passed / 0 failed**. The new bridge
contract test removes the aliases from a real canonical envelope copy and
confirms that canonical refs, tables, and owner meanings are sufficient.

No full suite, alias removal, R11, commit, push, or deploy was performed.
`_audit/` and unrelated worktree changes were preserved.
