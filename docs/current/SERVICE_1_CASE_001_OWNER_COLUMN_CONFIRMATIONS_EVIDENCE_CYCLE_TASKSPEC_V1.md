# Service 1 CASE_001 Owner Column Confirmations Evidence Cycle TaskSpec V1

Status: TASKSPEC_READY
Date: 2026-07-10
Scope: CASE_001 owner column-confirmation evidence cycle before any dry-run, calculation, diagnosis, or delivery.

## Verdict

```text
CASE_001_OWNER_COLUMN_CONFIRMATIONS: NEXT_REQUIRED_EVIDENCE
RUNTIME_AUTHORIZED: false
REEXECUTION_AUTHORIZED: false
RECALCULATION_AUTHORIZED: false
DELIVERY_AUTHORIZED: false
```

This TaskSpec defines the next single methodological cycle for Servicio 1: collect and validate the owner confirmations for the 12 CASE_001 column-confirmation questions.

It does not authorize runtime, runner, SaaS, API worker, storage worker, dry-run, calculation, final diagnosis, or delivery.

## Governing evidence

Current governing documents:

```text
docs/current/SERVICE_1_CASE_001_PHYSICAL_XLSX_E2E_EVIDENCE_ANCHOR_V1.md
docs/current/SERVICE_1_COLUMN_CONFIRMATION_REENTRY_CHECKPOINT_V1.md
docs/current/SERVICE_1_SAFE_PRESENTATION_GUIDE_V1.md
docs/current/SERVICE_1_WEB_COLUMN_CONFIRMATION_STATE_V1.md
docs/producto/SERVICE_1_COLUMN_CONFIRMATION_REENTRY_TASKSPEC_V1.md
docs/producto/SERVICE_1_COLUMN_CONFIRMATION_REENTRY_MODULE_CONTRACT_V1.md
```

Current certified state:

```text
CASE_001_PHYSICAL_XLSX: PASS_WITH_LIMITS
CASE_001_FINAL_STATE: NEEDS_OWNER_INPUT
COLUMN_CONFIRMATION_REENTRY: CANDIDATE_ONLY / FAIL_CLOSED
```

## Required input

The cycle requires real owner-provided answers for the 12 CASE_001 column-confirmation questions previously evidenced by the CASE_001 packet.

Each owner answer must be bound to a known question reference or equivalent governed question identity from the column-confirmation packet.

Synthetic answers may be used only as test fixtures. Synthetic answers are not owner evidence and must not be used to promote CASE_001.

## Required validation

Before any downstream decision, the validation must prove all of the following:

```text
12 known CASE_001 column-confirmation questions are answered
0 required answers are missing
0 answers are blank
0 answers are ambiguous
0 question refs are unknown
0 duplicate answers change the same question without explicit resolution
runtime_authorized = false
reexecution_authorized = false
recalculation_authorized = false
delivery_authorized = false
```

Ambiguous answers include, at minimum:

```text
unknown
no sé
no se
n/a
na
no aplica
empty text
repeating only the column name without operational meaning
```

## Expected artifact

The expected output of this cycle is a documentary evidence packet, not a runtime execution:

```text
docs/current/SERVICE_1_CASE_001_OWNER_COLUMN_CONFIRMATIONS_EVIDENCE_V1.md
```

That packet must include:

| Section | Requirement |
|---|---|
| Source | Where the 12 owner answers came from. |
| Answer table | question id/ref, sheet, column, owner answer, validation status. |
| Validation summary | missing, ambiguous, unknown, duplicate, accepted counts. |
| Safety flags | runtime/reexecution/recalculation/delivery all false. |
| Decision | Whether confirmed-columns candidate may be built. |
| Limits | No dry-run, calculation, diagnosis, or delivery yet. |

## Allowed technical verification

Allowed verification is limited to pure validation and existing candidate-only helpers.

Allowed:

```text
read existing CASE_001 question/answer packet if present
validate answer completeness
validate ambiguity/unknown refs
build candidate-only confirmed-columns artifact if an existing contract already authorizes it
run focal tests for existing candidate-only modules
```

Forbidden:

```text
runner
SaaS runtime
API worker
storage worker
dry-run
calculation
recalculation
final diagnosis
delivery
autonomous delivery
LLM decision authority
inventing owner answers
```

## Stop conditions

Stop the cycle and keep CASE_001 at `NEEDS_OWNER_INPUT` if any condition holds:

```text
fewer than 12 known answers
any required answer missing
any ambiguous answer
any unknown question ref
answers are synthetic but treated as real owner evidence
validation would require semantic inference by the LLM
validation would unlock runtime automatically
```

## Safe owner-facing wording

Use this wording with the owner:

```text
Necesitamos confirmar qué significa cada columna de tu Excel antes de calcular o diagnosticar. Tus respuestas no disparan una ejecución automática: sólo nos permiten validar si PymIA entiende correctamente la estructura del archivo.
```

## Next step after PASS

If, and only if, the evidence packet proves 12 valid owner confirmations, the next methodological step is a separate governed decision:

```text
confirmed-columns candidate -> dry-run authorization decision
```

That next step requires its own evidence and must not be implied by this TaskSpec.