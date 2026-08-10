# SERVICE_1_TENANT_SEMANTIC_CONTRACT_SUPERSESSION_V1 — TaskSpec

## Objective

Close the second-load persistence failure without changing semantic authority or the productive root.

```text
same tenant + same semantic mapping series
→ load current prior contract
→ revision = prior.revision + 1
→ supersedes_contract = prior
→ append new immutable contract
```

If no prior contract exists, create revision 1 as before.

## Scope

- tenant-scoped prior-contract lookup;
- deterministic latest-revision selection;
- fail closed on ambiguous latest revision or cross-tenant data;
- pass `revision` and `supersedes_contract` into the existing canonical builder;
- preserve owner reconfirmation as mandatory evidence;
- preserve append-only persistence.

## Forbidden

- changes to `service_1_product_pipeline_v1.py`;
- automatic semantic reuse;
- semantic rebinding;
- mutation/deletion of prior contracts;
- cross-tenant lookup;
- drift/conflict-resolution policy beyond fail-closed ambiguity detection;
- LLM authority.

## Acceptance

```text
first confirmation → revision 1
second confirmation same series → revision 2
revision 2 supersedes revision 1
revision 1 remains unchanged
no prior → revision 1
ambiguous latest prior → blocked
cross-tenant prior → blocked
owner confirmation remains explicit
```

## Validation

Run focal tests for tenant semantic contract, persistence wiring, Supabase persistence, assisted web tenant persistence and memory recall, then the relevant Service 1 regression.
