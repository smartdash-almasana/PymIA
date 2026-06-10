# Semantic Confirmation Reentry Block Closure

## Estado

`CLOSED`

## Frente

`SEMANTIC_CONFIRMATION_REENTRY_BLOCK`

## Objetivo cerrado

Cerrar la cadena contractual mínima para que una confirmación semántica explícita del dueño pueda ser transportada, proyectada y expuesta sin contaminar evidencia, diagnóstico, findings ni runtime.

## Cadena consolidada

```text
OwnerSemanticConfirmationGate pendiente
→ OwnerQuestion.metadata con expects_semantic_confirmation=True
→ dueño confirma, rechaza o corrige
→ OwnerSemanticConfirmationGate terminal
→ OwnerAnswer.metadata con semantic_confirmation_status explícito
→ owner answer capture preserva metadata
→ bridge reentry consume metadata explícita
→ owner_facing_report proyecta BLOCKED_ACTIONABLE si corresponde
→ graph persiste owner_facing_report.json
→ graph actualiza pending_question desde owner_facing_report proyectado
```

## Commits incluidos

- `e0f0854 feat(pymia): project confirmed semantic requests owner-facing`
- `6b87259 test(pymia): certify assisted simulated pilot 002 blocked actionable`
- `f220cc5 test(pymia): validate semantic confirmation reentry projection`
- `0d0db3f fix(pymia): core_delivery_bridge_reentry variable scope`
- `9884722 test(pymia): cover semantic confirmation bridge reentry`
- `dc80fc7 test(pymia): cover graph propagation of projected owner report`
- `1dfa0f7 chore(repo): ignore pytest temp artifacts`
- `6e0ab72 test(pymia): preserve semantic confirmation metadata in owner answers`
- `67a5e6b test(pymia): mark semantic confirmation source questions`
- `255d613 feat(pymia): project semantic confirmation gate metadata`
- `59d284f docs(pymia): document semantic confirmation gate metadata projection`
- `9c15ccd docs(pymia): index semantic confirmation metadata checkpoint`

## Archivos contractuales y funcionales relevantes

- `pymia/contracts/owner_semantic_confirmation.py`
- `pymia/smartpyme/owner_semantic_confirmation_reentry_projection.py`
- `pymia/smartpyme/owner_confirmed_semantic_request_flow.py`
- `pymia/smartpyme/owner_confirmed_semantic_request_projection.py`
- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/orchestration/graph.py`

## Tests relevantes

- `tests/smartpyme/test_owner_semantic_confirmation_gate.py`
- `tests/smartpyme/test_owner_questions_builder.py`
- `tests/smartpyme/test_owner_answers_capture.py`
- `tests/smartpyme/test_owner_semantic_confirmation_reentry_projection.py`
- `tests/smartpyme/test_owner_confirmed_semantic_request_flow.py`
- `tests/smartpyme/test_owner_confirmed_semantic_request_projection.py`
- `tests/smartpyme/test_core_delivery_bridge_reentry.py`
- `tests/orchestration/test_graph.py`
- `tests/smartpyme/test_assisted_simulated_pilot_002_bis_blocked_actionable.py`

## Límites preservados

Este bloque no autoriza ni implementa:

- promoción de narrativa del dueño a evidencia estructural;
- generación de findings desde semántica confirmada;
- diagnóstico desde confirmación semántica;
- inferencia de confirmación desde texto libre;
- cambios productivos en DiagnosticCore;
- cambios productivos en graph;
- runtime Hermes;
- Telegram productivo;
- PDF productivo;
- ERP;
- ejecución de fórmulas nuevas.

## Frontera arquitectónica resultante

- `OwnerSemanticConfirmationGate` define el contrato soberano de confirmación.
- `OwnerQuestion.metadata` puede declarar que espera confirmación semántica.
- `OwnerAnswer.metadata` puede transportar un estado explícito de confirmación.
- `bridge` transforma la respuesta confirmada en proyección owner-facing accionable.
- `graph` sólo propaga y persiste el reporte proyectado.
- `core` no se contamina.

## Auditorías realizadas

- Auditoría de Coder sobre fidelidad documental y arquitectónica: `PASS_WITH_GAPS`, decisión `CONSERVAR` para `255d613`.
- `audit_docs_index`: `OK`, `missing_count = 0` tras indexación.
- `check_forbidden_terms`: limpio.

## Gaps pendientes no bloqueantes

- CapabilitySpec específico para gate → metadata.
- ADR o sección ADR que fundamente formalmente la ubicación de la proyección en el contrato.
- ModuleContract opcional para `pymia/contracts/owner_semantic_confirmation.py`.
- Integración futura que genere gates desde conversación real sin inferir desde texto libre.

## Veredicto

`PASS_CLOSED`

El bloque queda cerrado como capacidad contractual y de propagación. Cualquier avance posterior debe abrir un nuevo frente explícito, con autorización separada, especialmente si toca generación real de gates desde conversación, runtime, Telegram o graph productivo.
