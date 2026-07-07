# SERVICE_1_RUNTIME_DELIVERY_FOLDER_INTEGRATION_AUDIT_V1

## VERDICT

```text
SERVICE_1_RUNTIME_DELIVERY_FOLDER_INTEGRATION_AUDIT_V1: PASS_WITH_REQUIRED_ADAPTER
```

## SCOPE

Auditar si la salida de:

```text
SERVICE_1_REAL_OWNER_PILOT_CASE_RUN_V1
```

puede integrarse con la infraestructura existente de carpeta/manifest de entrega sin crear un delivery paralelo.

Este documento no implementa delivery real, no ejecuta runtime, no escribe carpetas y no autoriza entrega al cliente.

## SOURCES READ

```text
PymIA-Live/pymia/smartpyme/service_1_real_owner_pilot_case_run_v1.py
PymIA-Live/pymia/smartpyme/service_1_case_delivery_folder_v1.py
PymIA-Live/pymia/smartpyme/service_1_delivery_manifest_audit_contract_v1.py
```

## CURRENT UPSTREAM

El piloto real con dueño produce un contrato de corrida con:

```text
status
case_id
tenant_id
intake_id
run_id
owner_ref
source_file_ref
owner_narrative
business_period_reference
adapter_result
bridge_status
pilot_pack_status
selected_primary_pathology
allowed_computation_ref
next_owner_question
package_candidate_ref
decision_checklist
stop_rules
blocked_reason
owner_confirmation_required
runtime_authorized=False
reexecution_authorized=False
recalculation_authorized=False
delivery_authorized=False
```

Estados upstream:

```text
REAL_OWNER_PACKAGE_CANDIDATE_READY
REAL_OWNER_NEEDS_OWNER_INPUT
REAL_OWNER_BLOCKED
```

## EXISTING DELIVERY INFRASTRUCTURE

Existe infraestructura real de carpeta de entrega en:

```text
PymIA-Live/pymia/smartpyme/service_1_case_delivery_folder_v1.py
```

Capacidades observadas:

```text
write_service_1_case_delivery_folder_v1(packet, base_dir)
finalize_service_1_case_delivery_folder_v1(packet, case_dir, files_written)
evaluate_service_1_final_delivery_folder_gate_v1(...)
build_service_1_delivery_policy_guard_v1(packet)
```

La carpeta existente espera un `packet` serializable con campos como:

```text
asset
owner_message
detected_structure
column_confirmation_packet
question_bundle
confirmed_columns
first_aid_eligibility_gate
first_aid_result
first_aid_owner_summary
owner_reentry_bridge
next_owner_question
evidence_loop_status
case_record
owner_delivery_packet
product_gate
delivery_policy_guard
```

La carpeta escribe artefactos como:

```text
owner_message.md
operator_packet.json
README.txt
delivery_policy_guard.json
final_qa_delivery_gate.json
manifest.json
next_owner_question.md
owner_delivery_packet.json
case_record.json
product_gate.json
```

## EXISTING MANIFEST AUDIT CONTRACT

Existe contrato de auditoría en:

```text
PymIA-Live/pymia/smartpyme/service_1_delivery_manifest_audit_contract_v1.py
```

Campos requeridos principales:

```text
case_id
manifest_present
case_family
period_present
operator_present
human_reviewer_present
input_files_listed
output_files_listed
xlsx_review_file_present
qa_checklist_present
qa_status
owner_message_present
operator_notes_present
evidence_gap_log_present
visible_differences_log_present
human_review_status
forbidden_claims_check
stop_conditions
delivery_status
next_safe_action
```

Estados relevantes:

```text
PASS_READY_FOR_DELIVERY
PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW
MISSING_REQUIRED_FIELDS
FAIL_MISSING_QA
FAIL_MISSING_HUMAN_REVIEW
FAIL_BLOCKED_BY_STOP_CONDITION
FAIL_FORBIDDEN_CLAIM_DETECTED
FAIL_REWORK_REQUIRED
```

## INTEGRATION FINDING

La integración NO debe hacerse conectando directamente `Service1RealOwnerPilotCaseRunV1` a `write_service_1_case_delivery_folder_v1(...)`.

Razón:

```text
El contrato del piloto real expresa una corrida operativa.
La carpeta de delivery espera un packet de entrega gobernado.
```

Por lo tanto, falta un adapter focal:

```text
SERVICE_1_REAL_OWNER_PILOT_TO_DELIVERY_PACKET_ADAPTER_V1
```

Ese adapter debe transformar:

```text
Service1RealOwnerPilotCaseRunV1
-> packet compatible con service_1_case_delivery_folder_v1.py
```

## REQUIRED MAPPING

### asset

```text
asset.asset_id          <- case_id
asset.source_file_ref   <- source_file_ref
asset.case_family       <- selected_primary_pathology or SERVICE_1_XLSX_FIRST
asset.period            <- business_period_reference
```

### owner_message

Si `status == REAL_OWNER_NEEDS_OWNER_INPUT`:

```text
owner_message <- next_owner_question
```

Si `status == REAL_OWNER_PACKAGE_CANDIDATE_READY`:

```text
owner_message <- mensaje operativo para dueño con límites explícitos
```

Si `status == REAL_OWNER_BLOCKED`:

```text
owner_message <- bloqueo claro + blocked_reason + próxima acción segura
```

### next_owner_question

Si existe `next_owner_question`:

```text
next_owner_question = {
  "markdown": next_owner_question,
  "owner_confirmation_required": True
}
```

### case_record

Debe incluir:

```text
case_id
tenant_id
intake_id
run_id
owner_ref
source_file_ref
owner_narrative
business_period_reference
status
bridge_status
pilot_pack_status
selected_primary_pathology
allowed_computation_ref
blocked_reason
```

### owner_delivery_packet

Debe incluir sólo salida visible/gobernada:

```text
status
owner_message
next_owner_question
selected_primary_pathology
allowed_computation_ref
package_candidate_ref
limits
stop_rules
owner_confirmation_required
```

### product_gate

Debe bloquear entrega autónoma:

```text
runtime_authorized=False
reexecution_authorized=False
recalculation_authorized=False
delivery_authorized=False
owner_confirmation_required=<from pilot>
status=READY_FOR_DELIVERY_POLICY_GUARD or BLOCKED
```

### delivery_policy_guard

Debe reutilizar:

```text
build_service_1_delivery_policy_guard_v1(packet)
```

No crear un guard paralelo.

## STATUS MAPPING

```text
REAL_OWNER_PACKAGE_CANDIDATE_READY
-> DELIVERY_PACKET_READY_FOR_POLICY_GUARD

REAL_OWNER_NEEDS_OWNER_INPUT
-> DELIVERY_PACKET_NEEDS_OWNER_INPUT

REAL_OWNER_BLOCKED
-> DELIVERY_PACKET_BLOCKED
```

## DELIVERY AUDIT INPUT MAPPING

Para `build_service_1_delivery_manifest_audit_contract_v1(...)`, el adapter futuro debe poder preparar un audit input conservador:

```text
case_id                         <- case_id
manifest_present                <- False until folder is actually finalized
case_family                     <- selected_primary_pathology or SERVICE_1_XLSX_FIRST
period_present                  <- business_period_reference is not blank
operator_present                <- True if metadata/operator_ref exists
human_reviewer_present          <- False by default before policy control
input_files_listed              <- source_file_ref present
output_files_listed             <- package_candidate_ref or next_owner_question present
xlsx_review_file_present        <- False unless real review artifact exists
qa_checklist_present            <- decision_checklist exists
qa_status                       <- PASSED only if checklist gates pass
owner_message_present           <- owner_message present
operator_notes_present          <- True only if metadata/operator_notes exists
evidence_gap_log_present        <- True if blocked/needs input is documented
visible_differences_log_present <- False unless explicitly produced
human_review_status             <- REQUIRED
forbidden_claims_check          <- PASSED only after claim scan/policy guard
default stop_conditions          <- NONE only when not blocked and not waiting owner
next_safe_action                <- policy/owner next action
```

## HARD LIMITS

This audit keeps the following boundaries:

```text
NO delivery folder writer changes in this slice.
NO parallel delivery package.
NO SaaS.
NO web.
NO API.
NO worker.
NO autonomous delivery.
NO final accounting claim.
NO definitive diagnosis claim.
```

## DECISION

The existing delivery infrastructure is reusable.

However, direct integration is not safe because the real-owner pilot contract is not a folder packet contract.

Required next implementation:

```text
SERVICE_1_REAL_OWNER_PILOT_TO_DELIVERY_PACKET_ADAPTER_V1
```

## ACCEPTANCE CRITERIA FOR NEXT PATCH

The next patch must:

```text
1. Read Service1RealOwnerPilotCaseRunV1.
2. Build a packet compatible with service_1_case_delivery_folder_v1.py.
3. Reuse build_service_1_delivery_policy_guard_v1(packet).
4. Never write folders.
5. Never call finalize_service_1_case_delivery_folder_v1(...).
6. Never authorize delivery.
7. Include owner_message, case_record, owner_delivery_packet, product_gate and delivery_policy_guard.
8. Preserve blocked/needs-owner-input states.
9. Include tests for ready, needs-owner-input and blocked cases.
```

## FINAL VERDICT

```text
DELIVERY_INFRASTRUCTURE_EXISTS: YES
DIRECT_REAL_OWNER_PILOT_TO_FOLDER_SAFE: NO
PARALLEL_DELIVERY_NEEDED: NO
REQUIRED_NEXT_ADAPTER: SERVICE_1_REAL_OWNER_PILOT_TO_DELIVERY_PACKET_ADAPTER_V1
SERVICE_1_STEP_3_STATUS: AUDITED_WITH_REQUIRED_ADAPTER
```
