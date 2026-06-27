# SERVICE_1_COLUMN_CONFIRMATION_REENTRY_TASKSPEC_V1

## Estado

```text
TASKSPEC_READY
Runtime impact: PLANNED_ONLY
Code impact: NOT_APPLIED
Tests impact: NOT_APPLIED
```

## Propósito

Definir el slice mínimo que, si luego se autoriza implementación, construya un **candidate packet** desde una pregunta proyectada respondida de la familia column confirmation.

El slice existe para cerrar esta transformación y nada más:

```text
Service1ProjectedQuestionV1(answered, eligible)
+ explicit proposed_role / suggested_semantic_role
-> Service1ColumnConfirmationReentryCandidateV1
```

Este TaskSpec no autoriza:

```text
classification
matrix apply
case patch
persistence
recalculation
evidence validation
```

## Cadena metodológica previa

```text
SERVICE_1_COLUMN_CONFIRMATION_REENTRY_AUDIT_V1
→ SERVICE_1_COLUMN_CONFIRMATION_REENTRY_CAPABILITYSPEC_V1
→ SERVICE_1_COLUMN_CONFIRMATION_REENTRY_MODULE_CONTRACT_V1
→ SERVICE_1_COLUMN_CONFIRMATION_REENTRY_TASKSPEC_V1
```

## Tesis

```text
Antes de clasificar una respuesta de reentry,
PymIA debe demostrar que esa respuesta pertenece realmente
a la familia column_confirmation y que todavía sigue siendo
declaración humana no validada.
```

## Slice autorizado

El slice futuro podrá:

- recibir una `Service1ProjectedQuestionV1`;
- validar elegibilidad;
- normalizar `proposed_role` / `suggested_semantic_role`;
- parsear `target_ref`;
- devolver un packet `READY_FOR_CLASSIFIER` o `BLOCKED`.

El slice futuro no podrá:

- llamar al classifier;
- llamar al applier;
- emitir case patch;
- persistir;
- recalcular;
- mutar estado previo;
- promover evidencia.

## Inputs requeridos

| Input | Tipo | Obligatorio | Regla |
|---|---|---:|---|
| `projected_question` | `Service1ProjectedQuestionV1` | sí | Debe venir de `answered_questions[]`. |
| `proposed_role` | `str \| None` | no | Si falta, puede usarse `suggested_semantic_role`. |
| `suggested_semantic_role` | `str \| None` | no | Si falta, puede usarse `proposed_role`. |
| `metadata` | `dict \| None` | no | Sólo passthrough local. |

## Gating obligatorio

La implementación futura debe bloquear si cualquiera de estas condiciones falla:

```text
projected_question.source == column_confirmation_matrix
projected_question.answer_type == confirm_column_role
projected_question.projection_status == ANSWERED
projected_question.latest_raw_owner_answer presente
projected_question.target_ref presente
projected_question.owner_answer_validation_status == DECLARED_NOT_VALIDATED
al menos uno de proposed_role / suggested_semantic_role presente
```

## Output requerido

La implementación futura debe producir:

```text
Service1ColumnConfirmationReentryCandidateV1
```

Campos mínimos:

```text
schema_version
service_name
status
blocked_reason
question_ref
question_source
target_ref
parsed_target_ref
answer_type
raw_owner_answer
proposed_role
owner_answer_validation_status
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
metadata
```

## Estados permitidos

```text
READY_FOR_CLASSIFIER
BLOCKED
```

### Blocked reasons permitidos

```text
QUESTION_SOURCE_UNSUPPORTED
ANSWER_TYPE_UNSUPPORTED
QUESTION_NOT_ANSWERED
RAW_OWNER_ANSWER_MISSING
TARGET_REF_INVALID
ROLE_MISSING
OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED
```

## Archivos permitidos si luego se implementa

```text
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_reentry_candidate_v1.py
PymIA-Live/tests/smartpyme/test_service_1_column_confirmation_reentry_candidate_v1.py
```

## Archivos prohibidos

```text
PymIA-Live/pymia/application/vertical_pipeline.py
PymIA-Live/pymia/smartpyme/storage.py
PymIA-Live/pymia/smartpyme/pipeline_registration.py
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_applier_v1.py
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_case_patch_v1.py
PymIA-Live/pymia/diagnostic_core/**
PymIA-Live/pymia/cli/**
landing/**
docs/**  (salvo este TaskSpec y artefactos metodológicos explícitos)
```

## Acceptance tests requeridos para la futura implementación

La implementación futura deberá cubrir al menos:

1. **happy path**
   - projected question elegible
   - `status=READY_FOR_CLASSIFIER`
   - `proposed_role` resuelto
   - flags de seguridad preservados

2. **source inválido**
   - `status=BLOCKED`
   - `blocked_reason=QUESTION_SOURCE_UNSUPPORTED`

3. **answer_type inválido**
   - `status=BLOCKED`
   - `blocked_reason=ANSWER_TYPE_UNSUPPORTED`

4. **projection_status no ANSWERED**
   - `status=BLOCKED`
   - `blocked_reason=QUESTION_NOT_ANSWERED`

5. **raw owner answer faltante**
   - `status=BLOCKED`
   - `blocked_reason=RAW_OWNER_ANSWER_MISSING`

6. **target_ref inválido**
   - `status=BLOCKED`
   - `blocked_reason=TARGET_REF_INVALID`

7. **role faltante**
   - `status=BLOCKED`
   - `blocked_reason=ROLE_MISSING`

8. **validation status inesperado**
   - `status=BLOCKED`
   - `blocked_reason=OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED`

9. **no side effects**
   - no filesystem IO
   - no imports prohibidos
   - no persistence

## Invariantes no negociables

La implementación futura debe preservar siempre:

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
owner_answer_validation_status=DECLARED_NOT_VALIDATED
```

Y además:

```text
declared owner input != validated evidence
candidate packet != classified answer
candidate packet != matrix mutation
```

## Stop conditions

Detener la implementación futura si aparece cualquiera de estos casos:

- hace falta inferir semantic role desde texto libre;
- hace falta asumir que `question_target_ref == column_confirmation_target_ref` sin prueba;
- hace falta llamar classifier/applier para “hacerlo funcionar”;
- hace falta tocar módulos congelados;
- hace falta promover evidencia o desbloquear cálculo;
- el target real del slice se expande más allá de candidate construction.

## Validación de este TaskSpec

Este artefacto queda PASS si:

- existe como documento independiente;
- preserva el alcance candidate-only;
- define tests futuros mínimos;
- no toca código;
- no contradice audit, CapabilitySpec ni ModuleContract previos.

## Próximo paso correcto

```text
acceptance test design
→ implementation of candidate packet bridge
```

No classifier.  
No applier.  
No patch.  
No persistence.
