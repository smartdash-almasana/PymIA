# SMARTPYME_INTAKE_STORAGE_PERSISTENCE

Estado: IMPLEMENTED

## Scope

Persistencia mínima por tenant para `IntakeRecord` sin ejecutar análisis.

## API pública

- `save_intake_record(base_dir, record)`
- `load_intake_records(base_dir, tenant_id)`
- `load_intake_record_by_id(base_dir, tenant_id, intake_id)`

## Comportamiento

- Guarda cada intake en `intakes.jsonl` por tenant.
- Escribe snapshot en `results/intake_record.json`.
- Carga historial por tenant en orden de append.
- Permite búsqueda por `intake_id`.
- Si no existe `intake_id`, retorna `None`.

## Restricciones

- No ejecuta diagnóstico.
- No procesa archivos de evidencia.
- No modifica runtime, CLI ni UI.
