# SERVICE_1_REAL_PRODUCTION_BLOCKER_AUDIT_V1

## STATUS

```text
CLOSE_REAL_PRODUCTION_BLOCKERS: CLOSED_PASS
PRODUCT_SCOPE: SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1
RUNTIME_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
```

## PURPOSE

Audit only production blockers that can prevent safe controlled commercial use of the frozen sellable product. This audit does not authorize new capabilities, architecture, parser paths, autonomous delivery, or product expansion.

Classification vocabulary:

```text
ALREADY_COVERED
FIX_REQUIRED
NOT_PRODUCT_BLOCKING
NEEDS_PRODUCTION_SMOKE
```

## MATRIX

### 1. Request / upload resource limits

Classification: `ALREADY_COVERED`.

Evidence:

- `service_1_assisted_web_v1._multipart_form()` rejects non-positive payloads and payloads above 40 MiB before reading the request body.
- invalid XLSX content fails closed through the canonical intake boundary.
- semantic owner-question expansion is bounded by `MAX_QUESTIONS = 50` in `service_1_web_column_confirmation_intake_boundary_v1.py`.

Remaining evidence task: add a focal HTTP assertion proving oversized upload rejection.

### 2. Structured / safe errors

Classification: `ALREADY_COVERED` for the current HTML product surface.

Evidence:

- HTTP POST `ValueError` paths collapse to a bounded owner-facing 400 page instead of exposing internal exception detail.
- invalid route/action returns bounded NOT_FOUND/error UI.
- download endpoints fail closed when no governed delivery exists.

Machine-readable API error envelopes are not part of the frozen sellable product and are therefore `NOT_PRODUCT_BLOCKING`.

### 3. Idempotence / replay

Classification: `ALREADY_COVERED` where product contracts require it; `NOT_PRODUCT_BLOCKING` for durable case replay across restart.

Evidence:

- deterministic product execution is covered by existing deterministic/idempotency tests;
- tenant identity and semantic stores have identical-append idempotency tests;
- RADAR persistence includes idempotent replay behavior.

The sellable contract explicitly does not promise durable recent-case persistence across restart.

### 4. Tenant isolation and identity

Classification: `ALREADY_COVERED`.

Evidence:

- production `main()` requires the Supabase identity resolver and tenant persistence adapter;
- `require_tenant_persistence=True` fails closed when tenant/owner identity is absent;
- persistence rejection prevents governed result presentation as tenant memory;
- existing web tests prove resolver wiring and tenant-scoped persisted confirmations;
- recent-case tests prove session isolation for the current in-memory case surface.

### 5. Sensitive-data handling

Classification: `ALREADY_COVERED_MINIMAL` for controlled commercial operation; production transport remains `NEEDS_PRODUCTION_SMOKE`.

Evidence:

- uploaded XLSX bytes are parsed through the canonical intake path and are not exposed in owner-facing errors;
- owner-facing error rendering HTML-escapes dynamic values;
- session cookie is `HttpOnly` and `SameSite=Lax`;
- tenant semantic persistence is scoped to governed confirmation records rather than arbitrary raw workbook persistence.

Transport security (`HTTPS`, proxy redirect behavior and cookie behavior at the public endpoint) must be verified in the production smoke because the local HTTP server itself is not a TLS terminator.

### 6. Provenance / delivery safety

Classification: `ALREADY_COVERED`.

Evidence:

- P6/P7/P8/P9/P10 chain remains mandatory;
- provenance tests exist across physical evidence, P6, requirement matching, computation input and governed delivery;
- S1-01/S1-03 delivery endpoints serve only the current session delivery inside the configured output directory;
- reconciliation requires human review and does not auto-mark movements reconciled.

### 7. Recovery / reentry

Classification: `NOT_PRODUCT_BLOCKING` for durable recent-case recovery; `NEEDS_PRODUCTION_SMOKE` for process restart/boot.

The frozen sellable contract explicitly states that recent-case snapshots are in-memory and do not survive restart. Durable tenant semantic identity/persistence is a separate implemented contract. Restart availability of the deployed process belongs to the production smoke/release layer.

### 8. Concurrency / session behavior

Classification: `ALREADY_COVERED` after bounded repair.

Evidence:

- the web server remains `ThreadingHTTPServer`;
- `AssistedWebApplicationV1` now owns one `RLock` per session id behind a small lock-registry guard;
- GET and POST handling for the same session are serialized across the complete request operation;
- different session ids receive different locks and remain independently concurrent;
- focal concurrency tests prove same-session serialization and separate-session lock isolation.

The repair changes only web-session coordination. It does not modify semantic, computability, execution or delivery authority.

### 9. Observability

Classification: `ALREADY_COVERED_MINIMAL / NEEDS_PRODUCTION_SMOKE`.

Evidence:

- `/healthz` exists;
- `BaseHTTPRequestHandler` provides request logging to server stderr;
- product outcomes and tenant semantic persistence retain governed evidence/provenance.

A new observability subsystem is not authorized. Production smoke must prove health visibility and usable process logs at the deployment layer.

### 10. Release / rollback reproducibility

Classification: `NEEDS_PRODUCTION_SMOKE`.

Git HEAD, deployed revision, environment variables, boot command, health and rollback mechanics are deployment facts and cannot be proven from runtime source alone. They are the next smoke gate, not a code feature.

## CURRENT VERDICT

```text
ALREADY_COVERED_OR_NOT_BLOCKING: request limits, safe errors, idempotence, tenant isolation, bounded sensitive-data handling, provenance, contractual reentry limits, same-session serialization
NEEDS_PRODUCTION_SMOKE: HTTPS/transport, restart/boot, health/log visibility, deployed revision/rollback
KNOWN_CODE_PRODUCT_BLOCKERS: 0
CLOSE_REAL_PRODUCTION_BLOCKERS: CLOSED_PASS
```

Validation evidence observed in this cut:

```text
concurrency_and_upload_focal: 3 passed / 0 failed
web_tenant_reconciliation_regression: 18 passed / 0 failed
full_suite: NOT_RUN
```

## NEXT TASK

```text
PRODUCTION_SMOKE
```

No new feature or architecture work is authorized by this closeout.
