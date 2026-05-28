# PymIA OS — Contratos operativos

Actualización: 2026-05-28  
Base de referencia: `d44f2e0 test(orchestration): add longitudinal e2e flow`

Este documento fija los contratos vigentes de PymIA OS. No es roadmap, tutorial ni referencia exhaustiva de API.

## 1. Fronteras de responsabilidad

| Capa | Responsabilidad | No debe hacer |
|---|---|---|
| PymIA OS | Orquestación, estado, persistencia, replay, lifecycle, adapters, auditoría | Semántica PyME directa, lógica Telegram, dependencias de framework externo |
| SmartPyme | Dominio PyME, anamnesis, evidencia de negocio, readiness, microservicios, hallazgos | Gobernar estado global del OS o persistencia transversal |
| Telegram | Entrada/salida del usuario | Lógica de negocio, memoria, diagnóstico o routing complejo |

Regla: si una capacidad es transversal, vive en PymIA OS. Si depende del dominio PyME, vive en SmartPyme. Si solo transporta mensajes, vive en Telegram.

## 2. PymIAState

`PymIAState` es el estado vivo del caso. Debe seguir siendo serializable, auditable y recuperable.

Campos relevantes vigentes:

- `tenant_id`
- `chat_id`
- `conversation_id`
- `phase`
- `last_user_message`
- `pending_question`
- `intake_id`
- `evidence_ids`
- `sufficiency_status`
- `readiness_status`
- `runtime_candidate_status`
- `execution_status`
- `gate_verdict`
- `delivery_status`
- `delivery_summary`
- `output_refs`
- `findings_count`
- `progressive_context`
- `latest_evidence_path`
- `decision_trail`
- `errors`
- `created_at`
- `updated_at`

### Reglas de estado

- No guardar objetos complejos dentro de `PymIAState`.
- No agregar `delivery_package` al estado.
- No usar `Optional[object]` como campo de estado.
- `progressive_context` debe ser un `dict` JSON-serializable.
- `output_refs` debe ser una lista serializable.
- Fechas persistidas deben quedar como strings ISO al salir a JSON.

## 3. Contexto progresivo

`progressive_context` es la memoria conversacional estructurada mínima del OS.

Uso permitido:

- Acumular contexto conversacional entre turnos.
- Transportar datos simples entre adapter, graph y storage.
- Persistir estado conversacional útil para replay y auditoría.

Uso prohibido:

- Guardar objetos Python, dataclasses, callbacks, modelos, archivos abiertos o `datetime` crudos.
- Convertirlo en memoria semántica, vectorial o RAG.
- Mezclarlo con storage documental o evidence storage.

## 4. Storage

`pymia/orchestration/state_storage.py` gobierna persistencia JSONL append-only.

Funciones vigentes:

- `save_state(...)`
- `load_state(...)`
- `replay_conversation(...)`
- `get_conversation_history(...)`
- `find_conversations_by_tenant(...)`
- `export_conversation_jsonl(...)`

Reglas:

- El storage es append-only.
- `load_state` y `replay_conversation` recuperan el último estado por chat.
- Las funciones de historial/export retornan estructuras simples.
- Estados legacy sin campos nuevos deben tener defaults seguros.
- JSONL corrupto debe fallar de forma explícita, no ocultarse silenciosamente.

## 5. Adapters

Los adapters son los puentes controlados entre PymIA OS y otros dominios.

### conversation_adapter

`pymia/orchestration/conversation_adapter.py` es el puente autorizado entre eventos de texto del OS y la anamnesis de SmartPyme.

Contrato:

- `graph.py` puede importar `adapt_text_message` desde `pymia.orchestration.conversation_adapter`.
- `graph.py` no debe importar `pymia.smartpyme` directamente.
- El adapter no conoce Telegram.
- El adapter no toca storage.
- El adapter no muta el `progressive_context` recibido.
- El adapter debe fallar cerrado ante errores del dominio.

`phase_hint` permitido:

- `CONVERSATIONAL`
- `NEEDS_EVIDENCE`
- `BLOCKED`

Mapeo actual en graph:

| phase_hint | PymIAState.phase |
|---|---|
| `CONVERSATIONAL` | `NEW` |
| `NEEDS_EVIDENCE` | `WAITING_FOR_EVIDENCE` |
| `BLOCKED` | `BLOCKED` |

## 6. Estados del OS

Fases vigentes:

| Fase | Significado |
|---|---|
| `NEW` | Caso conversacional inicial o en curso sin evidencia suficiente |
| `WAITING_FOR_EVIDENCE` | El sistema necesita archivo/evidencia |
| `EVIDENCE_RECEIVED` | Evidencia recibida y registrada |
| `READY_TO_EXECUTE` | Evidencia/readiness permiten candidato de ejecución |
| `DELIVERED` | Resultado entregable construido |
| `BLOCKED` | Falta condición necesaria o gate bloqueó |
| `FAILED` | Error controlado de ejecución/entrega |

Reglas:

- No crear fases nuevas sin test y justificación de contrato.
- No usar strings libres de fase desde SmartPyme.
- Todo mapeo dominio → OS debe pasar por adapter o capa explícita.

## 7. Decision trail

`decision_trail` registra decisiones relevantes del runtime.

Debe registrar, como mínimo:

- route decisions;
- sufficiency/readiness;
- runtime candidate;
- dispatch;
- execution gate;
- delivery;
- errores controlados relevantes;
- decisiones del adapter conversacional cuando correspondan.

Regla: si una transición cambia el estado operacional del caso, debe dejar rastro.

## 8. Reglas no-drift

Prohibido salvo ciclo explícito y justificado:

- Reabrir Hermes.
- Introducir LangGraph.
- Mover lógica de negocio a Telegram.
- Importar SmartPyme directamente desde `graph.py`.
- Guardar objetos complejos en `PymIAState`.
- Persistir `DeliveryPackage` completo.
- Agregar memoria vectorial o semántica antes de cerrar contratos estructurados.
- Tocar Excel/microservicios si el ciclo está clasificado como `OS_CORE`.

## 9. Clasificación de ciclos

Todo ciclo debe clasificarse antes de implementarse:

- `OS_CORE`
- `ADAPTER`
- `DOMAIN_SMARTPYME`
- `TELEGRAM_ADAPTER`
- `MEMORY`
- `FACTORY`
- `DOCS_CONTRACT`

Regla de ejecución:

1. Coder diseña el ciclo.
2. GPT audita/recorta.
3. Codex implementa solo TaskSpec cerrado.
4. Usuario corre o valida tests.
5. Se commitea.
6. Se actualiza memoria.

## 10. Ciclos de referencia

- C7: audit CLI para inspección humana de estado.
- C8: `progressive_context` persistente y auditable.
- C9: `conversation_adapter` como puente OS ↔ SmartPyme.
- C10: E2E longitudinal text → evidence → diagnostic → replay/export.

Estos ciclos fijan la frontera actual del OS. Cualquier cambio posterior debe preservar estos contratos o declarar explícitamente que los reemplaza.
