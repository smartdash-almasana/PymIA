# SMARTPYME_READY_FOR_ANALYSIS_GATE

**Estado:** Documentado (slice puro, sin persistencia).
**HEAD base:** `d5899eb`
**Módulo:** `pymia/smartpyme/readiness.py`
**Tests:** `tests/smartpyme/test_readiness.py`

---

## 1. Propósito

Implementar un **gate puro y determinístico** que decide si un intake
está listo para ejecutar análisis, basándose en:

- el `IntakeRecord` (o dict) y
- el `EvidenceSufficiencyResult` (o dict).

Devuelve un `AnalysisReadinessResult` que indica:

- estado (`READY_FOR_ANALYSIS`, `NEEDS_EVIDENCE`, `BLOCKED`, `UNSUPPORTED`);
- `runtime_classification` sugerida (`excel_diagnostic` o `supplier_duplicate_check`);
- `can_execute` (boolean);
- razones de bloqueo, warnings y notas de auditoría.

**No ejecuta análisis. No despacha microservicios. No muta estado. No persiste.**

---

## 2. Alcance

### Incluye
- Decisión determinística de readiness.
- Resolución conservadora de `runtime_classification`.
- Validaciones fail-closed de inputs.
- Output JSON-serializable vía `to_dict()`.

### No incluye
- Persistencia del resultado.
- Cambio de `intake_state` en `intakes.jsonl`.
- Ejecución de `excel_diagnostic` o `supplier_duplicate_check`.
- Lectura de archivos, cálculo de hash, inferencia MIME.
- Integración con Telegram, Hermes, Output Gateway.
- CLI, UI, jobs.

---

## 3. Input contracts

### `intake_record`
- `dict` o dataclass con `to_dict()`.
- Campos requeridos: `tenant_id`, `intake_id`.
- Campos usados: `intake_state`, `evidence_requests`, `tank_selection_result`.

### `sufficiency_result`
- `dict` o dataclass con `to_dict()`.
- Campos requeridos: `tenant_id`, `intake_id`, `status`.
- `status` debe ser uno de: `READY`, `NEEDS_MORE_EVIDENCE`, `BLOCKED`, `UNSUPPORTED`.

### Validaciones
- `tenant_id` e `intake_id` deben coincidir entre ambos inputs.
- `status` desconocido → `ValueError`.
- `evidence_requests` debe ser `list` si está presente.

---

## 4. Output contract

### `AnalysisReadinessResult`

| Campo | Tipo | Descripción |
|---|---|---|
| `tenant_id` | `str` | ID del tenant |
| `intake_id` | `str` | ID del intake |
| `status` | `str` | Uno de los `READINESS_*` |
| `suggested_next_state` | `str` | Próximo estado sugerido |
| `runtime_classification` | `str \| None` | Clasificación runtime sugerida |
| `can_execute` | `bool` | Si el runtime puede ejecutarse |
| `blocking_reasons` | `list[str]` | Razones por las que no se puede ejecutar |
| `missing_request_ids` | `list[str]` | IDs de requests faltantes |
| `matched_evidence_ids` | `list[str]` | IDs de evidencias matched |
| `warnings` | `list[str]` | Advertencias |
| `audit_notes` | `list[str]` | Notas de auditoría |
| `created_at` | `str` | Timestamp ISO |

Método: `to_dict() -> dict` (JSON-serializable).

---

## 5. Decision rules

### Regla 1: intake_state == "BLOCKED"
```
status = BLOCKED
suggested_next_state = BLOCKED
can_execute = False
blocking_reasons = ["Intake is blocked."]
```

### Regla 2: sufficiency.status == "BLOCKED"
```
status = BLOCKED
suggested_next_state = BLOCKED
can_execute = False
```

### Regla 3: sufficiency.status == "NEEDS_MORE_EVIDENCE"
```
status = NEEDS_EVIDENCE
suggested_next_state = NEEDS_EVIDENCE
can_execute = False
missing_request_ids propagado desde sufficiency
```

### Regla 4: sufficiency.status == "UNSUPPORTED"
```
status = UNSUPPORTED
suggested_next_state = UNSUPPORTED
can_execute = False
```

### Regla 5: sufficiency.status == "READY"
Resolver `runtime_classification` desde `evidence_requests[].enables_classification`:

- Si solo `excel_diagnostic` está habilitado → `runtime_classification = "excel_diagnostic"`.
- Si solo `supplier_duplicate_check` está habilitado → `runtime_classification = "supplier_duplicate_check"`.
- Si ambos están habilitados y no hay tie-break claro → `UNSUPPORTED` con warning de ambigüedad.
- Si ninguno está habilitado → `UNSUPPORTED` con `blocking_reasons = ["No supported runtime classification found."]`.

Tie-break disponible: si `tank_selection_result.selected_tanks` contiene un único tanque con nombre que incluye "supplier" + "duplicate" → preferir `supplier_duplicate_check`; si incluye "excel" + "diagnostic" → preferir `excel_diagnostic`.

### Regla 6: sufficiency READY + runtime soportado
```
status = READY_FOR_ANALYSIS
suggested_next_state = READY_FOR_ANALYSIS
can_execute = True
```

---

## 6. Runtime classification rules

Clasificaciones permitidas (closed set):

- `excel_diagnostic`
- `supplier_duplicate_check`

Cualquier otra cadena en `enables_classification` es ignorada.

---

## 7. Readiness statuses

| Constante | Valor |
|---|---|
| `READINESS_READY_FOR_ANALYSIS` | `"READY_FOR_ANALYSIS"` |
| `READINESS_NEEDS_EVIDENCE` | `"NEEDS_EVIDENCE"` |
| `READINESS_BLOCKED` | `"BLOCKED"` |
| `READINESS_UNSUPPORTED` | `"UNSUPPORTED"` |

---

## 8. Safety gates

- **Fail-closed** en inputs inválidos.
- **No mutación** de inputs.
- **No ejecución** de runtime.
- **No import** de `excel_diagnostic` ni `supplier_duplicate_check`.
- **Closed set** de clasificaciones runtime.
- **Conservador en ambigüedad**: si dos clasificaciones compiten sin tie-break → `UNSUPPORTED`.

---

## 9. No-goals

Este slice **NO**:

- Abre archivos.
- Lee Excel/PDF.
- Calcula hash.
- Infiere MIME.
- Valida contenido documental.
- Ejecuta diagnóstico.
- Actualiza `intakes.jsonl` ni `evidences.jsonl`.
- Persiste el readiness result.
- Cambia `intake_state`.
- Crea jobs, outputs, CLI ni UI.
- Modifica `storage.py`, `intake.py`, `evidence.py`, `evidence_gate.py`.

---

## 10. Relación con IntakeRecord

`AnalysisReadinessResult` **consume** `IntakeRecord` (o su dict) para:

- leer `intake_state` (regla 1);
- leer `evidence_requests` (regla 5/6);
- leer `tank_selection_result` (tie-break de ambigüedad).

**No modifica** el `IntakeRecord`. La transición real de estado debe hacerse en un slice posterior (`SMARTPYME_INTAKE_STATE_TRANSITION`).

---

## 11. Relación con EvidenceSufficiencyResult

`AnalysisReadinessResult` **consume** `EvidenceSufficiencyResult` (o su dict) para:

- leer `status` (reglas 2, 3, 4, 5);
- propagar `missing_request_ids`, `matched_evidence_ids`, `warnings`, `audit_notes`.

**No modifica** el `EvidenceSufficiencyResult`.

---

## 12. Relación con storage

Este slice **no interactúa con storage**. La integración esperada es externa:

```python
intake = load_intake_record_by_id(tenant_id, intake_id, base_dir=...)
evidences = load_evidence_records_by_intake_id(tenant_id, intake_id, base_dir=...)
suff = evaluate_evidence_sufficiency(intake, evidences)
readiness = evaluate_analysis_readiness(intake, suff)
```

---

## 13. Tests

Cobertura mínima en `tests/smartpyme/test_readiness.py`:

- Import smoke
- Rule 1: `test_blocked_intake_returns_blocked`
- Rule 2: `test_blocked_sufficiency_returns_blocked`
- Rule 3: `test_needs_more_evidence_returns_needs_evidence`
- Rule 4: `test_unsupported_sufficiency_returns_unsupported`
- Rule 5/6: `test_ready_sufficiency_with_excel_runtime_returns_ready`,
  `test_ready_sufficiency_with_supplier_runtime_returns_ready`,
  `test_ready_without_supported_runtime_returns_unsupported`,
  `test_runtime_classification_from_evidence_request`
- Ambigüedad: `test_ambiguous_runtime_returns_unsupported_with_warning`
- Validación: `test_tenant_mismatch_raises`, `test_intake_id_mismatch_raises`,
  `test_invalid_intake_raises`, `test_invalid_sufficiency_raises`,
  `test_unknown_sufficiency_status_raises`, `test_evidence_requests_must_be_list`
- Input handling: `test_accepts_dict_inputs`,
  `test_accepts_dataclass_like_inputs_with_to_dict`,
  `test_inputs_not_mutated`
- Output: `test_to_dict_json_serializable`, `test_missing_request_ids_preserved`,
  `test_matched_evidence_ids_preserved`, `test_warnings_are_lists`
- Runtime isolation: `test_does_not_import_runtime_modules`
- Integración: `test_accepts_evidence_sufficiency_result_dataclass`

---

## 14. Próximo slice recomendado

**`SMARTPYME_INTAKE_STATE_TRANSITION`**

Objetivo:
- Aplicar `AnalysisReadinessResult` para actualizar `intake_state` en `intakes.jsonl`.
- Transición: `NEEDS_EVIDENCE` → `READY_FOR_ANALYSIS` cuando `readiness.status == READY_FOR_ANALYSIS`.
- Integrar con `load_intake_record_by_id`, `evaluate_evidence_sufficiency`, `evaluate_analysis_readiness`, `save_intake_record`.

**Frentes posteriores posibles:**
- `SMARTPYME_READINESS_STORAGE_PERSISTENCE`: persistir `AnalysisReadinessResult` en `readiness.jsonl`.
- `SMARTPYME_EXECUTION_DISPATCH`: dado `can_execute=True`, ejecutar clasificación real (fuera de este slice).
