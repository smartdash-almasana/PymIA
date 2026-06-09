# M51 — Owner Response Capture Authorization TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION`

---

## 1. Objetivo

Implementar el contrato mínimo para representar respuestas explícitas del dueño PyME a preguntas ya emitidas por el sistema.

Este slice es:

```text
contrato + esquema puro
```

No autoriza runtime.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-019-guided-evidence-recovery-authority.md`
- `docs/adr/ADR-020-owner-response-capture-authority.md`
- `docs/pymia/M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_TASKSPEC.md`
- `docs/pymia/M50_GUIDED_EVIDENCE_RECOVERY_REPLAY_CHECKPOINT.md`
- `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_CAPABILITYSPEC.md`
- `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/adr/ADR-020-owner-response-capture-authority.md
docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_CAPABILITYSPEC.md
docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_MODULECONTRACT.md
docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/contracts/owner_answers.py
tests/smartpyme/test_owner_answers_contract.py
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
- `DiagnosticCore`;
- intake productivo;
- lógica conversacional;
- validación automática de verdad.

---

## 5. Contrato requerido

El módulo `pymia/contracts/owner_answers.py` debe permitir representar:

- `answer_id`
- `question_id`
- `question_text`
- `answer_text`
- `structured_answer`
- `answer_type`
- `capture_status`
- `source_ref`
- `metadata`
- bundle/lista de respuestas

---

## 6. Tests requeridos

El test focal debe validar al menos:

- construcción válida de una respuesta explícita;
- serialización estable;
- bundle/lista de respuestas;
- normalización de `answer_text` vacío hacia `None`;
- rechazo de respuestas sin identidad o trazabilidad básica;
- rechazo de respuesta `provided` sin contenido.

---

## 7. Criterios PASS

M51 puede declararse PASS si:

- el ADR existe;
- la documentación M51 existe;
- el contrato existe;
- el test focal pasa;
- no se tocó ningún archivo prohibido;
- no se agregó runtime.

---

## 8. Estado

```text
M51 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este TaskSpec autoriza el slice mínimo contractual de captura de respuestas.
