# M38 — Core Delivery Bridge Consumption CapabilitySpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M38_GRAPH_CONSUMES_CORE_DELIVERY_BRIDGE`

---

## 1. Capacidad

PymIA puede hacer que la orquestación operativa consuma el bridge soberano de M37 cuando éste ya existe en `progressive_context`, sin rediseñar el grafo completo ni crear un segundo circuito de delivery.

La capacidad autorizada es:

```text
progressive_context["core_delivery_bridge_payload"]
→ core_delivery_bridge
→ OperationalAuditResult
→ RenderContract
→ ExecutionResultGate
→ DeliveryPackage
→ PymIAState
```

---

## 2. Qué puede hacer

M38 puede:

- consumir `core_delivery_bridge_payload` dentro del flujo operativo;
- reutilizar `build_core_audit_delivery_bundle(...)`;
- reutilizar `project_bridge_result_to_state(...)`;
- actualizar `PymIAState` con estado operativo coherente;
- referenciar o producir `DeliveryPackage` usando la cadena ya existente.

---

## 3. Inputs requeridos

- `core_delivery_bridge_payload`
- `progressive_context`
- `output_dir`
- `PymIAState`

---

## 4. Outputs requeridos

- `OperationalAuditResult` soberano ya proyectado
- `DeliveryPackage` o estado bloqueado contractual equivalente
- `PymIAState` actualizado con:
  - `phase`
  - `gate_verdict`
  - `delivery_status`
  - `output_refs`
  - `findings_count`

---

## 5. Limitaciones obligatorias

M38 no autoriza:

- crear otro bridge;
- crear otro `DeliveryPackage`;
- crear `CaseTraceSnapshot`;
- rediseñar `graph.py` completo;
- tocar Telegram;
- tocar parser Excel;
- tocar `DiagnosticCoreV1`;
- generar narrativa owner-facing.

---

## 6. Failure states

La capacidad debe admitir:

- consumo exitoso del payload ya producido;
- actualización determinística del estado;
- fallback legacy si no existe payload;
- preservación de bloqueo si el bridge entrega estado no ejecutable.

---

## 7. Fuera de alcance

- producción automática del payload
- parseo Excel
- ampliación de fórmulas
- reportes para el dueño
- apertura de M39 sin contrato
