# M49 — Visible Owner Questions CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M49_VISIBLE_OWNER_QUESTIONS`

---

## 1. Capacidad

PymIA puede hacer visibles las preguntas owner-facing dentro del `render_contract` ya existente, sin abrir un canal nuevo ni cambiar el state/graph.

La capacidad autorizada es:

```text
OwnerQuestionsBundle.question_texts
→ render_contract["next_questions"]
→ render_contract["blocked_message"] = primera pregunta
→ owner-facing / delivery response ya existente
```

---

## 2. Qué puede hacer

M49 puede:

- copiar preguntas válidas del `OwnerQuestionsBundle` al `render_contract`;
- usar la primera pregunta como `blocked_message`;
- dejar visible ese contenido en artefactos ya existentes;
- hacer que `render_contract.json` refleje la nueva proyección.

---

## 3. Qué no puede hacer

M49 no autoriza:

- `graph.py`;
- `PymIAState`;
- `owner_questions.py`;
- `owner_questions_builder.py`;
- `DiagnosticCore`;
- parser;
- Telegram;
- Hermes;
- FastAPI;
- runtime conversacional.

---

## 4. Inputs requeridos

- `OwnerQuestionsBundle`
- `render_contract`
- `question_text` válidos del bundle

---

## 5. Outputs requeridos

- `render_contract["next_questions"]` con preguntas visibles
- `render_contract["blocked_message"]` igual a la primera pregunta, si existe
- `render_contract.json` escrito después de esa proyección

---

## 6. Estado

```text
M49 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este documento autoriza sólo la visibilidad de preguntas dentro del circuito ya existente.
