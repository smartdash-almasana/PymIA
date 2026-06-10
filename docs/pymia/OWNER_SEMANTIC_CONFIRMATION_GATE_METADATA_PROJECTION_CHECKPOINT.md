# Owner Semantic Confirmation Gate Metadata Projection Checkpoint

## Estado

`ACCEPTED_WITH_GAPS`

## Commit auditado

`255d613`

## Frente

`OWNER_SEMANTIC_CONFIRMATION_GATE_METADATA_PROJECTION`

## Decisión

Se conserva la proyección de metadata dentro de `OwnerSemanticConfirmationGate`.

Métodos aceptados:

- `to_owner_question_metadata()`
- `to_owner_answer_metadata()`

## Justificación arquitectónica

`OwnerSemanticConfirmationGate` es la fuente contractual del estado soberano de confirmación semántica del dueño.

La proyección hacia metadata pertenece al contrato porque:

- Es una lectura pura del propio estado del gate.
- No importa `OwnerQuestion`, `OwnerAnswer`, bridge, graph ni runtime.
- No ejecuta IO.
- No muta estado.
- No interpreta texto libre.
- No introduce dependencias inversas.
- Expone una forma canónica para que consumidores posteriores transporten confirmación explícita sin inventarla.

## Proyección hacia OwnerQuestion.metadata

`to_owner_question_metadata()` representa un gate pendiente que solicita confirmación explícita al dueño.

Debe transportar, como metadata trazable:

- `expects_semantic_confirmation = True`
- `semantic_confirmation_gate_id`
- `semantic_confirmation_target_type`
- `proposed_interpretation`
- `related_missing_keys`
- `related_pathology_candidates`
- `related_formula_candidates`
- `semantic_confirmation_source_ref`

No debe transportar `semantic_confirmation_status`, porque todavía no existe una respuesta terminal del dueño.

## Proyección hacia OwnerAnswer.metadata

`to_owner_answer_metadata()` representa un gate terminal confirmado, rechazado o corregido por el dueño.

Debe transportar, como metadata explícita para reentry:

- `semantic_confirmation_status`
- `semantic_confirmation_gate_id`
- `semantic_confirmation_target_type`
- `proposed_interpretation`
- `owner_response_text`
- `corrected_interpretation`, sólo si aplica
- `related_missing_keys`
- `related_pathology_candidates`
- `related_formula_candidates`
- `semantic_confirmation_source_ref`

Debe fallar si el gate no es terminal.

## Límites contractuales

Esta proyección NO hace:

- No convierte semántica del dueño en evidencia estructural.
- No crea `evidence_candidate`.
- No crea `computed_variables`.
- No genera findings.
- No ejecuta diagnóstico.
- No decide patologías.
- No decide fórmulas.
- No modifica graph.
- No modifica bridge.
- No interpreta texto libre como confirmación.

La confirmación sólo existe si el gate tiene estado explícito:

- `CONFIRMED_BY_OWNER`
- `REJECTED_BY_OWNER`
- `CORRECTED_BY_OWNER`

## Tests de cobertura

Archivo:

- `tests/smartpyme/test_owner_semantic_confirmation_gate.py`

Casos relevantes:

- `test_gate_projects_question_metadata_for_explicit_semantic_confirmation`
- `test_terminal_gate_projects_answer_metadata_for_bridge_reentry`
- `test_corrected_gate_answer_metadata_preserves_correction`
- `test_pending_gate_cannot_project_answer_metadata`

## Relación con la cadena semántica

La cadena aceptada queda:

```text
OwnerSemanticConfirmationGate pendiente
→ OwnerQuestion.metadata con expects_semantic_confirmation=True
→ dueño confirma, rechaza o corrige
→ OwnerSemanticConfirmationGate terminal
→ OwnerAnswer.metadata con semantic_confirmation_status explícito
→ bridge reentry consume metadata
→ owner_facing_report proyecta BLOCKED_ACTIONABLE si corresponde
→ graph persiste y propaga
```

## Gaps pendientes

Quedan pendientes, no bloqueantes para conservar el commit:

- CapabilitySpec específico para la proyección gate → metadata.
- ADR o sección ADR que fundamente por qué la proyección vive en el contrato y no en un mapper externo.
- ModuleContract para `pymia/contracts/owner_semantic_confirmation.py`, si se decide formalizar esta frontera con mayor detalle.

## Veredicto

`PASS_WITH_GAPS`

El commit `255d613` se conserva. La deuda restante es documental, no de código productivo.
