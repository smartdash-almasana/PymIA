# M59 — Owner Action Pipeline Boundary CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M59_OWNER_ACTION_PIPELINE_BOUNDARY`

---

## 1. Objetivo

Autorizar un pipeline lógico unificado:

```text
OwnerAnswersBundle
+ OwnerQuestionsBundle
+ render_contract
→ evaluación
→ decisión
→ resolución de targets
→ proyección a render_contract
```

Sin tocar `graph.py`, `core_delivery_bridge.py` ni `DiagnosticCore`.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_TASKSPEC.md`
- `docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_TASKSPEC.md`
- `docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_TASKSPEC.md`

---

## 3. Capacidad autorizada

M59 autoriza una orquestación lógica pura que:

- valida alineación entre respuestas y preguntas;
- ejecuta `evaluate_owner_answers`;
- ejecuta `decide_owner_next_action`;
- ejecuta `resolve_owner_next_action_targets`;
- ejecuta `project_resolved_owner_actions_to_render_contract`;
- retorna todos los artefactos intermedios relevantes.

---

## 4. Invariantes

- fail-closed ante desalineación de IDs;
- sin side effects;
- sin `evidence_candidate`;
- sin diagnóstico nuevo;
- sin findings nuevos;
- sin integración bridge;
- salida determinística y JSON-compatible en sus artefactos.

---

## 5. Artefacto esperado

Implementación en:

`pymia/smartpyme/owner_action_pipeline.py`

Con:

- `OwnerActionPipelineResult`
- `build_owner_action_projection_pipeline(...)`

---

## 6. Criterios PASS

M59 puede declararse PASS si:

- la orquestación existe;
- la alineación fail-closed queda implementada;
- la suite focal cubre `keep_as_declared`, `ask_clarification`, `reject_answer` y desalineación;
- no se tocó `graph.py`, `core_delivery_bridge.py` ni `DiagnosticCore`.
