# M61 — Owner Answer Structured Capture CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M61_OWNER_ANSWER_STRUCTURED_CAPTURE`

---

## 1. Objetivo

Autorizar una captura pura y estructurada:

```text
OwnerQuestionsBundle
+ answers_payload
+ source_ref
→ OwnerAnswersBundle
```

Sin integración runtime.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-023-owner-answer-entrypoint-rules.md`
- `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_CAPABILITYSPEC.md`
- `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_MODULECONTRACT.md`

---

## 3. Capacidad autorizada

M61 autoriza capturar respuestas del dueño únicamente desde payloads estructurados validados contra `OwnerQuestionsBundle`.

Debe:

- exigir `question_id` explícito;
- exigir contenido de respuesta;
- tomar `question_text` desde la pregunta contractual;
- resolver `answer_type` desde payload válido o desde `OwnerQuestion.expected_answer_type`;
- construir IDs determinísticos;
- preservar metadata mínima trazable.

---

## 4. Reglas obligatorias

- `question_id` es obligatorio
- `question_id` debe existir en `questions_bundle.questions`
- la respuesta debe incluir `answer_text` o `structured_answer` no vacío
- `question_text` del `OwnerAnswer` debe provenir del `OwnerQuestionsBundle`
- `source_ref` efectivo debe ser el parámetro `source_ref`
- si el payload también trae `source_ref`, el parámetro tiene prioridad
- si el payload trae `question_text` distinto del contractual, debe fallar cerrado

---

## 5. Invariantes

- `answer_id = f"{questions_bundle.bundle_id}:answer:{index}:{question_id}"`
- `bundle_id = f"{questions_bundle.bundle_id}:answers"`
- metadata mínima:
  - `source_questions_bundle_id`
  - `tenant_id`, si fue provisto
  - `capture_mode = "structured_payload"`
- sin mutar `questions_bundle`
- sin mutar `answers_payload`
- sin inferir desde texto libre
- sin LLM
- sin evidencia
- sin diagnóstico

---

## 6. Artefacto esperado

Implementación en:

`pymia/smartpyme/owner_answers_capture.py`

Función requerida:

`capture_owner_answers_from_structured_payload(...) -> OwnerAnswersBundle`
