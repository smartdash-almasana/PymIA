# SERVICE_1_COLUMN_CONFIRMATION_APPLIER_V1

## Estado

```text
IMPLEMENTED
```

## Objetivo

Aplicar una respuesta clasificada del dueño sobre una `ColumnConfirmationMatrix` en memoria.

Este slice conecta:

```text
Service1ColumnConfirmationClassificationV1
+ ColumnConfirmationMatrix
→ Service1ColumnConfirmationApplierResultV1
```

## Regla canónica

```text
PymIA interpreta cada columna.
PymIA se lo explica al dueño.
El dueño responde SÍ / NO / TU_RESPUESTA.
El classifier produce OwnerColumnConfirmationAnswer.
El applier aplica esa respuesta clasificada sobre la matriz en memoria.
```

## Archivo runtime

```text
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_applier_v1.py
```

## Test

```text
PymIA-Live/tests/smartpyme/test_service_1_column_confirmation_applier_v1.py
```

## Función pública

```python
apply_service_1_column_confirmation_v1(...)
```

## Input contract

```text
classification: Service1ColumnConfirmationClassificationV1
matrix: ColumnConfirmationMatrix
case_id: optional str
tenant_id: optional str
intake_id: optional str
variables_to_track: optional iterable[str]
metadata: optional dict
```

La matriz debe ser provista por el caller. Este módulo no carga ni persiste matrices.

## Output contract

```text
Service1ColumnConfirmationApplierResultV1
```

Incluye:

```text
schema_version
service_name
case_id
tenant_id
intake_id
target_ref
parsed_target_ref
applied_entry_snapshot
matrix_status_before
matrix_status_after
computation_unlocked
variables_affected
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
owner_answer_validation_status
created_at
metadata
```

## Regla de aplicación

El applier hace exactamente esto:

```text
1. Captura matrix.status() antes.
2. Captura can_compute_variable() antes para variables rastreadas.
3. Llama matrix.apply_owner_answer(classification.owner_column_confirmation_answer).
4. Captura snapshot de la entrada aplicada.
5. Captura matrix.status() después.
6. Captura can_compute_variable() después.
7. Calcula variables_affected.
8. Calcula computation_unlocked.
9. Devuelve wrapper de resultado.
```

## Semántica esperada

```text
CONFIRMED_COMPUTATIONAL
→ confirmation_status=CONFIRMED
→ puede desbloquear variables si can_compute_variable pasa de False a True

CONFIRMED_INFORMATIONAL
→ confirmation_status=CONFIRMED
→ no desbloquea cálculo numérico

CONFIRMED_NOT_RELEVANT
→ confirmation_status=IGNORED_NOT_RELEVANT
→ no recalcula

OWNER_REJECTED_MAPPING
→ confirmation_status=BLOCKED_AMBIGUOUS
→ no desbloquea cálculo

INSUFFICIENT_ANSWER
→ confirmation_status=PENDING_OWNER_CONFIRMATION
→ no desbloquea cálculo
```

## Seguridad preservada

Este slice fija siempre:

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
owner_answer_validation_status=DECLARED_NOT_VALIDATED
```

## Exclusiones explícitas

Este slice no hace:

```text
NO storage
NO persistence
NO rendering
NO bridge
NO vertical_pipeline
NO recalculation
NO reexecution
NO evidence validation
NO LLM
NO web
```

## Tests cubiertos

```text
- aplica confirmación computacional y detecta unlock
- aplica confirmación informacional sin unlock
- aplica no relevante como IGNORED_NOT_RELEVANT
- aplica NO como BLOCKED_AMBIGUOUS
- aplica TU_RESPUESTA como BLOCKED_AMBIGUOUS sin adivinar rol
- respuesta insuficiente queda pendiente
- captura status antes/después
- calcula variables_affected
- preserva flags de seguridad
- no genera efectos de filesystem
- serializa snapshot y metadata
```

## Próximo frente permitido

```text
SERVICE_1_COLUMN_CONFIRMATION_CASE_PATCH_V1
```

Ese próximo frente podrá envolver el resultado del applier como patch de caso, todavía sin persistir automáticamente ni recalcular.
