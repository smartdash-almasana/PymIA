# M36 — Ports and Gates Foundation TaskSpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente activo: `M36_PORTS_AND_GATES_AUTHORIZATION`

---

## 1. Objetivo

Implementar la base mínima ejecutable de puertos y gates entre evidencia y core, sin abrir un nuevo frente de diagnóstico.

El slice total de M36 queda dividido en:

```text
M36-S1 — Port Contract Skeleton
M36-S2 — Formula Input Gate
M36-S3 — Evidence Sufficiency Gate
```

---

## 2. Arquitectura objetivo

```text
StructuredEvidence
→ FormulaInputGate
→ EvidenceSufficiencyGate
→ DiagnosticCoreV1
```

---

## 3. Contratos mínimos

### FormulaInputGateResult

- `formula_id`
- `required_variables`
- `available_variables`
- `missing_variables`
- `status`

Estados:

- `READY`
- `MISSING_INPUTS`

### EvidenceGateDecision

- `formula_id`
- `decision`
- `missing_variables`

Decisiones:

- `ALLOW_EXECUTION`
- `BLOCK_MISSING_INPUTS`

---

## 4. Archivos permitidos

```text
pymia/diagnostic_core/evidence_sufficiency.py
pymia/diagnostic_core/models.py
pymia/diagnostic_core/__init__.py
tests/diagnosticcore/test_evidence_sufficiency.py
docs/pymia/M36_PORTS_AND_GATES_FOUNDATION_TASKSPEC.md
```

Sólo si es estrictamente necesario:

```text
pymia/diagnostic_core/evidence_binding.py
tests/diagnosticcore/test_evidence_binding.py
```

---

## 5. Archivos read-only

```text
pymia/contracts/evidence_v1.py
pymia/contracts/formula_contract.py
pymia/diagnostic_core/core.py
docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md
docs/pymia/M35_EVIDENCE_TO_CORE_CHECKPOINT.md
docs/adr/ADR-017-identity-scope-boundary.md
```

---

## 6. Archivos prohibidos

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

## 7. Invariantes obligatorios

- no ejecutar `DiagnosticCoreV1` desde los gates cuando el contrato sólo pide gate decision;
- no calcular fórmulas;
- no diagnosticar;
- no producir findings;
- no generar narrativa;
- no tocar parser Excel;
- no tocar Telegram;
- no tocar runtime;
- no agregar fórmulas;
- reutilizar contratos existentes cuando sea posible.

---

## 8. Slice M36-S1 — Port Contract Skeleton

Debe crear o completar los contratos mínimos para:

- `FORMULA_INPUT_GATE`
- `EVIDENCE_STATUS_PORT`
- `EVIDENCE_SUFFICIENCY_GATE`

Resultado esperado:

- contratos serializables;
- estados y decisiones explícitas;
- sin ejecución del core.

---

## 9. Slice M36-S2 — Formula Input Gate

Debe devolver por fórmula:

- `formula_id`
- `required_variables`
- `available_variables`
- `missing_variables`
- `status`

Reglas:

- `READY` si todas las variables requeridas están disponibles
- `MISSING_INPUTS` si falta una o más
- orden determinístico
- no inventar variables

---

## 10. Slice M36-S3 — Evidence Sufficiency Gate

Debe proyectar desde el estado de inputs una decisión explícita:

- `ALLOW_EXECUTION`
- `BLOCK_MISSING_INPUTS`

Reglas:

- bloquear cualquier fórmula con `missing_variables`
- no ejecutar core para producir esta decisión
- devolver `missing_variables` exacto

---

## 11. Tests obligatorios para implementación posterior

La implementación posterior deberá incluir como mínimo:

- `READY` con evidencia completa
- `MISSING_INPUTS` con evidencia incompleta
- `missing_variables` exacto
- `available_variables` exacto
- múltiples fórmulas
- orden determinístico
- gate decision `ALLOW_EXECUTION`
- gate decision `BLOCK_MISSING_INPUTS`
- prueba de no invocación de `DiagnosticCoreV1`

---

## 12. Validación focal esperada

```powershell
python -m pytest tests/diagnosticcore/test_evidence_sufficiency.py -q
```

Si se agregan tests separados del gate:

```powershell
python -m pytest tests/diagnosticcore/ -q
```

---

## 13. PASS

PASS si:

```text
- los contratos mínimos existen;
- Formula Input Gate devuelve estados correctos;
- Evidence Sufficiency Gate devuelve decisiones correctas;
- no se invoca DiagnosticCoreV1 al gatear;
- no se tocan capas prohibidas;
- tests focales pasan;
- checkpoint posterior registra evidencia;
- sin push automático.
```

---

## 14. PARTIAL

PARTIAL si:

```text
- contratos creados;
- gate de inputs parcial;
- gate de suficiencia parcial;
- alguna validación falta;
- no se tocaron capas prohibidas.
```

---

## 15. BLOCKED

BLOCKED si:

```text
- aparece contradicción contractual con M35 o ADR-017;
- para implementar habría que tocar runtime o parser;
- no se pueden definir tests focales;
- el gate exige nueva fórmula o nueva patología para existir.
```

---

## 16. Evidencia obligatoria de salida

La implementación posterior de M36 deberá devolver:

```text
VEREDICTO
FILES CHANGED
DIFF SUMMARY
TEST RESULTS
COMMIT HASH
GIT STATUS FINAL
CONFIRMACIÓN NO PUSH
```
