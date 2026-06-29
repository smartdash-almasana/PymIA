# S1_TENANT_ISOLATION_GUARD_V1 Contract Design

This document defines the technical contract for `S1_TENANT_ISOLATION_GUARD_V1`.

Its purpose is to make Phase F implementation-ready with a **pure tenant/session/case isolation guard** for Servicio 1 SaaS candidates.

It does not create authentication, authorization, persistence, storage, runtime SaaS, API exposure, workers, or tenant infrastructure.

## Quick path

1. Consume a mandatory `S1_SAAS_CASE_SESSION_MODEL_V1` candidate as the identity anchor.
2. Consume one or more source candidates from SaaS / conversational / audit slices.
3. Validate that every provided candidate belongs to the same `owner_ref`, `case_ref`, `service_name`, and `source_session_ref` lineage.
4. Emit either a tenant isolation pass candidate or a blocked result.

## Design decision

`S1_TENANT_ISOLATION_GUARD_V1` is a **pure guard contract**.

It does **not**:

- authenticate a user;
- create a tenant;
- read a tenant database;
- write audit logs;
- write storage;
- expose an API;
- start a worker;
- enqueue jobs;
- execute pipeline or runner;
- call LLM or Pydantic AI;
- read files;
- mutate `case_truth`;
- fix mismatched tenant/session/case values automatically.

It only decides whether the provided Servicio 1 candidates are safe to be considered part of the same tenant/session/case boundary.

## Canonical constants

```text
schema_version = S1_TENANT_ISOLATION_GUARD_V1
service_name = SERVICE_1
guard_kind = TENANT_ISOLATION_GUARD_CANDIDATE
source_session_kind = SAAS_CASE_SESSION_CANDIDATE
source_file_intake_kind = SAAS_FILE_INTAKE_CANDIDATE
source_job_kind = SAAS_JOB_ORCHESTRATION_CANDIDATE
source_audit_kind = AUDIT_LOG_APPEND_CANDIDATE
source_bridge_kind = CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE
source_guarded_kind = GUARDED_LLM_RESPONSE_CANDIDATE
source_route_kind = OWNER_QUESTION_ROUTE_CANDIDATE
```

## Input contract

The contract should accept one pure payload:

```python
class Service1TenantIsolationGuardInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    saas_file_intake_candidate: dict[str, object] | None
    saas_job_orchestration_candidate: dict[str, object] | None
    audit_log_append_candidate: dict[str, object] | None
    conversational_owner_bridge_candidate: dict[str, object] | None
    guarded_llm_response_candidate: dict[str, object] | None
    owner_question_route_candidate: dict[str, object] | None
    requested_source_candidate_kinds: list[str]
    notes: list[str]
```

### Required session anchor

`saas_case_session_candidate` is mandatory.

Minimum required fields:

```python
{
    "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
    "owner_ref": str,
    "case_ref": str,
    "service_name": "SERVICE_1",
    "session_lifecycle": str,
    "current_chain_status": str,
    "service_1_state_refs": dict[str, str],
    "runtime_authorized": False,
    "job_authorized": False,
    "file_upload_authorized": False,
    "api_exposed": False,
}
```

The session candidate is the canonical identity anchor for:

```text
owner_ref
case_ref
service_name
source_session_ref
```

## Output contract

```python
class Service1TenantIsolationGuardCandidateV1(TypedDict):
    guard_kind: Literal["TENANT_ISOLATION_GUARD_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    checked_source_candidate_kinds: list[str]
    checked_source_refs: dict[str, str]
    tenant_isolation_passed: Literal[True]
    cross_tenant_access_detected: Literal[False]
    cross_case_access_detected: Literal[False]
    cross_session_access_detected: Literal[False]
    correction_applied: Literal[False]
    auth_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
```

```python
class Service1TenantIsolationGuardResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: str
    tenant_isolation_guard_candidate: Service1TenantIsolationGuardCandidateV1 | None
    blocked_reason: str | None
    auth_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]
```

## Source candidate validation

The guard may validate these source candidate kinds:

```text
SAAS_CASE_SESSION_CANDIDATE
SAAS_FILE_INTAKE_CANDIDATE
SAAS_JOB_ORCHESTRATION_CANDIDATE
AUDIT_LOG_APPEND_CANDIDATE
CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE
GUARDED_LLM_RESPONSE_CANDIDATE
OWNER_QUESTION_ROUTE_CANDIDATE
```

A provided source candidate is valid only if:

1. Its canonical kind field matches the declared source kind.
2. `service_name` is exactly `SERVICE_1`.
3. `owner_ref` matches the session anchor.
4. `case_ref` matches the session anchor.
5. Any `source_session_ref` matches the session-derived source session ref.
6. All dangerous flags are explicitly `False`.
7. The candidate does not contain correction, mutation, API, runtime, DB, storage, worker, tool, pipeline, runner, LLM, or Pydantic AI authority.

## Tenant / session / case lineage rules

### Owner lineage

All candidates must preserve the same `owner_ref` as the session anchor.

Mismatch means:

```text
BLOCKED_CROSS_TENANT_CONTEXT
```

Reason:

```text
source_owner_ref_must_match_session
```

### Case lineage

All candidates must preserve the same `case_ref` as the session anchor.

Mismatch means:

```text
BLOCKED_CROSS_CASE_CONTEXT
```

Reason:

```text
source_case_ref_must_match_session
```

### Session lineage

Any candidate with `source_session_ref` must match the deterministic session ref implied by the anchor.

Mismatch means:

```text
BLOCKED_CROSS_SESSION_CONTEXT
```

Reason:

```text
source_session_ref_must_match_session_anchor
```

### Service lineage

All candidates must preserve:

```text
service_name = SERVICE_1
```

Mismatch means:

```text
BLOCKED_INVALID_SOURCE_CANDIDATE
```

Reason:

```text
source_service_name_must_be_service_1
```

## Relation with Audit Log

`S1_AUDIT_LOG_V1` records append-only event candidates.

`S1_TENANT_ISOLATION_GUARD_V1` validates whether a candidate set is tenant-safe before a future runtime considers storing, displaying, routing, or executing anything.

The relation is:

```text
session/intake/job/conversation/audit candidates
→ tenant isolation guard
→ pass/block candidate
```

The tenant guard may inspect an `AUDIT_LOG_APPEND_CANDIDATE`, but it must not append, rewrite, delete, reorder, or persist audit events.

Audit log is observability.

Tenant isolation guard is boundary safety.

Neither one authorizes runtime.

## Statuses

Recommended result statuses:

```text
TENANT_ISOLATION_GUARD_CANDIDATE_READY
BLOCKED_MISSING_SESSION
BLOCKED_INVALID_SESSION
BLOCKED_MISSING_SOURCE_CANDIDATES
BLOCKED_UNSUPPORTED_SOURCE_KIND
BLOCKED_MISSING_SOURCE_CANDIDATE
BLOCKED_INVALID_SOURCE_CANDIDATE
BLOCKED_CROSS_TENANT_CONTEXT
BLOCKED_CROSS_CASE_CONTEXT
BLOCKED_CROSS_SESSION_CONTEXT
BLOCKED_UNSAFE_FLAGS
UNKNOWN
```

## Status meaning

| Status | Meaning |
|---|---|
| `TENANT_ISOLATION_GUARD_CANDIDATE_READY` | All requested candidates passed tenant/session/case isolation checks |
| `BLOCKED_MISSING_SESSION` | No SaaS case session candidate was provided |
| `BLOCKED_INVALID_SESSION` | Session anchor is malformed or unsafe |
| `BLOCKED_MISSING_SOURCE_CANDIDATES` | No source candidates were requested/provided for isolation checking |
| `BLOCKED_UNSUPPORTED_SOURCE_KIND` | A requested source kind is outside this contract |
| `BLOCKED_MISSING_SOURCE_CANDIDATE` | A requested source kind has no provided candidate |
| `BLOCKED_INVALID_SOURCE_CANDIDATE` | A source candidate is malformed, wrong kind, wrong service, or not safe |
| `BLOCKED_CROSS_TENANT_CONTEXT` | Source candidate owner lineage differs from session owner lineage |
| `BLOCKED_CROSS_CASE_CONTEXT` | Source candidate case lineage differs from session case lineage |
| `BLOCKED_CROSS_SESSION_CONTEXT` | Source candidate session lineage differs from session anchor |
| `BLOCKED_UNSAFE_FLAGS` | Any dangerous flag is not explicitly `False` |
| `UNKNOWN` | Reserved fallback |

## Block reasons

Recommended canonical block reasons:

```text
saas_case_session_candidate_required
session_kind_must_be_saas_case_session_candidate
session_service_name_must_be_service_1
session_owner_ref_required
session_case_ref_required
session_runtime_authorized_must_be_false
session_job_authorized_must_be_false
session_file_upload_authorized_must_be_false
session_api_exposed_must_be_false
requested_source_candidate_kinds_required
source_candidate_kind_not_supported
source_candidate_required
source_candidate_kind_mismatch
source_service_name_must_be_service_1
source_owner_ref_required
source_case_ref_required
source_owner_ref_must_match_session
source_case_ref_must_match_session
source_session_ref_must_match_session_anchor
source_flags_must_be_false
correction_applied_must_be_false
auth_authorized_must_be_false
storage_write_authorized_must_be_false
db_authorized_must_be_false
worker_authorized_must_be_false
pipeline_authorized_must_be_false
runner_authorized_must_be_false
llm_authorized_must_be_false
pydantic_ai_authorized_must_be_false
runtime_authorized_must_be_false
api_exposed_must_be_false
```

## Cross-tenant block rules

The guard must block, not normalize, when any of these conditions appears:

```text
source.owner_ref != session.owner_ref
source.case_ref != session.case_ref
source.service_name != SERVICE_1
source.source_session_ref exists and source.source_session_ref != session-derived source_session_ref
source candidate declares any dangerous flag True
source candidate asks for correction_applied=True
source kind is missing or unsupported
```

No automatic correction is allowed.

The guard must not rewrite:

- `owner_ref`
- `case_ref`
- `source_session_ref`
- `service_name`
- source refs
- audit refs
- conversational refs
- job refs

Mismatch is a hard block.

## Source refs

The output candidate should expose only safe refs:

```text
checked_source_refs: dict[str, str]
```

Allowed examples:

```text
session_ref
file_ref
evidence_ref_candidate
source_file_intake_ref
saas_job_orchestration_ref
audit_log_ref_candidate
audit_event_ref_candidate
owner_message_ref_candidate
guarded_response_ref_candidate
owner_question_route_ref_candidate
```

It must not expose:

- raw owner messages;
- raw file contents;
- parsed spreadsheet rows;
- credentials;
- API tokens;
- tenant secrets;
- DB identifiers not already present as safe refs.

## Flags that must always be false

Canonical result flags:

```text
auth_authorized
storage_write_authorized
db_authorized
worker_authorized
pipeline_authorized
runner_authorized
llm_authorized
pydantic_ai_authorized
runtime_authorized
api_exposed
```

Candidate-level flags:

```text
tenant_isolation_passed = True
cross_tenant_access_detected = False
cross_case_access_detected = False
cross_session_access_detected = False
correction_applied = False
auth_authorized = False
storage_write_authorized = False
db_authorized = False
worker_authorized = False
pipeline_authorized = False
runner_authorized = False
llm_authorized = False
pydantic_ai_authorized = False
runtime_authorized = False
api_exposed = False
```

## Minimal validation rules

Implementation should block unless all of these are true:

1. Session candidate exists.
2. Session candidate has kind `SAAS_CASE_SESSION_CANDIDATE`.
3. Session `owner_ref` is non-empty.
4. Session `case_ref` is non-empty.
5. Session `service_name` is `SERVICE_1`.
6. Session dangerous flags are explicitly `False`.
7. At least one source candidate kind is requested.
8. Each requested source kind is supported.
9. Each requested source candidate exists.
10. Each source candidate has the correct canonical kind field.
11. Each source candidate has `owner_ref` matching the session.
12. Each source candidate has `case_ref` matching the session.
13. Each source candidate has `service_name = SERVICE_1`.
14. Each source candidate with `source_session_ref` matches the session anchor.
15. Each source candidate dangerous flag is explicitly `False`.
16. No correction/mutation/runtime authority is requested or implied.

## Non-goals

This design does **not** include:

- tenant database schema;
- RBAC or ABAC;
- login sessions;
- auth provider integration;
- encryption keys;
- storage partitions;
- row-level security implementation;
- API middleware;
- UI routing;
- observability dashboards;
- audit persistence;
- runtime enforcement outside this pure contract.

## Ready-for-implementation criterion

`S1_TENANT_ISOLATION_GUARD_V1` is design-ready when implementation can preserve this invariant:

> Every accepted output proves that the provided Servicio 1 candidates share one tenant/session/case lineage, while every mismatch is blocked without correction, mutation, persistence, or runtime authority.

If that invariant is preserved, Phase F gains a safe tenant-boundary guard before real SaaS infrastructure exists.
