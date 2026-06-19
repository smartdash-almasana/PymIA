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
| Owner-facing report | `PymIA-Live/pymia/smartpyme/owner_facing_report.py` | `FREEZE_OWNER_FACING_REPORTING` | `PASS` | `731e580` | auditoría de frontera cerrada |
| Owner output | `PymIA-Live/pymia/smartpyme/owner_output.py` | `FREEZE_OWNER_FACING_REPORTING` | `PASS` | `eca07e8` | auditoría de frontera cerrada |
| Owner markdown renderer | `PymIA-Live/pymia/rendering/owner_markdown_renderer.py` | `FREEZE_OWNER_FACING_REPORTING` | `PASS` | `1a9b58a` | auditoría de frontera cerrada |
| Question resolution | `PymIA-Live/pymia/smartpyme/question_resolution.py` | `FREEZE_OWNER_FACING_REPORTING` | `PASS` | `3816fb0` | auditoría de frontera cerrada |
| Question alignment gate | `PymIA-Live/pymia/smartpyme/question_alignment_gate.py` | `FREEZE_OWNER_FACING_REPORTING` | `PASS` | `af59465` | auditoría de frontera cerrada |
| Pipeline registration | `PymIA-Live/pymia/smartpyme/pipeline_registration.py` | `FREEZE_REGISTRATION_STORAGE` | `PASS` | `faf9008` | auditoría de frontera cerrada |
| Storage | `PymIA-Live/pymia/smartpyme/storage.py` | `FREEZE_REGISTRATION_STORAGE` | `PASS` | `35538b4` | auditoría de frontera cerrada |
| Case replay | `PymIA-Live/pymia/smartpyme/case_replay.py` | `FREEZE_CASE_REPLAY` | `PASS` | `902b0dd` | auditoría de frontera cerrada |
| OCF snapshot | `PymIA-Live/pymia/smartpyme/ocf_snapshot.py` | `FIXED` | `PASS` | `f372be5` | fix mínimo auditado |
| Service depth routing | `PymIA-Live/pymia/smartpyme/service_depth.py` | `FROZEN` | `PASS` | `current HEAD` | auditoría de routing proporcional |

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

### 4. `owner_facing_report.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/owner_facing_report.py` |
| decisión | `FREEZE_OWNER_FACING_REPORTING` |
| veredicto | `PASS` |
| commit relacionado | `731e580 refactor(pymia-live): externalize owner report warnings` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_owner_facing_report.py tests/smartpyme/test_owner_output_boundary.py tests/rendering/test_owner_markdown_renderer_boundary.py tests/smartpyme/test_question_resolution_boundary.py tests/smartpyme/test_question_alignment_gate.py tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py tests/smartpyme/test_ocf_snapshot.py -q` |
| riesgos residuales | Posible discrepancia futura entre labels/copy declarativos y claves dinámicas de catálogo/reconciliación. Riesgo mitigado por fallbacks existentes. |
| regla de reapertura | Reabrir sólo ante cambio en contratos de copy/labels, bug real de rendering owner-facing, nueva audiencia de reporte, cambio explícito de owner question flow, o integración futura con `service_depth` o packs que afecte presentación. |

### 5. `owner_output.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/owner_output.py` |
| decisión | `FREEZE_OWNER_FACING_REPORTING` |
| veredicto | `PASS` |
| commit relacionado | `eca07e8 refactor(pymia-live): extract owner simple output builder` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_owner_facing_report.py tests/smartpyme/test_owner_output_boundary.py tests/rendering/test_owner_markdown_renderer_boundary.py tests/smartpyme/test_question_resolution_boundary.py tests/smartpyme/test_question_alignment_gate.py tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py tests/smartpyme/test_ocf_snapshot.py -q` |
| riesgos residuales | Posible discrepancia futura entre labels/copy declarativos y claves dinámicas de catálogo/reconciliación. Riesgo mitigado por fallbacks existentes. |
| regla de reapertura | Reabrir sólo ante cambio en contratos de copy/labels, bug real de rendering owner-facing, nueva audiencia de reporte, cambio explícito de owner question flow, o integración futura con `service_depth` o packs que afecte presentación. |

### 6. `owner_markdown_renderer.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/rendering/owner_markdown_renderer.py` |
| decisión | `FREEZE_OWNER_FACING_REPORTING` |
| veredicto | `PASS` |
| commit relacionado | `1a9b58a feat(pymia-live): split owner and operator markdown views` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_owner_facing_report.py tests/smartpyme/test_owner_output_boundary.py tests/rendering/test_owner_markdown_renderer_boundary.py tests/smartpyme/test_question_resolution_boundary.py tests/smartpyme/test_question_alignment_gate.py tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py tests/smartpyme/test_ocf_snapshot.py -q` |
| riesgos residuales | Posible discrepancia futura entre labels/copy declarativos y claves dinámicas de catálogo/reconciliación. Riesgo mitigado por fallbacks existentes. |
| regla de reapertura | Reabrir sólo ante cambio en contratos de copy/labels, bug real de rendering owner-facing, nueva audiencia de reporte, cambio explícito de owner question flow, o integración futura con `service_depth` o packs que afecte presentación. |

### 7. `question_resolution.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/question_resolution.py` |
| decisión | `FREEZE_OWNER_FACING_REPORTING` |
| veredicto | `PASS` |
| commit relacionado | `3816fb0 refactor(pymia-live): extract question resolution from CLI` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_owner_facing_report.py tests/smartpyme/test_owner_output_boundary.py tests/rendering/test_owner_markdown_renderer_boundary.py tests/smartpyme/test_question_resolution_boundary.py tests/smartpyme/test_question_alignment_gate.py tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py tests/smartpyme/test_ocf_snapshot.py -q` |
| riesgos residuales | Posible discrepancia futura entre labels/copy declarativos y claves dinámicas de catálogo/reconciliación. Riesgo mitigado por fallbacks existentes. |
| regla de reapertura | Reabrir sólo ante cambio en contratos de copy/labels, bug real de rendering owner-facing, nueva audiencia de reporte, cambio explícito de owner question flow, o integración futura con `service_depth` o packs que afecte presentación. |

### 8. `question_alignment_gate.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/question_alignment_gate.py` |
| decisión | `FREEZE_OWNER_FACING_REPORTING` |
| veredicto | `PASS` |
| commit relacionado | `af59465 refactor(pymia-live): consume declarative question alignment contract` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_owner_facing_report.py tests/smartpyme/test_owner_output_boundary.py tests/rendering/test_owner_markdown_renderer_boundary.py tests/smartpyme/test_question_resolution_boundary.py tests/smartpyme/test_question_alignment_gate.py tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py tests/smartpyme/test_ocf_snapshot.py -q` |
| riesgos residuales | Posible discrepancia futura entre labels/copy declarativos y claves dinámicas de catálogo/reconciliación. Riesgo mitigado por fallbacks existentes. |
| regla de reapertura | Reabrir sólo ante cambio en contratos de copy/labels, bug real de rendering owner-facing, nueva audiencia de reporte, cambio explícito de owner question flow, o integración futura con `service_depth` o packs que afecte presentación. |

Cobertura auditada:

- `owner_facing_report.py` construye reporte owner-facing sin diagnóstico.
- `owner_output.py` simplifica salida sin inventar hallazgos.
- `owner_markdown_renderer.py` renderiza Markdown sin decidir estado de caso.
- `question_resolution.py` traduce referencias y evidencia solicitada sin ejecutar diagnóstico.
- `question_alignment_gate.py` alinea preguntas sin reescribir diagnóstico.
- Ninguno escribe storage ni crea records.
- Ninguno importa `vertical_pipeline.py`.
- Frontera datos del caso ≠ presentación ≠ diagnóstico ≠ persistencia preservada.

### 9. `pipeline_registration.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/pipeline_registration.py` |
| decisión | `FREEZE_REGISTRATION_STORAGE` |
| veredicto | `PASS` |
| commit relacionado | `faf9008 refactor(pymia-live): realign pipeline trace identity` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_anamnesis_storage.py tests/smartpyme/test_evidence_request_storage.py tests/smartpyme/test_investigation_storage.py tests/smartpyme/test_owner_answer_storage.py tests/smartpyme/test_pipeline_registration_boundary.py tests/smartpyme/test_case_replay.py tests/smartpyme/test_ocf_snapshot.py tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py -q` |
| riesgos residuales | `pipeline_registration.py` persiste `pipeline_runs.jsonl` directamente con helper local en vez de delegar en `storage.py`. No rompe comportamiento actual, pero debe reabrirse si se amplía persistencia, si aparece adapter DB, o si se formaliza `save_pipeline_run_record`. |
| regla de reapertura | Reabrir sólo ante nuevo backend de persistencia, nuevo tipo de record operativo, cambio de schema JSONL, bug real de replay/OCF, o decisión explícita de extraer `save_pipeline_run_record`. |

### 10. `storage.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/storage.py` |
| decisión | `FREEZE_REGISTRATION_STORAGE` |
| veredicto | `PASS` |
| commit relacionado | `35538b4 feat(pymia-live): add evidence request record contract and storage` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_anamnesis_storage.py tests/smartpyme/test_evidence_request_storage.py tests/smartpyme/test_investigation_storage.py tests/smartpyme/test_owner_answer_storage.py tests/smartpyme/test_pipeline_registration_boundary.py tests/smartpyme/test_case_replay.py tests/smartpyme/test_ocf_snapshot.py tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py -q` |
| riesgos residuales | La frontera queda parcialmente asimétrica porque `pipeline_registration.py` persiste `pipeline_runs.jsonl` con helper local en vez de delegar en `storage.py`. No rompe comportamiento actual, pero debe reabrirse si se amplía persistencia, si aparece adapter DB, o si se formaliza `save_pipeline_run_record`. |
| regla de reapertura | Reabrir sólo ante nuevo backend de persistencia, nuevo tipo de record operativo, cambio de schema JSONL, bug real de replay/OCF, o decisión explícita de extraer `save_pipeline_run_record`. |

### 11. `case_replay.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/case_replay.py` |
| decisión | `FREEZE_CASE_REPLAY` |
| veredicto | `PASS` |
| commit relacionado | `902b0dd feat(pymia-live): persist taxonomic intake through replay snapshot` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_case_replay.py tests/smartpyme/test_ocf_snapshot.py tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py -q` |
| riesgos residuales | Dependencia directa de `_JSONL_SPECS`; si se agregan nuevos archivos JSONL operacionales o nuevos record types, debe actualizarse `case_replay.py` y sus tests. |
| regla de reapertura | Reabrir sólo ante nuevo tipo de record JSONL, cambio de schema JSONL, bug real de replay, o incorporación explícita de eventos futuros. |

Cobertura auditada:

- read-only sobre JSONL
- no escribe storage
- no crea records
- no importa `vertical_pipeline.py`
- no importa `diagnostic_core`
- no ejecuta diagnóstico
- no infiere hallazgos no respaldados
- reconstruye determinísticamente la historia del caso
- expone datos suficientes para `ocf_snapshot.py`

### 12. `ocf_snapshot.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/ocf_snapshot.py` |
| decisión | `FIXED` |
| veredicto | `PASS` |
| commit relacionado | `f372be5 fix(pymia-live): include hashes in ocf snapshot refs` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_ocf_snapshot.py -q`; `python -m pytest tests/smartpyme/test_ocf_snapshot.py tests/smartpyme/test_case_replay.py -q`; `python -m pytest tests/application/test_vertical_pipeline_boundary.py tests/smartpyme/test_service_depth.py tests/smartpyme/test_ocf_snapshot.py -q` |
| riesgos residuales | El snapshot puede quedar desalineado si el replay o los records JSONL agregan nuevos refs y nadie los copia explícitamente. |
| regla de reapertura | Reabrir si cambian `run_refs`, `evidence_refs`, el contrato de replay, `heuristic_ratio`, o si el snapshot deja de ser read-only. |

### 13. `service_depth.py`

| Campo | Valor |
|---|---|
| archivo | `PymIA-Live/pymia/smartpyme/service_depth.py` |
| decisión | `FROZEN` |
| veredicto | `PASS` |
| commit relacionado | `current HEAD` |
| tests ejecutados | `python -m pytest tests/smartpyme/test_service_depth.py -q`; incluido además en baterías de frontera con `test_ocf_snapshot.py` y `test_vertical_pipeline_boundary.py`. |
| cobertura auditada | Clasifica profundidad proporcional de servicio: `FIRST_AID`, `DETERMINISTIC_DIAGNOSIS`, `ORGANIZATIONAL_LAB`. No diagnostica, no calcula fórmulas, no persiste, no llama LLM, no importa `diagnostic_core`. |
| riesgos residuales | Usa vocabulario V1 local limitado a routing. Este vocabulario no debe crecer hacia conocimiento sectorial ni reemplazar packs/contratos declarativos. |
| regla de reapertura | Reabrir sólo si se externaliza a contract/pack, cambia el modelo de profundidad de servicio, cambia la integración con OCF snapshot, o aparece deriva real hacia diagnóstico, fórmulas, persistencia o conocimiento sectorial hardcodeado. |

## Cadena viva auditada

```text
Excel
→ document_ingestion.py
→ structured_evidence_builder.py
→ vertical_pipeline.py
→ pipeline_registration.py
→ storage.py
→ case_replay.py
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
