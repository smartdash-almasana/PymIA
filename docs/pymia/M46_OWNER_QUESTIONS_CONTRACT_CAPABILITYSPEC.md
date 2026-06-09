# M46 — Owner Questions Contract CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M46_OWNER_QUESTIONS_CONTRACT_AUTHORIZATION`

---

## 1. Capacidad

PymIA puede representar preguntas explícitas al dueño PyME como un contrato estructurado, derivado únicamente de faltantes ya trazados en artefactos existentes.

La capacidad autorizada es:

```text
missing_evidence
+ next_questions
+ blocked_message
→ OwnerQuestion[]
→ OwnerQuestionsBundle
```

---

## 2. Qué puede hacer

M46 puede:

- definir un contrato mínimo para preguntas explícitas al dueño;
- representar preguntas derivadas de faltantes ya registrados;
- distinguir el motivo (`reason`) y la clave faltante (`missing_key`) cuando exista;
- preservar trazabilidad hacia el artefacto fuente (`source_ref`);
- agrupar preguntas en un bundle serializable.

---

## 3. Qué no puede hacer

M46 no autoriza:

- generar preguntas por heurística;
- lógica conversacional;
- runtime;
- Telegram;
- Hermes;
- FastAPI;
- graph;
- parser Excel;
- cambios en `DiagnosticCoreV1`;
- inventar evidencia o sentido operativo.

---

## 4. Inputs requeridos

- `missing_evidence`
- `next_questions`
- `blocked_message`
- referencias trazables al artefacto de origen

---

## 5. Outputs requeridos

Un contrato mínimo que permita representar:

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

## 6. Failure states

La capacidad debe admitir:

- preguntas ligadas a una variable faltante;
- preguntas ligadas a una aclaración operativa;
- preguntas ligadas a un bloqueo explícito;
- bundle vacío si no hay preguntas trazables.

---

## 7. Autoridad canónica

```text
ADR-019 — Guided Evidence Recovery Authority
```

---

## 8. Estado

```text
M46 = AUTHORIZED_FOR_MINIMAL_CONTRACT
```

Este documento autoriza el contrato mínimo.

No certifica runtime ni recuperación guiada implementada.
