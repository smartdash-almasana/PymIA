# SERVICE_1_CASE_FOLDER_MANIFEST_CONTRACT_V1

## Status

```text
IMPLEMENTED_MINIMAL_CONTRACT
```

## Purpose

Convert `SERVICE_1_CASE_FOLDER_MANIFEST_V1` into a minimal executable contract for Servicio 1 case-folder readiness.

This contract is infrastructure-only. It validates manifest shape and safety gates before QA handoff. It does not validate accounting accuracy, interpret business evidence, generate XLSX files, call APIs, run OCR, parse documents, or make fiscal/certification claims.

## Runtime boundary

Allowed:

```text
pure Python dict validation
required field checks
stop-condition detection
human-review gate
forbidden-claims gate
delivery_allowed decision
next_allowed_action decision
```

Forbidden:

```text
IO
XLSX processing
OCR
parser automático
LLM
chatbot
APIs
conciliación definitiva
auditoría/certificación/fiscalidad
asientos automáticos
vertical_slice.py changes
```

## Python module

```text
PymIA-Live/pymia/smartpyme/service_1_case_folder_manifest_contract_v1.py
```

## Public function

```python
build_service_1_case_folder_manifest_contract_v1(manifest_input: dict) -> dict
```

## Required fields

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

Blank values and empty lists/dicts count as missing.

## Output fields

```text
status
missing_fields
active_stop_conditions
human_review_required
forbidden_claims_check_status
delivery_allowed
next_allowed_action
```

## Statuses

```text
INVALID_INPUT
MISSING_REQUIRED_FIELDS
BLOCKED_BY_STOP_CONDITION
BLOCKED_BY_MISSING_HUMAN_REVIEWER
BLOCKED_BY_FORBIDDEN_CLAIMS_CHECK
READY_FOR_QA
```

`VALID` is reserved as a vocabulary status, but this implementation returns `READY_FOR_QA` for a manifest that passes all gates because the contract is specifically a QA handoff gate.

## Gate rules

### Stop conditions

A stop condition is active when:

```text
stop_conditions != NONE
```

Lists/tuples/sets are treated as active when they contain any non-empty item other than `NONE`.

### Forbidden claims

Forbidden claims check is valid only when:

```text
forbidden_claims_check == PASSED
```

### Human review

Human review is valid only when:

```text
human_reviewer is not blank
human_review_status in [REQUIRED, COMPLETED]
```

### Delivery allowed

Delivery is allowed only when:

```text
all required fields are present
stop_conditions == NONE
forbidden_claims_check == PASSED
human_reviewer is present
human_review_status in [REQUIRED, COMPLETED]
```

## Test file

```text
PymIA-Live/tests/smartpyme/test_service_1_case_folder_manifest_contract_v1.py
```

## Focal coverage

```text
valid manifest -> READY_FOR_QA / delivery_allowed true
non-dict input -> INVALID_INPUT
missing required fields -> MISSING_REQUIRED_FIELDS
missing/invalid human reviewer gate
active stop condition -> BLOCKED_BY_STOP_CONDITION
forbidden claims check failure -> BLOCKED_BY_FORBIDDEN_CLAIMS_CHECK
empty input_files -> MISSING_REQUIRED_FIELDS
no openpyxl/pandas/pathlib/open/read/write in contract module
no vertical_slice reference
```

## Contract status

```text
READY_FOR_OPERATOR_QA_GATE_USE
```
