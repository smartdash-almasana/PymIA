# M53 — Owner Answer Evaluation Minimal Flow TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW`

---

## 1. Objetivo

Implementar un evaluador puro:

```text
OwnerAnswersBundle
→ OwnerAnswerEvaluationBundle
```

Con reglas determinísticas mínimas y sin uso de runtime.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW_CAPABILITYSPEC.md`
- `docs/pymia/M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW_CAPABILITYSPEC.md
docs/pymia/M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW_MODULECONTRACT.md
docs/pymia/M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/smartpyme/owner_answers_evaluator.py
tests/smartpyme/test_owner_answers_evaluator.py
```

---

## 4. Reglas obligatorias

- `declined` o `unclear` → `rejected`
- respuesta vacía sin `structured_answer` → `needs_clarification`
- número no parseable → `rejected`
- número negativo → `rejected`
- número válido → `accepted_as_declared`
- `owner_declared_fact` o `operational_meaning` con texto → `accepted_as_declared`
- `verified` no se usa

---

## 5. Tests mínimos

El test focal debe validar:

- número válido
- número no parseable
- número negativo
- respuesta vacía
- `declined`
- `unclear`
- `operational_meaning`
- preservación de orden
- ausencia de `verified`
- ausencia de `evidence_candidate`
- ausencia de imports prohibidos

---

## 6. Criterios PASS

M53 puede declararse PASS si:

- el evaluador existe;
- la suite focal pasa;
- no se tocó ningún archivo prohibido;
- no se introdujeron side effects.
