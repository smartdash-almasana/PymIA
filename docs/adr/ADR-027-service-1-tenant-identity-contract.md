# ADR-027 — Service 1 Tenant Identity Contract

## Status

Accepted for specification. Productive implementation requires a separate explicit authorization.

## Date

2026-08-08

## Scope

Servicio 1 minimal persistent identity boundary required before wiring owner-confirmation persistence into the real assisted-web journey.

## Authority

- `docs/adr/ADR-017-identity-scope-boundary.md`
- `docs/adr/ADR-026-service-1-tenant-semantic-contract-boundary.md`
- `docs/current/SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1_CAPABILITY_SPEC.md`

## Context

The real assisted-web journey currently has no durable business/tenant identity authority.

Observed physical behavior at `main` HEAD `3e9bd53c973f52d7ba55ec286d79b87ce6458afa`:

```text
AssistedWebApplicationV1._sessions
→ in-memory session state only
→ upload/intake
→ deterministic case_id from workbook content
→ semantic questions
→ owner_answer stored in RAM
→ run_review
→ Service1OwnerConfirmationEventV1
```

Current properties:

- `session_id` is an ephemeral UI/session key backed only by an in-process dict and cookie;
- `session_id` survives requests while the process lives but does not survive process restart;
- `case_id` is deterministic from workbook/intake context but is not a tenant identity and is not persisted as a tenant record;
- `owner_answer` is kept only in RAM in the assisted-web session;
- the owner-confirmation event contains case/source/question/answer context but no `tenant_id`, `cliente_id`, `owner_actor_id`, or `owner_actor_role`;
- existing tenant storage helpers and CLI tenant-scoped owner-answer persistence are not wired into the assisted-web journey.

Therefore the web journey has no stable authority from which `tenant_id` may safely be inferred.

## Decision

Introduce a minimal Service 1 tenant identity contract before persistence wiring.

The contract is the explicit identity envelope required to connect one real first-contact case to the tenant-scoped semantic-contract foundation.

Required identity:

```text
tenant_id
case_id
owner_actor_id
owner_actor_role
```

Optional business identity:

```text
cliente_id
```

Required source identity:

```text
source_system_ref
source_context_ref
```

### Canonical meanings

`tenant_id`:

- technical scope and storage-isolation identity;
- explicitly supplied/established for first contact;
- stable beyond one HTTP session;
- never derived from `session_id`;
- never derived from `case_id`;
- never automatically derived from `cliente_id`.

`case_id`:

- canonical case/source execution identity produced by the existing intake boundary;
- linked explicitly to the tenant identity contract;
- does not become tenant identity.

`owner_actor_id` and `owner_actor_role`:

- attributable identity of the human owner/authorized confirmer;
- mandatory before owner-confirmed semantic evidence is persisted as tenant knowledge.

`cliente_id`:

- optional business identity under ADR-017;
- may coexist with `tenant_id`;
- may not silently replace or define `tenant_id`.

`source_system_ref` and `source_context_ref`:

- safe source-level context required by the tenant semantic contract;
- must be explicit and non-empty before persistence wiring.

## Identity lifecycle

The intended first-contact boundary is:

```text
explicit tenant identity
+ owner identity
+ source identity
+ existing intake case_id
→ Service1TenantIdentityContractV1
→ owner confirmation event
→ TenantSemanticContractV1
→ tenant-scoped append-only persistence
```

The identity contract must not depend on the transient `session_id` for durability or meaning.

## Fail-closed rules

Persistence of tenant semantic knowledge must be blocked if any required identity is missing, blank, contradictory, or unsafe.

At minimum:

```text
missing tenant_id → block
missing case_id → block
missing owner_actor_id → block
missing owner_actor_role → block
missing source_system_ref → block
missing source_context_ref → block
session_id used as tenant_id → block
case_id used/derived as tenant_id → block
cliente_id auto-derived into tenant_id → block
case mismatch between identity envelope and owner-confirmation event → block
```

Blocking persistence does not by itself authorize changing calculation/execution behavior in the existing deterministic product root. Runtime consequences beyond persistence remain a separate wiring contract.

## Persistence boundary

V1 may reuse the existing tenant storage boundary:

```text
resolve_tenant_storage_root(base_dir, tenant_id)
```

but this ADR does not authorize a second tenant store, a new product root, a DB/ORM migration, or automatic semantic reuse.

The identity record, when implemented, must be tenant-scoped and append/audit oriented. Exact storage format belongs to the implementation spec.

## Explicit non-goals

This ADR does not authorize:

- automatic mapping reuse;
- second-load question reduction;
- workbook/template equivalence;
- drift or contradiction resolution;
- semantic rebinding;
- changes to deterministic formulas;
- changes to execution or delivery authorization;
- a second product root;
- LLM runtime authority;
- connector expansion;
- UX redesign;
- Servicio 2 or Servicio 3.

## Consequences

Positive:

- tenant identity becomes explicit rather than inferred from transient web state;
- owner-confirmation persistence can later be wired without abusing `session_id` or `case_id`;
- ADR-017 identity meanings remain intact;
- ADR-026 tenant semantic contracts gain a safe upstream identity authority.

Cost:

- first contact must supply/establish tenant and owner identity explicitly before semantic evidence becomes durable tenant knowledge;
- wiring remains a separate cut after this identity contract is specified and implemented.
