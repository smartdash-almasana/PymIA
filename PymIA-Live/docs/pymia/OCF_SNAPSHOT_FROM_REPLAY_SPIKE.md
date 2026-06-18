# OCF Snapshot from Replay Spike

## Estado

```text
Estado: SPIKE_TASKSPEC_READY
Tipo: DOC_ONLY / SPIKE_TASKSPEC
Runtime impact: NONE
Productive code impact: NONE
Implementación: NOT_STARTED
Fecha: 2026-06-18
Basado en: ORGANIZATIONAL_CASE_FILE_V1_CONCEPT.md, case_replay.py (271 líneas),
           test_case_replay.py (351 líneas), evidence.py (EvidenceRecord),
           evidence_v1.py (StructuredEvidence), pipeline_run_v1.py (PipelineRunRecord),
           PRE_TASKSPEC_RESOLUTION_FOUNDATIONAL_CONTRACTS.md
```

## Contexto

PymIA-Live ya posee un pipeline vivo que registra evidencia, anamnesis, investigation, owner answers, evidence requests, pipeline runs, owner/operator output y replay desde JSONL. El diseño de producto define el OrganizationalCaseFile como el tejido conectivo del sistema, pero existe el riesgo de crear una arquitectura paralela separada del pipeline real.

Este spike prueba si la ficha organizacional puede nacer desde lo vivo — no desde contratos especulativos — usando exclusivamente los registros que el pipeline ya produce y persiste. La estrategia de transición es envoltura epistémica, no reemplazo.

> PymIA no migra por reemplazo. PymIA migra por lectura, envoltura y composición progresiva de lo vivo.

## Problema

Crear contratos fundacionales (EvidenceArtifact V1, EpistemicState V1, SalesChannelTaxonomy V1, MicroserviceResult V1, etc.) antes de probar que la ficha puede componerse desde la traza viva presenta los siguientes riesgos:

- **Sobreabstracción**: diseñar EpistemicState con 10 estados sin haber observado transiciones reales en casos vivos.
- **Arquitectura paralela**: los contratos definidos en abstracto pueden no encajar con lo que el pipeline realmente produce, generando fricción de integración posterior.
- **Duplicación inadvertida**: crear artefactos que duplican funcionalidad de EvidenceRecord, StructuredEvidence o PipelineRunRecord sin darse cuenta.
- **Deuda de documentación**: 6-7 contratos sin uso inmediato son deuda de mantenimiento, no arquitectura.
- **Demora de validación**: la hipótesis "la ficha nace de lo vivo" queda sin probar durante semanas mientras se definen contratos.

## Objetivo del spike

Construir una vista mínima de ficha organizacional desde `replay_case_from_jsonl(...)`, usando exclusivamente registros existentes y sin modificar runtime.

La pregunta del spike:

> ¿Puede la `OrganizationalCaseFile` nacer como una lectura/snapshot de los registros vivos actuales, sin duplicar contratos y sin romper pipeline?

### Hipótesis bajo prueba

- `replay_case_from_jsonl()` expone suficientes datos para componer una vista de caso mínima pero útil.
- La estructura de `EvidenceRecord` + `StructuredEvidence.computed_variables` permite identificar variables disponibles y faltantes.
- Las referencias cruzadas entre registros (evidence_ids, run_id, answer_id, request_id) permiten trazabilidad sin nuevos contratos.
- El snapshot revela qué semántica falta, informando qué contratos fundacionales son realmente necesarios y cuáles pueden esperar.

### Timebox

2 días máximo desde el inicio de la implementación. Si en 2 días no se produce un snapshot útil con un caso real, el spike se detiene y se reportan los hallazgos.

## No objetivos

El spike no persigue ni debe ser confundido con:

- implementar `OrganizationalCaseFile V1` final;
- crear `EvidenceArtifact V1`;
- crear `EpistemicState V1` como contrato formal (strings simples aceptables);
- crear `MicroserviceResult V1`;
- crear `EvidenceReconciliation V1`;
- crear `MarketplaceEvidence V1`;
- crear `SalesChannelTaxonomy` formal;
- crear `Excel Treatment Lab`;
- crear Mercado Libre plugin;
- crear storage nuevo (bases, archivos, JSONL adicional);
- modificar JSONL existente (escritura);
- ejecutar diagnóstico;
- recalcular structured evidence;
- tocar renderer (`pymia/rendering/`);
- tocar `vertical_pipeline.py`;
- tocar `diagnostic_core/`;
- crear owner-facing renderer nuevo;
- convertirse en CRM/ERP;
- reemplazar `EvidenceRecord`;
- reemplazar `StructuredEvidence`;
- reemplazar `PipelineRunRecord`;
- reemplazar `replay_case_from_jsonl()`;
- persistir el snapshot.

## Fuente de datos permitida

El spike lee exclusivamente el output de `replay_case_from_jsonl(...)`:

```python
replay = replay_case_from_jsonl(
    storage_dir=storage_dir,
    tenant_id=tenant_id,
    intake_id=intake_id,
)
```

Desde ese output puede extraer:

- `tenant_id`
- `intake_id`
- `status` (NOT_FOUND / PARTIAL_REPLAY / REPLAY_READY)
- `anamnesis_record` → dolor declarado, identidad del caso
- `investigation_record` → línea investigativa activa
- `owner_answer_records` → respuestas del dueño, preguntas respondidas
- `evidence_request_records` → evidencia solicitada, razones
- `evidence_records` → evidencia recibida, tipos, source_kind
- `pipeline_run_records` → ejecuciones, steps_executed, evidence_ids, metadata
- `latest_pipeline_run_record` → estado más reciente, output_artifact_id
- `missing_links` → relaciones rotas entre registros
- `warnings` → anomalías detectadas en lectura

Adicionalmente, puede inspeccionar el contenido de:

- `latest_pipeline_run_record.metadata` si contiene `structured_summary` o variables reportadas.
- `evidence_records[].metadata` si contiene claves semánticas.
- `owner_answer_records[].raw_owner_answer` y `question_ref` para extraer variables declaradas.
- `anamnesis_record` y `investigation_record` para extraer preguntas e incógnitas abiertas.

No debe leer:

- archivos Excel/PDF/CSV originales;
- bases de datos externas;
- APIs externas;
- storage fuera del directorio del tenant.

## Snapshot mínimo propuesto

```python
{
    # Identidad
    "case_id": str,                        # intake_id como case_id
    "tenant_id": str,
    "intake_id": str,

    # Estado del snapshot
    "case_status": "SNAPSHOT_READY"        # cuando replay es REPLAY_READY
                   | "PARTIAL_SNAPSHOT"    # cuando replay es PARTIAL_REPLAY
                   | "NOT_FOUND",          # cuando replay es NOT_FOUND

    # Referencias a registros origen
    "evidence_refs": [
        {
            "evidence_id": str,
            "evidence_type": str,
            "source_kind": str,
            "status": str,
            "trace_ref": f"evidences.jsonl:{evidence_id}"
        }
    ],
    "run_refs": [
        {
            "run_id": str,
            "pipeline_name": str,
            "status": str,
            "trace_ref": f"pipeline_runs.jsonl:{run_id}"
        }
    ],
    "owner_answer_refs": [
        {
            "answer_id": str,
            "question_ref": str,
            "answer_kind": str,
            "trace_ref": f"owner_answers.jsonl:{answer_id}"
        }
    ],
    "evidence_request_refs": [
        {
            "request_id": str,
            "requested_evidence": list[str],
            "status": str,
            "trace_ref": f"evidence_requests.jsonl:{request_id}"
        }
    ],

    # Variables
    "available_variables": [
        {
            "variable": str,               # nombre de variable
            "source": "structured_evidence" | "owner_declared" | "pipeline_output" | "inferred",
            "value": float | str | None,   # valor si está disponible
            "trace_ref": str               # a qué registro origen pertenece
        }
    ],
    "missing_variables": [
        {
            "variable": str,               # variable necesaria no encontrada
            "reason": str,                 # por qué se necesita
            "requested_in": str | None     # evidence_request_id si fue solicitada
        }
    ],

    # Incógnitas y próximos pasos
    "open_unknowns": [
        {
            "unknown": str,
            "type": "missing_evidence" | "unanswered_question" | "uncalculated_formula",
            "source_ref": str | None
        }
    ],
    "next_questions": [
        str                                 # preguntas que emergen del estado actual
    ],

    # Trazabilidad
    "trace_refs": {
        "anamnesis_id": str | None,
        "investigation_id": str | None,
        "latest_pipeline_run_id": str | None,
    },

    # Advertencias
    "warnings": list[str]
}
```

### Notas sobre los campos

1. **evidence_refs**: se compone desde `replay["evidence_records"]`. Cada registro ofrece `evidence_id`, `evidence_type`, `source_kind`, `status`. No se necesita EvidenceArtifact V1 para referenciar evidencia.

2. **available_variables**: se extrae de tres fuentes posibles en orden de prioridad:
   - `latest_pipeline_run_record.metadata` si contiene variables reportadas;
   - `owner_answer_records` donde `question_ref` indique una variable organizacional;
   - `evidence_records[].metadata` si contiene claves como `detected_variables`.
   Si ninguna fuente tiene variables, la lista puede estar vacía — eso es información válida sobre la carencia actual del pipeline.

3. **missing_variables**: se infiere contrastando `evidence_request_records[].requested_evidence` con `evidence_records`. Si se pidió "ventas_del_periodo" y no hay evidencia que lo cubra, aparece como missing.

4. **open_unknowns**: se compone desde:
   - `investigation_record.investigation_goal` o mensaje de anamnesis;
   - `evidence_request_records[].request_reason`;
   - owner answers donde `raw_owner_answer` exprese incertidumbre ("no sé", "no estoy seguro").

5. **next_questions**: emergen de `open_unknowns`. Si hay "falta evidencia de ventas", la siguiente pregunta puede ser "¿Podés subir un Excel de ventas?".

6. **warnings**: se heredan de `replay["warnings"]` más cualquier advertencia que el snapshot detecte al componer la vista.

### Invariantes del snapshot

- Cada variable en `available_variables` DEBE tener un `trace_ref` que permita ubicar el registro de origen.
- `case_status` NUNCA es `SNAPSHOT_READY` si `replay["status"]` es `NOT_FOUND`.
- El snapshot NO escribe JSONL, NO persiste, NO modifica registros existentes.
- Si no hay variables disponibles, `available_variables` es `[]` (no miente, no inventa).

## Criterios de éxito

El spike se considera exitoso cuando:

1. **Dado un intake_id real** con al menos 5 registros JSONL (anamnesis + investigation + owner_answers + evidence + pipeline_runs), `ocf_snapshot.compose_ocf_snapshot(...)` produce un snapshot con:
   - `case_id`, `tenant_id`, `intake_id`, `case_status` poblados;
   - `evidence_refs` ≥ 1 entrada con `trace_ref` trazable;
   - `run_refs` ≥ 1 entrada con `trace_ref` trazable;
   - `owner_answer_refs` ≥ 1 entrada (si hay owner answers);
   - `available_variables` ≥ 8 entradas (si existe evidence con variables computadas);
   - `open_unknowns` ≥ 2 entradas específicas (no genéricas);
   - `warnings` contiene solo advertencias genuinas.

2. **El snapshot es read-only**: `_snapshot_tree(storage_dir)` antes y después es idéntico.

3. **No modifica ningún archivo** fuera de `pymia/smartpyme/ocf_snapshot.py` y `tests/smartpyme/test_ocf_snapshot.py`.

4. **La salida es inspeccionable** por un operador humano sin recurrir a código fuente.

## Criterios de fracaso

El spike se considera fallido o insuficiente si:

1. `available_variables` < 5 para un caso con Excel subido y pipeline run exitoso con `COMPLETED`.
2. Las variables listadas no tienen trazabilidad (`trace_ref` ausente o incorrecto).
3. `open_unknowns` está vacío o contiene solo incógnitas genéricas como "falta información".
4. El snapshot requiere modificar `case_replay.py`, `storage.py`, `evidence.py` o cualquier archivo prohibido para funcionar.
5. El snapshot no puede responder la pregunta "¿qué variables existen y dónde se originan?".

## Implementación esperada

### API propuesta

```python
def compose_ocf_snapshot(
    *,
    storage_dir: Path,
    tenant_id: str,
    intake_id: str,
) -> dict:
    """Compone un snapshot read-only de caso organizacional desde replay JSONL.
    
    Args:
        storage_dir: directorio raíz de storage JSONL.
        tenant_id: identificador del tenant.
        intake_id: identificador del intake.
    
    Returns:
        dict con la estructura de snapshot mínimo propuesto.
    
    Invariantes:
        - Read-only: no escribe JSONL, no modifica storage.
        - No depende de contratos fundacionales (EvidenceArtifact, EpistemicState, etc.).
        - Cada variable tiene trace_ref al registro origen.
    """
    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )
    # ... compose snapshot from replay output ...
```

### Lógica esperada

1. Llamar a `replay_case_from_jsonl(...)`.
2. Derivar `case_status` desde `replay["status"]`:
   - `NOT_FOUND` → `NOT_FOUND`
   - `PARTIAL_REPLAY` → `PARTIAL_SNAPSHOT`
   - `REPLAY_READY` → `SNAPSHOT_READY`
3. Componer `evidence_refs` iterando `replay["evidence_records"]`.
4. Componer `run_refs` iterando `replay["pipeline_run_records"]`.
5. Componer `owner_answer_refs` iterando `replay["owner_answer_records"]`.
6. Componer `evidence_request_refs` iterando `replay["evidence_request_records"]`.
7. Extraer `available_variables`:
   - Intentar desde `latest_pipeline_run_record["metadata"]` si contiene claves como `structured_summary` o `computed_variables`.
   - Intentar desde `owner_answer_records[].question_ref` normalizado.
8. Componer `missing_variables` contrastando `evidence_request_records[].requested_evidence` con `evidence_records[].evidence_type`.
9. Componer `open_unknowns` desde `investigation_record` y evidencia faltante.
10. Componer `next_questions` desde `open_unknowns`.
11. Ensamblar `trace_refs` con IDs de anamnesis, investigation y última pipeline run.
12. Propagar `warnings` desde `replay["warnings"]`.

### Archivos

| Archivo | Acción |
|---------|--------|
| `PymIA-Live/pymia/smartpyme/ocf_snapshot.py` | NUEVO. Implementación principal (~200 líneas). |
| `PymIA-Live/tests/smartpyme/test_ocf_snapshot.py` | NUEVO. Tests del snapshot (~8-11 tests). |
| Este documento | SpikeSpec de referencia. |

### Dependencias

- `from pymia.smartpyme.case_replay import replay_case_from_jsonl` (lectura, NO modificada).
- `from pathlib import Path` (trazado de caminos).
- `from typing import Any` (tipado).
- Sin dependencias nuevas. Sin Pydantic. Sin BaseModel. Sin nuevos contratos.

## Flujo del spike

```text
1.   LEER este SpikeSpec
2.   CREAR ocf_snapshot.py con compose_ocf_snapshot()
3.   CREAR test_ocf_snapshot.py
       - test_snapshot_not_found
       - test_snapshot_partial
       - test_snapshot_ready
       - test_snapshot_evidence_refs_traced
       - test_snapshot_run_refs_traced
       - test_snapshot_owner_answer_refs_traced
       - test_snapshot_evidence_request_refs_traced
       - test_snapshot_available_variables_from_pipeline_metadata
       - test_snapshot_missing_variables_from_evidence_requests
       - test_snapshot_open_unknowns_from_investigation
       - test_snapshot_is_read_only
4.   EJECUTAR pytest contra test_ocf_snapshot.py
       → TODOS GREEN (evidencia de que el spike funciona)
5.   EVALUAR el snapshot contra un caso real (si existe JSONL de prueba)
       → Registrar available_variables, missing_variables, open_unknowns
6.   REPORTAR hallazgos en documento separado (no requerido en este SpikeSpec)
7.   DECIDIR: ¿qué contratos fundacionales necesita el OCF V1 según lo que el spike reveló?
```

## STOP conditions

```text
STOP si el spike modifica:
  - case_replay.py
  - storage.py
  - evidence.py
  - owner_answer.py
  - evidence_request.py
  - contracts/* (evidence_v1.py, pipeline_run_v1.py)
  - diagnostic_core/**
  - rendering/**
  - vertical_pipeline.py
  - PRE_TASKSPEC_RESOLUTION_FOUNDATIONAL_CONTRACTS.md

STOP si el spike crea storage nuevo (base de datos, JSONL, archivos de estado).

STOP si el spike ejecuta diagnóstico, recalcula variables o escribe JSONL.

STOP si el spike excede 2 días sin producir snapshot útil.

STOP si el spike depende de un contrato fundacional que no existe (EvidenceArtifact, EpistemicState, MicroserviceResult, etc.).
```

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| El snapshot es pobre porque el pipeline actual no expone variables semánticas | Eso es información: revela que el pipeline necesita exponer variables antes de que OCF V1 funcione. El spike no fracasa, ilumina. |
| Se trata el snapshot como el OCF V1 definitivo | Documentado explícitamente como spike. El TaskSpec del OCF V1 futuro debe reemplazar el snapshot. |
| El snapshot se vuelve complejo y muta de read-only a read-write | Timebox de 2 días evita creep. Si se necesita escritura, se detiene el spike y se inicia un TaskSpec de OCF V1 formal. |
| Dependencia silenciosa de contratos que no existen | `trace_ref` como string simple evita necesidad de EvidenceArtifact V1. Si el snapshot requiere tipos formales, ese hallazgo se reporta. |

## Relación con PRE_TASKSPEC_RESOLUTION

Este spike NO invalida `PRE_TASKSPEC_RESOLUTION_FOUNDATIONAL_CONTRACTS.md`. Lo modifica insertando este paso antes del Phase 1:

```text
0.   spike(pymia-live): add ocf snapshot from replay experiment    ← NUEVO
1.   docs(pymia-live): define product universe and service depth model
2.   feat(pymia-live): add sales channel taxonomy v1 contract
... (resto del plan inalterado)
```

El spike produce evidencia que informa qué contratos son realmente necesarios al llegar a Phase 5 (OCF V1). Si el spike revela que ciertos contratos pueden esperar, se documenta en una actualización de la resolución.

## Commit esperado

```text
spike(pymia-live): add ocf snapshot from replay experiment

Read-only snapshot composed from live JSONL replay.
Validates hypothesis that case file can be born from existing
traces without new contracts or storage.

SPIKESPEC: PymIA-Live/docs/pymia/OCF_SNAPSHOT_FROM_REPLAY_SPIKE.md
```
