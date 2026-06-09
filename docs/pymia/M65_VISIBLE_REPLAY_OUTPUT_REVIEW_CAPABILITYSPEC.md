# M65 — Visible Replay Output Review CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M65_VISIBLE_REPLAY_OUTPUT_REVIEW`

---

## 1. Propósito

Agregar una revisión humana sandbox de la salida técnica de M64.

La capacidad convierte un `OwnerAnswerToActionCompositionResult` en Markdown legible para auditoría y depuración interna.

No es salida productiva.
No es `OwnerFacingReport`.
No es renderer owner-facing.

---

## 2. Contexto

M64 ya demostró el circuito:

```text
OwnerQuestionsBundle
→ answers_payload estructurado
→ compose_owner_answers_to_actions
→ projected_render_contract
```

El resultado era verificable pero técnico.

M65 agrega una lectura humana sandbox sin cruzar a bridge, runtime ni frontera visible productiva.

---

## 3. Capacidad autorizada

Se autoriza un formateador puro:

```text
format_composition_result_for_human_review(result) -> str
```

El formateador debe:

- recibir un `OwnerAnswerToActionCompositionResult`;
- devolver Markdown;
- resumir respuestas capturadas;
- resumir evaluaciones;
- resumir próxima acción resuelta;
- resumir cambios proyectados en `render_contract`;
- declarar límites del sandbox.

---

## 4. Prohibiciones

M65 no autoriza:

- bridge;
- graph;
- runtime;
- Telegram;
- DiagnosticCore;
- `OwnerFacingReport` productivo;
- LLM;
- memoria conversacional;
- parser Excel;
- promoción de `OwnerAnswer` a evidencia dura;
- diagnóstico;
- renderer paralelo.

---

## 5. Reglas

El Markdown debe:

- ser legible para auditoría humana;
- indicar que es sandbox/review;
- no modificar `projected_render_contract`;
- no mostrar IDs contractuales crudos como texto humano principal;
- manejar secciones vacías con advertencia controlada;
- preservar la cadena M64 sin integrarse a producción.

---

## 6. Criterio PASS

M65 pasa si:

- crea el formateador puro;
- extiende el replay sandbox con asserts del Markdown;
- mantiene imports prohibidos fuera;
- no toca código productivo sensible;
- no toca bridge, graph ni runtime;
- mantiene M64 como sandbox.
