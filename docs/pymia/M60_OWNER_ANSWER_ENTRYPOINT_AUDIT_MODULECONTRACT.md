# M60 — Owner Answer EntryPoint Audit — ModuleContract

## Status

ACCEPTED

## Alcance

Este contrato define los límites del futuro módulo de captura estructurada de respuestas del dueño.

M60 no crea ese módulo. Sólo regula su forma autorizada.

## Contrato conceptual futuro

Nombre tentativo: `pymia.smartpyme.owner_answers_capture`.

Función futura esperada: `capture_owner_answers_from_structured_payload(...) -> OwnerAnswersBundle`.

## Inputs autorizados

- `OwnerQuestionsBundle` trazable.
- Lista de payloads estructurados con `question_id` explícito.
- `source_ref` de captura.
- `tenant_id` en payload o contexto autorizado.

## Output autorizado

- `OwnerAnswersBundle`.

## Reglas de validación

1. Cada payload debe declarar `question_id`.
2. Cada `question_id` debe existir en `questions_bundle.questions`.
3. Cada respuesta debe incluir `answer_text` o `structured_answer` no vacío.
4. El `question_text` del `OwnerAnswer` debe tomarse desde la pregunta contractual original.
5. `source_ref` debe preservarse.
6. El orden de respuestas debe ser determinístico.
7. La función debe ser pura y sin side effects.

## Imports permitidos futuros

- `pymia.contracts.owner_questions`
- `pymia.contracts.owner_answers`
- librería estándar estrictamente necesaria

## Imports prohibidos futuros

- orquestación conversacional
- estado runtime
- bridge de entrega
- Telegram
- DiagnosticCore
- pipeline owner-action
- proveedores generativos
- runtime externo

## Relación con progressive_context

`progressive_context` no es fuente soberana. Sólo podrá transportar payloads si estos cumplen el contrato estructurado y se validan contra `OwnerQuestionsBundle`.

## Relación con M59

M59 comienza después de la captura. El módulo de captura no debe invocar M59.

## Prohibiciones

- No inferir respuestas desde texto libre.
- No mapear por similitud semántica.
- No usar modelos generativos.
- No crear evidencia.
- No diagnosticar.
- No modificar findings.
- No escribir archivos.
- No modificar estado conversacional.

## Fail-closed

El módulo futuro debe lanzar error explícito ante desalineación de IDs, payload incompleto o falta de trazabilidad.
