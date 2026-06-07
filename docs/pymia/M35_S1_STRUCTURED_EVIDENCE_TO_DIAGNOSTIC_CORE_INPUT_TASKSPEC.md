# M35-S1 — StructuredEvidence to DiagnosticCoreInput TaskSpec

Fecha: 2026-06-07
Frente activo: `M35_EVIDENCE_TO_CORE_BINDING`
Slice: `M35-S1_STRUCTURED_EVIDENCE_TO_DIAGNOSTIC_CORE_INPUT`

---

## Objetivo

Crear el primer binding determinístico entre evidencia estructurada y el núcleo M34.

```text
StructuredEvidence / computed_variables
→ DiagnosticCoreInput
→ DiagnosticCoreV1
```

Alcance inicial:

```text
REN_001_margen_neto_real
LIQ_001_vendido_cobrado
INV_002_rotacion_stock
```

---

## Puertos afectados

```text
EVIDENCE_STATUS_PORT
FORMULA_EXECUTION_PORT
DIAGNOSTIC_RESULT_PORT
```

## Gates afectados

```text
EVIDENCE_SUFFICIENCY_GATE
FORMULA_INPUT_GATE
DIAGNOSTIC_EVIDENCE_GATE
```

---

## Archivos permitidos

```text
pymia/diagnostic_core/evidence_binding.py
pymia/diagnostic_core/__init__.py
tests/diagnosticcore/test_evidence_binding.py
docs/pymia/M35_S1_STRUCTURED_EVIDENCE_TO_DIAGNOSTIC_CORE_INPUT_TASKSPEC.md
```

Sólo si es estrictamente necesario:

```text
pymia/diagnostic_core/models.py
```

---

## Archivos read-only

```text
pymia/contracts/evidence_v1.py
pymia/diagnostic_core/core.py
pymia/contracts/formula_contract.py
pymia/services/formula_engine_service.py
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

1. Crear un adapter/binder puro, sin efectos laterales.
2. No leer archivos Excel directamente.
3. No parsear documentos.
4. No modificar FormulaEngineService.
5. No confirmar patologías.
6. No inventar variables faltantes.
7. Preservar `source_refs` cuando existan.
8. Si faltan variables, dejar que `DiagnosticCoreV1` bloquee por inputs faltantes.
9. Output principal: `DiagnosticCoreInput`.

---

## Mapping mínimo esperado

### REN_001_margen_neto_real

```text
sale_price ← computed_variables.sale_price o computed_variables.ventas_total
costs ← computed_variables.costs o computed_variables.costos_total
taxes ← computed_variables.taxes o computed_variables.impuestos_total
```

### LIQ_001_vendido_cobrado

```text
sold_amount ← computed_variables.sold_amount o computed_variables.ventas_total
collected_amount ← computed_variables.collected_amount o computed_variables.cobranzas_total
```

### INV_002_rotacion_stock

```text
cost_of_goods_sold ← computed_variables.cost_of_goods_sold o computed_variables.costos_total
average_stock ← computed_variables.average_stock o computed_variables.stock_promedio
```

---

## API esperada

Codex puede ajustar nombres, pero debe preservar esta semántica:

```python
build_diagnostic_core_input_from_structured_evidence(
    evidence,
    *,
    case_id: str,
    tenant_id: str,
    formula_ids: list[str],
    hypothesis_codes: list[str] | None = None,
) -> DiagnosticCoreInput
```

---

## Tests obligatorios

### Test 1 — REN_001 mapping completo

Dado `computed_variables` con:

```text
sale_price=1000
costs=700
taxes=100
```

Debe devolver `DiagnosticCoreInput` con esas variables y fórmula `REN_001_margen_neto_real`.

### Test 2 — LIQ_001 mapping completo

Dado `computed_variables` con:

```text
sold_amount=1000
collected_amount=650
```

Debe devolver variables correctas para `LIQ_001_vendido_cobrado`.

### Test 3 — INV_002 mapping completo

Dado `computed_variables` con:

```text
cost_of_goods_sold=12000
average_stock=3000
```

Debe devolver variables correctas para `INV_002_rotacion_stock`.

### Test 4 — no inventa faltantes

Dado REN_001 sin `taxes`, el input no debe inventar `taxes`.

### Test 5 — integración con DiagnosticCoreV1

Con evidencia suficiente para REN_001, el binder + core debe calcular `20.0` y devolver `CANDIDATE`, no `CONFIRMED`.

---

## Validación focal

```powershell
python -m pytest tests/diagnosticcore/test_evidence_binding.py -v
python -m pytest tests/diagnosticcore/test_diagnostic_core_v1.py -v
```

---

## PASS

PASS si:

```text
- crea DiagnosticCoreInput desde StructuredEvidence/computed_variables;
- soporta REN_001, LIQ_001, INV_002;
- no inventa faltantes;
- preserva source_refs si existen;
- integración con DiagnosticCoreV1 calcula cuando hay datos;
- no toca capas prohibidas;
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
