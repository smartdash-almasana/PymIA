# M37 — Core to Audit and Delivery Integration TaskSpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente activo: `M37_CORE_TO_AUDIT_AND_DELIVERY_INTEGRATION`

---

## 1. Objetivo

Conectar de forma real y mínima el resultado de `DiagnosticCoreV1` y los gates de M36 con:

- salida soberana SCN;
- render seguro;
- gate de entrega;
- paquete de entrega;
- estado operativo.

---

## 2. Slice mínimo implementable

```text
M37-S1 — Sovereign audit bridge
M37-S2 — Delivery bridge
M37-S3 — Operational state projection
```

No autoriza más slices en este frente.

---

## 3. Arquitectura objetivo

```text
StructuredEvidence
→ FormulaInputGateResult[]
→ EvidenceGateDecision[]
→ DiagnosticCoreResult
→ SCN OperationalAuditResult mapping
→ RenderContract
→ ExecutionResultGateVerdict
→ DeliveryPackage
→ PymIAState
```

---

## 4. Archivos permitidos

```text
pymia/audit_result/*
pymia/diagnostic_core/*
pymia/contracts/scn_output_gateway.py
pymia/orchestration/state.py
tests/diagnosticcore/*
tests/scn/*
docs/pymia/M37_CORE_TO_AUDIT_AND_DELIVERY_INTEGRATION_CAPABILITYSPEC.md
docs/pymia/M37_CORE_TO_AUDIT_AND_DELIVERY_INTEGRATION_MODULECONTRACT.md
docs/pymia/M37_CORE_TO_AUDIT_AND_DELIVERY_INTEGRATION_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
```

Sólo si es estrictamente necesario:

```text
pymia/orchestration/graph.py
tests/smartpyme/*
```

---

## 5. Archivos prohibidos

```text
pymia/telegram_bot_runtime.py
pymia/telegram_document_handler.py
tools/
SmartPyme/
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
```

---

## 6. Invariantes obligatorios

- no crear `CaseTraceSnapshot` nuevo salvo necesidad estricta;
- no crear `DeliveryPackage` paralelo;
- no duplicar `OperationalAuditResult`;
- no agregar fórmulas;
- no generar narrativa owner-facing;
- no tocar Telegram;
- no tocar parser Excel;
- no tocar runtime productivo;
- reutilizar verifier y render contract SCN existentes;
- reutilizar `ExecutionResultGate` y `DeliveryPackage` existentes.

---

## 7. Slice M37-S1 — Sovereign audit bridge

Debe:

- recibir evidencia, gates y `DiagnosticCoreResult`;
- construir resultado soberano mínimo compatible con SCN;
- verificarlo con la frontera SCN existente;
- preservar `source_refs` y `missing_evidence`.

---

## 8. Slice M37-S2 — Delivery bridge

Debe:

- derivar `RenderContract`;
- materializar artefactos mínimos en disco;
- construir un resultado compatible con `ExecutionResultGate`;
- pasar por `DeliveryPackage`.

---

## 9. Slice M37-S3 — Operational state projection

Debe:

- proyectar gate/core/delivery a `PymIAState`;
- actualizar `phase`, `gate_verdict`, `delivery_status`, `output_refs`, `findings_count`;
- agregar entradas trazables a `decision_trail`.

---

## 10. Tests obligatorios

- sovereign result `pending_data` cuando gates/core bloquean;
- sovereign result `ok` cuando hay salida ejecutable;
- preservación de `missing_evidence` y `forbidden_inferences`;
- `RenderContract` construido desde el resultado verificado;
- `ExecutionResultGate` en `PASS` con artefactos materiales mínimos;
- `DeliveryPackage` reutilizado, no duplicado;
- `PymIAState` actualizado con `DELIVERED` o `BLOCKED`;
- prueba de que no se toca Telegram ni runtime.

---

## 11. PASS

PASS si:

- existe bridge soberano verificable;
- existe bridge de delivery reutilizando contratos existentes;
- existe proyección a estado operativo;
- tests focales pasan;
- no se crearon artefactos paralelos;
- no se tocó Telegram ni runtime;
- no hay push automático.

---

## 12. BLOCKED

BLOCKED si:

- la integración exige crear nueva salida soberana;
- la entrega exige reemplazar `ExecutionResultGate` o `DeliveryPackage`;
- la proyección a estado obliga a tocar runtime o Telegram;
- no se puede materializar evidencia mínima para `output_refs`.
