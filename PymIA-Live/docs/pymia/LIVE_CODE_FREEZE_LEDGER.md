# LIVE_CODE_FREEZE_LEDGER

## Estado

`ACTIVE_FREEZE_LEDGER`

## Fecha

2026-06-18

## Propósito

Registrar en un documento versionado las auditorías recientes de módulos vivos para que no queden perdidas en el chat.

Este ledger **no crea resultados nuevos**. Sólo consolida cierres ya existentes en commits, checkpoints versionados o auditorías cerradas en esta línea de trabajo.

## Tabla de módulos vivos auditados

| Módulo | Archivo | Decisión | Veredicto | Commit relacionado | Fuente de evidencia |
|---|---|---|---|---|---|
| Document ingestion | `PymIA-Live/tools/document_ingestion.py` | `FROZEN` | `PASS` | `2d0e53e` | checkpoint/piloto histórico |
| Structured evidence builder | `PymIA-Live/pymia/smartpyme/structured_evidence_builder.py` | `FROZEN` | `PASS` | `f4494a3` | checkpoint histórico |
| Vertical pipeline | `PymIA-Live/pymia/application/vertical_pipeline.py` | `FROZEN` | `PASS` | `2606841` | auditoría de frontera cerrada |
| OCF snapshot | `PymIA-Live/pymia/smartpyme/ocf_snapshot.py` | `FIXED` | `PASS` | `f372be5` | fix mínimo auditado |

## Estado por módulo

### 1. `document_ingestion.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/tools/document_ingestion.py` |
| decisión | `FROZEN` |
| veredicto | `PASS` |
| commit relacionado | `2d0e53e feat(pymia-live): preserve evidence refs for computed variables` |
| tests ejecutados | Evidencia histórica upstream registrada en `docs/smartpyme/pilots/M31P-003.md`: `python -m pytest tests/test_excel_evidence.py tests/test_document_ingestion.py -q` → `12 passed in 29.41s` |
| riesgos residuales | Superficie amplia de curación/exportación; una deriva en artefactos, metadata o shape de `StructuredEvidence` puede propagarse aguas abajo sin que el freeze documental la capture solo. |
| regla de reapertura | Reabrir si cambia la exportación de `StructuredEvidence`, la persistencia de artefactos, la metadata principal de ingesta o el handoff hacia `structured_evidence_builder.py`. |

### 2. `structured_evidence_builder.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/structured_evidence_builder.py` |
| decisión | `FROZEN` |
| veredicto | `PASS` |
| commit relacionado | `f4494a3 feat(pymia-live): initial validated extraction` |
| tests ejecutados | Evidencia histórica upstream registrada en `docs/pymia/M41_CORE_DELIVERY_REPLAY_CHECKPOINT.md`: `python -m pytest tests/orchestration/test_graph.py tests/smartpyme/test_structured_evidence_builder.py tests/diagnosticcore/test_core_audit_delivery_bridge.py -q --basetemp .tmp_pytest_m41` → `36 passed in 15.85s` |
| riesgos residuales | Depende del contrato de `document_ingestion.py` y del shape de `intake_record`; una deriva en `formula_ids`, variables computadas o metadata puede alterar el contexto estructurado sin mover esta frontera. |
| regla de reapertura | Reabrir si cambia la extracción de `formula_ids`, la delegación a `build_structured_evidence_from_xlsx`, o la forma del payload `structured_evidence` entregado al flujo vivo. |

### 3. `vertical_pipeline.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/application/vertical_pipeline.py` |
| decisión | `FROZEN` |
| veredicto | `PASS` |
| commit relacionado | `2606841 refactor(pymia-live): extract owner resolution step` |
| tests ejecutados | `python -m pytest tests/application/test_vertical_pipeline_boundary.py -q`; `python -m pytest tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py tests/smartpyme/test_ocf_snapshot.py -q` |
| riesgos residuales | Sigue siendo el mayor concentrador de deriva funcional: lectura de Excel, evidencia, owner report, render, pipeline run, adapter diagnóstico y question alignment convergen ahí. |
| regla de reapertura | Reabrir si cambian las claves públicas de `build_pipeline()`, la trazabilidad mínima de `build_report()`, los imports prohibidos o la delegación de `build_markdown()` al renderer. |

### 4. `ocf_snapshot.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/ocf_snapshot.py` |
| decisión | `FIXED` |
| veredicto | `PASS` |
| commit relacionado | `f372be5 fix(pymia-live): include hashes in ocf snapshot refs` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_ocf_snapshot.py -q`; `python -m pytest tests/smartpyme/test_ocf_snapshot.py tests/smartpyme/test_case_replay.py -q`; `python -m pytest tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py tests/smartpyme/test_ocf_snapshot.py -q` |
| riesgos residuales | El snapshot puede quedar desalineado si el replay o los records JSONL agregan nuevos refs y nadie los copia explícitamente. |
| regla de reapertura | Reabrir si cambian `run_refs`, `evidence_refs`, el contrato de replay, `heuristic_ratio`, o si el snapshot deja de ser read-only. |

## Cadena viva auditada

```text
Excel
→ document_ingestion.py
→ structured_evidence_builder.py
→ vertical_pipeline.py
→ ocf_snapshot.py
```

## Regla de cierre

> “Una auditoría sólo cuenta como cerrada si queda registrada en este ledger o en un checkpoint versionado.”

## Guardrail sobre untracked ajenos

Los siguientes untracked ajenos al ledger **no deben tocarse, agregarse ni normalizarse** desde esta línea de auditoría:

- `.agents/`
- `.graphifyignore`
- `.opencode/`
- `graphify-out/`
- docs no relacionados
- `ORGANIZATIONAL_CASE_FILE_V1_CONCEPT.md` si ya existe como untracked

## Lectura correcta de este ledger

- `FROZEN / PASS` significa frontera cerrada sin autorizar refactor abierto.
- `FIXED / PASS` significa corrección mínima aplicada y validada, no rediseño.
- Este ledger **no reemplaza** tests, checkpoints ni commits; los indexa.
- Si un resultado no está en commit, checkpoint o este ledger, no cuenta como cierre certificado.
