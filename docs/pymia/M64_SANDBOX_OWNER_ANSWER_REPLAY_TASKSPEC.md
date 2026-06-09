# M64 — Sandbox Owner Answer Replay TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M64_SANDBOX_OWNER_ANSWER_REPLAY`

---

## 1. Objetivo

Cerrar un replay sandbox observable de la cadena owner-answer sin tocar runtime, graph ni bridge.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `Pymia-memoria/M64_SANDBOX_OWNER_ANSWER_REPLAY_AUDIT_APPROVAL_20260609.md`
- `docs/adr/ADR-018-owner-facing-report-boundary.md`
- `docs/adr/ADR-022-owner-action-visibility-boundary.md`
- `docs/adr/ADR-023-owner-answer-entrypoint-rules.md`
- `docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_MODULECONTRACT.md`
- `docs/pymia/M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY_MODULECONTRACT.md`
- `docs/pymia/M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
tests/smartpyme/e2e/test_owner_answer_e2e_sandbox.py
docs/pymia/M64_SANDBOX_OWNER_ANSWER_REPLAY_CAPABILITYSPEC.md
docs/pymia/M64_SANDBOX_OWNER_ANSWER_REPLAY_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
```

---

## 4. Tests mínimos

La suite focal debe validar:

- construcción explícita de `OwnerQuestionsBundle`;
- construcción explícita de `answers_payload` estructurado;
- llamada a `compose_owner_answers_to_actions(...)`;
- presencia de `owner_answers_bundle`, `evaluation_bundle`, `action_bundle`, `resolved_action_bundle` y `projected_render_contract`;
- `next_steps` proyectado no vacío o equivalente contractual;
- ausencia de IDs crudos en la salida final;
- no mutación de `answers_payload`;
- no mutación de `render_contract`;
- ausencia de imports prohibidos en el test sandbox.

---

## 5. Criterios PASS

M64 puede declararse PASS si:

- el test sandbox existe;
- la validación focal pasa;
- la validación ampliada de la owner-answer chain pasa;
- no se tocó ningún archivo prohibido;
- no se abrió integración visible productiva.
