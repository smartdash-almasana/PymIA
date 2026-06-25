# SERVICE_1_COLUMN_CONFIRMATION_CLASSIFIER_V1

## Estado

```text
IMPLEMENTED
```

## Objetivo

Este slice agrega el puente mínimo entre la respuesta textual del dueño y el contrato existente de confirmación de columnas.

Convierte:

```text
raw_owner_answer
+ question_target_ref
+ suggested_semantic_role / proposed_role
```

en:

```text
OwnerColumnConfirmationAnswer
```

sin aplicar todavía la respuesta sobre `ColumnConfirmationMatrix`.

## Contexto de cadena

La cadena basal existente ya cerraba:

```text
preguntas generadas por PymIA
→ question_ref estable
→ respuesta del dueño vinculada
→ persistencia en owner_answers.jsonl
→ lectura del caso
→ proyección de preguntas respondidas / pendientes
```

El gap era que la respuesta persistida quedaba como texto libre y no podía alimentar de forma segura:

```text
ColumnConfirmationMatrix.apply_owner_answer()
```

porque ese método exige un `OwnerColumnConfirmationAnswer` ya clasificado.

## Archivo runtime agregado

```text
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_classifier_v1.py
```

## Test agregado

```text
PymIA-Live/tests/smartpyme/test_service_1_column_confirmation_classifier_v1.py
```

## Funciones públicas

```python
parse_column_target_ref(target_ref: str) -> ColumnConfirmationTargetRefV1
```

Parsea referencias de la forma:

```text
file:{file_name}:sheet:{sheet_name}:column:{column_name}
```

y devuelve:

```text
file_name
sheet_name
column_name
```

```python
classify_owner_column_confirmation_answer(...) -> Service1ColumnConfirmationClassificationV1
```

Clasifica la respuesta del dueño y construye internamente un:

```text
OwnerColumnConfirmationAnswer
```

## Contratos existentes usados

```python
OwnerColumnConfirmationAnswer
OwnerColumnConfirmationOutcome
```

provenientes de:

```text
pymia.contracts.column_confirmation_v1
```

## Resultado wrapper

El contrato `OwnerColumnConfirmationAnswer` no contiene flags de seguridad de Servicio 1.

Por eso el clasificador devuelve un wrapper explícito:

```text
Service1ColumnConfirmationClassificationV1
```

que contiene:

```text
owner_column_confirmation_answer
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
owner_answer_validation_status
```

## Clasificación conservadora

### Regla owner-facing canónica

Este clasificador debe alinearse con la interfaz owner-facing:

```text
SÍ = correcto
NO = no es eso
TU_RESPUESTA = corregime qué significa
```

PymIA interpreta primero. El dueño no descubre la columna desde cero: confirma, rechaza o corrige la interpretación de PymIA.

### SÍ / confirmación explícita

Ejemplos:

```text
Sí
Correcto
Confirmo
Exacto
```

Resultado:

```text
CONFIRMED_COMPUTATIONAL
```

si el rol propuesto alimenta cálculo.

```text
CONFIRMED_INFORMATIONAL
```

si el rol propuesto es informacional.

Si el rol propuesto es `unknown`, no desbloquea cómputo.

### NO / rechazo de interpretación

Ejemplos:

```text
NO
No es eso
No es el total de ventas
Incorrecto, está mal clasificada
Esa columna no corresponde a la interpretación propuesta
```

Resultado:

```text
OWNER_REJECTED_MAPPING
```

La columna no debe usarse para cálculo y debe quedar bloqueada para revisión o corrección semántica.

### Columna explícitamente no relevante

Ejemplos:

```text
Ignorar esa columna
No sirve para este análisis
No usar
No relevante
Descartar
```

Resultado:

```text
CONFIRMED_NOT_RELEVANT
```

### TU_RESPUESTA / corrección semántica

Ejemplo:

```text
Tu respuesta: esa columna es el saldo pendiente, no la venta total.
```

Resultado en este slice:

```text
OWNER_REJECTED_MAPPING
```

El clasificador no adivina ni traduce todavía la nueva semántica a un rol computacional. Sólo bloquea el mapeo propuesto para que el siguiente frente trate la corrección explícita con seguridad.

### Ambigüedad o insuficiencia

Ejemplos:

```text
Creo que sí
Más o menos
No sé
Ok
```

Resultado:

```text
INSUFFICIENT_ANSWER
```

No desbloquea cómputo.

## Seguridad preservada

El slice fija siempre:

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
owner_answer_validation_status=DECLARED_NOT_VALIDATED
```

La respuesta del dueño sigue siendo declaración no validada.

## Exclusiones explícitas

Este slice no hace:

```text
NO apply_owner_answer()
NO persistir matrix
NO recalcular computed_variables
NO reejecutar vertical_pipeline
NO cambiar owner_answers.jsonl
NO actualizar question_bundle
NO aplicar column confirmation
NO generar nueva pregunta
NO declarar evidencia validada
NO web
NO chat
NO LLM
```

## Tests cubiertos

```text
parsea target_ref válido
rechaza target_ref inválido
clasifica confirmación computacional
clasifica confirmación informacional
clasifica NO como rechazo de interpretación
clasifica negación explícita como OWNER_REJECTED_MAPPING
clasifica corrección TU_RESPUESTA como OWNER_REJECTED_MAPPING sin adivinar nuevo rol
clasifica instrucción de ignorar como CONFIRMED_NOT_RELEVANT
clasifica ambigüedad como insuficiente
clasifica texto corto como insuficiente
no desbloquea cómputo cuando proposed_role=unknown
produce OwnerColumnConfirmationAnswer
preserva owner_answer_text original
usa proposed_role como confirmed_role sólo cuando corresponde
mantiene flags de seguridad
serializa wrapper y answer
no toca storage
```

## Próximo frente permitido

Recién después de este slice queda habilitado diseñar:

```text
SERVICE_1_COLUMN_CONFIRMATION_APPLIER_V1
```

Ese próximo frente podrá consumir:

```text
OwnerColumnConfirmationAnswer
+ ColumnConfirmationMatrix.apply_owner_answer()
```

para producir una matriz actualizada, todavía sin recalcular ni reejecutar pipeline salvo autorización explícita futura.
