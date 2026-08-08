# SERVICE_1_TENANT_IDENTITY_CONTRACT_V1 — CapabilitySpec

## State

```text
SPECIFIED_NOT_IMPLEMENTED
FOUNDATIONAL_IDENTITY_CAPABILITY
PRODUCT_RUNTIME_AUTHORITY: false
```

## Authority

- `docs/adr/ADR-017-identity-scope-boundary.md`
- `docs/adr/ADR-026-service-1-tenant-semantic-contract-boundary.md`
- `docs/adr/ADR-027-service-1-tenant-identity-contract.md`
- `docs/current/SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1_CAPABILITY_SPEC.md`

## Capability identity

```text
capability_id = SERVICE_1_TENANT_IDENTITY_CONTRACT_V1
version = 1
service = SERVICE_1
layer = IDENTITY_AND_TENANT_SCOPE
status = SPECIFIED_NOT_IMPLEMENTED
```

## Problem

The assisted-web first-contact journey has no durable tenant/business identity authority.

Today:

- `session_id` is transient UI state;
- `case_id` is deterministic intake identity, not tenant identity;
- `owner_answer` is RAM-only;
- `Service1OwnerConfirmationEventV1` has case/source/question evidence but no tenant or owner actor identity;
- tenant-scoped storage exists elsewhere but is not wired into the assisted-web journey.

Without an explicit identity contract, wiring owner-confirmation persistence would require unsafe inference or duplicate identity authority.

## Allowed promise

```text
PymIA can establish an explicit, tenant-scoped and attributable identity envelope
for one Servicio 1 first-contact case before semantic confirmation evidence is persisted.
```

## Prohibited promises

```text
The browser session identifies the tenant.
The workbook/case identifies the tenant.
cliente_id and tenant_id are automatically equivalent.
The identity contract authorizes calculation, execution or delivery.
Persisting identity enables automatic mapping reuse.
```

## Required inputs

```text
tenant_id
case_id
owner_actor_id
owner_actor_role
source_system_ref
source_context_ref
```

Optional:

```text
cliente_id
```

## Contract fields

| Group | Fields |
|---|---|
| Contract | `schema_version`, `identity_contract_id`, `status` |
| Tenant identity | `tenant_id` |
| Business identity | optional `cliente_id` |
| Case identity | `case_id` |
| Owner identity | `owner_actor_id`, `owner_actor_role` |
| Source identity | `source_system_ref`, `source_context_ref` |
| Provenance | safe identity-establishment metadata only |
| Safety | all runtime/reuse/rebind authority flags false |

The implementation may include an explicit `created_at`/`established_at` field if required for auditability, but time must not become identity authority.

## Identity invariants

1. `tenant_id` is required and non-empty.
2. `case_id` is required and non-empty.
3. `owner_actor_id` is required and non-empty.
4. `owner_actor_role` is required and non-empty.
5. `source_system_ref` is required and non-empty.
6. `source_context_ref` is required and non-empty.
7. `cliente_id` is optional.
8. `tenant_id` must never be derived from `session_id`.
9. `tenant_id` must never be derived from `case_id`.
10. `tenant_id` must never be automatically derived from `cliente_id`.
11. `case_id` remains the existing intake/case identity and does not become tenant scope.
12. The same identity contract cannot grant runtime, tool, delivery, reuse or semantic-rebind authority.
13. Any contradictory identity input fails closed.

## Session boundary

`session_id` may continue to route in-memory web state, but:

```text
session_id is not persisted as tenant identity
session_id is not hashed/translated into tenant_id
session_id is not accepted as fallback tenant_id
```

The implementation must keep the transient web-session boundary conceptually separate from the persistent tenant identity boundary.

## Relationship with the semantic contract

`Service1TenantIdentityContractV1` is upstream evidence for later wiring.

It must provide the identity/context required to safely call:

```text
build_service_1_tenant_semantic_contract_v1(...)
```

without deriving tenant/owner identity from the owner-confirmation event or the browser session.

The identity contract itself does not persist semantic mappings.

## Required states

At minimum:

```text
TENANT_IDENTITY_CONTRACT_READY
TENANT_IDENTITY_CONTRACT_RECORDED
TENANT_IDENTITY_CONTRACT_ALREADY_RECORDED
BLOCKED_MISSING_TENANT_ID
BLOCKED_MISSING_CASE_ID
BLOCKED_MISSING_OWNER_IDENTITY
BLOCKED_MISSING_SOURCE_IDENTITY
BLOCKED_INVALID_TENANT_IDENTITY
BLOCKED_IDENTITY_CONTEXT_MISMATCH
BLOCKED_CROSS_TENANT_ACCESS
BLOCKED_IDENTITY_CONTRACT_CONFLICT
```

Exact naming may be refined by the ModuleContract, but semantics may not be weakened.

## Persistence requirements

V1 persistence must be:

```text
tenant-scoped
append/audit oriented
path-traversal safe
idempotent for identical contract id + payload
fail-closed for same id + different payload
```

Existing storage boundary must be reused where compatible. Do not introduce a second tenant-root resolver.

## Physical acceptance

Implementation is acceptable only when it proves:

1. valid explicit identity builds a ready immutable contract;
2. missing each required identity blocks;
3. unsafe tenant ids/path traversal block;
4. tenant A records cannot be loaded/listed through tenant B;
5. identical append is idempotent;
6. same contract id with different payload blocks;
7. `cliente_id` remains optional and is never inferred from `tenant_id`;
8. no API accepts `session_id` as tenant fallback;
9. case identity and tenant identity remain independent;
10. all runtime/reuse/rebind authority flags remain false;
11. product root and deterministic formulas remain unchanged;
12. assisted-web wiring remains outside this implementation cut unless separately authorized.

## Explicitly deferred

```text
assisted-web identity input UX
owner_answer persistence wiring
TenantSemanticContract append wiring
automatic mapping reuse
second-load recognition
drift/template matching
connectors
new capabilities
Servicio 2 / Servicio 3
```

## Contribution

This capability closes the missing identity authority required before Servicio 1 can safely persist first-contact owner-confirmed semantics as tenant knowledge.
