# M34-S9 — PYME_017 Pricing Drift TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S9_PYME_017_PRICING_DRIFT`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
PYME_017_pricing_drift
```

---

## Fórmula fuente

Fuente documental:

```text
docs/formula_catalog.v1.json
```

Contrato de fórmula:

```text
formula_id: PYME_017_pricing_drift
pathology_code: PYME_017
expression: (own_price - market_price) / market_price * 100
required_variables:
  - own_price
  - market_price
output_unit: percentage
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
docs/pymia/M34_S9_PYME017_PRICING_DRIFT_TASKSPEC.md
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

1. Agregar `PYME_017_pricing_drift` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `own_price`
   - `market_price`
4. Bloquear si falta cualquier input.
5. Bloquear división por cero si `market_price == 0`.
6. Permitir resultado positivo, cero o negativo.
7. Devolver porcentaje como número.
8. Preservar `source_refs`.
9. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
10. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

### Test PYME_017 OK positivo

Entrada:

```text
own_price = 120
market_price = 100
```

Resultado esperado:

```text
status = OK
value = 20.0
source_refs preservados
```

### Test PYME_017 permite cero

Entrada:

```text
own_price = 100
market_price = 100
```

Resultado esperado:

```text
status = OK
value = 0.0
```

### Test PYME_017 permite negativo

Entrada:

```text
own_price = 90
market_price = 100
```

Resultado esperado:

```text
status = OK
value = -10.0
```

### Test PYME_017 bloquea input faltante

Entrada:

```text
own_price = 120
market_price faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: market_price"
```

### Test PYME_017 bloquea división por cero

Entrada:

```text
own_price = 120
market_price = 0
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "DIVISION_BY_ZERO: market_price"
```

### Test DiagnosticCoreV1 integra PYME_017 sin confirmar

Entrada:

```text
formula_id = PYME_017_pricing_drift
own_price = 120
market_price = 100
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 20.0
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
- PYME_017_pricing_drift calcula correctamente;
- input faltante bloquea;
- market_price cero bloquea;
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
