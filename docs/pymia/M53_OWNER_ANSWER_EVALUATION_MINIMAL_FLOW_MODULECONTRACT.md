# M53 — Owner Answer Evaluation Minimal Flow ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW`

---

## 1. Módulo autorizado

`pymia/smartpyme/owner_answers_evaluator.py`

---

## 2. Responsabilidad contractual

Este módulo implementa un evaluador puro que transforma `OwnerAnswersBundle` en `OwnerAnswerEvaluationBundle` sin side effects.

La frontera contractual es:

```text
OwnerAnswersBundle
→ evaluate_owner_answers(...)
→ OwnerAnswerEvaluationBundle
```

---

## 3. Reglas de salida

Cada evaluación debe:

- usar `source_answer_id = answer.answer_id`;
- usar `linked_question_id = answer.question_id`;
- usar `evaluation_id` determinístico derivado de la respuesta;
- preservar orden de entrada;
- omitir cualquier noción de `evidence_candidate`.

---

## 4. Mapeo mínimo

Para números válidos, el evaluador debe completar:

- `verdict = accepted_as_declared`
- `mapped_key` opcional derivado de metadata o estructura trazable
- `normalized_value` numérico

Para `owner_declared_fact` y `operational_meaning` con texto no vacío:

- `verdict = accepted_as_declared`

Para casos ambiguos o inválidos:

- `needs_clarification` o `rejected` fail-closed

---

## 5. Prohibiciones

El módulo no puede:

- tocar `graph.py`;
- tocar `PymIAState`;
- importar runtime;
- recalcular fórmulas;
- modificar diagnóstico;
- generar red, memoria o side effects externos.
