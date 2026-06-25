# SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1 — CapabilitySpec

## 1. Capacidad

Autoriza una capacidad mínima de alineación entre:

```text
Service1QuestionBundleV1
+ Service1ColumnConfirmationOwnerPromptBatchV1
→ aligned owner prompt display records
```

## 2. Problema

`Service1QuestionBundleV1` gobierna `question_ref`, `target_ref`, estado y reentrada.

`OwnerPromptBatchV1` gobierna la copia owner-facing humanizada.

Sin alineación, el dueño puede ver un prompt humanizado que no contiene el `question_ref` requerido para reentrada.

## 3. Inputs autorizados

```text
Service1QuestionBundleV1
Service1ColumnConfirmationOwnerPromptBatchV1
metadata: dict | None
```

## 4. Output autorizado

```text
Service1OwnerPromptBatchToQuestionBundleAlignmentV1
```

El output debe combinar:

```text
question_ref
target_ref
answer_type
file_name
sheet_name
column_name
owner_label
prompt_text
allowed_owner_responses
```

## 5. Qué puede hacer

```text
- validar inputs
- construir target_ref esperado desde file/sheet/column
- buscar pregunta canónica en Service1QuestionBundleV1
- copiar question_ref y answer_type del bundle
- copiar prompt_text y owner copy del batch
- reportar prompts no alineados
- devolver artefacto puro y serializable
```

## 6. Qué no puede hacer

```text
NO modificar QuestionBundle
NO modificar OwnerPromptBatch
NO crear question_ref nuevo
NO clasificar respuestas
NO aplicar respuestas
NO emitir case_patch
NO persistir
NO recalcular
NO reejecutar
NO usar LLM
NO tocar vertical_pipeline
NO tocar UI/chatbot/landing
```

## 7. Autoridad

```text
QuestionBundle = autoridad de reentry
OwnerPromptBatch = autoridad de copy visible
Alignment = puente display gobernado
```

## 8. Estado

```text
VIGENTE
```
