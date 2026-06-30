# Active Roadmap

## STATUS

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_MILESTONE_OPEN
```

## Current active front

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_MILESTONE_V1
```

## Closed Phase I baseline

Servicio 1 / SmartPyme Phase I is closed as a candidate/supervised system.

Closed Phase I chain:

```text
readiness
→ evidence packet
→ operator supervision
→ controlled execution candidate
→ supervised CLI run result candidate
→ abort/rollback result candidate
→ controlled delivery review candidate
→ full chain composition
→ Phase I closeout
```

## Reconciliation preserved

```text
PHASE_I: CLOSED
POST_I_HARDENING: CLOSED
ROADMAP_RECONCILED: YES
```

Phase I is not reopened by the XLSX runtime bridge milestone.

## Terminology correction

Use this term going forward:

```text
CONTROLLED_OPERATIONAL_CASE
```

Do not split valid development cases into lower-value categories such as "real" versus "synthetic".

The relevant boundary is now:

```text
controlled operational case
vs
controlled XLSX execution bridge
```

## Milestone now open

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_MILESTONE: OPEN
```

Goal:

```text
candidate / supervised model
→ controlled XLSX execution bridge
```

## Existing XLSX assets to reuse

```text
PymIA-Live/pymia/smartpyme/service_1_xlsx_to_normalized_table_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_structure_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_delivery_v1.py
PymIA-Live/pymia/smartpyme/first_aid_xlsx_delivery_v1.py
```

Rule:

```text
Do not duplicate XLSX parsing.
Use the existing XLSX reader/normalizer boundary.
```

## Finite milestone units

Only these units are allowed:

```text
1. SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT_V1
2. SERVICE_1_XLSX_RUNTIME_BRIDGE_ENTRYPOINT_V1
3. SERVICE_1_XLSX_RUNTIME_BRIDGE_CLOSEOUT_V1
```

Maximum units:

```text
3
```

If a fourth unit seems necessary:

```text
STOP_AND_RECONCILE
```

## Explicitly not active

```text
PHASE_I_REOPENED: NO
PHASE_J_ALLOWED_NOW: NO
SAAS_API_UI_ALLOWED_NOW: NO
SERVICE_2_ALLOWED_NOW: NO
PRODUCTIVE_RUNTIME_ALLOWED_NOW: NO
AUTONOMOUS_DELIVERY_ALLOWED_NOW: NO
OWNER_DELIVERY_ALLOWED_NOW: NO
PUBLISH_ALLOWED_NOW: NO
NOTIFICATION_ALLOWED_NOW: NO
WORKER_STORAGE_QUEUE_ALLOWED_NOW: NO
EXTERNAL_API_ALLOWED_NOW: NO
OCR_PDF_PARSER_ALLOWED_NOW: NO
```

## Current rule

```text
Phase I closed ≠ Service 1 complete.
Controlled operational case ≠ controlled XLSX execution bridge.
Bridge contract ready ≠ autonomous runtime.
Entry point ready ≠ owner delivery.
Tests passing ≠ SaaS/API/UI authorization.
```

## Current front result

The XLSX runtime bridge milestone is opened as the next finite Service 1 completion front.

It does not authorize:

```text
- SaaS/API/UI
- chatbot
- autonomous owner delivery
- publish
- notification
- worker/storage/queue
- external API integration
- Servicio 2
- Phase J
```

## Next decision gate

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT_V1
```

No future roadmap document may add extra units to this milestone without explicit reconciliation.
