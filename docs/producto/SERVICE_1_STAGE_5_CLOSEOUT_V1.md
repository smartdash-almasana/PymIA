# SERVICE_1_STAGE_5_CLOSEOUT_V1

## Estado final de Stage 5

**Status:** `FORMALLY_CLOSED`

Stage 5 queda cerrado como frontera común de ingestión y normalización tabular para Servicio 1.

La frontera cerrada es:

```text
CSV  -> Common normalization router -> NormalizedTableV1
XLSX -> Common normalization router -> NormalizedTableV1
PDF  -> PDF_INTAKE_DEFERRED explícito
Otros -> UNSUPPORTED_FILE_TYPE explícito
```

No se abrirán más slices dentro de Stage 5 salvo demanda real posterior con especificación nueva y decisión explícita de reabrir la etapa.

---

## Capacidades cerradas

Stage 5 integra cinco capacidades versionadas:

1. **CSV intake** — `SERVICE_1_STAGE_5_CSV_INTAKE_V1`
2. **NormalizedTable V1** — `SERVICE_1_STAGE_5_NORMALIZED_TABLE_V1`
3. **CSV → NormalizedTable adapter** — `SERVICE_1_STAGE_5_CSV_TO_NORMALIZED_TABLE_ADAPTER_V1`
4. **XLSX → NormalizedTable adapter** — `SERVICE_1_STAGE_5_XLSX_TO_NORMALIZED_TABLE_ADAPTER_V1`
5. **Common normalization router** — `SERVICE_1_STAGE_5_COMMON_NORMALIZATION_ROUTER_V1`

---

## Tests certificados

```text
55 passed
```

Distribución por slice:

- CSV intake: 10 tests
- NormalizedTable V1: 12 tests
- CSV adapter: 11 tests
- XLSX adapter: 14 tests
- Common normalization router: 8 tests

Comando certificado por auditoría de cierre:

```bash
python -m pytest tests/smartpyme/test_service_1_csv_intake_v1.py tests/smartpyme/test_service_1_normalized_table_v1.py tests/smartpyme/test_service_1_csv_to_normalized_table_v1.py tests/smartpyme/test_service_1_xlsx_to_normalized_table_v1.py tests/smartpyme/test_service_1_common_normalization_router_v1.py -q --tb=line --basetemp .tmp_pytest_stage5_closeout_audit
```

Resultado certificado:

```text
55 passed in 2.99s
```

---

## Commits certificados

| Commit | Scope | Descripción |
|---|---|---|
| `69fc176` | runtime | Stage 5 XLSX → NormalizedTableV1 |
| `a5a0444` | memoria | Memoria Stage 5 CSV/XLSX actualizada |
| `001087c` | docs | Closeout Stage 5 inicial |
| `c249701` | runtime | Common normalization router CSV/XLSX/PDF-gate |

---

## Decisión sobre COMMON_TABLE_NORMALIZER_V1

**Resultado:** `NOT_APPROVED`

Se evaluó la apertura de `SERVICE_1_STAGE_5_COMMON_TABLE_NORMALIZER_V1` para consolidar normalización interna entre adapters. La auditoría determinó que no corresponde abrirlo.

---

## Razón de la decisión

- `NormalizedTableV1` ya cumple la función de contrato común suficiente para CSV y XLSX.
- La duplicación menor observada entre adapters (`_fit_width`, warnings, limpieza menor) es tolerable y no justifica un normalizador adicional.
- Crear un normalizador común interno sería una abstracción prematura sin consumidor específico.
- El cierre correcto de Stage 5 no es un normalizador interno adicional, sino un router común de entrada que derive tipos de archivo hacia adapters existentes y bloquee explícitamente lo no soportado.

---

## Common normalization router

**Estado:** `CLOSED`

El router común cierra la frontera de entrada de Stage 5 sin abrir Stage 6.

Responsabilidades cerradas:

```text
CSV  -> adapter CSV existente -> NormalizedTableV1
XLSX -> adapter XLSX existente -> NormalizedTableV1
PDF  -> PDF_INTAKE_DEFERRED
Otros -> UNSUPPORTED_FILE_TYPE
```

Garantías:

- No toca CLI.
- No toca pipeline.
- No toca chatbot.
- No toca LLM.
- No toca contabilidad.
- No implementa OCR.
- No implementa parser PDF.
- No abre consumidor downstream.
- No abre Stage 6.
- Mantiene `runtime_authorized=False` en todos los paths.

---

## PDF status

**Estado:** `PDF_INTAKE_DEFERRED`

PDF queda explícitamente bloqueado para Stage 5.

No hay:

- parsing PDF;
- OCR;
- interpretación documental;
- extracción semántica;
- ingestión PDF productiva.

El bloqueo está testeado y forma parte del contrato de cierre.

---

## Runtime authorization status

**Estado:** `runtime_authorized=False`

La autorización de runtime permanece cerrada en:

- CSV intake;
- NormalizedTableV1;
- CSV adapter;
- XLSX adapter;
- Common normalization router;
- paths OK;
- paths BLOCKED;
- PDF diferido;
- extensiones no soportadas.

No hay ningún path Stage 5 que retorne `runtime_authorized=True`.

---

## Fronteras prohibidas dentro de Stage 5

No se admite apertura de slices que involucren:

- PDF productivo ni OCR;
- chatbot;
- LLM;
- FSM;
- CLI (`service_1_operator.py`);
- pipeline (`service_1_pipeline_v1.py`);
- contabilidad;
- consumidores downstream;
- diagnóstico de negocio;
- ejecución de fórmulas.

---

## Disciplina de roadmap

Stage 5 no redefine Servicio 1.

Stage 5 no achica Servicio 1 a MVP/demo.

Stage 5 no abre Stage 6.

Stage 5 cierra exclusivamente la frontera técnica de normalización inicial:

```text
archivo soportado / no soportado
-> router común
-> adapter seguro
-> NormalizedTableV1 o bloqueo explícito
```

El router común pertenece al cierre de Stage 5, no a Stage 6.

---

## Próximas opciones posibles

Stage 5 queda formalmente cerrado.

Las próximas opciones pertenecen a un frente posterior y requieren decisión separada:

1. **Stage 6 — Consumidor operativo**: sólo si aparece un consumidor real que use `NormalizedTableV1`.
2. **Stage 6 — Integración controlada**: sólo con especificación clara de boundary, sin mezclar CLI/pipeline/chatbot/LLM.
3. **Detener runtime**: mantener Servicio 1 sin más runtime hasta que exista demanda real o caso de uso operativo.

La decisión de abrir Stage 6 requiere identificación de consumidor downstream con especificación clara y prompt separado.

---

## Criterio final de cierre

```text
SERVICE_1_STAGE_5 = FORMALLY_CLOSED
```

Motivos:

- 5 capacidades cerradas.
- 55 tests certificados.
- CSV/XLSX normalizados por frontera común.
- PDF diferido explícitamente.
- Unsupported bloqueado explícitamente.
- Runtime no autorizado.
- Sin apertura de CLI/pipeline/chatbot/LLM/OCR/contabilidad.
- Sin Stage 6 abierto.

---

## Firma

- Documento actualizado en modo `DOC ONLY`.
- Sin modificación de runtime, tests, CLI, pipeline ni memoria.
- Commit limitado exclusivamente a este archivo.
