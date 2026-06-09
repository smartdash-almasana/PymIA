# M39 — Core Bridge Payload Production TaskSpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M39_CORE_BRIDGE_PAYLOAD_PRODUCER`

---

## 1. Objetivo

Hacer que el flujo operativo produzca automáticamente `core_delivery_bridge_payload` desde evidencia estructurada y gates, para habilitar el consumo de M38 sin payload manual.

---

## 2. Slice implementativo

Slice único:

- helper productor determinístico de payload
- conexión mínima al grafo u otro punto limpio del flujo operativo
- tests focales para evidencia suficiente e insuficiente

---

## 3. Archivos permitidos

- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/orchestration/graph.py`
- `tests/diagnosticcore/test_core_audit_delivery_bridge.py`
- `tests/orchestration/test_graph.py`

---

## 4. Prohibiciones

- no tocar parser Excel
- no tocar Telegram
- no tocar `DiagnosticCoreV1`
- no agregar fórmulas
- no crear `DeliveryPackage` nuevo

---

## 5. Criterios PASS

- el payload se produce automáticamente cuando hay `StructuredEvidence` y `formula_ids`
- el core no ejecuta fórmulas bloqueadas
- evidencia insuficiente produce bloqueo determinístico y trazable

---

## 6. Evidencia mínima

- tests focales del productor
- tests del consumo del payload en `graph`
