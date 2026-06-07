# M35-S4 — Excel Fixture to Core Execution TaskSpec

Fecha: 2026-06-07
Frente activo: `M35_EVIDENCE_TO_CORE_BINDING`
Slice: `M35-S4_EXCEL_FIXTURE_TO_CORE_EXECUTION`

---

## Objetivo

Validar el flujo con fixture Excel real ya existente:

```text
Excel fixture
→ parser/evidence existente
→ StructuredEvidence
→ evidence_binding
→ DiagnosticCoreV1
→ cálculo o bloqueo explícito
```

---

## Alcance inicial

Intentar cubrir, según variables reales disponibles en el fixture:

```text
REN_001_margen_neto_real
LIQ_001_vendido_cobrado
INV_002_rotacion_stock
```

Si el fixture no alcanza para calcular alguna fórmula, el resultado correcto es bloqueo explícito por input faltante.

---

## Archivos permitidos

```text
tests/diagnosticcore/test_excel_fixture_core_execution.py
docs/pymia/M35_S4_EXCEL_FIXTURE_TO_CORE_EXECUTION_TASKSPEC.md
```

Sólo si es estrictamente necesario:

```text
pymia/diagnostic_core/evidence_binding.py
```

---

## Archivos read-only

```text
pymia/contracts/evidence_v1.py
pymia/diagnostic_core/core.py
pymia/diagnostic_core/evidence_binding.py
tools/excel_evidence.py
tools/document_ingestion.py
pymia/smartpyme/semantic_field_resolution.py
pymia/smartpyme/xlsx_document_metadata_adapter.py
```

---

## Archivos prohibidos

```text
pymia/services/formula_engine_service.py
pymia/contracts/formula_contract.py
pymia/smartpyme/post_ficha_evidence_gate.py
pymia/smartpyme/anamnesis_fsm.py
conversa-engine/
SmartPyme/
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
```

---

## Fixture preferido

Usar uno de estos si existe en repo:

```text
prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
prueba_excels/distribuidora_mayorista_compleja.xlsx
```

No crear fixture nuevo salvo que no exista ninguno.

---

## Reglas

1. No implementar parser nuevo.
2. Reusar parser/evidence existente.
3. No modificar fórmula engine.
4. No modificar contratos de fórmula.
5. No inventar variables.
6. Si el parser no genera una variable requerida, debe quedar faltante.
7. Preservar `source_refs` si el camino existente los produce.
8. No confirmar diagnósticos.
9. Mantener `CANDIDATE` para fórmulas calculadas.
10. Tests deben reflejar comportamiento real del fixture, no forzar datos manuales ajenos al parser.

---

## Tests obligatorios

### Test 1 — fixture Excel genera StructuredEvidence utilizable

Dado fixture real, construir `StructuredEvidence` usando funciones existentes.

Esperado:

```text
StructuredEvidence válido
computed_variables dict
metadata dict
```

### Test 2 — fixture pasa por binder y core

Ejecutar:

```text
StructuredEvidence
→ build_diagnostic_core_input_from_structured_evidence
→ DiagnosticCoreV1
```

Con fórmula ids:

```text
REN_001_margen_neto_real
LIQ_001_vendido_cobrado
INV_002_rotacion_stock
```

Esperado:

```text
resultado serializable
formula_results presentes
ningún diagnóstico CONFIRMED
si hay datos suficientes: fórmula OK
si faltan datos: fórmula BLOCKED con missing input
```

### Test 3 — no inventa faltantes

Si alguna variable requerida no aparece en `computed_variables`, verificar que:

```text
no aparece inventada en DiagnosticCoreInput.variables
la fórmula correspondiente bloquea
```

---

## Validación focal

```powershell
python -m pytest tests/diagnosticcore/test_excel_fixture_core_execution.py -v
python -m pytest tests/diagnosticcore/test_evidence_binding_core_execution.py -v
python -m pytest tests/diagnosticcore/test_evidence_binding.py -v
```

---

## PASS

PASS si:

```text
- fixture real entra al flujo;
- se genera StructuredEvidence válido;
- binder produce DiagnosticCoreInput;
- core devuelve resultados calculados o bloqueados;
- no se inventan variables;
- no se confirman diagnósticos;
- no se tocan capas prohibidas;
- tests focales pasan;
- commit local sin push.
```

---

## BLOCKED aceptable

BLOCKED válido si:

```text
- no existe fixture Excel;
- no hay función existente para convertir fixture a StructuredEvidence;
- usar el fixture exigiría crear parser nuevo;
- el contrato real de StructuredEvidence no permite representar la salida actual.
```

En ese caso no implementar workaround.

---

## Salida obligatoria Codex

```text
VEREDICTO
FILES CHANGED
DIFF SUMMARY
TEST RESULTS
COMMIT HASH o BLOCKED_REASON
GIT STATUS FINAL
CONFIRMACIÓN NO PUSH
```
