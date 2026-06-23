# SERVICE_1_CASE_FOLDER_MANIFEST_V1

VEREDICT:

```text
SERVICE_1_CASE_FOLDER_MANIFEST_V1: CREATED
```

PURPOSE:

```text
Definir el manifest mínimo de carpeta de caso para Servicio 1 V1.

El objetivo es que cada caso asistido tenga trazabilidad operativa antes de avanzar a entrega cliente, QA, XLSX operativo o revisión humana.
```

WHY_THIS_EXISTS:

```text
Servicio 1 ya cuenta con runbook, QA checklist, synthetic XLSX edge-case run y gates de seguridad.

El siguiente riesgo no es conceptual sino operativo: que cada caso se ejecute con estructura distinta, archivos sueltos, notas dispersas o límites no trazables.

Este manifest ordena el contenedor del caso.
No ejecuta lógica.
No calcula resultados.
No valida exactitud contable.
No reemplaza revisión humana.
```

MANIFEST_SCOPE:

```text
Aplica a casos de Servicio 1 bajo modelo:
microservicio asistido bajo revisión humana.

Incluye:
- identificación del caso
- familia operativa
- período
- operador
- responsable humano
- archivos de entrada
- archivos de salida
- QA checklist
- XLSX operativo de revisión
- owner message
- notas operador
- diferencias visibles
- faltantes de evidencia
- stop conditions
- claims prohibidos
- estado de entrega
- próxima acción segura

No incluye:
- auditoría
- certificación
- conciliación definitiva
- validación fiscal
- asientos automáticos
- reemplazo del contador
- APIs vivas
- OCR
- parser automático
- chatbot libre
```

MANIFEST_FIELDS:

```text
case_id:
client_alias:
case_family:
period:
operator:
human_reviewer:
intake_status:
accepted_scope:
rejected_scope:
input_files:
output_files:
xlsx_review_file:
qa_checklist_file:
owner_message_file:
operator_notes_file:
evidence_gap_log:
visible_differences_log:
human_review_status:
forbidden_claims_check:
stop_conditions:
delivery_status:
next_safe_action:
```

REQUIRED_FIELDS:

```text
case_id
client_alias
case_family
period
operator
human_reviewer
intake_status
accepted_scope
input_files
human_review_status
forbidden_claims_check
stop_conditions
delivery_status
next_safe_action
```

OPTIONAL_FIELDS:

```text
rejected_scope
output_files
xlsx_review_file
qa_checklist_file
owner_message_file
operator_notes_file
evidence_gap_log
visible_differences_log
```

CASE_STATUS_VALUES:

```text
INTAKE_PENDING
INTAKE_RECEIVED
SCOPE_ACCEPTED
SCOPE_REDUCTION_REQUIRED
BLOCKED_BY_SCOPE
BLOCKED_BY_EVIDENCE
BLOCKED_BY_HUMAN_REVIEW
READY_FOR_QA
QA_PASSED
QA_FAILED
READY_FOR_DELIVERY
DELIVERED_AS_DRAFT
CLOSED_UNDER_HUMAN_REVIEW
```

DELIVERY_STATUS_VALUES:

```text
NOT_READY
BLOCKED
REWORK_REQUIRED
READY_FOR_OPERATOR_REVIEW
READY_FOR_HUMAN_REVIEW
READY_FOR_CLIENT_DELIVERY
DELIVERED_AS_OPERATIONAL_DRAFT
CLOSED
```

STOP_CONDITION_VALUES:

```text
NONE
MISSING_MINIMUM_EVIDENCE
MISSING_HUMAN_REVIEWER
SCOPE_TOO_BROAD
SCOPE_NOT_SUPPORTED
FORBIDDEN_CLAIM_REQUESTED
AUDIT_REQUESTED
CERTIFICATION_REQUESTED
FISCAL_VALIDATION_REQUESTED
FINAL_RECONCILIATION_REQUESTED
ACCOUNTING_ENTRY_REQUESTED
API_REQUIRED
OCR_REQUIRED
PARSER_REQUIRED
CHATBOT_AUTONOMY_REQUIRED
REAL_DATA_POLICY_VIOLATION
```

FORBIDDEN_CLAIMS_CHECK:

```text
The manifest must explicitly record whether forbidden claims were checked.

Forbidden claims:
- auditado
- certificado
- conciliado definitivamente
- validado fiscalmente
- exacto
- cerrado contablemente
- aprobado fiscalmente
- reemplaza al contador
- garantiza exactitud
- listo para presentación fiscal
- resultado contable final

Required safe language:
- borrador operativo
- evidencia declarada
- diferencias visibles
- faltantes de evidencia
- advertencias operativas
- requiere revisión humana
```

FOLDER_STRUCTURE:

```text
Recommended external case folder:

E:\BuenosPasos\smartbridge\PymIA-local-artifacts\service_1_cases\<CASE_ID>\

Subfolders:
01_contexto\
02_evidencia_base\
03_outputs_operativos\
04_qa\
05_entrega_cliente\
06_review_sanitizado\

Required local-only files:
01_contexto\case_manifest.md
01_contexto\case_context.md
02_evidencia_base\<input files>
03_outputs_operativos\<output files>
04_qa\qa_checklist_result.md
05_entrega_cliente\owner_message.md
05_entrega_cliente\delivery_notes.md

Never commit:
- service_1_cases/
- real client folders
- XLSX client inputs
- XLSX operational outputs
- sensitive evidence
- scratch scripts
```

EXAMPLE_MANIFEST:

```yaml
case_id: SERVICE1_CASE_0001
client_alias: cliente_anonimizado_001
case_family: ventas_declaradas_vs_cobros_declarados
period: 2026-05
operator: operator_alias
human_reviewer: reviewer_alias
intake_status: INTAKE_RECEIVED
accepted_scope: "ventas declaradas vs cobros declarados, período 2026-05"
rejected_scope: "validación fiscal, conciliación definitiva, auditoría"
input_files:
  - ventas_declaradas_2026_05.xlsx
  - cobros_declarados_2026_05.xlsx
output_files:
  - accounting_workpaper_review_draft.xlsx
xlsx_review_file: accounting_workpaper_review_draft.xlsx
qa_checklist_file: qa_checklist_result.md
owner_message_file: owner_message.md
operator_notes_file: operator_notes.md
evidence_gap_log: evidence_gap_log.md
visible_differences_log: visible_differences_log.md
human_review_status: REQUIRED
forbidden_claims_check: PASSED
stop_conditions: NONE
delivery_status: READY_FOR_CLIENT_DELIVERY
next_safe_action: DELIVER_AS_OPERATIONAL_DRAFT_UNDER_HUMAN_REVIEW
```

VALIDATION_RULES:

```text
1. case_id must exist.
2. client_alias must not expose sensitive real identity if the manifest may be summarized.
3. case_family must be supported or explicitly marked as scope reduction required.
4. period must be defined.
5. operator must be identified.
6. human_reviewer must be identified before delivery.
7. accepted_scope must be explicit.
8. input_files must be listed.
9. evidence declared must remain separate from inference.
10. xlsx_review_file must not be treated as final accounting output.
11. qa_checklist_file must exist before delivery.
12. forbidden_claims_check must pass before delivery.
13. stop_conditions must be NONE before client delivery.
14. next_safe_action must always be present.
```

FAIL_CLOSED_RULES:

```text
Block delivery if:
- missing case_id
- missing period
- missing human_reviewer
- missing minimum evidence
- unsupported family without scope reduction
- QA checklist missing
- forbidden claims not checked
- forbidden claims detected
- stop conditions active
- XLSX appears as final/dictamen
- owner message lacks borrador operativo / evidencia declarada / revisión humana requerida
```

RELATION_TO_QA_CHECKLIST:

```text
The case manifest is the container.
The QA checklist is the delivery gate.

The manifest must point to the QA checklist result.
A case cannot move to READY_FOR_CLIENT_DELIVERY without QA checklist passed.
```

RELATION_TO_OPERATOR_RUNBOOK:

```text
The runbook defines how the operator acts.
The manifest records that the operator acted inside the allowed path.

The manifest must reflect scope, evidence, warnings, review status and stop conditions produced during runbook execution.
```

RELATION_TO_XLSX_RUNTIME:

```text
The manifest does not generate XLSX.
It only records the existence and role of the XLSX operational review file.

Current allowed language:
- XLSX operativo de revisión
- borrador operativo
- evidencia declarada
- requiere revisión humana

Not allowed:
- runtime contable productivo
- conciliación definitiva
- cierre contable
- exactitud garantizada
```

OUT_OF_SCOPE:

```text
This manifest does not:
- execute calculations
- parse files
- call APIs
- run OCR
- run chatbot
- certify evidence
- validate tax position
- create accounting entries
- replace the accountant
- approve final reconciliation
```

NEXT_SAFE_ACTION:

```text
SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1
```

COMMIT_READY:

```text
YES
```
