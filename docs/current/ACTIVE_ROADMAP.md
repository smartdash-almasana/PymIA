# Active Roadmap

## STATUS

```text
POST_A_TO_I_SYNTHETIC_OPERATOR_PACKET_REHEARSAL
```

## Current active front

```text
SERVICE_1_SYNTHETIC_OPERATOR_PACKET_REHEARSAL_V1
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
→ operator packet template
→ operator packet template acceptance audit
→ synthetic operator packet rehearsal
```

## Explicitly not active

```text
PHASE_J_ALLOWED_NOW: NO
RUNTIME_REAL_ALLOWED_NOW: NO
CLI_EXECUTION_ALLOWED_NOW: NO
BUSINESS_FILES_ALLOWED_NOW: NO
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
Operator packet template ≠ case instance.
Synthetic rehearsal ≠ case instance.
Synthetic checklist pass ≠ CLI executed.
```

## Current front result

The synthetic operator packet rehearsal validates the packet template with synthetic placeholders only.

It does not authorize:

```text
- case instance
- business file intake
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

Choose explicitly between:

```text
A. SERVICE_1_OPERATOR_PACKET_CASE_INSTANCE_V1
   - only with explicit case approval
   - still no CLI execution by implication

B. SERVICE_1_SYNTHETIC_OPERATOR_PACKET_REHEARSAL_HARDENING_V1
   - more synthetic negative cases
   - still no business files

C. STOP_AND_DECIDE
```

No future roadmap document overrides this active gate unless explicitly updated after review.
