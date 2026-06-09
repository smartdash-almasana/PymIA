# M60 — Owner Answer EntryPoint Audit — CapabilitySpec

## Status

ACCEPTED

## Tipo

Auditoría documental de frontera. No código ejecutable.

## Objetivo

Definir la capacidad futura que permitirá capturar respuestas del dueño como `OwnerAnswersBundle` sin inferir, inventar ni asociar texto libre a preguntas contractuales.

M60 no implementa captura. Sólo fija la frontera metodológica para M61.

## Contexto certificado

PymIA ya puede:

```text
missing_evidence
→ OwnerQuestionsBundle
→ pregunta visible owner-facing
```

También existe un pipeline lógico puro:

```text
OwnerAnswersBundle
→ evaluate_owner_answers
→ decide_owner_next_action
→ resolve_owner_next_action_targets
→ project_resolved_owner_actions_to_render_contract
```

El gap actual es anterior al pipeline:

```text
¿Cómo nace legalmente OwnerAnswersBundle?
```

## Capacidad autorizada futura

La capacidad futura autorizada por esta especificación es:

```text
OwnerQuestionsBundle + structured answer payload
→ OwnerAnswersBundle
```

Sólo será válida si cada respuesta declara explícitamente el `question_id` respondido.

## Entrada autorizada

Payload estructurado mínimo:

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

Campos obligatorios:

- `question_id`
- `source_ref`
- `answer_text` o `structured_answer`
- `tenant_id` en payload o contexto autorizado

## Salida futura esperada

`OwnerAnswersBundle` con respuestas validadas contra `OwnerQuestionsBundle`.

## Invariantes

- No inferir `question_id`.
- No usar LLM para asociar respuesta a pregunta.
- No usar `last_user_message` como respuesta contractual sin payload estructurado.
- No asumir que `pending_question` textual equivale a `question_id`.
- No promover respuestas declaradas a evidencia dura.
- No diagnosticar.
- No crear findings.

## Fail-closed

La futura capacidad debe fallar cerrado si:

- falta `question_id`;
- falta contenido de respuesta;
- falta `source_ref`;
- el `question_id` no existe en el `OwnerQuestionsBundle`;
- no hay trazabilidad hacia la pregunta emitida;
- el payload intenta sustituir el texto contractual de la pregunta.

## Fuera de alcance de M60

- Implementación de capturador.
- Cambios en `graph.py`.
- Cambios en Telegram.
- Cambios en `core_delivery_bridge.py`.
- Cambios en `owner_action_pipeline.py`.
- Tests ejecutables.
- Runtime.

## Próximo frente recomendado

```text
M61_OWNER_ANSWER_STRUCTURED_CAPTURE
```

Implementará un capturador puro basado en esta frontera.
