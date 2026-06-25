# SERVICE_1_OWNER_ANSWER_REENTRY_V1

## Verdict

```text
STATUS: IMPLEMENTED_CONTRACT
RUNTIME_AUTHORIZED: FALSE
HUMAN_REVIEW_REQUIRED: TRUE
REEXECUTION_AUTHORIZED: FALSE
RECALCULATION_AUTHORIZED: FALSE
WEB_OR_CHAT_RUNTIME: NOT_INCLUDED
```

## Purpose

`SERVICE_1_OWNER_ANSWER_REENTRY_V1` closes the next basal boundary after `SERVICE_1_QUESTION_BUNDLE_AND_REF_V1`.

It validates that an owner answer targets an existing pending Servicio 1 question and creates a bound `OwnerAnswerRecord` with explicit metadata for future reentry.

It does not re-run the pipeline, recalculate evidence, unlock column confirmation, or authorize runtime delivery.

## Input

```text
question_bundle: Service1QuestionBundleV1 | dict
question_ref: stable question reference
raw_owner_answer: owner declaration
anamnesis_id: existing anamnesis record id
investigation_id: existing investigation record id
metadata: optional dict
```

## Output

```text
Service1OwnerAnswerReentryV1
```

Fields:

```text
schema_version
service_name
status
case_id
tenant_id
intake_id
source_run_id
question_ref
owner_answer_record
selected_question
blocked_reason
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
created_at
metadata
```

## Accepted path

```text
Service1QuestionBundleV1
+ pending question_ref
+ owner answer
-> OwnerAnswerRecord bound to question_ref
-> Service1OwnerAnswerReentryV1(status=ACCEPTED_FOR_REENTRY)
```

The created `OwnerAnswerRecord.metadata` includes:

```text
service_1_reentry_schema_version
case_id
source_run_id
question_source
question_target_ref
question_answer_type
question_text
owner_answer_validation_status=DECLARED_NOT_VALIDATED
reexecution_authorized=false
recalculation_authorized=false
```

## Blocked paths

```text
QUESTION_REF_NOT_FOUND
QUESTION_NOT_PENDING
QUESTION_BUNDLE_SCHEMA_UNSUPPORTED
```

Blocked packets do not create `OwnerAnswerRecord`.

## Non-goals

This slice explicitly does not:

- persist the record to JSONL
- load prior case state
- re-run `vertical_pipeline`
- recalculate structured evidence
- apply answers to `ColumnConfirmationMatrix`
- convert owner text into validated evidence
- generate the next question
- implement CLI, web, HTTP, chat, or LLM behavior
- authorize production/runtime use

## Implemented file

```text
PymIA-Live/pymia/smartpyme/service_1_owner_answer_reentry_v1.py
```

## Test file

```text
PymIA-Live/tests/smartpyme/test_service_1_owner_answer_reentry_v1.py
```

## Why this comes before runtime/chat

A chat or interactive runtime cannot safely accept owner answers unless it can prove the answer targets an existing pending question.

This slice makes that binding explicit while preserving the current safety line:

```text
owner answer = declared human input
owner answer != validated evidence
owner answer != recalculation authorization
```

## Next valid slice

```text
SERVICE_1_OWNER_ANSWER_REENTRY_PERSISTENCE_V1
```

Expected purpose:

```text
accept Service1OwnerAnswerReentryV1(status=ACCEPTED_FOR_REENTRY)
persist owner_answer_record via existing storage/pipeline_registration boundary
return persisted reference packet
still no recalculation
```
