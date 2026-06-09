# M61 — Owner Answer Structured Capture TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M61_OWNER_ANSWER_STRUCTURED_CAPTURE`

---

## 1. Objetivo

Implementar un capturador puro de respuestas estructuradas del dueño sin integración runtime.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-023-owner-answer-entrypoint-rules.md`
- `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_CAPABILITYSPEC.md`
- `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_MODULECONTRACT.md`
- `docs/pymia/M61_OWNER_ANSWER_STRUCTURED_CAPTURE_CAPABILITYSPEC.md`
- `docs/pymia/M61_OWNER_ANSWER_STRUCTURED_CAPTURE_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M61_OWNER_ANSWER_STRUCTURED_CAPTURE_CAPABILITYSPEC.md
docs/pymia/M61_OWNER_ANSWER_STRUCTURED_CAPTURE_MODULECONTRACT.md
docs/pymia/M61_OWNER_ANSWER_STRUCTURED_CAPTURE_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/smartpyme/owner_answers_capture.py
tests/smartpyme/test_owner_answers_capture.py
```

---

## 4. Tests mínimos

La suite focal debe validar:

- captura con `answer_text`
- captura con `structured_answer` sin `answer_text`
- toma de `question_text` desde contrato
- fallo ante `question_text` diferente
- fallo por falta de `question_id`
- fallo por `question_id` inexistente
- fallo por falta de contenido
- fallo por `source_ref` vacío
- fallback a `expected_answer_type`
- aceptación de `answer_type` válido del payload
- rechazo de `answer_type` inválido
- IDs determinísticos
- metadata trazable
- no mutación de inputs
- ausencia de imports prohibidos

---

## 5. Criterios PASS

M61 puede declararse PASS si:

- el capturador existe;
- la suite focal pasa;
- no se tocó ningún archivo prohibido;
- no se introdujeron side effects.
