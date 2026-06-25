# SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1 — ModuleContract

## 1. Frontera

```text
DocumentCurationReport → OwnerPromptBatch wrapper
```

El módulo no pertenece a ingestion. Es un adaptador owner-facing que consume un reporte ya producido.

## 2. Responsabilidades permitidas

```text
- recibir DocumentCurationReport
- leer report.file_name
- leer report.status
- leer report.column_confirmation_matrix
- fallar cerrado si la matrix falta
- fallar cerrado si matrix.file_name no coincide con report.file_name
- llamar el batch builder ya existente
- propagar metadata al batch
- serializar salida con to_dict()
```

## 3. Responsabilidades prohibidas

```text
NO file IO
NO Excel IO
NO pandas
NO openpyxl
NO document ingestion
NO curation pipeline
NO semantic mapping
NO matrix construction
NO owner answer classification
NO owner answer application
NO case patch
NO persistence
NO recalculation
NO runtime execution
NO LLM
```

## 4. Dependencias permitidas

```text
tools.document_ingestion.DocumentCurationReport
pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1
```

## 5. Invariantes

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
persistence_authorized=False
```

## 6. Failure states

```text
COLUMN_CONFIRMATION_MATRIX_MISSING
COLUMN_CONFIRMATION_MATRIX_FILE_NAME_MISMATCH
```

## 7. Side effects

```text
NONE
```

## 8. Estado

```text
VIGENTE
```
