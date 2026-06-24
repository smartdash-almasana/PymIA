# SERVICE_1_XLSX_BROWSER_SANDBOX_LANDING_V1

## Status

```text
IMPLEMENTED_CANDIDATE
```

## Purpose

Adapt the existing landing idea into a Servicio 1-compatible browser sandbox for XLSX rehearsal.

The goal is to support an online/internal test flow with:

```text
- real XLSX loading in the browser through SheetJS
- sheet preview
- sheet tabs
- owner-question side panel
- TXT export of owner/operator answers
```

## Implemented files

```text
landing/build_service1_sandbox_html.py
tests/test_service1_sandbox_landing_generator.py
docs/producto/SERVICE_1_XLSX_BROWSER_SANDBOX_LANDING_V1.md
```

## Generated local file

The generator writes:

```text
landing/servicio1-sandbox.html
```

Command:

```powershell
python landing/build_service1_sandbox_html.py
```

Note: the MCP file tool currently blocks direct creation of `.html` files, so this slice commits a deterministic Python generator instead of the generated HTML file.

## Servicio 1 scope

Allowed:

```text
SANDBOX_REHEARSAL_ONLY
local browser XLSX reading
preview of sheets
owner answers
operator notes
TXT export
human review input
```

Blocked:

```text
real-client production claim
server upload
backend API call
OCR
Mercado Pago
Servicio 2
autonomous chatbot
diagnosis
final accounting result
final tax/fiscal result
final reconciliation
```

## Safety copy embedded in UI

The generated page declares:

```text
SANDBOX · NO PRODUCCIÓN · REVISIÓN HUMANA
```

It also states:

```text
No envía archivos a un servidor.
No diagnostica.
No concilia.
No produce resultados contables finales.
```

Before enabling file selection, it requires two confirmations:

```text
Confirmo que no usaré datos reales sensibles.
Entiendo que esto es sandbox y no producción.
```

## Export format

The TXT export starts with:

```text
PYMIA_SERVICIO_1_XLSX_SANDBOX_OWNER_ANSWERS_V1
```

and includes:

```text
created_at
environment: SANDBOX_REHEARSAL_ONLY
runtime_authorized: false
production_allowed: false
human_review_required: true
real_client_claim: false
file context
owner answers
operator notes
limitations
```

## Why this is useful

This creates the first usable online rehearsal surface for Servicio 1 without opening runtime risk.

It can be used to test:

```text
- whether users understand the sandbox limitation
- whether XLSX preview is enough to guide owner questions
- what evidence owners can describe
- what columns generate confusion
- what operator notes are needed before a real Service 1 route
```

## What it does not yet connect to

It does not yet consume:

```text
service_1_web_test_route_registry_v1.py
service_1_web_test_run_spec_v1.py
service_1_web_test_review_checklist_v1.py
```

The next interface hardening step should connect the UI copy to the route registry and run spec.

## Tests

The test file verifies:

```text
- safety boundaries are present
- SheetJS is used
- preview functions exist
- tabs exist
- owner questions exist
- TXT export marker exists
- sensitive real data copy is blocked
- no backend /api/curate endpoint remains
- no Servicio 2 or Mercado Pago API claim appears
- generator writes the expected HTML
```

## Recommended next slice

```text
SERVICE_1_WEB_TEST_INTERFACE_REVIEW_CHECKLIST_V1
```

Then:

```text
SERVICE_1_XLSX_BROWSER_SANDBOX_ROUTE_BINDING_V1
```

Purpose:

```text
Bind the browser sandbox copy/options to the allowed route registry and run spec.
```

## Closeout verdict

```text
SERVICE_1_XLSX_BROWSER_SANDBOX_LANDING_V1:
IMPLEMENTED_CANDIDATE

USAGE:
Generate landing/servicio1-sandbox.html locally and publish only as private/internal sandbox.
```
