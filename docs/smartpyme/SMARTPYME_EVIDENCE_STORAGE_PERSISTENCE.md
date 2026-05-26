# SMARTPYME_EVIDENCE_STORAGE_PERSISTENCE

## 1. Estado y propósito

**Estado:** Implementado.
**Commit:** `feat(smartpyme): persist evidence records by tenant`
**HEAD base:** `cb6fda6 fix(smartpyme): align intake storage API with contract`

Este slice persiste `EvidenceRecord` por tenant en formato JSON Lines.

**Propósito:**
- Persistir evidencia registrada (metadata, no contenido) por tenant.
- Permitir recuperación por tenant, intake_id o evidence_id.
- Mantener separación entre registro y contenido documental.

**No propósito:**
- NO abre archivos.
- NO lee Excel/PDF.
- NO calcula hash.
- NO valida contenido documental.
- NO decide si una EvidenceRequest queda satisfecha.
- NO cambia intake_state.
- NO marca READY_FOR_ANALYSIS.
- NO ejecuta análisis.
- NO despacha microservicios.

## 2. Alcance

### Archivos modificados
- `pymia/smartpyme/storage.py` — agregadas 4 funciones públicas para evidence storage
- `tests/smartpyme/test_evidence_storage.py` — 23 tests nuevos

### Archivos NO modificados
- `pymia/smartpyme/evidence.py` — contrato de EvidenceRecord intacto
- `pymia/smartpyme/intake.py` — contrato de IntakeRecord intacto
- `e2e_cli.py` — sin cambios
- `docs/mermaid/` — excluido (ruido preexistente)

## 3. Layout de storage

```
tenant_root/
  evidence/
  reports/
  results/
  receptions.jsonl
  intakes.jsonl
  evidences.jsonl        ← NUEVO
```

Cada línea de `evidences.jsonl`:
- Un `EvidenceRecord` serializado como JSON.
- Append-only.
- UTF-8.
- Preserva orden de inserción.

## 4. API pública

### save_evidence_record

```python
def save_evidence_record(
    tenant_id: str,
    record: Any,
    *,
    base_dir: str | Path | None = None,
) -> Path:
```

**Comportamiento:**
- Acepta `EvidenceRecord` (con `to_dict()`) o `dict`.
- Valida tenant_id no vacío.
- Valida record["tenant_id"] == tenant_id.
- Valida 15 campos core requeridos.
- Valida tipos de campos core (notes: list, metadata: dict, size_bytes: int|None).
- Append a `<base_dir>/<tenant_id>/evidences.jsonl`.
- Retorna `Path` al archivo.
- No muta record.

### load_evidence_records

```python
def load_evidence_records(
    tenant_id: str,
    *,
    base_dir: str | Path | None = None,
) -> list[dict]:
```

**Comportamiento:**
- Valida tenant_id no vacío.
- Retorna `[]` si evidences.jsonl no existe.
- Retorna `list[dict]` (NO `EvidenceRecord`).
- Preserva orden de inserción.
- ValueError en JSON malformado.
- ValueError en línea que no es dict.

### load_evidence_records_by_intake_id

```python
def load_evidence_records_by_intake_id(
    tenant_id: str,
    intake_id: str,
    *,
    base_dir: str | Path | None = None,
) -> list[dict]:
```

**Comportamiento:**
- Valida tenant_id e intake_id no vacíos.
- Filtra por intake_id.
- Retorna `list[dict]` filtrado.
- Preserva orden.
- Retorna `[]` si no hay matches.
- No cruza boundaries de tenant.

### load_evidence_record_by_id

```python
def load_evidence_record_by_id(
    tenant_id: str,
    evidence_id: str,
    *,
    base_dir: str | Path | None = None,
) -> dict | None:
```

**Comportamiento:**
- Valida tenant_id y evidence_id no vacíos.
- Busca por evidence_id.
- Retorna `dict` si existe.
- Retorna `None` si no existe.
- No cruza boundaries de tenant.

## 5. Validaciones

### save_evidence_record lanza ValueError si:
- tenant_id vacío
- base_dir es None
- record no es dict ni tiene to_dict()
- record["tenant_id"] no existe
- record["tenant_id"] != tenant_id
- falta cualquier campo core requerido:
  - evidence_id, tenant_id, intake_id, request_id
  - evidence_type, source_kind, source_ref
  - original_filename, mime_type, size_bytes, content_hash
  - status, received_at, notes, metadata
- notes no es list
- metadata no es dict
- size_bytes no es int|None
- request_id, original_filename, mime_type, content_hash no son str|None

### load_evidence_records lanza ValueError si:
- tenant_id vacío
- base_dir es None
- línea JSON malformada
- línea JSON no decodifica a dict

### load_evidence_records_by_intake_id lanza ValueError si:
- tenant_id vacío
- intake_id vacío
- base_dir es None

### load_evidence_record_by_id lanza ValueError si:
- tenant_id vacío
- evidence_id vacío
- base_dir es None

## 6. Relación con EvidenceRecord

`EvidenceRecord` (módulo `evidence.py`) define el contrato de metadata:
- 15 campos
- 5 estados permitidos
- 5 source kinds permitidos
- `to_dict()` para serialización JSON-safe

`save_evidence_record` persiste la metadata.
`load_evidence_records` recupera la metadata como `list[dict]`.

**NO** reconstruye `EvidenceRecord` al cargar (retorna dict plano).

## 7. Relación con IntakeRecord

`IntakeRecord` y `EvidenceRecord` se vinculan por:
- `tenant_id` (obligatorio en ambos)
- `intake_id` (obligatorio en EvidenceRecord)

`load_evidence_records_by_intake_id` filtra evidencias de un intake específico.

**NO** decide si la evidencia satisface una `IntakeEvidenceRequest`.
**NO** cambia `intake_state`.
**NO** marca `READY_FOR_ANALYSIS`.

## 8. Relación con IntakeEvidenceRequest

`IntakeEvidenceRequest` (en `intake.py`) define qué evidencia se necesita.
`EvidenceRecord` registra qué evidencia fue recibida o referenciada.

La vinculación mínima se hace por:
- `tenant_id`
- `intake_id`
- `request_id` (opcional en EvidenceRecord)
- `evidence_type`

**NO** decide si la evidencia satisface la request.
Esa decisión corresponde a un futuro slice de readiness gate.

## 9. Safety gates

- **NO_DIAGNOSIS_WITHOUT_EVIDENCE:** este slice no diagnostica.
- **NO_FILE_PROCESSING:** no abre archivos, no lee bytes, no calcula hash.
- **NO_CONTENT_VALIDATION:** no valida contenido documental.
- **NO_SUFFICIENCY_DECISION:** no decide si la evidencia es suficiente.
- **NO_INTAKE_STATE_CHANGE:** no cambia intake_state.
- **NO_RUNTIME_EXECUTION:** no ejecuta excel_diagnostic ni supplier_duplicate_check.
- **FAIL_CLOSED:** validaciones estrictas, ValueError en inputs inválidos.
- **TENANT_ISOLATION:** no cruza boundaries de tenant.

## 10. No-goals

Este slice **NO**:
- Abre archivos.
- Lee Excel/PDF.
- Calcula hash.
- Infiere MIME.
- Valida contenido documental.
- Decide si una EvidenceRequest queda satisfecha.
- Cambia intake_state.
- Marca READY_FOR_ANALYSIS.
- Ejecuta análisis.
- Despacha microservicios.
- Agrega CLI.
- Agrega HTML.
- Agrega Telegram/Hermes/Output Gateway.
- Modifica evidence.py.
- Modifica intake.py.

## 11. Tests

Archivo: `tests/smartpyme/test_evidence_storage.py`
Cantidad: 23 tests (incluyendo variantes parametrizadas)

Cobertura:
1. Import smoke
2. Signature verification (4 tests)
3. Load missing returns []
4. Save creates evidences.jsonl
5. Save returns Path
6. Save accepts EvidenceRecord instance
7. Save accepts plain dict
8. Load preserves insertion order
9. Load returns list[dict]
10. load_evidence_records_by_intake_id returns matching
11. load_evidence_records_by_intake_id returns empty when absent
12. load_evidence_record_by_id returns matching
13. load_evidence_record_by_id returns None when absent
14. Empty tenant_id raises on save
15. Empty tenant_id raises on load
16. Whitespace tenant_id raises
17. Empty intake_id raises on load_by_intake_id
18. Empty evidence_id raises on lookup
19. Whitespace evidence_id raises on lookup
20. Tenant mismatch raises
21. Missing required field raises
22. Record missing tenant_id field raises
23. Malformed JSON line raises
24. Non-dict JSON line raises
25. JSON line is valid JSON
26. No cross-tenant reads
27. Record is not mutated
28. Existing intake storage not broken
29. base_dir required on save
30. base_dir required on load
31. base_dir required on load_by_id
32. base_dir required on load_by_intake_id
33. notes must be list
34. metadata must be dict
35. size_bytes must be int or None

## 12. Próximo slice recomendado

**SMARTPYME_EVIDENCE_READINESS_GATE**

Objetivo:
- Decidir si un conjunto de evidencias satisface las `IntakeEvidenceRequest` de un `IntakeRecord`.
- Cambiar `intake_state` de `NEEDS_EVIDENCE` a `READY_FOR_ANALYSIS` cuando corresponda.
- No ejecutar análisis.
- No procesar archivos.
- Solo evaluar metadata.

Dependencias:
- `IntakeRecord` (intake.py)
- `IntakeEvidenceRequest` (intake.py)
- `EvidenceRecord` (evidence.py)
- `load_evidence_records_by_intake_id` (storage.py)
