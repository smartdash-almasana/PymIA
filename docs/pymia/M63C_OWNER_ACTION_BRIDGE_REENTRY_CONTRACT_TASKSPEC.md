# M63C — Owner Action Bridge Reentry Contract TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT`

---

## 1. Tipo de tarea

Documentación contractual.

No implementación.
No tests nuevos.
No modificación de bridge.

---

## 2. Objetivo

Crear el contrato previo para un futuro hito bridge-adjacent que podría conectar `OwnerAnswerToActionCompositionResult` con la cadena owner-facing de delivery.

---

## 3. Fuentes obligatorias

- `Pymia-memoria/M63B_PRE_AUDIT_BRIDGE_REENTRY_20260609.md`
- `docs/pymia/M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY_MODULECONTRACT.md`
- `docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_MODULECONTRACT.md`
- `pymia/audit_result/core_delivery_bridge.py` sólo como lectura

---

## 4. Archivos autorizados

- `docs/pymia/M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT_CAPABILITYSPEC.md`
- `docs/pymia/M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT_MODULECONTRACT.md`
- `docs/pymia/M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT_TASKSPEC.md`
- `docs/DOCUMENTATION_INDEX.md`
- `Pymia-memoria/_task_actual.md`
- `Pymia-memoria/CHECKPOINT_M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT_20260609.md`

---

## 5. Archivos prohibidos

- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/orchestration/graph.py`
- `pymia/orchestration/state.py`
- `pymia/orchestration/conversation_adapter.py`
- `pymia/telegram_bot_runtime.py`
- `pymia/diagnostic_core/`
- `pymia/smartpyme/owner_answers_composer.py`
- `tests/`
- `conversa-engine/`

---

## 6. Pasos

1. Verificar repo limpio.
2. Leer M63B preaudit.
3. Leer M63 ModuleContract.
4. Crear CapabilitySpec M63C.
5. Crear ModuleContract M63C.
6. Crear TaskSpec M63C.
7. Actualizar `docs/DOCUMENTATION_INDEX.md`.
8. Actualizar memoria local.
9. Verificar que sólo haya cambios documentales versionados.

---

## 7. Validación documental

M63C se valida si:

- existen los tres documentos M63C;
- el índice contiene las tres entradas;
- no hay cambios de código;
- no hay cambios de tests;
- el contrato no autoriza implementación directa;
- M64 sigue separado.

---

## 8. Criterio PASS

```text
M63C docs creados
DOCUMENTATION_INDEX actualizado
sin código
sin tests
sin bridge
sin graph
sin runtime
sin Telegram
```

---

## 9. Criterio BLOCKED

Bloquear si aparece necesidad de:

- modificar bridge ahora;
- modificar graph;
- modificar runtime;
- usar LLM;
- crear renderer paralelo;
- mezclar con M64;
- reparar tests globales dentro de M63C.
