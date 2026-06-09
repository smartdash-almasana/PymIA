# M63 — Owner Action Visibility Reentry Boundary CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY`

---

## 1. Propósito

Autorizar una frontera documental para definir cómo el `render_contract` proyectado por M62 puede reingresar a la frontera visible soberana `OwnerFacingReport` sin crear un renderer paralelo, sin tocar runtime y sin introducir autoridad diagnóstica adicional.

M63 no implementa integración.

M63 fija el contrato conceptual previo para una futura integración controlada.

---

## 2. Contexto certificado

La cadena owner-answer ya contiene:

```text
M59 = pipeline owner-action puro
M60 = regla legal de nacimiento de OwnerAnswer
M61 = captura estructurada pura de OwnerAnswer
M62 = composición pura M61 + M59
```

M62 produce:

```text
OwnerAnswerToActionCompositionResult
- owner_answers_bundle
- evaluation_bundle
- action_bundle
- resolved_action_bundle
- projected_render_contract
```

ADR-018 establece que `OwnerFacingReport` es una traducción controlada y trazable de artefactos existentes.

ADR-022 establece que `OwnerFacingReport` sigue siendo la frontera owner-facing soberana y prohíbe renderizadores paralelos de acciones owner-facing.

M63A clasificó las fallas globales preexistentes como deuda separada y determinó que no bloquean M63 documental.

---

## 3. Capacidad autorizada

M63 autoriza únicamente documentación de frontera para:

1. declarar `OwnerFacingReport` como frontera visible soberana de reentrada;
2. definir que `projected_render_contract` de M62 es un artefacto técnico intermedio, no una salida visible directa;
3. prohibir mostrar `OwnerNextActionBundle` o `OwnerResolvedNextActionBundle` por un canal paralelo;
4. declarar `core_delivery_bridge.py` como candidato futuro de integración, pero no modificarlo en M63;
5. fijar criterios mínimos para una futura implementación M63B/M64B si fuera autorizada.

---

## 4. Fuentes permitidas para una futura reentrada visible

Una futura reentrada visible sólo podrá leer artefactos ya existentes y trazables:

- `RenderContract`
- `OwnerFacingReport`
- `DeliveryPackage`
- `OwnerQuestionsBundle`
- `OwnerAnswerEvaluationBundle`
- `OwnerNextActionBundle`
- `OwnerResolvedNextActionBundle`
- `OwnerAnswerToActionCompositionResult.projected_render_contract`

La fuente visible soberana seguirá siendo `OwnerFacingReport` o su frontera contractual equivalente.

---

## 5. Fuentes prohibidas

Una futura reentrada visible no puede leer:

- texto libre del último mensaje como `OwnerAnswer`;
- IDs crudos como salida final al dueño;
- memoria no contractual;
- LLM para asociar preguntas y respuestas;
- Telegram o runtime como fuente de verdad owner-facing;
- heurísticas conversacionales antiguas como sustituto de `question_id`.

---

## 6. Conductas prohibidas

M63 no autoriza:

- tocar `graph.py`;
- tocar `state.py`;
- tocar `conversation_adapter.py`;
- tocar `core_delivery_bridge.py`;
- tocar Telegram;
- tocar runtime;
- tocar `DiagnosticCore`;
- crear renderer paralelo;
- duplicar `OwnerFacingReport`;
- diagnosticar desde declaraciones del dueño;
- convertir `OwnerAnswer` u `OwnerNextAction` en evidencia dura;
- ocultar bloqueos;
- mostrar IDs crudos al dueño;
- mezclar estabilización global M64 con la frontera M63.

---

## 7. Resultado esperado de M63

M63 debe dejar tres documentos:

- CapabilitySpec
- ModuleContract
- TaskSpec

Estos documentos deben bastar para que un futuro frente implementativo sepa:

- qué artefacto es visible y soberano;
- qué artefactos son técnicos;
- qué módulo candidato podría integrar en el futuro;
- qué archivos están prohibidos ahora;
- qué criterios fail-closed rigen antes de hacer visible una acción owner-facing.

---

## 8. Criterio PASS

M63 pasa si:

- no modifica código productivo;
- no modifica tests;
- no toca bridge, graph, runtime ni Telegram;
- actualiza el índice documental;
- deja explícita la separación entre `projected_render_contract` y salida visible al dueño;
- preserva `OwnerFacingReport` como frontera visible soberana;
- registra que M64 global-test-stabilization es un frente separado.
