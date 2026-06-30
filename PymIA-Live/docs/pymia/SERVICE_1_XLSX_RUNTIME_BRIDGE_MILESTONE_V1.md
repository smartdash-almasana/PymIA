# SERVICE 1 — XLSX RUNTIME BRIDGE MILESTONE V1

## VERDICT

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_MILESTONE_OPENED
```

## Purpose

Open the next finite milestone after Phase I closeout.

This milestone exists to progress toward Servicio 1 completion by crossing the next real engineering boundary:

```text
candidate / supervised model
→ controlled XLSX execution bridge
```

This is not a new Phase I microcycle.
This is not Phase J.
This is not Servicio 2.
This is not SaaS/API/UI.

## Terminology correction

For PymIA development, do not split controlled cases into lower-value categories such as "real" versus "synthetic".

Correct operational term:

```text
CONTROLLED_OPERATIONAL_CASE
```

A well-enunciated constructed case is operationally valid for development when it has:

```text
- business scenario
- declared inputs
- expected columns
- known gaps
- operator boundary
- abort conditions
- testable outcome
```

The remaining distinction is not case reality.

The remaining distinction is:

```text
controlled operational case
vs
controlled XLSX execution bridge
```

## Prior phase status

```text
PHASE_I: CLOSED
POST_I_HARDENING: CLOSED
ROADMAP_RECONCILED: YES
NEXT_GATE_WAS: STOP_AND_DECIDE
```

This document consumes that decision gate and opens the next macrofront outside Phase I.

## Existing assets recognized

The repo already contains XLSX-capable Service 1 components that must be reused instead of reimplemented:

```text
PymIA-Live/pymia/smartpyme/service_1_xlsx_to_normalized_table_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_structure_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_delivery_v1.py
PymIA-Live/pymia/smartpyme/first_aid_xlsx_delivery_v1.py
```

Known principle:

```text
Do not duplicate XLSX parsing.
Use the existing XLSX reader/normalizer boundary.
```

## Milestone definition

The milestone is complete when Servicio 1 has an official controlled XLSX bridge that can:

```text
1. accept a controlled XLSX fixture or controlled operational case file path;
2. read XLSX through existing Service 1 XLSX boundaries;
3. produce a normalized/control packet suitable for Service 1 operator review;
4. expose a deterministic CLI or callable entrypoint;
5. return blocked results instead of crashing on invalid input;
6. preserve explicit non-autonomous delivery boundaries;
7. prove behavior with focal tests and an acotada regression.
```

## Finite work units

This milestone may contain only these work units:

```text
1. SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT_V1
   - pure bridge contract + tests
   - uses existing XLSX reader/normalizer
   - no autonomous delivery

2. SERVICE_1_XLSX_RUNTIME_BRIDGE_ENTRYPOINT_V1
   - controlled CLI/callable entrypoint + tests
   - no SaaS/API/UI
   - no Servicio 2

3. SERVICE_1_XLSX_RUNTIME_BRIDGE_CLOSEOUT_V1
   - closeout only
   - verifies milestone DoD
```

No additional micro-slices are allowed unless a concrete contradiction is found.

## In scope

```text
- controlled XLSX fixture/case processing
- Service 1 XLSX structure reading
- Service 1 normalized table output
- deterministic bridge packet
- blocked result semantics
- operator-reviewable manifest
- focal tests
- acotada regression
```

## Out of scope

```text
- SaaS/API/UI
- chatbot
- autonomous owner delivery
- publish/notification
- worker/storage/queue
- Servicio 2
- Phase J
- tax conclusion
- final accounting conclusion
- external bank/API integrations
- OCR/PDF parser
- new XLSX parser duplication
```

## Runtime boundary

This milestone may authorize controlled local XLSX bridge execution only after the contract and tests define it.

It still does not authorize:

```text
- autonomous delivery
- production runtime
- external integrations
- owner publish/notification
- Servicio 2
- Phase J
```

## DoD

The milestone is done only if:

```text
- official bridge module exists
- official bridge tests pass
- official entrypoint exists if needed
- entrypoint tests pass if created
- invalid XLSX paths block safely
- non-XLSX inputs block safely
- malformed workbooks block safely
- normalized output is deterministic
- operator manifest is explicit
- no duplicate parser exists
- no SaaS/API/UI introduced
- no Servicio 2 introduced
- no Phase J introduced
- roadmap closes the milestone
```

## Anti-infinite rule

```text
Maximum units for this milestone: 3.
If unit 3 closes, STOP_AND_DECIDE.
If a fourth unit seems necessary, stop and reconcile before creating it.
```

## Current milestone status

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_MILESTONE: OPEN
PHASE_I_REOPENED: FALSE
CONTROLLED_OPERATIONAL_CASE_TERMINOLOGY: ACTIVE
NEXT_ALLOWED_UNIT: SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT_V1
MICROCYCLES_ALLOWED: FALSE
```

## Final declaration

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_MILESTONE_V1: PASS
MILESTONE_OPENED: YES
PHASE_I_REOPENED: FALSE
NEXT_UNIT: SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT_V1
SERVICE_2_OPENED: FALSE
PHASE_J_OPENED: FALSE
SAAS_API_UI_OPENED: FALSE
AUTONOMOUS_DELIVERY_OPENED: FALSE
```
