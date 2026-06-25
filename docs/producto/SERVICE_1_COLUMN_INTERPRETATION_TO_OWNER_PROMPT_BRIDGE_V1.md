# SERVICE_1_COLUMN_INTERPRETATION_TO_OWNER_PROMPT_BRIDGE_V1

## Estado

```text
IMPLEMENTED
```

## Objetivo

Conectar tres piezas reales ya existentes:

```text
ColumnConfirmationEntry
+ owner-facing role explanation catalog
+ owner prompt builder
→ owner-facing prompt completo para una columna interpretada
```

Este slice es un bridge puro. No interpreta Excel, no clasifica respuestas, no aplica respuestas y no persiste.

## Archivo runtime

```text
PymIA-Live/pymia/smartpyme/service_1_column_interpretation_to_owner_prompt_bridge_v1.py
```

## Test

```text
PymIA-Live/tests/smartpyme/test_service_1_column_interpretation_to_owner_prompt_bridge_v1.py
```

## Input contract

```text
file_name: str
entry: ColumnConfirmationEntry
metadata: dict | None
```

## Output contract

```text
Service1ColumnInterpretationToOwnerPromptBridgeV1
```

Campos principales:

```text
schema_version
service_name
file_name
sheet_name
column_name
suggested_semantic_role
owner_label
owner_facing_role_explanation
known_role
calculation_relevance
owner_prompt
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
persistence_authorized
created_at
metadata
```

## Flujo interno

```text
1. Toma entry.suggested_semantic_role.
2. Llama explain_owner_facing_semantic_role_v1(...).
3. Usa owner_facing_role_explanation del catálogo.
4. Llama build_service_1_column_confirmation_owner_prompt_v1(...).
5. Devuelve wrapper frozen con explicación y prompt.
```

## Seguridad fija

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
persistence_authorized=False
```

## Exclusiones

```text
NO leer Excel
NO construir ColumnConfirmationMatrix
NO inventar semantic roles
NO modificar ColumnSemanticClassifier
NO clasificar respuesta del dueño
NO aplicar respuesta
NO emitir case patch
NO persistir
NO recalcular
NO reejecutar
NO vertical_pipeline
NO landing/browser
```

## Tests cubiertos

```text
- bridge venta_total → owner prompt
- bridge producto/informational role
- bridge unknown role con fallback seguro
- metadata passthrough
- flags de seguridad
- prompt contiene archivo/hoja/columna
- prompt no filtra semantic_role interno
- to_dict serializa wrapper y prompt
- pureza filesystem
- owner_question del entry no reemplaza el prompt nuevo
- validación de file_name
- validación de tipo entry
```

## Próximo frente permitido

```text
SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1
```

Objetivo futuro:

```text
ColumnConfirmationMatrix.entries
→ lista de prompts owner-facing
```

Todavía sin persistence, sin recalculation y sin vertical_pipeline.
