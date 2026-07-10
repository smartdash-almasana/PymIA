# SERVICE_1_WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW_TASKSPEC_V1

## Veredicto

```text
WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW: NOT_CERTIFIED_NEXT_TASK
RUNTIME_AUTHORIZED: false
REEXECUTION_AUTHORIZED: false
RECALCULATION_AUTHORIZED: false
DELIVERY_AUTHORIZED: false
AUTONOMOUS_DELIVERY_AUTHORIZED: false
```

Este TaskSpec define el próximo ciclo metodológico para certificar el flujo web real de
confirmación de columnas de Servicio 1 / CASE_001. No certifica ese flujo: lo declara como
tarea siguiente y fija su frontera.

## Estado actual

```text
landing smoke / prototype: EXISTS
python pure chain: TESTED
real html / backend integration: NOT_CERTIFIED
```

Hechos observados en el repo:

- `landing/` contiene smoke / prototipos browser-only:
  - `service_1_excel_upload_smoke.html`
  - `build_service1_excel_ingestion_chat_web.py`
  - `build_service1_xlsx_owner_chat_html.py`
  Estos no gobiernan Servicio 1 y no procesan uploads reales certificados.
- Existe una cadena Python pura ya testeada:
  - XLSX extracted structure
  - `ColumnConfirmationMatrix`
  - display model
  - owner answer intake
  - closed-loop smoke
- `docs/current/SERVICE_1_WEB_COLUMN_CONFIRMATION_STATE_V1.md` declara explícitamente:
  - No conecta HTML real.
  - No procesa uploads web reales.
- Tests observados: 20 passed para web smoke / owner intake / structure chain.
- `docs/current/SERVICE_1_CASE_001_OWNER_COLUMN_CONFIRMATIONS_EVIDENCE_CYCLE_TASKSPEC_V1.md`
  ya define la validación de las 12 respuestas owner; este TaskSpec es el mecanismo de
  captura real que alimenta a ese ciclo, no lo reemplaza.

Conclusión de estado:

```text
WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW_NOT_CERTIFIED
```

## Objetivo del ciclo

Cerrar un flujo observable de punta a punta, manteniendo runtime / delivery / diagnóstico
bloqueados:

```text
real XLSX upload (web)
-> canonical PymIA reader (not SheetJS as certified source of truth)
-> ColumnConfirmationMatrix
-> 12 CASE_001 column-confirmation questions shown to owner
-> real owner answers captured online
-> evidence artifact
```

Puntos obligatorios del objetivo:

- Cargar un XLSX real desde la web.
- Usar el reader canónico de PymIA
  (`service_1_xlsx_to_normalized_table_v1.py` / `service_1_xlsx_structure_v1.py`),
  no SheetJS local como fuente certificada de verdad semántica.
- Generar `ColumnConfirmationMatrix` desde la estructura canónica.
- Mostrar las 12 preguntas de confirmación de columnas de CASE_001 al owner.
- Capturar las respuestas reales del owner online (SÍ / NO / TU_RESPUESTA o equivalente
  gobernado).
- Producir un evidence artifact (exportado o persistido) que alimente el ciclo de
  evidencia de las 12 respuestas.

## Prohibiciones

El ciclo no autoriza:

```text
no runtime
no runner
no SaaS / API worker
no dry-run
no cálculo
no recálculo
no diagnóstico
no delivery
no autonomous delivery
no LLM decision authority
no respuestas simuladas / fixture tratadas como owner real
```

La fuente de verdad semántica sigue siendo PymIA (el reader canónico), no el browser.
El LLM, si interviene, sólo comunica; no decide estado de caso, evidencia, ni desbloquea
runtime.

## Acceptance criteria

El ciclo se considera evidencia mínima válida sólo si se prueba todo lo siguiente:

```text
1. upload real comprobado (archivo XLSX recibido por el backend PymIA, no sólo preview browser)
2. reader canónico PymIA usado para extraer estructura (no SheetJS como verdad certificada)
3. ColumnConfirmationMatrix construida desde esa estructura
4. las 12 preguntas CASE_001 visibles para el owner
5. las 12 respuestas owner capturadas online (0 faltantes)
6. evidence artifact exportado o persistido
7. runtime_authorized = false
8. reexecution_authorized = false
9. recalculation_authorized = false
10. delivery_authorized = false
11. tests / smoke reproducibles del flujo real
```

La validación de completitud, ambigüedad y refs desconocidas de las 12 respuestas debe
seguir `docs/current/SERVICE_1_CASE_001_OWNER_COLUMN_CONFIRMATIONS_EVIDENCE_CYCLE_TASKSPEC_V1.md`.

## Stop conditions

Detener y mantener `WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW_NOT_CERTIFIED` si alguna condición ocurre:

```text
1. la web usa sólo SheetJS local como fuente de verdad (sin backend/cable PymIA)
2. no hay backend / cable PymIA que reciba el upload real
3. las respuestas son fixture / simuladas tratadas como owner real
4. falta alguna de las 12 respuestas
5. alguna respuesta es ambigua o ref desconocida sin resolver
6. se intenta desbloquear runtime / dry-run / cálculo / diagnóstico / delivery
7. el LLM asume autoridad de decisión de caso o evidencia
```

## Próximo paso después del TaskSpec

Según lo que el repo ya tiene, el siguiente paso no es web aún:

- El repo ya posee la cadena Python pura testeada y los readers canónicos.
- Lo que falta es el boundary de intake web real: upload -> reader canónico PymIA.

Por lo tanto, el próximo artefacto debe ser:

```text
ModuleContract para el boundary de web intake real
(service_1_web_column_confirmation_intake_boundary_v1 o nombre análogo)
```

Ese ModuleContract debe declarar:

```text
- módulo boundary puro de intake (upload -> canonical reader -> matrix -> 12 preguntas)
- no runtime / no delivery / no diagnóstico
- backend PymIA como única fuente de verdad
- tests focales reproducibles
```

Sólo tras ese ModuleContract autorizado puede considerarse una implementación mínima de
wiring, y nunca antes de la evidencia de las 12 respuestas owner del ciclo de evidencia.

## Frase segura

```text
Hoy existe smoke/prototipo local y cadena Python testeada; falta certificar el flujo web real upload -> preguntas -> respuestas -> evidencia.
```
