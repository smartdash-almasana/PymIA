# M34-S6 — PYME_013 DSO DPO Gap TaskSpec

Fecha: 2026-06-07
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S6_PYME_013_DSO_DPO_GAP`

---

## Objetivo

Implementar soporte determinístico mínimo para la fórmula:

```text
PYME_013_dso_dpo_gap
```

---

## Fórmula fuente

Fuente documental:

```text
docs/formula_catalog.v1.json
```

Contrato de fórmula:

```text
formula_id: PYME_013_dso_dpo_gap
pathology_code: PYME_013
expression: dso - dpo
required_variables:
  - dso
  - dpo
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
docs/pymia/M34_S6_PYME013_DSO_DPO_GAP_TASKSPEC.md
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

1. Agregar `PYME_013_dso_dpo_gap` a `SUPPORTED_FORMULAS`.
2. Implementar cálculo en `FormulaEngineService`.
3. Requerir exactamente:
   - `dso`
   - `dpo`
4. Bloquear si falta cualquier input.
5. Permitir resultado positivo, cero o negativo.
6. Devolver días como número.
7. Preservar `source_refs`.
8. `DiagnosticCoreV1` debe mantener `CANDIDATE`, no `CONFIRMED`.
9. No cambiar comportamiento de fórmulas previas.

---

## Tests obligatorios

### Test PYME_013 OK

Entrada:

```text
dso = 45
dpo = 30
```

Resultado esperado:

```text
status = OK
value = 15.0
source_refs preservados
```

### Test PYME_013 permite cero

Entrada:

```text
dso = 30
dpo = 30
```

Resultado esperado:

```text
status = OK
value = 0.0
```

### Test PYME_013 permite negativo

Entrada:

```text
dso = 25
dpo = 40
```

Resultado esperado:

```text
status = OK
value = -15.0
```

### Test PYME_013 bloquea input faltante

Entrada:

```text
dso = 45
dpo faltante
```

Resultado esperado:

```text
status = BLOCKED
blocking_reason == "MISSING_INPUTS: dpo"
```

### Test DiagnosticCoreV1 integra PYME_013 sin confirmar

Entrada:

```text
formula_id = PYME_013_dso_dpo_gap
dso = 45
dpo = 30
```

Resultado esperado:

```text
formula_result.status = OK
formula_result.value = 15.0
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
- PYME_013_dso_dpo_gap calcula correctamente;
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
