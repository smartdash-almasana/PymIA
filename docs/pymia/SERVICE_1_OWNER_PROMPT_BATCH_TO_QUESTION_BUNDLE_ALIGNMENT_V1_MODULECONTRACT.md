# SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1 — ModuleContract

## Frontera

```text
QuestionBundle + OwnerPromptBatch -> aligned display records
```

## Permitido

```text
- recibir Service1QuestionBundleV1
- recibir Service1ColumnConfirmationOwnerPromptBatchV1
- usar preguntas source=column_confirmation_matrix
- usar answer_type=confirm_column_role
- construir target_ref desde file/sheet/column
- buscar question_ref existente por target_ref
- devolver prompts alineados con question_ref
- listar prompts no alineados
```

## Prohibido

```text
No crear preguntas nuevas. No crear question_ref nuevo. No modificar status.
No capturar respuestas. No clasificar respuestas. No aplicar respuestas.
No case_patch. No persistence. No recalculation. No runtime. No UI.
```

## Dependencias permitidas

```text
service_1_question_bundle_v1
service_1_column_confirmation_owner_prompt_batch_v1
```

## Invariantes

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
persistence_authorized=False
```

## Status

```text
ALIGNED
PARTIAL
EMPTY
BLOCKED
```

## Estado

```text
VIGENTE
```
