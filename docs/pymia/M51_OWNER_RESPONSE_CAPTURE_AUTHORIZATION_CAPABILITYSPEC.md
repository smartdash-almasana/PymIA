# M51 — Owner Response Capture Authorization CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION`

---

## 1. Objetivo

Autorizar el contrato mínimo para capturar respuestas explícitas del dueño PyME a preguntas previamente emitidas por el sistema.

El alcance es puramente estructural.

No incluye runtime, ingestión productiva ni reinterpretación diagnóstica.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-019-guided-evidence-recovery-authority.md`
- `docs/adr/ADR-020-owner-response-capture-authority.md`
- `docs/pymia/M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_TASKSPEC.md`
- `docs/pymia/M50_GUIDED_EVIDENCE_RECOVERY_REPLAY_CHECKPOINT.md`

---

## 3. Capacidad autorizada

M51 autoriza una capacidad mínima para representar:

- qué pregunta originó la respuesta;
- qué texto o payload estructural respondió el dueño;
- qué tipo de respuesta se esperaba o se recibió;
- cuál es la referencia trazable de captura;
- en qué estado quedó la respuesta capturada;
- cómo agrupar múltiples respuestas en un bundle soberano.

---

## 4. Invariantes

La capacidad debe cumplir:

- trazabilidad explícita hacia la pregunta origen;
- trazabilidad explícita hacia la captura;
- separación estricta entre respuesta capturada y evidencia validada;
- serialización estable;
- fail-closed cuando falte referencia básica;
- cero inferencia diagnóstica.

---

## 5. No objetivos

M51 no autoriza:

- canales productivos;
- lógica conversacional;
- intake de archivos;
- parser documental;
- interpretación semántica libre;
- scoring o verificación de verdad;
- cambio de `state`, `graph` o runtime.

---

## 6. Artefacto esperado

El contrato mínimo debe existir en:

`pymia/contracts/owner_answers.py`

Y debe permitir, como mínimo:

- una entidad de respuesta individual;
- un bundle/lista de respuestas;
- serialización JSON estable;
- validaciones básicas de identidad y trazabilidad.

---

## 7. Criterio de cierre de este slice

M51 puede declararse PASS si:

- la documentación autorizante existe;
- el contrato existe;
- el test focal del contrato pasa;
- no se abrió runtime ni código fuera del alcance autorizado.
