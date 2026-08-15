# Servicio 1 — estado técnico actual

**Fecha de corte:** 2026-08-14
**Autoridad de continuidad:** `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

## Resumen

```text
CANONICAL_PRODUCT_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
PRODUCTION_APP_SHA: 53a0016085c864eb4ddbd3baa42dba48f2d7173d
PRODUCTION_REVISION: pymia-service1-00005-d5l
PRODUCTION_TRAFFIC: 100%
RUNNER_HEAD: e26f7acfaf5c68c1e5aaad1380992d5f4034883c
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: SEM8_MIGRATION_IMPLEMENTED_IN_WORKTREE / NOT_PRODUCTION_CERTIFIED
WORKING_CAPITAL_SEMANTICS: SEM8_COMPOSITE_SCOPE_LOCAL_PASS
EXTERNAL_LLM_PROVIDER: NOT_CONNECTED
SAFE_DETERMINISTIC_PROVIDER: ACTIVE
KERNEL_GENÉRICO_PRODUCTIVO: ACTIVO
SIN_DIAGNÓSTICO_CAUSAL
12/12_PATOLOGÍAS_PRODUCTIVAS_CONECTADAS: CONSERVADAS
NEW_PRODUCTIVE_CAPABILITY_AUTHORIZED: NO
```

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
| SEM-9 | PASS acotado | Cobros y Margen; Working Capital conserva piloto legacy |

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
PRODUCTION_CERTIFIED: NO
SEMANTIC_SCOPING: SEM8_COMPOSITE_SCOPE_LOCAL_PASS
COMPONENTS:
- projected_closing_cash_balance
- dso
- current_ratio
```

La composición usa capacidades ya gobernadas, pero no está todavía alineada al carril SEM-8 certificado. DPO/payment_collection_gap siguen fuera del alcance.

## Tenant semantics

```text
TENANT_SEMANTIC_CONTRACT: IMPLEMENTED
TENANT_STORE: APPEND_ONLY / TENANT_ISOLATED
STRUCTURAL_COMPATIBILITY: IMPLEMENTED
COMPATIBLE_MEMORY: HINT_ONLY
AUTOMATIC_REUSE: FORBIDDEN
SEMANTIC_REBIND: FORBIDDEN
```

## Deuda abierta prioritaria

```text
SEMANTIC_FORK_WORKING_CAPITAL: CLOSED_LOCAL_PASS / PENDING_PRODUCTION_CERTIFICATION
MULTIPLE_REENTRY_MECHANISMS: OPEN
LEGACY_P8/P6_COMPATIBILITY_PROJECTIONS: OPEN
UNUSED_SANDBOX_SLICES: NEEDS_CLASSIFICATION
DOCUMENTATION_HISTORICAL_DRIFT: SANITATION_IN_PROGRESS
```

## Frente actual

```text
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1
```

No agregar features/capabilities ni conectar provider externo hasta cerrar sanidad, convergencia, regresión y recertificación.

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
