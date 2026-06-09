# M59 — Owner Action Pipeline Boundary TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M59_OWNER_ACTION_PIPELINE_BOUNDARY`

---

## 1. Objetivo

Implementar el pipeline lógico unificado de procesamiento de respuestas del dueño sin tocar integración conversacional ni bridge de entrega.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/pymia/M59_OWNER_ACTION_PIPELINE_BOUNDARY_CAPABILITYSPEC.md`
- `docs/pymia/M59_OWNER_ACTION_PIPELINE_BOUNDARY_MODULECONTRACT.md`
- `docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_TASKSPEC.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M59_OWNER_ACTION_PIPELINE_BOUNDARY_CAPABILITYSPEC.md
docs/pymia/M59_OWNER_ACTION_PIPELINE_BOUNDARY_MODULECONTRACT.md
docs/pymia/M59_OWNER_ACTION_PIPELINE_BOUNDARY_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/smartpyme/owner_action_pipeline.py
tests/smartpyme/test_owner_action_pipeline.py
```

---

## 4. Checklist implementativo

1. Definir `OwnerActionPipelineResult`.
2. Validar alineación `answer.question_id` contra `questions_bundle`.
3. Invocar `evaluate_owner_answers`.
4. Invocar `decide_owner_next_action`.
5. Invocar `resolve_owner_next_action_targets`.
6. Invocar `project_resolved_owner_actions_to_render_contract`.
7. Retornar todos los artefactos resultantes.

---

## 5. Validación mínima

La suite focal debe certificar:

- transición exitosa hacia `keep_as_declared`;
- transición hacia `ask_clarification`;
- transición hacia `reject_answer`;
- fail-closed por desalineación de IDs.

---

## 6. Criterios PASS

M59 puede declararse PASS si:

- el pipeline existe;
- la suite focal pasa;
- el diff no toca `graph.py`, `core_delivery_bridge.py` ni `DiagnosticCore`;
- no se introducen side effects.
