# M47 — Owner Questions Builder TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M47_OWNER_QUESTIONS_BUILDER_IMPLEMENTATION`

---

## 1. Objetivo

Implementar el builder determinístico mínimo que convierta:

- `missing_evidence`
- `next_questions`
- `blocked_message`
- `source_ref`

en `OwnerQuestionsBundle`.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-019-guided-evidence-recovery-authority.md`
- `docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_TASKSPEC.md`
- `pymia/contracts/owner_questions.py`
- `docs/pymia/M47_OWNER_QUESTIONS_BUILDER_CAPABILITYSPEC.md`
- `docs/pymia/M47_OWNER_QUESTIONS_BUILDER_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M47_OWNER_QUESTIONS_BUILDER_CAPABILITYSPEC.md
docs/pymia/M47_OWNER_QUESTIONS_BUILDER_MODULECONTRACT.md
docs/pymia/M47_OWNER_QUESTIONS_BUILDER_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/smartpyme/owner_questions_builder.py
tests/smartpyme/test_owner_questions_builder.py
```

---

## 4. Reglas implementativas

- usar `OwnerQuestion` y `OwnerQuestionsBundle` existentes;
- preservar orden determinístico;
- deduplicar entradas repetidas;
- generar `question_id` determinístico;
- `required=True` por defecto;
- `metadata` opcional;
- preservar `source_ref`;
- variable conocida → pregunta por mapeo estático;
- variable desconocida → pregunta genérica segura;
- `blocked_message` puede generar pregunta contextual;
- `next_questions` se integran sin narrativa libre.

---

## 5. Prohibiciones

No tocar:

- runtime;
- graph;
- Telegram;
- Hermes;
- FastAPI;
- parser;
- `DiagnosticCore`;
- LLM;
- NLP.

---

## 6. Tests requeridos

El test focal debe validar al menos:

- variables conocidas → preguntas explícitas;
- variables desconocidas → fallback seguro;
- deduplicación;
- orden estable;
- IDs determinísticos;
- `blocked_message` preservado en metadata o `reason`;
- `next_questions` integradas;
- serialización válida del `OwnerQuestionsBundle`.

---

## 7. Criterios PASS

M47 puede declararse PASS si:

- el builder existe;
- el test focal pasa;
- el diff toca sólo archivos autorizados;
- no se introdujo runtime ni heurística libre.

---

## 8. Estado

```text
M47 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este TaskSpec autoriza el slice mínimo del builder.
