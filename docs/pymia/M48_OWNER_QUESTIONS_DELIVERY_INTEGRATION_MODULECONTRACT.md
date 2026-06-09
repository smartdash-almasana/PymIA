# M48 — Owner Questions Delivery Integration ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M48_OWNER_QUESTIONS_DELIVERY_INTEGRATION`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
OperationalAuditResult / RenderContract
↔ OwnerQuestionsBuilder
↔ CoreAuditDeliveryBundle / DeliveryPackage.output_refs
```

La frontera M48 agrega un artefacto documental trazable.

No modifica state ni graph.

---

## 2. Responsabilidades permitidas

La frontera M48 puede:

- leer `missing_evidence`, `next_questions` y `blocked_message`;
- construir `OwnerQuestionsBundle`;
- escribir `owner_questions_bundle.json`;
- extender `output_refs`;
- reflejar el artefacto en `DeliveryPackage.output_refs`;
- devolver el payload en `CoreAuditDeliveryBundle`.

---

## 3. Responsabilidades prohibidas

La frontera M48 no puede:

- tocar `graph.py`;
- tocar `PymIAState`;
- cambiar diagnóstico o findings;
- recalcular fórmulas;
- abrir canales externos;
- usar LLM o heurística libre;
- reemplazar artefactos soberanos existentes.

---

## 4. Invariantes

- el artefacto debe ser JSON trazable;
- `output_refs` debe contener la ruta del bundle;
- `DeliveryPackage.output_refs` debe conservar esa ruta;
- la información fuente debe preservarse sin reinterpretación;
- la integración no debe afectar la proyección a state ni graph.

---

## 5. Dependencias permitidas

- `pymia/contracts/owner_questions.py`
- `pymia/smartpyme/owner_questions_builder.py`
- `pymia/audit_result/core_delivery_bridge.py`

---

## 6. Estado

```text
M48 ModuleContract = AUTHORIZED_FOR_IMPLEMENTATION
```

Este contrato autoriza la integración documental mínima al bundle.
