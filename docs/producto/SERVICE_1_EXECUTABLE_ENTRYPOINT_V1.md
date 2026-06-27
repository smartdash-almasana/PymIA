# SERVICE_1_EXECUTABLE_ENTRYPOINT_V1

## Estado

```text
ENTRYPOINT_CONTRACT_DOC
READY_FOR_IMPLEMENTATION
RUNTIME_IMPACT: NONE
CODE_IMPACT: NONE
TEST_IMPACT: NONE
```

## Veredicto

```text
SERVICE_1_EXECUTABLE_ENTRYPOINT_V1: DEFINED
MINIMAL_SCOPE_ONLY: YES
REENTRY_INCLUDED: NO
PIPELINE_INCLUDED: NO
FSM_INCLUDED: NO
AUTONOMOUS_RUNTIME_ALLOWED: NO
```

## Propósito

Definir el entrypoint ejecutable mínimo y controlado de Servicio 1 para correr la cadena ya existente de intake owner-facing sin abrir runtime autónomo, pipeline full, FSM ni reentry.

Este documento no implementa código.

Su función es fijar:

- cuál es la cadena mínima que debe ejecutar el entrypoint;
- qué input recibe;
- qué output debe devolver;
- qué módulos puede tocar;
- qué tests deben congelar su frontera;
- qué cosas quedan explícitamente fuera de alcance.

## Quick path

1. Recibir un `FileAsset` y `source_channel`.
2. Ejecutar intake → taskspec patch → owner response → formatted message.
3. Devolver un packet único, gobernado y con `runtime_authorized = False`.

## Regla central

```text
El entrypoint ejecutable de Servicio 1 V1 no decide negocio,
no corre herramientas,
no reejecuta casos,
no persiste reentry,
no arma pipeline,
no habilita runtime autónomo.
```

Sólo compone una cadena mínima ya validada y la expone como unidad operable.

## Cadena autorizada

```text
FileAsset
→ classify_file_intake(...)
→ derive_taskspec_patch_from_file_intake(...)
→ render_owner_response_v1(...)
→ format_owner_message_v1(...)
```

## Módulos autorizados

| Módulo | Rol |
|---|---|
| `file_intake_v1.py` | clasificación inicial XLSX-first |
| `file_intake_taskspec_boundary_v1.py` | patch técnico mínimo |
| `owner_response_renderer_v1.py` | respuesta owner-facing prudente |
| `owner_message_formatter_v1.py` | texto final para canal manual |

## Módulos explícitamente fuera

```text
service_1_boundary_chain_v1.py
service_1_fsm_decision_patch_v1.py
service_1_pipeline_v1.py
service_1_owner_answer_reentry_v1.py
service_1_owner_answer_reentry_persistence_v1.py
service_1_case_reentry_read_model_v1.py
vertical_pipeline.py
document_ingestion runtime real
LLM adapters
chatbot
CLI nueva
```

## Input mínimo esperado

El entrypoint debe aceptar como mínimo:

```yaml
source_channel: cli | chat | upload | api | unknown
asset:
  asset_id: string
  filename: string | null
  declared_mime_type: string | null
  size_bytes: int | null
  source: upload | path | message | api | unknown
```

No debe exigir:

```text
credenciales
paths productivos obligatorios
storage previo
owner answers
question_ref
pipeline run config
```

## Output mínimo esperado

El entrypoint debe devolver un packet único que conserve, como mínimo:

```yaml
service_name: SERVICE_1
runtime_authorized: false
file_intake: FileIntakeResult
taskspec_patch: TaskSpecPatch
owner_response: OwnerResponseV1
owner_message_text: string
notes: list
```

## Invariantes obligatorios

El output debe congelar estas invariantes:

```text
runtime_authorized = False
service_name = SERVICE_1
owner_message_text no puede estar vacío
owner_response.next_owner_action debe existir
taskspec_patch.next_allowed_action debe existir
el entrypoint no puede alterar las decisiones del intake
```

## Comportamiento esperado

### Caso XLSX soportado

Debe devolver:

```text
support.status = SUPPORTED
column_confirmation_required = True
runtime_authorized = False
next step prudente para el dueño
```

### Caso CSV/PDF/imagen/ZIP no soportado

Debe devolver:

```text
support.status = UNSUPPORTED_IN_V1
runtime_authorized = False
pedido explícito de XLSX o archivo verificable
```

### Caso desconocido o inseguro

Debe devolver:

```text
support.status = UNKNOWN o bloqueo unsafe
runtime_authorized = False
mensaje prudente
```

## Claims prohibidos

El entrypoint no puede afirmar:

```text
que ya leyó internamente el XLSX
que ya diagnosticó la empresa
que ya calculó márgenes, caja o stock
que ya generó entregable final
que puede reentry sin question flow previo
que quedó autorizado un runtime
```

## Write scope mínimo para implementación

Cuando se implemente este frente, el write scope mínimo debe ser:

```text
PymIA-Live/pymia/smartpyme/service_1_executable_entrypoint_v1.py
PymIA-Live/tests/smartpyme/test_service_1_executable_entrypoint_v1.py
```

Idealmente sin tocar vecinos ya validados.

## Tests esperados

La implementación futura debe congelar como mínimo:

1. caso XLSX soportado compone correctamente la cadena;
2. caso CSV bloquea y pide XLSX;
3. caso unknown devuelve bloqueo prudente;
4. `runtime_authorized` queda siempre en `False`;
5. no importa `vertical_pipeline`, `service_1_boundary_chain_v1`, `service_1_fsm_decision_patch_v1`, `openai`, `chatbot`;
6. no ejecuta reentry ni persistence;
7. delega el formato final en `format_owner_message_v1`.

## Criterio de PASS

El frente pasa si:

```text
existe un módulo único de entrypoint
compone sólo la cadena autorizada
preserva bloqueo de runtime
devuelve packet completo y mensaje final
los tests de frontera pasan
```

## Criterio de FAIL

El frente falla si:

```text
mezcla reentry
mezcla pipeline
mezcla FSM
altera decisiones del intake
habilita runtime
importa capas prohibidas
```

## Non-goals

Este documento no autoriza:

```text
pipeline full
delivery XLSX
evidence custody persistence
rehearsal end-to-end
checkpoint final de Servicio 1
```

## Próximo paso correcto

```text
Implementar service_1_executable_entrypoint_v1.py
con tests focales de frontera.
```
