# SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_V1

## Estado

```text
IMPLEMENTED
```

## Regla canónica

```text
PymIA interpreta cada columna.
PymIA se lo explica al dueño en lenguaje natural.
El dueño responde: SÍ / NO / TU_RESPUESTA.
```

Este slice corrige la experiencia owner-facing de confirmación de columnas.

PymIA no debe preguntarle al dueño:

```text
¿Qué es esta columna?
```

Debe decirle:

```text
PymIA interpretó esta columna así. Confirmame si esta lectura es correcta.
```

## Objetivo

Crear un módulo puro que renderice prompts de confirmación semántica de columnas para el dueño.

Entrada mínima:

```text
file_name
sheet_name
column_name
suggested_semantic_role
owner_facing_role_explanation
```

Salida:

```text
Service1ColumnConfirmationOwnerPromptV1
```

con:

```text
prompt_text
allowed_owner_responses = ["SÍ", "NO", "TU_RESPUESTA"]
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
```

## Archivo runtime

```text
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_owner_prompt_v1.py
```

## Test

```text
PymIA-Live/tests/smartpyme/test_service_1_column_confirmation_owner_prompt_v1.py
```

## Función pública

```python
build_service_1_column_confirmation_owner_prompt_v1(...)
```

## Formato de prompt

Ejemplo:

```text
Dueño, revisé tu Excel y entendí esta columna así:

Archivo: "ventas_marzo.xlsx"
Hoja: "Ventas"
Columna: "Ventas"

Interpretación de PymIA:
Esta columna representa las ventas de este período.

Confirmame:
SÍ = correcto
NO = no es eso
TU_RESPUESTA = corregime qué significa
```

## Reglas de lenguaje

El texto al dueño debe:

```text
- decir que PymIA revisó e interpretó;
- explicar la interpretación en lenguaje PyME;
- pedir confirmación;
- mostrar explícitamente SÍ / NO / TU_RESPUESTA;
- evitar nombres internos.
```

## Términos internos prohibidos en el prompt

El prompt owner-facing no debe exponer términos como:

```text
venta_total
precio_venta
costo_unitario
costo_total
computed_variables
margen_bruto
margen_bruto_pct
```

Esos términos pueden existir dentro del objeto como `suggested_semantic_role`, pero no deben aparecer en el mensaje al dueño.

## Seguridad preservada

Este slice fija siempre:

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
```

## Exclusiones explícitas

Este slice no hace:

```text
NO classifier changes
NO applier
NO apply_owner_answer()
NO matrix mutation
NO persistencia
NO recalcular
NO vertical_pipeline
NO storage
NO landing/browser
NO LLM
NO web
```

## Tests cubiertos

```text
- renderiza prompt para Ventas en lenguaje natural
- renderiza prompt para Costo en lenguaje natural
- renderiza prompt para Cantidad en lenguaje natural
- incluye exactamente SÍ / NO / TU_RESPUESTA
- no expone semantic_role interno al dueño
- rechaza copy owner-facing que filtre términos internos
- mantiene flags de seguridad
- serializa allowed_owner_responses como lista
- es función pura sin storage
- valida campos mínimos requeridos
```

## Próximo frente

Después de este slice, el próximo ajuste lógico es:

```text
SERVICE_1_COLUMN_CONFIRMATION_NEGATION_SEMANTICS_V1
```

para alinear el classifier con el contrato owner-facing:

```text
SÍ → confirmación
NO → rechazo de interpretación / bloqueo semántico
TU_RESPUESTA → corrección semántica explícita
```

Recién después corresponde avanzar hacia:

```text
SERVICE_1_COLUMN_CONFIRMATION_APPLIER_V1
```
