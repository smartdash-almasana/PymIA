# SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1 — CapabilitySpec

## 1. Capacidad

Autoriza una capacidad mínima de adaptación entre el reporte de curación documental y el batch owner-facing de confirmación de columnas.

```text
DocumentCurationReport
→ ColumnConfirmationMatrix existente
→ Service1ColumnConfirmationOwnerPromptBatchV1
```

## 2. Input autorizado

```text
DocumentCurationReport
```

El único campo consumible para generar prompts es:

```text
report.column_confirmation_matrix
```

## 3. Output autorizado

```text
Service1DocumentCurationReportToOwnerPromptBatchBridgeV1
```

El output puede contener:

```text
owner_prompt_batch: Service1ColumnConfirmationOwnerPromptBatchV1 | None
blocked_reason: str | None
```

## 4. Qué puede hacer

```text
- validar tipo de report
- validar metadata dict/None
- verificar existencia de column_confirmation_matrix
- verificar consistencia file_name entre report y matrix
- llamar build_service_1_column_confirmation_owner_prompt_batch_v1(...)
- devolver wrapper fail-closed trazable
```

## 5. Qué no puede hacer

```text
NO leer XLSX
NO llamar curate_xlsx_document
NO llamar XlsxCurationPipeline
NO llamar DocumentCurator
NO construir ColumnConfirmationMatrix
NO modificar DocumentCurationReport
NO clasificar columnas
NO clasificar respuestas del dueño
NO aplicar respuestas
NO emitir case_patch
NO persistir
NO recalcular
NO reejecutar
NO usar LLM
NO tocar vertical_pipeline
NO tocar landing/browser
```

## 6. Invariantes

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
persistence_authorized=False
```

## 7. Estado

```text
VIGENTE
```
