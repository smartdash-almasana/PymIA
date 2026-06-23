# SERVICE_1_MICROSERVICE_ACTIVATION_CONTRACT_V1

## Status

```text
IMPLEMENTED_MINIMAL_CONTRACT
```

## Purpose

Decide whether a Servicio 1 microservice can be activated for a concrete operational request.

This contract depends on:

```text
SERVICE_1_MICROSERVICE_REGISTRY_CONTRACT_V1
```

## Module

```text
PymIA-Live/pymia/smartpyme/service_1_microservice_activation_contract_v1.py
```

## Test module

```text
PymIA-Live/tests/smartpyme/test_service_1_microservice_activation_contract_v1.py
```

## Public function

```python
build_service_1_microservice_activation_contract_v1(activation_input: dict) -> dict
```

## Required input fields

```text
microservice_id
requested_capability
runtime_requested
human_review_present
```

Optional:

```text
available_microservices
```

## Output fields

```text
status
microservice_id
requested_capability
activated_microservice
activation_allowed
runtime_authorized
human_review_required
required_human_actions
blocked_reason
blocked_capabilities
next_allowed_action
```

## Status values

```text
ACTIVATION_ALLOWED
INVALID_INPUT
MISSING_REQUIRED_FIELDS
UNKNOWN_MICROSERVICE
BLOCKED_BY_REGISTRY
BLOCKED_BY_DEPENDENCIES
BLOCKED_BY_FORBIDDEN_CAPABILITY
BLOCKED_BY_RUNTIME_REQUEST
BLOCKED_BY_MISSING_HUMAN_REVIEW
```

## Rules

```text
Activation requires registry VALID.
Out-of-scope microservices remain blocked.
Missing dependencies block activation.
Runtime requests always block in V1.
Human review required by registry must be present.
Requested capabilities matching blocked capabilities are blocked.
Finality/external runtime terms are blocked.
```

## Explicit non-goals

```text
No runtime execution
No IO
No XLSX generation
No OCR
No parser
No APIs
No chatbot
No LLM adapter
No final reconciliation
No audit/certification/tax validation
No Servicio 2
No vertical_slice.py changes
```

## Contract status

```text
READY_FOR_MICROSERVICE_CHAIN_DRY_RUN
```
