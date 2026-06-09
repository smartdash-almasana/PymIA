# M46 — Owner Questions Contract TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M46_OWNER_QUESTIONS_CONTRACT_AUTHORIZATION`

---

## 1. Objetivo

Implementar el contrato mínimo para representar preguntas explícitas al dueño PyME derivadas de:

- `missing_evidence`
- `next_questions`
- `blocked_message`

Este slice define estructura, no comportamiento conversacional.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-019-guided-evidence-recovery-authority.md`
- `docs/pymia/M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_CAPABILITYSPEC.md`
- `docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_CAPABILITYSPEC.md
docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_MODULECONTRACT.md
docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/contracts/owner_questions.py
tests/smartpyme/test_owner_questions_contract.py
```

---

## 4. Prohibiciones

No tocar:

- runtime;
- Telegram;
- Hermes;
- FastAPI;
- graph;
- parser Excel;
- `DiagnosticCoreV1`;
- lógica conversacional;
- generación heurística de preguntas.

---

## 5. Contrato requerido

El módulo `pymia/contracts/owner_questions.py` debe permitir representar:

- `question_id`
- `question_text`
- `reason`
- `missing_key`
- `source_ref`
- `expected_answer_type`
- `required`
- `metadata`
- bundle/lista de preguntas

---

## 6. Tests requeridos

El test focal debe validar al menos:

- construcción válida de una pregunta;
- serialización estable;
- bundle/lista de preguntas;
- preservación de `missing_key=None` cuando no exista;
- rechazo de preguntas sin texto o sin referencia trazable.

---

## 7. Criterios PASS

M46 puede declararse PASS si:

- el contrato existe;
- el test focal pasa;
- no se tocó ningún archivo prohibido;
- no se agregó runtime ni lógica heurística.

---

## 8. Estado

```text
M46 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este TaskSpec autoriza el slice mínimo contractual.
