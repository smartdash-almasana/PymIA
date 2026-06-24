# SERVICE_1_WEB_TEST_INTERFACE_ROUTE_REGISTRY_V1

## Status

```text
IMPLEMENTED_CANDIDATE
```

## Purpose

Create a pure deterministic route registry for the future Servicio 1 web test interface.

The registry defines which sandbox routes may be exposed online and which routes must remain blocked.

It does not implement a frontend, backend, API, runtime runner, upload flow, chatbot, OCR, Mercado Pago integration, Servicio 2, or production client delivery.

## Context

Previous design document:

```text
docs/producto/SERVICE_1_WEB_TEST_INTERFACE_DESIGN_V1.md
```

The design requires a safe allowlist before any interface is built.

This slice implements that allowlist as code:

```text
PymIA-Live/pymia/smartpyme/service_1_web_test_route_registry_v1.py
```

## Doctrine

```text
La web no decide.
La web expone rutas permitidas.
La registry bloquea rutas prohibidas.
El operador revisa.
Los archivos son el producto.
```

## Implemented files

```text
PymIA-Live/pymia/smartpyme/service_1_web_test_route_registry_v1.py
PymIA-Live/tests/smartpyme/test_service_1_web_test_route_registry_v1.py
docs/producto/SERVICE_1_WEB_TEST_INTERFACE_ROUTE_REGISTRY_V1.md
```

## Allowed route ids

```text
excel_treatment_lab_sandbox
invoice_collection_matching_sandbox
bank_reconciliation_sandbox
accounting_workpaper_draft_sandbox
first_aid_synthetic_delivery_rehearsal
```

## Blocked route ids

```text
mercado_pago_reconciliation
mercado_pago_reconciliation_sandbox
servicio_2_diagnostic
servicio_2_diagnostic_sandbox
ocr_ingestion
api_ingestion
chatbot_autonomo
real_client_delivery
final_accounting_review
```

## Route fields

Each route exposes:

```text
route_id
label
status
maturity_hint
allowed_data_modes
blocked_data_modes
runner_ref
expected_artifacts
forbidden_claims
human_review_required
runtime_authorized
production_allowed
```

## Universal safety flags

Every exposed route must keep:

```text
human_review_required=true
runtime_authorized=false
production_allowed=false
```

## Allowed data modes

Default allowed data modes:

```text
SYNTHETIC_FIXTURE
MANUAL_METADATA
ANONYMIZED_REHEARSAL_CANDIDATE
```

Exception:

```text
first_aid_synthetic_delivery_rehearsal
```

This route allows only:

```text
SYNTHETIC_FIXTURE
MANUAL_METADATA
```

because its purpose is synthetic delivery rehearsal, not anonymized real-case rehearsal.

## Blocked data modes

Every route blocks:

```text
REAL_CLIENT_DATA
SENSITIVE_ACCOUNTING_RECORDS
BANK_CREDENTIALS
MERCADO_PAGO_CREDENTIALS
PRODUCTION_API_TOKENS
```

## Functions

```text
list_service_1_web_test_routes_v1()
get_service_1_web_test_route_v1(route_id: str)
is_service_1_web_test_route_allowed_v1(route_id: str)
assert_service_1_web_test_route_allowed_v1(route_id: str)
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
- exactly 5 allowed routes are listed
- every route has stable required fields
- every route has runtime_authorized=false
- every route has production_allowed=false
- every route has human_review_required=true
- REAL_CLIENT_DATA is blocked by default
- Mercado Pago routes are not exposed
- Servicio 2 routes are not exposed
- unknown routes are blocked
- blank route ids are blocked
- forbidden claims exist for every route
- route copies are defensive
- module has no IO/web/runtime/LLM dependencies
```

## What this enables

This slice allows a future web interface to consume a controlled route registry instead of hardcoding UI options.

The UI may display route cards, limitations, expected artifacts and forbidden claims from the registry.

The UI must still not execute production workflows.

## What this does not enable

```text
No public production launch.
No client uploads.
No real-client data mode.
No real accounting claims.
No final reconciliation claims.
No final diagnostic claims.
No tax/fiscal claims.
No autonomous chat.
No API integrations.
No OCR.
No Mercado Pago.
No Servicio 2.
```

## Recommended next slice

```text
SERVICE_1_WEB_TEST_INTERFACE_RUN_SPEC_V1
```

Purpose:

```text
Define a pure test-run spec around an allowed route: run_id, route_id, data_mode, operator label, status, expected artifacts and review gate.
```

Reason:

```text
After route allowlisting, the web interface needs a safe run contract before any actual UI or runner adapter is built.
```

## Closeout verdict

```text
SERVICE_1_WEB_TEST_INTERFACE_ROUTE_REGISTRY_V1:
IMPLEMENTED_CANDIDATE

NEXT_VALIDATION:
pytest focal + smartpyme suite
```
