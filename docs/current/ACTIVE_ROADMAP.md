# Active Roadmap

## STATUS

```text
POST_A_TO_I_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL
```

## Current active front

```text
SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_MODEL_V1
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
→ synthetic controlled case instance
→ synthetic controlled case run preparation
→ synthetic supervised run request model
→ synthetic blocked variants
→ pre-run gate closeout
→ execution candidate alignment
→ full chain dry binding
→ synthetic controlled case phase closeout
→ synthetic controlled case candidate model + tests
```

## Methodological correction

For this stage:

```text
controlled case = synthetic, well-enunciated, operationally plausible case
```

No external client is required to advance methodology.

## Anti-micro-slice rule

```text
Do not split candidate model, focal tests, and Phase I regression into separate micro-fronts unless a concrete contradiction appears.
```

## Explicitly not active

```text
PHASE_J_ALLOWED_NOW: NO
RUNTIME_REAL_ALLOWED_NOW: NO
CLI_EXECUTION_ALLOWED_NOW: NO
BUSINESS_FILES_ALLOWED_NOW: NO
DATA_PROCESSING_ALLOWED_NOW: NO
ARTIFACT_GENERATION_ALLOWED_NOW: NO
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
Synthetic controlled case ≠ external client case.
Full chain dry binding ≠ actual run.
Candidate model ready ≠ CLI executed.
Tests passing ≠ runtime authorized.
```

## Current front result

The synthetic controlled case documentation phase has been converted into a pure Python candidate model with tests.

Validated:

```text
Focal: 22/22 passed
Regression: 101/101 passed
```

It does not authorize:

```text
- business file intake
- CLI execution
- runtime execution
- data processing
- artifact generation
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
A. SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CANDIDATE_CHAIN_COMPOSITION_V1
   - pure candidate composition only
   - no CLI execution
   - no runtime

B. SERVICE_1_SYNTHETIC_CONTROLLED_CASE_CODE_FRONT_CLOSEOUT_V1
   - docs closeout only

C. STOP_AND_DECIDE
```

No future roadmap document overrides this active gate unless explicitly updated after review.
