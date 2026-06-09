# M39 — Core Bridge Payload Production ModuleContract

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M39_CORE_BRIDGE_PAYLOAD_PRODUCER`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
StructuredEvidence
↔ gates M36
↔ DiagnosticCoreV1
↔ core_delivery_bridge_payload
```

---

## 2. Responsabilidades permitidas

La frontera M39 puede:

- construir `DiagnosticCoreInput` desde evidencia estructurada;
- construir `FormulaInputGateResult[]`;
- construir `EvidenceGateDecision[]`;
- derivar el conjunto ejecutable de fórmulas;
- ejecutar `DiagnosticCoreV1` sólo sobre fórmulas permitidas;
- empaquetar el payload para M38/M37.

---

## 3. Responsabilidades prohibidas

La frontera M39 no puede:

- inventar variables;
- ejecutar fórmulas bloqueadas;
- omitir `missing_variables`;
- crear findings fuera del core;
- saltarse gates;
- escribir outputs owner-facing.

---

## 4. Dependencias permitidas

- `pymia.diagnostic_core.evidence_binding`
- `pymia.diagnostic_core.evidence_sufficiency`
- `pymia.diagnostic_core.core`
- `pymia.audit_result.core_delivery_bridge`

---

## 5. Invariantes

- determinismo por `formula_id`;
- `missing_variables` exacto;
- si no hay fórmulas habilitadas, el resultado debe ser insuficiente y trazable;
- el payload no reemplaza al bridge M37, sólo lo alimenta.
