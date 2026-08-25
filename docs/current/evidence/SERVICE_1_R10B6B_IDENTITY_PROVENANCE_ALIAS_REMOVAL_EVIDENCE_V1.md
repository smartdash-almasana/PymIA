# Service 1 — R10B6B Identity/Provenance Alias Removal Evidence

## Scope

R10B6B removes only zero-consumer identity/provenance aliases from the inner
`CanonicalIngestionOutput` envelope produced by
`service_1_owner_confirmation_to_canonical_ingestion_output_v1.py`.

The canonical nested locations remain authoritative:

- `workbook_context.case_id`
- `workbook_context.source_artifact_ref`
- `workbook_context.workbook_ref`
- `workbook_context.ingestion_scope`
- `provenance.source_kind`
- `provenance.source_artifact_ref`
- `provenance.source_file_ref`
- `provenance.workbook_ref`
- `provenance.ingestion_scope`
- `provenance.filename`
- `provenance.sheet_names`
- `provenance.sheet_refs`

## Aliases removed from the inner envelope

- `case_id`
- `source_artifact_ref`
- `workbook_ref`
- `source_file_ref`
- `source_kind`
- `filename`
- `ingestion_scope`
- `sheet_name`
- `sheet_names`
- `sheet_ref`
- `sheet_refs`

The outer owner-confirmation connector packet and the semantic bridge packet
retain their own explicit contract fields. They are not `CanonicalIngestionOutput`
aliases and were not removed.

## Aliases intentionally retained

Semantic/data aliases were not touched:

- `available_data_fields`
- `columns`
- `input_values`
- `normalized_values`
- `column_meaning_confirmations`
- `column_evidence`
- `declared_data_sources`

## Consumer migration evidence

Affected test consumers were migrated to the nested canonical paths, including
multisheet sheet identity, F13 case identity, SEM-8 owner re-entry provenance,
and the bridge contract assertion. A runtime scan found no remaining direct
reads of the removed top-level aliases in `pymia/` or test consumers of the
inner envelope.

## Verification

Final affected focal command:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_multisheet_parity_guard_v1.py \
  tests/smartpyme/test_service_1_canonical_ingestion_output_to_semantic_bridge_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_result_memory_f13_v1.py
```

Result: **86 passed / 0 failed** in 74.79 seconds.

The broader affected D1–D7/Product Root/F7/F12/F13 run produced 217 passed and
one stale assertion failure before the bridge test was migrated. The final
focused rerun above passed after that test-only migration.

Target-file `git diff --check`: **PASS**. A repository-wide check reports only
pre-existing trailing whitespace in the unrelated
`docs/current/SERVICE_1_ARCHITECTURE_LOCK.md`; that file was not changed by
R10B6B.

No full suite, R11, commit, push, or deploy was performed. `_audit/` and all
unrelated worktree changes were preserved.
