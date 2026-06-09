# M53 — Owner Answer Evaluation Minimal Flow CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW`

---

## 1. Objetivo

Autorizar un evaluador puro y determinístico:

```text
OwnerAnswersBundle
→ OwnerAnswerEvaluationBundle
```

Sin runtime, sin graph/state y sin promoción a evidencia dura.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_TASKSPEC.md`

---

## 3. Capacidad autorizada

M53 autoriza una transformación mínima y determinística desde respuestas capturadas hacia evaluaciones estructuradas.

Debe:

- preservar orden;
- preservar `source_answer_id`;
- preservar `linked_question_id`;
- generar IDs determinísticos;
- producir salida JSON-compatible;
- no usar `verified`.

---

## 4. Reglas mínimas obligatorias

El evaluador debe aplicar:

1. `capture_status in {"declined", "unclear"}` → `rejected`
2. `answer_text` vacío y sin `structured_answer` → `needs_clarification`
3. `answer_type == "number"`
   - no parseable → `rejected`
   - negativo → `rejected`
   - válido → `accepted_as_declared`
4. `answer_type in {"owner_declared_fact", "operational_meaning"}` con texto → `accepted_as_declared`

---

## 5. No objetivos

M53 no autoriza:

- `verified`;
- `evidence_candidate`;
- diagnóstico;
- fórmulas;
- runtime;
- imports de graph/state/DiagnosticCore/Hermes/Telegram/FastAPI/LLM.

---

## 6. Artefacto esperado

Implementación en:

`pymia/smartpyme/owner_answers_evaluator.py`

Función requerida:

`evaluate_owner_answers(bundle: OwnerAnswersBundle) -> OwnerAnswerEvaluationBundle`
