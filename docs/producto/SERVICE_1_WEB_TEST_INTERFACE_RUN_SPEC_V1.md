# SERVICE_1_WEB_TEST_INTERFACE_RUN_SPEC_V1

## Status

```text
IMPLEMENTED_CANDIDATE
```

## Purpose

Define a pure deterministic test-run spec for the future Servicio 1 web test interface.

This slice wraps an allowed web-test route with run metadata, data mode, operator label, case label, expected artifacts, forbidden claims, review state, and closure decision.

It does not execute any route.

## Context

Previous slices:

```text
docs/producto/SERVICE_1_WEB_TEST_INTERFACE_DESIGN_V1.md
PymIA-Live/pymia/smartpyme/service_1_web_test_route_registry_v1.py
docs/producto/SERVICE_1_WEB_TEST_INTERFACE_ROUTE_REGISTRY_V1.md
```

The route registry says which routes may appear in the web interface.

The run spec says how a selected route becomes a controlled sandbox run candidate.

## Implemented files

```text
PymIA-Live/pymia/smartpyme/service_1_web_test_run_spec_v1.py
PymIA-Live/tests/smartpyme/test_service_1_web_test_run_spec_v1.py
docs/producto/SERVICE_1_WEB_TEST_INTERFACE_RUN_SPEC_V1.md
```

## Doctrine

```text
La web no decide.
La route registry permite o bloquea.
El run spec estructura la prueba.
La ejecución real sigue separada.
La revisión humana cierra.
```

## Inputs

The builder accepts:

```text
run_id
route_id
data_mode
operator_label
case_label
```

Required:

```text
run_id
route_id
```

Defaults:

```text
data_mode = SYNTHETIC_FIXTURE
operator_label = internal_operator
case_label = sandbox_rehearsal_case
```

## Output fields

```text
status
run_id
route_id
route_label
data_mode
operator_label
case_label
state
review_decision
human_review_required
runtime_authorized
production_allowed
expected_artifacts
forbidden_claims
blocked_reason
next_allowed_action
```

## Statuses

```text
READY_FOR_SANDBOX_REHEARSAL
INVALID_INPUT
BLOCKED_ROUTE
BLOCKED_DATA_MODE
```

## States

```text
CREATED
ROUTE_CONFIRMED
INPUT_CONFIRMED
ARTIFACTS_EXPECTED
OPERATOR_REVIEW_REQUIRED
CLOSED_AS_SANDBOX_REHEARSAL
BLOCKED
```

In this first version, a valid built run lands directly in:

```text
OPERATOR_REVIEW_REQUIRED
```

because the run spec does not execute anything. It prepares the future UI to show expected artifacts and forbidden claims before any runner adapter exists.

## Review decisions

Allowed review decisions:

```text
PENDING_REVIEW
CLOSE_SANDBOX_REHEARSAL
BLOCK_RUN
REQUEST_MORE_EVIDENCE
```

Explicitly not allowed:

```text
APPROVE_FINAL_DELIVERY
APPROVE_ACCOUNTING_RESULT
APPROVE_TAX_RESULT
APPROVE_DIAGNOSIS
```

## Universal safety flags

Every result, including blocked results, keeps:

```text
human_review_required=true
runtime_authorized=false
production_allowed=false
```

## Blocked by design

The run spec blocks:

```text
unknown routes
Mercado Pago routes
Servicio 2 routes
REAL_CLIENT_DATA
route-specific blocked data modes
unsupported review decisions
```

## Functions

```text
build_service_1_web_test_run_spec_v1(run_input: dict)
close_service_1_web_test_run_spec_v1(run_spec, review_decision=...)
```

## Design constraints

The module is intentionally pure.

It must not import or depend on:

```text
openpyxl
pandas
pathlib
requests
httpx
FastAPI
flask
django
streamlit
subprocess
OpenAI
LangChain
vertical_slice
```

It performs no:

```text
file IO
web IO
runtime execution
artifact creation
upload handling
LLM calls
framework wiring
```

## Tests added

The focal test file verifies:

```text
- valid run specs are built for allowed routes
- required fields are stable
- safe defaults are applied
- every ready run is non-production and human-reviewed
- invalid input is blocked
- missing run_id is blocked
- missing route_id is blocked
- unknown route is blocked
- Mercado Pago route is blocked
- Servicio 2 route is blocked
- REAL_CLIENT_DATA is blocked
- first_aid_synthetic_delivery_rehearsal blocks anonymized candidate mode
- ready run may close only as sandbox rehearsal
- operator may block a run
- operator may request more evidence
- blocked run cannot be closed as success
- unsupported review decision is rejected
- module has no IO/web/runtime/LLM dependencies
```

## What this enables

A future web UI can create a safe run preview before any execution:

```text
route selected
+ data mode validated
+ artifacts expected
+ forbidden claims visible
+ review required
+ production blocked
```

## What this does not enable

```text
No frontend.
No backend.
No route execution.
No file upload.
No artifact writing.
No public launch.
No client data.
No accounting conclusion.
No tax/fiscal conclusion.
No diagnostic conclusion.
No autonomous chat.
No OCR.
No Mercado Pago.
No Servicio 2.
```

## Recommended next slice

```text
SERVICE_1_WEB_TEST_INTERFACE_REVIEW_CHECKLIST_V1
```

Purpose:

```text
Define a pure review checklist required before a sandbox run can be closed in the future UI.
```

Reason:

```text
The web interface should force human review explicitly before any test run is marked closed.
```

## Closeout verdict

```text
SERVICE_1_WEB_TEST_INTERFACE_RUN_SPEC_V1:
IMPLEMENTED_CANDIDATE

NEXT_VALIDATION:
pytest focal + smartpyme suite + full suite
```
