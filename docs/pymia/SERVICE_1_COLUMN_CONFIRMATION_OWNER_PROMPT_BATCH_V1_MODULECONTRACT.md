# SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1 — ModuleContract

## Frontera

```text
ColumnConfirmationMatrix → Service1ColumnConfirmationOwnerPromptBatchV1
```

## Responsabilidad permitida

- Validar input (matrix type, metadata type)
- Iterar matrix.entries
- Filtrar entry.is_actionable()
- Llamar bridge por entry actionable
- Consolidar batch frozen
- Propagar metadata

## Responsabilidad prohibida

- Ingestion (leer archivos)
- Curation (construir reportes)
- Semantic mapping (asignar roles)
- Matrix construction
- Answer classification
- Answer application
- Storage / persistence
- Calculation

## Invariantes

- `runtime_authorized=False` siempre
- `human_review_required=True` siempre
- `reexecution_authorized=False` siempre
- `recalculation_authorized=False` siempre
- `persistence_authorized=False` siempre
- No semantic role leakage in prompt_text
- `file_name` comes from `matrix.file_name`

## Side effects

Ninguno. Función pura.
