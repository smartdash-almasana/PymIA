# M52 — Owner Answer Evaluation Authorization ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION`

---

## 1. Módulo autorizado

`pymia/contracts/owner_evaluation.py`

---

## 2. Responsabilidad contractual

Este módulo define la estructura mínima para evaluar un `OwnerAnswersBundle` como artefacto epistemológico separado de evidencia, diagnóstico y runtime.

La frontera contractual es:

```text
OwnerAnswersBundle
→ OwnerAnswerEvaluation / OwnerAnswerEvaluationBundle
→ futuro consumo gobernado, si se autoriza en otro ciclo
```

---

## 3. Entrada conceptual

El contrato debe poder referenciar como input conceptual:

- `OwnerAnswersBundle`
- `source_answer_id`
- `linked_question_id`

No debe importar runtime para hacerlo.

---

## 4. Salida conceptual

El módulo debe exponer:

- `OwnerAnswerEvaluation`
- `OwnerAnswerEvaluationBundle`

Ambos deben ser serializables, trazables y determinísticos.

---

## 5. Reglas obligatorias

`OwnerAnswerEvaluation` debe:

- tener identificador estable;
- referenciar la respuesta origen;
- referenciar la pregunta asociada;
- tener un `verdict` explícito;
- permitir `mapped_key` opcional;
- permitir `normalized_value` opcional;
- preservar `validation_errors`;
- permitir `warnings` y `notes` opcionales.

`OwnerAnswerEvaluationBundle` debe:

- agrupar evaluaciones;
- preservar el orden;
- tener identificador estable;
- referenciar conceptualmente el `OwnerAnswersBundle` de entrada;
- serializar de manera estable.

---

## 6. Validaciones mínimas

Se debe rechazar, como mínimo:

- evaluaciones sin `evaluation_id`;
- evaluaciones sin `source_answer_id`;
- evaluaciones sin `linked_question_id`;
- bundles sin `bundle_id`;
- veredictos fuera del conjunto contractual.

Se debe permitir:

- `needs_clarification` con `validation_errors`;
- `rejected` con `validation_errors`;
- `accepted_as_declared` sin `evidence_candidate`;
- `verified` sin efectos laterales.

---

## 7. Prohibiciones

Este módulo no puede:

- escribir evidencia dura;
- modificar diagnóstico;
- recalcular fórmulas;
- tocar `graph`, `state` o runtime;
- importar `diagnostic_core`, Telegram o Hermes;
- introducir `evidence_candidate` en este slice.
