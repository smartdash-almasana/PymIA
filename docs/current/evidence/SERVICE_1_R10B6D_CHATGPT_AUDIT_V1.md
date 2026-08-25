# Service 1 — R10B6D ChatGPT physical audit

Date/time: 2026-08-24 18:16 ART (UTC-03:00)

VERDICT: PASS_PHYSICAL_CODE_AUDIT

Observed:
- R10B6D evidence file exists and matches the reported scope.
- `_canonical_ingestion_envelope` no longer emits `available_data_fields`, `columns`, `input_values`, `normalized_values`, `column_meaning_confirmations`, `column_evidence`, or `declared_data_sources`.
- Canonical envelope still contains `workbook_context`, `normalized_tables`, `column_refs`, `physical_lineage`, `provenance`, and safety/runtime flags.
- `_column_evidence` remains an internal deterministic projection only.
- Searches confirm previously retired R10 switches remain absent: `semantic_reception_only=0`, `use_assisted_semantics=0`, `semantic_run_override=0`, productive `Sheet1=0`.
- `analysis_execution_request` only appears inside the canonical blocking reason `ANALYSIS_EXECUTION_REQUEST_MUST_BE_EXCLUSIVE`; no informal request dict consumer was observed.

Test evidence supplied by Codex: 99 passed / 0 failed.
Independent MCP rerun: NOT_OBSERVED_MCP_502. This is infrastructure failure, not a test failure.

R10B6D = PASS. Next action should be R10 closure verification, not another migration slice.
