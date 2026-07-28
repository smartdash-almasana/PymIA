# S1_SAAS_RUNTIME_BOUNDARY_CONTRACTS_V1

## Status

```text
PHASE_G_PREPARATION_DOCUMENT
```

This document prepares the real SaaS runtime boundary for Servicio 1.

It does **not** start Phase G.

It does **not** implement runtime.

It defines the minimum boundary contracts required before opening any real endpoint, auth, storage/upload, or worker/runtime implementation.

---

## Purpose

Servicio 1 has completed the critical path from Phase A through Phase F.

The next risk is premature infrastructure: building API, auth, storage, uploads, workers, or UI before the runtime boundary is explicit.

This document prevents that drift by defining four pure boundary contracts:

```text
1. S1_REAL_ENDPOINT_API_BOUNDARY_CONTRACT_V1
2. S1_REAL_AUTH_BOUNDARY_CONTRACT_V1
3. S1_REAL_STORAGE_UPLOAD_BOUNDARY_CONTRACT_V1
4. S1_REAL_WORKER_RUNTIME_BOUNDARY_CONTRACT_V1
```

These are contracts only.

They are not implementations.

---

## Governing Rule

```text
Phase G can only start after the real runtime boundary is explicit.
```

The boundary must preserve the existing PymIA rule:

```text
Conversation translates.
Gates govern.
Tools execute.
Evidence decides.
Files are the product.
```

No real infrastructure may bypass:

- case/session candidate rules;
- tenant isolation;
- audit expectations;
- failure recovery classification;
- cost/rate limits;
- explicit runtime authorization gates;
- owner evidence/reentry gates;
- delivery release gates.

---

## Current Certified Dependencies

The runtime boundary depends on already implemented contracts and guards:

```text
S1_SAAS_CASE_SESSION_MODEL_V1
S1_SAAS_FILE_INTAKE_API_V1
S1_SAAS_JOB_ORCHESTRATION_V1
S1_AUDIT_LOG_V1
S1_TENANT_ISOLATION_GUARD_V1
S1_FAILURE_RECOVERY_V1
S1_COST_AND_RATE_LIMIT_GUARD_V1
S1_AUTONOMOUS_PIPELINE_RUNNER_V1
S1_AUTONOMOUS_DELIVERY_RELEASE_GATE_V1
S1_OWNER_REENTRY_TO_AUTONOMOUS_RERUN_V1
S1_LLM_GUARDED_RESPONSE_GATE_V1
```

The boundary must not weaken any of them.

---

## Boundary 1 — S1_REAL_ENDPOINT_API_BOUNDARY_CONTRACT_V1

### Purpose

Define the minimum contract for a future real API endpoint that lets a PyME owner create or interact with a Servicio 1 case.

This boundary is a protocol definition, not a web framework implementation.

### Minimum Inputs

```text
tenant_ref
owner_ref
case_ref or case_creation_payload
request_id
operation_kind
payload_ref or payload
idempotency_key
client_channel
```

### Minimum Outputs

```text
api_boundary_status
case_session_candidate_ref or case_session_candidate
accepted_operation_kind
next_required_action
errors
warnings
audit_event_candidate
runtime_authorization_required
```

### Expected Statuses

```text
API_BOUNDARY_CANDIDATE_READY
BLOCKED_MISSING_TENANT
BLOCKED_MISSING_OWNER
BLOCKED_INVALID_OPERATION
BLOCKED_INVALID_SESSION
BLOCKED_TENANT_ISOLATION
BLOCKED_COST_OR_RATE_LIMIT
BLOCKED_UNAUTHORIZED_RUNTIME
NEEDS_OWNER_INPUT
NEEDS_EVIDENCE
UNKNOWN
```

### Dependencies

Must call or preserve compatibility with:

```text
S1_SAAS_CASE_SESSION_MODEL_V1
S1_TENANT_ISOLATION_GUARD_V1
S1_COST_AND_RATE_LIMIT_GUARD_V1
S1_AUDIT_LOG_V1
```

### Explicit Non-Scope

This boundary does **not** include:

```text
FastAPI
Flask
Django
HTTP server
routing table
middleware
CORS
JWT validation
OAuth
Supabase
PostgreSQL
real request parsing
real response serialization
```

### Flags That Must Stay Governed

```text
api_exposed
runtime_authorized
pipeline_authorized
runner_authorized
storage_write_authorized
db_authorized
llm_authorized
mutation_authorized
```

No endpoint boundary may turn these on by itself.

---

## Boundary 2 — S1_REAL_AUTH_BOUNDARY_CONTRACT_V1

### Purpose

Define the minimum contract for resolving identity and authorization context before any real SaaS operation touches Servicio 1 state.

This boundary is not an auth provider.

It maps external identity into PymIA-safe references.

### Minimum Inputs

```text
auth_subject_ref
external_identity_ref
tenant_claim_ref
owner_claim_ref
requested_operation_kind
case_ref optional
session_ref optional
client_channel
```

### Minimum Outputs

```text
auth_boundary_status
tenant_ref
owner_ref
authorized_operation_kind
case_access_candidate
session_access_candidate
errors
warnings
audit_event_candidate
```

### Expected Statuses

```text
AUTH_BOUNDARY_CANDIDATE_READY
BLOCKED_MISSING_SUBJECT
BLOCKED_MISSING_TENANT_CLAIM
BLOCKED_MISSING_OWNER_CLAIM
BLOCKED_TENANT_MISMATCH
BLOCKED_OWNER_CASE_MISMATCH
BLOCKED_OPERATION_NOT_ALLOWED
BLOCKED_SESSION_NOT_ALLOWED
UNKNOWN
```

### Dependencies

Must preserve compatibility with:

```text
S1_SAAS_CASE_SESSION_MODEL_V1
S1_TENANT_ISOLATION_GUARD_V1
S1_AUDIT_LOG_V1
```

### Explicit Non-Scope

This boundary does **not** include:

```text
JWT implementation
OAuth flow
password login
session cookies
Supabase Auth
Clerk
Auth0
RBAC system
user database
password reset
email verification
```

### Flags That Must Stay Governed

```text
auth_authorized
api_exposed
db_authorized
storage_write_authorized
runtime_authorized
mutation_authorized
```

The auth boundary can produce an authorization candidate.

It cannot execute runtime or mutate case truth.

---

## Boundary 3 — S1_REAL_STORAGE_UPLOAD_BOUNDARY_CONTRACT_V1

### Purpose

Define the minimum contract for receiving file references from a PyME owner without letting upload/storage become an uncontrolled runtime path.

This boundary separates:

```text
file arrival
from
file interpretation
from
pipeline execution
```

### Minimum Inputs

```text
tenant_ref
owner_ref
case_ref
upload_request_ref
file_name
file_kind
file_size_bytes
content_type
storage_object_ref optional
checksum optional
client_channel
```

### Minimum Outputs

```text
storage_upload_boundary_status
file_intake_candidate_ref or file_intake_candidate
storage_object_ref
safe_file_ref
evidence_ref_candidate
errors
warnings
audit_event_candidate
processing_job_candidate_required
```

### Expected Statuses

```text
STORAGE_UPLOAD_BOUNDARY_CANDIDATE_READY
BLOCKED_MISSING_TENANT
BLOCKED_MISSING_OWNER
BLOCKED_MISSING_CASE
BLOCKED_INVALID_FILE_NAME
BLOCKED_INVALID_FILE_KIND
BLOCKED_INVALID_FILE_SIZE
BLOCKED_MISSING_STORAGE_REF
BLOCKED_TENANT_ISOLATION
NEEDS_FILE_INTAKE
NEEDS_OWNER_CONFIRMATION
UNKNOWN
```

### Dependencies

Must preserve compatibility with:

```text
S1_SAAS_FILE_INTAKE_API_V1
S1_SAAS_CASE_SESSION_MODEL_V1
S1_TENANT_ISOLATION_GUARD_V1
S1_AUDIT_LOG_V1
S1_COST_AND_RATE_LIMIT_GUARD_V1
```

### Explicit Non-Scope

This boundary does **not** include:

```text
real multipart upload
presigned URLs
S3
Supabase Storage
GCS
local filesystem write
virus scanning
OCR
PDF parsing
Excel parsing
file normalization
pipeline execution
```

### Flags That Must Stay Governed

```text
storage_write_authorized
file_processing_authorized
pipeline_authorized
runner_authorized
runtime_authorized
evidence_authorized
mutation_authorized
```

Upload acceptance is not evidence acceptance.

Storage reference is not case truth.

---

## Boundary 4 — S1_REAL_WORKER_RUNTIME_BOUNDARY_CONTRACT_V1

### Purpose

Define the minimum contract for turning a safe job candidate into a future runtime execution path without bypassing gates, audit, tenant isolation, failure recovery, or cost/rate limits.

This boundary is not a worker implementation.

It defines the contract around future asynchronous processing.

### Minimum Inputs

```text
tenant_ref
owner_ref
case_ref
session_ref
job_candidate_ref
operation_kind
pipeline_request_candidate_ref optional
file_intake_candidate_ref optional
cost_estimate
rate_limit_context
retry_context optional
```

### Minimum Outputs

```text
worker_runtime_boundary_status
job_execution_candidate
runtime_authorization_candidate
failure_recovery_candidate optional
audit_event_candidate
next_required_action
errors
warnings
```

### Expected Statuses

```text
WORKER_RUNTIME_BOUNDARY_CANDIDATE_READY
BLOCKED_MISSING_SESSION
BLOCKED_INVALID_JOB
BLOCKED_TENANT_ISOLATION
BLOCKED_COST_OR_RATE_LIMIT
BLOCKED_RUNTIME_NOT_AUTHORIZED
BLOCKED_PIPELINE_NOT_AUTHORIZED
BLOCKED_FAILURE_RECOVERY_REQUIRED
NEEDS_OWNER_INPUT
NEEDS_EVIDENCE
UNKNOWN
```

### Dependencies

Must preserve compatibility with:

```text
S1_SAAS_JOB_ORCHESTRATION_V1
S1_AUTONOMOUS_PIPELINE_RUNNER_V1
S1_AUTONOMOUS_DELIVERY_RELEASE_GATE_V1
S1_OWNER_REENTRY_TO_AUTONOMOUS_RERUN_V1
S1_TENANT_ISOLATION_GUARD_V1
S1_FAILURE_RECOVERY_V1
S1_COST_AND_RATE_LIMIT_GUARD_V1
S1_AUDIT_LOG_V1
```

### Explicit Non-Scope

This boundary does **not** include:

```text
Celery
RQ
BullMQ
Temporal
Prefect
cron
scheduler
queue broker
Redis
worker process
thread pool
async runtime
real retries
real job persistence
pipeline execution
```

### Flags That Must Stay Governed

```text
worker_authorized
queue_authorized
scheduler_authorized
pipeline_authorized
runner_authorized
runtime_authorized
retry_authorized
storage_write_authorized
db_authorized
mutation_authorized
```

A worker boundary candidate can propose execution.

It cannot execute by itself.

---

## Cross-Boundary Invariants

All four boundaries must preserve these invariants:

```text
No tenant_ref, no runtime.
No owner_ref, no runtime.
No case/session candidate, no runtime.
No evidence reference, no evidence claim.
No gate authorization, no tool execution.
No audit event candidate, no SaaS operation.
No cost/rate clearance, no worker execution.
No failure recovery classification, no retry.
No delivery release gate, no owner-facing final delivery.
```

---

## Required Fail-Closed Behavior

When a boundary cannot classify safely, it must return:

```text
UNKNOWN
```

or a specific `BLOCKED_*` status.

It must not infer permission from missing data.

It must not repair malformed identity, tenant, file, job, or runtime references.

---

## Phase G Opening Rule

Phase G may be opened only by a first implementation slice that explicitly names which boundary it implements.

Recommended first implementation slice:

```text
S1_REAL_ENDPOINT_API_BOUNDARY_CONTRACT_V1_IMPLEMENTATION
```

Allowed scope for that slice:

```text
pure Python contract/model
typed inputs/outputs
status classification
focal tests
source guard tests
no HTTP framework
no external infrastructure
```

Phase G should still avoid real infrastructure until all four boundary contracts are represented in code and tested as pure gates/candidates.

---

## Still Not Allowed

```text
No FastAPI.
No Flask.
No Django.
No Supabase.
No JWT/OAuth implementation.
No DB.
No storage real.
No upload real.
No worker real.
No queue real.
No scheduler real.
No UI real.
No external infrastructure.
No replacement of CLI/operator flow.
No Hermes reactivation.
No commercial claim as runtime evidence.
```

---

## Definition of Done for This Preparation Document

This document is complete when it defines:

```text
- endpoint/API boundary;
- auth boundary;
- storage/upload boundary;
- worker/runtime boundary;
- minimum inputs and outputs;
- expected statuses;
- dependencies on Phase D/F contracts;
- non-scope for each boundary;
- cross-boundary invariants;
- Phase G opening rule.
```

This document does not require tests because it is documentation-only preparation.

---

## Next Unique Front

```text
S1_REAL_ENDPOINT_API_BOUNDARY_CONTRACT_V1_IMPLEMENTATION
```

Mode:

```text
pure contract/model + tests only
no real API
no runtime
no infrastructure
```
