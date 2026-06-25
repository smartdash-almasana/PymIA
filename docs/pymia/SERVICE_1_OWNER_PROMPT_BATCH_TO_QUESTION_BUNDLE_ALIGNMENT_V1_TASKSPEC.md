# SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1 — TaskSpec

## Objetivo

Implementar un alineador puro entre:

```text
Service1QuestionBundleV1
+ Service1ColumnConfirmationOwnerPromptBatchV1
→ Service1OwnerPromptBatchToQuestionBundleAlignmentV1
```

## Regla central

```text
QuestionBundle aporta question_ref, target_ref, answer_type y status.
OwnerPromptBatch aporta prompt_text, owner_label y copy humanizado.
```

## Archivos del slice

```text
PymIA-Live/pymia/smartpyme/service_1_owner_prompt_batch_to_question_bundle_alignment_v1.py
PymIA-Live/tests/smartpyme/test_service_1_owner_prompt_batch_to_question_bundle_alignment_v1.py
docs/producto/SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1.md
docs/pymia/SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1_CAPABILITYSPEC.md
docs/pymia/SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1_MODULECONTRACT.md
```

## Scope permitido

```text
- validar Service1QuestionBundleV1
- validar Service1ColumnConfirmationOwnerPromptBatchV1
- construir target_ref file/sheet/column
- buscar question_ref existente en el bundle
- devolver aligned owner prompt display records
- listar prompts no alineados
```

## Prohibiciones

```text
NO crear question_ref nuevo
NO modificar QuestionBundle
NO modificar OwnerPromptBatch
NO capturar respuestas
NO clasificar respuestas
NO aplicar respuestas
NO emitir case_patch
NO persistir
NO recalcular
NO reejecutar
NO tocar vertical_pipeline
NO tocar UI/chatbot/landing
```

## Tests requeridos

```text
- alignment feliz por target_ref
- question_ref viene del bundle
- prompt_text viene del batch
- question_text y prompt_text pueden diferir
- partial alignment reporta targets faltantes
- blocked si ningún prompt alinea
- empty si no hay prompts
- metadata, flags y to_dict estables
- inputs inválidos rechazados
- módulo sin IO/ingestion/runtime
```

## Resultado validado

```text
Focal:
7 passed

Chain short:
29 passed
```

## Estado

```text
IMPLEMENTED
TESTED
PUSHED
```
