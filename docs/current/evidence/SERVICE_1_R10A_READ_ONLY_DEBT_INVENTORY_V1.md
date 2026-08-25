# Service 1 — R10A Read-Only Debt Inventory V1

**Scope:** R10A inventory only. No runtime or test files were modified. No tests were run. No R10B cleanup was performed.

## Baseline

```text
branch = work/service1-cafeteria-flow-v1
head = 8d5708e9becdddaa5aa24387b310972643d1ef86
worktree = intentionally dirty; all pre-existing changes preserved
```

## Classification rules

- `DELETE_SAFE`: no productive definition/consumer remains for the named debt item. This does not authorize deleting a canonical field or contract with the same word.
- `MIGRATE_FIRST`: a productive definition/consumer remains; migrate the consumer to the canonical contract before removal.
- `KEEP_CANONICAL`: the item is a current architectural contract or data required by the canonical path; do not remove it as R10 debt.

## DELETE_SAFE

### CLI `normalized_tables` reinjection

- Definition searched: `pymia/cli/service_1_product.py`; no assignment/update/reinjection of `normalized_tables` exists.
- Current CLI path takes `connector["ingestion_output"]` and passes that immutable envelope to `run_service_1_product_pipeline_v1`.
- Productive consumers of a CLI reinjection shim: **NONE**.
- Decision: `DELETE_SAFE` (already absent). The canonical envelope field `normalized_tables` remains `KEEP_CANONICAL`.

### `use_assisted_semantics`

- Definition/consumer search in `pymia/**/*.py`: **NONE**.
- Decision: `DELETE_SAFE` (already absent from productive runtime).

### `semantic_run_override`

- Definition/consumer search in `pymia/**/*.py`: **NONE**.
- Decision: `DELETE_SAFE` (already absent from productive runtime).

### Productive `sheet1`

- Definition/consumer search in `pymia/**/*.py`: **NONE**. The canonical reader receives explicit `sheet_name`/`sheet_names`; no fabricated `sheet1` fallback was found.
- Decision: `DELETE_SAFE` (already absent from productive runtime).

### Removed legacy semantic files

- `pymia/smartpyme/service_1_deterministic_semantic_pipeline_v1.py`: deleted in the current worktree; no current production imports/callers.
- `pymia/smartpyme/service_1_legacy_semantic_reentry_compat_v1.py`: deleted in the current worktree; no current production imports/callers.
- The matching legacy semantic tests are also deleted in the current worktree.
- Decision for the files themselves: `DELETE_SAFE` (already removed in the current worktree).
- Important boundary: the residual post-discovery `available`/`blocked` compatibility projection is still active and is classified separately under `MIGRATE_FIRST` below; this audit does not declare that projection removable.

### Informal `analysis_execution_request` dict

- Definition: local mapping in `pymia/smartpyme/service_1_product_pipeline_v1.py:507-515`.
- Consumers: only the same function's exclusive branch at `:582-607`; no external production consumer found.
- Canonical replacement already exists: `WorkbookAnalysisExecuteRequestV1` in `service_1_product_execution_contracts_v1.py`.
- Decision: `DELETE_SAFE` for the local dict only. Keep the typed request contract and governed-analysis call.

## MIGRATE_FIRST

### Canonical-ingestion aliases

- Definition: `_canonical_ingestion_envelope` in `pymia/smartpyme/service_1_owner_confirmation_to_canonical_ingestion_output_v1.py:118-170` emits transitional top-level aliases alongside `workbook_context` and canonical `provenance`.
- Productive consumers still present:
  - `service_1_product_pipeline_v1.py:_validate_workbook_envelope_v2` validates top-level `case_id` and `source_file_ref` against `workbook_context`.
  - `service_1_canonical_ingestion_output_to_semantic_bridge_v1.py` reads top-level `case_id`, `source_kind`, `filename`, `available_data_fields`, `columns`, `confirmed_columns`, `input_values`, `normalized_values`, `owner_answers`, and `column_evidence`.
  - `service_1_assisted_web_v1.py` and `service_1_assisted_web_semantic_reception_v1.py` use `filename`/`source_file_ref` fallbacks for owner-facing provenance.
  - `service_1_logical_table_candidate_v1.py`, `service_1_workbook_profiler_v1.py`, and `service_1_region_evidence_v1.py` still have `source_file_ref`/`filename` fallback reads.
- Decision: `MIGRATE_FIRST`. Remove only after all listed consumers read the canonical location explicitly. Do not remove canonical `workbook_context`, `normalized_tables`, `column_refs`, `physical_lineage`, or `provenance`.

### `service_1_request_kind_v1`

- Definition: `pymia/smartpyme/service_1_request_kind_v1.py` defines `REQUEST_KIND_WORKBOOK`, `REQUEST_KIND_SPECIALIZED`, `REQUEST_KIND_RESULTSET_REENTRY`, and a normalizer.
- Productive consumer/producer: `service_1_owner_confirmation_to_canonical_ingestion_output_v1.py:13,120` imports `REQUEST_KIND_WORKBOOK` and emits the top-level `request_kind` field.
- No other productive runtime consumer of the helper module was found; however, the explicit `request_kind` field is listed as part of the canonical ingestion contract in the current architecture docs.
- Decision: `MIGRATE_FIRST` for the helper module; `KEEP_CANONICAL` for explicit request-kind/execution context. Absorb the helper only after the field/contract is represented by the canonical typed execution boundary.

### `semantic_reception_only`

- Definition: local switch in `service_1_product_pipeline_v1.py:501-504`, derived from `WorkbookSemanticStartRequestV1` with no requested capability.
- Productive consumer: `service_1_product_pipeline_v1.py:822-843` changes the root result into the semantic-confirmation projection.
- Decision: `MIGRATE_FIRST`. Replace the top-level/procedural switch with the explicit typed semantic command/result contract before deleting it.

### Legacy top-level `owner_answers` path

- Definitions/producers: `service_1_owner_confirmation_to_canonical_ingestion_output_v1.py:291,302,368-422,498,692` accepts and emits top-level `owner_answers`; `pymia/cli/service_1_product.py:88` supplies owner column answers to that connector.
- Productive consumer: `service_1_canonical_ingestion_output_to_semantic_bridge_v1.py:333-336` falls back to `owner_answers` when `input_values` and `normalized_values` are absent.
- Decision: `MIGRATE_FIRST`. Migrate the bridge to the canonical confirmed-ingestion/semantic evidence fields first. Do not delete the separate `OwnerAnswersBundle`/owner-confirmation evidence domain contracts; those are canonical human evidence, not this legacy alias path.

### Specialized kwargs separated from the typed command

- Definition/dispatch: `service_1_product_pipeline_v1.py:508-529,612-689` converts `SpecializedDomainExecuteRequestV1.payload` into `specialized_request`, `specialized_subtype`, `expense_variance_request`, `collection_aging_request`, and `reconciliation_request` mappings.
- Productive consumers:
  - `build_expense_variance_product_request_v1(request=dict(expense_variance_request))`.
  - `build_collection_aging_product_request_v1(request=dict(collection_aging_request))`.
  - `build_reconciliation_product_request_v1(reconciliation_request=reconciliation_request)`.
  - Web callers construct `SpecializedDomainExecuteRequestV1` in `service_1_assisted_web_v1.py:660,758,1021`.
- Decision: `MIGRATE_FIRST`. Converge the downstream call boundary on the typed specialized command/payload while preserving the specialized workflows. Keep `SpecializedDomainExecuteRequestV1` and the specialized domain contracts canonical.

### Residual legacy semantic launch projection

- Definition: `build_service_1_post_semantic_analysis_discovery_v1` in `service_1_assisted_web_semantic_reception_v1.py:99-214` explicitly documents and emits legacy `available`/`blocked` projections plus `legacy_launch_compatibility`.
- Productive consumers/callers: the same web module calls it at `:441` and `:856`; its result is returned through the web semantic flow.
- Decision: `MIGRATE_FIRST`. The deleted legacy semantic files are safe, but this surviving compatibility projection is not zero-consumer and must be migrated before removal.

## KEEP_CANONICAL

- Canonical ingestion envelope identity and evidence: `workbook_context`, `normalized_tables`, `column_refs`, `physical_lineage`, `provenance`, and false safety flags.
- Explicit request/execution context: the canonical `request_kind` field and typed `WorkbookSemanticStartRequestV1`, `WorkbookSemanticContinueRequestV1`, `WorkbookAnalysisExecuteRequestV1`, and `SpecializedDomainExecuteRequestV1` contracts.
- Owner confirmation evidence: typed owner-answer/confirmation contracts and SEM-8 dialogue evidence. Only the legacy top-level alias path is a cleanup target.
- Specialized capabilities: collection aging, expense variance, and reconciliation workflow contracts remain canonical; only their informal mapping kwargs are debt.

## R10A conclusion

```text
DELETE_SAFE = CLI normalized_tables reinjection (absent), use_assisted_semantics (absent), semantic_run_override (absent), productive sheet1 fallback (absent), removed legacy semantic files, local analysis_execution_request dict
MIGRATE_FIRST = ingestion aliases, request_kind helper absorption, semantic_reception_only, legacy top-level owner_answers, specialized mapping kwargs, residual legacy launch projection
KEEP_CANONICAL = canonical ingestion envelope, explicit request/execution contracts, owner confirmation evidence, specialized workflow contracts
PRODUCTIVE_COMPATIBILITY_SHIMS_REMAIN = YES
```

No tests were run for this read-only inventory. No runtime or test files were changed. No commit, push, deploy, reset, or checkout was performed.
