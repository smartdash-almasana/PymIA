# S1_FAILURE_RECOVERY_V1 Contract Design

This document defines the technical contract for `S1_FAILURE_RECOVERY_V1`.

Its purpose is to make Phase F implementation-ready with a **pure failure recovery candidate contract** that classifies deterministic Servicio 1 slice failures and emits non-executable retry or safe fallback candidates without executing real recovery, running retries, or invoking runtime infrastructure.

## Quick path

1. Consume a **READY** `S1_SAAS_CASE_SESSION_MODEL_V1` candidate as the identity anchor.
2. Consume one source slice candidate (session, intake, job, audit, or conversational) that produced a failure/blocked condition.
3. Consume a structured failure event describing what went wrong.
4. Deterministically classify the failure as **recoverable** or **non-recoverable**.
5. Emit either a `retry recovery candidate` or a `safe fallback candidate` — both non-executable.

## Design decision

`S1_FAILURE_RECOVERY_V1` is a **pure failure classification contract**.

It does **not**:

- execute real recovery or retry logic;
- start workers or queues;
- invoke schedulers or timers;
- write to DB or storage;
- expose an API;
- run pipelines or runners;
- call an LLM or Pydantic AI;
- mutate `case_truth`;
- mutate audit log events;
- correct tenant/session/case mismatches;
- hide or suppress failure conditions;
- reorder, compact, or rewrite prior error state.

It only decides whether a deterministic failure event is safe to describe as a **retry candidate** or a **fallback candidate**, leaving execution authority to a future runtime.

## Canonical constants

```text
schema_version = S1_FAILURE_RECOVERY_V1
service_name = SERVICE_1
recovery_kind = FAILURE_RECOVERY_CANDIDATE
recovery_retry_kind = FAILURE_RECOVERY_RETRY_CANDIDATE
recovery_fallback_kind = FAILURE_RECOVERY_FALLBACK_CANDIDATE
source_session_kind = SAAS_CASE_SESSION_CANDIDATE
source_file_intake_kind = SAAS_FILE_INTAKE_CANDIDATE
source_job_kind = SAAS_JOB_ORCHESTRATION_CANDIDATE
source_audit_kind = AUDIT_LOG_APPEND_CANDIDATE
source_bridge_kind = CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE
source_guarded_kind = GUARDED_LLM_RESPONSE_CANDIDATE
source_route_kind = OWNER_QUESTION_ROUTE_CANDIDATE
```

## Failure event schema

The failure event captures **what went wrong at the contract level**, not raw payload contents.

### Required failure semantics

| Field | Meaning |
|---|---|
| `failure_kind` | Canonical type of failure detected |
| `failure_status` | Deterministic slice status that triggered the failure |
| `failure_summary` | Short normalized description of the failure |
| `source_slice_kind` | Which slice produced the failure |
| `source_slice_ref` | Optional stable ref from the failed slice |
| `source_session_ref` | Session lineage anchor |
| `is_recoverable` | Whether the failure can be retried by a future runtime |
| `recovery_attempt_count` | Number of previous recovery attempts (0 for first) |
| `recovery_max_attempts` | Maximum allowed attempts before mandatory fallback |

### Failure event ref

```python
failure_event_ref_candidate: str
```

Computed deterministically:

```text
failure_event_candidate:{safe_ref(owner_ref)}:{safe_ref(case_ref)}:{safe_ref(failure_kind)}:{safe_ref(failure_ref_suffix)}
```

`failure_ref_suffix` is required (same rationale as audit log `event_ref_suffix` — pure contract has no clock or sequence).

## Recoverable vs non-recoverable classification

### Recoverable criteria

A failure is recoverable when ALL of these are true:

1. `failure_kind` is in the canonical recoverable set.
2. `recovery_attempt_count < recovery_max_attempts`.
3. The source slice candidate is still structurally valid (owner_ref, case_ref, service_name match session).
4. No mutation, runtime, storage, DB, worker, pipeline, runner, LLM, or API authority is implied.
5. The source slice candidate flags remain `False`.

Canonical recoverable failure kinds:

```text
SLICE_BLOCKED_TEMPORARY
SESSION_LIFECYCLE_BLOCKED
FILE_INTAKE_BLOCKED_RETRYABLE
JOB_ORCHESTRATION_BLOCKED_TEMPORARY
AUDIT_APPEND_BLOCKED_RETRYABLE
CONVERSATIONAL_BRIDGE_BLOCKED_TEMPORARY
GUARDED_RESPONSE_BLOCKED_TEMPORARY
OWNER_ROUTE_BLOCKED_TEMPORARY
```

### Non-recoverable criteria

A failure is non-recoverable when ANY of these are true:

1. `failure_kind` is in the canonical non-recoverable set.
2. `recovery_attempt_count >= recovery_max_attempts`.
3. The source slice candidate is structurally invalid or missing session lineage.
4. The source slice candidate carries any dangerous flag set to `True`.
5. The failure implies mutation, runtime, or storage authority.

Canonical non-recoverable failure kinds:

```text
SLICE_BLOCKED_PERMANENT
SESSION_CROSS_TENANT_VIOLATION
FILE_INTAKE_KIND_UNSUPPORTED
JOB_ORCHESTRATION_KIND_UNSUPPORTED
SOURCE_CANDIDATE_MISSING_SESSION_LINEAGE
UNSUPPORTED_FAILURE_KIND
FATAL_CONTRACT_VIOLATION
```

### Classification rule

```text
if failure_kind in NON_RECOVERABLE_KINDS:
    → non-recoverable
elif recovery_attempt_count >= recovery_max_attempts:
    → non-recoverable (exhausted)
elif failure_kind in RECOVERABLE_KINDS and all lineage/flags checks pass:
    → recoverable
else:
    → non-recoverable (unsafe)
```

## Retry recovery candidate

Emitted when the failure is classified as recoverable.

```python
class Service1FailureRecoveryRetryCandidateV1(TypedDict):
    recovery_kind: Literal["FAILURE_RECOVERY_RETRY_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    failure_event_ref_candidate: str
    failure_kind: str
    failure_status: str
    failure_summary: str
    source_slice_kind: str
    source_slice_ref: str | None
    recovery_attempt_count: int
    recovery_max_attempts: int
    source_context_refs: dict[str, str]
    recovery_execution_authorized: Literal[False]
    scheduled_retry_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    db_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
```

## Safe fallback recovery candidate

Emitted when the failure is non-recoverable.

```python
class Service1FailureRecoveryFallbackCandidateV1(TypedDict):
    recovery_kind: Literal["FAILURE_RECOVERY_FALLBACK_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    failure_event_ref_candidate: str
    failure_kind: str
    failure_status: str
    failure_summary: str
    source_slice_kind: str
    source_slice_ref: str | None
    recovery_attempt_count: int
    recovery_max_attempts: int
    fallback_reason: str
    requires_owner_intervention: bool
    requires_operator_escalation: bool
    hide_failure: Literal[False]
    source_context_refs: dict[str, str]
    owner_notified: Literal[False]
    operator_escalation_authorized: Literal[False]
    recovery_execution_authorized: Literal[False]
    scheduled_retry_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    db_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
```

Note: `requires_owner_intervention` and `requires_operator_escalation` are advisory booleans that describe the failure, not authorization flags. They inform a future runtime about the expected escalation path without authorizing it.

## Input contract

```python
class Service1FailureRecoveryInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    saas_file_intake_candidate: dict[str, object] | None
    saas_job_orchestration_candidate: dict[str, object] | None
    audit_log_append_candidate: dict[str, object] | None
    conversational_owner_bridge_candidate: dict[str, object] | None
    guarded_llm_response_candidate: dict[str, object] | None
    owner_question_route_candidate: dict[str, object] | None
    failure_event: dict[str, object] | None
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

### Structured failure event

```python
class Service1FailureEventV1(TypedDict):
    failure_kind: str
    failure_status: str
    failure_summary: str
    failure_ref_suffix: str
    source_slice_kind: str
    source_ref_keys: list[str]
    recovery_attempt_count: int
    recovery_max_attempts: int
    is_recoverable: Literal[False]  # always False in request; contract reclassifies
    owner_visible: Literal[False]
    mutation_requested: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
```

## Output contract

```python
class Service1FailureRecoveryResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: str
    failure_recovery_candidate: Service1FailureRecoveryRetryCandidateV1 | Service1FailureRecoveryFallbackCandidateV1 | None
    blocked_reason: str | None
    is_recoverable: bool
    recovery_attempt_count: int
    recovery_max_attempts: int
    recovery_execution_authorized: Literal[False]
    scheduled_retry_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    db_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]
```

## Retry candidate rules

1. `recovery_attempt_count` must be a non-negative integer.
2. `recovery_max_attempts` must be a positive integer.
3. If `recovery_attempt_count >= recovery_max_attempts`, the candidate must be fallback, not retry.
4. The candidate must never authorize execution, retry scheduling, workers, queues, DB, storage, pipeline, runner, LLM, or mutation.
5. The candidate must expose `source_context_refs` from the failed slice safe context only.
6. No candidate may include raw file contents, parsed data, owner message bodies, or credentials.

## Safe fallback candidate rules

1. `fallback_reason` is required — a short normalized description of why recovery is not possible.
2. `requires_owner_intervention` may be `True` only when the failure is structural (e.g., cross-tenant, unsupported kind) not transient.
3. `requires_operator_escalation` may be `True` only when the failure cannot be resolved by owner action alone.
4. `hide_failure` must always be `False` — failures are never suppressed.
5. `owner_notified` must always be `False` — this contract does not notify owners.
6. `operator_escalation_authorized` must always be `False` — escalation is not authorized here.

## Relation with audit log

`S1_AUDIT_LOG_V1` records the failure/recovery event as an append-only candidate.

`S1_FAILURE_RECOVERY_V1` classifies the failure and emits the recovery candidate.

The relation is:

```text
failed slice candidate + failure event
→ failure recovery contract
→ recovery candidate (retry or fallback)
→ audit log records the classification result
```

The recovery contract must not:

- write audit events directly;
- mutate existing audit log candidates;
- read or replay past audit events.

## Relation with tenant isolation guard

`S1_TENANT_ISOLATION_GUARD_V1` validates tenant/session/case lineage.

`S1_FAILURE_RECOVERY_V1` must check that the provided source candidate session lineage matches the session anchor, but it must not reimplement the full tenant isolation guard.

A cross-tenant or cross-case failure is always non-recoverable and must produce a fallback candidate with `requires_owner_intervention=True`.

The recovery contract must not:

- correct tenant/session/case mismatches;
- create or modify tenant/session/case refs;
- bypass or override the tenant isolation guard.

## Statuses

```text
FAILURE_RECOVERY_RETRY_CANDIDATE_READY
FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY
BLOCKED_MISSING_SESSION
BLOCKED_INVALID_SESSION
BLOCKED_MISSING_FAILURE_EVENT
BLOCKED_INVALID_FAILURE_EVENT
BLOCKED_UNSUPPORTED_FAILURE_KIND
BLOCKED_MISSING_SOURCE_CANDIDATE
BLOCKED_INVALID_SOURCE_CANDIDATE
BLOCKED_SOURCE_CONTEXT_MISMATCH
BLOCKED_RECOVERY_ATTEMPT_EXHAUSTED
BLOCKED_UNSAFE_RECOVERY_FLAGS
BLOCKED_UNSAFE_SOURCE_FLAGS
BLOCKED_SOURCE_OWNER_MISMATCH
BLOCKED_SOURCE_CASE_MISMATCH
BLOCKED_SOURCE_SERVICE_MISMATCH
BLOCKED_SOURCE_MUTATION_VIOLATION
BLOCKED_HIDE_FAILURE_VIOLATION
UNKNOWN
```

### Status meaning

| Status | Meaning |
|---|---|
| `FAILURE_RECOVERY_RETRY_CANDIDATE_READY` | Failure is recoverable; retry candidate emitted |
| `FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY` | Failure is non-recoverable; fallback candidate emitted |
| `BLOCKED_MISSING_SESSION` | No SaaS case session candidate provided |
| `BLOCKED_INVALID_SESSION` | Session anchor is malformed or unsafe |
| `BLOCKED_MISSING_FAILURE_EVENT` | No structured failure event provided |
| `BLOCKED_INVALID_FAILURE_EVENT` | Failure event is malformed or missing required fields |
| `BLOCKED_UNSUPPORTED_FAILURE_KIND` | Failure kind is not in the canonical set |
| `BLOCKED_MISSING_SOURCE_CANDIDATE` | Required source slice candidate not provided |
| `BLOCKED_INVALID_SOURCE_CANDIDATE` | Source candidate has wrong kind/service/identity |
| `BLOCKED_SOURCE_CONTEXT_MISMATCH` | Source candidate identity does not match session |
| `BLOCKED_RECOVERY_ATTEMPT_EXHAUSTED` | Attempt count >= max with unsafe reclassification |
| `BLOCKED_UNSAFE_RECOVERY_FLAGS` | Failure event carries dangerous flags |
| `BLOCKED_UNSAFE_SOURCE_FLAGS` | Source candidate carries dangerous flags |
| `BLOCKED_SOURCE_OWNER_MISMATCH` | Source owner_ref != session owner_ref |
| `BLOCKED_SOURCE_CASE_MISMATCH` | Source case_ref != session case_ref |
| `BLOCKED_SOURCE_SERVICE_MISMATCH` | Source service_name != SERVICE_1 |
| `BLOCKED_SOURCE_MUTATION_VIOLATION` | Source or event requests mutation semantics |
| `BLOCKED_HIDE_FAILURE_VIOLATION` | Event requests hide_failure=True |
| `UNKNOWN` | Reserved fallback |

## Block reasons

```text
saas_case_session_candidate_required
session_kind_must_be_saas_case_session_candidate
session_service_name_must_be_service_1
session_owner_ref_required
session_case_ref_required
session_runtime_authorized_must_be_false
session_api_exposed_must_be_false
failure_event_required
failure_kind_required
failure_kind_not_supported
failure_status_required
failure_summary_required
failure_ref_suffix_required
source_slice_kind_required
source_slice_kind_not_supported
source_candidate_required_for_failure_kind
source_candidate_kind_mismatch
source_candidate_service_name_must_be_service_1
source_candidate_owner_ref_must_match_session
source_candidate_case_ref_must_match_session
source_candidate_flags_must_be_false
recovery_attempt_exhausted
recovery_attempt_count_invalid
recovery_max_attempts_invalid
hide_failure_must_be_false
owner_notified_must_be_false
operator_escalation_authorized_must_be_false
mutation_requested_must_be_false
recovery_flags_must_be_false
recovery_execution_authorized_must_be_false
scheduled_retry_authorized_must_be_false
pipeline_authorized_must_be_false
runner_authorized_must_be_false
llm_authorized_must_be_false
pydantic_ai_authorized_must_be_false
runtime_authorized_must_be_false
api_exposed_must_be_false
```

## Flags that must always be false

Canonical result flags:

```text
recovery_execution_authorized
scheduled_retry_authorized
worker_authorized
queue_authorized
db_authorized
storage_write_authorized
pipeline_authorized
runner_authorized
llm_authorized
pydantic_ai_authorized
mutation_authorized
runtime_authorized
api_exposed
```

Retry candidate flags:

```text
recovery_execution_authorized = False
scheduled_retry_authorized = False
worker_authorized = False
queue_authorized = False
db_authorized = False
storage_write_authorized = False
pipeline_authorized = False
runner_authorized = False
llm_authorized = False
pydantic_ai_authorized = False
mutation_authorized = False
runtime_authorized = False
api_exposed = False
```

Fallback candidate flags (same as retry plus):

```text
owner_notified = False
operator_escalation_authorized = False
hide_failure = False
```

## Minimal validation rules

Implementation should block unless ALL of these are true:

1. Session candidate exists and is valid.
2. Structured failure event exists and is valid.
3. `failure_kind` is one of the canonical allowed kinds.
4. `failure_status` is non-empty.
5. `failure_summary` is non-empty after normalization.
6. `failure_ref_suffix` is non-empty.
7. `source_slice_kind` is one of the canonical slice kinds.
8. The required source candidate exists for the provided source slice kind.
9. Source candidate `service_name` is `SERVICE_1`.
10. Source candidate `owner_ref` matches the session anchor.
11. Source candidate `case_ref` matches the session anchor.
12. Source candidate dangerous flags are explicitly `False`.
13. `hide_failure` is explicitly `False`.
14. `owner_notified` is explicitly `False`.
15. `operator_escalation_authorized` is explicitly `False`.
16. `mutation_requested` is explicitly `False`.
17. All dangerous/runtime flags in the failure event are `False`.
18. `recovery_attempt_count` is a non-negative integer.
19. `recovery_max_attempts` is a positive integer.
20. If `recovery_attempt_count >= recovery_max_attempts`, the output must be fallback, never retry.

## Non-goals

This design does **not** include:

- real retry execution;
- worker or queue management;
- scheduler or cron integration;
- exponential backoff or timeout logic;
- alerting or notification delivery;
- escalation workflow execution;
- owner message delivery;
- operator ticket creation;
- DB or persistence for recovery state;
- state machine for retry lifecycle;
- real failure recovery automation.

## Ready-for-implementation criterion

`S1_FAILURE_RECOVERY_V1` is design-ready when implementation can preserve this invariant:

> Every accepted failure input produces exactly one non-executable recovery candidate — either a retry candidate bounded by attempt limits or a fallback candidate that preserves failure visibility — with zero execution authority, zero mutation, and zero infrastructure dependency.

If that invariant is preserved, Phase F gains a safe failure classification boundary before real recovery automation exists.
