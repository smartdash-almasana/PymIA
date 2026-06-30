# Active Roadmap

## STATUS

```text
POST_A_TO_I_PRE_OPERATOR_PACKET_GATE
```

## Current active front

```text
SERVICE_1_REAL_CONTROLLED_CASE_PRECHECK_GATE_V1
```

## Closed baseline

Servicio 1 / SmartPyme A→I is closed as a candidate/supervised system.

Closed chain:

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
→ doc drift and naming cleanup
```

## Explicitly not active

```text
PHASE_J_ALLOWED_NOW: NO
RUNTIME_REAL_ALLOWED_NOW: NO
CLI_EXECUTION_ALLOWED_NOW: NO
SAAS_API_UI_ALLOWED_NOW: NO
SERVICE_2_ALLOWED_NOW: NO
PRODUCTIVE_RUNTIME_ALLOWED_NOW: NO
AUTONOMOUS_DELIVERY_ALLOWED_NOW: NO
OWNER_DELIVERY_ALLOWED_NOW: NO
```

## Current rule

```text
Candidate complete ≠ runtime real.
Authorized ≠ executed.
Review candidate ≠ delivery real.
Run result candidate ≠ CLI executed.
Precheck gate defined ≠ operator packet created.
Operator packet created ≠ CLI executed.
```

## Current gate purpose

The current front only defines the conditions required before preparing an operator packet for a real controlled case.

It does not authorize:

```text
- raw client data intake
- CLI execution
- runtime execution
- owner delivery
- publish
- notification
- SaaS/API/UI
- worker/storage/queue
- Servicio 2
- Phase J
```

## Next decision gate

If and only if `SERVICE_1_REAL_CONTROLLED_CASE_PRECHECK_GATE_V1` is accepted as READY, the next allowed front may be:

```text
SERVICE_1_OPERATOR_PACKET_FOR_REAL_CONTROLLED_CASE_V1
```

Otherwise choose explicitly between:

```text
A. Reduce scope / define missing precheck inputs
B. Additional docs cleanup / anti-deriva
C. STOP_AND_DECIDE
```

No future roadmap document overrides this active gate unless explicitly updated after review.
