# M64 — Sandbox Owner Answer Replay CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M64_SANDBOX_OWNER_ANSWER_REPLAY`

---

## 1. Propósito

Certificar un replay sandbox observable de la cadena owner-answer ya implementada hasta M62.

La cadena autorizada es:

```text
OwnerQuestionsBundle
→ answers_payload estructurado
→ compose_owner_answers_to_actions(...)
→ projected_render_contract
→ salida verificable en test
```

---

## 2. Alcance

M64 autoriza únicamente:

- documentación mínima del frente;
- un test e2e sandbox;
- validación local focal y ampliada de la owner-answer chain.

M64 no autoriza:

- bridge;
- graph;
- runtime productivo;
- Telegram;
- LLM;
- `OwnerFacingReport`;
- persistencia;
- diagnóstico;
- evidencia dura.

---

## 3. Artefacto observable

El artefacto observable de M64 es:

```text
OwnerAnswerToActionCompositionResult.projected_render_contract
```

Este artefacto:

- sigue siendo técnico;
- no reemplaza `OwnerFacingReport`;
- no crea renderer paralelo;
- sólo permite verificar la proyección contractual ya existente.

---

## 4. Reglas obligatorias

El replay sandbox debe:

- construir `OwnerQuestionsBundle` explícito;
- capturar respuestas desde `answers_payload` estructurado;
- invocar `compose_owner_answers_to_actions(...)`;
- verificar artefactos intermedios y salida proyectada;
- demostrar no mutación de inputs;
- demostrar ausencia de IDs crudos en la salida final proyectada.

---

## 5. Fail-closed

M64 debe fallar si:

- el payload no alinea con `question_id` contractual;
- la salida observable depende de bridge, graph o runtime;
- el test introduce imports prohibidos;
- el replay intenta promover respuestas del dueño a evidencia dura;
- se intenta usar `OwnerFacingReport` como atajo de visibilidad.
