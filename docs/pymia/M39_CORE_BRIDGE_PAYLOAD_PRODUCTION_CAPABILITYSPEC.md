# M39 — Core Bridge Payload Production CapabilitySpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M39_CORE_BRIDGE_PAYLOAD_PRODUCER`

---

## 1. Capacidad

PymIA puede producir automáticamente `core_delivery_bridge_payload` a partir de evidencia estructurada, gates M36 y `DiagnosticCoreV1`, para que M38 pueda consumirlo sin depender de payload manual.

La capacidad autorizada es:

```text
StructuredEvidence
→ evidence_binding
→ FormulaInputGate / EvidenceGateDecision
→ DiagnosticCoreV1
→ core_delivery_bridge_payload
```

---

## 2. Qué puede hacer

M39 puede:

- construir payload determinístico del bridge;
- reutilizar binder existente;
- reutilizar sufficiency/gates existentes;
- ejecutar el core sólo para fórmulas habilitadas;
- producir estado insuficiente si no hay fórmulas ejecutables.

---

## 3. Inputs requeridos

- `StructuredEvidence`
- `formula_ids`
- `tenant_id`
- `case_id`
- `hypothesis_codes` opcional

---

## 4. Outputs requeridos

`core_delivery_bridge_payload` con:

- evidencia estructurada de entrada
- `FormulaInputGateResult[]`
- `EvidenceGateDecision[]`
- `DiagnosticCoreResult`
- metadata mínima necesaria para el bridge M37

---

## 5. Limitaciones obligatorias

M39 no autoriza:

- fórmulas nuevas;
- bypass de gates;
- ejecución de fórmulas bloqueadas;
- diagnóstico paralelo;
- bridge nuevo;
- narrativa owner-facing.

---

## 6. Failure states

La capacidad debe admitir:

- payload producido con fórmulas `READY`;
- fórmulas faltantes bloqueadas sin ejecución;
- payload insuficiente determinístico cuando ninguna fórmula pueda correr;
- preservación exacta de `missing_variables`.

---

## 7. Fuera de alcance

- poblar `progressive_context` desde intake/Excel
- render para dueño
- cambios en parser Excel
