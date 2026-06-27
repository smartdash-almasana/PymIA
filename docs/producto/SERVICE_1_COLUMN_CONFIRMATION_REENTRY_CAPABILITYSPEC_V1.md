# SERVICE_1_COLUMN_CONFIRMATION_REENTRY_CAPABILITYSPEC_V1

## VERDICT

```text
AUTHORIZED_FOR_MINIMAL_CONTRACT_ONLY
```

## CAPABILITY

PymIA may represent a Servicio 1 reentry answer as a **column-confirmation reentry candidate** only when the answer already belongs to the column-confirmation question family and all current safety flags remain preserved.

The authorized capability is:

```text
Service1ProjectedQuestionV1
+ explicit proposed_role / suggested_semantic_role
-> Service1ColumnConfirmationReentryCandidateV1
```

This capability authorizes **candidate construction only**.

It does not authorize:

```text
classification
matrix application
case patch emission
persistence
reexecution
recalculation
evidence validation
```

## WHAT_IT_CAN_DO

This capability may:

- verify that a projected question really belongs to the column-confirmation family;
- require the projected question to be already `ANSWERED`;
- require an explicit role proposal from an existing column-confirmation source;
- preserve `question_ref`, `target_ref`, `raw_owner_answer`, `answer_type`, and `owner_answer_validation_status`;
- expose a deterministic blocked status when the projected question is not eligible;
- preserve:

```text
runtime_authorized=false
human_review_required=true
reexecution_authorized=false
recalculation_authorized=false
```

## WHAT_IT_CANNOT_DO

This capability does not authorize:

- inferring a semantic role from free text;
- assuming every reentry answer belongs to column confirmation;
- assuming `ANSWERED` means semantically confirmed;
- treating raw owner text as validated evidence;
- calling `classify_owner_column_confirmation_answer(...)`;
- calling `apply_service_1_column_confirmation_v1(...)`;
- emitting a case patch;
- mutating `ColumnConfirmationMatrix`;
- touching `vertical_pipeline.py`, `storage.py`, or any frozen module;
- adding CLI, web, chat, API, or LLM runtime.

## INPUTS_REQUIRED

- `projected_question: Service1ProjectedQuestionV1`
- `proposed_role: str | None`
- `suggested_semantic_role: str | None`
- `metadata: dict | None`

### Input gate

The projected question is eligible only if all of these hold:

```text
source == column_confirmation_matrix
answer_type == confirm_column_role
projection_status == ANSWERED
latest_raw_owner_answer is present
target_ref is present and parseable as file:sheet:column
at least one of proposed_role / suggested_semantic_role is present
owner_answer_validation_status remains DECLARED_NOT_VALIDATED
```

## OUTPUTS_REQUIRED

A minimal contract able to represent:

- `schema_version`
- `service_name`
- `status`
- `blocked_reason`
- `question_ref`
- `question_source`
- `target_ref`
- `answer_type`
- `raw_owner_answer`
- `proposed_role`
- `owner_answer_validation_status`
- `runtime_authorized`
- `human_review_required`
- `reexecution_authorized`
- `recalculation_authorized`
- `metadata`

The output is a **candidate packet**, not a classified answer and not a patch.

## FAILURE_STATES

The capability must admit at least these blocked states:

- `QUESTION_SOURCE_UNSUPPORTED`
- `ANSWER_TYPE_UNSUPPORTED`
- `QUESTION_NOT_ANSWERED`
- `RAW_OWNER_ANSWER_MISSING`
- `TARGET_REF_INVALID`
- `ROLE_MISSING`
- `OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED`

## CANONICAL_AUTHORITY

```text
SERVICE_1_COLUMN_CONFIRMATION_REENTRY_AUDIT_V1
```

This CapabilitySpec exists because the audit concluded:

```text
NEEDS_CONTRACT
```

before any implementation.

## STATUS

```text
SERVICE_1_COLUMN_CONFIRMATION_REENTRY = AUTHORIZED_FOR_MINIMAL_CONTRACT_ONLY
```

This document authorizes the minimal capability boundary.

It does not certify runtime implementation.
