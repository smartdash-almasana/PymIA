# M58 — Owner Next Action Report Projection TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M58_OWNER_NEXT_ACTION_REPORT_PROJECTION`

---

## 1. Objetivo

Implementar una proyección pura de `OwnerResolvedNextActionBundle` hacia un `render_contract` existente.

Sin integración bridge todavía.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-022-owner-action-visibility-boundary.md`
- `docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_TASKSPEC.md`
- `docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_CAPABILITYSPEC.md`
- `docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_CAPABILITYSPEC.md
docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_MODULECONTRACT.md
docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/smartpyme/owner_actions_projector.py
tests/smartpyme/test_owner_actions_projector.py
```

---

## 4. Tests mínimos

El test focal debe validar:

- `ask_clarification` proyecta `next_questions` y `blocked_message`
- `reject_answer` proyecta `blocked_message` fijo y `next_questions`
- `keep_as_declared` agrega `next_step` declarativo
- bundle vacío no cambia el `render_contract`
- no muta el input
- preserva campos existentes
- no muestra IDs crudos
- no crea `evidence_candidate`
- no toca diagnóstico/findings
- no imports prohibidos

---

## 5. Criterios PASS

M58 puede declararse PASS si:

- el proyector existe;
- la suite focal pasa;
- no se tocó ningún archivo prohibido;
- no se introdujeron side effects.
