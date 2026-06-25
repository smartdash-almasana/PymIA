# SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1 — TaskSpec

## Objetivo

Implementar un bridge puro:

```text
DocumentCurationReport
→ report.column_confirmation_matrix
→ Service1ColumnConfirmationOwnerPromptBatchV1
```

## Archivos autorizados

```text
PymIA-Live/pymia/smartpyme/service_1_document_curation_report_to_owner_prompt_batch_bridge_v1.py
PymIA-Live/tests/smartpyme/test_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1.py
```

## Reglas

```text
- input: DocumentCurationReport
- si no hay column_confirmation_matrix: fail closed
- si matrix.file_name no coincide con report.file_name: fail closed
- si la matrix es válida: llamar el batch builder existente
- propagar metadata
- preservar flags de seguridad
```

## Prohibiciones

```text
No ingestion. No Excel IO. No curation pipeline. No matrix construction.
No owner-answer classification. No applier. No case patch.
No persistence. No recalculation. No vertical_pipeline. No UI.
```

## Tests requeridos

```text
- report con matrix válida genera batch
- report sin matrix devuelve COLUMN_CONFIRMATION_MATRIX_MISSING
- matrix con file_name distinto devuelve COLUMN_CONFIRMATION_MATRIX_FILE_NAME_MISMATCH
- metadata se propaga
- flags preservados
- to_dict serializa batch o None
- rechaza input inválido
- rechaza metadata inválida
- pureza sin filesystem
- módulo sin dependencias de ingestion runtime
```

## PASS

```text
Tests focales pasan y no se toca ingestion, pipeline, UI ni persistence.
```

## Estado

```text
VIGENTE
```
