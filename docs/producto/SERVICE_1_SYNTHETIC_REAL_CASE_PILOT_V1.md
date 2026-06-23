# SERVICE_1_SYNTHETIC_REAL_CASE_PILOT_V1

## Status

```text
IMPLEMENTED_AND_TESTED_SYNTHETIC_CASE
```

## Purpose

Run a synthetic real-case rehearsal for Servicio 1 without real client data.

This is not a commercial launch and not a real-client case. It is a synthetic pilot that exercises the current delivery chain with plausible PyME data.

## Module

```text
PymIA-Live/pymia/smartpyme/service_1_synthetic_real_case_pilot_v1.py
```

## Test module

```text
PymIA-Live/tests/smartpyme/test_service_1_synthetic_real_case_pilot_v1.py
```

## Chain exercised

```text
operator harness sample case
-> service_1_pipeline_v1
-> first aid tools
-> XLSX delivery
-> operator delivery package
-> microservice activation
-> case folder manifest contract
-> delivery manifest audit contract
-> operator harness v2 contract
-> final delivery decision
```

## Synthetic case

```text
Business: comercio minorista alimentos
Scope: First Aid + XLSX operational draft delivery
Data: declared synthetic values
Real client data: false
Runtime authorized: false
Human review: required
```

## Outputs generated in temp test folder

```text
First Aid XLSX files
summary.txt
operator_report.txt
README_ENTREGA.md
manifest.json
```

## Safety assertions

```text
synthetic_data == true
real_client_data == false
runtime_authorized == false
activation allowed only for xlsx_delivery operational draft
case manifest READY_FOR_QA
delivery audit PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW
operator harness v2 READY_FOR_OPERATIONAL_DRAFT_DELIVERY
claims remain conservative
no chatbot
no LLM
no OCR
no parser
no APIs
no Servicio 2
no final reconciliation
```

## Non-goals

```text
No real client execution
No production runtime authorization
No accounting final result
No bank reconciliation final result
No Mercado Pago API
No fiscal validation
No autonomous conversation
```

## Contract status

```text
READY_FOR_REVIEW_BEFORE_NEXT_FUNCTIONAL_CAPABILITY_SLICE
```
