# M34-S2 — REN_001 Margen Neto Real TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S2_REN_001_MARGEN_NETO_REAL`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
REN_001_margen_neto_real
```

sin tocar Telegram, SmartPyme legacy, tools, conversa-engine ni runtime.

---

## Fórmula fuente

Fuente documental:

```text
docs/formula_catalog.v1.json
```

Contrato de fórmula:

```text
formula_id: REN_001_margen_neto_real
pathology_code: REN_001
expression: ((sale_price - costs - taxes) / sale_price) * 100
required_variables:
  - sale_price
  - costs
  - taxes
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
```

Opcional sólo si es estrictamente necesario:

```text
docs/pymia/M34_S2_REN001_TASKSPEC.md
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

1. Agregar `REN_001_margen_neto_real` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `sale_price`
   - `costs`
   - `taxes`
4. Bloquear si falta cualquier input.
5. Bloquear división por cero si `sale_price == 0`.
6. Devolver porcentaje, no ratio.
7. Preservar `source_refs`.
8. No confirmar patología como `CONFIRMED` en `DiagnosticCoreV1` todavía; M34-S2 sólo habilita fórmula.
9. No implementar LIQ_001.
10. No cambiar comportamiento de `margen_bruto` ni `ganancia_bruta`.

---

## Tests obligatorios

### Test fórmula REN_001 OK

Entrada:

```text
sale_price = 1000
costs = 700
taxes = 100
```

Resultado esperado:

```text
status = OK
value = 20.0
source_refs preservados
```

### Test REN_001 bloquea input faltante

Entrada:

```text
sale_price = 1000
costs = 700
taxes faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason incluye MISSING_INPUTS: taxes
```

### Test REN_001 bloquea división por cero

Entrada:

```text
sale_price = 0
costs = 700
taxes = 100
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason incluye DIVISION_BY_ZERO: sale_price
```

### Test DiagnosticCoreV1 ya no bloquea REN_001 por fórmula no soportada

Entrada:

```text
formula_id = REN_001_margen_neto_real
sale_price = 1000
costs = 700
taxes = 100
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

Codex debe ejecutar sólo:

```powershell
python -m pytest tests/services/test_formula_engine_service.py -v
python -m pytest tests/diagnosticcore/test_diagnostic_core_v1.py -v
```

No correr suite grande.

---

## PASS

PASS si:

```text
- REN_001_margen_neto_real calcula correctamente;
- inputs faltantes bloquean;
- división por cero bloquea;
- source_refs se preservan;
- DiagnosticCoreV1 mantiene estado CANDIDATE, no CONFIRMED;
- no se toca LIQ_001;
- no se toca Telegram, SmartPyme, tools ni conversa-engine;
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
