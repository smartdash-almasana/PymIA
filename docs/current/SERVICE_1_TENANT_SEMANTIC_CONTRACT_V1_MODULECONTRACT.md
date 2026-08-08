# SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1 — ModuleContract

## State

```text
MODULE_CONTRACT_DEFINED
IMPLEMENTATION_NOT_STARTED
RUNTIME_AUTHORIZED: false
AUTOMATIC_REUSE_AUTHORIZED: false
```

## Modules in scope

Future files, only after explicit implementation authorization:

```text
pymia/smartpyme/service_1_tenant_semantic_contract_v1.py
pymia/smartpyme/service_1_tenant_semantic_contract_store_v1.py
```

Focal tests:

```text
tests/smartpyme/test_service_1_tenant_semantic_contract_v1.py
tests/smartpyme/test_service_1_tenant_semantic_contract_store_v1.py
```

## Responsibility split

### Contract module

Responsible for:

- validating explicit identity and safe context;
- validating one canonical owner-confirmation event;
- projecting an immutable `Service1TenantSemanticContractV1`;
- deriving `confirmation_event_ref`, `mapping_series_id` and `contract_id` deterministically;
- serializing a closed, safe payload;
- rejecting mismatches and forbidden authority claims.

Public boundary:

```python
build_service_1_tenant_semantic_contract_v1(
    *,
    tenant_id: str,
    cliente_id: str | None,
    owner_actor_id: str,
    owner_actor_role: str,
    source_system_ref: str,
    source_context_ref: str,
    workbook_ref: str,
    source_column_name: str,
    normalized_column_ref: str,
    owner_confirmation_event: Service1OwnerConfirmationEventV1 | Mapping[str, object],
    revision: int = 1,
    supersedes_contract: Service1TenantSemanticContractV1 | Mapping[str, object] | None = None,
    inferred_data_type: str | None = None,
    neighboring_column_refs: Sequence[str] = (),
    vertical_ref: str | None = None,
    service_ref: str = "SERVICE_1",
) -> Service1TenantSemanticContractV1
```

### Store module

Responsible for:

- tenant-safe append-only persistence;
- exact tenant-scoped list/load operations;
- idempotent append of an identical record;
- conflict rejection for a reused id with different content;
- preserving insertion history and revision records.

Public boundary:

```python
append_service_1_tenant_semantic_contract_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
    contract: Service1TenantSemanticContractV1 | Mapping[str, object],
) -> Service1TenantSemanticContractAppendResultV1

list_service_1_tenant_semantic_contracts_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
) -> tuple[Service1TenantSemanticContractV1, ...]

load_service_1_tenant_semantic_contract_by_id_v1(
    *,
    base_dir: str | Path,
    tenant_id: str,
    contract_id: str,
) -> Service1TenantSemanticContractV1 | None
```

## Storage boundary

The store must reuse the existing tenant path validation semantics from `pymia/smartpyme/storage.py`.

Default artifact:

```text
<base_dir>/<tenant_id>/tenant_semantic_contracts.jsonl
```

It must not introduce a database, ORM, cache, network service, worker, or parallel storage root.

## Allowed dependencies

```text
Python standard library
pymia.smartpyme.service_1_owner_confirmation_event_v1
pymia.smartpyme.storage tenant path validation
```

## Forbidden dependencies

```text
service_1_product_pipeline_v1 calls
assisted web calls
P6/P7/P8 mutation
capability execution
delivery modules
LLM SDKs
RAG
external HTTP
database/ORM
Servicio 2 or Servicio 3
```

## Required validation

The contract module must validate:

- all required identity and context fields;
- `tenant_id != session_id` cannot be inferred or silently substituted;
- optional `cliente_id` is stored only when explicitly supplied;
- owner event is explicit and valid;
- event context matches the projection;
- semantic-scope invariants;
- revision and supersession invariants;
- no raw values or forbidden authority fields in provenance.

The store must validate:

- argument `tenant_id` equals record `tenant_id`;
- tenant id passes existing safe path rules;
- record schema and hashes are valid on load;
- cross-tenant contract ids are not searched globally;
- append is atomic enough for the existing local JSONL boundary;
- no in-place update or delete operation exists.

## Output safety line

Every contract payload must include:

```text
runtime_authorized = false
tool_execution_authorized = false
product_ready = false
delivery_authorized = false
diagnosis_generated = false
automatic_reuse_authorized = false
semantic_rebind_authorized = false
```

## Non-goals

- choosing which mapping is current;
- applying a mapping;
- reducing questions;
- comparing workbook signatures;
- detecting drift or contradiction;
- wiring HTTP identity;
- changing `AssistedWebSessionV1`;
- changing `run_service_1_product_pipeline_v1`;
- promoting Tenant Memory as implemented.

## Stop conditions

Stop implementation if:

- a caller tries to use `session_id` as tenant identity;
- actor identity would be defaulted or fabricated;
- a confirmation event cannot be matched exactly;
- persistence requires raw workbook data;
- revision history requires mutating a prior line;
- mapping reuse or P6 semantic rebinding enters scope;
- a second product or storage root is proposed.
