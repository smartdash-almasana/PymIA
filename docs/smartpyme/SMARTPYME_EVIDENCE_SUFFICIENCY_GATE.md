# SMARTPYME_EVIDENCE_SUFFICIENCY_GATE

## 1. Propósito

Módulo puro y determinístico que evalúa si las evidencias registradas
para un `intake_id` satisfacen las `IntakeEvidenceRequest` declaradas
en el `IntakeRecord` correspondiente.

Devuelve un `EvidenceSufficiencyResult` que downstream slices pueden
usar para decidir transiciones de estado, sin ejecutar análisis ni
modificar `intake_state` por sí mismo.

## 2. Alcance

### Lo que este slice HACE

- Recibe un `IntakeRecord` (o dict) y una lista de `EvidenceRecord` (o dicts).
- Compara metadata: `tenant_id`, `intake_id`, `evidence_type`, `request_id`, `status`.
- Verifica `required_fields` contra `evidence.metadata` (solo keys).
- Devuelve un `EvidenceSufficiencyResult` JSON-serializable.
- Aplica validaciones fail-closed sobre inputs.
- No muta inputs.

### Lo que este slice NO HACE

- No abre archivos.
- No lee Excel/PDF.
- No calcula hash.
- No infiere MIME.
- No valida contenido documental.
- No ejecuta análisis.
- No cambia `intake_state`.
- No persiste resultados.
- No despacha microservicios.
- No implementa `READY_FOR_ANALYSIS` runtime.

El resultado es una **recomendación/salida pura**, no una mutación.

## 3. Input contracts

### intake_record

Puede ser:
- una instancia de `IntakeRecord` con método `to_dict()`
- un `dict` con los campos mínimos

Campos requeridos:
- `tenant_id: str`
- `intake_id: str`
- `evidence_requests: list[dict]`

Opcional:
- `intake_state: str` (si es `"BLOCKED"`, el gate short-circuita a `BLOCKED`)

### evidence_records

Lista donde cada elemento puede ser:
- instancia de `EvidenceRecord` con `to_dict()`
- `dict` con los campos mínimos

Campos requeridos por evidencia:
- `tenant_id`
- `intake_id`
- `evidence_id`
- `evidence_type`
- `status`

Opcional:
- `request_id` (para match fuerte)
- `metadata: dict` (para validar `required_fields`)

## 4. Output contract

### EvidenceSufficiencyResult

```python
@dataclass
class EvidenceSufficiencyResult:
    tenant_id: str
    intake_id: str
    status: str                # READY | NEEDS_MORE_EVIDENCE | BLOCKED | UNSUPPORTED
    suggested_next_state: str  # READY_FOR_ANALYSIS | NEEDS_EVIDENCE | BLOCKED | UNSUPPORTED
    assessments: list[EvidenceRequestAssessment]
    matched_evidence_ids: list[str]
    missing_request_ids: list[str]
    blocking_request_ids: list[str]
    warnings: list[str]
    audit_notes: list[str]
    created_at: str

    def to_dict(self) -> dict: ...
```

### EvidenceRequestAssessment

```python
@dataclass
class EvidenceRequestAssessment:
    request_id: str
    evidence_type: str
    source_tank: str | None
    required: bool
    blocking: bool
    matched_evidence_ids: list[str]
    status: str                # SATISFIED | MISSING | PARTIAL | WAIVED | BLOCKED
    reason: str
    missing_fields: list[str]
    notes: list[str]

    def to_dict(self) -> dict: ...
```

## 5. Matching rules

Una evidencia satisface una request cuando se cumplen **todas** estas condiciones:

1. `evidence.tenant_id == intake.tenant_id`
2. `evidence.intake_id == intake.intake_id`
3. Match de identidad:
   - **Fuerte**: `request.request_id` y `evidence.request_id` existen y coinciden.
   - **Débil (fallback)**: si alguno de los `request_id` falta, match por `evidence_type`.
4. `evidence.status` es aceptable: `RECEIVED`, `REGISTERED` o `LINKED`.

Estados rechazados: `REJECTED`, `SUPERSEDED`.

`source_tank` **no** es condición de match, pero se preserva en el assessment.

### Required fields

Si la request declara `required_fields`, se validan contra las **keys**
de `evidence.metadata` (dict). No se inspecciona contenido de archivo.

- Si todos los campos presentes → `SATISFIED`.
- Si falta alguno → `PARTIAL`, con `missing_fields` poblado.
- Si es blocking y está `PARTIAL` → el resultado global es `NEEDS_MORE_EVIDENCE`.

## 6. Assessment statuses

| Status | Significado |
|---|---|
| `SATISFIED` | Evidencia matcheada y required_fields presentes |
| `MISSING` | Ninguna evidencia aceptable matcheó |
| `PARTIAL` | Matcheó pero faltan required_fields en metadata |
| `WAIVED` | Request eximida (no implementado aún) |
| `BLOCKED` | Bloqueo por regla de seguridad |

## 7. Sufficiency statuses

| Status | Suggested next state | Cuándo |
|---|---|---|
| `READY` | `READY_FOR_ANALYSIS` | Todos los blocking requests satisfechos, o ninguno declarado |
| `NEEDS_MORE_EVIDENCE` | `NEEDS_EVIDENCE` | Algún blocking request `MISSING` o `PARTIAL` |
| `BLOCKED` | `BLOCKED` | `intake_state` es `BLOCKED` |
| `UNSUPPORTED` | `UNSUPPORTED` | Caso no soportado (reserva futura) |

## 8. Safety gates

- **NO_MUTATE_INPUTS**: ni `intake_record` ni `evidence_records` son modificados.
- **FAIL_CLOSED_ON_INVALID_INPUT**: `ValueError` si falta algún campo core.
- **NO_FILE_INSPECTION**: `required_fields` se valida solo contra `metadata` keys.
- **NO_STATE_MUTATION**: este módulo no cambia `intake_state`.
- **NO_PERSISTENCE**: el resultado no se escribe a storage.
- **SHORT_CIRCUIT_ON_BLOCKED_INTAKE**: si el intake ya está `BLOCKED`, devuelve `BLOCKED`.
- **EMPTY_REQUESTS_MEANS_READY**: si no hay `evidence_requests`, el resultado es `READY` con warning.

## 9. No-goals

- Ejecutar análisis.
- Despachar a `excel_diagnostic` ni `supplier_duplicate_check`.
- Modificar `intakes.jsonl` ni `evidences.jsonl`.
- Implementar `READY_FOR_ANALYSIS` como estado runtime persistente.
- Proveer UI/CLI.
- Integrar con Hermes real, Telegram, Output Gateway.

## 10. Relación con IntakeRecord

Este módulo **consume** `IntakeRecord` (o su forma dict) y su lista de
`evidence_requests`. No lo modifica. Un slice posterior
(`SMARTPYME_INTAKE_STATE_TRANSITION`) será responsable de actualizar
`intake_state` en base al `EvidenceSufficiencyResult`.

## 11. Relación con EvidenceRecord

Este módulo **consume** `EvidenceRecord` (o dict). No lo valida
documentalmente, no calcula hash, no inspecciona contenido. Solo
compara metadata y estado.

## 12. Relación con storage

Este módulo **no carga ni persiste**. La integración típica será:

```python
intake = load_intake_record_by_id(tenant_id, intake_id, base_dir=...)
evidences = load_evidence_records_by_intake_id(tenant_id, intake_id, base_dir=...)
result = evaluate_evidence_sufficiency(intake, evidences)
```

El `EvidenceSufficiencyResult` puede ser persistido o no por un slice
posterior, pero este módulo es agnóstico al storage.

## 13. Tests

Archivo: `tests/smartpyme/test_evidence_gate.py`

Cobertura:
- import smoke
- no evidence_requests → READY
- blocking missing → NEEDS_MORE_EVIDENCE
- match by request_id (fuerte)
- match by evidence_type fallback (débil)
- wrong tenant / wrong intake no matchean
- REJECTED / SUPERSEDED no matchean
- RECEIVED / REGISTERED / LINKED matchean
- required_fields faltantes → PARTIAL
- required_fields presentes → SATISFIED
- non-blocking missing no bloquea READY
- blocked intake → BLOCKED
- múltiples requests, uno missing blocking
- todos blocking satisfied → READY
- serialización JSON de Result y Assessment
- aceptación de IntakeRecord/EvidenceRecord/dataclass/dict
- inputs no mutados
- matched_evidence_ids deduplicados
- missing_request_ids en orden
- validaciones fail-closed

## 14. Próximo slice recomendado

**SMARTPYME_INTAKE_STATE_TRANSITION**

Objetivo: aplicar `EvidenceSufficiencyResult` para actualizar
`intake_state` en `intakes.jsonl` (de `NEEDS_EVIDENCE` a
`READY_FOR_ANALYSIS` cuando el resultado sea `READY`).

Ese slice **sí** mutará estado y **sí** persistirá.
Este slice (evidence_gate) permanece puro.
