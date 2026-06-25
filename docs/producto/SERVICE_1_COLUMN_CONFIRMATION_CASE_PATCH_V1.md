# SERVICE_1_COLUMN_CONFIRMATION_CASE_PATCH_V1

## Estado

```text
IMPLEMENTED
```

## Objetivo

Convertir `Service1ColumnConfirmationApplierResultV1` en un patch declarativo de caso.

```text
ApplierResult
→ CasePatch
```

El patch describe el cambio. No lo persiste, no recalcula y no reejecuta.

## Archivo runtime

```text
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_case_patch_v1.py
```

## Test

```text
PymIA-Live/tests/smartpyme/test_service_1_column_confirmation_case_patch_v1.py
```

## Input contract

```text
applier_result: Service1ColumnConfirmationApplierResultV1
metadata: dict | None
```

No acepta raw owner text, matrix, storage handle ni classification.

## Output contract

```text
Service1ColumnConfirmationCasePatchV1
```

Campos principales:

```text
schema_version
service_name
case_id
tenant_id
intake_id
target_ref
parsed_target_ref
patch_kind
confirmation_status_before
confirmation_status_after
computation_unlocked
variables_affected
applied_entry_snapshot
runtime_authorized
human_review_required
reexecution_authorized
recalculation_authorized
persistence_authorized
owner_answer_validation_status
created_at
metadata
```

## Patch kinds

```text
CONFIRM_COMPUTATIONAL
CONFIRM_INFORMATIONAL
IGNORE_NOT_RELEVANT
BLOCK_REJECTED
KEEP_PENDING
```

## Derivación determinista

```text
CONFIRMED + computation_unlocked=True  -> CONFIRM_COMPUTATIONAL
CONFIRMED + computation_unlocked=False -> CONFIRM_INFORMATIONAL
IGNORED_NOT_RELEVANT                   -> IGNORE_NOT_RELEVANT
BLOCKED_AMBIGUOUS                      -> BLOCK_REJECTED
PENDING_OWNER_CONFIRMATION             -> KEEP_PENDING
```

No introduce heurística nueva.

## Seguridad fija

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
persistence_authorized=False
owner_answer_validation_status=DECLARED_NOT_VALIDATED
```

## Exclusiones

```text
NO re-clasificar
NO re-aplicar matrix
NO persistir
NO recalcular
NO reejecutar
NO vertical_pipeline
NO validar evidencia
NO resolver case_id vacío
NO LLM
NO web
```

## Tests cubiertos

```text
CONFIRM_COMPUTATIONAL
CONFIRM_INFORMATIONAL
IGNORE_NOT_RELEVANT
BLOCK_REJECTED
KEEP_PENDING
passthrough case_id/tenant_id/intake_id/target_ref
flags de seguridad
pureza filesystem
no muta applier_result
to_dict snapshot + metadata
patch_kind 1:1 sin heurística
frozen dataclass
```

## Próximo frente permitido

```text
SERVICE_1_COLUMN_CONFIRMATION_PATCH_LEDGER_V1
```
