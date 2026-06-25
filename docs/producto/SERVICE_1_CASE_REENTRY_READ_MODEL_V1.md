# SERVICE_1_CASE_REENTRY_READ_MODEL_V1

## Verdict

```text
STATUS: IMPLEMENTED_READ_MODEL
RUNTIME_AUTHORIZED: FALSE
HUMAN_REVIEW_REQUIRED: TRUE
REEXECUTION_AUTHORIZED: FALSE
RECALCULATION_AUTHORIZED: FALSE
WEB_OR_CHAT_RUNTIME: NOT_INCLUDED
```

## Purpose

`SERVICE_1_CASE_REENTRY_READ_MODEL_V1` is the first read boundary for Servicio 1 reentry.

It reads persisted `OwnerAnswerRecord` entries from:

```text
<storage_dir>/<tenant_id>/owner_answers.jsonl
```

and exposes only the answers that were created by the Servicio 1 reentry path.

This turns append-only storage into a consultable case view without mutating storage or executing the pipeline.

## Input

```text
storage_dir
tenant_id
intake_id
metadata: optional dict
```

## Output

```text
Service1CaseReentryReadModelV1
```

Fields:

```text
schema_version
service_name
status
tenant_id
intake_id
case_id
answers_count
answered_question_refs
latest_answer
answers
storage_path
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
metadata
```

Each answer is exposed as:

```text
Service1ReentryAnswerViewV1
```

with:

```text
answer_id
tenant_id
intake_id
anamnesis_id
investigation_id
question_ref
raw_owner_answer
answer_kind
created_at
case_id
source_run_id
question_source
question_target_ref
question_answer_type
question_text
owner_answer_validation_status
metadata
```

## Statuses

```text
READY
EMPTY
STORAGE_MISSING
```

## Service 1 reentry filter

The read model only includes owner answers whose metadata contains:

```text
service_1_reentry_schema_version
```

Plain `OwnerAnswerRecord` entries created by other flows are ignored.

## Safety line

This slice preserves:

```text
runtime_authorized=false
human_review_required=true
reexecution_authorized=false
recalculation_authorized=false
```

Owner answers remain declared human input, not validated evidence.

## Existing boundaries used

This slice reads the storage format written by:

```text
PymIA-Live/pymia/smartpyme/storage.py::save_owner_answer_record
```

It is compatible with the persistence packet from:

```text
SERVICE_1_OWNER_ANSWER_REENTRY_PERSISTENCE_V1
```

## Non-goals

This slice explicitly does not:

- write to storage
- update question status
- update evidence request status
- load full case replay
- re-run `vertical_pipeline`
- recalculate evidence
- apply column confirmation
- decide next question
- implement CLI, web, HTTP, chat, or LLM behavior
- authorize runtime/productive delivery

## Implemented file

```text
PymIA-Live/pymia/smartpyme/service_1_case_reentry_read_model_v1.py
```

## Test file

```text
PymIA-Live/tests/smartpyme/test_service_1_case_reentry_read_model_v1.py
```

## Why this comes before projection

A future projection layer needs a reliable read model before it can mark questions as answered or identify pending questions.

The safe order remains:

```text
question bundle
-> owner answer reentry
-> owner answer persistence
-> case reentry read model
-> reentry projection
```

## Next valid slice

```text
SERVICE_1_REENTRY_PROJECTION_V1
```

Expected purpose:

```text
question_bundle + Service1CaseReentryReadModelV1
-> answered/pending projection
-> next pending question ref
-> no recalculation
```
