# Service 1 — R10B1 Cleanup Evidence V1

**Scope:** Delete-safe cleanup from R10A plus migration of `semantic_reception_only` to the existing explicit `WorkbookSemanticStartRequestV1` contract. No R10C/R11 work.

## Changes

- Removed the internal `analysis_execution_request` mapping from `pymia/smartpyme/service_1_product_pipeline_v1.py`.
- The `WorkbookAnalysisExecuteRequestV1` branch now reads its typed fields directly and still calls the existing governed-analysis authority.
- Removed the `semantic_reception_only` local flag and all runtime references.
- Semantic reception is selected only by the existing explicit typed request contract and its existing `requested_capability` field; no new flag, wrapper, alias, or shape-dispatch was added.
- DELETE_SAFE items already absent in the current worktree (CLI `normalized_tables` reinjection, `use_assisted_semantics`, `semantic_run_override`, productive `sheet1`, and removed legacy semantic files) were not recreated or touched.
- Ingestion aliases, legacy `owner_answers`, specialized kwargs, `service_1_request_kind_v1`, and the legacy launch projection were not changed.

## Verification

```text
semantic_reception_only references before = 2 (definition + consumer)
semantic_reception_only references after  = 0 in pymia/ and tests/
analysis_execution_request references after = 0 in runtime/tests
Product Root + semantic/web focal = 37 passed / 0 failed
```

Executed:

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_product_pipeline_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py
```

## Compatibility-shim status

```text
semantic_reception_only = REMOVED
analysis_execution_request = REMOVED
remaining_productive_shims = YES
remaining = ingestion aliases; request_kind helper; legacy owner_answers; specialized kwargs; legacy launch projection
```

The canonical `request_kind` field, typed execution contracts, owner-confirmation evidence, specialized workflows, and canonical ingestion envelope remain intact.

No full suite, R11, commit, push, or deploy was performed.
