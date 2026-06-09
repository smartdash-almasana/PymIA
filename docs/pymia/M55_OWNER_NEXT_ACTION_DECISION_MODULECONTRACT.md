# M55 — Owner Next Action Decision ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M55_OWNER_NEXT_ACTION_DECISION`

---

## 1. Módulos autorizados

- `pymia/contracts/owner_actions.py`
- `pymia/smartpyme/owner_actions_decider.py`

---

## 2. Responsabilidad contractual

Estos módulos definen y ejecutan una decisión mínima sobre un `OwnerAnswerEvaluationBundle` sin tocar ninguna otra capa.

La frontera contractual es:

```text
OwnerAnswerEvaluationBundle
→ decide_owner_next_action(...)
→ OwnerNextActionBundle
```

---

## 3. Contrato requerido

`OwnerNextAction` debe permitir:

- `action_id`
- `action_type`
- `target_questions`
- `metadata`

`OwnerNextActionBundle` debe permitir:

- `bundle_id`
- `source_evaluation_bundle_id`
- `actions`
- `created_at` ISO UTC

---

## 4. Reglas de decisión

Se permite una única acción por bundle en este slice.

La acción debe:

- ser determinística;
- preservar preguntas objetivo relevantes;
- conservar `source_evaluation_bundle_id`;
- no promover nada a evidencia.

---

## 5. Prohibiciones

Estos módulos no pueden:

- tocar `graph.py`;
- tocar `PymIAState`;
- tocar `core_delivery_bridge.py`;
- tocar `DiagnosticCore`;
- importar runtime, Hermes, Telegram, FastAPI, LLM o memoria;
- emitir respuesta visible.
