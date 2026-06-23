# SERVICE_1_DELIVERY_MANIFEST_AUDIT_CONTRACT_V1

## Status

```text
IMPLEMENTED_MINIMAL_CONTRACT
```

## Purpose

Convert `SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1` into a minimal executable contract for Servicio 1 delivery safety.

This contract validates whether a delivery package may proceed as an operational draft under human review. It is a fail-closed gate. It does not audit accounting correctness, validate taxes, certify results, run OCR, parse documents, generate XLSX, call APIs, or replace professional review.

## Python module

```text
PymIA-Live/pymia/smartpyme/service_1_delivery_manifest_audit_contract_v1.py
```

## Test module

```text
PymIA-Live/tests/smartpyme/test_service_1_delivery_manifest_audit_contract_v1.py
```

## Public function

```python
build_service_1_delivery_manifest_audit_contract_v1(audit_input: dict) -> dict
```

## Required input fields

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

Blank values and empty lists/dicts count as missing.

## Output fields

```text
status
missing_fields
failed_gates
active_stop_conditions
delivery_allowed
human_review_required
next_allowed_action
```

## Status values

```text
INVALID_INPUT
MISSING_REQUIRED_FIELDS
FAIL_MISSING_QA
FAIL_MISSING_HUMAN_REVIEW
FAIL_BLOCKED_BY_STOP_CONDITION
FAIL_FORBIDDEN_CLAIM_DETECTED
FAIL_REWORK_REQUIRED
PASS_READY_FOR_DELIVERY
PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW
```

## Pass gates

Delivery can pass only when:

```text
all required fields are present
manifest_present == true
period_present == true
operator_present == true
human_reviewer_present == true
input_files_listed == true
output_files_listed == true
xlsx_review_file_present == true
qa_checklist_present == true
qa_status == PASSED
owner_message_present == true
operator_notes_present == true
evidence_gap_log_present == true
visible_differences_log_present == true
human_review_status in [REQUIRED, COMPLETED]
forbidden_claims_check == PASSED
stop_conditions == NONE
delivery_status in [READY_FOR_CLIENT_DELIVERY, DELIVERED_AS_OPERATIONAL_DRAFT]
next_safe_action is present
```

## Warning behavior

Documented warnings produce:

```text
PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW
```

Warnings do not authorize final accounting claims. They only allow an operational draft to proceed under human review when all hard gates pass.

Supported warning inputs:

```text
warning_flags: list[str]
duplicate_payments_or_collections_present: true
missing_master_data_exists: true
transaction_keys_incomplete: true
negative_amounts_or_credit_notes_present: true
material_evidence_gaps_documented: true
aggregate_only_due_to_missing_keys: true
operational_draft_only: true
```

## Fail-closed behavior

The contract blocks delivery when:

```text
input is not a dict
required fields are missing
QA is missing or not PASSED
human reviewer is missing
human_review_status is not REQUIRED or COMPLETED
stop_conditions is anything other than NONE
forbidden_claims_check is not PASSED
delivery_status implies final accounting result or unsupported delivery state
owner/operator/evidence/differences references are missing
next_safe_action is missing
```

## Explicit non-goals

```text
No IO
No XLSX generation
No OCR
No parser automático
No LLM
No chatbot
No APIs
No conciliación definitiva
No auditoría/certificación/fiscalidad
No asientos automáticos
No vertical_slice.py changes
```

## Focal test coverage

```text
valid audit input -> PASS_READY_FOR_DELIVERY / delivery_allowed true
human_review_status COMPLETED -> no human_review_required
non-dict input -> INVALID_INPUT
missing required fields -> MISSING_REQUIRED_FIELDS
QA failed/missing -> FAIL_MISSING_QA
human reviewer missing -> FAIL_MISSING_HUMAN_REVIEW
invalid human_review_status -> FAIL_MISSING_HUMAN_REVIEW
active stop condition -> FAIL_BLOCKED_BY_STOP_CONDITION
forbidden claims check failed -> FAIL_FORBIDDEN_CLAIM_DETECTED
final accounting delivery status -> FAIL_REWORK_REQUIRED
documented warning -> PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW
owner message missing -> FAIL_REWORK_REQUIRED
no IO/XLSX/parser/LLM dependencies in contract module
no vertical_slice reference
```

## Contract status

```text
READY_FOR_DELIVERY_SAFETY_GATE_USE
```
