# OWNER_ANSWER_TO_MISSING_INPUTS_RECONCILIATION_CHECKPOINT

Fecha: 2026-06-10
Estado: PARTIAL
Clasificacion: SIN_CODIGO
Origen: `OWNER_ANSWER_TO_MISSING_INPUTS_RECONCILIATION_TASKSPEC.md`

## VEREDICTO

```text
PARTIAL
```

La auditoria confirma que la reentrada owner-answer funciona y preserva trazabilidad basica, pero no existe todavia una clasificacion explicita de missing inputs ni estados de resolucion por faltante.

No se aplica patch en este frente porque los faltantes generados actualmente por el flujo core/bridge son faltantes estructurales derivados de variables, gates y evidencia. Una respuesta narrativa del dueno no debe resolverlos como evidencia dura.

## ARCHIVOS LEIDOS

- `docs/pymia/OWNER_ANSWER_TO_MISSING_INPUTS_RECONCILIATION_TASKSPEC.md`
- `docs/pymia/SIMULATED_PILOT_FRICTION_RECONCILIATION.md`
- `docs/pymia/ASSISTED_SIMULATED_PILOT_001_CHECKPOINT.md`
- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/orchestration/graph.py`
- `pymia/smartpyme/owner_answers_capture.py`
- `pymia/smartpyme/owner_answers_evaluator.py`
- `pymia/smartpyme/owner_action_pipeline.py`
- `pymia/smartpyme/owner_actions_decider.py`
- `pymia/smartpyme/owner_actions_projector.py`
- `pymia/smartpyme/owner_questions_builder.py`
- `pymia/contracts/owner_questions.py`
- `pymia/contracts/owner_answers.py`
- `pymia/contracts/owner_evaluation.py`
- `pymia/contracts/owner_actions.py`
- `tests/smartpyme/test_core_delivery_bridge_reentry.py`
- `tests/orchestration/test_graph.py`

## EVIDENCIA OBSERVADA

### 1. Donde se consumen las respuestas del dueno

La reentrada se consume en:

```text
pymia/orchestration/graph.py
```

Ruta observada:

```text
text_message en estado BLOCKED
-> decide_route(...)
-> progressive_context["owner_answer_reentry"]
-> execute_static_capability(...)
-> _consume_owner_answer_reentry_if_available(...)
-> project_owner_answers_into_delivery_bundle(...)
```

El bridge consume la respuesta en:

```text
pymia/audit_result/core_delivery_bridge.py
```

mediante:

```text
compose_owner_answers_to_actions(...)
```

### 2. Si la respuesta se adjunta o resuelve faltantes

Actualmente la respuesta:

- se captura como `OwnerAnswer`;
- se evalua como `OwnerAnswerEvaluation`;
- produce una `OwnerNextAction`;
- se proyecta sobre `render_contract`;
- se refleja en `owner_facing_report`.

Pero no modifica:

- `operational_audit_result["missing_evidence"]`;
- `DiagnosticCoreResult`;
- formula gates;
- evidencia dura;
- findings.

Por lo tanto, hoy la respuesta no resuelve missing inputs estructurales. Queda como declaracion o como motivo para pedir aclaracion/rechazo.

### 3. Clasificacion explicita de missing inputs

No existe una clasificacion explicita vigente como:

```text
STRUCTURAL_INPUT
OWNER_SEMANTIC_CLARIFICATION
MIXED
```

Tampoco existen estados persistidos por faltante como:

```text
resolved_by_owner_answer
still_blocked_requires_structured_evidence
partially_resolved_still_blocked
not_applicable_to_missing_input
```

### 4. Diferencia estructural vs semantica

La diferencia existe metodologicamente en el TaskSpec, pero no esta formalizada en el runtime contractual actual.

Los faltantes generados por `core_delivery_bridge.py` nacen de:

- `FormulaInputGateResult.missing_variables`;
- `EvidenceGateDecision.missing_variables`;
- `DiagnosticCoreResult.missing_evidence`.

Eso los clasifica, en la practica actual, como:

```text
STRUCTURAL_INPUT
```

### 5. Respuesta narrativa y resolved_by_owner_answer

Hoy una respuesta narrativa no puede pasar un faltante a:

```text
resolved_by_owner_answer
```

El flujo puede aceptar respuestas como declaracion del dueno en el evaluador minimo, pero no hay puente desde esa aceptacion hacia resolucion de un missing input especifico.

Ademas, el contrato vigente de preguntas/respuestas no modela todavia `operational_meaning` como tipo ordinario de `OwnerQuestion.expected_answer_type` ni de `OwnerAnswer.answer_type` en la ruta normal.

### 6. Si el caso sigue BLOCKED, explicacion visible

El caso sigue `BLOCKED` cuando el `DeliveryPackage.status` original es `BLOCKED`.

El reporte visible conserva pregunta/bloqueo owner-facing, pero aun no distingue con precision:

- "falta dato estructural";
- "falta aclaracion de sentido";
- "respuesta parcialmente util pero insuficiente".

### 7. Trazabilidad sin inventar evidencia

La trazabilidad se preserva en:

- `question_id`;
- `question_text`;
- `source_ref`;
- `missing_key` en `OwnerQuestion`;
- `OwnerAnswer.source_ref`;
- `OwnerAnswerEvaluation.source_answer_id`;
- `OwnerAnswerEvaluation.linked_question_id`;
- `OwnerNextAction.target_questions`;
- `OwnerResolvedNextAction.resolved_questions`.

No se inventa evidencia. La respuesta del dueno no se promueve a evidencia dura ni reejecuta DiagnosticCore.

## CLASIFICACION DE FALTANTES

Clasificacion para el estado actual:

```text
missing_evidence derivado de formula gates/core -> STRUCTURAL_INPUT
blocked_message generico -> MIXED conceptual, no clasificado en runtime
next_questions heredadas de render_contract -> depende del origen; hoy no clasificado
```

Decision de auditoria:

```text
Los faltantes actuales del flujo core/bridge deben tratarse como STRUCTURAL_INPUT.
```

Una respuesta narrativa puede aportar contexto, pero no debe desbloquear esos faltantes sin dato estructurado o evidencia verificable.

## TESTS EJECUTADOS

```bash
python -m pytest tests/smartpyme/test_core_delivery_bridge_reentry.py tests/smartpyme/test_owner_answers_capture.py tests/smartpyme/test_owner_answers_evaluator.py tests/smartpyme/test_owner_action_pipeline.py tests/smartpyme/test_owner_questions_builder.py -q --basetemp .tmp_pytest_owner_answer_reconciliation
```

Resultado:

```text
42 passed, 1 warning
```

```bash
python -m pytest tests/orchestration/test_graph.py::test_graph_blocked_owner_answer_reentry_projects_bridge_without_rerunning_core tests/orchestration/test_graph.py::test_graph_blocked_owner_answer_reentry_fail_closed_without_question_mapping -q --basetemp .tmp_pytest_owner_answer_reconciliation_graph
```

Resultado:

```text
2 passed, 1 warning
```

Warnings:

```text
PytestCacheWarning
```

No bloqueante.

## DECISION

```text
patch necesario: NO en este frente
```

Motivo:

- no hay evidencia de que un faltante semantico generado por el flujo real este quedando bloqueado indebidamente;
- los faltantes reales observados son estructurales;
- resolverlos con texto narrativo inventaria evidencia o saltaria gates.

## DEUDA REAL IDENTIFICADA

Queda deuda para un frente posterior si se quiere permitir resolucion semantica real:

- agregar clasificacion explicita de missing input;
- distinguir `STRUCTURAL_INPUT`, `OWNER_SEMANTIC_CLARIFICATION` y `MIXED`;
- persistir estado por pregunta/faltante;
- permitir `resolved_by_owner_answer` solo para aclaraciones semanticas;
- explicar bloqueo residual cuando una respuesta es util pero insuficiente;
- mantener prohibicion de promover declaraciones del dueno a evidencia dura.

## NO PUSH

Confirmado.
