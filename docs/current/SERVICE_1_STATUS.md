# Servicio 1 — estado técnico actual

**Fecha de corte:** 2026-08-16
**Autoridad de continuidad:** `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

## Resumen

```text
CANONICAL_PRODUCT_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
MAIN_HEAD: 26ef6c8c57bb201da1a36a1073147c641d1309f4
PRODUCTION_APP_SHA: d2c9c24
PRODUCTION_REVISION: pymia-service1-00008-mtf
PRODUCTION_TRAFFIC: 100%
SERVICE_1_PRODUCTION_SMOKE: PASS
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: PRODUCTION_CERTIFIED
WORKING_CAPITAL_SEMANTICS: SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
LLM_COLUMN_INTERPRETER_IMPLEMENTATION: MERGED_IN_MAIN
SEQUENTIAL_OWNER_CORROBORATION: MERGED_IN_MAIN
PRODUCTION_DEPLOYMENT_OF_SEMANTIC_RECEPTION_CUT: PENDING
EXTERNAL_LLM_RUNTIME_ACTIVATION: NOT_PROVEN
DETERMINISTIC_SEMANTIC_FALLBACK: PRESERVED
LLM_AUTHORITY: NONE
KERNEL GENÉRICO PRODUCTIVO: ACTIVO
SIN DIAGNÓSTICO CAUSAL
12/12 PATOLOGÍAS PRODUCTIVAS CONECTADAS
NEW_PRODUCTIVE_CAPABILITY_AUTHORIZED: NO
```

`main` contiene el nuevo corte semántico; producción todavía conserva la revisión certificada anterior. No declarar el provider externo activo en runtime hasta deploy y smoke productivo.

## Autoridad productiva

```text
CLI:  pymia/cli/service_1_product.py
WEB:  pymia/smartpyme/service_1_assisted_web_v1.py
ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
```

La web y la CLI son superficies de entrada; no crean una segunda raíz ni una segunda autoridad matemática.

## Cadena vigente

```text
canonical XLSX ingestion
→ physical/workbook evidence
→ semantic assistance proposal
→ deterministic validation
→ owner material confirmation
→ P6 ApprovalDecision
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision + GovernedComputationInput
→ Derived Evidence cuando corresponda
→ deterministic execution/kernel
→ bounded outcome
→ controlled delivery
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

Corte posterior integrado en `main`:

```text
LLM_COLUMN_INTERPRETER_V1: MERGED_IN_MAIN
SEQUENTIAL_OWNER_CORROBORATION_V1: MERGED_IN_MAIN
QUESTIONS_VISIBLE_AT_ONCE: 1 (FOCUSED_TEST_AND_LOCAL_SMOKE_PASS)
PRODUCTION_CERTIFICATION_OF_THIS_CUT: PENDING
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
PERSISTED_CASE_LISTING: PASS
PERSISTED_CASE_REENTRY: PASS
DURABLE_REENTRY_SCOPE: OWNER_EVIDENCE_ONLY
```

No afirmar restauración durable del XLSX/result snapshot después de restart.

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

La composición usa capacidades ya gobernadas y está certificada en producción sobre SEM-8. DPO/payment_collection_gap siguen fuera del alcance.

## Tenant semantics

```text
TENANT_SEMANTIC_CONTRACT: IMPLEMENTED
TENANT_STORE: APPEND_ONLY / TENANT_ISOLATED
STRUCTURAL_COMPATIBILITY: IMPLEMENTED
COMPATIBLE_MEMORY: HINT_ONLY
AUTOMATIC_REUSE: FORBIDDEN
SEMANTIC_REBIND: FORBIDDEN
```

## Provider semántico actual

```text
PYDANTIC_AI_COLUMN_PROVIDER: IMPLEMENTED_AND_MERGED_IN_MAIN
EXTERNAL_LLM_RUNTIME_ACTIVATION: NOT_PROVEN
DETERMINISTIC_SAFE_BASELINE_PROVIDER: PRESERVED
LLM_CALCULATION_AUTHORITY: NONE
LLM_RUNTIME_AUTHORITY: NONE
LLM_TOOL_AUTHORITY: NONE
LLM_PERSISTENCE_AUTHORITY: NONE
LLM_DELIVERY_AUTHORITY: NONE
```

## Cierre técnico

```text
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1: CLOSED_PASS
SERVICE_1_FINAL_SANITATION_REGRESSION_AND_CLOSURE_V1: PASS
SERVICE_1_TECHNICAL_CLOSURE: PASS
FULL_SUITE: PASS (3605 passed / 0 failed / 7 skipped)
ARCHITECTURE_BASELINE: PASS_ARCHITECTURE_BASELINE_V1 / BLOCKERS NONE
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: PRODUCTION_CERTIFIED
LEGACY_SUPPORT_RESIDUAL: ACCEPTED_TECHNICAL_DEBT / BOUNDED / NON_AUTHORITATIVE / OUTSIDE_CANONICAL_ROOT / FROZEN
```

El cierre técnico previo permanece válido; el nuevo corte semántico integrado requiere su propia actualización de producción antes de declararlo productivo.

## Deuda abierta prioritaria

```text
SEMANTIC_FORK_WORKING_CAPITAL: CLOSED_PRODUCTION_PASS
RUN_OWNER_REENTRY_COMPATIBILITY: ACCEPTED_TECHNICAL_DEBT / FROZEN / OUTSIDE_CANONICAL_ROOT
LEGACY_P6_REENTRY_COMPATIBILITY: ACCEPTED_TECHNICAL_DEBT / FROZEN / NON_AUTHORITATIVE
DOCUMENTATION_HISTORICAL_DRIFT: CLOSED
```

Política del residual legacy:

```text
NEW_CALLERS: FORBIDDEN
NEW_FEATURE_DEPENDENCY: FORBIDDEN
AUTHORITY: NONE
DELETE_TRIGGER:
- ZERO_CALLERS
- FULL_SUITE_PASS
- ARCHITECTURE_BASELINE_PASS
- PRODUCTION_SMOKE_PASS
```

Hasta que se cumpla ese trigger, el residual se conserva congelado como compatibilidad técnica aceptada; no constituye frente activo de Servicio 1.

## Frente actual

```text
DOCUMENTATION_RECONCILIATION_AFTER_PR14: CLOSED
SEMANTIC_RECEPTION_SEQUENTIAL_CUT: MERGED_IN_MAIN
PRODUCTION_DEPLOYMENT_OF_SEMANTIC_RECEPTION_CUT: NEXT
PRODUCTION_SMOKE_OF_SEMANTIC_RECEPTION_CUT: AFTER_DEPLOY
PYMIARADAR: FUTURE_REFERENCE_ONLY / OUT_OF_CURRENT_SCOPE
```

No agregar nuevas features/capabilities durante este cierre. El siguiente paso es desplegar y certificar el corte ya integrado. PymiaRadar queda fuera del camino crítico hasta finalizar Servicio 1.

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
