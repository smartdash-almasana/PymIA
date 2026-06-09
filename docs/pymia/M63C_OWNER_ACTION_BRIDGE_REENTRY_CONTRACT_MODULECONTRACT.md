# M63C — Owner Action Bridge Reentry Contract ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT`

---

## 1. Naturaleza

Contrato documental.

No crea módulo Python.
No modifica `core_delivery_bridge.py`.
No modifica tests.

---

## 2. Frontera futura candidata

Todavía no implementada:

```text
CoreAuditDeliveryBundle
+ OwnerAnswerToActionCompositionResult
→ bundle derivado o resultado bridge-adjacent trazable
```

La forma exacta de salida queda para un hito implementativo posterior.

---

## 3. Entradas permitidas futuras

Sólo artefactos estructurados:

- `CoreAuditDeliveryBundle`
- `OwnerAnswerToActionCompositionResult`
- `OwnerAnswersBundle`
- `OwnerAnswerEvaluationBundle`
- `OwnerNextActionBundle`
- `OwnerResolvedNextActionBundle`
- `projected_render_contract`
- `owner_facing_report`
- `owner_questions_bundle`
- `delivery_package`
- `output_refs`

---

## 4. Responsabilidad futura autorizable

Un hito posterior podrá coordinar la reentrada visible de acciones owner-facing ya resueltas hacia la cadena de delivery.

Debe preservar:

- `OwnerFacingReport` como frontera visible soberana;
- `output_refs`;
- bloqueos;
- trazabilidad;
- diagnóstico y findings existentes sin cambios.

Debe rechazar acciones sin texto owner-facing.

---

## 5. Prohibiciones

Una futura implementación no puede:

- leer texto libre;
- inferir `question_id`;
- usar similitud semántica para asociar pregunta/respuesta;
- promover `OwnerAnswer` u `OwnerNextAction` a evidencia dura;
- recalcular diagnóstico;
- recalcular fórmulas;
- crear findings;
- ocultar bloqueos;
- crear renderer paralelo;
- mostrar IDs crudos;
- hacer que `graph.py` conozca `OwnerNextActionBundle`;
- tocar Telegram;
- tocar runtime;
- usar LLM;
- usar memoria conversacional para completar datos.

---

## 6. Fail-closed futuro

Debe fallar en cerrado si falta:

- `CoreAuditDeliveryBundle`;
- `OwnerAnswerToActionCompositionResult`;
- `OwnerFacingReport`;
- `projected_render_contract`;
- texto owner-facing resuelto.

También debe fallar si la proyección intenta alterar diagnóstico, findings o bloqueos.

---

## 7. Archivos prohibidos en M63C

M63C no puede modificar:

- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/orchestration/graph.py`
- `pymia/orchestration/state.py`
- `pymia/orchestration/conversation_adapter.py`
- `pymia/telegram_bot_runtime.py`
- `pymia/diagnostic_core/`
- `tests/`
- `conversa-engine/`

---

## 8. Para abrir implementación posterior

El próximo hito implementativo deberá traer:

- CapabilitySpec propio;
- ModuleContract propio;
- TaskSpec propio;
- tests focales;
- evidencia de no mutación;
- evidencia de fail-closed;
- evidencia de imports prohibidos ausentes;
- decisión explícita sobre salida: bundle derivado o resultado bridge-adjacent.
