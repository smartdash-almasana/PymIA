# Service 1 — R10B2 Owner Answers Path Evidence V1

**Scope:** Remove only the legacy top-level `owner_answers` output/fallback path. Canonical owner-confirmation input contracts remain. Ingestion aliases, `request_kind`, specialized kwargs, and legacy launch projection were not changed.

## Runtime changes

- `pymia/smartpyme/service_1_owner_confirmation_to_canonical_ingestion_output_v1.py`
  - Removed top-level `owner_answers` from confirmed, unconfirmed, and blocked connector response packets.
  - Preserved the `owner_answers` function input and validation contract.
  - Preserved canonical `ingestion_output["input_values"]` and `normalized_values`.
- `pymia/smartpyme/service_1_canonical_ingestion_output_to_semantic_bridge_v1.py`
  - `_extract_input_values` now reads only canonical `input_values` and `normalized_values`; no legacy top-level fallback.
- Tests migrated to assert `ingestion_output["input_values"]` and absence of the legacy top-level output key.

## Reference gate

```text
OWNER_ANSWERS_LEGACY_REFS_BEFORE = 4
  (three connector output keys + one semantic-bridge fallback key in the target runtime)
OWNER_ANSWERS_LEGACY_REFS_AFTER = 0
  (target runtime connector/bridge output/fallback keys)
CANONICAL_OWNER_CONFIRMATION_INPUT = PRESERVED
```

The remaining `owner_answers` identifiers are canonical function inputs, owner-confirmation contracts, durable owner-answer storage, or unrelated test fixtures; they were not deleted.

## Verification

### Ingestion → semantic → owner → web focal

```text
89 passed / 0 failed
```

Executed:

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_canonical_ingestion_output_to_semantic_bridge_v1.py \
  tests/smartpyme/test_service_1_canonical_ingestion_to_region_evidence_adapter_v1.py \
  tests/smartpyme/test_service_1_multisheet_parity_guard_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py
```

### Requested CLI/Web affected focal

```text
89 passed / 15 failed
```

The 15 failures are confined to the pre-existing stale CLI tests:

- `tests/cli/test_service_1_product_cli_v1.py`
- `tests/cli/test_service_1_product_liq_001_delivery_flag_v1.py`

Their failures expect the already-removed `resolve_service_1_legacy_semantic_run_v1`, the removed `tool_requests` argument/CLI option, and the old CLI execution-mode contract. They do not exercise the R10B2 owner-answer output/fallback path. No wrapper, fallback, or unrelated CLI repair was added.

## Scope guard

```text
INGESTION_ALIASES_CHANGED = NO
REQUEST_KIND_HELPER_CHANGED = NO
SPECIALIZED_KWARGS_CHANGED = NO
LEGACY_LAUNCH_PROJECTION_CHANGED = NO
R11 = NOT_STARTED
FULL_SUITE = NOT_RUN
COMMIT = NO
PUSH = NO
DEPLOY = NO
```
