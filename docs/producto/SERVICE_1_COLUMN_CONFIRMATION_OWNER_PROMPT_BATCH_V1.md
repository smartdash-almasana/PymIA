# SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1

## Estado

```text
IMPLEMENTED
```

## Objetivo

Generar un batch owner-facing de prompts de confirmación desde una `ColumnConfirmationMatrix` ya existente.

Este slice conecta:

```text
ColumnConfirmationMatrix.entries
→ Service1ColumnInterpretationToOwnerPromptBridgeV1 por cada entry accionable
→ batch de prompts owner-facing
```

## Archivo runtime

```text
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_owner_prompt_batch_v1.py
```

## Test

```text
PymIA-Live/tests/smartpyme/test_service_1_column_confirmation_owner_prompt_batch_v1.py
```

## Input contract

```python
matrix: ColumnConfirmationMatrix
metadata: dict | None = None
```

## Output contract

```text
Service1ColumnConfirmationOwnerPromptBatchV1
```

Campos:

```text
schema_version
service_name
file_name
matrix_status
total_entries
actionable_entries_count
prompts
has_prompts
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
persistence_authorized
created_at
metadata
```

`prompts` contiene:

```text
tuple[Service1ColumnInterpretationToOwnerPromptBridgeV1, ...]
```

## Regla de selección

El batch incluye sólo entries accionables:

```python
entry.is_actionable()
```

Eso incluye:

```text
PENDING_OWNER_CONFIRMATION
BLOCKED_AMBIGUOUS
```

Y excluye:

```text
CONFIRMED
IGNORED_NOT_RELEVANT
```

## Flujo interno

```text
1. Recibe ColumnConfirmationMatrix.
2. Itera matrix.entries.
3. Filtra entries accionables.
4. Para cada entry llama build_service_1_column_interpretation_to_owner_prompt_bridge_v1(...).
5. Devuelve batch frozen con prompts y metadata.
```

## Seguridad fija

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
persistence_authorized=False
```

## Exclusiones

```text
NO lee XLSX
NO llama DocumentCurator
NO construye ColumnConfirmationMatrix
NO modifica ingestion
NO inventa semantic roles
NO clasifica respuestas del dueño
NO aplica respuestas a la matrix
NO emite case_patch
NO persiste
NO recalcula
NO reejecuta
NO vertical_pipeline
NO landing/browser
```

## Tests cubiertos

```text
- matrix con venta_total pendiente genera 1 prompt
- matrix con varias columnas pending genera N prompts
- matrix sin actionable entries devuelve batch vacío
- matrix vacía devuelve batch vacío
- unknown role usa fallback seguro
- metadata se propaga a batch, bridge y prompt
- flags de seguridad preservados
- entries no accionables quedan excluidas
- to_dict serializa batch y nested prompts
- pureza sin filesystem/storage
- prompt_text no filtra semantic roles internos
- validación de tipo matrix
- validación de metadata
```

## Próximo frente permitido

```text
SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1_PRECHECK
```

Pregunta futura:

```text
¿Conviene crear un bridge mínimo que tome DocumentCurationReport.column_confirmation_matrix y devuelva este batch?
```

Todavía sin persistence, sin recalculation, sin vertical_pipeline y sin UI.
