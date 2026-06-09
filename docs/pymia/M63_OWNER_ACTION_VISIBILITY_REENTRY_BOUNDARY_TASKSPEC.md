# M63 — Owner Action Visibility Reentry Boundary TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY`

---

## 1. Tipo de tarea

Documentación de frontera.

No implementación.

No tests productivos.

No cambio de runtime.

---

## 2. Objetivo de la tarea

Crear una frontera documental que defina cómo debe pensarse la reentrada visible del resultado de M62 hacia `OwnerFacingReport`, sin implementar esa reentrada todavía.

---

## 3. Entradas metodológicas

Leer y respetar:

- `AGENTS.md`
- `Pymia-memoria/M63A_GLOBAL_TEST_FAILURE_CLASSIFICATION_20260609.md`
- `docs/adr/ADR-018-owner-facing-report-boundary.md`
- `docs/adr/ADR-022-owner-action-visibility-boundary.md`
- `docs/adr/ADR-023-owner-answer-entrypoint-rules.md`
- `docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_MODULECONTRACT.md`

---

## 4. Archivos autorizados

M63 autoriza modificar únicamente documentación:

- `docs/pymia/M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY_CAPABILITYSPEC.md`
- `docs/pymia/M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY_MODULECONTRACT.md`
- `docs/pymia/M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY_TASKSPEC.md`
- `docs/DOCUMENTATION_INDEX.md`
- `Pymia-memoria/_task_actual.md`
- `Pymia-memoria/CHECKPOINT_M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY_20260609.md`

La memoria local puede actualizarse para continuidad, pero no forma parte del commit si está ignorada por Git.

---

## 5. Archivos prohibidos

M63 no puede modificar:

- `pymia/orchestration/graph.py`
- `pymia/orchestration/state.py`
- `pymia/orchestration/conversation_adapter.py`
- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/telegram_bot_runtime.py`
- `pymia/diagnostic_core/`
- `pymia/smartpyme/owner_answers_composer.py`
- `tests/`
- `conversa-engine/`

---

## 6. Pasos

1. Verificar repo limpio antes de escribir.
2. Leer fuentes obligatorias.
3. Crear CapabilitySpec.
4. Crear ModuleContract.
5. Crear TaskSpec.
6. Actualizar `docs/DOCUMENTATION_INDEX.md`.
7. Actualizar memoria local.
8. Verificar `git status --short`.
9. Reportar como documentación únicamente.

---

## 7. Validación documental

La validación de M63 consiste en verificar que:

- existen los tres documentos M63;
- el índice documental contiene las tres entradas M63;
- no se modificó código;
- no se modificaron tests;
- no se tocó bridge, graph, runtime ni Telegram;
- la frontera declara `OwnerFacingReport` como soberano visible;
- la frontera declara `projected_render_contract` como artefacto técnico intermedio;
- la frontera mantiene M64 como deuda separada.

---

## 8. Criterio PASS

M63 puede declararse PASS si:

```text
solo docs cambiados
M63 CapabilitySpec creado
M63 ModuleContract creado
M63 TaskSpec creado
DOCUMENTATION_INDEX actualizado
Pymia-memoria actualizada
repo sin cambios de código
```

---

## 9. Criterio BLOCKED

M63 debe bloquearse si:

- se requiere tocar `core_delivery_bridge.py`;
- se requiere tocar `graph.py`;
- se requiere crear un renderer paralelo;
- se requiere usar runtime/Telegram/LLM;
- no queda claro cuál es la frontera visible soberana;
- se intenta mezclar M63 con M64.
