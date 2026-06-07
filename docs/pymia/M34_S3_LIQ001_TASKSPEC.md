# M34-S3 — LIQ_001 Vendido Cobrado TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S3_LIQ_001_VENDIDO_COBRADO`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
LIQ_001_vendido_cobrado
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
formula_id: LIQ_001_vendido_cobrado
pathology_code: LIQ_001
expression: sold_amount - collected_amount
required_variables:
  - sold_amount
  - collected_amount
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
docs/pymia/M34_S3_LIQ001_TASKSPEC.md
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

1. Agregar `LIQ_001_vendido_cobrado` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `sold_amount`
   - `collected_amount`
4. Bloquear si falta cualquier input.
5. Permitir resultado cero.
6. Permitir resultado negativo; no interpretar todavía.
7. Devolver moneda/currency como valor numérico.
8. Preservar `source_refs`.
9. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
10. No cambiar comportamiento de `margen_bruto`, `ganancia_bruta` ni `REN_001_margen_neto_real`.

---

## Tests obligatorios

### Test LIQ_001 OK

Entrada:

```text
sold_amount = 1000
collected_amount = 650
```

Resultado esperado:

```text
status = OK
value = 350.0
source_refs preservados
```

### Test LIQ_001 bloquea input faltante

Entrada:

```text
sold_amount = 1000
collected_amount faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: collected_amount"
```

### Test LIQ_001 permite cero

Entrada:

```text
sold_amount = 1000
collected_amount = 1000
```

Resultado esperado:

```text
status = OK
value = 0.0
```

### Test DiagnosticCoreV1 integra LIQ_001 sin confirmar

Entrada:

```text
formula_id = LIQ_001_vendido_cobrado
sold_amount = 1000
collected_amount = 650
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 350.0
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
- LIQ_001_vendido_cobrado calcula correctamente;
- inputs faltantes bloquean;
- resultado cero funciona;
- source_refs se preservan;
- DiagnosticCoreV1 mantiene CANDIDATE, no CONFIRMED;
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
