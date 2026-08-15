# SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1

## STATUS

```text
DEPLOYMENT_TARGET: GOOGLE_CLOUD_RUN
SERVICE: pymia-service1
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
DEPLOYED_GIT_SHA: 53a0016085c864eb4ddbd3baa42dba48f2d7173d
CLOUD_RUN_REVISION: pymia-service1-00005-d5l
TRAFFIC: 100%
PRODUCTION_SMOKE_RUNNER_HEAD: e26f7acfaf5c68c1e5aaad1380992d5f4034883c
RUNTIME_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
WEB_ENTRYPOINT: python -m pymia.smartpyme.service_1_assisted_web_v1
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

The smoke runner additionally reads:

```text
PYMIA_PRODUCTION_BASE_URL
PYMIA_SMOKE_EMAIL
PYMIA_SMOKE_PASSWORD
```

Smoke credentials must not be committed or printed.

## PYTHON PACKAGE REQUIREMENT

Production must install the Supabase optional dependency because the production entrypoint constructs the Supabase identity resolver and persistence adapter.

Expected install shape:

```text
python -m pip install .[supabase]
```

or an equivalent deployment-specific package installation that provides the same declared dependency set.

## BOOT CONTRACT

The process must execute the existing canonical assisted-web entrypoint:

```text
python -m pymia.smartpyme.service_1_assisted_web_v1 --host <bind-host> --port <port>
```

No alternative productive pipeline or web business-computation root is authorized.

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
DURABLE_REENTRY_SCOPE: OWNER_EVIDENCE_ONLY
```

The certified reentry path proves persisted owner semantic evidence. It does not prove restoration of the original XLSX or the complete result snapshot after process restart.

## NON-CLAIMS

This deployment contract does not claim:

```text
durable XLSX/result snapshots across restart
multi-region or multi-instance result-state replication
zero-downtime deployment
automatic rollback
working_capital production certification
```

`working_capital` has a local SEM-8 composite-scope migration with focal PASS, but remains outside the current production certification boundary until the new cut is committed, deployed, and production-smoked.

## SANITATION FRONT

```text
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1
```

During sanitation, new capabilities, provider expansion, DPO/payment_collection_gap and new productive pipelines remain frozen.

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
PRODUCTION_SMOKE: PASS | FAIL
```

Never return secret values.

## NEXT GATE

There is no pending release gate for the current LIQ_001/REN_001 cut; it is production certified.

The next production gate occurs only after a sanitation/convergence change requires recertification.
