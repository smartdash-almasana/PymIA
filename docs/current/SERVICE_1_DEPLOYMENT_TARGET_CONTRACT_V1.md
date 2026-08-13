# SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1

## STATUS

```text
IDENTIFY_OR_CREATE_SERVICE_1_DEPLOYMENT_TARGET_V1: READY_FOR_EXTERNAL_DEPLOY
RUNTIME_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
WEB_ENTRYPOINT: python -m pymia.smartpyme.service_1_assisted_web_v1
```

## PURPOSE

Define the minimum deployment facts required before `PRODUCTION_SMOKE` can claim evidence.

This contract does not authorize a second product root, a new runtime authority, a new parser, or a new capability.

## REQUIRED DEPLOYMENT FACTS

The deployed Servicio 1 instance must expose:

```text
PROVIDER_OR_HOST
PUBLIC_HTTPS_BASE_URL
DEPLOYED_GIT_SHA
BOOT_COMMAND
HEALTH_ENDPOINT=/healthz
LOG_TARGET
RESTART_OR_REDEPLOY_COMMAND
ROLLBACK_OR_PREVIOUS_REVISION_MECHANISM
```

No production claim is allowed if these facts are unknown.

## REQUIRED RUNTIME CONFIGURATION

The production process requires these environment variables:

```text
PYMIA_SUPABASE_URL
PYMIA_SUPABASE_PUBLISHABLE_KEY
PYMIA_SUPABASE_SERVICE_ROLE_KEY
```

Values are secrets/configuration and must not be committed to the repository.

The smoke runner additionally reads:

```text
PYMIA_PRODUCTION_BASE_URL
PYMIA_SMOKE_EMAIL
PYMIA_SMOKE_PASSWORD
```

`PYMIA_SMOKE_EMAIL` and `PYMIA_SMOKE_PASSWORD` are smoke-only credentials and must not be committed.

## PYTHON PACKAGE REQUIREMENT

Production must install the Supabase optional dependency because the production entrypoint constructs both the Supabase identity resolver and persistence adapter.

Expected install shape:

```text
python -m pip install .[supabase]
```

or an equivalent deployment-specific package installation that provides the same declared dependency set.

## BOOT CONTRACT

The process must execute the existing canonical assisted-web entrypoint. A deployment platform may choose its own host/port injection, but it must ultimately run the equivalent of:

```text
python -m pymia.smartpyme.service_1_assisted_web_v1 --host <bind-host> --port <port>
```

No alternative productive pipeline or web business-computation root is authorized.

## HEALTH CONTRACT

```text
GET /healthz
→ HTTP 200
→ {"status":"ok"}
```

The public production URL must use HTTPS.

## IDENTITY CONTRACT

For protected POST operations:

```text
Authorization: Bearer <Supabase access token>
```

The application validates the JWT through Supabase before accepting identity.

Trusted business identity is taken only from verified `app_metadata`:

```text
tenant_id
cliente_id
owner_actor_role
```

`owner_actor_id` is taken from the verified Supabase user id.

The smoke identity must therefore be an existing Supabase Auth user whose verified app metadata contains all required fields.

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

## SMOKE CHECKS

The runner proves, in one controlled journey:

```text
HTTPS target
/healthz
unauthenticated protected upload fails closed
Supabase login returns access token
authenticated XLSX upload
owner semantic confirmation
deterministic sold-vs-collected execution
tenant semantic persistence path participates in production runtime
XLSX delivery/download
recent-case reentry on the current process instance
```

Restart/redeploy and log visibility are deployment-layer checks and must be appended to the production smoke evidence by the deployment operator.

## NON-CLAIMS

This deployment contract does not claim:

```text
durable recent-case snapshots across process restart
multi-region or multi-instance case-state replication
zero-downtime deployment
automatic rollback
```

Those properties are not part of the frozen sellable product contract unless separately authorized and proven.

## DEPLOYMENT OPERATOR RETURN CONTRACT

The deployment operator must return only non-secret evidence:

```text
PROVIDER_OR_HOST:
PUBLIC_HTTPS_BASE_URL:
DEPLOYED_GIT_SHA:
BOOT_COMMAND:
HEALTH_STATUS:
LOG_TARGET:
RESTART_OR_REDEPLOY_COMMAND:
ROLLBACK_OR_PREVIOUS_REVISION_MECHANISM:
REQUIRED_ENV_NAMES_PRESENT: PASS | FAIL
SMOKE_USER_READY: PASS | FAIL
```

Never return secret values.

## NEXT GATE

When the deployment operator returns the required facts and the target is live:

```text
PRODUCTION_SMOKE
```
