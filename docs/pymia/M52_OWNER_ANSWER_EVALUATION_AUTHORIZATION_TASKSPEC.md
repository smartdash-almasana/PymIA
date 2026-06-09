# M52 — Owner Answer Evaluation Authorization TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION`

---

## 1. Objetivo

Implementar el contrato mínimo para evaluar un `OwnerAnswersBundle` como salida estructurada separada de evidencia, diagnóstico y runtime.

Este slice es:

```text
contrato + esquema puro
```

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-020-owner-response-capture-authority.md`
- `docs/adr/ADR-021-owner-answer-evaluation-authority.md`
- `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_CAPABILITYSPEC.md`
- `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/adr/ADR-021-owner-answer-evaluation-authority.md
docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_CAPABILITYSPEC.md
docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_MODULECONTRACT.md
docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/contracts/owner_evaluation.py
tests/smartpyme/test_owner_evaluation_contract.py
```

---

## 4. Prohibiciones

No tocar:

- runtime;
- graph;
- state;
- Telegram;
- Hermes;
- FastAPI;
- `DiagnosticCore`;
- red;
- LLM;
- evidencia dura;
- fórmulas.

---

## 5. Contrato requerido

El módulo `pymia/contracts/owner_evaluation.py` debe permitir representar:

- `OwnerAnswerEvaluation`
- `OwnerAnswerEvaluationBundle`
- input conceptual: `OwnerAnswersBundle`
- output estructurado
- `verdict`
- `mapped_key`
- `normalized_value`
- `validation_errors`
- `warnings`
- `notes`
- `source_answer_id`
- `linked_question_id`

---

## 6. Tests requeridos

El test focal debe validar al menos:

- creación válida de `OwnerAnswerEvaluation`;
- creación válida de `OwnerAnswerEvaluationBundle`;
- serialización determinística;
- preservación de orden;
- rechazo de `verdict` inválido;
- soporte de `needs_clarification` con `validation_errors`;
- soporte de `rejected` con `validation_errors`;
- soporte de `accepted_as_declared` sin `evidence_candidate`;
- ausencia de side effects para `verified`;
- ausencia de imports prohibidos.

---

## 7. Criterios PASS

M52 puede declararse PASS si:

- el ADR existe;
- la documentación M52 existe;
- el contrato existe;
- el test focal pasa;
- no se tocó ningún archivo prohibido;
- no se agregó runtime.

---

## 8. Estado

```text
M52 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este TaskSpec autoriza el slice mínimo contractual de evaluación de respuestas del dueño.
