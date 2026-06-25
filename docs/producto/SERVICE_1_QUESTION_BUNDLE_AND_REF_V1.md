# SERVICE_1_QUESTION_BUNDLE_AND_REF_V1

## Verdict

```text
STATUS: IMPLEMENTED_CONTRACT
RUNTIME_AUTHORIZED: FALSE
HUMAN_REVIEW_REQUIRED: TRUE
WEB_OR_CHAT_RUNTIME: NOT_INCLUDED
```

## Purpose

`SERVICE_1_QUESTION_BUNDLE_AND_REF_V1` closes the first basal boundary needed before any real interactive chat for Servicio 1.

It does not create chat, web, API, background processing, diagnosis, accounting output, or runtime authorization.

It converts questions already emitted by existing PymIA components into stable, bindable records:

```text
owner question / next question / catalog question / column confirmation question
-> Service1QuestionV1
-> deterministic question_ref
-> Service1QuestionBundleV1
```

## Problem Closed

Before this slice, questions could exist as free text in reports, catalog reconciliation, or column confirmation entries. Owner answers could carry `question_ref`, but the reference could be arbitrary or manually supplied.

This slice provides a deterministic question reference layer so future owner answers can bind to a concrete computational target.

## Non-goals

This slice explicitly does not:

- run a chat loop
- call an LLM
- parse natural language answers
- apply owner answers to evidence
- recalculate formulas
- unlock column confirmation
- persist bundle records in storage
- modify `vertical_pipeline.py`
- modify `storage.py`
- modify web or landing files
- authorize production/runtime delivery

## Implemented file

```text
PymIA-Live/pymia/smartpyme/service_1_question_bundle_v1.py
```

## Test file

```text
PymIA-Live/tests/smartpyme/test_service_1_question_bundle_v1.py
```

## Core objects

### Service1QuestionV1

```text
question_ref
source
text
target_ref
answer_type
required
status
metadata
```

### Service1QuestionBundleV1

```text
schema_version
service_name
case_id
tenant_id
intake_id
run_id
questions
selected_next_question_ref
runtime_authorized
human_review_required
created_at
metadata
```

## Supported question sources

```text
report.owner_question
report.next_questions
structured_summary.catalog_reconciliation[].next_audit_questions
column_confirmation_matrix.entries[].owner_question
```

## Stable question reference rule

The reference prefers computational target over wording:

```text
service_1:{source}:{normalized_target_ref}
```

When no target exists, it falls back to a stable hash of the question text:

```text
service_1:{source}:text_{sha256_12}
```

This prevents frontends, CLIs, or operators from inventing arbitrary `question_ref` values.

## Safety flags

Every bundle is emitted with:

```text
runtime_authorized: false
human_review_required: true
```

This preserves the current Servicio 1 constraint: questions may become bindable, but the system is still not an autonomous runtime.

## Why this comes before chat

A chat interface needs to know what exact question an owner is answering. Without a stable `question_ref`, the next turn cannot be governed. It becomes text exchange, not Servicio 1.

This slice enables the next boundary:

```text
SERVICE_1_OWNER_ANSWER_REENTRY_V1
```

but does not implement it.

## Next valid slice

```text
SERVICE_1_OWNER_ANSWER_REENTRY_V1
```

Expected purpose:

```text
load or receive Service1QuestionBundleV1
accept owner_answer + question_ref
validate that question_ref exists and is PENDING
create/bind OwnerAnswerRecord metadata to the selected question
prepare reentry without claiming recalculation
```
