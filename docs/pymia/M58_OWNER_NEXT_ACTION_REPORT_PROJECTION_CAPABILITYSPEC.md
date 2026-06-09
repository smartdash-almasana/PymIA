# M58 — Owner Next Action Report Projection CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M58_OWNER_NEXT_ACTION_REPORT_PROJECTION`

---

## 1. Objetivo

Autorizar una proyección pura:

```text
render_contract
+ OwnerResolvedNextActionBundle
→ render_contract proyectado
```

Sin integración bridge todavía.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-022-owner-action-visibility-boundary.md`
- `docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_TASKSPEC.md`

---

## 3. Capacidad autorizada

M58 autoriza proyectar acciones owner-facing ya resueltas dentro de un `render_contract` existente, sin tocar su frontera soberana ni abrir render paralelo.

Debe:

- devolver copia y no mutar el input;
- usar únicamente `resolved_questions` ya resueltas a texto;
- preservar campos existentes no relacionados;
- agregar warnings trazables compatibles con el contrato existente.

---

## 4. Reglas obligatorias

- `ask_clarification`
  - `next_questions = resolved_questions`
  - `blocked_message = primera resolved_question`, si existe
- `reject_answer`
  - `blocked_message = "No puedo usar esa respuesta sin una aclaración o respaldo adicional."`
  - `next_questions = resolved_questions`
  - agregar warning trazable
- `keep_as_declared`
  - agregar en `next_steps`: `"La respuesta queda registrada como declaración del dueño, no como evidencia validada."`
  - agregar warning trazable
- si no hay acciones
  - devolver el `render_contract` sin cambios semánticos

---

## 5. No objetivos

M58 no autoriza:

- integración en `core_delivery_bridge.py`
- mutación de `OwnerFacingReport`
- render visible final
- `evidence_candidate`
- diagnóstico
- findings

---

## 6. Artefactos esperados

Implementación en:

`pymia/smartpyme/owner_actions_projector.py`

Función requerida:

`project_resolved_owner_actions_to_render_contract(render_contract: dict, resolved_action_bundle: OwnerResolvedNextActionBundle) -> dict`
