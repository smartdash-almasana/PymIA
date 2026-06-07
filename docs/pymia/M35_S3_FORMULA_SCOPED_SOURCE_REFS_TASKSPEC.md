# M35-S3 — Formula Scoped Source Refs TaskSpec

Fecha: 2026-06-07
Frente activo: `M35_EVIDENCE_TO_CORE_BINDING`
Slice: `M35-S3_FORMULA_SCOPED_SOURCE_REFS`

---

## Objetivo

Ajustar `DiagnosticCoreV1` para que cada `formula_result.source_refs` conserve sólo las referencias de evidencia usadas por esa fórmula.

Actualmente, cuando el core recibe un pool común de variables, cada fórmula puede arrastrar `source_refs` de variables que no usa.

---

## Alcance

```text
DiagnosticCoreInput
→ DiagnosticCoreV1
→ FormulaEngineService
→ CoreFormulaResult.source_refs específicos por fórmula
```

---

## Archivos permitidos

```text
pymia/diagnostic_core/core.py
tests/diagnosticcore/test_diagnostic_core_v1.py
tests/diagnosticcore/test_evidence_binding_core_execution.py
docs/pymia/M35_S3_FORMULA_SCOPED_SOURCE_REFS_TASKSPEC.md
```

Sólo si es estrictamente necesario:

```text
pymia/diagnostic_core/models.py
```

---

## Archivos read-only

```text
pymia/contracts/formula_contract.py
pymia/services/formula_engine_service.py
pymia/diagnostic_core/evidence_binding.py
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

## Regla de implementación

1. El core debe pasar a cada fórmula sólo los inputs requeridos por esa fórmula.
2. No modificar `FormulaEngineService` si no es necesario.
3. No cambiar contratos de fórmula existentes.
4. No perder bloqueos por input faltante.
5. No inventar variables.
6. No confirmar diagnósticos.
7. Mantener estado `CANDIDATE` para fórmulas OK.
8. Preservar tests existentes.

---

## Comportamiento esperado

Dado un `DiagnosticCoreInput` con variables para varias fórmulas:

```text
sale_price → sheet:ventas
costs → sheet:costos
taxes → sheet:impuestos
sold_amount → sheet:ventas
collected_amount → sheet:cobranzas
cost_of_goods_sold → sheet:cmv
average_stock → sheet:stock
```

Al ejecutar:

```text
REN_001_margen_neto_real
LIQ_001_vendido_cobrado
INV_002_rotacion_stock
```

Debe ocurrir:

```text
REN_001.source_refs = sheet:ventas, sheet:costos, sheet:impuestos
LIQ_001.source_refs = sheet:ventas, sheet:cobranzas
INV_002.source_refs = sheet:cmv, sheet:stock
```

No debe aparecer el pool completo en cada fórmula.

---

## Tests obligatorios

### Test 1 — source_refs scoped por fórmula en DiagnosticCoreV1

Crear o ajustar test para tres fórmulas simultáneas:

```text
REN_001_margen_neto_real
LIQ_001_vendido_cobrado
INV_002_rotacion_stock
```

Esperado:

```text
cada formula_result.source_refs contiene sólo refs de sus inputs requeridos
```

### Test 2 — source_refs scoped en flujo binder + core

Ajustar `test_evidence_binding_core_execution.py` para exigir refs por fórmula, no pool común.

### Test 3 — input faltante sigue bloqueando

Verificar que filtrar inputs por fórmula no rompe:

```text
REN_001 sin taxes → MISSING_INPUTS: taxes
LIQ_001 completo → OK
estado global PARTIAL
```

---

## Validación focal

```powershell
python -m pytest tests/diagnosticcore/test_diagnostic_core_v1.py -v
python -m pytest tests/diagnosticcore/test_evidence_binding_core_execution.py -v
python -m pytest tests/diagnosticcore/test_evidence_binding.py -v
```

---

## PASS

PASS si:

```text
- source_refs quedan acotados por fórmula;
- no se rompe bloqueo por input faltante;
- binder + core siguen ejecutando;
- no se modifica FormulaEngineService salvo justificación fuerte;
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
