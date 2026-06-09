# M52 — Owner Answer Evaluation Authorization CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION`

---

## 1. Objetivo

Autorizar el contrato mínimo para evaluar epistemológicamente un `OwnerAnswersBundle` sin consumirlo en diagnóstico, graph, state ni evidencia dura.

El alcance es puramente estructural.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-020-owner-response-capture-authority.md`
- `docs/adr/ADR-021-owner-answer-evaluation-authority.md`
- `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_TASKSPEC.md`

---

## 3. Capacidad autorizada

M52 autoriza una capacidad mínima para representar:

- una evaluación por respuesta capturada;
- el vínculo entre respuesta y pregunta;
- un veredicto contractual explícito;
- mapeo opcional hacia una clave normalizada;
- valor normalizado opcional;
- errores de validación;
- advertencias y notas opcionales;
- un bundle estable de evaluaciones.

---

## 4. Veredictos obligatorios

El contrato debe soportar exactamente:

- `accepted_as_declared`
- `verified`
- `needs_clarification`
- `rejected`

`verified` en este slice no implica verificación real externa.

---

## 5. Invariantes

La capacidad debe cumplir:

- trazabilidad explícita a `source_answer_id`;
- trazabilidad explícita a `linked_question_id`;
- serialización JSON-compatible determinística;
- preservación de orden;
- fail-closed para respuestas ambiguas, incompletas o contradictorias;
- ausencia de side effects.

---

## 6. No objetivos

M52 no autoriza:

- graph;
- state;
- runtime;
- recalculo de fórmulas;
- evidencia dura;
- validación material externa;
- `evidence_candidate`.

---

## 7. Artefacto esperado

El contrato mínimo debe existir en:

`pymia/contracts/owner_evaluation.py`

Y debe exponer:

- `OwnerAnswerEvaluation`
- `OwnerAnswerEvaluationBundle`

---

## 8. Criterio de cierre de este slice

M52 puede declararse PASS si:

- la documentación autorizante existe;
- el contrato existe;
- el test focal pasa;
- no se abrió runtime ni código fuera del alcance autorizado.
