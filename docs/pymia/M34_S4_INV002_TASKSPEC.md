# M34-S4 — INV_002 Rotación de Stock TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S4_INV_002_ROTACION_STOCK`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
INV_002_rotacion_stock
```

---

## Fórmula fuente

Fuente documental:

```text
docs/formula_catalog.v1.json
```

Contrato de fórmula:

```text
formula_id: INV_002_rotacion_stock
pathology_code: INV_002
expression: cost_of_goods_sold / average_stock
required_variables:
  - cost_of_goods_sold
  - average_stock
output_unit: ratio
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
docs/pymia/M34_S4_INV002_TASKSPEC.md
```

---

## Archivos prohibidos

```text
pymia/telegram_bot_runtime.py
pymia/telegram_document_handler.py
pymia/smartpyme/
conversa-engine/
tools/
SmartPyme/
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
```

---

## Reglas de implementación

1. Agregar `INV_002_rotacion_stock` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `cost_of_goods_sold`
   - `average_stock`
4. Bloquear si falta cualquier input.
5. Bloquear división por cero si `average_stock == 0`.
6. Devolver ratio numérico.
7. Preservar `source_refs`.
8. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
9. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

### Test INV_002 OK

Entrada:

```text
cost_of_goods_sold = 12000
average_stock = 3000
```

Resultado esperado:

```text
status = OK
value = 4.0
source_refs preservados
```

### Test INV_002 bloquea input faltante

Entrada:

```text
cost_of_goods_sold = 12000
average_stock faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: average_stock"
```

### Test INV_002 bloquea división por cero

Entrada:

```text
cost_of_goods_sold = 12000
average_stock = 0
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "DIVISION_BY_ZERO: average_stock"
```

### Test DiagnosticCoreV1 integra INV_002 sin confirmar

Entrada:

```text
formula_id = INV_002_rotacion_stock
cost_of_goods_sold = 12000
average_stock = 3000
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 4.0
diagnostic_result.status = CANDIDATE
no CONFIRMED
source_refs preservados
```

---

## Validación focal

Codex debe ejecutar sólo:

```powershell
python -m pytest tests/services/test_formula_engine_service.py -v
python -m pytest tests/diagnosticcore/test_diagnostic_core_v1.py -v
```

---

## PASS

PASS si:

```text
- INV_002_rotacion_stock calcula correctamente;
- inputs faltantes bloquean;
- average_stock cero bloquea;
- source_refs se preservan;
- DiagnosticCoreV1 mantiene CANDIDATE, no CONFIRMED;
- no se altera REN_001, LIQ_001 ni fórmulas previas;
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
