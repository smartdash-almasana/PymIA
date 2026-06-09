# M47 — Owner Questions Builder CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M47_OWNER_QUESTIONS_BUILDER_IMPLEMENTATION`

---

## 1. Capacidad

PymIA puede construir de forma determinística un `OwnerQuestionsBundle` a partir de faltantes ya trazados, sin abrir runtime ni conversación.

La capacidad autorizada es:

```text
missing_evidence
+ next_questions
+ blocked_message
+ source_ref
→ OwnerQuestion[]
→ OwnerQuestionsBundle
```

---

## 2. Qué puede hacer

M47 puede:

- convertir variables faltantes conocidas en preguntas explícitas por mapeo estático;
- convertir variables faltantes desconocidas en preguntas genéricas seguras;
- integrar `next_questions` como preguntas explícitas sin narrativa libre;
- proyectar `blocked_message` a una pregunta contextual mínima;
- deduplicar entradas repetidas;
- preservar orden determinístico;
- generar `question_id` determinísticos;
- preservar `source_ref`;
- adjuntar `metadata` opcional.

---

## 3. Qué no puede hacer

M47 no autoriza:

- runtime;
- graph;
- Telegram;
- Hermes;
- FastAPI;
- parser;
- `DiagnosticCore`;
- LLM;
- NLP;
- heurísticas libres;
- diagnóstico;
- findings nuevos.

---

## 4. Inputs requeridos

- `missing_evidence`
- `next_questions`
- `blocked_message`
- `source_ref`
- `metadata` opcional

---

## 5. Outputs requeridos

- `OwnerQuestionsBundle` válido
- preguntas con `required=True` por defecto
- `question_id` estable
- `reason` contractual
- `source_ref` preservado

---

## 6. Failure states

La capacidad debe admitir:

- bundle vacío si no hay entradas;
- faltantes conocidos;
- faltantes desconocidos;
- deduplicación de valores repetidos;
- integración simultánea de `missing_evidence`, `next_questions` y `blocked_message`.

---

## 7. Autoridad canónica

```text
ADR-019 — Guided Evidence Recovery Authority
```

---

## 8. Estado

```text
M47 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este documento autoriza el builder mínimo determinístico.
