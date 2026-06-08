# M34-S13 — PYME_027 Intereses EBITDA TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S13_PYME_027_INTERESES_EBITDA`

---

## Objetivo

Implementar soporte determinístico para la fórmula:

```text
PYME_027_intereses_ebitda
```

---

## Fórmula fuente

Fuente documental:

```text
docs/formula_catalog.v1.json
```

Contrato de fórmula:

```text
formula_id: PYME_027_intereses_ebitda
pathology_code: PYME_027
expression: interest_expense / ebitda
required_variables:
  - interest_expense
  - ebitda
output_unit: ratio
```

---

## Archivos permitidos

```text
pymia/contracts/formula_contract.py
pymia/services/formula_engine_service.py
pymia/diagnostic_core/core.py
tests/services/test_formula_engine_service.py
tests/diagnosticcore/test_diagnostic_core_v1.py
docs/pymia/M34_S13_PYME027_INTERESES_EBITDA_TASKSPEC.md
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

## Reglas

1. Agregar `PYME_027_intereses_ebitda` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo exacto: `interest_expense / ebitda`.
3. Requerir exactamente:
   - `interest_expense`
   - `ebitda`
4. Bloquear si falta cualquier input.
5. Bloquear división por cero si `ebitda == 0`.
6. Permitir resultado cero si `interest_expense == 0`.
7. Preservar `source_refs`.
8. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
9. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

### Test OK

Entrada:

```text
interest_expense = 500
ebitda = 2500
```

Resultado esperado:

```text
status = OK
value = 0.2
source_refs preservados
```

### Test input faltante

Entrada:

```text
interest_expense = 500
ebitda faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: ebitda"
```

### Test división por cero

Entrada:

```text
interest_expense = 500
ebitda = 0
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "DIVISION_BY_ZERO: ebitda"
```

### Test cero permitido

Entrada:

```text
interest_expense = 0
ebitda = 2500
```

Resultado esperado:

```text
status = OK
value = 0.0
```

### Test DiagnosticCoreV1

Entrada:

```text
formula_id = PYME_027_intereses_ebitda
interest_expense = 500
ebitda = 2500
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 0.2
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
- PYME_027_intereses_ebitda calcula correctamente;
- input faltante bloquea;
- ebitda cero bloquea;
- interest_expense cero funciona;
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
