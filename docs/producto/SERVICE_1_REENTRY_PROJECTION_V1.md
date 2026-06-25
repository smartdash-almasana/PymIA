# SERVICE_1_REENTRY_PROJECTION_V1

## Verdict

```text
STATUS: IMPLEMENTED_PROJECTION
RUNTIME_AUTHORIZED: FALSE
HUMAN_REVIEW_REQUIRED: TRUE
REEXECUTION_AUTHORIZED: FALSE
RECALCULATION_AUTHORIZED: FALSE
WEB_OR_CHAT_RUNTIME: NOT_INCLUDED
```

## Purpose

`SERVICE_1_REENTRY_PROJECTION_V1` is the first pure state projection over Servicio 1 reentry data.

It combines:

```text
Service1QuestionBundleV1
+ Service1CaseReentryReadModelV1
```

and derives:

```text
answered_questions
pending_questions
answered_question_refs
pending_question_refs
selected_next_pending_question_ref
projection status
```

It does not mutate question status, storage, evidence, pipeline records, or column confirmation.

## Input

```text
question_bundle: Service1QuestionBundleV1
read_model: Service1CaseReentryReadModelV1
metadata: optional dict
```

## Output

```text
Service1ReentryProjectionV1
```

Fields:

```text
schema_version
service_name
status
blocked_reason
case_id
tenant_id
intake_id
source_run_id
read_model_status
total_questions
answered_count
pending_count
answered_question_refs
pending_question_refs
selected_next_pending_question_ref
answered_questions
pending_questions
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
metadata
```

Each projected question is represented as:

```text
Service1ProjectedQuestionV1
```

with:

```text
question_ref
source
text
target_ref
answer_type
required
original_status
projection_status
latest_answer_id
latest_raw_owner_answer
owner_answer_validation_status
metadata
```

## Projection statuses

```text
NO_QUESTIONS
NO_ANSWERS
PARTIAL
COMPLETE
BLOCKED
```

## Blocked path

```text
CASE_MISMATCH
```

A projection is blocked when `question_bundle` and `read_model` do not share the same `tenant_id + intake_id`.

## Matching rule

A question is projected as `ANSWERED` when its `question_ref` appears in the read model answers.

If multiple answers exist for the same `question_ref`, the latest answer in read model order is used for the projected answer view.

## Safety line

This slice preserves:

```text
runtime_authorized=false
human_review_required=true
reexecution_authorized=false
recalculation_authorized=false
```

Projection means state derivation only. It is not evidence validation, recalculation, or delivery authorization.

## Non-goals

This slice explicitly does not:

- write to storage
- update question status in the bundle
- update evidence request status
- re-run `vertical_pipeline`
- recalculate evidence
- apply column confirmation
- generate new questions
- infer answer validity
- implement CLI, web, HTTP, chat, or LLM behavior
- authorize runtime/productive delivery

## Implemented file

```text
PymIA-Live/pymia/smartpyme/service_1_reentry_projection_v1.py
```

## Test file

```text
PymIA-Live/tests/smartpyme/test_service_1_reentry_projection_v1.py
```

## Position in the Servicio 1 reentry chain

```text
SERVICE_1_QUESTION_BUNDLE_AND_REF_V1
-> SERVICE_1_OWNER_ANSWER_REENTRY_V1
-> SERVICE_1_OWNER_ANSWER_REENTRY_PERSISTENCE_V1
-> SERVICE_1_CASE_REENTRY_READ_MODEL_V1
-> SERVICE_1_REENTRY_PROJECTION_V1
```

## Next valid slice

```text
SERVICE_1_COLUMN_CONFIRMATION_REENTRY_AUDIT_V1
```

Reason:

```text
The next step would start mapping projected owner answers to column-confirmation targets.
That touches evidence semantics, so it should be audited before implementation.
```
