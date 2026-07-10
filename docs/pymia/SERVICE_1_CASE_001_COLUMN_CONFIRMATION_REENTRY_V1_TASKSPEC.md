# SERVICE_1_CASE_001_COLUMN_CONFIRMATION_REENTRY_V1_TASKSPEC

Status: TASKSPEC
Date: 2026-07-10
Scope: Implement and verify CASE_001 column-confirmation reentry adapter and confirmed-columns transformer.
Governing ADR: `docs/adr/SERVICE_1_CASE_001_COLUMN_CONFIRMATION_REENTRY_SCHEMA_ADR_V1.md`
Governing ModuleContract: `docs/pymia/SERVICE_1_CASE_001_COLUMN_CONFIRMATION_REENTRY_V1_MODULECONTRACT.md`

## Task verdict

This TaskSpec authorizes a narrow implementation slice only after acceptance tests are created.

Allowed slice:

```text
column_confirmation_packet.json
-> Service1QuestionBundleV1 adapter
-> owner answers/read-model validation
-> confirmed-columns candidate transformer
```

Not allowed:

```text
CASE_001 computation/dry-run
real runner
SaaS runtime
API/storage/worker
autonomous delivery
final diagnosis
second XLSX parser
```

## Files to add

Expected production module:

```text
PymIA-Live/pymia/smartpyme/service_1_case_001_column_confirmation_reentry_v1.py
```

Expected test module:

```text
tests/smartpyme/test_service_1_case_001_column_confirmation_reentry_v1.py
```

No existing production code should be changed unless tests prove a narrow integration import/export is required.

## Required public API

The production module must expose:

```python
build_case_001_column_confirmation_question_bundle_v1(...)
build_case_001_confirmed_columns_candidate_v1(...)
```

It may expose typed constants/dataclasses as needed, but must keep the behavior pure and deterministic.

## Task 1 — packet to question bundle adapter

### Input

- CASE_001 `column_confirmation_packet.json` as dict.
- `case_id`.
- `tenant_id`.
- `intake_id`.
- `run_id`.
- `source_file_ref`.
- optional metadata.

### Output

A valid `Service1QuestionBundleV1` with 12 `Service1QuestionV1` questions.

### Acceptance tests

1. Converts all 12 real CASE_001 packet questions.
2. Uses `source == column_confirmation_matrix` for every question.
3. Uses `answer_type == confirm_column_role` for every question.
4. Uses `target_ref == case_001:<sheet_name>:<column_name>`.
5. Generates stable `question_ref` using existing `build_stable_question_ref` behavior.
6. Preserves source `question_id` as `metadata.source_question_id`.
7. Preserves packet `answer_type=owner_text` only as `metadata.source_answer_type`.
8. Sets `runtime_authorized == False` and `owner_confirmation_required == True`.
9. Selects the first required pending question as `selected_next_question_ref`.
10. Rejects missing required packet fields.
11. Rejects duplicate generated question refs.
12. Rejects packet `runtime_authorized=True`.

## Task 2 — owner answers to confirmed-columns candidate

### Input

- `Service1QuestionBundleV1` from Task 1.
- `Service1CaseReentryReadModelV1` or equivalent read-model-compatible object with owner answers.
- `case_id`.
- `source_file_ref`.
- optional metadata.

### Output when incomplete

```text
status: NEEDS_OWNER_INPUT
confirmed_columns_candidate: None
missing_question_refs: non-empty if missing
ambiguous_question_refs: non-empty if ambiguous
runtime_authorized: false
reexecution_authorized: false
recalculation_authorized: false
```

### Output when complete

```text
status: CONFIRMED_COLUMNS_CANDIDATE_READY
confirmed_columns_candidate.schema_version: SERVICE_1_CASE_001_CONFIRMED_COLUMNS_V1
confirmed_columns_candidate.columns: 12 entries
runtime_authorized: false
reexecution_authorized: false
recalculation_authorized: false
```

### Acceptance tests

1. Missing all answers returns `NEEDS_OWNER_INPUT` with 12 missing refs.
2. One missing answer returns `NEEDS_OWNER_INPUT` with the exact missing ref.
3. Blank answer is invalid.
4. Circular answer equal to column name is invalid.
5. `unknown`, `n/a`, `no se`, `no sé`, or equivalent explicit unknown is invalid.
6. Answers to unknown question refs are ignored or reported without satisfying required refs.
7. Complete valid owner answers produce 12 confirmed column entries.
8. Each confirmed entry preserves `question_ref`, `source_question_id`, `sheet_name`, `column_name`, `owner_answer_raw`, and `confirmed_meaning`.
9. Candidate result never authorizes runtime/reexecution/recalculation.
10. Transformer does not write files, re-run CASE_001, compute, diagnose, or deliver.

## Task 3 — evidence fixture strategy

Use the real CASE_001 packet as read-only test input when available:

```text
C:\Users\PC\AppData\Local\Temp\opencode\case001_run\.tmp\service_1_cases\case_asset_a7e85d9a7ed2\column_confirmation_packet.json
```

If local temp artifact is unavailable in CI, tests must use an inline fixture copied from the same schema and explicitly marked as CASE_001 column-confirmation fixture.

Do not depend on the physical XLSX file for this unit slice.

## Stop conditions

Stop implementation if:

- adapter needs to change `Service1QuestionBundleV1` schema;
- transformer needs to change `Service1CaseReentryReadModelV1` schema;
- implementation needs runtime/reexecution/recalculation authorization;
- implementation needs API/storage/worker/SaaS runtime;
- tests require owner answers to be invented as real evidence rather than synthetic fixtures;
- code would run CASE_001 computation/dry-run;
- code would generate delivery or diagnosis.

## Validation command

Expected focal validation:

```text
python -m pytest tests/smartpyme/test_service_1_case_001_column_confirmation_reentry_v1.py -q
```

Optional broader validation after focal pass:

```text
python -m pytest tests/smartpyme/test_service_1_question_bundle_v1.py tests/smartpyme/test_service_1_case_reentry_read_model_v1.py tests/smartpyme/test_service_1_reentry_projection_v1.py tests/smartpyme/test_service_1_case_001_column_confirmation_reentry_v1.py -q
```

## Evidence to create after implementation

After tests pass, create:

```text
docs/current/SERVICE_1_CASE_001_COLUMN_CONFIRMATION_REENTRY_IMPLEMENTATION_EVIDENCE_V1.md
```

It must report:

- files changed;
- tests run by this agent;
- exact pass count;
- whether CASE_001 packet was converted to bundle;
- whether synthetic complete owner answers produced a confirmed-columns candidate;
- explicit non-authorization of runtime/dry-run/delivery/diagnosis.

## Presentation boundary after this task

If implementation and evidence pass, Servicio 1 may be presented as:

```text
CASE_001 has a governed path from physical XLSX intake to owner online column confirmation candidate and confirmed-columns handoff.
```

It still must not be presented as:

```text
final diagnosis complete
SaaS runtime complete
autonomous delivery complete
real runner complete
CASE_001 computation/dry-run complete
```
