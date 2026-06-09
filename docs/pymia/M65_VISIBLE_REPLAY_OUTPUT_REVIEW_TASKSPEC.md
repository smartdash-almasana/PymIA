# M65 — Visible Replay Output Review TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M65_VISIBLE_REPLAY_OUTPUT_REVIEW`

---

## 1. Tipo de tarea

Sandbox/review.

No producción.
No bridge.
No runtime.

---

## 2. Objetivo

Crear una revisión humana controlada para el resultado técnico de M64, usando un formateador puro y tests e2e sandbox.

---

## 3. Archivos autorizados

- `pymia/smartpyme/owner_answer_replay_formatter.py`
- `tests/smartpyme/e2e/test_owner_answer_e2e_sandbox.py`
- `docs/pymia/M65_VISIBLE_REPLAY_OUTPUT_REVIEW_CAPABILITYSPEC.md`
- `docs/pymia/M65_VISIBLE_REPLAY_OUTPUT_REVIEW_TASKSPEC.md`
- `docs/DOCUMENTATION_INDEX.md`

---

## 4. Archivos prohibidos

- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/orchestration/graph.py`
- `pymia/orchestration/state.py`
- `pymia/orchestration/conversation_adapter.py`
- `pymia/telegram_bot_runtime.py`
- `pymia/diagnostic_core/`
- `pymia/smartpyme/owner_facing_report.py`
- `conversa-engine/`

---

## 5. Implementación

Crear:

```text
format_composition_result_for_human_review(result) -> str
```

La función debe:

- devolver Markdown;
- no mutar input;
- no escribir archivos;
- no usar runtime;
- no llamar `build_owner_facing_report`;
- no diagnosticar;
- no convertir respuestas en evidencia dura.

---

## 6. Tests

Extender el sandbox M64 para verificar:

- happy path del formatter;
- secciones Markdown esperadas;
- contenido humano relevante;
- ausencia de IDs contractuales crudos;
- no mutación de `projected_render_contract`;
- comportamiento robusto con secciones vacías;
- ausencia de imports prohibidos.

---

## 7. Validación

Ejecutar:

```text
python -m pytest tests/smartpyme/e2e/test_owner_answer_e2e_sandbox.py -q
```

Luego:

```text
python -m pytest tests/smartpyme/e2e/test_owner_answer_e2e_sandbox.py tests/smartpyme/test_owner_answers_composer.py tests/smartpyme/test_owner_action_pipeline.py tests/smartpyme/test_owner_answers_capture.py tests/smartpyme/test_owner_answers_evaluator.py tests/smartpyme/test_owner_actions_decider.py -q
```

---

## 8. Criterio PASS

```text
formatter creado
sandbox extendido
sin imports prohibidos
sin bridge
sin graph
sin runtime
tests focales verdes
```
