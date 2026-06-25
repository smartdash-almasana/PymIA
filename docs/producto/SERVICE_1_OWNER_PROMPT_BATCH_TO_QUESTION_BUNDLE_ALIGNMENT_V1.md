# SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1

## Estado

```text
IMPLEMENTED
```

## Objetivo

Alinear el batch de prompts owner-facing con el bundle canónico de preguntas de Servicio 1.

```text
Service1QuestionBundleV1
+ Service1ColumnConfirmationOwnerPromptBatchV1
→ aligned owner prompt display records
```

## Decisión de arquitectura

```text
QuestionBundle = autoridad de reentry
OwnerPromptBatch = autoridad de copy visible
Alignment = puente display gobernado
```

## Archivo runtime

```text
PymIA-Live/pymia/smartpyme/service_1_owner_prompt_batch_to_question_bundle_alignment_v1.py
```

## Test

```text
PymIA-Live/tests/smartpyme/test_service_1_owner_prompt_batch_to_question_bundle_alignment_v1.py
```

## Qué resuelve

Evita que el dueño vea un prompt humanizado sin `question_ref` gobernado.

El alineador produce records visibles con:

```text
question_ref
target_ref
answer_type
question_status
question_text
file_name
sheet_name
column_name
owner_label
owner_facing_role_explanation
prompt_text
allowed_owner_responses
metadata
```

## Regla de matching

El alineador construye el target:

```text
file:{file_name}:sheet:{sheet_name}:column:{column_name}
```

y busca una pregunta del bundle con:

```text
source=column_confirmation_matrix
answer_type=confirm_column_role
target_ref=<target esperado>
```

## Alignment status

```text
ALIGNED  — todos los prompts tienen question_ref
PARTIAL  — algunos prompts tienen question_ref y otros no
EMPTY    — no hay prompts visibles
BLOCKED  — hay prompts, pero ninguno tiene question_ref
```

## Qué no hace

```text
NO crea question_ref nuevo
NO modifica QuestionBundle
NO modifica OwnerPromptBatch
NO captura respuestas
NO clasifica respuestas
NO aplica respuestas
NO emite case_patch
NO persiste
NO recalcula
NO toca vertical_pipeline
NO toca UI/chatbot/landing
```

## Tests cubiertos

```text
- alineación feliz por target file/sheet/column
- question_ref viene del bundle
- prompt_text viene del batch
- question_text y prompt_text pueden diferir
- partial alignment reporta targets faltantes
- blocked si no hay preguntas coincidentes
- empty si el batch no tiene prompts
- metadata, flags y to_dict estables
- inputs inválidos rechazados
- módulo sin IO/ingestion/runtime
```

## Próximo frente permitido

```text
SERVICE_1_ALIGNED_OWNER_PROMPT_DISPLAY_PACKET_V1
```

Pregunta futura:

```text
¿Hace falta empaquetar estos records alineados en una salida operator/owner-facing lista para CLI/web sin abrir runtime conversacional?
```
