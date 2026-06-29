# S1_FIRST_REAL_CLIENT_PILOT_INTAKE_PACKET_V1

## VERDICT

```text
S1_FIRST_REAL_CLIENT_PILOT_INTAKE_PACKET_V1: CREATED
```

## BASELINE

```text
S1_FULL_ASSISTED_V1: CLOSED_WITH_LIMITS
S1_FULL_ASSISTED_V1_HARDENING: CLOSED_WITH_SCOPE_NOTE
S1_REAL_CLIENT_PILOT_READINESS_AUDIT_V1: PASS_WITH_OPERATOR_SUPERVISION
S1_FIRST_REAL_CLIENT_PILOT_PROTOCOL_V1: CREATED
```

This packet is the intake gate for the first controlled real-client pilot. It does not authorize production, autonomous delivery, or commercial launch.

## PURPOSE

```text
Collect the minimum case information required before running Servicio 1 on real-client data.
```

If this packet is incomplete, the operator must not run the canonical CLI.

## PILOT LIMITS

```text
one_client_case_only: true
one_explicit_question_only: true
one_supported_family_only: true
xlsx_only: true
operator_supervision_required: true
human_review_required: true
runtime_authorized: false
autonomous_use_authorized: false
production_claim_allowed: false
```

## CLIENT / CASE DATA

```text
case_alias:
client_alias:
business_type:
operator_name:
human_reviewer_name:
intake_date:
period_under_review:
```

Do not record sensitive client identifiers in repo-tracked documents.

## OWNER QUESTION

The owner must express one operational question.

```text
owner_question:
```

Accepted examples:

```text
- Quiero revisar precios, costos y margen de esta planilla.
- Quiero ordenar caja diaria con ingresos y egresos declarados.
- Quiero ordenar gastos por concepto/categoría e importe.
- Quiero revisar variaciones visibles de precios de proveedores.
- Quiero una alerta básica de stock sobre valores declarados.
```

If the owner asks for more than one question, reduce scope to one question before running.

## SELECTED FAMILY

The operator must select exactly one family before running.

```text
selected_family:
```

Allowed values:

```text
precio_margen_basico
caja_diaria_triage
gastos_triage
proveedores_precio_variacion_triage
stock_alertas_basicas
```

If no allowed family fits, block the pilot.

## INPUT FILE REQUIREMENTS

```text
input_file_type: XLSX
input_file_location: outside_repo
input_file_name_only:
file_received_by:
file_received_date:
```

Pre-run file checks:

```text
[ ] File is XLSX.
[ ] File is stored outside repo.
[ ] File belongs to the identified case.
[ ] File corresponds to the declared period or scope.
[ ] File does not contain unnecessary sensitive data for the selected question.
[ ] No PDFs, images, scans, credentials, tokens, API keys, fiscal keys or live access were received.
```

## MINIMUM COLUMN EXPECTATIONS BY FAMILY

These are not final mappings. They are intake expectations before CLI/column confirmation.

```text
precio_margen_basico:
- price/sale amount column candidate
- cost column candidate

caja_diaria_triage:
- opening balance or declared starting amount
- income/inflow column candidate
- expense/outflow column candidate

gastos_triage:
- concept/description column candidate
- amount column candidate
- optional category column candidate

proveedores_precio_variacion_triage:
- supplier column candidate
- product/input column candidate
- price/cost column candidate

stock_alertas_basicas:
- product/SKU column candidate
- current stock column candidate
- minimum stock column candidate
- optional average daily sales candidate
```

If the workbook does not plausibly contain the minimum evidence for the selected family, block or ask for a better XLSX before running.

## EXCLUSIONS CONFIRMATION

The operator must confirm all exclusions before running:

```text
[ ] The client is not asking for audit.
[ ] The client is not asking for tax/fiscal validation.
[ ] The client is not asking for final accounting result.
[ ] The client is not asking for definitive bank reconciliation.
[ ] The client is not asking for automatic journal entries.
[ ] The client is not asking for OCR/PDF/image parsing.
[ ] The client is not asking for API connection.
[ ] The client is not asking for autonomous chatbot/client resolution.
[ ] The client understands this is an operational draft under human review.
```

If any checkbox fails, block or reduce scope.

## OPERATIONAL CONSENT

The operator must record explicit operational consent in safe language:

```text
The client understands that Servicio 1 will produce an operational draft from declared spreadsheet data, not an audit, certification, fiscal validation, final accounting result, or autonomous decision.

consent_recorded: yes/no
consent_recorded_by:
consent_date:
```

If `consent_recorded` is not `yes`, do not run.

## TOOL REQUEST PREPARATION

The operator prepares `tool_requests.json` outside the repo after selecting the family and reading the available columns/data.

Required rule:

```text
No tool request may be generated from invented values.
All inputs must come from declared spreadsheet data or explicit owner confirmation.
```

Tool request file path:

```text
tool_requests_path_outside_repo:
```

## PRE-RUN GO / NO-GO

Run only if all are true:

```text
[ ] Intake packet complete.
[ ] One question selected.
[ ] One supported family selected.
[ ] XLSX file available outside repo.
[ ] Human reviewer identified.
[ ] Consent recorded.
[ ] Stop conditions absent.
[ ] tool_requests.json prepared outside repo when tools will run.
```

Decision:

```text
pre_run_decision: GO / BLOCKED
blocked_reason:
```

## CANONICAL RUN COMMAND

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\PymIA-Live
python -m pymia.cli.service_1_operator --file "E:\RUTA_EXTERNA_CLIENTE\archivo_cliente.xlsx" --run-tools "E:\RUTA_EXTERNA_CLIENTE\tool_requests.json"
```

Do not run from files committed to the repository.

## REQUIRED STOP POINT AFTER RUN

The first real-client pilot must stop at:

```text
final_qa_delivery_gate.status = PASS
final_qa_delivery_gate.delivery_status = READY_FOR_HUMAN_REVIEW
human_review_gate.status = PENDING_HUMAN_REVIEW
runtime_authorized = false
```

If this state is not reached, do not deliver anything to the client.

## INTAKE RECORD TEMPLATE

Use this private template outside client-sensitive repo context:

```text
case_alias:
client_alias:
business_type:
operator_name:
human_reviewer_name:
intake_date:
period_under_review:
owner_question:
selected_family:
input_file_name_only:
input_file_location_outside_repo:
tool_requests_path_outside_repo:
consent_recorded:
pre_run_decision:
blocked_reason:
next_safe_action:
```

## FINAL POSITION

```text
READY_TO_INTAKE_FIRST_CONTROLLED_REAL_CLIENT_PILOT
```

This packet authorizes intake preparation only. Runtime remains governed by `S1_FIRST_REAL_CLIENT_PILOT_PROTOCOL_V1` and must stop before client delivery until human review is completed.
