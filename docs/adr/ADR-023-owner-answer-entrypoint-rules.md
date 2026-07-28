# ADR-023 — Owner Answer EntryPoint Rules

## Status

ACCEPTED

## Fecha

2026-06-09

## Dueño conceptual

Kernel PymIA / Owner Interaction Boundary / Contract Governance / EntryPoint Governance

## Context

Después de M45-M59, PymIA ya posee una cadena lógica pura para operar sobre respuestas del dueño:

```text
OwnerAnswersBundle
→ OwnerAnswerEvaluationBundle
→ OwnerNextActionBundle
→ OwnerResolvedNextActionBundle
→ RenderContract proyectado
```

Sin embargo, el repositorio todavía no define una frontera operacional soberana para el nacimiento de `OwnerAnswersBundle`.

El riesgo es que una respuesta conversacional libre sea tratada como contrato sin ancla formal, por ejemplo:

```text
last_user_message
→ inferir pregunta respondida
→ construir OwnerAnswer
```

Esa ruta queda prohibida porque puede asociar una respuesta ambigua a una pregunta incorrecta y contaminar el circuito owner-facing.

## Problem

El sistema necesita definir cuándo una respuesta del dueño puede transformarse en `OwnerAnswer` y agruparse en `OwnerAnswersBundle`.

La pregunta arquitectónica no es cómo evaluar respuestas —eso ya existe— sino cómo nacen legalmente.

Sin esta frontera, cualquier integración futura con `core_delivery_bridge.py`, `graph.py`, Telegram o adaptadores conversacionales podría fabricar respuestas implícitas.

## Decision

Se decide que una `OwnerAnswer` sólo puede nacer si existe una relación explícita y trazable con una pregunta contractual previa.

Reglas obligatorias:

1. Toda respuesta debe declarar `question_id` explícito.
2. El `question_id` debe existir en `OwnerQuestionsBundle.questions`.
3. La respuesta debe incluir `answer_text` o `structured_answer`.
4. La respuesta debe incluir `source_ref` trazable.
5. El `tenant_id` debe estar presente en el payload de entrada o en el contexto autorizado que envuelve la operación.
6. `question_text` debe provenir del `OwnerQuestionsBundle`, no de texto libre inventado.
7. El sistema debe fallar cerrado si no puede validar el vínculo `question_id -> OwnerQuestion`.

## Authorized entrypoint

La primera entrada autorizada es captura asistida estructurada:

```json
{
  "tenant_id": "tenant-demo",
  "question_id": "owner_question_dias_periodo",
  "answer_text": "El período es de 30 días",
  "structured_answer": {},
  "source_ref": "operator_assisted_capture",
  "metadata": {}
}
```

También puede omitirse `answer_text` si existe `structured_answer` suficiente y no vacío.

## Prohibited entrypoints

Queda prohibido:

- inferir `question_id` desde `last_user_message`;
- asumir que `pending_question` textual equivale a `question_id`;
- asociar respuesta a pregunta mediante LLM;
- asociar respuesta a pregunta mediante heurística blanda;
- construir `OwnerAnswer` desde texto libre sin payload estructurado;
- tratar `progressive_context` como fuente soberana si no contiene contrato explícito;
- promover `OwnerAnswer` a evidencia dura;
- generar diagnóstico o findings a partir de una respuesta declarada;
- integrar M59 en `core_delivery_bridge.py` sin un entrypoint formal de captura.

## Relation with progressive_context

`progressive_context` puede transportar datos transitorios, pero no es una fuente soberana por sí misma.

Sólo puede participar si contiene un payload estructurado que respete esta ADR y puede validarse contra un `OwnerQuestionsBundle` trazable.

## Relation with M59

M59 opera después de esta frontera.

```text
M60/M61 captura OwnerAnswersBundle
→ M59 evalúa, decide, resuelve y proyecta
```

M59 no debe recibir respuestas sintéticas ni inferidas.

## Fail-closed limits

El sistema debe fallar cerrado si:

- falta `question_id`;
- falta `answer_text` y falta `structured_answer`;
- falta `source_ref`;
- `question_id` no existe en el `OwnerQuestionsBundle`;
- el `OwnerQuestionsBundle` no está disponible o no es trazable;
- el payload intenta reemplazar `question_text` con texto no autorizado;
- se intenta capturar desde texto libre sin estructura.

## Consequences

Desde esta ADR:

- M60 se cierra como frontera documental de nacimiento de respuestas.
- M61 podrá implementar captura estructurada de respuestas.
- No queda autorizado modificar `graph.py`, Telegram, `core_delivery_bridge.py` ni runtime.
- `OwnerAnswersBundle` sigue separado de evidencia dura y diagnóstico.

## Future authorized slice

El siguiente frente implementativo recomendado es:

```text
M61_OWNER_ANSWER_STRUCTURED_CAPTURE
```

Función futura esperada:

```python
capture_owner_answers_from_structured_payload(
    *,
    questions_bundle: OwnerQuestionsBundle,
    answers_payload: list[dict],
    source_ref: str,
) -> OwnerAnswersBundle
```

Ese frente debe ser puro, testeable, fail-closed y sin integración runtime inicial.
