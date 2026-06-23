# SERVICE_1_MICROSERVICE_REGISTRY_CONTRACT_V1

## Status

```text
IMPLEMENTED_MINIMAL_CONTRACT
```

## Purpose

Define an executable internal registry for Servicio 1 microservices.

The registry answers:

```text
which microservice exists
what state it has
which inputs are allowed
which outputs are allowed
whether runtime is authorized
whether human review is required
which capabilities are blocked
which dependencies are required
what the next allowed action is
```

This is not a commercial document and not a real-case readiness audit.

## Module

```text
PymIA-Live/pymia/smartpyme/service_1_microservice_registry_contract_v1.py
```

## Test module

```text
PymIA-Live/tests/smartpyme/test_service_1_microservice_registry_contract_v1.py
```

## Public function

```python
build_service_1_microservice_registry_contract_v1(registry_input: dict) -> dict
```

## Input

```text
microservice_id
available_microservices optional list[str]
```

If `available_microservices` is omitted, the registry assumes the declared internal Servicio 1 registry is available. If supplied, dependencies are checked against that list.

## Output fields

```text
status
microservice_id
state
allowed_inputs
allowed_outputs
runtime_authorized
human_review_required
blocked_capabilities
dependencies
missing_dependencies
next_allowed_action
```

## Status values

```text
VALID
INVALID_INPUT
UNKNOWN_MICROSERVICE
BLOCKED_MICROSERVICE
BLOCKED_BY_DEPENDENCIES
```

## State values

```text
IMPLEMENTED_VALIDATED
IMPLEMENTED_PARTIAL
CONTRACT_ONLY
EXPERIMENTAL_FROZEN
OUT_OF_SCOPE
```

## Registered Servicio 1 microservices

```text
file_intake
first_aid_triage
excel_treatment_lab
exceland_bridge
owner_output
xlsx_delivery
accounting_contracts
bank_reconciliation_basic
mercado_pago_reconciliation_basic
invoice_collection_matching_basic
supplier_purchase_review_basic
accounting_workpaper
case_folder_manifest
delivery_manifest_audit
operator_harness
```

## Explicitly blocked / out of scope entries

```text
chatbot
servicio_2_diagnostic
```

These are registered only to be blocked by the registry, not to activate them.

## Hard rule

```text
runtime_authorized is false for every registered entry in V1.
```

This registry does not authorize:

```text
chatbot runtime
LLM runtime
OCR runtime
parser runtime
APIs
final reconciliation
accounting certification
tax validation
automatic journal entries
Servicio 2 diagnosis
```

## Dependency examples

```text
delivery_manifest_audit depends on case_folder_manifest
operator_harness depends on case_folder_manifest and delivery_manifest_audit
bank_reconciliation_basic depends on accounting_contracts and xlsx_delivery
mercado_pago_reconciliation_basic depends on accounting_contracts and xlsx_delivery
accounting_workpaper depends on accounting_contracts and xlsx_delivery
```

## Test coverage

```text
file_intake valid entry
operator_harness dependencies and blocked capabilities
accounting_contracts contract-only boundary
bank_reconciliation dependency blocking
delivery_manifest_audit dependency pass
chatbot blocked as out of scope
servicio_2_diagnostic blocked as out of scope
unknown microservice rejected
invalid input rejected
blank microservice_id rejected
all registered entries runtime_authorized false
all outputs have exact required fields
core microservices registered
no IO/XLSX/parser/API/LLM dependencies
no vertical_slice reference
```

## Contract status

```text
READY_FOR_MICROSERVICE_ACTIVATION_CONTRACT
```
