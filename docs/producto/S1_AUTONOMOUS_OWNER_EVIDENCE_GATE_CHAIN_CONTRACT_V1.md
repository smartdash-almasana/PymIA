# S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_CONTRACT_V1

## VERDICT

```text
MODULE_CONTRACT_AUTHORIZED_FOR_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_ONLY
```

## DOCUMENT_STATUS

```text
Type: MODULE_CONTRACT
Service: SERVICE_1
Target: S1_AUTONOMOUS_GUARDED_SAAS_V1
Active front: S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_V1
Runtime impact: FUTURE_CANDIDATE_ONLY_IF_LATER_AUTHORIZED
Code impact: NONE_IN_THIS_DOCUMENT
Tests impact: NONE_IN_THIS_DOCUMENT
Implementation authorized: NO
```

This document defines the contract for the first autonomous guarded SaaS control chain.

It does not implement code.

It does not authorize tests.

It does not modify runtime.

It does not reopen Servicio 1 Full Assisted V1.

## SOURCE_DOCUMENTS

```text
docs/producto/S1_AUTONOMOUS_GUARDED_SAAS_V1_ACTIVE_FRONT_DECISION.md
docs/current/SAAS_AUTONOMY_TARGET.md
docs/current/SERVICE_1_STATUS.md
docs/current/ACTIVE_ROADMAP.md
docs/producto/SERVICE_1_RUNTIME_GOVERNANCE_V1.md
```

## MODULE_NAME

```text
S1AutonomousOwnerEvidenceGateChainV1
```

Proposed runtime file, if later authorized:

```text
PymIA-Live/pymia/smartpyme/s1_autonomous_owner_evidence_gate_chain_v1.py
```

Proposed public function, if later authorized:

```text
build_s1_autonomous_owner_evidence_gate_chain_v1()
```

This document is a module contract only.

## RESPONSIBILITY

Evaluate whether a Servicio 1 SaaS case may advance, block, ask the owner for missing evidence/context, become eligible for release, or require operator fallback.

Canonical contracted chain:

```text
owner input
+ required evidence profile
+ received evidence profile
+ computational gate result
+ delivery release gate result
+ fallback signals
-> autonomous gate chain decision
```

The module must not execute tools, parse files, diagnose, release delivery, send messages, persist state, or call an LLM.

It produces a decision packet only.

## INPUTS_ALLOWED

Only these inputs are allowed:

| Input | Source | Required |
|---|---|---|
| `case_id` | existing case/session context | yes |
| `owner_input_status` | owner/anamnesis/reentry layer | yes |
| `required_evidence_profile` | existing service/evidence requirement layer | yes |
| `received_evidence_profile` | existing evidence/read-model layer | yes |
| `computational_gate_result` | PymIA computational gate | yes |
| `delivery_release_gate_result` | existing delivery/release gate | no |
| `owner_reentry_context` | existing owner question/reentry layer | no |
| `operator_fallback_signals` | existing fallback/supervision layer | no |
| `metadata` | local passthrough only | no |

Forbidden inputs:

```text
raw XLSX parser output as authority
LLM diagnosis
pathology shadow candidates as routing authority
operator opinion as normal-path requirement
final owner-facing delivery text
storage handles
filesystem paths as authority
HTTP requests or API payloads as runtime authority
```

## OUTPUTS_REQUIRED

The future module must return a plain JSON-serializable decision packet.

Required output shape:

```python
{
    "schema_version": str,
    "service_name": "SERVICE_1",
    "case_id": str,
    "status": str,
    "blocked_reason": str | None,
    "advance_authorized": bool,
    "owner_reentry_required": bool,
    "owner_reentry_reason": str | None,
    "owner_question_refs": list[str],
    "evidence_sufficiency_status": str,
    "computational_gate_status": str,
    "delivery_release_eligible": bool,
    "operator_fallback_required": bool,
    "operator_fallback_reason": str | None,
    "runtime_execution_authorized": bool,
    "llm_decision_authorized": bool,
    "metadata": dict,
}
```

Allowed `status` values:

```text
READY_TO_ADVANCE
BLOCKED_NEEDS_OWNER_REENTRY
BLOCKED_NEEDS_EVIDENCE
BLOCKED_BY_COMPUTATIONAL_GATE
BLOCKED_BY_RELEASE_GATE
OPERATOR_FALLBACK_REQUIRED
INVALID_INPUT
```

Allowed `evidence_sufficiency_status` values:

```text
SUFFICIENT
INSUFFICIENT
UNKNOWN
INVALID
```

Allowed `computational_gate_status` values:

```text
PASS
FAIL
UNKNOWN
NOT_RUN
INVALID
```

## DECISION_RULES

### Rule 1: missing case id

```text
If case_id is missing, return INVALID_INPUT.
```

### Rule 2: insufficient evidence

```text
If required evidence is not satisfied by received evidence, return BLOCKED_NEEDS_EVIDENCE.
advance_authorized=False.
owner_reentry_required=True.
```

### Rule 3: missing owner context

```text
If owner input is missing or context is unresolved, return BLOCKED_NEEDS_OWNER_REENTRY.
advance_authorized=False.
owner_reentry_required=True.
```

### Rule 4: computational gate fail

```text
If computational_gate_result is FAIL, return BLOCKED_BY_COMPUTATIONAL_GATE.
advance_authorized=False.
delivery_release_eligible=False.
```

### Rule 5: release gate fail

```text
If delivery_release_gate_result is present and FAIL, return BLOCKED_BY_RELEASE_GATE.
delivery_release_eligible=False.
```

### Rule 6: operator fallback

```text
If fallback signals indicate unsupported ambiguity, unsafe state, or unresolved exception, return OPERATOR_FALLBACK_REQUIRED.
Operator fallback is exceptional, not normal path.
```

### Rule 7: ready to advance

```text
Only return READY_TO_ADVANCE when:
owner input is sufficient;
required evidence is satisfied;
computational gate passes;
no operator fallback signal is active;
release gate is either not applicable or passing.
```

## SAFETY_LINE_REQUIRED

Every output must preserve:

```text
runtime_execution_authorized=False
llm_decision_authorized=False
```

This contract does not authorize runtime execution.

This contract does not authorize LLM decision-making.

A future module may only say whether advancement would be allowed by the gate chain.

It must not perform the advancement.

## OWNER_REENTRY_RULE

When evidence or context is missing, the decision packet must expose:

```text
owner_reentry_required=True
owner_reentry_reason=<specific reason>
owner_question_refs=<existing question references if supplied>
```

The module must not generate new owner-facing copy.

It may only reference existing questions or reasons supplied by upstream layers.

## RELEASE_ELIGIBILITY_RULE

Delivery release eligibility may be true only if:

```text
evidence_sufficiency_status=SUFFICIENT
computational_gate_status=PASS
status=READY_TO_ADVANCE
operator_fallback_required=False
```

The module must not release delivery.

It may only compute eligibility.

## OPERATOR_FALLBACK_RULE

Operator fallback is allowed only as an exception.

Allowed fallback reasons:

```text
UNSUPPORTED_CASE
CONFLICTING_EVIDENCE
UNRESOLVED_OWNER_CONTEXT
GATE_INCONSISTENCY
SAFETY_EXCEPTION
```

Forbidden fallback behavior:

```text
operator as mandatory normal step
operator replacing owner evidence
operator replacing computational gates
operator authorizing delivery by opinion
```

## FORBIDDEN_DEPENDENCIES

The future module must not import:

```text
external LLM SDKs
HTTP clients
web/API/FastAPI/Fasthtml surfaces
storage.py
vertical_pipeline.py
pipeline_registration.py
XLSX parsers
pathology shadow artifact builder as routing authority
delivery package builders
final release handoff modules
Service 2 modules
```

Allowed dependencies:

```text
typing
dataclasses
standard-library validation helpers
existing immutable DTO/contracts if import-safe
```

## ACCEPTANCE_TEST_DESIGN_REQUIRED_BEFORE_CODE

Before implementation, create focal tests covering at least:

```text
1. missing case_id returns INVALID_INPUT.
2. insufficient evidence blocks and requires owner reentry.
3. missing owner context blocks and requires owner reentry.
4. computational gate FAIL blocks advancement.
5. release gate FAIL blocks delivery eligibility.
6. fallback signal returns OPERATOR_FALLBACK_REQUIRED.
7. all gates satisfied returns READY_TO_ADVANCE.
8. ready output still has runtime_execution_authorized=False.
9. ready output still has llm_decision_authorized=False.
10. operator fallback is not required on normal passing case.
11. output is JSON-serializable.
12. forbidden imports are absent.
```

## STOP_CONDITIONS

Stop before implementation if missing:

```text
explicit TaskSpec
acceptance tests
input fixture model
status vocabulary
owner reentry reason mapping
forbidden import guard
```

Stop immediately if proposed behavior would:

```text
execute runtime;
call LLM;
parse uploaded files;
select tools;
release delivery;
write to storage;
make pathology candidates routing authority;
make operator normal path.
```

## NEXT_STEP_IF_LATER_AUTHORIZED

Create:

```text
S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_TASKSPEC_V1
```

It must remain tests-first and contract-bound.

## FINAL_STATUS

```text
S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_CONTRACT_V1: CREATED
RUNTIME_TOUCHED: NO
CODE_TOUCHED: NO
TESTS_RUN: NO
IMPLEMENTATION_AUTHORIZED: NO
NEXT_STEP: TASKSPEC_ONLY
```
