# SERVICE_1_COLUMN_CONFIRMATION_REENTRY_AUDIT_V1

## Verdict

```text
STATUS: NEEDS_CONTRACT
SLICE_TYPE: DOCUMENTARY_AUDIT_ONLY
RUNTIME_AUTHORIZED: FALSE
HUMAN_REVIEW_REQUIRED: TRUE
REEXECUTION_AUTHORIZED: FALSE
RECALCULATION_AUTHORIZED: FALSE
WEB_OR_CHAT_RUNTIME: NOT_INCLUDED
```

## Purpose

`SERVICE_1_COLUMN_CONFIRMATION_REENTRY_AUDIT_V1` defines the semantic audit that must exist before any bridge is implemented between Servicio 1 reentry projection and column confirmation.

It exists to answer one methodological question:

```text
Can projected owner answers be mapped to column-confirmation targets
without promoting declared human input into validated evidence?
```

This document does not authorize runtime code, matrix mutation, recalculation, or evidence validation.

## Why this exists

The Servicio 1 reentry chain is already documented up to projection:

```text
SERVICE_1_QUESTION_BUNDLE_AND_REF_V1
-> SERVICE_1_OWNER_ANSWER_REENTRY_V1
-> SERVICE_1_OWNER_ANSWER_REENTRY_PERSISTENCE_V1
-> SERVICE_1_CASE_REENTRY_READ_MODEL_V1
-> SERVICE_1_REENTRY_PROJECTION_V1
```

The column confirmation chain is also already documented:

```text
SERVICE_1_COLUMN_CONFIRMATION_CLASSIFIER_V1
-> SERVICE_1_COLUMN_CONFIRMATION_APPLIER_V1
-> SERVICE_1_COLUMN_CONFIRMATION_CASE_PATCH_V1
```

`SERVICE_1_REENTRY_PROJECTION_V1` declares the next valid slice as:

```text
SERVICE_1_COLUMN_CONFIRMATION_REENTRY_AUDIT_V1
```

with the explicit reason:

```text
The next step would start mapping projected owner answers to column-confirmation targets.
That touches evidence semantics, so it should be audited before implementation.
```

## Certified facts

| Fact | Source |
|---|---|
| Reentry projection produces `Service1ProjectedQuestionV1` items with `question_ref`, `target_ref`, `answer_type`, `projection_status`, `latest_raw_owner_answer`, and `owner_answer_validation_status`. | `docs/producto/SERVICE_1_REENTRY_PROJECTION_V1.md` |
| Reentry projection preserves `runtime_authorized=false`, `human_review_required=true`, `reexecution_authorized=false`, `recalculation_authorized=false`. | `docs/producto/SERVICE_1_REENTRY_PROJECTION_V1.md` |
| Owner answer reentry creates bound owner-answer records with `owner_answer_validation_status=DECLARED_NOT_VALIDATED`. | `docs/producto/SERVICE_1_OWNER_ANSWER_REENTRY_V1.md` |
| Column confirmation classifier converts `raw_owner_answer + question_target_ref + suggested_semantic_role / proposed_role` into `OwnerColumnConfirmationAnswer` wrapped by `Service1ColumnConfirmationClassificationV1`. | `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_CLASSIFIER_V1.md` |
| Column confirmation classifier outcomes are `CONFIRMED_COMPUTATIONAL`, `CONFIRMED_INFORMATIONAL`, `OWNER_REJECTED_MAPPING`, `CONFIRMED_NOT_RELEVANT`, `INSUFFICIENT_ANSWER`. | `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_CLASSIFIER_V1.md` |
| The classifier also preserves `runtime_authorized=false`, `human_review_required=true`, `reexecution_authorized=false`, `recalculation_authorized=false`, and `owner_answer_validation_status=DECLARED_NOT_VALIDATED`. | `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_CLASSIFIER_V1.md` |
| No dedicated document, module contract, or task spec currently defines the bridge between reentry projection and column-confirmation targets. | Repository audit at creation time |

## Semantic boundary

Three concepts must remain separate:

### 1. Projected owner answers for reentry

These are owner declarations already bound to an existing `question_ref` and projected into a read-only state view.

They express:

```text
what the owner answered
```

not:

```text
that the answer is validated evidence
```

Authority in this layer:

```text
Service1QuestionBundleV1
+ Service1CaseReentryReadModelV1
+ Service1ReentryProjectionV1
```

### 2. Column-confirmation targets

These are explicit `file:sheet:column` targets that may require semantic confirmation, rejection, or correction before any computational use.

They express:

```text
what column interpretation is being proposed
```

not:

```text
that the owner's answer already resolved evidence semantics safely
```

Authority in this layer:

```text
ColumnConfirmationMatrix
+ OwnerColumnConfirmationAnswer
+ Service1ColumnConfirmationClassificationV1
```

### 3. Evidence meaning

This is the business meaning of a column or datum in operational context.

It expresses:

```text
what the data actually means for the case
```

not merely:

```text
what the owner declared in one reentry answer
```

Current certified safety line:

```text
owner answer = declared human input
owner answer != validated evidence
owner answer != recalculation authorization
```

## Boundary rule

A projected owner answer is not automatically a column confirmation.

Any future bridge would have to do all of the following explicitly:

1. determine whether `target_ref` in reentry projection can resolve to a column-confirmation target;
2. preserve the distinction between projected answer state and classified confirmation state;
3. keep `owner_answer_validation_status=DECLARED_NOT_VALIDATED` unless a separate capability authorizes evidence validation;
4. preserve all current safety flags as `false` for runtime, reexecution, and recalculation.

## Forbidden assumptions

The following assumptions are forbidden unless a future contract proves them safely:

```text
question_target_ref == column_confirmation_target_ref
projected ANSWERED == confirmed column meaning
raw owner text == validated evidence
projection completeness == recalculation authorization
reentry projection == permission to call apply_owner_answer()
```

## Drift risks

| Risk | Description | Severity |
|---|---|---|
| Premature 1:1 mapping | Assuming every projected question with a `target_ref` maps directly to one column-confirmation target. | HIGH |
| Classification bypass | Treating a reentry answer as already classified without using the explicit confirmation grammar. | HIGH |
| Evidence promotion | Turning declared owner text into validated evidence without a separate validation capability. | CRITICAL |
| Target ref conflation | Treating question-bundle target references and column-confirmation target references as identical without proof. | MEDIUM |
| Scope creep into applier | Allowing this audit to authorize `apply_owner_answer()` or matrix mutation. | HIGH |
| Safety flag erosion | Allowing any future mapping to imply `runtime_authorized=true` or `recalculation_authorized=true`. | CRITICAL |

## Decision

```text
NEEDS_CONTRACT
```

Reason:

```text
The bridge touches evidence semantics and currently has no dedicated CapabilitySpec,
ModuleContract, TaskSpec, or ADR governing the transition from declared owner input
into column-confirmation semantics.
```

## Required artifacts before any implementation

Before any mapping code can exist, the repository must decide whether it needs:

- a CapabilitySpec for the bridge behavior;
- a ModuleContract defining allowed inputs, forbidden assumptions, and output boundary;
- a TaskSpec for the first safe implementation slice;
- an ADR if evidence validation authority changes or if a new semantic promotion rule is introduced.

## Non-goals

This audit does not:

- implement a runtime bridge;
- create or modify Python modules;
- create tests;
- authorize `ColumnConfirmationMatrix.apply_owner_answer()`;
- validate owner text as evidence;
- unlock recalculation, reexecution, or delivery;
- modify frozen modules listed in `LIVE_CODE_FREEZE_LEDGER.md`.

## Acceptance / documentary checks

This audit is complete only if a reviewer can verify that:

- the semantic boundary between reentry projection and column confirmation is explicit;
- forbidden assumptions are listed and rejected;
- the safety line remains unchanged;
- no evidence-promotion path is authorized here;
- the outcome is documentary only;
- no runtime files or tests were touched to create this artifact.

## Stop conditions

Stop and do not implement a bridge if any of these remain unresolved:

- there is no explicit contract for the mapping boundary;
- the mapping would require promoting `DECLARED_NOT_VALIDATED` into validated evidence;
- the bridge would blur projection state with confirmation state;
- the bridge would require changing frozen module boundaries;
- the next step cannot be described without inventing behavior.

## Final verdict

```text
SERVICE_1_COLUMN_CONFIRMATION_REENTRY_AUDIT_V1
STATUS: NEEDS_CONTRACT
NEXT_VALID_STEP: decide whether to write CapabilitySpec + ModuleContract for the bridge,
or explicitly defer the mapping if evidence semantics remain unresolved.
```
