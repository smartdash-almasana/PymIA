# M34-S5 — PYME_011 DSO TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S5_PYME_011_DSO`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
PYME_011_dso
```

---

## Fórmula fuente

Fuente documental:

```text
docs/formula_catalog.v1.json
```

Contrato de fórmula:

```text
formula_id: PYME_011_dso
pathology_code: PYME_011
expression: accounts_receivable / sales * days
required_variables:
  - accounts_receivable
  - sales
  - days
output_unit: days
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
docs/pymia/M34_S5_PYME011_DSO_TASKSPEC.md
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

1. Agregar `PYME_011_dso` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `accounts_receivable`
   - `sales`
   - `days`
4. Bloquear si falta cualquier input.
5. Bloquear división por cero si `sales == 0`.
6. Devolver días como número.
7. Preservar `source_refs`.
8. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
9. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

### Test PYME_011 OK

Entrada:

```text
accounts_receivable = 3000
sales = 12000
days = 30
```

Resultado esperado:

```text
status = OK
value = 7.5
source_refs preservados
```

### Test PYME_011 bloquea input faltante

Entrada:

```text
accounts_receivable = 3000
sales = 12000
days faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: days"
```

### Test PYME_011 bloquea división por cero

Entrada:

```text
accounts_receivable = 3000
sales = 0
days = 30
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "DIVISION_BY_ZERO: sales"
```

### Test DiagnosticCoreV1 integra PYME_011 sin confirmar

Entrada:

```text
formula_id = PYME_011_dso
accounts_receivable = 3000
sales = 12000
days = 30
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 7.5
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
- PYME_011_dso calcula correctamente;
- inputs faltantes bloquean;
- sales cero bloquea;
- source_refs se preservan;
- DiagnosticCoreV1 mantiene CANDIDATE, no CONFIRMED;
- no se altera REN_001, LIQ_001, INV_002 ni fórmulas previas;
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
