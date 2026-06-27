# SERVICE_1_COLUMN_CONFIRMATION_REENTRY_ACCEPTANCE_TEST_DESIGN_V1

## Estado

```text
ACCEPTANCE_TEST_DESIGN_READY
Runtime impact: NONE
Code impact: NONE
Tests impact: PLANNED_ONLY
```

## Propósito

Definir los tests de aceptación que deben existir antes de implementar el bridge:

```text
Service1ProjectedQuestionV1(answered, eligible)
+ explicit proposed_role / suggested_semantic_role
-> Service1ColumnConfirmationReentryCandidateV1
```

Este documento no autoriza runtime todavía.

Su función es fijar:

- qué escenarios son válidos;
- qué escenarios deben bloquearse;
- qué invariantes no pueden romperse;
- qué cosas NO pertenecen al test porque serían deriva.

## Cadena metodológica

```text
SERVICE_1_COLUMN_CONFIRMATION_REENTRY_AUDIT_V1
→ SERVICE_1_COLUMN_CONFIRMATION_REENTRY_CAPABILITYSPEC_V1
→ SERVICE_1_COLUMN_CONFIRMATION_REENTRY_MODULE_CONTRACT_V1
→ SERVICE_1_COLUMN_CONFIRMATION_REENTRY_TASKSPEC_V1
→ SERVICE_1_COLUMN_CONFIRMATION_REENTRY_ACCEPTANCE_TEST_DESIGN_V1
```

## Archivo de test previsto

```text
PymIA-Live/tests/smartpyme/test_service_1_column_confirmation_reentry_candidate_v1.py
```

## Archivo runtime previsto

```text
PymIA-Live/pymia/smartpyme/service_1_column_confirmation_reentry_candidate_v1.py
```

## Tesis del diseño

```text
El test no debe probar una solución “útil”.
Debe probar una frontera segura.
```

El bridge futuro sólo será correcto si demuestra:

1. que recibe una pregunta proyectada que realmente pertenece a column confirmation;
2. que no clasifica la respuesta;
3. que no aplica nada sobre la matrix;
4. que preserva el estado de input declarado y no validado.

## Fixture mínima requerida

El archivo de tests futuro debe contar como mínimo con una factory o helper para construir:

```text
Service1ProjectedQuestionV1
```

con defaults seguros:

```text
source=column_confirmation_matrix
answer_type=confirm_column_role
projection_status=ANSWERED
target_ref=file:ventas.xlsx:sheet:Ventas:column:MetodoPago
latest_raw_owner_answer=Sí, esa columna indica el medio de pago.
owner_answer_validation_status=DECLARED_NOT_VALIDATED
```

Y además permitir override de:

- `source`
- `answer_type`
- `projection_status`
- `target_ref`
- `latest_raw_owner_answer`
- `owner_answer_validation_status`

## Escenarios obligatorios

### 1. Happy path con `proposed_role`

**Given**
- pregunta proyectada elegible
- `proposed_role="payment_method"`

**When**
- se construye el candidate packet

**Then**
- `status == READY_FOR_CLASSIFIER`
- `blocked_reason is None`
- `question_ref` se preserva
- `target_ref` se preserva
- `parsed_target_ref` expone `file_name`, `sheet_name`, `column_name`
- `raw_owner_answer` se preserva sin transformación semántica
- `proposed_role == "payment_method"`
- `runtime_authorized == False`
- `human_review_required == True`
- `reexecution_authorized == False`
- `recalculation_authorized == False`
- `owner_answer_validation_status == DECLARED_NOT_VALIDATED`

### 2. Happy path con fallback a `suggested_semantic_role`

**Given**
- pregunta proyectada elegible
- `proposed_role is None`
- `suggested_semantic_role="payment_method"`

**Then**
- `status == READY_FOR_CLASSIFIER`
- el role final resuelto es `"payment_method"`
- se preservan todos los flags de seguridad

### 3. Source inválido

**Given**
- `source != column_confirmation_matrix`

**Then**
- `status == BLOCKED`
- `blocked_reason == QUESTION_SOURCE_UNSUPPORTED`

### 4. Answer type inválido

**Given**
- `answer_type != confirm_column_role`

**Then**
- `status == BLOCKED`
- `blocked_reason == ANSWER_TYPE_UNSUPPORTED`

### 5. Projection status no respondido

**Given**
- `projection_status != ANSWERED`

**Then**
- `status == BLOCKED`
- `blocked_reason == QUESTION_NOT_ANSWERED`

### 6. Raw owner answer faltante

**Given**
- `latest_raw_owner_answer` vacío o `None`

**Then**
- `status == BLOCKED`
- `blocked_reason == RAW_OWNER_ANSWER_MISSING`

### 7. Target ref inválido

**Given**
- `target_ref` ausente o malformado

**Then**
- `status == BLOCKED`
- `blocked_reason == TARGET_REF_INVALID`

### 8. Role faltante

**Given**
- `proposed_role is None`
- `suggested_semantic_role is None`

**Then**
- `status == BLOCKED`
- `blocked_reason == ROLE_MISSING`

### 9. Validation status inesperado

**Given**
- `owner_answer_validation_status != DECLARED_NOT_VALIDATED`

**Then**
- `status == BLOCKED`
- `blocked_reason == OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED`

## Invariantes transversales

Todos los escenarios, incluyendo bloqueados, deben verificar:

```text
runtime_authorized=False
human_review_required=True
reexecution_authorized=False
recalculation_authorized=False
```

Y además:

```text
declared owner input != validated evidence
candidate packet != classified answer
candidate packet != matrix mutation
```

## Assertions negativas obligatorias

El test futuro debe dejar explícito que el módulo:

- no devuelve `OwnerColumnConfirmationAnswer`;
- no devuelve `Service1ColumnConfirmationClassificationV1`;
- no devuelve `Service1ColumnConfirmationApplierResultV1`;
- no devuelve `Service1ColumnConfirmationCasePatchV1`;
- no expone `computation_unlocked`;
- no expone `persistence_authorized`;
- no cambia `owner_answer_validation_status`.

## Anti-deriva en tests

El archivo de tests futuro no debe:

- importar `service_1_column_confirmation_applier_v1.py`;
- importar `service_1_column_confirmation_case_patch_v1.py`;
- importar `vertical_pipeline.py`;
- abrir filesystem real;
- escribir JSONL;
- ejecutar classifier para “validar” el candidate packet;
- inferir role desde texto libre como parte del fixture.

## Criterio de PASS del futuro archivo de tests

El archivo de tests futuro queda bien diseñado si:

- cubre los 9 escenarios obligatorios;
- usa fixtures puras e in-memory;
- verifica blocked reasons 1:1;
- verifica invariantes en escenarios READY y BLOCKED;
- no mezcla classifier/applier/persistence.

## Comando de validación previsto

Cuando exista el runtime:

```text
python -m pytest tests/smartpyme/test_service_1_column_confirmation_reentry_candidate_v1.py -q
```

## Próximo paso correcto

```text
implementar el archivo de test
→ luego implementar el runtime mínimo para hacerlo pasar
```

No más alcance que eso.
