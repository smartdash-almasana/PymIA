# M34-S8 — PYME_024 Liquidez Corriente TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S8_PYME_024_LIQUIDEZ_CORRIENTE`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
PYME_024_liquidez_corriente
```

---

## Fórmula fuente

Fuente documental:

```text
docs/formula_catalog.v1.json
```

Contrato de fórmula:

```text
formula_id: PYME_024_liquidez_corriente
pathology_code: PYME_024
expression: current_assets / current_liabilities
required_variables:
  - current_assets
  - current_liabilities
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
docs/pymia/M34_S8_PYME024_LIQUIDEZ_CORRIENTE_TASKSPEC.md
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

1. Agregar `PYME_024_liquidez_corriente` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `current_assets`
   - `current_liabilities`
4. Bloquear si falta cualquier input.
5. Bloquear división por cero si `current_liabilities == 0`.
6. Devolver ratio numérico.
7. Preservar `source_refs`.
8. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
9. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

### Test PYME_024 OK

Entrada:

```text
current_assets = 15000
current_liabilities = 10000
```

Resultado esperado:

```text
status = OK
value = 1.5
source_refs preservados
```

### Test PYME_024 bloquea input faltante

Entrada:

```text
current_assets = 15000
current_liabilities faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: current_liabilities"
```

### Test PYME_024 bloquea división por cero

Entrada:

```text
current_assets = 15000
current_liabilities = 0
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "DIVISION_BY_ZERO: current_liabilities"
```

### Test DiagnosticCoreV1 integra PYME_024 sin confirmar

Entrada:

```text
formula_id = PYME_024_liquidez_corriente
current_assets = 15000
current_liabilities = 10000
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 1.5
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
- PYME_024_liquidez_corriente calcula correctamente;
- input faltante bloquea;
- current_liabilities cero bloquea;
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
