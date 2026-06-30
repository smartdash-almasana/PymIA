# Active Roadmap

## STATUS

```text
POST_A_TO_I_OPERATOR_PACKET_TEMPLATE
```

## Current active front

```text
SERVICE_1_OPERATOR_PACKET_FOR_REAL_CONTROLLED_CASE_V1
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
→ real controlled case precheck gate
```

## Explicitly not active

```text
PHASE_J_ALLOWED_NOW: NO
RUNTIME_REAL_ALLOWED_NOW: NO
CLI_EXECUTION_ALLOWED_NOW: NO
RAW_CLIENT_DATA_ALLOWED_NOW: NO
SAAS_API_UI_ALLOWED_NOW: NO
SERVICE_2_ALLOWED_NOW: NO
PRODUCTIVE_RUNTIME_ALLOWED_NOW: NO
AUTONOMOUS_DELIVERY_ALLOWED_NOW: NO
OWNER_DELIVERY_ALLOWED_NOW: NO
PUBLISH_ALLOWED_NOW: NO
NOTIFICATION_ALLOWED_NOW: NO
WORKER_STORAGE_QUEUE_ALLOWED_NOW: NO
```

## Current rule

```text
Candidate complete ≠ runtime real.
Authorized ≠ executed.
Review candidate ≠ delivery real.
Run result candidate ≠ CLI executed.
Precheck gate defined ≠ operator packet created.
Operator packet template ≠ real case instance.
Operator packet created ≠ CLI executed.
```

## Current front purpose

The current front defines the operator packet template for one future real controlled Service 1 case.

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

If and only if `SERVICE_1_OPERATOR_PACKET_FOR_REAL_CONTROLLED_CASE_V1` is accepted as template-defined and a case-specific packet instance is later completed, the next possible front may be:

```text
SERVICE_1_REAL_CONTROLLED_CASE_SUPERVISED_RUN_PREPARATION_V1
```

That future front still must not execute CLI unless separately and explicitly approved.

Otherwise choose explicitly between:

```text
A. Return to precheck gate
B. Reduce scope / define missing packet inputs
C. Additional docs cleanup / anti-deriva
D. STOP_AND_DECIDE
```

No future roadmap document overrides this active gate unless explicitly updated after review.
