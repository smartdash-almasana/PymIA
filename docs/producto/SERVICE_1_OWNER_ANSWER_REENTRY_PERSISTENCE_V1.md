# SERVICE_1_OWNER_ANSWER_REENTRY_PERSISTENCE_V1

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

`SERVICE_1_OWNER_ANSWER_REENTRY_PERSISTENCE_V1` persists an already accepted Servicio 1 owner-answer reentry packet.

It receives:

```text
Service1OwnerAnswerReentryV1(status=ACCEPTED_FOR_REENTRY)
```

and writes its embedded `OwnerAnswerRecord` to the existing JSONL storage boundary:

```text
<storage_dir>/<tenant_id>/owner_answers.jsonl
```

It does not recreate the owner answer record, because the previous slice already bound the answer to a validated pending `question_ref` and enriched the record metadata.

## Input

```text
reentry_packet: Service1OwnerAnswerReentryV1
storage_dir: Path-like
metadata: optional dict
```

## Output

```text
Service1OwnerAnswerReentryPersistenceV1
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
answer_id
persisted_path
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
Service1OwnerAnswerReentryV1(status=ACCEPTED_FOR_REENTRY)
+ OwnerAnswerRecord
+ storage_dir
-> save_owner_answer_record(...)
-> Service1OwnerAnswerReentryPersistenceV1(status=PERSISTED)
```

## Blocked paths

```text
REENTRY_NOT_ACCEPTED
OWNER_ANSWER_RECORD_MISSING
```

Blocked packets do not write to storage.

## Existing boundary used

```text
PymIA-Live/pymia/smartpyme/storage.py::save_owner_answer_record
```

This slice intentionally does not use `pipeline_registration.register_owner_answer_record`, because that function creates a new `OwnerAnswerRecord`. The reentry slice already created the correctly bound record, so persistence must save that record directly.

## Non-goals

This slice explicitly does not:

- load prior case state
- update evidence_request status
- mark pending question as answered
- re-run `vertical_pipeline`
- recalculate evidence
- apply column confirmation
- convert owner answer into validated evidence
- generate next question
- implement CLI, web, HTTP, chat, or LLM behavior
- authorize runtime/productive delivery

## Implemented file

```text
PymIA-Live/pymia/smartpyme/service_1_owner_answer_reentry_persistence_v1.py
```

## Test file

```text
PymIA-Live/tests/smartpyme/test_service_1_owner_answer_reentry_persistence_v1.py
```

## Why this comes before read model / runtime

A future case reentry read model needs real persisted owner answers before it can reconstruct case state.

This slice establishes that a bound answer can cross the memory/storage boundary without losing:

```text
case_id
source_run_id
question_ref
question_target_ref
question_text
owner_answer_validation_status
runtime/reexecution/recalculation safety flags
```

## Next valid slice

```text
SERVICE_1_CASE_REENTRY_READ_MODEL_V1
```

Expected purpose:

```text
read owner_answers.jsonl and related JSONL records
recover accepted owner answers for tenant_id + intake_id
expose a read model for future reentry projection
still no recalculation
```
