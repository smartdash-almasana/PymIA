# Servicio 1 — estado técnico actual

**Fecha de corte:** 2026-08-19
**Autoridad de continuidad:** `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

## Resumen

```text
CANONICAL_PRODUCT_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
F0_F13: CLOSED_COMMITTED
RC3_COMMIT: 07f1f9b85591f99dc72d94271b117dfcb6ef6582
TENANT_REENTRY_HARDENING_COMMIT: c9de7497a9e61cfa575975a4c5f5d9815c4855de
RC1: CLOSED_COMMITTED_FROZEN
RC2: CLOSED_COMMITTED_FROZEN
RC3: CLOSED_COMMITTED_FROZEN
TENANT_REENTRY_HARDENING: CLOSED_COMMITTED
RC4: CLOSED_BY_DOCUMENTATION_SYNC
SERVICE_1_RELEASE_CANDIDATE_ACCEPTED: NO

SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
PRODUCTION_APP_SHA: d2c9c24
PRODUCTION_REVISION: pymia-service1-00008-mtf
PRODUCTION_TRAFFIC: 100%
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: PRODUCTION_CERTIFIED

EXTERNAL_LLM_RUNTIME_ACTIVATION_CURRENT_RC: NOT_PROVEN
DETERMINISTIC_SEMANTIC_FALLBACK: PRESERVED
LLM_AUTHORITY: NONE
NO_LLM_RUNTIME_AUTHORITY
SIN DIAGNÓSTICO CAUSAL
12/12 PATOLOGÍAS PRODUCTIVAS CONECTADAS
FULL_SUITE_CURRENT_RC: NOT_OBSERVED
```

El corte productivo documentado sigue siendo anterior al release candidate actual. No declarar el provider externo activo ni el RC desplegado hasta verificar el SHA exacto y completar el smoke productivo.

## Autoridad productiva

```text
CLI:  pymia/cli/service_1_product.py
WEB:  pymia/smartpyme/service_1_assisted_web_semantic_reception_v1.py
SERVER: pymia/smartpyme/service_1_semantic_reception_server_v1.py
ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
```

La web y la CLI son superficies de entrada; no crean una segunda raíz ni una segunda autoridad matemática.

## Cadena vigente

```text
canonical XLSX ingestion
→ WorkbookProfiler
→ semantic assistance proposal
→ deterministic validation
→ owner confirmation/correction
→ P6
→ AnalysisPlan
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision + GovernedAnalysisInput
→ F7 Governed Evidence Preparation
→ F8 / FormulaEngineService
→ F9 Governed ResultSet
→ F13 durable result memory
→ UI
```

## SEM-1 → SEM-9

| Corte | Estado | Responsabilidad |
|---|---|---|
| SEM-1 | PASS | WorkbookProfilerV1 |
| SEM-2 | PASS | contrato provider-neutral |
| SEM-3 | PASS | validator determinístico fail-closed |
| SEM-4 | PASS | diálogo owner mínimo y agrupado |
| SEM-5 | PASS | owner evidence canónica |
| SEM-6 | PASS | reentry hacia P6 existente |
| SEM-7 | PASS | compatibilidad estructural tenant |
| SEM-8 | PASS | wiring a raíz productiva canónica |
| SEM-9 | PASS | Cobros, Margen y Working Capital usan SEM-8; Working Capital usa scope compuesto |

Recepción semántica actual:

```text
LLM_COLUMN_INTERPRETER_V1: IMPLEMENTED
SEQUENTIAL_OWNER_CORROBORATION_V1: IMPLEMENTED
QUESTIONS_VISIBLE_AT_ONCE: 1
EXTERNAL_LLM_RUNTIME_ACTIVATION_CURRENT_RC: NOT_PROVEN
```

## Producción certificada

### LIQ_001

```text
HEALTH: PASS
UNAUTHENTICATED_FAIL_CLOSED: PASS
SUPABASE_LOGIN: PASS
AUTHENTICATED_UPLOAD: PASS
SEM8_OWNER_FLOW: PASS
OWNER_CONFIRMATION: PASS
DETERMINISTIC_EXECUTION: PASS
XLSX_DELIVERY: PASS
```

### REN_001

```text
MISSING_TAXES_FAIL_CLOSED: PASS
SEM8_OWNER_FLOW: PASS
RELATIONSHIP_DEDUPLICATION: PASS
DISCOUNT_UNIT_CONFIRMATION: PASS
DERIVED_EVIDENCE: PASS
DETERMINISTIC_EXECUTION: PASS
XLSX_DELIVERY: PASS
```

## Persistencia / reentry

```text
F13_DURABLE_RESULT_MEMORY: PASS
CONTENT_ADDRESSED: YES
TENANT_SCOPED: YES
APPEND_ONLY: YES
RC3_RESULTSET_REENTRY: CLOSED_COMMITTED_FROZEN
TENANT_REENTRY_HARDENING: CLOSED_COMMITTED
```

RC3 reabre el ResultSet persistido sin XLSX, sin LLM y sin recalculación. La prueba online después de restart real sigue pendiente.

## Working Capital

```text
TECHNICAL_E2E_READY: YES
PRODUCTION_CERTIFIED: YES
SEMANTIC_SCOPING: SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
COMPONENTS:
- projected_closing_cash_balance
- dso
- current_ratio
```

## Tenant semantics

```text
TENANT_SEMANTIC_CONTRACT: IMPLEMENTED
TENANT_STORE: APPEND_ONLY / TENANT_ISOLATED
COMPATIBLE_MEMORY: HINT_ONLY
AUTOMATIC_REUSE: FORBIDDEN
SEMANTIC_REBIND: FORBIDDEN
```

## Provider semántico actual

```text
PYDANTIC_AI_COLUMN_PROVIDER: IMPLEMENTED
EXTERNAL_LLM_RUNTIME_ACTIVATION_CURRENT_RC: NOT_PROVEN
DETERMINISTIC_SAFE_BASELINE_PROVIDER: PRESERVED
LLM_CALCULATION_AUTHORITY: NONE
LLM_RUNTIME_AUTHORITY: NONE
LLM_TOOL_AUTHORITY: NONE
LLM_DELIVERY_AUTHORITY: NONE
```

## Estado de pruebas del RC

```text
RC1_POST_COMMIT_FOCAL: 30 passed
RC2_POST_COMMIT_REGRESSION: 69 passed
RC3_FOCAL: 4 passed
RC3_EXTENDED_GATE: 73 passed
TENANT_REENTRY_HARDENING_FOCAL: 3 passed
TENANT_F13_HTTP_ARCHITECTURE_GATE: 48 passed
FULL_SUITE_CURRENT_RC: NOT_OBSERVED
```

El full suite de cortes anteriores no se usa como evidencia del RC actual.

## Deuda abierta real

```text
RC3_COMMIT_FREEZE: CLOSED
TENANT_REENTRY_HARDENING: CLOSED
RC4_DOCUMENTATION_AND_STALE_TEST_SYNC: CLOSED
FULL_SUITE_CURRENT_RC: PENDING
DEPLOY_EXACT_RC_SHA: PENDING
REAL_EXTERNAL_LLM_PROOF: PENDING
ONLINE_CAFETERIA_ACCEPTANCE: PENDING
ONLINE_F13_REENTRY_AFTER_RESTART: PENDING
FINAL_PRODUCTION_SMOKE: PENDING
```

## Frente actual

```text
FULL_SUITE
→ RC5_DEPLOY_AND_REAL_LLM
→ RC6_ONLINE_CAFETERIA
→ RC7_ONLINE_REENTRY
→ FINAL_PRODUCTION_SMOKE
```

No crear F14 ni ampliar el producto por inercia.

## Invariantes

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_LLM_RUNTIME_AUTHORITY
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
FAIL_CLOSED
P8_IS_COMPUTABILITY_AUTHORITY
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
```
