# SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1 — TaskSpec

## Tarea

Implementar y validar `service_1_column_confirmation_owner_prompt_batch_v1.py`.

## Archivos

- Runtime: `PymIA-Live/pymia/smartpyme/service_1_column_confirmation_owner_prompt_batch_v1.py`
- Tests focales: `PymIA-Live/tests/smartpyme/test_service_1_column_confirmation_owner_prompt_batch_v1.py`
- Acceptance seam: `PymIA-Live/tests/smartpyme/test_service_1_column_confirmation_owner_prompt_batch_acceptance_v1.py`

## Acceptance seam test requerido

```text
XLSX temporal mínimo (openpyxl)
→ curate_xlsx_document(...)
→ curated.report.column_confirmation_matrix
→ build_service_1_column_confirmation_owner_prompt_batch_v1(...)
→ verificar batch completo
```

## Tests focales (13)

1. pending venta_total genera 1 prompt
2. varias pending genera N prompts
3. sin actionable entries devuelve vacío
4. matrix vacía devuelve vacío
5. unknown role usa fallback
6. metadata propagada
7. flags preservados
8. non-actionable excluidas
9. to_dict serializa nested prompts
10. pure no filesystem
11. prompt_text no filtra semantic roles internos
12. reject invalid matrix
13. reject invalid metadata

## Prohibiciones

No tocar ingestion, vertical_pipeline, landing, contratos existentes.

## PASS criteria

- batch focal pasa (13/13)
- acceptance seam XLSX→matrix→batch pasa
- governance docs existen
- no archivos prohibidos tocados
- no sucios preexistentes en commit
