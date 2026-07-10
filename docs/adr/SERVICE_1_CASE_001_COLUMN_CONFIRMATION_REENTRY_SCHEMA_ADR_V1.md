# SERVICE_1_CASE_001_COLUMN_CONFIRMATION_REENTRY_SCHEMA_ADR_V1

Status: ACCEPTED
Date: 2026-07-10
Scope: CASE_001 column-confirmation packet, online owner reentry, and confirmed-columns handoff.

## Decision

CASE_001 column confirmation requires a formal schema boundary before implementation.

The current `column_confirmation_packet.json` is a certified owner-question source, but it must not be treated as a `Service1QuestionBundleV1` as-is. Servicio 1 will use two explicit modules in a later ModuleContract:

```text
column_confirmation_packet.json
-> packet-to-question-bundle adapter
-> Service1QuestionBundleV1 / owner online reentry
-> owner answers
-> answers-to-confirmed-columns transformer/validator
-> confirmed-columns.json
-> CASE_001 re-run candidate
```

This ADR authorizes the schema decision only. It does not authorize code, runtime execution, dry-run, runner, SaaS runtime, API/storage/worker, autonomous delivery, or final diagnosis.

## Context

CASE_001 is currently:

```text
XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT: PASS_WITH_LIMITS
CASE_001_FINAL_STATE: NEEDS_OWNER_INPUT
```

The physical XLSX run produced `column_confirmation_packet.json` with 12 required owner questions. A separate owner-facing confirmation packet was committed at `51e57b5`, and a candidate online reentry mapping was committed at `74f28ba`.

The technical audit found:

- owner reentry primitives exist and are runtime-free;
- `column_confirmation_packet.json` does not directly satisfy `Service1QuestionBundleV1`;
- the packet lacks full case/session identity required by the bundle;
- the packet uses `answer_type: owner_text`, while the bundle allows `confirm_column_role`;
- there is no certified transformer from online owner answers to `confirmed-columns.json`;
- `--confirmed-columns` exists as a CLI input for later re-run, but only as a loader/consumer boundary.

Therefore the correct state is `NEEDS_MODULECONTRACT`, with this ADR as the prior architecture decision.

## Decisions

### 1. Packet is not a bundle

`column_confirmation_packet.json` remains a source artifact, not the online reentry bundle itself.

Required later module:

```text
SERVICE_1_CASE_001_COLUMN_CONFIRMATION_PACKET_TO_QUESTION_BUNDLE_ADAPTER_V1
```

It must convert source packet questions into `Service1QuestionV1` items without mutating the source packet.

### 2. Online source and answer type

The adapter must use existing bundle vocabulary:

```text
source: column_confirmation_matrix
answer_type: confirm_column_role
runtime_authorized: false
owner_confirmation_required: true
```

It must not use packet `answer_type: owner_text` as the bundle answer type. `owner_text` may be preserved only as source metadata.

### 3. target_ref convention

For CASE_001 online reentry, the canonical target reference is:

```text
case_001:<sheet_name>:<column_name>
```

The resulting `question_ref` must be generated through the existing stable question-ref convention:

```text
service_1:<source_slug>:<target_ref_slug>
```

Example:

```text
target_ref: case_001:Ventas_Junio_2026:fecha
question_ref: service_1:column_confirmation_matrix:case_001_ventas_junio_2026_fecha
```

Rationale: this makes the CASE_001 owner confirmation boundary explicit and avoids binding the owner-facing semantic question to an incidental local filename. If a future generic extractor uses `file:<name>:sheet:<sheet>:column:<column>`, a later generalized ADR/ModuleContract may define that broader convention. This ADR governs CASE_001 only.

### 4. question_id preservation

Source `question_id` values such as `col_confirm_001` must be preserved in metadata, not used as `question_ref`.

Required metadata fields:

```text
source_question_id
source_packet_type
source_packet_status
source_answer_type
sheet_name
column_name
case_id
source_file_ref, when available
```

Rationale: `question_id` is source-local and order-like; `question_ref` is the stable online answer-binding key.

### 5. Owner answers are not confirmed columns

Online owner answers are raw evidence until validated. They must not be treated directly as `confirmed-columns.json`.

Required later module:

```text
SERVICE_1_CASE_001_OWNER_ANSWERS_TO_CONFIRMED_COLUMNS_TRANSFORMER_V1
```

It must validate completeness, ambiguity, and answer binding before emitting a controlled `confirmed-columns.json` candidate.

### 6. Authorization flags remain closed

All intermediate reentry/read-model/projection artifacts remain fail-closed:

```text
runtime_authorized: false
reexecution_authorized: false
recalculation_authorized: false
```

A later CASE_001 re-run with `--confirmed-columns` is not authorized by this ADR. It requires ModuleContract, TaskSpec, tests, and evidence.

## Consequences

### Allowed now

- Create a ModuleContract for the adapter and transformer boundaries.
- Define acceptance tests for packet-to-bundle conversion and answers-to-confirmed-columns validation.
- Keep using the owner-facing packet as documentation for the PyME owner.

### Not allowed yet

- Implement adapter or transformer code without ModuleContract + TaskSpec.
- Generate `confirmed-columns.json` without validated owner answers.
- Re-run CASE_001 as computation/dry-run.
- Claim online owner reentry for CASE_001 is certified.
- Use operator-invented answers.
- Promote runner, SaaS runtime, API/storage/worker, autonomous delivery, or final diagnosis.

## ModuleContract requirements

The next ModuleContract must define at least two boundaries:

| Module | Input | Output | Must preserve | Must not do |
|---|---|---|---|---|
| packet-to-question-bundle adapter | `column_confirmation_packet.json` + case/session refs | `Service1QuestionBundleV1` | source `question_id` in metadata; sheet/column/question text; fail-closed flags | no owner answer invention; no runtime; no confirmed-columns output |
| answers-to-confirmed-columns transformer | `Service1CaseReentryReadModelV1` / owner answers + bundle | controlled `confirmed-columns.json` candidate | answer binding, validation status, source question metadata | no computation; no re-run; no diagnosis; no delivery |

## Acceptance criteria for later TaskSpec

A later TaskSpec must prove:

1. All 12 packet questions become `Service1QuestionV1` entries.
2. `source == column_confirmation_matrix` for all entries.
3. `answer_type == confirm_column_role` for all entries.
4. `target_ref == case_001:<sheet_name>:<column_name>` for all entries.
5. `question_id` is preserved in metadata as `source_question_id`.
6. Runtime, reexecution, and recalculation flags remain false.
7. Incomplete or ambiguous owner answers do not emit `confirmed-columns.json`.
8. Complete validated owner answers can emit a controlled `confirmed-columns.json` candidate.
9. No computation/dry-run/delivery happens inside either module.

## Related documents

- `docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md`
- `docs/current/SERVICE_1_CASE_001_PHYSICAL_XLSX_E2E_EVIDENCE_V1.md`
- `docs/current/SERVICE_1_CASE_001_OWNER_COLUMN_CONFIRMATION_PACKET_V1.md`
- `docs/current/SERVICE_1_CASE_001_ONLINE_OWNER_COLUMN_REENTRY_MAPPING_V1.md`
- `PymIA-Live/pymia/smartpyme/service_1_question_bundle_v1.py`
- `PymIA-Live/pymia/smartpyme/service_1_case_reentry_read_model_v1.py`
- `PymIA-Live/pymia/smartpyme/service_1_reentry_projection_v1.py`
- `PymIA-Live/pymia/cli/service_1_operator.py`

## Next step

Create:

```text
docs/pymia/SERVICE_1_CASE_001_COLUMN_CONFIRMATION_REENTRY_V1_MODULECONTRACT.md
```

Do not write implementation code before that ModuleContract and a following TaskSpec exist.
