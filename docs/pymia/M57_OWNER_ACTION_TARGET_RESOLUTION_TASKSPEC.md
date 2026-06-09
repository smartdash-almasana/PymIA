# M57 — Owner Action Target Resolution TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M57_OWNER_ACTION_TARGET_RESOLUTION`

---

## 1. Objetivo

Implementar una resolución pura de IDs a texto:

```text
OwnerNextActionBundle
+ OwnerQuestionsBundle
→ OwnerResolvedNextActionBundle
```

Sin visibilidad todavía.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-022-owner-action-visibility-boundary.md`
- `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_TASKSPEC.md`
- `docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_CAPABILITYSPEC.md`
- `docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_CAPABILITYSPEC.md
docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_MODULECONTRACT.md
docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/contracts/owner_resolved_actions.py
pymia/smartpyme/owner_actions_resolver.py
tests/smartpyme/test_owner_actions_resolver.py
```

---

## 4. Tests mínimos

El test focal debe validar:

- resolución de un ID a `question_text` exacto;
- resolución múltiple preservando orden;
- `ValueError` ante ID inexistente;
- ausencia de texto inventado;
- resolución también para `keep_as_declared`;
- acción sin `target_questions` → `resolved_questions=[]`;
- preservación de `source_action_bundle_id`;
- preservación de `source_questions_bundle_id`;
- serialización del bundle;
- rechazo de `action_type` inválido;
- ausencia de imports prohibidos.

---

## 5. Criterios PASS

M57 puede declararse PASS si:

- el contrato existe;
- el resolver existe;
- la suite focal pasa;
- no se tocó ningún archivo prohibido;
- no se introdujeron side effects.
