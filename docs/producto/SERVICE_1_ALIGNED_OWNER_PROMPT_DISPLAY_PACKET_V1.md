# SERVICE_1_ALIGNED_OWNER_PROMPT_DISPLAY_PACKET_V1

## Estado

```text
IMPLEMENTED
```

## Objetivo

Convertir prompts alineados en un paquete visible mínimo para operador/dueño.

```text
Service1OwnerPromptBatchToQuestionBundleAlignmentV1
→ Service1AlignedOwnerPromptDisplayPacketV1
```

## Decisión

Este slice convierte la cadena interna en una salida operable:

```text
question_ref + prompt_text humanizado + respuestas permitidas
```

## Archivo runtime

```text
PymIA-Live/pymia/smartpyme/service_1_aligned_owner_prompt_display_packet_v1.py
```

## Test

```text
PymIA-Live/tests/smartpyme/test_service_1_aligned_owner_prompt_display_packet_v1.py
```

## Output principal

```text
Service1AlignedOwnerPromptDisplayPacketV1
```

Campos clave:

```text
case_id
tenant_id
intake_id
run_id
file_name
display_status
total_items
items
blocked_reason
unaligned_prompt_targets
```

Cada item visible contiene:

```text
display_index
question_ref
target_ref
answer_type
question_status
file_name
sheet_name
column_name
owner_label
display_title
prompt_text
allowed_owner_responses
operator_note
```

## Status

```text
READY   — hay items visibles con question_ref
EMPTY   — no hay prompts para mostrar
BLOCKED — hay prompts, pero ninguno tiene question_ref
```

## Qué no hace

```text
NO crea question_ref
NO captura respuestas
NO clasifica respuestas
NO aplica respuestas
NO persiste
NO recalcula
NO reejecuta
NO toca vertical_pipeline
NO toca UI/chatbot/landing
```

## Prueba funcional cubierta

```text
ColumnConfirmationMatrix
→ QuestionBundle
→ OwnerPromptBatch
→ Alignment
→ DisplayPacket
```

## Resultado esperado

El operador puede mostrar al dueño una pregunta con:

```text
question_ref
target_ref
prompt_text
respuestas permitidas: SÍ / NO / TU_RESPUESTA
```

sin autorizar runtime, recalculation ni persistence automática.
