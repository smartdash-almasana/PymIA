# SERVICE_1_COLUMN_CONFIRMATION_REENTRY_MODULE_CONTRACT_V1

## VERDICT

```text
MODULE_CONTRACT_AUTHORIZED_FOR_CANDIDATE_BRIDGE_ONLY
```

## MODULE_NAME

```text
Service1ColumnConfirmationReentryCandidateBridge
```

Proposed runtime file, if later authorized:

```text
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_reentry_candidate_v1.py
```

Public function, if later authorized:

```text
build_service_1_column_confirmation_reentry_candidate_v1()
```

This document is a module contract only.

It does not authorize implementation.

## RESPONSIBILITY

Transform one answered projected Servicio 1 question from the column-confirmation family into a **classifier-ready candidate packet** while preserving the current evidence safety line.

The module is a boundary guard only:

```text
eligible projected question
+ explicit role proposal
-> candidate packet
```

It must not classify, apply, persist, recalculate, or validate evidence.

## INPUTS_ALLOWED

Only these inputs are allowed:

| Input | Source | Required |
|---|---|---|
| `projected_question` | `Service1ReentryProjectionV1.answered_questions[]` | yes |
| `proposed_role` | caller-provided existing column-confirmation context | no |
| `suggested_semantic_role` | caller-provided existing column-confirmation context | no |
| `metadata` | local passthrough only | no |

### Required eligibility of `projected_question`

The module may proceed only if:

```text
projected_question.source == column_confirmation_matrix
projected_question.answer_type == confirm_column_role
projected_question.projection_status == ANSWERED
projected_question.latest_raw_owner_answer is not empty
projected_question.target_ref is present
projected_question.owner_answer_validation_status == DECLARED_NOT_VALIDATED
```

At least one of these must be present:

```text
proposed_role
suggested_semantic_role
```

Forbidden inputs:

```text
ColumnConfirmationMatrix
Service1ColumnConfirmationClassificationV1
Service1ColumnConfirmationApplierResultV1
Service1ColumnConfirmationCasePatchV1
storage handles
JSONL paths
vertical_pipeline output
LLM output
inferred roles from free text only
```

## OUTPUTS_REQUIRED

The module must produce a candidate packet only.

Required output shape:

```python
{
    "schema_version": str,
    "service_name": str,
    "status": str,
    "blocked_reason": str | None,
    "question_ref": str,
    "question_source": str,
    "target_ref": str | None,
    "parsed_target_ref": dict | None,
    "answer_type": str,
    "raw_owner_answer": str | None,
    "proposed_role": str,
    "owner_answer_validation_status": str,
    "runtime_authorized": bool,
    "human_review_required": bool,
    "reexecution_authorized": bool,
    "recalculation_authorized": bool,
    "metadata": dict,
}
```

Expected allowed `status` values:

```text
READY_FOR_CLASSIFIER
BLOCKED
```

Expected allowed `blocked_reason` values:

```text
QUESTION_SOURCE_UNSUPPORTED
ANSWER_TYPE_UNSUPPORTED
QUESTION_NOT_ANSWERED
RAW_OWNER_ANSWER_MISSING
TARGET_REF_INVALID
ROLE_MISSING
OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED
```

## INTERNAL_FUNCTIONS_ALLOWED

Public function:

```text
build_service_1_column_confirmation_reentry_candidate_v1()
```

Allowed internal helpers:

```text
_validate_projected_question()
_normalize_role()
_parse_target_ref()
_build_ready_packet()
_build_blocked_packet()
```

Allowed logic:

```text
field validation
status gating
target_ref parsing
plain metadata passthrough
fixed blocked-reason selection
```

Forbidden helper behavior:

```text
_infer_role_from_text()
_classify_owner_answer()
_apply_owner_answer()
_emit_case_patch()
_persist()
_recalculate()
_promote_evidence()
_call_llm()
```

## FORBIDDEN_DEPENDENCIES

The future module must not import:

```text
vertical_pipeline.py
storage.py
pipeline_registration.py
diagnostic_core modules
service_1_column_confirmation_applier_v1.py
service_1_column_confirmation_case_patch_v1.py
web/auth/postgres/fasthtml surfaces
external HTTP clients
external LLM SDKs
```

Allowed dependencies:

```text
typing
dataclasses
existing projection/read-model types, if import-safe
column confirmation contract types, if import-safe
standard-library helpers needed for validation only
```

## SAFETY_LINE_REQUIRED

Every output packet must preserve:

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
owner_answer_validation_status=DECLARED_NOT_VALIDATED
```

The module must never transform:

```text
declared owner input -> validated evidence
```

## NON_GOALS

This module must not:

```text
classify the answer
apply the answer to ColumnConfirmationMatrix
persist anything
emit a case patch
unlock computation
unlock recalculation
change projection status
change read-model state
invent missing target refs
invent missing semantic roles
```

## NEXT_STEP_IF_LATER_AUTHORIZED

If this module is ever implemented safely, the next slice may evaluate whether a separate classifier-consumption contract is needed.

It must still remain before:

```text
applier
case patch
persistence
recalculation
```
