# SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1

## Estado

```text
IMPLEMENTED
```

## Objetivo

Conectar un `DocumentCurationReport` ya producido con el batch owner-facing de confirmación de columnas.

```text
DocumentCurationReport
→ report.column_confirmation_matrix
→ Service1ColumnConfirmationOwnerPromptBatchV1
```

## Archivo runtime

```text
PymIA-Live/pymia/smartpyme/service_1_document_curation_report_to_owner_prompt_batch_bridge_v1.py
```

## Test

```text
PymIA-Live/tests/smartpyme/test_service_1_document_curation_report_to_owner_prompt_batch_bridge_v1.py
```

## Input contract

```python
report: DocumentCurationReport
metadata: dict | None = None
```

## Output contract

```text
Service1DocumentCurationReportToOwnerPromptBatchBridgeV1
```

Campos principales:

```text
schema_version
service_name
file_name
report_status
has_column_confirmation_matrix
owner_prompt_batch
prompts_count
has_prompts
blocked_reason
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
persistence_authorized
created_at
metadata
```

## Failure states

```text
COLUMN_CONFIRMATION_MATRIX_MISSING
COLUMN_CONFIRMATION_MATRIX_FILE_NAME_MISMATCH
```

## Qué hace

```text
1. Recibe DocumentCurationReport.
2. Verifica report.column_confirmation_matrix.
3. Verifica matrix.file_name == report.file_name.
4. Si pasa, llama build_service_1_column_confirmation_owner_prompt_batch_v1(...).
5. Si falla, devuelve wrapper fail-closed sin batch.
```

## Qué no hace

```text
NO lee XLSX
NO llama curate_xlsx_document
NO llama XlsxCurationPipeline
NO llama DocumentCurator
NO construye ColumnConfirmationMatrix
NO clasifica respuestas del dueño
NO aplica respuestas
NO emite case_patch
NO persiste
NO recalcula
NO toca vertical_pipeline
NO toca landing/browser
```

## Seguridad fija

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
persistence_authorized=False
```

## Tests cubiertos

```text
- report con matrix válida genera batch
- report sin matrix devuelve COLUMN_CONFIRMATION_MATRIX_MISSING
- matrix con file_name distinto devuelve COLUMN_CONFIRMATION_MATRIX_FILE_NAME_MISMATCH
- metadata se propaga al wrapper, batch y prompts
- flags de seguridad preservados
- to_dict serializa batch o None
- rechaza report inválido
- rechaza metadata inválida
- pureza sin filesystem/storage
- módulo sin dependencias de ingestion runtime ni IO
```

## Próximo frente permitido

```text
SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_PRECHECK
```

Pregunta futura:

```text
¿Cómo conviven el batch owner-facing nuevo y Service1QuestionBundleV1 sin duplicar preguntas ni romper refs?
```
