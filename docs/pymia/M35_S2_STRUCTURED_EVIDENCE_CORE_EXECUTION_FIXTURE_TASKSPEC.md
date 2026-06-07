# M35-S2 — StructuredEvidence Core Execution Fixture TaskSpec

Fecha: 2026-06-07
Frente activo: `M35_EVIDENCE_TO_CORE_BINDING`
Slice: `M35-S2_STRUCTURED_EVIDENCE_CORE_EXECUTION_FIXTURE`

---

## Objetivo

Validar el flujo completo mínimo:

```text
StructuredEvidence realista
→ build_diagnostic_core_input_from_structured_evidence
→ DiagnosticCoreV1
→ resultados calculados o bloqueados
```

Alcance inicial:

```text
REN_001_margen_neto_real
LIQ_001_vendido_cobrado
INV_002_rotacion_stock
```

---

## Archivos permitidos

```text
pymia/diagnostic_core/evidence_binding.py
tests/diagnosticcore/test_evidence_binding_core_execution.py
docs/pymia/M35_S2_STRUCTURED_EVIDENCE_CORE_EXECUTION_FIXTURE_TASKSPEC.md
```

Sólo si es estrictamente necesario:

```text
pymia/diagnostic_core/__init__.py
tests/diagnosticcore/test_evidence_binding.py
```

---

## Archivos read-only

```text
pymia/contracts/evidence_v1.py
pymia/diagnostic_core/core.py
pymia/diagnostic_core/models.py
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

## Reglas

1. No parsear Excel en este slice.
2. Usar `StructuredEvidence` como frontera de entrada.
3. Construir fixture realista con `computed_variables` y `metadata.variable_source_refs`.
4. Ejecutar binder + `DiagnosticCoreV1`.
5. No confirmar patologías.
6. No inventar faltantes.
7. Preservar source refs.
8. Si una fórmula tiene datos incompletos, debe bloquear por input faltante.

---

## Tests obligatorios

### Test 1 — ejecución completa 3 fórmulas

Fixture `StructuredEvidence` con:

```text
sale_price = 1000
costs = 700
taxes = 100
sold_amount = 1000
collected_amount = 650
cost_of_goods_sold = 12000
average_stock = 3000
```

Formula ids:

```text
REN_001_margen_neto_real
LIQ_001_vendido_cobrado
INV_002_rotacion_stock
```

Esperado:

```text
REN_001 = 20.0
LIQ_001 = 350.0
INV_002 = 4.0
3 diagnostic_results en CANDIDATE
source_refs preservados
```

### Test 2 — ejecución parcial con faltante

Fixture sin `taxes`, pero con variables para LIQ_001.

Esperado:

```text
REN_001 bloquea por MISSING_INPUTS: taxes
LIQ_001 calcula 350.0
estado global PARTIAL
no finding confirmado
```

### Test 3 — aliases desde variables de parser

Fixture con aliases:

```text
ventas_total
costos_total
impuestos_total
cobranzas_total
stock_promedio
```

Esperado:

```text
REN_001 calcula
LIQ_001 calcula
INV_002 calcula si hay costos_total + stock_promedio
```

---

## Validación focal

```powershell
python -m pytest tests/diagnosticcore/test_evidence_binding_core_execution.py -v
python -m pytest tests/diagnosticcore/test_evidence_binding.py -v
python -m pytest tests/diagnosticcore/test_diagnostic_core_v1.py -v
```

---

## PASS

PASS si:

```text
- binder + core ejecutan REN_001, LIQ_001, INV_002;
- ejecución parcial bloquea sólo lo incompleto;
- aliases funcionan;
- source_refs se preservan;
- no se confirma diagnóstico;
- no se tocan capas prohibidas;
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
