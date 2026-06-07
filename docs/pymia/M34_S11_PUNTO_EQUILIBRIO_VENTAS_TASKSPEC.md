# M34-S11 — Punto de Equilibrio en Ventas TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S11_PUNTO_EQUILIBRIO_VENTAS`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
punto_equilibrio_ventas
```

---

## Fórmula fuente

Fuente documental:

```text
docs/ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md
```

Nota: esta fórmula está documentada como fórmula inicial, pero no figura todavía en `docs/formula_catalog.v1.json`. En este slice se implementa en el motor determinístico sin modificar catálogos JSON.

Contrato de fórmula:

```text
formula_id: punto_equilibrio_ventas
expression: fixed_costs / contribution_margin_rate
required_variables:
  - fixed_costs
  - contribution_margin_rate
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
docs/pymia/M34_S11_PUNTO_EQUILIBRIO_VENTAS_TASKSPEC.md
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

1. Agregar `punto_equilibrio_ventas` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `fixed_costs`
   - `contribution_margin_rate`
4. Bloquear si falta cualquier input.
5. Bloquear división por cero si `contribution_margin_rate == 0`.
6. Bloquear si `contribution_margin_rate < 0`, con `INVALID_INPUT: contribution_margin_rate`.
7. Permitir resultado cero si `fixed_costs == 0`.
8. Devolver moneda como número.
9. Preservar `source_refs`.
10. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
11. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

### Test punto equilibrio OK

Entrada:

```text
fixed_costs = 10000
contribution_margin_rate = 0.25
```

Resultado esperado:

```text
status = OK
value = 40000.0
source_refs preservados
```

### Test punto equilibrio permite cero

Entrada:

```text
fixed_costs = 0
contribution_margin_rate = 0.25
```

Resultado esperado:

```text
status = OK
value = 0.0
```

### Test punto equilibrio bloquea input faltante

Entrada:

```text
fixed_costs = 10000
contribution_margin_rate faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: contribution_margin_rate"
```

### Test punto equilibrio bloquea división por cero

Entrada:

```text
fixed_costs = 10000
contribution_margin_rate = 0
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "DIVISION_BY_ZERO: contribution_margin_rate"
```

### Test punto equilibrio bloquea margen negativo

Entrada:

```text
fixed_costs = 10000
contribution_margin_rate = -0.1
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "INVALID_INPUT: contribution_margin_rate"
```

### Test DiagnosticCoreV1 integra punto equilibrio sin confirmar

Entrada:

```text
formula_id = punto_equilibrio_ventas
fixed_costs = 10000
contribution_margin_rate = 0.25
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 40000.0
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
- punto_equilibrio_ventas calcula correctamente;
- input faltante bloquea;
- contribution_margin_rate cero bloquea;
- contribution_margin_rate negativo bloquea;
- fixed_costs cero funciona;
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
