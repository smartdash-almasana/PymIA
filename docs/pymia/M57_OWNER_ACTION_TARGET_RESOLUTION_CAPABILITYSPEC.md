# M57 — Owner Action Target Resolution CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M57_OWNER_ACTION_TARGET_RESOLUTION`

---

## 1. Objetivo

Autorizar una resolución pura:

```text
OwnerNextActionBundle
→ resolución de target_questions ID -> question_text
→ OwnerResolvedNextActionBundle
```

Sin visibilidad todavía y sin side effects.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-022-owner-action-visibility-boundary.md`
- `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_TASKSPEC.md`

---

## 3. Capacidad autorizada

M57 autoriza resolver cada ID de `target_questions` contra `OwnerQuestionsBundle.questions`.

Debe:

- usar `question_text` exacto cuando exista;
- fallar con `ValueError` si un ID no existe;
- no inventar texto;
- no mostrar IDs crudos como texto final;
- preservar orden y `action_type`.

---

## 4. Invariantes

- IDs determinísticos, no UUID random
- salida json-compatible
- fail-closed ante ID inexistente
- sin side effects
- sin `evidence_candidate`
- sin diagnóstico
- sin render visible todavía

---

## 5. Artefactos esperados

Contrato:

`pymia/contracts/owner_resolved_actions.py`

Implementación:

`pymia/smartpyme/owner_actions_resolver.py`
