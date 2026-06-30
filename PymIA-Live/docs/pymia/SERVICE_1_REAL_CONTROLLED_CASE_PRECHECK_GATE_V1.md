# SERVICE 1 — REAL CONTROLLED CASE PRECHECK GATE V1

## VERDICT

```text
REAL_CONTROLLED_CASE_PRECHECK_GATE_DEFINED
```

## Mode

```text
DOC_CONTRACT_ONLY
NO_RUNTIME
NO_CLI_EXECUTION
NO_CLIENT_DATA_INGESTION
NO_OPERATOR_PACKET_YET
NO_DELIVERY
NO_PUBLISH
NO_NOTIFICATION
NO_PHASE_J
NO_SAAS_API_UI
NO_WORKER_STORAGE_QUEUE
NO_SERVICE_2
```

This gate defines the conditions required before preparing an operator packet for a real controlled case.

It does not allow actual execution.
It does not allow CLI execution.
It does not allow real client data processing.
It does not allow delivery to owner.
It does not allow publish, notification, SaaS/API/UI, worker, storage, queue, Phase J, or Servicio 2.

## Background

Service 1 A→I is closed as a candidate/supervised system.

Closed chain:

```text
readiness
→ evidence packet
→ operator supervision
→ controlled execution candidate
→ supervised CLI run result candidate
→ abort/rollback result candidate
→ controlled delivery review candidate
→ full chain composition
→ Phase I closeout
→ doc drift and naming cleanup
```

The next operational risk is crossing from candidate/supervised design toward a real controlled case without a formal precheck.

This document creates a pre-operator-packet gate.

## Gate purpose

```text
Decide whether a real controlled case may be prepared for an operator packet.
```

This gate does not decide whether a case may be executed. It decides whether it is safe to prepare the packet that would later instruct a human operator.

## Boundary rule

```text
Precheck gate defined ≠ approval granted.
Operator packet preparation ≠ CLI execution.
Case preparation ≠ data processing.
Run result candidate ≠ CLI executed.
Delivery review candidate ≠ owner delivery.
```

## Gate status vocabulary

```text
REAL_CONTROLLED_CASE_PRECHECK_READY
BLOCKED_NO_OWNER_APPROVAL_REF
BLOCKED_NO_OPERATOR_ASSIGNED
BLOCKED_SCOPE_TOO_BROAD
BLOCKED_SENSITIVE_OR_PROHIBITED_DATA
BLOCKED_MISSING_EVIDENCE_PLAN
BLOCKED_MISSING_ABORT_POLICY
BLOCKED_DELIVERY_EXPECTATION_UNSAFE
BLOCKED_RUNTIME_OR_AUTONOMY_REQUESTED
BLOCKED_SERVICE_2_SCOPE
BLOCKED_PHASE_J_OR_SAAS_REQUESTED
UNKNOWN
```

## Required inputs

A real controlled case may advance to operator packet preparation only if all required inputs exist:

```text
owner_approval_ref
operator_ref
tenant_ref
case_ref
case_scope
allowed_data_types
prohibited_data_types
evidence_plan_ref
abort_policy_ref
non_delivery_acknowledgement
human_review_acknowledgement
runtime_block_acknowledgement
service_boundary_acknowledgement
```

## Required yes/no assertions

All assertions must be explicit.

```text
OWNER_APPROVES_CASE_PREPARATION: YES
OPERATOR_ASSIGNED: YES
SCOPE_IS_NARROW: YES
EVIDENCE_PLAN_DEFINED: YES
ABORT_POLICY_DEFINED: YES
HUMAN_REVIEW_REQUIRED: YES
OWNER_DELIVERY_NOT_AUTOMATIC: YES
RUNTIME_REAL_ALLOWED_NOW: NO
CLI_EXECUTION_ALLOWED_NOW: NO
SAAS_API_UI_ALLOWED_NOW: NO
WORKER_STORAGE_QUEUE_ALLOWED_NOW: NO
SERVICE_2_ALLOWED_NOW: NO
PHASE_J_ALLOWED_NOW: NO
AUTONOMOUS_DELIVERY_ALLOWED_NOW: NO
```

## Allowed data boundary

Allowed at this gate:

```text
- case description
- synthetic or redacted sample description
- declared file categories
- operator assignment
- scope statement
- evidence plan
- abort policy
- delivery expectation limits
```

Not allowed at this gate:

```text
- raw real client files
- personal data not needed for precheck
- tax credentials
- bank credentials
- API tokens
- production database credentials
- unrestricted customer lists
- uncontrolled accounting exports
- confidential third-party data without explicit owner approval
```

## Permitted scope examples

Allowed narrow scopes:

```text
- Review one spreadsheet family for column/field readiness.
- Prepare a controlled first-aid Excel triage packet.
- Prepare a supervised operator checklist for one declared case.
- Validate whether evidence is sufficient before any run.
```

Blocked broad scopes:

```text
- Solve all accounting problems for the company.
- Automate final reconciliation.
- Send results to the owner automatically.
- Run autonomous SaaS flow.
- Connect to bank / Mercado Pago / tax systems.
- Execute Servicio 2 reconciliation.
- Open Phase J.
```

## Operator requirement

A named operator is required before operator packet preparation.

The operator is responsible for:

```text
- confirming scope
- confirming allowed data boundary
- confirming evidence plan
- confirming abort policy
- preventing runtime/autonomy drift
- preventing delivery/publish confusion
- stopping if real execution is requested prematurely
```

## Abort policy requirement

Abort policy must exist before operator packet preparation.

Minimum abort triggers:

```text
- owner approval missing or ambiguous
- scope exceeds Service 1
- evidence is insufficient
- prohibited data appears
- operator is not assigned
- client requests autonomous delivery
- client expects final accounting/tax certification
- runtime execution is requested before explicit approval
- Servicio 2 scope appears
- Phase J/SaaS/API/UI request appears
```

## Delivery expectation boundary

The owner must acknowledge:

```text
- no automatic delivery
- no final certification
- no tax/accounting opinion
- no autonomous decision
- no production runtime
- no publish/notification
- human review remains required
```

## Output of this gate

The only valid output is a decision for preparing an operator packet.

Allowed outputs:

```text
PRECHECK_READY_FOR_OPERATOR_PACKET_PREPARATION
PRECHECK_BLOCKED
PRECHECK_UNKNOWN
```

Forbidden outputs:

```text
CLI_EXECUTION_ALLOWED
RUNTIME_ALLOWED
DELIVERY_ALLOWED
PUBLISH_ALLOWED
NOTIFICATION_ALLOWED
SAAS_ALLOWED
SERVICE_2_ALLOWED
PHASE_J_ALLOWED
```

## If READY

If the gate is ready, the next allowed front is:

```text
SERVICE_1_OPERATOR_PACKET_FOR_REAL_CONTROLLED_CASE_V1
```

Even then, the operator packet must remain preparation-only unless separately approved.

## If BLOCKED

If the gate is blocked, the next action must be one of:

```text
- reduce scope
- obtain explicit owner approval
- assign operator
- define evidence plan
- define abort policy
- remove prohibited data
- clarify delivery expectation
- return to STOP_AND_DECIDE
```

## Relation to CCI cleanup

This gate depends on:

```text
SERVICE_1_PHASE_I_CLOSEOUT_V1.md
SERVICE_1_DOC_DRIFT_AND_NAMING_CLEANUP_V1.md
docs/current/ACTIVE_ROADMAP.md
```

It preserves the post-A→I finding:

```text
A_TO_I_CANDIDATE_SYSTEM: CLOSED
RUNTIME_REAL: NOT_ENABLED
PHASE_J: NOT_ALLOWED
```

## Final gate declaration

```text
REAL_CONTROLLED_CASE_PRECHECK_GATE_V1: DEFINED
OPERATOR_PACKET_ALLOWED_NOW: ONLY_AFTER_THIS_GATE_READY
CLI_EXECUTION_ALLOWED_NOW: NO
RUNTIME_REAL_ALLOWED_NOW: NO
OWNER_DELIVERY_ALLOWED_NOW: NO
PHASE_J_ALLOWED_NOW: NO
SAAS_API_UI_ALLOWED_NOW: NO
SERVICE_2_ALLOWED_NOW: NO
```
