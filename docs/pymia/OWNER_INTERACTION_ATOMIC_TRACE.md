# OWNER_INTERACTION_ATOMIC_TRACE

## Estado

`DRAFT_ATOMIC_TRACE`

## Fecha

2026-06-12

## Propósito

Fijar la traza atómica de interacción entre el dueño PyME y PymIA:

```text
Dueño
→ mensaje crudo
→ anamnesis / ficha
→ evidencia
→ suficiencia
→ core diagnóstico
→ findings candidatos
→ reporte owner-facing
→ preguntas al dueño
→ respuestas del dueño
→ reentry
→ próximo paso
```

Este documento separa:

- lo implementado;
- lo documentado;
- lo conceptual;
- lo bloqueado;
- lo que decide el kernel;
- lo que confirma o aporta el dueño;
- lo que una respuesta del dueño NO puede reemplazar.

## Fuentes leídas

Código leído físicamente:

- `pymia/orchestration/graph.py`
- `pymia/orchestration/conversation_adapter.py`
- `pymia/smartpyme/anamnesis_fsm_integration.py`
- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/smartpyme/owner_answers_composer.py`
- `pymia/smartpyme/owner_answers_capture.py`
- `pymia/smartpyme/owner_action_pipeline.py`

Documentos fuente inmediatos:

- `docs/pymia/PYMIA_AUDIT_LEDGER.md`
- `docs/pymia/PACK_BOUNDARY_CODE_RECONCILIATION.md`
- `docs/adr/ADR-010-conversational-anamnesis-contract.md`
- `docs/adr/ADR-018-owner-facing-report-boundary.md`
- `docs/contratos/evidence-chain-v1.md`
- `docs/contratos/owner-decision-v1.md`

Lecturas bloqueadas por conector:

- `pymia/contracts/owner_questions.py`

Mitigación:

- La traza owner/reentry se reconstruye desde `graph.py`, `core_delivery_bridge.py`, `owner_answers_composer.py`, `owner_answers_capture.py` y `owner_action_pipeline.py`, que sí fueron leídos.

## No autorizaciones

Este documento no autoriza:

- Modificar código.
- Ejecutar tests.
- Crear runtime.
- Crear packs.
- Migrar owner-answer pipeline.
- Cambiar contratos owner.
- Promover respuestas del dueño a evidencia estructurada automática.
- Confirmar findings automáticamente.
- Abrir diagnóstico final sin evidencia suficiente.

---

# 1. Veredicto ejecutivo

`PASS_TRACE_DRAFT`

La traza dueño → sistema → dueño → reentry existe como arquitectura parcialmente implementada y documentalmente coherente.

El tramo más sólido es:

```text
text_message
→ conversation_adapter
→ anamnesis_fsm_integration
→ progressive_context
→ evidence_requests
```

y:

```text
core_delivery_bridge
→ owner_facing_report
→ owner_questions_bundle
→ owner_answer_reentry
→ owner_action_pipeline
→ projected_render_contract
```

La regla crítica está preservada en código:

```text
La respuesta del dueño puede ser considerada,
pero no reemplaza evidencia estructurada faltante.
```

Evidencia de código:

- `core_delivery_bridge.py` define `STRUCTURAL_INPUT_OWNER_MESSAGE`.
- `core_delivery_bridge.py` define `STRUCTURAL_INPUT_OWNER_WARNING`.
- `_apply_missing_input_resolution_trace()` agrega advertencia si la respuesta no resuelve falta estructural.

---

# 2. Trazado atómico de interacción

## 2.1 Tabla principal

| Paso | Actor | Entrada | Código / artefacto | Salida | Estado | Límite |
|---|---|---|---|---|---|---|
| 1 | Dueño | Mensaje crudo | `PymIAEvent(event_type="text_message")` | Evento normalizado | IMPLEMENTED | No diagnostica. |
| 2 | Orquestación | Evento | `normalize_event()` en `graph.py` | `last_user_message`, decision trail | IMPLEMENTED | Sólo registra y normaliza. |
| 3 | Orquestación | Texto | `decide_route()` en `graph.py` | Ruta conversacional o reentry | IMPLEMENTED | Reentry sólo si estado BLOCKED + bundle de preguntas. |
| 4 | Adaptador | Texto + contexto | `adapt_text_message()` | `ConversationAdapterResult` | IMPLEMENTED | Fail-closed si falla FSM. |
| 5 | Anamnesis | Texto + progressive_context | `run_anamnesis_turn()` | reply + contexto actualizado | IMPLEMENTED | No usa Telegram, red, I/O, Excel ni diagnóstico. |
| 6 | FSM / ficha | Perfil PyME | `process_message()` vía integration | `fsm_state`, profile_data, readiness | IMPLEMENTED | Opciones/mapeos tienen deuda pack. |
| 7 | Post ficha | Perfil completo | `_build_post_ficha_routing_projection()` | intake projection + evidence_requests | IMPLEMENTED | Proyección, no diagnóstico. |
| 8 | Sistema | Evidence request | `_build_post_ficha_reply()` | Pedido mínimo de evidencia | IMPLEMENTED | Aclara que no diagnostica ni calcula sin evidencia. |
| 9 | Dueño | Archivo / referencia / texto de evidencia | `post_ficha_evidence_gate` o `document_received` | Evidence path / EvidenceRecord | IMPLEMENTED_PARTIAL | Evidencia debe ser validada. |
| 10 | Orquestación | Evidencia | `execute_static_capability()` | IntakeRecord + EvidenceRecord | IMPLEMENTED | Puede fallar cerrado. |
| 11 | Gate | Intake + evidence | `evaluate_evidence_sufficiency()` | sufficiency_status | IMPLEMENTED | Si falta evidencia, bloquea. |
| 12 | Builder | Excel / evidencia estructurable | `build_structured_evidence_context()` | `StructuredEvidence` + formula_ids | IMPLEMENTED_PARTIAL | Sólo si hay evidencia válida. |
| 13 | Bridge | StructuredEvidence | `build_core_delivery_bridge_payload_from_structured_evidence()` | formula gates + core result | IMPLEMENTED | Ejecuta sólo fórmulas con inputs listos. |
| 14 | Core | Core input | `DiagnosticCoreV1.run()` | `DiagnosticCoreResult` | IMPLEMENTED | Findings son CANDIDATE; no CONFIRMED. |
| 15 | Bridge delivery | Core result | `build_core_audit_delivery_bundle()` | audit result + render contract + owner report + questions | IMPLEMENTED | No agrega findings fuera del core. |
| 16 | Dueño | Reporte + preguntas | `owner_facing_report`, `owner_questions_bundle` | Preguntas accionables | IMPLEMENTED | Traduce, no inventa. |
| 17 | Dueño | Respuesta textual | `_is_owner_answer_reentry_candidate()` + `owner_answer_reentry` | reentry payload | IMPLEMENTED | Sólo si estado BLOCKED y existen preguntas. |
| 18 | Sistema | Reentry payload | `_consume_owner_answer_reentry_if_available()` | bundle proyectado | IMPLEMENTED | Si falla, queda BLOCKED. |
| 19 | Captura | Respuesta estructurada | `capture_owner_answers_from_structured_payload()` | `OwnerAnswersBundle` | IMPLEMENTED | Exige question_id y source_ref. |
| 20 | Pipeline | OwnerAnswersBundle | `build_owner_action_projection_pipeline()` | evaluación + acción + render proyectado | IMPLEMENTED | No convierte automáticamente en evidencia dura. |
| 21 | Bridge | Evaluación de respuesta | `project_owner_answers_into_delivery_bundle()` | owner-facing report proyectado | IMPLEMENTED | Puede seguir bloqueado por evidencia faltante. |
| 22 | Orquestación | Estado proyectado | `project_bridge_result_to_state()` | phase / delivery_summary / output_refs | IMPLEMENTED | Entrega sólo si status permite. |

---

# 3. Dinámica conversacional inicial

## 3.1 Entrada del dueño

El dueño entra con un `text_message`.

Código:

- `graph.py::normalize_event()` guarda `last_user_message`.
- `graph.py::decide_route()` decide si el texto es conversación normal o reentry de respuesta owner.

Regla:

```text
Un mensaje inicial del dueño no dispara diagnóstico.
```

Sólo habilita:

- anamnesis;
- ficha;
- extracción de contexto;
- pedido posterior de evidencia.

## 3.2 Adapter conversacional

Código:

- `conversation_adapter.py::adapt_text_message()`

Función:

```text
text_message + tenant_id + user_id + progressive_context
→ run_anamnesis_turn()
→ reply_text + updated_progressive_context + phase_hint
```

Estados devueltos:

```text
CONVERSATIONAL
NEEDS_EVIDENCE
BLOCKED
```

Límite:

```text
Si algo falla, el adapter no inventa diagnóstico.
Devuelve pedido de reformulación o contexto operativo.
```

## 3.3 Anamnesis integration

Código:

- `anamnesis_fsm_integration.py`

El propio módulo declara que:

```text
NO usa Telegram.
NO usa red.
NO usa I/O.
NO ejecuta microservicios.
NO lee Excel.
NO diagnostica.
```

Función real:

```text
Recibe mensaje + contexto previo.
Reconstruye FSM.
Ejecuta process_message().
Serializa progressive_context.
```

---

# 4. Ficha, anamnesis y pedido de evidencia

## 4.1 Perfil completo

Cuando la ficha inicial queda completa, `run_anamnesis_turn()` evalúa:

```text
_is_initial_profile_complete(new_state)
```

Si está completa y no se está manejando evidencia, construye:

```text
post_ficha_routing
```

Código:

- `_build_post_ficha_routing_projection()`

Salida:

- `intake_id`
- `intake_state`
- `suggested_next_state`
- `candidate_symptoms`
- `evidence_requests`
- `hypotheses`

## 4.2 Pedido owner-facing de evidencia

Código:

- `_build_post_ficha_reply()`

Mensaje de sistema:

```text
Ya tengo la ficha inicial.
Para avanzar sin adivinar necesito esta evidencia mínima.
```

También declara:

```text
Todavía no voy a diagnosticar ni calcular rentabilidad hasta tener evidencia suficiente.
```

Regla preservada:

```text
Ficha completa ≠ diagnóstico habilitado.
Ficha completa → evidencia mínima requerida.
```

---

# 5. Evidencia y suficiencia

## 5.1 Evidencia recibida

En ruta `document_received`, `execute_static_capability()` crea:

- IntakeRecord
- EvidenceRecord

Código:

- `graph.py::execute_static_capability()`

Regla:

```text
La evidencia queda registrada antes de análisis.
```

## 5.2 Suficiencia

Código:

- `evaluate_evidence_sufficiency()` llamado desde `execute_static_capability()`.

Salida al estado:

```text
new_state.sufficiency_status = sufficiency.status
```

Regla:

```text
Si no hay suficiencia, no hay ejecución diagnóstica entregable.
```

## 5.3 Evidencia estructurada

Código:

- `_populate_progressive_context_with_structured_evidence_if_available()`

Función:

```text
latest_evidence_path
→ build_structured_evidence_context()
→ progressive_context[structured_evidence]
→ progressive_context[formula_ids]
```

Fail-closed:

```text
Si falla ingestion, registra decisión y preserva legacy flow.
```

---

# 6. Core diagnóstico y hallazgos candidatos

## 6.1 Bridge hacia DiagnosticCore

Código:

- `_produce_core_delivery_bridge_payload_if_available()`
- `build_core_delivery_bridge_payload_from_structured_evidence()`

Condiciones:

- `structured_evidence` debe existir.
- `formula_ids` debe existir y no estar vacío.

## 6.2 Gates de fórmula y evidencia

Código:

- `build_formula_input_gate_results_from_structured_evidence()`
- `build_evidence_gate_decisions_from_formula_input_results()`

Regla:

```text
Sólo pasan a ejecución las fórmulas con inputs READY.
```

## 6.3 Core

Código:

- `DiagnosticCoreV1().run(core_input)`

Si no hay fórmulas ejecutables:

```text
_empty_core_result(... status=INSUFFICIENT ...)
```

Regla:

```text
La ausencia de evidencia produce resultado insuficiente, no inferencia.
```

## 6.4 Findings

Los findings nacen en el core y luego se materializan en el bridge.

Regla preservada desde auditorías previas:

```text
Finding = CANDIDATE salvo confirmación externa explícita.
```

Este documento no certifica confirmación automática de findings.

---

# 7. Owner-facing delivery

## 7.1 Operational audit result

Código:

- `build_scn_operational_audit_result_from_core()`

Produce:

- `status`
- `findings`
- `evidence_used`
- `missing_evidence`
- `forbidden_inferences`
- `allowed_rendering`
- `audit_trail_ref`

Reglas prohibidas explícitas:

```text
No inventar evidencia ni variables faltantes.
No agregar findings fuera de DiagnosticCoreResult.
No diagnosticar más allá de los estados ya computados.
No generar narrativa owner-facing en esa capa.
```

## 7.2 Render contract y preguntas

Código:

- `build_render_contract_from_operational_audit_result()`
- `build_owner_questions_bundle()`

Salida:

- `render_contract.json`
- `owner_questions_bundle.json`
- `delivery_summary.md`
- `owner_facing_report.json`

Regla:

```text
Si el resultado está pending_data o blocked, las preguntas al dueño se derivan de missing_evidence / next_questions.
```

## 7.3 Reporte al dueño

Código:

- `build_owner_facing_report()`

Rol:

```text
Traducir un resultado controlado a forma comprensible para el dueño.
```

Límite:

```text
No agrega diagnóstico nuevo fuera del audit/core/render contract.
```

---

# 8. Reentry de respuestas del dueño

## 8.1 Cuándo se acepta reentry

Código:

- `_is_owner_answer_reentry_candidate()`

Condiciones:

```text
event.event_type == text_message
state.phase == BLOCKED
core_delivery_bridge_payload existe en progressive_context
hay output_ref terminado en owner_questions_bundle.json
```

Regla:

```text
No todo texto del dueño es reentry.
Sólo lo es si el sistema estaba bloqueado y había preguntas contractuales pendientes.
```

## 8.2 Construcción del payload de reentry

Código:

- `decide_route()`

Crea:

```text
progressive_context[owner_answer_reentry] = {
  answer_text,
  source_ref: graph://owner_answer_reentry/<conversation_id>
}
```

Estado:

```text
phase = BLOCKED
```

Regla:

```text
La respuesta entra como dato de reentry, no como evidencia estructurada automática.
```

## 8.3 Consumo del reentry

Código:

- `_consume_owner_answer_reentry_if_available()`

Función:

1. Reconstruye bundle previo.
2. Resuelve `question_id` desde `pending_question`.
3. Verifica `answer_text` no vacío.
4. Verifica `source_ref`.
5. Proyecta respuesta sobre delivery bundle.
6. Reescribe artefactos JSON/summary.
7. Proyecta estado.

Fail-closed:

```text
Si falla, phase = BLOCKED.
Registra error y decisión.
```

---

# 9. Captura y evaluación de respuestas del dueño

## 9.1 Captura

Código:

- `owner_answers_capture.py::capture_owner_answers_from_structured_payload()`

Reglas:

- `source_ref` obligatorio y no vacío.
- `question_id` obligatorio.
- `question_id` debe existir en `questions_bundle`.
- Si `question_text` viene en payload, debe coincidir con la pregunta contractual.
- Debe existir `answer_text` o `structured_answer`.

Salida:

```text
OwnerAnswersBundle
```

Regla:

```text
La respuesta del dueño queda trazada contra una pregunta contractual.
```

## 9.2 Composición a acciones

Código:

- `owner_answers_composer.py::compose_owner_answers_to_actions()`

Pipeline:

```text
capture_owner_answers_from_structured_payload()
→ build_owner_action_projection_pipeline()
```

## 9.3 Pipeline owner action

Código:

- `owner_action_pipeline.py::build_owner_action_projection_pipeline()`

Secuencia:

```text
_validate_answer_question_alignment()
→ evaluate_owner_answers()
→ decide_owner_next_action()
→ resolve_owner_next_action_targets()
→ project_resolved_owner_actions_to_render_contract()
```

Regla:

```text
La respuesta se evalúa y proyecta como próximo paso, no como verdad diagnóstica automática.
```

---

# 10. Respuesta del dueño vs evidencia dura

## 10.1 Regla crítica implementada

Código:

- `core_delivery_bridge.py`

Constantes:

```text
STILL_BLOCKED_REQUIRES_STRUCTURED_EVIDENCE
STRUCTURAL_INPUT_OWNER_MESSAGE
STRUCTURAL_INPUT_OWNER_WARNING
```

Mensaje estructural:

```text
Tu respuesta fue considerada, pero todavía falta evidencia o dato estructurado para resolver este punto.
```

Advertencia:

```text
la respuesta del dueño fue considerada, pero no reemplaza evidencia estructurada faltante.
```

## 10.2 Aplicación

Código:

- `_apply_missing_input_resolution_trace()`

Si una evaluación mantiene:

```text
missing_input_resolution_status == still_blocked_requires_structured_evidence
```

entonces agrega:

- próximo paso explicativo;
- advertencia trazable;
- persistencia de bloqueo.

## 10.3 Conclusión

```text
Respuesta del dueño ≠ evidencia dura automática.
```

Puede:

- aclarar;
- confirmar sentido;
- responder una pregunta;
- orientar una acción;
- ayudar a resolver ambigüedad;
- activar reentry;
- proyectar próximo paso.

No puede por sí sola:

- crear EvidenceRecord estructurado;
- completar variable faltante sin dato verificable;
- confirmar finding;
- cerrar diagnóstico;
- reemplazar Excel/documento/extracto/campo faltante;
- saltar evidence sufficiency.

---

# 11. Qué decide cada parte

## 11.1 Dueño

El dueño puede:

- iniciar relato;
- aportar contexto de negocio;
- completar ficha;
- confirmar o corregir sentido;
- aportar evidencia;
- responder preguntas;
- decidir próximos pasos;
- aclarar ambigüedad.

El dueño no debe:

- ser tratado como evidencia estructurada automática;
- confirmar hallazgos computados sin evidencia;
- reemplazar los gates técnicos;
- convertir hipótesis en diagnóstico por opinión sola.

## 11.2 Kernel / sistema

El kernel puede:

- normalizar eventos;
- mantener estado;
- pedir evidencia;
- validar suficiencia;
- bloquear;
- ejecutar core si hay inputs;
- generar findings candidatos;
- renderizar owner-facing report;
- capturar respuestas owner;
- proyectar próximo paso.

El kernel no debe:

- inventar evidencia;
- diagnosticar sin suficiencia;
- confirmar findings automáticamente;
- cargar conocimiento de dominio nuevo sin pack;
- convertir memoria o relato en prueba computable sin contrato.

## 11.3 IA / capa conversacional

La IA puede:

- reformular;
- preguntar;
- explicar bloqueo;
- ordenar próximos pasos;
- traducir para dueño.

La IA no debe:

- agregar findings;
- completar variables faltantes;
- saltar evidencia;
- prometer pronóstico;
- decidir por el dueño;
- cambiar kernel.

---

# 12. Estados atómicos de la interacción

| Estado | Significado | Qué puede pasar | Qué no puede pasar |
|---|---|---|---|
| `NEW` | Conversación inicial | Anamnesis / ficha | Diagnóstico |
| `WAITING_FOR_EVIDENCE` | Se necesita evidencia | Pedir archivo / dato | Calcular sin datos |
| `EVIDENCE_RECEIVED` | Evidencia recibida | Crear Intake/EvidenceRecord | Confirmar patología |
| `READY_TO_EXECUTE` | Hay evidencia candidata | Evaluar sufficiency/readiness | Saltar gates |
| `BLOCKED` | Falta evidencia/dato/condición | Preguntar al dueño / reentry | Entregar diagnóstico final |
| `DELIVERED` | Salida entregable | Reporte controlado | Agregar claims no computados |
| `FAILED` | Error controlado | Informar error | Inventar respuesta |

---

# 13. Lo implementado vs lo pendiente

## 13.1 Implementado

| Capacidad | Evidencia |
|---|---|
| Entrada por `text_message` | `graph.py` |
| Adapter a anamnesis | `conversation_adapter.py` |
| Anamnesis offline serializable | `anamnesis_fsm_integration.py` |
| Post ficha routing projection | `anamnesis_fsm_integration.py` |
| Pedido de evidencia mínimo | `_build_post_ficha_reply()` |
| Intake/EvidenceRecord en documento recibido | `graph.py` |
| Suficiencia de evidencia | `graph.py` llama `evaluate_evidence_sufficiency()` |
| StructuredEvidence context | `_populate_progressive_context_with_structured_evidence_if_available()` |
| Bridge a DiagnosticCore | `core_delivery_bridge.py` |
| Owner-facing report | `core_delivery_bridge.py` + `owner_facing_report.py` |
| Owner questions bundle | `core_delivery_bridge.py` |
| Owner answer reentry | `graph.py` |
| Owner answer capture | `owner_answers_capture.py` |
| Owner action pipeline | `owner_action_pipeline.py` |
| Protección respuesta owner ≠ evidencia estructurada | `core_delivery_bridge.py` |

## 13.2 Pendiente o no certificado aquí

| Capacidad | Estado |
|---|---|
| Contratos owner leídos directamente | Parcial; un archivo fue bloqueado por conector |
| Tests de owner reentry ejecutados | No ejecutados |
| Runtime productivo | No abierto |
| Telegram live | No abierto |
| Pack System runtime | No implementado |
| Pronóstico | No implementado |
| Confirmación automática de findings | No autorizada |

---

# 14. Riesgos de deriva

| Riesgo | Severidad | Control |
|---|---|---|
| Tratar respuesta owner como evidencia dura | Alta | Mantener advertencia estructural y evidence gate. |
| Diagnosticar al completar ficha | Alta | Ficha completa sólo habilita pedido de evidencia. |
| Reentry fuera de preguntas contractuales | Alta | Reentry sólo si BLOCKED + owner_questions_bundle. |
| Owner-facing report agrega claims | Alta | Render contract y audit result limitan salida. |
| Core inventa con inputs faltantes | Alta | Formula gates + empty core result insufficient. |
| IA decide por dueño | Media | OwnerDecision contract + pipeline de next action. |
| Anamnesis hardcodeada se confunde con pack | Media | PACK_BOUNDARY_CODE_RECONCILIATION. |

---

# 15. Relación con diagnóstico / pronóstico / intervención

Este documento certifica la traza de intervención del dueño.

No certifica pronóstico.

Para la próxima auditoría:

```text
DIAGNOSIS_PROGNOSIS_OWNER_INTERVENTION_AUDIT.md
```

se debe usar esta traza como base para separar:

```text
diagnóstico real
pronóstico no implementado
pronóstico posible si...
intervención owner como confirmación/sentido/decisión
respuesta owner como input trazable pero no evidencia dura automática
```

---

# 16. Síntesis mínima

```text
El dueño inicia, aclara, confirma, aporta evidencia y responde preguntas.
PymIA registra, bloquea, estructura, calcula si puede, pregunta si falta y reingresa respuestas.
La respuesta del dueño orienta, pero no reemplaza evidencia estructurada.
```

---

# 17. Veredicto

`PASS_TRACE_DRAFT`

La traza atómica queda registrada.

Próximo frente:

```text
DIAGNOSIS_PROGNOSIS_OWNER_INTERVENTION_AUDIT.md
```
