# M37 — Core to Audit and Delivery Integration CapabilitySpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M37_CORE_TO_AUDIT_AND_DELIVERY_INTEGRATION`

---

## 1. Capacidad

PymIA puede proyectar la salida de `DiagnosticCoreV1` y los gates de M36 hacia artefactos soberanos ya existentes de:

- auditoría operativa;
- render seguro;
- gate de entrega;
- paquete de entrega;
- estado operativo.

La capacidad autorizada es:

```text
StructuredEvidence
→ FormulaInputGateResult[]
→ EvidenceGateDecision[]
→ DiagnosticCoreResult
→ SCN OperationalAuditResult mapping
→ RenderContract
→ ExecutionResultGate
→ DeliveryPackage
→ PymIAState
```

---

## 2. Qué puede hacer

M37 puede:

- reutilizar `DiagnosticCoreV1`, `evidence_binding` y `evidence_sufficiency`;
- construir un `OperationalAuditResult` soberano mínimo en formato SCN verificable;
- construir un `RenderContract` desde ese resultado soberano;
- materializar artefactos mínimos serializables para que `ExecutionResultGate` y `DeliveryPackage` operen sobre salida real;
- propagar a `PymIAState` el resultado de gates, core y entrega sin tocar Telegram.

---

## 3. Qué no puede hacer

M37 no autoriza:

- crear un `CaseTraceSnapshot` nuevo por defecto;
- crear un `DeliveryPackage` paralelo;
- duplicar `OperationalAuditResult`;
- agregar fórmulas;
- agregar narrativa owner-facing;
- tocar parser Excel;
- tocar Telegram;
- tocar runtime productivo;
- reabrir `M35` o `M36`.

---

## 4. Inputs mínimos

- `StructuredEvidence`
- `case_id`
- `intake_id`
- `FormulaInputGateResult[]`
- `EvidenceGateDecision[]`
- `DiagnosticCoreResult`
- `output_dir` para materializar artefactos mínimos de salida

---

## 5. Outputs mínimos

### Port 1 — `OPERATIONAL_AUDIT_PORT`

Mapping SCN verificable con al menos:

- `result_id`
- `tenant_id`
- `status`
- `findings`
- `missing_evidence`
- `forbidden_inferences`
- `allowed_rendering`
- `audit_trail_ref`
- `sovereign_mark`

### Port 2 — `RENDER_CONTRACT_PORT`

`RenderContract` derivado sólo desde el resultado soberano verificado.

### Port 3 — `DELIVERY_PORT`

`ExecutionResultGateVerdict` y `DeliveryPackage` derivados desde artefactos materiales mínimos.

### Port 4 — `OPERATIONAL_STATE_PORT`

Proyección a `PymIAState` de:

- `phase`
- `gate_verdict`
- `delivery_status`
- `output_refs`
- `findings_count`
- trazabilidad de decisiones

---

## 6. Failure states

La capacidad debe admitir explícitamente:

- `blocked` / `pending_data` cuando los gates o el core indiquen evidencia faltante;
- `candidate` cuando el core tenga resultados parciales sin bloqueo total;
- `ok` sólo cuando exista salida material verificable;
- fail-closed si el resultado soberano no satisface SCN.

---

## 7. Evidencia mínima esperada antes de PASS implementativo

La implementación posterior de M37 sólo podrá declararse PASS si aporta:

- tests focales del bridge soberano;
- tests focales de conexión con `ExecutionResultGate` y `DeliveryPackage`;
- tests focales de actualización de `PymIAState`;
- evidencia de que no se creó pieza paralela a `OperationalAuditResult` o `DeliveryPackage`;
- evidencia de que no se tocó Telegram ni runtime.
