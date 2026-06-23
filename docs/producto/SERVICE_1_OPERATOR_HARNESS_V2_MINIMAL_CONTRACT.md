# SERVICE_1_OPERATOR_HARNESS_V2_MINIMAL_CONTRACT

## Status

```text
IMPLEMENTED_MINIMAL_CONTRACT
```

## Purpose

Convert `SERVICE_1_OPERATOR_HARNESS_V2_DESIGN` into a minimal executable contract that governs allowed operator actions for Servicio 1.

This contract is not a chatbot, LLM adapter, OCR/parser layer, accounting runtime, API integration, audit, certification, tax validation, final reconciliation, or Servicio 2 component.

## Module

```text
PymIA-Live/pymia/smartpyme/service_1_operator_harness_v2_contract.py
```

## Test module

```text
PymIA-Live/tests/smartpyme/test_service_1_operator_harness_v2_contract.py
```

## Public function

```python
build_service_1_operator_harness_v2_contract(operator_input: dict) -> dict
```

## Required input fields

```text
case_folder_manifest_status
delivery_manifest_audit_status
operator_requested_action
human_reviewer_present
human_review_status
forbidden_claims_check
stop_conditions
delivery_allowed_by_audit
```

## Output fields

```text
status
allowed_operator_actions
blocked_operator_actions
required_human_actions
delivery_allowed
next_allowed_action
```

## Allowed operator actions

```text
request_missing_evidence
prepare_owner_summary
prepare_operator_notes
prepare_operational_xlsx_draft
send_to_human_review
deliver_operational_draft
block_delivery
```

## Status values

```text
INVALID_INPUT
MISSING_REQUIRED_FIELDS
BLOCKED_BY_CASE_MANIFEST
BLOCKED_BY_DELIVERY_AUDIT
BLOCKED_BY_STOP_CONDITION
BLOCKED_BY_MISSING_HUMAN_REVIEW
BLOCKED_BY_FORBIDDEN_CLAIMS
BLOCKED_BY_FORBIDDEN_ACTION
READY_FOR_HUMAN_REVIEW
READY_FOR_OPERATIONAL_DRAFT_DELIVERY
```

## Delivery allow rule

`delivery_allowed` can be true only when all conditions hold:

```text
case_folder_manifest_status in [READY_FOR_QA, VALID]
delivery_manifest_audit_status in [PASS_READY_FOR_DELIVERY, PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW]
delivery_allowed_by_audit == true
stop_conditions == NONE
human_reviewer_present == true
human_review_status in [REQUIRED, COMPLETED]
forbidden_claims_check == PASSED
operator_requested_action == deliver_operational_draft
```

## Blocking rules

The contract blocks delivery when:

```text
input is not a dict
required fields are missing
case manifest is not ready
delivery audit is not passing
delivery audit does not allow delivery
stop condition is active
human reviewer is missing
human review status is invalid
forbidden claims check is not PASSED
operator action is outside the allowlist
```

## Explicit exclusions

```text
No IO
No XLSX generation
No OCR
No parser automatico
No chatbot
No LLM adapter
No APIs
No accounting runtime
No final reconciliation
No audit/certification/tax validation
No Servicio 2
No vertical_slice.py changes
```

## Focal test coverage

```text
valid delivery action -> READY_FOR_OPERATIONAL_DRAFT_DELIVERY / delivery_allowed true
non-dict input -> INVALID_INPUT
missing fields -> MISSING_REQUIRED_FIELDS
manifest not ready -> BLOCKED_BY_CASE_MANIFEST
delivery audit fail -> BLOCKED_BY_DELIVERY_AUDIT
delivery audit disallow flag -> BLOCKED_BY_DELIVERY_AUDIT
active stop condition -> BLOCKED_BY_STOP_CONDITION
missing human review -> BLOCKED_BY_MISSING_HUMAN_REVIEW
invalid human review status -> BLOCKED_BY_MISSING_HUMAN_REVIEW
forbidden claims check failed -> BLOCKED_BY_FORBIDDEN_CLAIMS
forbidden operator action -> BLOCKED_BY_FORBIDDEN_ACTION
send_to_human_review -> READY_FOR_HUMAN_REVIEW / delivery_allowed false
prepare_operator_notes -> READY_FOR_HUMAN_REVIEW / delivery_allowed false
no IO/XLSX/parser/API/LLM dependencies
no vertical_slice reference
```

## Contract status

```text
READY_FOR_OPERATOR_ACTION_GOVERNANCE_USE
```
