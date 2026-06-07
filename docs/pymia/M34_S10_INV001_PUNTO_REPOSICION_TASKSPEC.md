# M34-S10 — INV_001 Punto de Reposición TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S10_INV_001_PUNTO_REPOSICION`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
INV_001_punto_reposicion
```

---

## Fórmula fuente

Fuente documental:

```text
docs/formula_catalog.v1.json
```

Contrato de fórmula:

```text
formula_id: INV_001_punto_reposicion
pathology_code: INV_001
expression: (average_sales * lead_time) + safety_stock
required_variables:
  - average_sales
  - lead_time
  - safety_stock
output_unit: units
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
docs/pymia/M34_S10_INV001_PUNTO_REPOSICION_TASKSPEC.md
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

1. Agregar `INV_001_punto_reposicion` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `average_sales`
   - `lead_time`
   - `safety_stock`
4. Bloquear si falta cualquier input.
5. Permitir resultado cero.
6. Permitir resultado decimal si los inputs son decimales.
7. Devolver unidades como número.
8. Preservar `source_refs`.
9. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
10. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

### Test INV_001 OK

Entrada:

```text
average_sales = 20
lead_time = 5
safety_stock = 30
```

Resultado esperado:

```text
status = OK
value = 130.0
source_refs preservados
```

### Test INV_001 permite cero

Entrada:

```text
average_sales = 0
lead_time = 5
safety_stock = 0
```

Resultado esperado:

```text
status = OK
value = 0.0
```

### Test INV_001 permite decimal

Entrada:

```text
average_sales = 12.5
lead_time = 4
safety_stock = 10
```

Resultado esperado:

```text
status = OK
value = 60.0
```

### Test INV_001 bloquea input faltante

Entrada:

```text
average_sales = 20
lead_time = 5
safety_stock faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: safety_stock"
```

### Test DiagnosticCoreV1 integra INV_001 sin confirmar

Entrada:

```text
formula_id = INV_001_punto_reposicion
average_sales = 20
lead_time = 5
safety_stock = 30
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 130.0
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
- INV_001_punto_reposicion calcula correctamente;
- input faltante bloquea;
- cero y decimal funcionan;
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
