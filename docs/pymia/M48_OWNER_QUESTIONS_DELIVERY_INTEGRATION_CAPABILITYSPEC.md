# M48 — Owner Questions Delivery Integration CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M48_OWNER_QUESTIONS_DELIVERY_INTEGRATION`

---

## 1. Capacidad

PymIA puede integrar un `OwnerQuestionsBundle` al bundle soberano de entrega como artefacto JSON trazable.

La capacidad autorizada es:

```text
OperationalAuditResult.missing_evidence
+ RenderContract.next_questions
+ RenderContract.blocked_message
+ source_ref trazable
→ OwnerQuestionsBundle
→ owner_questions_bundle.json
→ DeliveryPackage.output_refs
→ CoreAuditDeliveryBundle.owner_questions_bundle
```

---

## 2. Qué puede hacer

M48 puede:

- construir `OwnerQuestionsBundle` desde artefactos ya emitidos;
- escribir `owner_questions_bundle.json` en `target_dir`;
- incluir la ruta del bundle en `output_refs`;
- incluir la ruta del bundle en `DeliveryPackage.output_refs`;
- exponer el payload en `CoreAuditDeliveryBundle.owner_questions_bundle`.

---

## 3. Qué no puede hacer

M48 no autoriza:

- graph;
- `PymIAState`;
- Telegram;
- Hermes;
- FastAPI;
- parser;
- `DiagnosticCore`;
- fórmulas;
- LLM;
- runtime conversacional.

---

## 4. Inputs requeridos

- `render_contract["next_questions"]`
- `render_contract["blocked_message"]`
- `operational_audit_result["missing_evidence"]`
- `source_ref` del artefacto fuente

---

## 5. Outputs requeridos

- `owner_questions_bundle.json`
- `DeliveryPackage.output_refs` incluye la ruta del bundle
- `CoreAuditDeliveryBundle.owner_questions_bundle` contiene el payload serializado

---

## 6. Failure states

La capacidad debe admitir:

- bundle con preguntas cuando haya faltantes o bloqueo;
- bundle vacío si no hay preguntas trazables;
- output trazable y determinístico.

---

## 7. Estado

```text
M48 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este documento autoriza sólo la integración al bundle de entrega.
