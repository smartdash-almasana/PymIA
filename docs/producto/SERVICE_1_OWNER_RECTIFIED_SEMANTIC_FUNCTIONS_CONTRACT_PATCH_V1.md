# SERVICE_1_OWNER_RECTIFIED_SEMANTIC_FUNCTIONS_CONTRACT_PATCH_V1

## VEREDICTO

PROPOSED

## Objetivo

Separar contractualmente, dentro de Column Confirmation, los tres niveles semánticos necesarios para Servicio 1:

- `RAW_HEADER`
- `PYMIA_INFERRED_FUNCTION`
- `OWNER_RECTIFIED_FUNCTION`

La meta de este patch documental es evitar que la función inferida por PymIA y la función rectificada por el dueño PyME se mezclen, se pisen o queden implícitas.

## Problema actual

La capa actual de Column Confirmation ya soporta roles semánticos y no trabaja solamente con nombres de columnas.

Hoy existen señales reales de semántica, por ejemplo:

- `suggested_semantic_role`
- `owner_confirmed_role`
- `proposed_role`
- `confirmed_role`

Sin embargo, el modelo actual presenta tres problemas contractuales:

1. `suggested_semantic_role` y `confirmed_role` pueden colapsarse en la práctica.
2. La respuesta del dueño tipo `TU_RESPUESTA` puede terminar bloqueando el caso sin registrar una función rectificada trazable.
3. La función inferida original de PymIA no queda preservada como capa separada e inmutable cuando hay confirmación o corrección.

## Modelo contractual objetivo

Toda confirmación de columna relevante para Servicio 1 debe preservar explícitamente tres niveles:

### 1. `RAW_HEADER`

Lo que el archivo XLSX dice literalmente en su encabezado.

Ejemplo:

```text
Total
MetodoPago
Observaciones
```

### 2. `PYMIA_INFERRED_FUNCTION`

La función semántica probable propuesta por PymIA a partir de headers, estructura, muestra de valores, contexto del rubro y heurísticas históricas.

Ejemplo:

```text
venta_total
payment_method
unknown
```

### 3. `OWNER_RECTIFIED_FUNCTION`

La función semántica resultante después de la intervención del dueño PyME.

Puede:

- confirmar la inferencia;
- corregirla a una nueva función;
- rechazarla;
- dejarla bloqueada por falta de normalización segura.

Sólo `OWNER_RECTIFIED_FUNCTION` puede alimentar uso operativo posterior.

## Regla de inmutabilidad

### `RAW_HEADER`

No se altera.

Debe conservar el texto original de la columna tal como llega desde el archivo.

### `PYMIA_INFERRED_FUNCTION`

No se sobreescribe.

Debe conservar la propuesta original de PymIA aunque luego el dueño confirme otra cosa.

### `OWNER_RECTIFIED_FUNCTION`

Se registra separado.

No debe reemplazar ni borrar la inferencia original.

## Estados contractuales

La capa futura debe exponer, como mínimo, estos estados:

### `INFERRED_NOT_RECTIFIED`

PymIA ya propuso una función, pero el dueño PyME todavía no la rectificó.

### `OWNER_CONFIRMED_AS_INFERRED`

El dueño confirma que la función inferida por PymIA es correcta.

Resultado esperado:

```text
PYMIA_INFERRED_FUNCTION == OWNER_RECTIFIED_FUNCTION
```

sin perder trazabilidad de ambas capas.

### `OWNER_RECTIFIED_TO_NEW_FUNCTION`

El dueño corrige la función propuesta y define una nueva función normalizable.

Resultado esperado:

```text
PYMIA_INFERRED_FUNCTION != OWNER_RECTIFIED_FUNCTION
```

sin adivinanza del sistema y con trazabilidad explícita.

### `OWNER_REJECTED`

El dueño rechaza la propuesta de PymIA, pero no aporta una función nueva normalizable.

No debe habilitar uso operativo.

### `BLOCKED_UNNORMALIZABLE_OWNER_RESPONSE`

El dueño responde, pero la respuesta no permite normalización segura hacia una función semántica operativa.

Debe bloquear sin adivinar.

## Patch futuro recomendado

Para alinear Column Confirmation con la regla rectora vigente, el patch futuro mínimo debería:

1. agregar `owner_rectified_function` como campo separado;
2. conservar `suggested_semantic_role` como inferencia original de PymIA;
3. adaptar la ruta `TU_RESPUESTA` para registrar corrección cuando sea normalizable;
4. si la corrección no es normalizable, bloquear sin adivinar ni pisar la inferencia original.

## Criterios de PASS para futura implementación

La futura implementación de runtime sólo debe considerarse `PASS` si cumple todos estos criterios:

- no se pierde `RAW_HEADER`;
- no se pisa `PYMIA_INFERRED_FUNCTION`;
- `OWNER_RECTIFIED_FUNCTION` queda trazable;
- ninguna tool usa función no rectificada;
- los tests cubren confirmación, corrección, rechazo y respuesta no normalizable.

## Alcance de este documento

Este documento define un patch contractual mínimo.

No implementa runtime.
No modifica tests.
No autoriza pipeline.
No redefine roadmap.

## Cierre

SERVICE_1_OWNER_RECTIFIED_SEMANTIC_FUNCTIONS_CONTRACT_PATCH_V1: PROPOSED

RUNTIME_CODE_CHANGED: NO

TESTS_REQUIRED_FOR_DOC: NO
