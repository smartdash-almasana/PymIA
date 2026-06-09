# M60 — Owner Answer EntryPoint Audit — TaskSpec

## Status

ACCEPTED

## Tipo

TaskSpec documental. No código ejecutable.

## Objetivo

Cerrar M60 como auditoría de frontera para el nacimiento legal de `OwnerAnswersBundle`.

## Tareas autorizadas

1. Crear ADR-023 con reglas de entrypoint de respuestas.
2. Crear CapabilitySpec M60.
3. Crear ModuleContract M60.
4. Crear TaskSpec M60.
5. Indexar documentos en `docs/DOCUMENTATION_INDEX.md`.

## Archivos autorizados

- `docs/adr/ADR-023-owner-answer-entrypoint-rules.md`
- `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_CAPABILITYSPEC.md`
- `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_MODULECONTRACT.md`
- `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_TASKSPEC.md`
- `docs/DOCUMENTATION_INDEX.md`

## Archivos prohibidos

- `pymia/`
- `tests/`
- `pymia/orchestration/graph.py`
- `pymia/orchestration/state.py`
- `pymia/orchestration/conversation_adapter.py`
- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/smartpyme/owner_action_pipeline.py`
- runtime
- Telegram
- Hermes
- DiagnosticCore

## Criterios PASS

- ADR-023 existe y define la frontera de nacimiento de `OwnerAnswer`.
- M60 CapabilitySpec existe.
- M60 ModuleContract existe.
- M60 TaskSpec existe.
- `DOCUMENTATION_INDEX.md` referencia ADR-023 y los documentos M60.
- No se modifica código ejecutable.
- No se agregan tests.
- No se autoriza integración runtime.

## Criterios BLOCKED

- Se intenta inferir `question_id` desde texto libre.
- Se propone tocar `graph.py` o Telegram.
- Se propone integrar M59 al bridge sin capturador estructurado.
- Se promueve `OwnerAnswer` a evidencia dura.
- Se introduce diagnóstico o findings.

## Resultado esperado

M60 debe dejar preparado el frente M61:

`M61_OWNER_ANSWER_STRUCTURED_CAPTURE`

M61 será el primer frente implementativo para transformar payloads estructurados en `OwnerAnswersBundle`.
