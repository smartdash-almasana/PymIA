# M55 — Owner Next Action Decision CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M55_OWNER_NEXT_ACTION_DECISION`

---

## 1. Objetivo

Autorizar una decisión mínima y pura:

```text
OwnerAnswerEvaluationBundle
→ OwnerNextActionBundle
```

Sin integración, sin side effects y sin respuesta visible todavía.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M54_OWNER_ANSWER_EVALUATION_REPLAY_CHECKPOINT.md`

---

## 3. Capacidad autorizada

M55 autoriza un decider mínimo que:

- recibe un `OwnerAnswerEvaluationBundle`;
- decide una sola acción para el bundle;
- preserva `source_evaluation_bundle_id`;
- produce salida JSON-compatible;
- no usa UUIDs aleatorios.

---

## 4. Prioridad obligatoria

La decisión debe respetar:

```text
needs_clarification
> rejected
> keep_as_declared
```

Reglas:

1. bundle vacío → `ask_clarification`
2. si existe `needs_clarification` → `ask_clarification`
3. si existe `rejected` y no hay `needs_clarification` → `reject_answer`
4. si todas son `accepted_as_declared` o `verified` → `keep_as_declared`

---

## 5. No objetivos

M55 no autoriza:

- `evidence_candidate`
- diagnóstico
- runtime
- graph/state
- respuesta visible
- integración con `core_delivery_bridge`

---

## 6. Artefactos esperados

Contrato:

`pymia/contracts/owner_actions.py`

Implementación:

`pymia/smartpyme/owner_actions_decider.py`
