# Owner Conversation to Initial Diagnosis ModuleContract

## Estado

**CANDIDATO_OPERATIVO**

**Fecha:** 2026-06-13

## Propósito

Definir la frontera modular futura para transformar una conversación inicial del dueño en un diagnóstico inicial candidato P1, sin implementar runtime ni modificar código todavía.

## Módulo futuro

```text
pymia/smartpyme/owner_conversation_initial_diagnosis.py
```

## Responsabilidad única

El módulo futuro deberá recibir un mensaje inicial del dueño y contexto disponible, producir una salida estructurada de estado conversacional inicial y decidir si corresponde:

- pedir aclaración,
- pedir evidencia,
- bloquear accionablemente,
- emitir diagnóstico inicial candidato P1,
- dejar reentry pendiente.

## Inputs permitidos

```text
owner_message: str
tenant_id: str
cliente_id: str | None
case_id: str | None
progressive_context: dict | None
attachments_summary: list | None
```

## Outputs permitidos

```text
OwnerConversationInitialDiagnosisResult
```

Campos mínimos futuros:

```text
status
case_context
semantic_hypothesis
missing_context
missing_evidence
owner_questions
initial_diagnosis_candidate
blocked_reason
next_required_owner_action
source_refs
warnings
```

## Estados permitidos

```text
OWNER_MESSAGE_RECEIVED
CASE_CONTEXT_OPENED
SEMANTIC_HYPOTHESIS_CANDIDATE
NEEDS_OWNER_CLARIFICATION
NEEDS_EVIDENCE
BLOCKED_ACTIONABLE
INITIAL_DIAGNOSIS_CANDIDATE
OWNER_REENTRY_PENDING
```

## Imports permitidos futuros

Sólo contratos y módulos puros:

```text
pymia.contracts.*
pymia.smartpyme.owner_questions_builder
pymia.smartpyme.owner_semantic_gate_builder
pymia.smartpyme.anamnesis_fsm_integration
```

## Imports prohibidos

```text
telegram
fastapi
hermes
requests
openai
llm client
pandas/polars runtime pesado
pymia.diagnostic_core.core
pymia.services.formula_engine_service
filesystem writes
network IO
```

## Reglas de frontera

1. No ejecuta DiagnosticCoreV1.
2. No calcula fórmulas.
3. No produce findings confirmados.
4. No convierte relato del dueño en evidencia dura.
5. No crea DecisionRecord automático.
6. No abre canal visible externo.
7. No modifica progressive_context por side effect.
8. No ejecuta acciones.
9. No autoriza pronóstico.
10. No carga packs.

## Relación con P1

El módulo futuro puede producir `initial_diagnosis_candidate` sólo como artefacto pre-core P1.

Ese output no reemplaza:

- `DiagnosticCoreResult`,
- `OperationalAuditResult`,
- `OwnerFacingReport`,
- `RenderContract`,
- `DeliveryPackage`.

## Relación con evidencia

Si faltan datos materiales, la salida debe ser:

```text
NEEDS_EVIDENCE
```

o:

```text
BLOCKED_ACTIONABLE
```

Nunca debe completar variables faltantes por inferencia libre.

## Relación con dueño

El módulo puede formular preguntas al dueño, pero debe distinguir:

```text
aclaración semántica
aporte de evidencia
confirmación de comprensión
autorización de acción
```

No debe tratarlas como equivalentes.

## Fail-closed

Debe bloquear si:

- falta `owner_message`,
- falta `tenant_id`,
- no puede inferir contexto mínimo,
- falta período para análisis,
- falta evidencia material,
- el relato es contradictorio,
- la hipótesis excede lo dicho por el dueño,
- la salida podría confundirse con diagnóstico final.

## Tests futuros mínimos

Cuando se autorice implementación:

```text
test_initial_owner_message_opens_case_context
test_ambiguous_message_requests_clarification
test_missing_evidence_blocks_actionably
test_candidate_diagnosis_is_pre_core_only
test_owner_reply_not_promoted_to_decision_record
test_no_diagnostic_core_imports
```

## Criterios de aceptación

- Frontera pura.
- Sin IO.
- Sin runtime.
- Sin core.
- Sin fórmulas.
- Sin pronóstico.
- Sin delivery.
- Salida trazable.
- Bloqueo explícito ante insuficiencia.

## Veredicto

```text
OWNER_CONVERSATION_TO_INITIAL_DIAGNOSIS_MODULECONTRACT_DEFINED
```
