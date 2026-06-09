# M55 — Owner Next Action Decision TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M55_OWNER_NEXT_ACTION_DECISION`

---

## 1. Objetivo

Implementar una decisión pura:

```text
OwnerAnswerEvaluationBundle
→ OwnerNextActionBundle
```

Sin integración y sin side effects.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M54_OWNER_ANSWER_EVALUATION_REPLAY_CHECKPOINT.md`
- `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_CAPABILITYSPEC.md`
- `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_CAPABILITYSPEC.md
docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_MODULECONTRACT.md
docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/contracts/owner_actions.py
pymia/smartpyme/owner_actions_decider.py
tests/smartpyme/test_owner_actions_decider.py
```

---

## 4. Reglas obligatorias

- bundle vacío → `ask_clarification`
- `needs_clarification` domina
- `rejected` sin `needs_clarification` → `reject_answer`
- `accepted_as_declared` o `verified` únicamente → `keep_as_declared`
- una sola acción por bundle

---

## 5. Tests mínimos

El test focal debe validar:

- bundle vacío
- prioridad `needs_clarification > rejected`
- `reject_answer` cuando corresponda
- `keep_as_declared` para `accepted_as_declared`
- `keep_as_declared` para `verified`
- preservación de `source_evaluation_bundle_id`
- serialización
- rechazo de `action_type` inválido
- ausencia de `evidence_candidate`
- ausencia de imports prohibidos

---

## 6. Criterios PASS

M55 puede declararse PASS si:

- el contrato existe;
- el decider existe;
- la suite focal pasa;
- no se tocó ningún archivo prohibido;
- no se introdujeron side effects.
