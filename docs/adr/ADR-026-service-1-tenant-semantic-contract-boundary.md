# ADR-026 — Service 1 Tenant Semantic Contract Boundary

## Status

Accepted for specification. Productive implementation requires a separate explicit authorization.

## Date

2026-08-07

## Scope

Servicio 1 tenant-scoped semantic confirmation persistence.

## Context

Servicio 1 already produces canonical `Service1OwnerConfirmationEventV1` evidence and requires explicit owner confirmation on first contact. The current product root and assisted web flow do not carry a real `tenant_id`, do not identify the confirming actor, and do not persist a versioned semantic record.

The PymIA hub requires first-load confirmations to become private tenant knowledge and later loads to reduce friction. That future behavior needs a narrow, auditable foundation before any lookup, reuse, template recognition, drift detection, contradiction resolution, or learning is allowed.

ADR-017 remains authoritative:

- `tenant_id` is the technical isolation identity;
- `cliente_id` is a business identity;
- they are not automatic synonyms.

## Decision

Create `SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1` as an immutable, tenant-scoped projection of one canonical owner-confirmation event.

The contract records:

```text
who confirmed
what source column was discussed
what semantic decision was confirmed
in which tenant and case
under which safe source context
when it was confirmed
which revision it is
which prior contract it explicitly supersedes, if any
```

The contract is evidence and governed tenant knowledge. It is not runtime permission and is not an automatic mapping recipe.

### Identity

Required:

```text
tenant_id
case_id
owner_actor_id
owner_actor_role
```

Optional:

```text
cliente_id
```

`cliente_id` must never be derived from `tenant_id`.

`session_id` must never be used as `tenant_id`.

### Evidence source

Every contract must be projected from a valid `Service1OwnerConfirmationEventV1` with `confirmed_by_owner=true`.

The projection must preserve the event lineage and compute a safe `confirmation_event_ref`. It must not copy raw uploaded bytes or raw spreadsheet rows.

### Persistence

The first implementation must be append-only and tenant-partitioned, reusing the existing tenant storage boundary.

Allowed operations:

```text
append one validated contract
list contracts for exactly one tenant
load one contract by id inside exactly one tenant
```

Forbidden operations:

```text
cross-tenant reads
in-place mutation
deletion
automatic current-version resolution
automatic reuse
runtime semantic rebinding
```

### Versioning

A first record uses `revision=1`.

A later record may use `revision=n+1` only when it:

- belongs to the same tenant and mapping series;
- explicitly references `supersedes_contract_id`;
- preserves the prior record unchanged;
- is based on a new owner-confirmation event.

Versioning does not authorize selecting or applying a current mapping in runtime.

### Safety

Every serialized contract must keep these claims false:

```text
runtime_authorized
tool_execution_authorized
product_ready
delivery_authorized
diagnosis_generated
automatic_reuse_authorized
semantic_rebind_authorized
```

## Consequences

Positive:

- owner-confirmed semantics become durable and attributable;
- tenant isolation and revision history become testable;
- future reuse and drift work gains a safe input contract;
- the canonical product root remains unchanged.

Costs:

- the web and product root still need a later identity/wiring slice;
- V1 stores knowledge but does not reduce questions yet;
- template equivalence and current-version resolution remain future contracts.

## Not authorized

This ADR does not authorize:

- changes to `service_1_product_pipeline_v1.py`;
- assisted-web identity or persistence wiring;
- automatic mapping reuse;
- second-load question reduction;
- workbook/template signature matching;
- drift or contradiction resolution;
- learning across tenants;
- LLM runtime authority;
- OCR, PDF ingestion, Servicio 2, Servicio 3, API, worker, SaaS runtime, or a second product root.

## Evidence basis

Repository:

- `pymia/smartpyme/service_1_owner_confirmation_event_v1.py`
- `pymia/smartpyme/service_1_product_pipeline_v1.py`
- `pymia/smartpyme/service_1_assisted_web_v1.py`
- `pymia/smartpyme/storage.py`
- `docs/adr/ADR-017-identity-scope-boundary.md`

Hub:

- page 13 — first load confirmation and tenant mapping memory;
- page 32 — contextual reuse, private tenant knowledge, versioning and contradiction rules;
- page 34 — Spec-Driven + Evidence-Governed + Vertical-First method.
