# SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1

## STATUS

```text
DEPLOYMENT_TARGET: GOOGLE_CLOUD_RUN
SERVICE: pymia-service1
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
LAST_CERTIFIED_DEPLOYED_GIT_SHA: d2c9c24
LAST_CERTIFIED_CLOUD_RUN_REVISION: pymia-service1-00008-mtf
LAST_CERTIFIED_TRAFFIC: 100%
RC3_COMMIT: 07f1f9b85591f99dc72d94271b117dfcb6ef6582
TENANT_REENTRY_HARDENING_COMMIT: c9de7497a9e61cfa575975a4c5f5d9815c4855de
CURRENT_RC_DEPLOYED_SHA: NOT_PROVEN
RUNTIME_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
CURRENT_RC_WEB_ENTRYPOINT: python -m pymia.smartpyme.service_1_semantic_reception_server_v1
```

## PURPOSE

Define the minimum deployment facts and evidence required for Servicio 1 production certification.

This contract does not authorize a second product root, a new runtime authority, a new parser, or a new capability.

## REQUIRED DEPLOYMENT FACTS

The deployed Servicio 1 instance must expose:

```text
PROVIDER_OR_HOST
PUBLIC_HTTPS_BASE_URL
DEPLOYED_GIT_SHA
BOOT_COMMAND
HEALTH_ENDPOINT=GET / (Cloud Run) | GET /healthz (local)
LOG_TARGET
RESTART_OR_REDEPLOY_COMMAND
ROLLBACK_OR_PREVIOUS_REVISION_MECHANISM
```

No production claim is allowed if these facts are unknown.

## REQUIRED RUNTIME CONFIGURATION

The production process requires:

```text
PYMIA_SUPABASE_URL
PYMIA_SUPABASE_PUBLISHABLE_KEY
PYMIA_SUPABASE_SERVICE_ROLE_KEY
```

Values are secrets/configuration and must not be committed.

For RC5, activating the bounded external semantic provider additionally requires environment configuration equivalent to:

```text
GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION
PYMIA_SEMANTIC_LLM_MODEL
```

The model name must not be hardcoded in product code. Absence of this configuration must not grant any new authority to the fallback provider.

The smoke runner additionally reads:

```text
PYMIA_PRODUCTION_BASE_URL
PYMIA_SMOKE_EMAIL
PYMIA_SMOKE_PASSWORD
```

Smoke credentials must not be committed or printed.

## PYTHON PACKAGE REQUIREMENT

Production must install the Supabase runtime dependency because the production entrypoint constructs the Supabase identity resolver and persistence adapter.

Expected install shape:

```text
python -m pip install .
```

or an equivalent deployment-specific package installation that provides the same declared runtime dependency set.

## BOOT CONTRACT

For the current release candidate, the process must execute the semantic-reception entrypoint that wires Supabase identity/persistence and the bounded semantic provider:

```text
python -m pymia.smartpyme.service_1_semantic_reception_server_v1 --host <bind-host> --port <port>
```

This entrypoint still delegates productive analysis to `service_1_product_pipeline_v1.py`. No alternative productive pipeline or web business-computation root is authorized.

## HEALTH CONTRACT

Local/non-Cloud-Run:

```text
GET /healthz
→ HTTP 200
→ {"status":"ok"}
```

Cloud Run:

```text
GET /
→ HTTP 200 with application page
```

The public production URL must use HTTPS.

## IDENTITY CONTRACT

Protected POST operations require:

```text
Authorization: Bearer <Supabase access token>
```

The application validates the JWT through Supabase before accepting identity.

Trusted business identity comes from verified auth metadata and user identity:

```text
tenant_id
cliente_id
owner_actor_role
owner_actor_id
```

## PRODUCTION SMOKE RUNNER

Canonical runner:

```text
tools/service_1_production_smoke_v1.py
```

Execution contract:

```text
PYMIA_PRODUCTION_BASE_URL=<https-url>
PYMIA_SUPABASE_URL=<configured>
PYMIA_SUPABASE_PUBLISHABLE_KEY=<configured>
PYMIA_SMOKE_EMAIL=<smoke-user>
PYMIA_SMOKE_PASSWORD=<smoke-password>
python tools/service_1_production_smoke_v1.py
```

The runner must not print token, password, publishable key, or service-role key.

## CURRENT CERTIFIED SMOKE SCOPE

The current certified production cut proves:

```text
LIQ_001:
- health
- unauthenticated fail-closed
- Supabase login
- authenticated upload
- SEM-8 owner flow
- owner confirmation
- deterministic execution
- XLSX delivery

REN_001:
- missing taxes fail-closed
- SEM-8 owner flow
- relationship deduplication
- discount unit confirmation
- Derived Evidence
- deterministic execution/kernel
- XLSX delivery

PERSISTENCE / REENTRY:
- persisted case listing
- persisted owner-evidence reentry
```

## DURABLE REENTRY BOUNDARY

```text
F13_DURABLE_RESULT_MEMORY: IMPLEMENTED
RC3_RESULTSET_REENTRY: CLOSED_COMMITTED_FROZEN
TENANT_REENTRY_HARDENING: CLOSED_COMMITTED
ONLINE_REENTRY_AFTER_REAL_RESTART: NOT_PROVEN
```

The current RC can reopen an immutable persisted ResultSet without restoring the XLSX or recalculating. The remaining deployment claim is to prove that behavior on the deployed RC after a real restart.

## NON-CLAIMS

This deployment contract does not yet claim:

```text
CURRENT_RC_DEPLOYED_SHA = VERIFIED
EXTERNAL_LLM_CURRENT_RC = PROVEN
ONLINE_RESULTSET_REENTRY_AFTER_RESTART = PROVEN
multi-region result-state replication
zero-downtime deployment
automatic rollback
```

The last certified production cut already includes `working_capital`; the RC acceptance must not regress it.

## CURRENT RC FRONT

```text
RC1: CLOSED
RC2: CLOSED
RC3: CLOSED
TENANT_REENTRY_HARDENING: CLOSED
RC4: CLOSED
RC5: DEPLOY EXACT SHA + REAL LLM
RC6: ONLINE CAFETERIA ACCEPTANCE
RC7: ONLINE RESULTSET REENTRY
```

New capabilities and new productive pipelines remain frozen during release-candidate closure.

## DEPLOYMENT OPERATOR RETURN CONTRACT

A future deployment/recertification operator must return non-secret evidence only:

```text
PROVIDER_OR_HOST:
PUBLIC_HTTPS_BASE_URL:
DEPLOYED_GIT_SHA:
CLOUD_RUN_REVISION:
TRAFFIC:
BOOT_COMMAND:
HEALTH_STATUS:
LOG_TARGET:
ROLLBACK_OR_PREVIOUS_REVISION_MECHANISM:
REQUIRED_ENV_NAMES_PRESENT: PASS | FAIL
EXTERNAL_LLM_PROVIDER_ACTIVE: PASS | FAIL
LLM_MATH: 0 | FAIL
ONLINE_CAFETERIA_ACCEPTANCE: PASS | FAIL
ONLINE_F13_REENTRY_AFTER_RESTART: PASS | FAIL
PRODUCTION_SMOKE: PASS | FAIL
```

Never return secret values.

## NEXT GATE

The last certified production cut is historical and does not close the pending gates for the current release candidate.

```text
FULL_SUITE_CURRENT_RC: PENDING
RC5_DEPLOY_EXACT_COMMITTED_SHA_AND_REAL_EXTERNAL_LLM: PENDING
RC6_ONLINE_CAFETERIA_ACCEPTANCE: PENDING
RC7_ONLINE_RESULTSET_REENTRY_AFTER_RESTART: PENDING
FINAL_PRODUCTION_SMOKE_CURRENT_RC: PENDING
```

The next gate is the full suite for the current RC, followed by RC5, RC6, RC7, and the final production smoke. No pending gate is PASS without observed evidence.
