# SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1 — CapabilitySpec

## State

```text
SPECIFIED_NOT_IMPLEMENTED
FOUNDATIONAL_CAPABILITY
PRODUCT_RUNTIME_AUTHORITY: false
```

## Authority

- `AGENTS.md`
- `ARCHITECTURE_GUARDRAILS.md`
- `docs/adr/ADR-017-identity-scope-boundary.md`
- `docs/adr/ADR-026-service-1-tenant-semantic-contract-boundary.md`
- `docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md`

## Capability identity

```text
capability_id = SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1
version = 1
service = SERVICE_1
layer = EVIDENCE_AND_TENANT_KNOWLEDGE
status = SPECIFIED_NOT_IMPLEMENTED
```

## Problem

The first-contact flow confirms every active column, but the confirmation currently dies with the case/session. PymIA cannot prove, tenant by tenant, who confirmed a meaning, under which source context, or which revision is current history.

## Allowed promise

```text
PymIA can preserve an owner-confirmed column meaning as immutable,
versioned and tenant-isolated knowledge with attributable provenance.
```

## Prohibited promises

```text
PymIA already remembers automatically.
PymIA will recognize the next workbook.
PymIA can reuse a mapping because a header has the same name.
PymIA can resolve drift or contradictions automatically.
The persisted confirmation authorizes computation or delivery.
```

## Required input evidence

1. A valid `Service1OwnerConfirmationEventV1`.
2. Explicit `tenant_id`.
3. Explicit `owner_actor_id` and `owner_actor_role`.
4. Safe source context:
   - `source_system_ref`;
   - `source_context_ref`;
   - `workbook_ref`;
   - `sheet_ref`;
   - `source_column_name`;
   - `normalized_column_ref`;
   - optional inferred data type and neighboring column refs.
5. Revision metadata.
6. Optional `cliente_id`, never inferred from `tenant_id`.

No raw cell values, workbook bytes, credentials, tokens, or unrestricted free-text conversation may be persisted by this contract.

## Contract fields

| Group | Required fields |
|---|---|
| Identity | `schema_version`, `contract_id`, `mapping_series_id`, `tenant_id`, `case_id` |
| Business identity | optional `cliente_id`, never auto-derived |
| Source context | `source_system_ref`, `source_context_ref`, `workbook_ref`, `sheet_ref`, `source_column_name`, `normalized_column_ref` |
| Context metadata | optional `inferred_data_type`, `neighboring_column_refs`, `vertical_ref`, `service_ref` |
| Semantic decision | `confirmation_scope`, `confirmed_role`, `confirmed_variable`, `corrected_meaning`, `column_excluded` |
| Confirmation | `confirmation_event_ref`, `question_ref`, `owner_actor_id`, `owner_actor_role`, `confirmed_at` |
| Version | `revision`, optional `supersedes_contract_id`, `validity_status` |
| Provenance | safe refs only; all authority flags false |

## Semantic invariants

- `SEMANTIC_ROLE` requires a non-empty `confirmed_role`.
- `COLUMN_EXCLUSION` requires `column_excluded=true` and no confirmed role.
- `FREE_TEXT_MEANING` requires non-empty `corrected_meaning` and remains non-computable by itself.
- Event case, sheet, column, question and semantic decision must match the projected contract.
- `tenant_id`, source context and actor identity must be non-empty.
- `revision >= 1`.
- `revision > 1` requires `supersedes_contract_id`.
- A superseding record must preserve tenant and `mapping_series_id`.
- Any mismatch blocks; no correction or fallback is allowed.

## Mapping series identity

`mapping_series_id` must be deterministic over safe context:

```text
tenant_id
+ source_system_ref
+ source_context_ref
+ sheet_ref
+ source_column_name
```

This identity groups revision history. It does not prove that a future workbook is equivalent and must not be used for automatic reuse.

## Required states

```text
TENANT_SEMANTIC_CONTRACT_READY
TENANT_SEMANTIC_CONTRACT_RECORDED
TENANT_SEMANTIC_CONTRACT_ALREADY_RECORDED
BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT
BLOCKED_MISSING_TENANT_ID
BLOCKED_MISSING_ACTOR_IDENTITY
BLOCKED_MISSING_SOURCE_CONTEXT
BLOCKED_EVENT_CONTEXT_MISMATCH
BLOCKED_REVISION_INVALID
BLOCKED_SUPERSESSION_MISMATCH
BLOCKED_CROSS_TENANT_ACCESS
BLOCKED_CONTRACT_ID_CONFLICT
```

## Physical acceptance

The implementation is acceptable only when it proves:

1. a real canonical owner-confirmation event can be projected into revision 1;
2. the record is appended under tenant A and round-trips exactly;
3. tenant B cannot list or load tenant A records;
4. path traversal tenant ids are rejected;
5. missing actor identity blocks;
6. event/source mismatches block;
7. a valid revision 2 appends without mutating revision 1;
8. same id + same payload is idempotent;
9. same id + different payload blocks;
10. serialized records contain no raw rows or authority flags set true;
11. product root and assisted web remain unchanged;
12. no mapping lookup, reuse, drift, contradiction or semantic rebinding is introduced.

## Contribution

This capability creates the governed evidence primitive required for later tenant repetition. It does not itself complete second-load reuse or a sellable repeated-onboarding flow.
