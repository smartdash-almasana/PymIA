# SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1 — Implementation TaskSpec

## State

```text
TASKSPEC_READY
IMPLEMENTATION_REQUIRES_EXPLICIT_USER_AUTHORIZATION
```

## Objective

Implement the immutable contract and append-only tenant store defined by:

- `docs/adr/ADR-026-service-1-tenant-semantic-contract-boundary.md`;
- `docs/current/SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1_CAPABILITY_SPEC.md`;
- `docs/current/SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1_MODULECONTRACT.md`;
- `docs/current/SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1_ACCEPTANCE_EVIDENCE_SPEC.md`.

## Writable paths

Exactly:

```text
pymia/smartpyme/service_1_tenant_semantic_contract_v1.py
pymia/smartpyme/service_1_tenant_semantic_contract_store_v1.py
pymia/smartpyme/storage.py
tests/smartpyme/test_service_1_tenant_semantic_contract_v1.py
tests/smartpyme/test_service_1_tenant_semantic_contract_store_v1.py
docs/current/SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1.md
docs/current/SERVICE_1_STATUS.md
docs/current/ACTIVE_ROADMAP.md
```

`storage.py` may change only to expose the tenant-safe JSONL path or a narrowly reusable path validator. Existing storage APIs and formats must remain compatible.

## Required implementation order

```text
1. Write focal acceptance tests from TS-01 through TS-18.
2. Implement immutable contract projection.
3. Implement tenant-safe append/list/load.
4. Prove idempotency and conflict behavior.
5. Run focal tests.
6. Run bounded neighboring storage/event regression.
7. Inspect forbidden imports and changed paths.
8. Update state documents with observed evidence only.
9. Run graphify update when available.
10. Stop for independent review.
```

## Forbidden changes

```text
service_1_product_pipeline_v1.py
service_1_assisted_web_v1.py
P6/P7/P8 modules
capability registry
semantic catalogs
reconciliation modules
CLI/API/worker
LLM/RAG
template signatures
reuse/drift/contradiction logic
Servicio 2/3
OCR/PDF ingestion
```

No new root, background service, database, authentication system or free-form memory layer.

## Stop conditions

Stop and report without broadening scope if:

- current HEAD differs from the definition base and the diff is not understood;
- worktree contains unrelated changes;
- canonical owner event cannot express the required evidence;
- source context cannot be stored without raw rows;
- versioning cannot remain append-only;
- tests require changing current owner-confirmation behavior;
- cross-tenant isolation cannot be proven with the existing path boundary;
- implementation would need web/root identity wiring.

## Required report

```text
VERDICT
BASE_HEAD
FILES_CHANGED
FOCAL_TESTS
NEIGHBOR_TESTS
ACCEPTANCE_MATRIX
CROSS_TENANT_NEGATIVE
IDEMPOTENCY
FORBIDDEN_IMPORTS
GRAPHIFY
FULL_SUITE
COMMIT
PUSH
NEXT_STEP
```

## Next step after implementation closeout

Only after independent PASS:

```text
DEFINE_TENANT_IDENTITY_AND_CONFIRMATION_PERSISTENCE_WIRING_V1
```

That later slice may connect real tenant/actor identity to the first-contact flow. Mapping reuse and drift remain deferred.
