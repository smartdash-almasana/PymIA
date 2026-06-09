# M48 — Owner Questions Delivery Integration TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M48_OWNER_QUESTIONS_DELIVERY_INTEGRATION`

---

## 1. Objetivo

Integrar `OwnerQuestionsBundle` al `CoreAuditDeliveryBundle` y a `output_refs` como artefacto JSON trazable.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-019-guided-evidence-recovery-authority.md`
- `docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_TASKSPEC.md`
- `pymia/contracts/owner_questions.py`
- `pymia/smartpyme/owner_questions_builder.py`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M48_OWNER_QUESTIONS_DELIVERY_INTEGRATION_CAPABILITYSPEC.md
docs/pymia/M48_OWNER_QUESTIONS_DELIVERY_INTEGRATION_MODULECONTRACT.md
docs/pymia/M48_OWNER_QUESTIONS_DELIVERY_INTEGRATION_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/audit_result/core_delivery_bridge.py
tests/diagnosticcore/test_core_audit_delivery_bridge.py
```

---

## 4. Cambio autorizado

- importar `build_owner_questions_bundle`
- agregar `owner_questions_bundle: dict[str, Any]` a `CoreAuditDeliveryBundle`
- crear `owner_questions_bundle.json` en `target_dir`
- construir bundle desde:
  - `render_contract["next_questions"]`
  - `render_contract["blocked_message"]`
  - `operational_audit_result["missing_evidence"]`
  - `source_ref` del artefacto fuente
- agregar `owner_questions_bundle.json` a `output_refs`
- incluirlo en `DeliveryPackage.output_refs`
- retornarlo en `CoreAuditDeliveryBundle.owner_questions_bundle`

---

## 5. Prohibiciones

No tocar:

- `graph.py`
- `PymIAState`
- Telegram
- Hermes
- FastAPI
- parser
- `DiagnosticCore`
- fórmulas
- LLM
- runtime conversacional

---

## 6. Tests requeridos

El test focal debe validar:

- genera `owner_questions_bundle.json`
- `owner_questions_bundle.json` está en `DeliveryPackage.output_refs`
- `CoreAuditDeliveryBundle.owner_questions_bundle` contiene preguntas
- conserva `missing_evidence` / `next_questions` / `blocked_message`
- no toca state ni graph

---

## 7. Criterios PASS

M48 puede declararse PASS si:

- el artefacto JSON se genera;
- la ruta queda en `output_refs` y `DeliveryPackage.output_refs`;
- el payload vuelve en `CoreAuditDeliveryBundle.owner_questions_bundle`;
- el test focal pasa;
- no se tocaron archivos prohibidos.

---

## 8. Estado

```text
M48 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este TaskSpec autoriza sólo la integración al bundle.
