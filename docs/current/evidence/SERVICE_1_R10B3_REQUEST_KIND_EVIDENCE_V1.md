# Service 1 R10B3 request-kind absorption evidence

## Scope

Only the redundant `service_1_request_kind_v1` helper was absorbed. The
canonical `request_kind` field remains in the canonical ingestion envelope.
No ingestion aliases, specialized kwargs, or legacy launch projection were
changed.

## Change

- The helper's only productive consumer was
  `service_1_owner_confirmation_to_canonical_ingestion_output_v1.py`.
- `REQUEST_KIND_WORKBOOK` is now defined by that canonical ingestion-output
  contract, next to the envelope it produces.
- The untracked helper module was removed; no wrapper, alias, or fallback was
  introduced.
- The canonical envelope continues to emit `request_kind: "WORKBOOK"`.

## Verification

Helper references before: **1 productive import plus the helper definition**.

Helper references after: **0** (`service_1_request_kind_v1` and its normalizer
are absent from runtime and tests).

Focused gate:

```text
58 passed / 0 failed
```

The gate covered canonical ingestion, semantic bridge, Product Root typed
execution, request-contract dispatch, and the architecture lock.

No full suite, R11, commit, push, or deploy was performed.
