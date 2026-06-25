# SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1 — CapabilitySpec

## Estado

```text
IMPLEMENTED
```

## Capacidad

Construir batch owner-facing de prompts de confirmación de columnas desde una `ColumnConfirmationMatrix` existente.

## Input autorizado

```text
ColumnConfirmationMatrix (ya construida por ingestion/curation)
metadata: dict | None
```

## Output autorizado

```text
Service1ColumnConfirmationOwnerPromptBatchV1
```

## Dependencias permitidas

- `pymia.contracts.column_confirmation_v1` — `ColumnConfirmationMatrix`, `ColumnConfirmationEntry`
- `service_1_owner_facing_role_explanation_catalog_v1` — `explain_owner_facing_semantic_role_v1`
- `service_1_column_interpretation_to_owner_prompt_bridge_v1` — bridge entry→prompt
- `service_1_column_confirmation_owner_prompt_v1` — prompt builder

## Prohibiciones

- Leer XLSX
- Llamar DocumentCurator
- Construir ColumnConfirmationMatrix
- Clasificar owner answers
- Aplicar respuestas
- Emitir case_patch
- Persistir
- Recalcular
- Reejecutar
- LLM
- vertical_pipeline
- landing/browser
