# SERVICE_1_WEB_TEST_INTERFACE_DESIGN_V1

## Status

```text
DESIGN_ONLY
```

## Purpose

Design a minimal web interface to test Servicio 1 online as a controlled assisted-service sandbox.

This is not a production runtime, not a chatbot, not Servicio 2, not an API integration, not OCR, and not a real-client delivery claim. The interface exists to let an operator or invited tester exercise the current Servicio 1 routes safely and inspect generated/reviewable artifacts.

## Product intent

The web interface must answer one question:

```text
Can a human operator test Servicio 1 online, select a safe route, understand required inputs, run a sandbox/rehearsal flow, inspect outputs, and avoid forbidden claims?
```

It is not intended to answer:

```text
Can Servicio 1 autonomously solve a real client case online?
```

## Operating doctrine

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
La revisión humana cierra.
```

Web translation:

```text
The UI guides.
The backend only runs allowed sandbox/test routes.
The output is a review packet.
The operator reviews before any client-facing use.
The interface must display limitations before and after execution.
```

## Allowed first version

```text
SERVICE_1_WEB_TEST_INTERFACE_V1
```

Allowed mode:

```text
SANDBOX_REHEARSAL_ONLY
```

Allowed users:

```text
internal_operator
invited_reviewer
founder/admin
```

Allowed data:

```text
synthetic fixtures
manual mock metadata
anonymized files only if explicitly enabled later
```

Blocked data:

```text
real client files by default
sensitive accounting records
bank credentials
Mercado Pago credentials
production API tokens
personal tax data
```

## Scope boundaries

### Allowed routes in V1

```text
1. Excel Treatment Lab sandbox
2. Invoice / Collection Matching sandbox
3. Bank Reconciliation sandbox
4. Accounting Workpaper draft sandbox
5. First Aid synthetic delivery rehearsal
```

### Blocked routes in V1

```text
Mercado Pago reconciliation
real bank reconciliation
real invoice ingestion
OCR ingestion
API ingestion
chatbot autonomous resolution
Servicio 2 diagnosis
final accounting/tax/fiscal conclusion
```

## Interface structure

```text
/login-or-access-gate
/service-1/dashboard
/service-1/new-test-run
/service-1/route/:route_id
/service-1/run/:run_id
/service-1/run/:run_id/artifacts
/service-1/run/:run_id/review
/service-1/run/:run_id/export
```

## Main screens

### 1. Access gate

Purpose:

```text
Prevent casual users from treating the sandbox as a production service.
```

Required UI copy:

```text
Servicio 1 Web Test Interface
Modo: sandbox/rehearsal
No subas datos reales ni sensibles.
Los outputs son borradores revisables, no conclusiones finales.
```

Required controls:

```text
[ ] Confirmo que no subiré datos reales ni sensibles.
[ ] Entiendo que los resultados no son finales ni certificados.
[Continue to sandbox]
```

Blocked until both confirmations are checked.

### 2. Dashboard

Purpose:

```text
Show current maturity and available sandbox routes.
```

Cards:

```text
Excel Treatment Lab Sandbox
Invoice / Collection Matching Sandbox
Bank Reconciliation Sandbox
Accounting Workpaper Draft Sandbox
First Aid Synthetic Delivery Rehearsal
```

Each card must show:

```text
status
maturity
allowed_data
forbidden_claims
last_test_evidence
```

Example card:

```text
Excel Treatment Lab Sandbox
Status: READY_FOR_SANDBOX_REHEARSAL
Maturity: ~82%
Allowed data: synthetic metadata only
Output: XLSX review packet + owner summary + operator notes
Blocked: real workbook normalization claim
```

### 3. New test run

Purpose:

```text
Create a controlled test run with explicit route and data mode.
```

Fields:

```text
route_id
case_label
data_mode
operator_name
reviewer_role
notes
```

Allowed data_mode values:

```text
SYNTHETIC_FIXTURE
MANUAL_METADATA
ANONYMIZED_REHEARSAL_CANDIDATE
```

Default:

```text
SYNTHETIC_FIXTURE
```

Blocked in V1 unless explicitly enabled:

```text
REAL_CLIENT_DATA
```

### 4. Route screen

Purpose:

```text
Explain what the selected route does and does not do before execution.
```

Sections:

```text
What this route tests
Required inputs
Generated outputs
Human review checklist
Forbidden claims
Run button
```

The run button label must be conservative:

```text
Run sandbox rehearsal
```

Do not use:

```text
Solve case
Generate final result
Reconcile now
Normalize client file
Diagnose company
```

### 5. Run execution screen

Purpose:

```text
Show deterministic execution status without implying autonomy.
```

State machine:

```text
CREATED
INPUT_CONFIRMED
SANDBOX_ROUTE_SELECTED
RUNNING_ALLOWED_TOOL
ARTIFACTS_GENERATED
OPERATOR_REVIEW_REQUIRED
CLOSED_BY_OPERATOR
BLOCKED
```

Displayed status must include:

```text
runtime_authorized=false
production_allowed=false
human_review_required=true
```

### 6. Artifacts screen

Purpose:

```text
Show downloadable reviewable outputs.
```

Artifact table columns:

```text
artifact_name
artifact_type
route_id
created_at
sha256
review_status
download_link
```

Allowed artifact types:

```text
xlsx_review_packet
owner_summary_txt
operator_notes_txt
manifest_json
readme_md
```

Each artifact must show:

```text
This artifact is a review draft. It is not a final accounting, tax, fiscal, or diagnostic conclusion.
```

### 7. Review screen

Purpose:

```text
Force human review before any test run is marked closed.
```

Checklist:

```text
[ ] Output files open correctly.
[ ] Owner summary is conservative.
[ ] Operator notes describe limits.
[ ] Forbidden claims are absent.
[ ] runtime_authorized=false.
[ ] production_allowed=false.
[ ] No real-client claim is made.
[ ] Human reviewer accepts sandbox result.
```

Final actions:

```text
Close as sandbox rehearsal
Block run
Request more evidence
```

There must be no action named:

```text
Approve final delivery
Approve accounting result
Approve tax result
Approve diagnosis
```

## Route-specific designs

### Route A — Excel Treatment Lab Sandbox

Route ID:

```text
excel_treatment_lab_sandbox
```

Underlying current slice:

```text
run_excel_treatment_lab_completion_slice_v1
```

Inputs in V1:

```text
source_file_ref: synthetic label only
columns_detected: declared metadata
columns_confirmed: declared metadata
rows_processed: declared count
```

Output files:

```text
excel_treatment_lab_review_packet.xlsx
owner_summary_excel_treatment_lab.txt
operator_notes_excel_treatment_lab.txt
```

UI preview:

```text
Detected columns: 5
Confirmed columns: 5
Pending confirmation: 0
Exceland bridge: OK
Final status: READY
```

Forbidden claims:

```text
No confirma archivo cliente normalizado.
No ejecuta fórmulas.
No procesa workbook real.
No reemplaza revisión humana.
```

### Route B — Invoice / Collection Matching Sandbox

Route ID:

```text
invoice_collection_matching_sandbox
```

Underlying current slice:

```text
run_invoice_collection_matching_sandbox_completion_slice_v1
```

Output files:

```text
invoice_collection_matching_sandbox_review_packet.xlsx
owner_summary_invoice_collection_matching_sandbox.txt
operator_notes_invoice_collection_matching_sandbox.txt
```

UI preview:

```text
Matched by invoice number: 1
Pending collection: 2
Unmatched collection: 1
Amount difference review: 1
Final status: READY
```

Forbidden claims:

```text
No confirma deuda final.
No confirma cobranza aplicada definitiva.
No certifica saldo de cliente.
No genera asientos.
```

### Route C — Bank Reconciliation Sandbox

Route ID:

```text
bank_reconciliation_sandbox
```

Underlying current slice:

```text
run_bank_reconciliation_sandbox_completion_slice_v1
```

Output files:

```text
bank_reconciliation_sandbox_review_packet.xlsx
owner_summary_bank_reconciliation_sandbox.txt
operator_notes_bank_reconciliation_sandbox.txt
```

Forbidden claims:

```text
No confirma saldo conciliado.
No confirma diferencia final.
No usa API bancaria.
No lee extractos reales.
```

### Route D — Accounting Workpaper Draft Sandbox

Route ID:

```text
accounting_workpaper_draft_sandbox
```

Underlying current slice:

```text
run_accounting_workpaper_completion_slice_v1
```

Output files:

```text
accounting_workpaper_draft_packet.xlsx
owner_summary_accounting_workpaper.txt
operator_notes_accounting_workpaper.txt
```

Forbidden claims:

```text
No confirma papel de trabajo final.
No certifica evidencia contable.
No genera asiento.
No reemplaza contador.
```

### Route E — First Aid Synthetic Delivery Rehearsal

Route ID:

```text
first_aid_synthetic_delivery_rehearsal
```

Underlying current slice:

```text
run_service_1_synthetic_real_case_pilot_v1
```

Outputs:

```text
First Aid XLSX outputs
summary.txt
operator_report.txt
README_ENTREGA.md
manifest.json
case manifest
delivery audit
operator harness decision
```

Forbidden claims:

```text
No confirma caso real.
No confirma diagnóstico final.
No reemplaza revisión humana.
```

## Minimal visual layout

### Layout principle

```text
Clinical operational interface.
Dense but calm.
No marketing-first landing.
No flashy SaaS dashboard.
No chatbot-centered design.
```

### Visual hierarchy

```text
Left sidebar: routes and evidence
Top bar: environment badge + current run status
Main panel: route/run/artifacts/review
Right panel: limitations + forbidden claims
```

### Environment badge

Always visible:

```text
SANDBOX MODE
runtime_authorized=false
production_allowed=false
human_review_required=true
```

### Color semantics

```text
Green: test passed / artifact generated
Yellow: human review required
Red: blocked / forbidden claim
Blue/neutral: informational sandbox state
```

No celebratory completion language.

## Data model

### TestRun

```text
run_id
created_at
route_id
case_label
data_mode
operator_name
status
runtime_authorized
production_allowed
human_review_required
output_dir
artifacts
review_decision
review_notes
```

### Artifact

```text
artifact_id
run_id
artifact_name
artifact_type
file_path
sha256
created_at
review_status
```

### ReviewDecision

```text
run_id
reviewer_role
decision
checklist
notes
created_at
```

Allowed review decisions:

```text
CLOSE_SANDBOX_REHEARSAL
BLOCK_RUN
REQUEST_MORE_EVIDENCE
```

## Minimal implementation architecture

### Recommended local-first implementation

```text
Static frontend + thin local command runner + artifact folder browser
```

Preferred first implementation:

```text
No public production deployment.
No authentication complexity at first.
No persistent database unless needed.
No upload of real files.
No cloud storage.
```

Suggested technical shape:

```text
Frontend:
- simple React/Vite or plain HTML static prototype

Backend adapter:
- thin Python CLI wrapper around existing run_*_completion_slice_v1 functions
- writes artifacts to local/sandbox output folder
- returns JSON manifest to frontend

Storage:
- local .tmp/service_1_web_test_runs/<run_id>/
```

Do not use this interface to add:

```text
LLM runtime
OCR runtime
Mercado Pago API
bank API
client upload production flow
Servicio 2 router
```

## First online deployment mode

If online access is required, use:

```text
PRIVATE_DEMO_DEPLOYMENT
```

Allowed deployment constraints:

```text
password-protected
sandbox-only
synthetic routes only
no real uploads
temporary artifacts
manual cleanup
clear disclaimers
```

Recommended environment label:

```text
PymIA Servicio 1 — Sandbox Online
```

Not allowed environment label:

```text
PymIA Servicio 1 Production
```

## Acceptance criteria for V1 interface

The interface is acceptable when:

```text
[ ] Operator can create a sandbox test run.
[ ] Operator can select one of the allowed routes.
[ ] Route limitations are visible before execution.
[ ] Run produces expected artifacts.
[ ] Artifact hashes are visible.
[ ] Owner summary and operator notes are viewable/downloadable.
[ ] Human review checklist blocks final close until completed.
[ ] Forbidden claims are visible.
[ ] No real-client production claim appears anywhere.
[ ] No unsupported route is executable.
```

## Tests needed for implementation later

When this moves from design to code, add tests for:

```text
route registry exposes only allowed sandbox routes
real_client_data mode blocked by default
unsupported route blocked
run creates artifact directory
run returns artifact metadata and hashes
review checklist required before close
forbidden claims rendered for each route
no Mercado Pago route exposed
no Servicio 2 route exposed
```

## No-go list

```text
No public production launch.
No client uploads by default.
No real accounting claims.
No final reconciliation claims.
No final diagnosis claims.
No tax/fiscal claims.
No autonomous chat.
No API integrations.
No OCR.
No Mercado Pago.
No Servicio 2.
```

## Recommended next implementation slice

```text
SERVICE_1_WEB_TEST_INTERFACE_ROUTE_REGISTRY_V1
```

Purpose:

```text
Create a pure deterministic registry of allowed web-test routes with labels, descriptions, forbidden claims, output names, and linked runner function names.
```

Reason:

```text
Before building UI, the web interface needs a safe route registry so the frontend cannot accidentally expose blocked capabilities.
```

Expected maturity impact:

```text
Real-client readiness: no direct increase.
Operator rehearsal readiness: moderate increase.
Online demo readiness: high increase.
```

## Closeout verdict

```text
SERVICE_1_WEB_TEST_INTERFACE_DESIGN_V1:
READY_FOR_REVIEW

NEXT_SAFE_STEP:
SERVICE_1_WEB_TEST_INTERFACE_ROUTE_REGISTRY_V1
```
