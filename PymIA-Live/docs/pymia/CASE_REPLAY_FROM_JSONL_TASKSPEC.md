# Case Replay from JSONL TaskSpec

## Estado

```text
Estado: TASKSPEC_READY
Tipo: DOCUMENTARY_TASKSPEC
Runtime impact: NONE
Productive code impact: NONE
Fecha: 2026-06-17
```

## Propósito

Definir el primer slice de reconstrucción histórica de un caso PymIA-Live desde los registros JSONL persistidos por tenant.

El objetivo no es reejecutar diagnóstico ni recalcular resultados, sino reconstruir una vista trazable del caso ya ocurrido.

```text
JSONL persistidos
→ reconstrucción de caso
→ vista de auditoría / operador
```

## Motivación

PymIA-Live ya persiste registros separados por tenant:

```text
anamnesis.jsonl
investigations.jsonl
owner_answers.jsonl
evidence_requests.jsonl
evidences.jsonl
pipeline_runs.jsonl
```

La continuidad básica de traza ya fue cerrada, pero todavía falta una operación explícita para reconstruir un caso desde esos registros.

Este frente reduce fricción en auditoría, soporte y continuidad operativa: permite revisar qué ocurrió en un caso sin rerun y sin leer manualmente todos los JSONL.

## Evidencia de código leída

Archivos observados:

```text
pymia/smartpyme/storage.py
pymia/smartpyme/pipeline_registration.py
```

Hallazgos:

```text
storage.py
- ensure_tenant_storage() crea archivos JSONL por tenant.
- save_anamnesis_record() persiste anamnesis.jsonl.
- save_investigation_record() persiste investigations.jsonl.
- save_owner_answer_record() persiste owner_answers.jsonl.
- save_evidence_request_record() persiste evidence_requests.jsonl.
- save_evidence_record() persiste evidences.jsonl.

pipeline_registration.py
- register_pipeline_run_record() persiste pipeline_runs.jsonl.
- output_payload incluye tenant_id, intake_id, anamnesis_id, investigation_id, evidence_id, structured_evidence_status y blocked.
- metadata incluye anamnesis_id, investigation_id, owner_answer_id si existe, evidence_request_id si existe.
```

## Alcance del primer slice

El primer slice debe reconstruir un único caso por:

```text
tenant_id + intake_id
```

Debe leer registros JSONL existentes y producir un dict o dataclass de sólo lectura con:

```text
- tenant_id;
- intake_id;
- latest/anamnesis matching intake_id;
- latest/investigation matching intake_id;
- owner_answers matching intake_id;
- evidence_requests matching intake_id;
- evidences matching intake_id;
- pipeline_runs matching intake_id;
- selected latest pipeline run, si existe;
- trace_status;
- missing_links;
- warnings.
```

## No objetivos

Este frente no debe:

```text
- reejecutar vertical_pipeline;
- recalcular structured evidence;
- recalcular diagnostic_operator_summary;
- modificar JSONL;
- escribir nuevos registros;
- promover owner answers a evidence;
- alterar EvidenceRecord;
- alterar PipelineRunRecord;
- alterar renderer owner/operator;
- crear CRM o ficha empresa formal;
- usar LLM;
- usar Graphify en runtime.
```

## Definición propuesta

Crear una utilidad pura de lectura, por ejemplo:

```text
pymia/smartpyme/case_replay.py
```

con una API mínima:

```python
replay_case_from_jsonl(
    *,
    storage_dir: Path,
    tenant_id: str,
    intake_id: str,
) -> dict
```

Nombre alternativo aceptable:

```python
load_case_trace_from_jsonl(...)
```

La función debe ser determinística, sin efectos laterales y sin escribir archivos.

## Resultado esperado

Estructura mínima esperada:

```python
{
    "tenant_id": "...",
    "intake_id": "...",
    "status": "REPLAY_READY" | "PARTIAL_REPLAY" | "NOT_FOUND",
    "anamnesis_record": {...} | None,
    "investigation_record": {...} | None,
    "owner_answer_records": [...],
    "evidence_request_records": [...],
    "evidence_records": [...],
    "pipeline_run_records": [...],
    "latest_pipeline_run_record": {...} | None,
    "missing_links": [...],
    "warnings": [...],
}
```

## Criterios de estado

### REPLAY_READY

```text
Existe al menos:
- anamnesis_record;
- investigation_record;
- evidence_record;
- latest_pipeline_run_record.
```

### PARTIAL_REPLAY

```text
Existe parte de la traza, pero faltan uno o más enlaces esperados.
```

### NOT_FOUND

```text
No existe ningún registro para tenant_id + intake_id.
```

## Validaciones requeridas

La implementación futura debe validar:

```text
- tenant_id obligatorio;
- intake_id obligatorio;
- tenant_id sin traversal path;
- storage_dir existente o manejado como NOT_FOUND/PARTIAL según decisión explícita;
- líneas JSONL inválidas no deben romper toda la reconstrucción sin reportar warning;
- sólo se devuelven registros cuyo tenant_id e intake_id coinciden;
- no se mezclan tenants;
- si hay múltiples pipeline runs, se conserva la lista y se selecciona latest por created_at/run_id de forma documentada;
- missing_links registra relaciones esperadas ausentes.
```

## Acceptance tests requeridos

Antes de implementar, crear tests para:

```text
1. replay returns NOT_FOUND when tenant storage does not exist.
2. replay returns REPLAY_READY after a vertical slice run with persisted JSONL.
3. replay includes anamnesis, investigation, evidence and pipeline run for same intake_id.
4. replay includes owner answers when present.
5. replay includes evidence requests when present.
6. replay does not mix records from another tenant.
7. replay does not mix records from another intake_id.
8. replay reports PARTIAL_REPLAY when pipeline_runs.jsonl is missing or empty but other records exist.
9. replay reports warnings for malformed JSONL lines and continues reading valid lines.
10. replay is read-only: no JSONL file content changes after replay.
```

## Archivos permitidos para implementación futura

```text
pymia/smartpyme/case_replay.py
tests/smartpyme/test_case_replay.py
```

Opcional, sólo si se decide exponer CLI después del primer slice:

```text
pymia/cli/case_replay.py
tests/e2e/test_case_replay_cli.py
```

## Archivos que no deben tocarse

```text
pymia/diagnostic_core/
pymia/contracts/evidence_v1.py
pymia/contracts/pipeline_run_v1.py
pymia/smartpyme/evidence.py
pymia/smartpyme/pipeline_registration.py
pymia/rendering/owner_markdown_renderer.py
pymia/application/vertical_pipeline.py
```

## Riesgos

```text
- Confundir replay con rerun.
- Recalcular evidencia o diagnóstico en lugar de reconstruir traza.
- Mezclar tenants o intake_ids.
- Asumir orden JSONL sin criterio explícito.
- Fallar ante líneas corruptas en JSONL.
- Convertir replay en herramienta de reporting owner-facing antes de tiempo.
```

## Stop conditions

Detener implementación si:

```text
- se necesita modificar contratos existentes;
- se necesita tocar diagnostic_core;
- se necesita escribir nuevos JSONL durante replay;
- no está claro cómo seleccionar latest pipeline run;
- los tests no protegen no mezcla de tenant/intake;
- aparece intención de reejecutar pipeline desde replay;
- se intenta commitear tooling local o graphify-out/.
```

## Validación futura esperada

Validación mínima:

```text
pytest PymIA-Live/tests/smartpyme/test_case_replay.py -q --tb=short
```

Validación ampliada opcional:

```text
pytest PymIA-Live/tests/smartpyme/test_case_replay.py PymIA-Live/tests/e2e/test_vertical_slice_cli.py -q --tb=short
```

## Estado git esperado

Dirty local conocido y ajeno al frente:

```text
?? .agents/
?? .graphifyignore
?? .opencode/
?? graphify-out/
```

No pertenecen al frente y no deben incluirse en commits.

## Veredicto

```text
CASE_REPLAY_FROM_JSONL = TASKSPEC_READY
IMPLEMENTATION = NOT_STARTED
REQUIRES_EXTERNAL_AUDIT_BEFORE_CODE = YES
```
