# SERVICE 1 — OPERATOR PACKET FOR REAL CONTROLLED CASE V1

## VERDICT

```text
OPERATOR_PACKET_FOR_REAL_CONTROLLED_CASE_DEFINED
```

## Mode

```text
DOC_PACKET_ONLY
NO_RUNTIME
NO_CLI_EXECUTION
NO_RAW_CLIENT_DATA
NO_DATA_PROCESSING
NO_DELIVERY
NO_PUBLISH
NO_NOTIFICATION
NO_PHASE_J
NO_SAAS_API_UI
NO_WORKER_STORAGE_QUEUE
NO_SERVICE_2
```

This document defines the operator packet structure for a future real controlled case.

It does not execute a case.
It does not ingest raw client files.
It does not run CLI.
It does not authorize runtime.
It does not deliver anything to an owner.
It does not open Phase J, SaaS/API/UI, worker/storage/queue, or Servicio 2.

## Dependency

This packet depends on:

```text
SERVICE_1_REAL_CONTROLLED_CASE_PRECHECK_GATE_V1.md
SERVICE_1_DOC_DRIFT_AND_NAMING_CLEANUP_V1.md
SERVICE_1_PHASE_I_CLOSEOUT_V1.md
docs/current/ACTIVE_ROADMAP.md
```

The precheck gate must be READY before this packet is instantiated for a specific real case.

## Purpose

```text
Give a human operator a strict preparation packet for one real controlled Service 1 case, without allowing execution or delivery by implication.
```

This packet is a containment tool. It narrows scope, evidence, allowed inputs, forbidden actions, abort triggers, and review boundaries before any supervised run can be considered.

## Boundary rule

```text
Operator packet defined ≠ case approved.
Operator packet instantiated ≠ CLI executed.
Checklist completed ≠ runtime allowed.
Evidence prepared ≠ data processed.
Manifest prepared ≠ delivery ready.
Review candidate ≠ owner delivery.
```

## Packet status vocabulary

```text
OPERATOR_PACKET_TEMPLATE_DEFINED
OPERATOR_PACKET_INSTANCE_READY
OPERATOR_PACKET_BLOCKED
OPERATOR_PACKET_UNKNOWN
```

For this document:

```text
STATUS: OPERATOR_PACKET_TEMPLATE_DEFINED
```

No case-specific packet is ready until all instance fields are completed and reviewed.

## Required instance fields

Every real controlled case packet must define:

```text
packet_ref
case_ref
tenant_ref
owner_approval_ref
operator_ref
precheck_result_ref
case_scope
allowed_data_types
prohibited_data_types
evidence_plan_ref
abort_policy_ref
expected_artifact_plan
review_plan_ref
non_delivery_acknowledgement
runtime_block_acknowledgement
service_boundary_acknowledgement
created_at
operator_signoff_ref
```

Missing any required field blocks packet instance readiness.

## Operator identity block

The operator block must include:

```text
operator_ref
operator_name_or_handle
operator_role
operator_scope
operator_contact_channel
operator_signoff_ref
```

Rules:

```text
- operator_ref must match the precheck gate operator_ref.
- operator cannot expand scope.
- operator cannot approve runtime.
- operator cannot approve delivery.
- operator can only stop, reduce, prepare, or escalate.
```

## Case scope block

Allowed structure:

```text
case_scope:
  family: <one Service 1 family only>
  business_question: <narrow owner question>
  file_categories_expected: <declared categories only>
  output_intent: <draft / review / triage / evidence check>
  explicitly_excluded: <list>
```

Scope must be narrow enough for one controlled Service 1 packet.

Blocked scope indicators:

```text
- all accounting
- complete company diagnosis
- final reconciliation
- tax validation
- automatic accounting entry
- autonomous delivery
- SaaS flow
- API execution
- Servicio 2
- Phase J
```

## Data boundary block

Allowed before execution approval:

```text
- declared file names or categories
- redacted sample description
- synthetic sample reference
- expected columns description
- owner-provided business context
- evidence plan
```

Blocked in this packet stage:

```text
- raw client files
- tax credentials
- bank credentials
- API tokens
- production DB credentials
- unrestricted customer lists
- uncontrolled accounting exports
- third-party confidential data without explicit approval
```

If blocked data appears, packet status becomes:

```text
OPERATOR_PACKET_BLOCKED
```

## Folder structure template

The packet may define this structure, but must not populate it with raw client data at this stage:

```text
case_<case_ref>/
  00_precheck/
    precheck_result.md
    owner_approval_ref.txt
    operator_assignment.md
  01_scope/
    case_scope.md
    exclusions.md
    service_boundary.md
  02_evidence_plan/
    expected_files.md
    allowed_data_types.md
    prohibited_data_types.md
    missing_evidence.md
  03_abort_policy/
    abort_triggers.md
    escalation_path.md
  04_operator_checklist/
    checklist.md
    forbidden_actions.md
    review_questions.md
  05_manifest_template/
    expected_artifacts_manifest.md
    hash_policy.md
  06_delivery_boundary/
    non_delivery_acknowledgement.md
    owner_review_limits.md
```

No raw real file should be placed in this structure by this document.

## Operator checklist

Before any later supervised run can even be requested, the operator must check:

```text
[ ] precheck_result_ref exists.
[ ] precheck status is READY.
[ ] owner_approval_ref exists.
[ ] operator_ref matches precheck.
[ ] scope is one Service 1 family only.
[ ] expected data types are allowed.
[ ] prohibited data types are absent.
[ ] evidence plan is explicit.
[ ] abort policy is explicit.
[ ] no runtime request is present.
[ ] no delivery/publish/notification request is present.
[ ] no SaaS/API/UI request is present.
[ ] no Servicio 2 scope is present.
[ ] no Phase J request is present.
[ ] owner understands this is not final accounting/tax output.
[ ] human review remains required.
```

Any unchecked item blocks the packet.

## Forbidden operator actions

The operator must not:

```text
- run CLI from this packet
- execute runtime
- ingest raw client files
- upload files to storage
- call APIs
- start a worker or queue
- publish artifacts
- notify owner
- deliver final files
- certify accounting/tax conclusions
- open Servicio 2
- open Phase J
- treat candidate outputs as final delivery
```

## Abort triggers

Abort immediately if:

```text
- precheck is missing or not READY
- owner approval is missing or ambiguous
- operator is not assigned
- operator_ref mismatch appears
- scope expands during packet preparation
- prohibited data appears
- client expects final certification
- client requests autonomous handling
- runtime/CLI execution is requested
- delivery/publish/notification is requested
- SaaS/API/UI/worker/storage/queue is requested
- Servicio 2 appears
- Phase J appears
```

## Manifest template

A future case-specific packet may include a manifest with these fields:

```text
manifest_version
packet_ref
case_ref
tenant_ref
operator_ref
precheck_result_ref
scope_ref
evidence_plan_ref
abort_policy_ref
expected_artifact_plan
forbidden_actions_acknowledged
non_delivery_acknowledged
runtime_block_acknowledged
service_boundary_acknowledged
status
created_at
```

Allowed manifest status values:

```text
PACKET_TEMPLATE_DEFINED
PACKET_INSTANCE_READY
PACKET_BLOCKED
PACKET_ABORTED
```

Forbidden manifest status values:

```text
CLI_EXECUTED
RUNTIME_EXECUTED
DELIVERY_EXECUTED
PUBLISHED
NOTIFIED
SERVICE_2_EXECUTED
PHASE_J_OPENED
```

## Expected artifact plan

The operator may plan expected artifacts but must not produce or deliver them from this document.

Allowed expected artifacts:

```text
- operator checklist
- evidence sufficiency notes
- scope boundary notes
- expected files manifest
- missing evidence list
- abort decision notes
- review questions for owner
```

Forbidden expected artifacts at this stage:

```text
- final XLSX delivery
- final accounting workpaper
- final reconciliation
- tax conclusion
- automatic journal entry
- owner-facing final packet
- production report
```

## Review boundary

Human review is mandatory.

Minimum review questions:

```text
1. Is this still Service 1?
2. Is the scope still narrow?
3. Is the owner approval explicit?
4. Is the operator assigned?
5. Are data boundaries respected?
6. Is there any hidden runtime request?
7. Is there any delivery expectation?
8. Is Servicio 2 accidentally involved?
9. Is Phase J accidentally involved?
10. Should this packet be blocked instead of prepared?
```

## If packet is READY

If a future instance reaches `OPERATOR_PACKET_INSTANCE_READY`, the only next allowed decision is whether to request a separately approved supervised run preparation front.

It still does not authorize CLI execution.

Possible next front, only by explicit decision:

```text
SERVICE_1_REAL_CONTROLLED_CASE_SUPERVISED_RUN_PREPARATION_V1
```

## If packet is BLOCKED

If blocked, choose one:

```text
- reduce scope
- return to precheck
- clarify owner approval
- assign operator
- remove prohibited data
- clarify evidence plan
- clarify abort policy
- STOP_AND_DECIDE
```

## Relation to existing operator docs

This document does not replace earlier operator-ready material.

It narrows it for the post-A→I boundary:

```text
Existing operator docs: general safe operator use.
This document: one real controlled case packet template before any run.
```

## Final declaration

```text
SERVICE_1_OPERATOR_PACKET_FOR_REAL_CONTROLLED_CASE_V1: DEFINED
PACKET_STATUS: TEMPLATE_ONLY
REAL_CASE_INSTANCE: NOT_CREATED
CLI_EXECUTION_ALLOWED_NOW: NO
RUNTIME_REAL_ALLOWED_NOW: NO
RAW_CLIENT_DATA_ALLOWED_NOW: NO
OWNER_DELIVERY_ALLOWED_NOW: NO
PHASE_J_ALLOWED_NOW: NO
SAAS_API_UI_ALLOWED_NOW: NO
SERVICE_2_ALLOWED_NOW: NO
```
