# SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1

VEREDICT:

```text
SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1: CREATED
```

PURPOSE:

```text
Definir una auditoría documental-operativa del manifest de entrega de Servicio 1 antes de cualquier salida al cliente.

El objetivo es verificar que el caso tenga contenedor, evidencia, QA, revisión humana, mensaje seguro, límites explícitos y ausencia de claims prohibidos.
```

WHY_THIS_EXISTS:

```text
SERVICE_1_CASE_FOLDER_MANIFEST_V1 define el contenedor del caso.
SERVICE_1_QA_DELIVERY_CHECKLIST_V1 define el gate de calidad.
SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1 verifica que ambos estén alineados antes de entregar.

Este documento reduce riesgo operativo antes de mejorar runtime o ejecutar casos reales.
```

AUDIT_SCOPE:

```text
Audita:
- manifest de carpeta de caso
- archivos esperados
- estado QA
- estado human review
- owner message
- operator package
- XLSX operativo de revisión
- diferencias visibles
- faltantes de evidencia
- stop conditions
- forbidden claims
- próxima acción segura

No audita:
- exactitud contable final
- validez fiscal
- conciliación definitiva
- suficiencia jurídica
- certificación
- auditoría profesional
```

INPUTS_REQUIRED:

```text
case_manifest.md
qa_checklist_result.md
owner_message.md
operator_notes.md
evidence_gap_log.md
visible_differences_log.md
xlsx_review_file reference
human reviewer reference
delivery notes if present
```

AUDIT_FIELDS:

```text
case_id:
manifest_present:
case_family:
period_present:
operator_present:
human_reviewer_present:
input_files_listed:
output_files_listed:
xlsx_review_file_present:
qa_checklist_present:
qa_status:
owner_message_present:
operator_notes_present:
evidence_gap_log_present:
visible_differences_log_present:
human_review_status:
forbidden_claims_check:
stop_conditions:
delivery_status:
next_safe_action:
audit_result:
```

PASS_CONDITIONS:

```text
PASS only if:
- case_id exists
- manifest exists
- period exists
- case_family is supported or scope-reduced
- operator is identified
- human reviewer is identified
- input files are listed
- output files are listed when delivery exists
- XLSX review file is referenced when applicable
- QA checklist exists and passed
- owner message exists
- evidence gaps are logged or explicitly none
- visible differences are logged or explicitly none
- forbidden claims check passed
- stop conditions are NONE
- delivery status is READY_FOR_CLIENT_DELIVERY or DELIVERED_AS_OPERATIONAL_DRAFT
- next safe action exists
```

FAIL_CONDITIONS:

```text
FAIL if:
- manifest missing
- QA missing
- human reviewer missing
- forbidden claims not checked
- forbidden claims detected
- stop condition active
- case scope too broad
- evidence minimum missing
- XLSX appears as final/dictamen
- owner message lacks safe language
- delivery status implies final accounting result
- next safe action missing
```

WARNING_CONDITIONS:

```text
WARN if:
- duplicate payments or collections are present
- missing master data exists
- transaction keys are incomplete
- negative amounts or credit notes appear
- evidence gaps are material but documented
- analysis is aggregate-only due to missing keys
- output can proceed only as borrador operativo
```

FORBIDDEN_CLAIMS_AUDIT:

```text
Reject delivery if any of these appear in owner-facing or delivery-facing text:
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

Required safe language when applicable:
- borrador operativo
- evidencia declarada
- diferencias visibles
- faltantes de evidencia
- advertencias operativas
- requiere revisión humana
```

STOP_CONDITION_AUDIT:

```text
Delivery must block if manifest includes any active stop condition other than NONE.

Critical stop conditions:
- MISSING_MINIMUM_EVIDENCE
- MISSING_HUMAN_REVIEWER
- SCOPE_TOO_BROAD
- SCOPE_NOT_SUPPORTED
- FORBIDDEN_CLAIM_REQUESTED
- AUDIT_REQUESTED
- CERTIFICATION_REQUESTED
- FISCAL_VALIDATION_REQUESTED
- FINAL_RECONCILIATION_REQUESTED
- ACCOUNTING_ENTRY_REQUESTED
- API_REQUIRED
- OCR_REQUIRED
- PARSER_REQUIRED
- CHATBOT_AUTONOMY_REQUIRED
- REAL_DATA_POLICY_VIOLATION
```

DELIVERY_AUDIT_RESULT_VALUES:

```text
PASS_READY_FOR_DELIVERY
PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW
FAIL_REWORK_REQUIRED
FAIL_SCOPE_REDUCTION_REQUIRED
FAIL_BLOCKED_BY_STOP_CONDITION
FAIL_FORBIDDEN_CLAIM_DETECTED
FAIL_MISSING_HUMAN_REVIEW
FAIL_MISSING_QA
```

AUDIT_PROCEDURE:

```text
1. Open case manifest.
2. Confirm required manifest fields.
3. Confirm folder references exist locally.
4. Confirm QA checklist result.
5. Confirm human reviewer.
6. Confirm owner message exists.
7. Confirm XLSX role is operational review only.
8. Confirm evidence gaps are explicit.
9. Confirm visible differences are explicit.
10. Confirm no forbidden claims.
11. Confirm stop_conditions = NONE.
12. Confirm next_safe_action exists.
13. Assign audit result.
14. Block delivery if any fail condition is present.
```

RELATION_TO_CASE_FOLDER_MANIFEST:

```text
The case folder manifest is the source of truth for case state.
This audit reads and verifies it.

The audit must not create or alter evidence.
The audit must not infer missing data.
The audit only approves, warns, blocks or requests rework.
```

RELATION_TO_QA_DELIVERY_CHECKLIST:

```text
QA checklist validates delivery quality.
Delivery manifest audit verifies that QA actually exists, passed, and aligns with manifest state.

A delivery cannot pass audit if QA checklist is missing or failed.
```

RELATION_TO_OPERATOR_RUNBOOK:

```text
The runbook governs operator behavior.
The audit checks whether the delivery artifacts reflect allowed behavior:
- no invented evidence
- no automatic netting of duplicates
- no credit notes treated as normal payments without warning
- no unsupported broad case
- no final accounting claims
```

RELATION_TO_XLSX_RUNTIME:

```text
Current allowed XLSX role:
- XLSX operativo de revisión
- borrador operativo
- evidence/differences/gaps support artifact
- requires human review

Current disallowed XLSX role:
- accounting runtime productivo
- conciliación definitiva
- dictamen
- cierre contable
- exactitud garantizada
```

EXAMPLE_AUDIT_RECORD:

```yaml
case_id: SERVICE1_CASE_0001
manifest_present: true
case_family: ventas_declaradas_vs_cobros_declarados
period_present: true
operator_present: true
human_reviewer_present: true
input_files_listed: true
output_files_listed: true
xlsx_review_file_present: true
qa_checklist_present: true
qa_status: PASSED
owner_message_present: true
operator_notes_present: true
evidence_gap_log_present: true
visible_differences_log_present: true
human_review_status: REQUIRED
forbidden_claims_check: PASSED
stop_conditions: NONE
delivery_status: READY_FOR_CLIENT_DELIVERY
next_safe_action: DELIVER_AS_OPERATIONAL_DRAFT_UNDER_HUMAN_REVIEW
audit_result: PASS_READY_FOR_DELIVERY
```

FAIL_CLOSED_RULES:

```text
If unsure, block delivery.
If evidence is missing, do not infer it.
If scope is broad, reduce scope or block.
If human review is missing, block.
If QA is missing, block.
If forbidden claims appear, block.
If stop condition is active, block.
If XLSX looks final, block.
```

OUT_OF_SCOPE:

```text
This audit does not:
- execute code
- run tests
- call APIs
- run OCR
- parse documents
- generate XLSX
- validate taxes
- certify accounting correctness
- replace professional review
- approve final reconciliation
```

NEXT_SAFE_ACTION:

```text
SERVICE_1_ACCOUNTING_XLSX_RUNTIME_V1_DESIGN_OR_SERVICE_1_OPERATOR_HARNESS_V2
```

COMMIT_READY:

```text
YES
```
