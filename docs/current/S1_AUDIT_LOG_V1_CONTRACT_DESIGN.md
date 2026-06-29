# S1_AUDIT_LOG_V1 Contract Design

This document defines the technical contract for `S1_AUDIT_LOG_V1`.

Its purpose is to leave Phase F implementation-ready with a **pure append-only audit candidate** that records deterministic Servicio 1 slice events without creating persistence, runtime authority, or side effects.

## Quick path

1. Consume a **READY** `S1_SAAS_CASE_SESSION_MODEL_V1` candidate as the identity anchor.
2. Consume one optional source slice candidate (`session`, `intake`, `job`, or conversational candidate) plus one structured audit event request.
3. Deterministically allow or block creation of one append-only audit event candidate.

## Design decision

`S1_AUDIT_LOG_V1` is a **pure append-only audit contract**.

It does **not**:

- create a DB record;
- write to storage;
- expose an API;
- start a worker;
- execute runtime SaaS behavior;
- trigger pipeline or runner;
- call an LLM;
- call Pydantic AI;
- write real log files;
- read uploaded files;
- mutate any existing slice;
- touch owner delivery publication.

It only validates whether a structured audit event is safe enough to remain an **append-only audit candidate**.

## Why append-only must still be explicit in a pure contract

Because this slice has **no real persistence**, it cannot pretend to append by mutating hidden state.

So the contract must express append-only behavior explicitly:

- one input request represents **one new event candidate**;
- one successful result emits **one append operation candidate**;
- no output may contain replace, update, delete, truncate, or reorder semantics.

This keeps the future runtime honest: persistence can be added later, but the contract boundary already forbids mutation.

## Canonical constants

```text
schema_version = S1_AUDIT_LOG_V1
service_name = SERVICE_1
audit_kind = AUDIT_LOG_APPEND_CANDIDATE
audit_event_kind = AUDIT_EVENT_CANDIDATE
source_session_kind = SAAS_CASE_SESSION_CANDIDATE
source_file_intake_kind = SAAS_FILE_INTAKE_CANDIDATE
source_job_kind = SAAS_JOB_ORCHESTRATION_CANDIDATE
source_bridge_kind = CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE
source_guarded_kind = GUARDED_LLM_RESPONSE_CANDIDATE
source_route_kind = OWNER_QUESTION_ROUTE_CANDIDATE
append_operation = APPEND_EVENT
```

## Input contract

The contract should accept one pure payload:

```python
class Service1AuditLogInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    saas_file_intake_candidate: dict[str, object] | None
    saas_job_orchestration_candidate: dict[str, object] | None
    conversational_owner_bridge_candidate: dict[str, object] | None
    guarded_llm_response_candidate: dict[str, object] | None
    owner_question_route_candidate: dict[str, object] | None
    audit_event_request: dict[str, object] | None
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

The session candidate is the audit identity anchor for:

- `owner_ref`
- `case_ref`
- `service_name`
- `source_session_ref`

## Structured audit event request

The audit event request must be structured and deterministic.

```python
class Service1AuditEventRequestV1(TypedDict):
    event_kind: str
    event_status: str
    event_summary: str
    event_ref_suffix: str
    append_operation: Literal["APPEND_EVENT"]
    source_slice_kind: str
    source_ref_keys: list[str]
    owner_visible: Literal[False]
    mutation_requested: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
```

### Why `event_ref_suffix` is required

A pure contract has no clock, DB sequence, or storage write.

Without an explicit caller-provided suffix, repeated equal inputs would either:

- fake uniqueness; or
- collapse multiple intended append events into the same candidate identity.

So `event_ref_suffix` is required to let a future runtime generate distinct append candidates without giving this contract hidden state.

## Output contract

```python
class Service1AuditEventCandidateV1(TypedDict):
    audit_event_kind: Literal["AUDIT_EVENT_CANDIDATE"]
    event_kind: str
    event_status: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_slice_kind: str
    source_slice_ref: str | None
    audit_log_ref_candidate: str
    audit_event_ref_candidate: str
    append_operation: Literal["APPEND_EVENT"]
    event_summary: str
    source_context_refs: dict[str, str]
    owner_visible: Literal[False]
    mutation_requested: Literal[False]
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
class Service1AuditLogAppendCandidateV1(TypedDict):
    audit_kind: Literal["AUDIT_LOG_APPEND_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    audit_log_ref_candidate: str
    append_operation: Literal["APPEND_EVENT"]
    appended_event_count: Literal[1]
    audit_event_candidate: Service1AuditEventCandidateV1
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
class Service1AuditLogResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: str
    audit_log_append_candidate: Service1AuditLogAppendCandidateV1 | None
    blocked_reason: str | None
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

## Audit event schema

The event schema should capture **what happened at the contract level**, not raw payload contents.

### Required event semantics

| Field | Meaning |
|---|---|
| `event_kind` | Canonical type of audited slice event |
| `event_status` | Deterministic slice state being recorded |
| `event_summary` | Short normalized summary of the event |
| `source_slice_kind` | Which slice produced the audited event |
| `source_slice_ref` | Optional stable ref from the audited slice |
| `source_session_ref` | Session lineage anchor |
| `source_context_refs` | Safe refs only, never raw file bytes or full free text |
| `append_operation` | Must always be `APPEND_EVENT` |
| `audit_event_ref_candidate` | Deterministic candidate ref for this append event |
| `audit_log_ref_candidate` | Deterministic candidate ref for the case audit stream |

### Source context rule

`source_context_refs` may include only already-existing safe refs such as:

- `case_ref`
- `owner_ref`
- `source_session_ref`
- `file_ref`
- `evidence_ref_candidate`
- `owner_message_ref_candidate`
- `owner_delivery_packet_ref`
- `saas_job_orchestration_ref`
- safe contextual refs preserved by the conversational bridge / guarded gate

It must **not** include:

- raw file contents;
- parsed spreadsheets;
- raw owner message bodies when only a ref exists;
- invented refs;
- runtime-only IDs not present in source candidates.

## Event kinds

Recommended canonical event kinds:

```text
SESSION_CANDIDATE_RECORDED
FILE_INTAKE_CANDIDATE_RECORDED
JOB_ORCHESTRATION_CANDIDATE_RECORDED
CONVERSATIONAL_BRIDGE_CANDIDATE_RECORDED
GUARDED_LLM_RESPONSE_CANDIDATE_RECORDED
OWNER_QUESTION_ROUTE_CANDIDATE_RECORDED
SLICE_BLOCKED_RECORDED
```

### Meaning

| Event kind | Meaning |
|---|---|
| `SESSION_CANDIDATE_RECORDED` | A `S1_SAAS_CASE_SESSION_MODEL_V1` candidate state is being recorded |
| `FILE_INTAKE_CANDIDATE_RECORDED` | A `S1_SAAS_FILE_INTAKE_API_V1` candidate state is being recorded |
| `JOB_ORCHESTRATION_CANDIDATE_RECORDED` | A `S1_SAAS_JOB_ORCHESTRATION_V1` candidate state is being recorded |
| `CONVERSATIONAL_BRIDGE_CANDIDATE_RECORDED` | An E.1 conversational bridge candidate state is being recorded |
| `GUARDED_LLM_RESPONSE_CANDIDATE_RECORDED` | An E.2 guarded conversational response candidate state is being recorded |
| `OWNER_QUESTION_ROUTE_CANDIDATE_RECORDED` | An E.3 routed conversational candidate state is being recorded |
| `SLICE_BLOCKED_RECORDED` | A deterministic blocked condition from one slice is being recorded |

## Statuses

Recommended result statuses:

```text
AUDIT_LOG_APPEND_CANDIDATE_READY
BLOCKED_MISSING_SESSION
BLOCKED_INVALID_SESSION
BLOCKED_MISSING_AUDIT_EVENT_REQUEST
BLOCKED_INVALID_AUDIT_EVENT_REQUEST
BLOCKED_UNSUPPORTED_EVENT_KIND
BLOCKED_MISSING_SOURCE_CANDIDATE
BLOCKED_INVALID_SOURCE_CANDIDATE
BLOCKED_SOURCE_CONTEXT_MISMATCH
BLOCKED_APPEND_ONLY_VIOLATION
BLOCKED_MUTATION_VIOLATION
BLOCKED_UNSAFE_FLAGS
UNKNOWN
```

## Meaning

| Status | Meaning |
|---|---|
| `AUDIT_LOG_APPEND_CANDIDATE_READY` | The append-only audit candidate is safe and deterministic |
| `BLOCKED_MISSING_SESSION` | No SaaS case session candidate was provided |
| `BLOCKED_INVALID_SESSION` | Session anchor is malformed or unsafe |
| `BLOCKED_MISSING_AUDIT_EVENT_REQUEST` | No structured audit event request was provided |
| `BLOCKED_INVALID_AUDIT_EVENT_REQUEST` | Event request is malformed or missing required fields |
| `BLOCKED_UNSUPPORTED_EVENT_KIND` | Requested event kind is outside the contract |
| `BLOCKED_MISSING_SOURCE_CANDIDATE` | The event kind requires a slice candidate that was not provided |
| `BLOCKED_INVALID_SOURCE_CANDIDATE` | The provided source candidate has the wrong kind/service or missing identity |
| `BLOCKED_SOURCE_CONTEXT_MISMATCH` | Source candidate identity does not match the session anchor |
| `BLOCKED_APPEND_ONLY_VIOLATION` | The request tries to replace/delete/update instead of append |
| `BLOCKED_MUTATION_VIOLATION` | The request attempts any mutation semantics |
| `BLOCKED_UNSAFE_FLAGS` | Any dangerous/runtime flag is not `False` |
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
session_api_exposed_must_be_false
audit_event_request_required
event_kind_required
event_kind_not_supported
event_status_required
event_summary_required
event_ref_suffix_required
append_operation_must_be_append_event
source_slice_kind_required
source_slice_kind_not_supported
source_candidate_required_for_event_kind
source_candidate_kind_mismatch
source_candidate_service_name_must_be_service_1
source_candidate_owner_ref_must_match_session
source_candidate_case_ref_must_match_session
source_candidate_flags_must_be_false
source_ref_key_not_allowed
append_only_operation_required
replace_update_delete_not_allowed
mutation_requested_must_be_false
audit_event_flags_must_be_false
```

## Append-only rule

`S1_AUDIT_LOG_V1` must preserve these invariants:

1. One successful result appends **exactly one** event candidate.
2. `append_operation` must always be `APPEND_EVENT`.
3. `appended_event_count` must always be `1`.
4. The contract may reference an audit stream candidate, but it may not read, reorder, compact, or rewrite prior events.
5. No output may contain delete, replace, merge, patch, or truncate semantics.

## No mutation rule

The audit contract must never mutate:

- the session candidate;
- the file intake candidate;
- the job orchestration candidate;
- the conversational bridge candidate;
- the guarded LLM response candidate;
- the owner question route candidate;
- `case_truth`;
- owner delivery outputs;
- any previous audit event.

It is an **observer contract**, not an authority contract.

## Relationship with session / intake / job / conversational slices

## Session (`S1_SAAS_CASE_SESSION_MODEL_V1`)

The session slice is the **mandatory identity anchor**.

Audit may record:

- session lifecycle candidate creation;
- current chain status snapshots;
- state ref availability;
- blocked session-level contract outcomes.

Audit must not:

- create or persist the session;
- authorize runtime or API exposure;
- change lifecycle state.

## File intake (`S1_SAAS_FILE_INTAKE_API_V1`)

Audit may record:

- declared file metadata candidate acceptance/block;
- `file_ref` and `evidence_ref_candidate` lineage;
- intake contract blocked reasons.

Audit must not:

- upload a file;
- read file bytes;
- parse spreadsheets;
- create storage.

## Job orchestration (`S1_SAAS_JOB_ORCHESTRATION_V1`)

Audit may record:

- requested job kind candidate;
- planned job steps candidate;
- chain refs used to describe the non-executable job;
- blocked orchestration decisions.

Audit must not:

- enqueue a job;
- start a worker;
- run a pipeline;
- call a runner.

## Conversational slices (Phase E)

Audit may record:

- E.1 bridge candidate creation/block;
- E.2 guarded response candidate creation/block;
- E.3 owner route candidate creation/block;
- safe context refs cited by conversation contracts.

Audit must not:

- log raw free-text as a new source of truth when a safe ref already exists;
- authorize LLM, chatbot, or prompt runtime;
- publish a conversational answer;
- mutate case truth from owner conversation.

## Flags that must always be false

These flags must remain `False` in:

- the input session candidate;
- the input source slice candidate, when present;
- the input audit event request;
- the output event candidate;
- the output append candidate;
- the result.

Canonical flags:

```text
owner_visible
mutation_requested
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

### Note about `owner_visible`

`owner_visible` must remain `False` because this slice is an internal audit contract candidate, not a user-facing delivery surface.

## Minimal validation rules

Implementation should block unless all of these are true:

1. Session candidate exists and is valid.
2. Structured audit event request exists and is valid.
3. `event_kind` is one of the canonical allowed kinds.
4. `event_status` is non-empty.
5. `event_summary` is non-empty after normalization.
6. `event_ref_suffix` is non-empty.
7. `append_operation` is exactly `APPEND_EVENT`.
8. `source_slice_kind` matches the event kind.
9. The required source candidate exists for the requested event kind.
10. Source candidate `owner_ref` and `case_ref` match the session anchor.
11. Any referenced safe keys exist in the selected source candidate context.
12. All dangerous/runtime/mutation/storage flags remain `False`.

## Non-goals

This design does **not** include:

- real audit DB schema;
- storage adapters;
- rotation or retention policy;
- search or filter APIs;
- analytics or monitoring dashboards;
- worker retry logs;
- tenant persistence implementation;
- delivery publication;
- message archive storage.

## Ready-for-implementation criterion

`S1_AUDIT_LOG_V1` is design-ready when implementation can preserve this invariant:

> Every accepted audit output is exactly one append-only Servicio 1 audit event candidate, anchored to a valid case session and source slice, with zero persistence authority and zero mutation authority.

If that invariant is preserved, Phase F can start with a safe audit boundary before real runtime persistence exists.