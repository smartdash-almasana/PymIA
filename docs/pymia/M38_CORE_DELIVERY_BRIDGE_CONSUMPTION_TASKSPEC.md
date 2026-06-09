# M38 — Core Delivery Bridge Consumption TaskSpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M38_GRAPH_CONSUMES_CORE_DELIVERY_BRIDGE`

---

## 1. Objetivo

Conectar de forma mínima `graph.py` con el bridge M37 para que la orquestación pueda consumir un `core_delivery_bridge_payload` ya producido y cerrar el circuito hacia `DeliveryPackage` y `PymIAState`.

---

## 2. Slice implementativo

Slice único:

- consumo opcional de `core_delivery_bridge_payload` en `graph.py`
- proyección del bundle a `PymIAState`
- test focal del flujo conectado

---

## 3. Arquitectura objetivo

```text
progressive_context
→ core_delivery_bridge_payload
→ build_core_audit_delivery_bundle(...)
→ project_bridge_result_to_state(...)
→ PymIAState
```

---

## 4. Archivos permitidos

- `pymia/orchestration/graph.py`
- `tests/orchestration/test_graph.py`

---

## 5. Prohibiciones

- no tocar `DiagnosticCoreV1`
- no tocar Telegram
- no tocar parser Excel
- no crear bridge nuevo
- no crear `DeliveryPackage` paralelo
- no rediseñar el grafo completo

---

## 6. Criterios PASS

- el grafo consume el payload cuando existe
- el estado final refleja `phase`, `gate_verdict`, `delivery_status`, `output_refs`, `findings_count`
- el flujo legacy sigue disponible cuando no hay payload

---

## 7. Evidencia mínima

- test focal de `graph`
- evidencia de que el bridge M37 es realmente consumido
