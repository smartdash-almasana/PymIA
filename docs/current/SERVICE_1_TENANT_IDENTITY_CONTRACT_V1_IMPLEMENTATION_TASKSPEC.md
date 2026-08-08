# SERVICE_1_TENANT_IDENTITY_CONTRACT_V1 — Implementation TaskSpec

## State

```text
READY_FOR_REVIEW
IMPLEMENTATION_NOT_AUTHORIZED_BY_THIS_DOCUMENT
```

## Objective

Implement only the minimal immutable tenant identity contract and tenant-scoped persistence primitive required by ADR-027.

Do not wire the assisted-web journey in this cut.

## Base

Expected base authority:

```text
main >= 3e9bd53c973f52d7ba55ec286d79b87ce6458afa
TENANT_SEMANTIC_CONTRACT_FOUNDATION_V1 = FROZEN_IN_MAIN
```

## Required implementation boundary

Expected new modules:

```text
pymia/smartpyme/service_1_tenant_identity_contract_v1.py
pymia/smartpyme/service_1_tenant_identity_contract_store_v1.py
```

Expected tests:

```text
tests/smartpyme/test_service_1_tenant_identity_contract_v1.py
tests/smartpyme/test_service_1_tenant_identity_contract_store_v1.py
```

Existing storage helper may be reused. `storage.py` may be modified only if a strictly necessary generic tenant-storage helper is missing; no second tenant-root resolver is allowed.

## Writable paths

Implementation authorization, when granted, is limited to exactly:

```text
pymia/smartpyme/service_1_tenant_identity_contract_v1.py
pymia/smartpyme/service_1_tenant_identity_contract_store_v1.py
tests/smartpyme/test_service_1_tenant_identity_contract_v1.py
tests/smartpyme/test_service_1_tenant_identity_contract_store_v1.py
```

`pymia/smartpyme/storage.py` is not writable by default. Any need to modify it must stop the task and request explicit scope expansion.

## Forbidden productive paths

Do not modify:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/smartpyme/service_1_assisted_web_v1.py
pymia/smartpyme/service_1_owner_confirmation_event_v1.py
pymia/smartpyme/service_1_tenant_semantic_contract_v1.py
pymia/smartpyme/service_1_tenant_semantic_contract_store_v1.py
```

Do not modify owner-answer CLI wiring, connectors, APIs or workers.

## Contract requirements

The implementation must expose an immutable V1 record containing at least:

```text
schema_version
identity_contract_id
tenant_id
cliente_id (optional)
case_id
owner_actor_id
owner_actor_role
source_system_ref
source_context_ref
provenance
status
```

Runtime/reuse/rebind authority flags, if serialized for explicit safety, must all be false.

## Deterministic identity

`identity_contract_id` must be deterministic over safe canonical fields. The exact hash payload must be documented in code/tests and must not include:

```text
session_id
raw workbook bytes
raw rows
credentials
tokens
unrestricted conversation text
```

The deterministic id must support idempotent append semantics. It must not imply that the identity is a current/active mapping or authorize semantic reuse.

## Validation requirements

Fail closed on:

```text
missing/blank tenant_id
missing/blank case_id
missing/blank owner_actor_id
missing/blank owner_actor_role
missing/blank source_system_ref
missing/blank source_context_ref
unsafe tenant path
forbidden provenance authority claims
contract id / payload contradiction
cross-tenant access
```

No fallback from `session_id`, `case_id` or `cliente_id` into `tenant_id` is permitted.

## Store requirements

Allowed operations only:

```text
append one validated identity contract
list identity contracts for exactly one tenant
load one identity contract by id inside exactly one tenant
```

Forbidden:

```text
global lookup
cross-tenant search
in-place mutation
deletion
automatic current identity resolution
session-based tenant fallback
```

The store must reuse the existing tenant storage root boundary.

## Acceptance evidence

Required physical tests:

```text
TI-01 valid immutable contract
TI-02 missing tenant blocks
TI-03 missing case blocks
TI-04 missing owner actor id blocks
TI-05 missing owner actor role blocks
TI-06 missing source system blocks
TI-07 missing source context blocks
TI-08 unsafe tenant path blocks
TI-09 append + exact round-trip
TI-10 tenant A cannot load/list through tenant B
TI-11 identical append is idempotent
TI-12 same id + changed payload blocks
TI-13 cliente_id optional and not auto-derived
TI-14 no session_id fallback/field authority
TI-15 authority/reuse/rebind provenance claims block
TI-16 product root, assisted web and semantic contract modules unchanged
```

## Verification order

```text
new focal tests
→ tenant storage neighbor tests
→ diff inspection against forbidden paths
→ independent read-only review
```

Do not run the full suite unless the independent reviewer finds a reason to widen verification.

## Exit criteria

The implementation cut may be frozen only when:

```text
all TI acceptance cases pass
cross-tenant isolation is physically demonstrated
forbidden paths are unchanged
no second tenant-root resolver exists
no web wiring exists
no semantic reuse/drift logic exists
independent review = PASS
```

Only after this foundation is frozen may the project define:

```text
DEFINE_TENANT_IDENTITY_AND_CONFIRMATION_PERSISTENCE_WIRING_V1
```
