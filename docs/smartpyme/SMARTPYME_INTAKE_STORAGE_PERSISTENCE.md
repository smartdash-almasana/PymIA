# SMARTPYME_INTAKE_STORAGE_PERSISTENCE

Estado: IMPLEMENTED (API alineada con contrato aprobado)

## Scope

Persistencia mínima por tenant para `IntakeRecord` sin ejecutar análisis.

## API pública

```python
save_intake_record(
    tenant_id: str,
    record: IntakeRecord | dict,
    *,
    base_dir: str | Path | None = None,
) -> Path

load_intake_records(
    tenant_id: str,
    *,
    base_dir: str | Path | None = None,
) -> list[dict]

load_intake_record_by_id(
    tenant_id: str,
    intake_id: str,
    *,
    base_dir: str | Path | None = None,
) -> dict | None
```

## Comportamiento

### save_intake_record

- Acepta `IntakeRecord` (con `to_dict()`) o `dict` plano
- Valida `tenant_id` no vacío
- Valida `record["tenant_id"]` existe
- Valida `record["tenant_id"] == tenant_id`
- Valida 12 campos core requeridos
- Valida tipos de campos core (dict/list según corresponda)
- Escribe una línea JSON en `<base_dir>/<tenant_id>/intakes.jsonl`
- Retorna `Path` al archivo `intakes.jsonl`
- No muta `record`

### load_intake_records

- Valida `tenant_id` no vacío
- Retorna `[]` si `intakes.jsonl` no existe
- Retorna `list[dict]` (no `IntakeRecord`)
- Preserva orden de inserción
- Lanza `ValueError` en JSON malformado
- Lanza `ValueError` si línea no es dict

### load_intake_record_by_id

- Valida `tenant_id` no vacío
- Valida `intake_id` no vacío
- Retorna `dict` si existe
- Retorna `None` si no existe
- No cruza boundaries de tenant

## Layout de storage

```
<base_dir>/
  <tenant_id>/
    evidence/
    reports/
    results/
    receptions.jsonl
    intakes.jsonl
```

## Validaciones fail-closed

Campos core requeridos:
- `intake_id`
- `tenant_id`
- `raw_input`
- `structured_selectors` (dict)
- `interrogation_result` (dict)
- `tank_selection_result` (dict)
- `evidence_requests` (list)
- `intake_state`
- `suggested_next_state`
- `warnings` (list)
- `audit_notes` (list)
- `created_at`

## Restricciones

- No ejecuta diagnóstico
- No procesa archivos de evidencia
- No modifica runtime, CLI ni UI
- No ejecuta análisis
- No despacha microservicios
- No valida contenido documental
- No cambia estados de `IntakeRecord`

## Relación con IntakeRecord

- `IntakeRecord` se crea con `create_intake_record()`
- `save_intake_record()` persiste el record (explícito, no automático)
- Son responsabilidades separadas

## Tests

Archivo: `tests/smartpyme/test_intake_storage.py`

Cobertura:
- Signature verification (tenant_id primero, base_dir keyword-only)
- Save acepta IntakeRecord y dict
- Save retorna Path
- Load retorna list[dict]
- Load by id retorna dict
- Tenant mismatch raises
- Missing required field raises
- Malformed JSON raises
- Non-dict JSON raises
- Insertion order preserved
- No cross-tenant reads
- Empty tenant_id raises
- Empty intake_id raises
- JSON line is valid JSON
- Existing storage layout not broken

## Próximo slice recomendado

`SMARTPYME_EVIDENCE_STORAGE_PERSISTENCE` — persistir `EvidenceRecord` en `<base_dir>/<tenant_id>/evidences.jsonl` con API análoga.
