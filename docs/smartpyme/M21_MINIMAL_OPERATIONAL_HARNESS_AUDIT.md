# M21 — Auditoría Arnés Operacional Mínimo

Fecha: 2026-06-03  
Rol: auditor de lectura pesada. No se implementó código.  
Alcance: diseño de un arnés determinístico que consolide el estado operacional del pipeline SmartPyme a partir de fuentes ya existentes en el repo.

---

## 0. Veredicto

```text
M21 Minimal Operational Harness = READY_FOR_GEMINI_REVIEW
```

### Causa

- Las fuentes de datos (registry, summary.json, trace.json, report.md) ya existen y son estables.
- El reader `pymia/smartpyme/capability_registry.py` ya valida el registry.
- El output de `run_scenarios.py` ya produce `summary.json` con campos consumibles.
- El arnés puede construirse como lector puro sin tocar dispatcher, plugins, ni introducir IA.
- Los riesgos identificados son acotables con el scope mínimo propuesto.

---

## 1. Datos del registry útiles para el arnés

Fuente: `pymia/smartpyme/capabilities.yaml` y `pymia/smartpyme/capability_registry.py`.

El arnés debe consumir el registry **vía el lector Python** (`load_registry()`, `list_capabilities()`), no parseando YAML directamente, para heredar las validaciones existentes.

### 1.1 Campos requeridos del registry

| Campo | Por qué sirve al arnés |
|---|---|
| `capability_id` | Identificador único; clave de agrupación. |
| `label` | Nombre legible para humanos en el output. |
| `status` | Semáforo maestro (PIPELINE_CERTIFIED, PARTIALLY_AVAILABLE_BY_PATH, NOT_FOUND, etc.). |
| `pipeline_certified` (bool) | Determina si la capacidad cuenta como certificada por radiografía. |
| `dispatcher_available` (bool) | Determina si es ejecutable por el dispatcher formal. |
| `cli_available` (bool) | Determina si es ejecutable por camino lateral. |
| `plugin_module` (str \| null) | Trazabilidad del módulo real (solo para referencia, no para ejecutar). |
| `plugin_function` (str \| null) | Idem. |
| `dispatcher_classification` (str \| null) | Permite correlacionar con `trace.final_summary.runtime_classification`. |
| `tests` (list[str]) | Inventario de cobertura declarada. |
| `docs` (list[str]) | Trazabilidad documental. |
| `no_promise_reason` (str \| null) | Texto explicativo si `status != PIPELINE_CERTIFIED`. |

### 1.2 Reglas de agrupación derivadas del registry

- **certified_capabilities** = capacidades con `status == "PIPELINE_CERTIFIED"` y `pipeline_certified == true`.
- **partial_capabilities** = capacidades con `status in {"PARTIALLY_AVAILABLE_BY_PATH", "UNSUPPORTED_IN_DISPATCHER", "AVAILABLE"}` y `pipeline_certified == false` (o `dispatcher_available == false`).
- **documented_not_implemented** = capacidades con `status in {"DOCUMENTED_NOT_IMPLEMENTED", "NOT_FOUND", "CONCEPTUAL"}`.

### 1.3 Lo que el arnés NO debe leer del registry

- `version` del YAML: no es necesario para el estado operacional.
- Campos de `metadata` que pudieran agregarse: no están validados por el reader y serían frágiles.

---

## 2. Datos de summary.json útiles

Fuente: `.pipeline_radiography/*/summary.json` (producido por `pymia/pipeline_radiography/run_scenarios.py:_build_summary`).

### 2.1 Estructura observada (lectura de `.pipeline_radiography/summary.json`)

```json
{
  "timestamp": "2026-06-02T16:44:19.026412+00:00",
  "total_scenarios": 4,
  "passed": 2,
  "blocked_expected": 2,
  "failed": 0,
  "ambiguous": 0,
  "scenarios": [
    {
      "scenario_id": "margin_excel_happy_path",
      "trace_id": "trace_97f399bc21f7",
      "overall_status": "PASS",
      "blocked_at": null,
      "duration_ms": 64
    }
  ]
}
```

### 2.2 Campos requeridos para el arnés

| Campo | Uso en el arnés |
|---|---|
| `total_scenarios` | Total ejecutado; base de cobertura. |
| `passed` | Conteo de escenarios OK. |
| `blocked_expected` | Conteo de bloqueos sanos. |
| `failed` | Conteo de fallos contractuales. |
| `ambiguous` | Conteo de no evaluables. |
| `scenarios[].scenario_id` | Identificador de escenario. |
| `scenarios[].trace_id` | Enlace al trace.json correspondiente. |
| `scenarios[].overall_status` | Clasificación PASS / BLOCKED_EXPECTED / FAIL / AMBIGUOUS. |
| `scenarios[].blocked_at` | Fase donde se bloqueó (null si PASS o AMBIGUOUS). |
| `scenarios[].duration_ms` | Métrica operativa; no crítica para el estado. |

### 2.3 Reglas de agrupación derivadas de summary.json

- **failed_scenarios** = `scenarios[].overall_status == "FAIL"`.
- **blocked_expected_scenarios** = `scenarios[].overall_status == "BLOCKED_EXPECTED"`.
- **ambiguous_scenarios** = `scenarios[].overall_status == "AMBIGUOUS"` (no estaba en la lista de output pedido, pero debe existir para el veredicto).

### 2.4 Lo que el arnés NO debe leer de summary.json

- `timestamp`: irrelevante para el estado consolidado (puede usarse solo para etiquetar el output, no para decidir).
- `duration_ms`: ruido para el semáforo.

---

## 3. Datos de trace.json útiles

Fuente: `.pipeline_radiography/*/<scenario_id>/trace.json` (producido por `pymia/pipeline_radiography/report.py:generate_developer_report`).

### 3.1 Estructura observada (campos clave)

```json
{
  "trace_id": "trace_97f399bc21f7",
  "scenario_id": "margin_excel_happy_path",
  "scenario": { "...": "Snapshot del escenario" },
  "trace": {
    "stages": [
      {
        "name": "intake",
        "status": "OK",
        "input_type": "...",
        "output_type": "...",
        "summary": { "...": "..." },
        "error": null,
        "duration_ms": 12
      }
    ],
    "overall_status": "PASS",
    "blocked_at": null,
    "final_summary": {
      "final_status": "READY_TO_DELIVER",
      "runtime_classification": "excel_diagnostic",
      "dispatch_status": "EXECUTED",
      "findings_count": 3,
      "must_not_dispatch": false
    },
    "duration_ms": 64
  },
  "result": { "...": "Resultado completo del pipeline" }
}
```

### 3.2 Campos requeridos para el arnés

| Campo | Uso en el arnés |
|---|---|
| `trace.trace_id` | Identificador único de traza. |
| `trace.scenario_id` | Enlace con el escenario. |
| `trace.overall_status` | Doble verificación contra summary.json. |
| `trace.blocked_at` | Fase exacta de bloqueo. |
| `trace.final_summary.runtime_classification` | Correlación con `capabilities.yaml:dispatcher_classification`. |
| `trace.final_summary.final_status` | Estado final de negocio. |
| `trace.final_summary.dispatch_status` | Estado del dispatch. |
| `trace.final_summary.findings_count` | Sanity check de findings. |
| `trace.final_summary.must_not_dispatch` | Validación de contrato. |
| `trace.stages[].error` | Primer error no nulo para diagnóstico. |
| `trace.stages[].name` | Lista de fases ejecutadas. |

### 3.3 Reglas de correlación trace ↔ registry

- Para cada trace con `runtime_classification` no nulo:
  - Buscar la capacidad en el registry cuyo `dispatcher_classification` coincida.
  - Si no existe → `scenario_orphan_classification` (inconsistencia de cobertura).
  - Si existe y `dispatcher_available == false` → `scenario_expected_unsupported` (esto es lo que M19.6 llama EXPECTED_UNSUPPORTED).
  - Si existe y `dispatcher_available == true` y el trace terminó en PASS → capacidad certificada en este run.

### 3.4 Lo que el arnés NO debe leer de trace.json

- `scenario` (snapshot completo): redundante con el catálogo.
- `result.*` (intake_record, evidence_records, sufficiency_result, etc.): bajo nivel; suficiente con `final_summary`.
- `stages[].summary` profundo: solo el `error` es accionable; el resto es ruido para el semáforo.

---

## 4. Output mínimo recomendado

El arnés debe producir un único artefacto JSON determinístico. Esquema propuesto:

```json
{
  "harness_version": "1.0",
  "generated_at_utc": "2026-06-03T00:00:00Z",
  "registry_version": "1.0",
  "pipeline_status": "GREEN",
  "counts": {
    "certified_capabilities": 2,
    "partial_capabilities": 0,
    "failed_scenarios": 0,
    "blocked_expected_scenarios": 2,
    "ambiguous_scenarios": 0,
    "total_scenarios": 4
  },
  "certified_capabilities": [
    {
      "capability_id": "excel_diagnostic",
      "label": "Diagnostico Excel",
      "status": "PIPELINE_CERTIFIED",
      "trace_ids": ["trace_97f399bc21f7"],
      "scenario_ids": ["margin_excel_happy_path"]
    },
    {
      "capability_id": "supplier_duplicate_check",
      "label": "Revision de proveedores duplicados",
      "status": "PIPELINE_CERTIFIED",
      "trace_ids": ["trace_supplier_..."],
      "scenario_ids": ["supplier_duplicate_check_happy_path"]
    }
  ],
  "partial_capabilities": [],
  "failed_scenarios": [
    {
      "scenario_id": "...",
      "trace_id": "...",
      "overall_status": "FAIL",
      "blocked_at": "...",
      "first_error": "..."
    }
  ],
  "blocked_expected_scenarios": [
    {
      "scenario_id": "margin_excel_missing_evidence",
      "trace_id": "trace_266f0842a224",
      "blocked_at": "evidence_gate",
      "duration_ms": 4
    }
  ],
  "ambiguous_scenarios": [],
  "next_action": "NONE"
}
```

### 4.1 Valores permitidos

- `pipeline_status`:
  - `GREEN` = 0 FAIL y 0 AMBIGUOUS.
  - `YELLOW` = 0 FAIL y >=1 AMBIGUOUS, o >=1 capacidad parcial.
  - `RED` = >=1 FAIL.
- `next_action` (enum cerrado, no texto libre):
  - `NONE` = GREEN.
  - `RE_RUN_RADIOGRAPHY` = YELLOW por AMBIGUOUS.
  - `FIX_SCENARIO` = RED con un único FAIL.
  - `FIX_SCENARIOS` = RED con múltiples FAIL.
  - `REVIEW_REGISTRY` = hay `scenario_orphan_classification`.
  - `REVIEW_PARTIAL_CAPABILITY` = hay capacidades parciales con escenarios esperados.

### 4.2 Determinismo

- `generated_at_utc` se incluye solo para auditoría, pero **no** afecta `pipeline_status` ni `next_action`.
- El arnés no debe incluir en el output campos derivados de timestamps (duración, hora de ejecución) que cambien entre runs.
- El orden de las listas debe ser estable: ordenar por `capability_id` y `scenario_id`.

---

## 5. Archivo / módulo que Codex debe implementar

### 5.1 Archivos nuevos

```text
pymia/operational_harness/
  __init__.py
  harness.py          # entrypoint: read_registry() + read_radiography() + consolidate()
  sources.py          # loaders tipados: load_registry(), load_summary(), load_trace()
  consolidate.py      # lógica pura de agrupación y semáforo
  schema.py           # dataclasses del output (sin dependencias externas)

tests/smartpyme/
  test_operational_harness.py   # tests del lector puro

docs/smartpyme/
  M21_MINIMAL_OPERATIONAL_HARNESS_CHECKPOINT.md  # cierre operativo
```

### 5.2 Archivos a NO tocar

- `pymia/smartpyme/capabilities.yaml` (solo lectura).
- `pymia/smartpyme/capability_registry.py` (solo lectura; el arnés lo consume, no lo modifica).
- `pymia/pipeline_radiography/*` (solo lectura).
- `pymia/smartpyme/microservice_dispatcher.py` (prohibido: no tocar dispatcher).
- Cualquier plugin (`excel_diagnostic.py`, `supplier_duplicate_check`).
- Nada en `conversa-engine/`, `landing/`, `Pymia-memoria/`.
- Nada de Telegram, PDF, HTML, UI.

### 5.3 Dependencias permitidas

- `pyyaml` (ya en el repo).
- `dataclasses` (stdlib).
- `pathlib` (stdlib).
- `json` (stdlib).
- `pymia.smartpyme.capability_registry` (reader existente).
- `pymia.pipeline_radiography.trace.ALLOWED_RADIOGRAPHY_VERDICTS` (constantes ya definidas).

### 5.4 Prohibido

- `requests`, `httpx`, `urllib`: el arnés no hace red.
- Cualquier import de modelo de lenguaje, SDK de Gemini/Vertex, o `langchain`.
- Cualquier import de `pymia.smartpyme.microservice_dispatcher` o plugins.
- Cualquier import de UI/Telegram/PDF/HTML.

---

## 6. Tests mínimos requeridos

### 6.1 Tests del reader puro (`tests/smartpyme/test_operational_harness.py`)

1. **test_harness_reads_registry_via_reader**
   - Verifica que `harness` llama a `load_registry()`, no a `yaml.safe_load` directo.
2. **test_harness_groups_certified_capabilities**
   - Fixture: registry con 2 PIPELINE_CERTIFIED, 1 PARTIALLY_AVAILABLE_BY_PATH, 1 NOT_FOUND.
   - Assert: `certified_capabilities` tiene longitud 2, ordenadas por id.
3. **test_harness_groups_partial_capabilities**
   - Misma fixture.
   - Assert: `partial_capabilities` tiene longitud 1, contiene la capacidad parcial.
4. **test_harness_reads_summary_with_zero_failures**
   - Fixture: summary.json con 4 PASS, 0 FAIL.
   - Assert: `pipeline_status == "GREEN"`, `next_action == "NONE"`.
5. **test_harness_reads_summary_with_failures**
   - Fixture: summary.json con 1 FAIL.
   - Assert: `pipeline_status == "RED"`, `failed_scenarios` tiene 1 entrada, `next_action == "FIX_SCENARIO"` o `FIX_SCENARIOS` según cantidad.
6. **test_harness_reads_summary_with_ambiguous**
   - Fixture: summary.json con 1 AMBIGUOUS, 0 FAIL.
   - Assert: `pipeline_status == "YELLOW"`, `next_action == "RE_RUN_RADIOGRAPHY"`.
7. **test_harness_correlates_trace_with_registry**
   - Fixture: trace.json con `runtime_classification="supplier_duplicate_check"`.
   - Assert: el trace aparece en `certified_capabilities[supplier_duplicate_check].trace_ids` o en `ambiguous_scenarios` según `dispatcher_available`.
8. **test_harness_detects_orphan_classification**
   - Fixture: trace con `runtime_classification="nonexistent_capability"`.
   - Assert: el trace aparece en `ambiguous_scenarios` con razón `orphan_classification` y `next_action == "REVIEW_REGISTRY"`.
9. **test_harness_determinism**
   - Ejecutar `consolidate()` dos veces con los mismos fixtures.
   - Assert: JSON byte-a-byte idéntico (excluyendo `generated_at_utc`).
10. **test_harness_does_not_import_forbidden_modules**
    - Inspección estática: `ast` parse de `harness.py` y assert de que no aparecen imports prohibidos (`langchain`, `openai`, `google.generativeai`, `telegram`, `pdf`, `html`, `dashboard`, `requests`, `httpx`).
11. **test_harness_handles_missing_trace_file**
    - Fixture: scenario en summary sin trace.json correspondiente.
    - Assert: el arnés registra el escenario con `trace_id` pero sin fase de error; `pipeline_status` cae a YELLOW por missing data, no a RED.
12. **test_harness_handles_empty_radiography_dir**
    - Si `.pipeline_radiography/` no existe: `pipeline_status == "RED"`, `next_action == "RE_RUN_RADIOGRAPHY"`.

### 6.2 Tests de integración (opcional, lentos)

- `test_harness_end_to_end_against_real_artifacts`:
  - Corre `python -m pymia.pipeline_radiography.run_scenarios --output-dir .tmp_radiography/test_harness`.
  - Corre el arnés contra `.tmp_radiography/test_harness/summary.json`.
  - Assert: `pipeline_status in {"GREEN", "YELLOW"}` (no RED en main).

### 6.3 Cobertura mínima

- Ramas cubiertas: `consolidate.py` >= 90%.
- `harness.py` y `sources.py` >= 80% (puede haber branches de error de I/O no cubiertos).

---

## 7. Qué NO debe hacer el arnés (todavía)

1. **No debe ejecutar el pipeline**: solo lee artefactos. Quien ejecuta es `run_scenarios`.
2. **No debe conectar a dispatcher, plugins, ni microservicios**: es un lector.
3. **No debe generar HTML, PDF, dashboards, ni UIs**: solo JSON.
4. **No debe invocar LLMs, Gemini, Vertex, ni ningún modelo de lenguaje**: la consolidación es por reglas determinísticas.
5. **No debe escribir en `pymia/smartpyme/capabilities.yaml`**: el registry es fuente de verdad externa al arnés.
6. **No debe inferir capacidades**: si una capacidad no está en el registry, no existe para el arnés.
7. **No debe "arreglar" el estado**: solo reporta. El `next_action` es una sugerencia enum, no una acción ejecutada.
8. **No debe depender de red, archivos temporales fuera de `.pipeline_radiography/`, ni servicios externos.
9. **No debe usar timestamps para decidir**: el semáforo se basa en `overall_status` y `counts`.
10. **No debe consumir `result.*` de trace.json**: solo `final_summary` y `stages[].error`.
11. **No debe incluir capacidades CONCEPTUAL o DOCUMENTED_NOT_IMPLEMENTED en `partial_capabilities`**: esas van a un grupo aparte (`documented_not_implemented`) o se omiten del output mínimo.
12. **No debe modificar archivos en `conversa-engine/`, `landing/`, `Pymia-memoria/`, ni nada de Telegram/PDF/HTML/UI.

---

## 8. Cómo evitar volverse IA residente prematura

El M21 es lector, no agente. Para que no se deslice hacia IA residente:

### 8.1 Reglas arquitectónicas

- **Una sola función pura de consolidación**: `consolidate(registry, summary, traces) -> dict`. Sin estado, sin I/O, sin red. Determinista y testeable.
- **Sin bucle de decisión**: el output no se retroalimenta al pipeline. El arnés no decide qué escenario correr.
- **Sin memoria de runs anteriores**: cada ejecución lee los artefactos del run actual. No hay base de datos propia.
- **Sin texto libre generado**: todos los campos string son enums cerrados (`pipeline_status`, `next_action`, `overall_status`).

### 8.2 Reglas de dependencia

- **Prohibido**: cualquier SDK de LLM, vector store, embeddings, RAG.
- **Prohibido**: imports de `pymia.smartpyme.*` que ejecuten lógica de negocio (solo `capability_registry` y constantes de `pipeline_radiography.trace`).
- **Prohibido**: dependencias nuevas en `pyproject.toml` más allá de `pyyaml` (ya presente).

### 8.3 Reglas de output

- El JSON producido no contiene campos opacos: cada campo tiene un dominio cerrado.
- `next_action` es enum: no se genera texto natural.
- No hay `confidence`, `score`, `probability`, ni `rationale`: eso es territorio de IA.

### 8.4 Reglas de tests

- El test `test_harness_does_not_import_forbidden_modules` es la barrera principal.
- Un test de snapshot del JSON producido contra fixtures fijos garantiza que el output no crece accidentalmente.

### 8.5 Señales de alarma a vigilar en code review

- Aparición de un campo `"explanation"` o `"narrative"` en el output.
- Aparición de un import nuevo en `harness.py` o `consolidate.py`.
- Cualquier intento de que el arnés "aprenda" de runs previos.
- Cualquier intento de que el arnés sugiera código a escribir.

---

## 9. Riesgos identificados

### 9.1 Riesgos reales

1. **Acoplamiento a la forma de summary.json**:
   El arnés depende de los campos `total_scenarios`, `passed`, `blocked_expected`, `failed`, `ambiguous`, `scenarios[]`. Si `run_scenarios.py` cambia la forma del summary, el arnés se rompe silenciosamente.
   *Mitigación*: test snapshot del summary esperado; el arnés debe fallar loud si falta un campo.

2. **Acoplamiento a la forma de trace.json**:
   El arnés lee `trace.final_summary.runtime_classification`, `dispatch_status`, `findings_count`, `must_not_dispatch`. Si el reporte cambia la forma, falla.
   *Mitigación*: leer solo lo necesario y validar tipos con dataclasses (`schema.py`).

3. **Stale data en `.pipeline_radiography/`**:
   El arnés local lee la última corrida. Si el usuario corre el arnés sin correr `run_scenarios` primero, el estado estará desactualizado.
   *Mitigación*: si el directorio no existe o no hay `summary.json`, retornar `pipeline_status=RED` con `next_action=RE_RUN_RADIOGRAPHY`.

4. **Inconsistencia registry ↔ radiography**:
   Una capacidad marcada PIPELINE_CERTIFIED en el registry pero sin trace que la cubra (o viceversa) genera un hueco.
   *Mitigación*: sección `ambiguous_scenarios` y `next_action=REVIEW_REGISTRY` para gaps detectados.

5. **Crecimiento accidental del output**:
   Un desarrollador agrega un campo "útil" al JSON y empieza a usarse como dependencia aguas abajo, atrapando al arnés en un esquema no cerrado.
   *Mitigación*: test de snapshot estricto y regla "schema cerrado por enum".

6. **Confusión con CI**:
   El arnés puede confundirse con un gate de CI. El gate sigue siendo `python -m pymia.pipeline_radiography.run_scenarios` y su exit code. El arnés es observacional.
   *Mitigación*: documentar explícitamente que el arnés no se invoca desde `.github/workflows/smartpyme-radiography.yml` en M21. Si se quiere correr en CI, va en un job separado en un hito posterior.

7. **Tiempo de lectura en CI**:
   Si el arnés se corre dentro del job de CI, agregar latencia al feedback. En M21, no se corre en CI; corre local o en un job opcional futuro.

### 9.2 Riesgos falsos o exagerados

1. **"El arnés se va a convertir en dashboard"**: falso, mientras se limite a JSON y no haya UI, no es dashboard.
2. **"El arnés va a terminar llamando a Gemini"**: falso, no hay import de LLM y el test estático lo bloquea.
3. **"El arnés va a romper el dispatcher"**: falso, el arnés no importa ni llama al dispatcher.
4. **"El arnés necesita servicios externos"**: falso, todo es lectura de archivos locales.
5. **"El arnés va a re-correr el pipeline"**: falso, solo lee; quien corre es `run_scenarios`.

### 9.3 Riesgos residuales aceptables

- Que el orden de los campos JSON cambie entre versiones de Python: aceptable, el lector es tolerante a orden.
- Que `pyyaml` se actualice: aceptable, el reader ya lo usa.

---

## 10. Archivos a tocar (resumen)

### 10.1 Archivos nuevos

- `pymia/operational_harness/__init__.py`
- `pymia/operational_harness/harness.py`
- `pymia/operational_harness/sources.py`
- `pymia/operational_harness/consolidate.py`
- `pymia/operational_harness/schema.py`
- `tests/smartpyme/test_operational_harness.py`
- `docs/smartpyme/M21_MINIMAL_OPERATIONAL_HARNESS_CHECKPOINT.md` (al cierre, no en M21 audit)

### 10.2 Archivos a actualizar

- `docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md`: agregar una línea describiendo el arnés como "lector operacional del pipeline" (sin features nuevas).
- `docs/smartpyme/M20_MACHINE_READABLE_REGISTRY_CHECKPOINT.md`: actualizar "Próximos frentes" para mencionar M21 cerrado.

### 10.3 Archivos explícitamente NO a tocar

- `pymia/smartpyme/capabilities.yaml`
- `pymia/smartpyme/capability_registry.py`
- `pymia/pipeline_radiography/*` (todos los módulos existentes)
- `pymia/smartpyme/microservice_dispatcher.py`
- Cualquier plugin (`excel_diagnostic`, `supplier_duplicate_check`)
- `conversa-engine/`, `landing/`, `Pymia-memoria/`
- Nada de Telegram, PDF, HTML, UI

---

## 11. Veredicto final

```text
M21 Minimal Operational Harness = READY_FOR_GEMINI_REVIEW
```

### Causa

1. **Fuentes de datos completas y estables**: registry validado por `capability_registry.py`, summary.json producido por `run_scenarios.py`, trace.json producido por `report.py`. Todas tienen tests asociados.
2. **Reader existente**: `pymia/smartpyme/capability_registry.py` ya provee `load_registry()`, `list_capabilities()`, `is_pipeline_certified()`. El arnés lo consume, no lo reescribe.
3. **Alcance acotado y testeable**: consolidar en una función pura `consolidate(registry, summary, traces) -> dict` con 12 tests mínimos definidos.
4. **Sin superficies prohibidas**: el arnés no toca dispatcher, plugins, ni introduce IA. El test estático de imports lo garantiza.
5. **Output determinístico y cerrado**: schema con enums, sin texto libre, sin dependencias de timestamp para decidir.
6. **Riesgos acotables**: los 7 riesgos reales tienen mitigación concreta en este mismo documento.
7. **Alineado con el plan**: M20 y M19.8 ya están cerrados; M21 es el siguiente paso lógico (lector mínimo que prepare el terreno para una futura IA residente, sin serla).

### Próximos pasos para Codex

1. Crear los archivos listados en 10.1.
2. Implementar `sources.py` con loaders tipados.
3. Implementar `consolidate.py` como función pura con las reglas de 4.1.
4. Implementar `harness.py` como entrypoint CLI opcional: `python -m pymia.operational_harness.harness --output .pipeline_radiography/harness/status.json`.
5. Correr los 12 tests de 6.1.
6. Verificar que `test_harness_does_not_import_forbidden_modules` pasa.
7. Generar un run de humo: `python -m pymia.pipeline_radiography.run_scenarios --output-dir .tmp_radiography/m21` y luego el arnés contra ese output.
8. Crear `docs/smartpyme/M21_MINIMAL_OPERATIONAL_HARNESS_CHECKPOINT.md` con el cierre.

### Próximos frentes recomendados (no en M21)

- M22: integrar el arnés como job opcional en `.github/workflows/smartpyme-radiography.yml` (NO en M21; esto es un frente separado).
- M23: tercer plugin/capacidad solo después de consolidar CI + arnés.
- M24 (futuro, no ahora): IA residente que consuma el JSON del arnés. M21 no es ese hito.

---

## 12. Frase rectora

```text
El arnés no decide, no ejecuta, no sugiere con IA.
Lee, agrupa, semáforiza.
La inteligencia que venga después se apoyará en sus hechos, no en sus inferencias.
```
