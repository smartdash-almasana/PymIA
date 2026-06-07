# M34-S7 — LIQ_002 Saldo Final Proyectado TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S7_LIQ_002_SALDO_FINAL_PROYECTADO`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
LIQ_002_saldo_final_proyectado
```

---

## Fórmula fuente

Fuente documental:

```text
docs/formula_catalog.v1.json
```

Contrato de fórmula:

```text
formula_id: LIQ_002_saldo_final_proyectado
pathology_code: LIQ_002
expression: initial_balance + expected_collections - expected_payments
required_variables:
  - initial_balance
  - expected_collections
  - expected_payments
output_unit: currency
```

---

## Puertos afectados

```text
FORMULA_EXECUTION_PORT
DIAGNOSTIC_RESULT_PORT
FINDING_PORT
```

## Gates afectados

```text
FORMULA_INPUT_GATE
DIAGNOSTIC_EVIDENCE_GATE
FINDING_GROUNDING_GATE
```

---

## Archivos permitidos

```text
pymia/contracts/formula_contract.py
pymia/services/formula_engine_service.py
pymia/diagnostic_core/core.py
tests/services/test_formula_engine_service.py
tests/diagnosticcore/test_diagnostic_core_v1.py
docs/pymia/M34_S7_LIQ002_SALDO_FINAL_PROYECTADO_TASKSPEC.md
```

---

## Archivos prohibidos

```text
pymia/smartpyme/
conversa-engine/
tools/
SmartPyme/
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
```

---

## Reglas de implementación

1. Agregar `LIQ_002_saldo_final_proyectado` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `initial_balance`
   - `expected_collections`
   - `expected_payments`
4. Bloquear si falta cualquier input.
5. Permitir resultado positivo, cero o negativo.
6. Devolver moneda como número.
7. Preservar `source_refs`.
8. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
9. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

### Test LIQ_002 OK

Entrada:

```text
initial_balance = 1000
expected_collections = 5000
expected_payments = 4200
```

Resultado esperado:

```text
status = OK
value = 1800.0
source_refs preservados
```

### Test LIQ_002 permite cero

Entrada:

```text
initial_balance = 1000
expected_collections = 3000
expected_payments = 4000
```

Resultado esperado:

```text
status = OK
value = 0.0
```

### Test LIQ_002 permite negativo

Entrada:

```text
initial_balance = 1000
expected_collections = 2000
expected_payments = 4000
```

Resultado esperado:

```text
status = OK
value = -1000.0
```

### Test LIQ_002 bloquea input faltante

Entrada:

```text
initial_balance = 1000
expected_collections = 5000
expected_payments faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: expected_payments"
```

### Test DiagnosticCoreV1 integra LIQ_002 sin confirmar

Entrada:

```text
formula_id = LIQ_002_saldo_final_proyectado
initial_balance = 1000
expected_collections = 5000
expected_payments = 4200
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 1800.0
diagnostic_result.status = CANDIDATE
no CONFIRMED
source_refs preservados
```

---

## Validación focal

```powershell
python -m pytest tests/services/test_formula_engine_service.py -v
python -m pytest tests/diagnosticcore/test_diagnostic_core_v1.py -v
```

---

## PASS

PASS si:

```text
- LIQ_002_saldo_final_proyectado calcula correctamente;
- input faltante bloquea;
- cero y negativo funcionan;
- source_refs se preservan;
- DiagnosticCoreV1 mantiene CANDIDATE, no CONFIRMED;
- no se alteran fórmulas previas;
- tests focales pasan;
- commit local sin push.
```

---

## Salida obligatoria Codex

```text
VEREDICTO
FILES CHANGED
DIFF SUMMARY
TEST RESULTS
COMMIT HASH
GIT STATUS FINAL
CONFIRMACIÓN NO PUSH
```
