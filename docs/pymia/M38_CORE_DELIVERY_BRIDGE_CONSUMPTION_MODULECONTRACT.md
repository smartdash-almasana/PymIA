# M38 — Core Delivery Bridge Consumption ModuleContract

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M38_GRAPH_CONSUMES_CORE_DELIVERY_BRIDGE`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
orchestration/graph
↔ core_delivery_bridge bundle
↔ delivery/state projection
```

El grafo puede consumir el bundle soberano, pero no puede reemplazarlo con lógica paralela.

---

## 2. Responsabilidades permitidas

La frontera M38 puede:

- detectar presencia de `core_delivery_bridge_payload`;
- invocar el bridge M37;
- proyectar el resultado a `PymIAState`;
- retornar estado final del flujo operativo.

---

## 3. Responsabilidades prohibidas

La frontera M38 no puede:

- recomputar findings fuera del bridge;
- inventar `RenderContract`;
- crear delivery paralelo;
- alterar el diagnóstico emitido por el core;
- introducir narrativa libre.

---

## 4. Side effects permitidos

Sólo se permiten los side effects ya definidos por la cadena existente:

- materialización de `DeliveryPackage`;
- escritura operativa ya gobernada por el bridge/delivery package;
- actualización del estado de orquestación.

No se autorizan side effects nuevos.

---

## 5. Dependencias permitidas

- `pymia.audit_result.core_delivery_bridge`
- `pymia.orchestration.state`
- `pymia.smartpyme.delivery_package`
- `pymia.smartpyme.execution_result_gate`

---

## 6. Invariantes

- si no hay payload, el flujo legacy puede continuar;
- si hay payload, debe consumirse sin duplicar la cadena legacy;
- el estado final debe preservar `gate_verdict`, `delivery_status`, `output_refs` y `findings_count`;
- no se puede ocultar un bloqueo preexistente.
