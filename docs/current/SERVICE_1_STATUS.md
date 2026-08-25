# Servicio 1 — estado técnico actual

**Fecha de corte:** 2026-08-23
**Autoridad de continuidad:** `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

## Override de convergencia integral — 2026-08-23

La arquitectura objetivo ya no está bajo discusión: quedó **cerrada dialécticamente y convertida en autoridad normativa**. El worktree actual, sin embargo, todavía contiene generaciones transitorias/legacy y **no está certificado integralmente**.

```text
DIALECTICAL_REVIEW_COMPLETE: PASS
OPEN_ARCHITECTURAL_DECISIONS: 0
TARGET_ARCHITECTURE_CLOSED: YES
CANONICAL_AXIS_FINAL_ARCHITECTURE: DOCUMENTED
ARCHITECTURE_LOCK_FINAL_ARCHITECTURE: DOCUMENTED
IMPLEMENTATION_HANDOFF_PACKAGE: COMPLETE
RECONSTRUCTION_PLAN: AUTHORITATIVE
COMPLETION_CONTRACT: AUTHORITATIVE
RECONSTRUCTION_IMPLEMENTATION: IN_PROGRESS
R0_R1: CLOSED_PASS
R2: CLOSED_PASS
R3: CLOSED_PASS
NEXT_ALLOWED_NODE: R4
CURRENT_WORKTREE_INTEGRAL_CERTIFICATION: NO
FULL_SUITE_AFTER_RECONSTRUCTION: NOT_YET_RUN
REAL_WORKBOOK_E2E_AFTER_RECONSTRUCTION: NOT_YET_RUN
LAST_AUDIT_FULL_SUITE: 3806 passed / 77 failed / 7 skipped / 3 errors
MODULE_REGISTRY_CURRENT_WORKTREE: NOT_RECONCILED
COMMIT_PUSH_DEPLOY: NOT_AUTHORIZED
```

Este checkpoint distingue la arquitectura objetivo cerrada de la reconstrucción todavía en curso, la certificación integral aún pendiente y cualquier autorización de release. R0/R1, R2 y R3 están cerrados en PASS; R4 es el único nodo siguiente autorizado.

Los antiguos Phase 1–4 son evidencia histórica de la convergencia previa y ya no definen el plan siguiente. La reconstrucción debe derivarse del delta físico contra `SERVICE_1_CANONICAL_AXIS.md` y `SERVICE_1_ARCHITECTURE_LOCK.md`, en orden de dependencias.

Ninguna decisión que exista sólo en chat, prompt o `_audit/` gobierna implementación.

## Resumen histórico del último corte documentado

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

## Cadena objetivo normativa

```text
XLSX
→ source_artifact_ref (content-addressed)
→ canonical reader
→ CanonicalIngestionOutput V2
→ D1 → D2 → D3 → D4 → D5 → D6 → D7
→ ProductExecutionRoot / WorkbookSemanticStartRequest
→ provider determinístico | bounded LLM
→ deterministic validator
→ owner dialogue
→ WorkbookSemanticContinueRequest
→ shared reinjector / P6
→ CONFIRMED_BINDINGS
→ WorkbookAnalysisExecuteRequest
→ P7 RequirementMatch + Grain
→ P8 Computability + governed provenance
→ F7 physical join/evidence materialization + runtime safety
→ FormulaEngineService / MathPrimitiveOperation / formula catalog
→ declarative classification policy
→ F9 Governed ResultSet
→ F13 persistence
```

Lectura persistida:

```text
Web / CLI
→ Service1ResultQueryV1
→ ResultReadBoundary
→ F13 load
→ persisted presentation
```

La ruta de lectura no recalcula ni reejecuta SEM/P7/P8/F7/F8/F9.

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
ONE_PRODUCTIVE_EXECUTION_ROOT
FOUR_EXPLICIT_EXECUTION_COMMANDS
RESULT_READ_SEPARATE_FROM_EXECUTION
ONE_CANONICAL_PRODUCTIVE_XLSX_READER
ONE_CANONICAL_INGESTION_ENVELOPE
WORKBOOK_D1_D7_MANDATORY
D7_EVIDENCE_ONLY
ONE_PRODUCTIVE_SEMANTIC_FSM
TABLE_SCOPE_BUILT_ONCE_IN_D6_D7
P7_IS_GRAIN_REQUIREMENT_AUTHORITY
P8_IS_COMPUTABILITY_AND_PROVENANCE_AUTHORITY
F7_IS_ONLY_JOIN_MATERIALIZER_WITH_RUNTIME_SAFETY
FORMULA_ENGINE_SERVICE_IS_MATH_KERNEL_AUTHORITY
CLASSIFICATION_POLICY_DOES_NO_ARITHMETIC
NO_LLM_RUNTIME_OR_MATH_AUTHORITY
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
NO_FILENAME_WORKBOOK_IDENTITY
NO_SHEET1_FALLBACK
NO_INDEFINITE_COMPATIBILITY
FAIL_CLOSED
```
