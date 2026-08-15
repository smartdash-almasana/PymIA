# Active Roadmap — Servicio 1

**Fecha de corte:** 2026-08-14
**Autoridad:** `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

## Estado

```text
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
PRODUCTION_APP_SHA: 225f2c4
PRODUCTION_REVISION: pymia-service1-00006-h45
PRODUCTION_TRAFFIC: 100%
SERVICE_1_PRODUCTION_SMOKE: PASS
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: PRODUCTION_CERTIFIED
WORKING_CAPITAL_SEMANTICS: SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
LOCAL_SANITATION: P8_LEGACY_PROJECTION_REMOVED / 3_DEAD_SANDBOX_SLICES_REMOVED
LOCAL_SANITATION_DEPLOYED: NO
```

## Frente actual único

```text
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1
```

No hay un frente productivo paralelo autorizado.

## Objetivo

Reducir deuda técnica, arquitectónica y documental; converger journeys y eliminar compatibilidades probadamente innecesarias sin ampliar alcance ni introducir nuevas authorities.

## Secuencia obligatoria

```text
1. DOCUMENTATION_AUTHORITY_SYNC — CLOSED
2. PHYSICAL_JOURNEY_MAP — CLOSED
3. LEGACY_DEPENDENCY_INVENTORY — CLOSED
4. CONVERGE_WEB_JOURNEYS — CLOSED_PRODUCTION_PASS
5. LEGACY_REENTRY_AND_P8_PROJECTION_SANITATION — IN_PROGRESS
6. NORMALIZE_PERSISTENCE_REENTRY_DELIVERY — PENDING
7. DELETE_PROVEN_DEAD_PATHS — PARTIAL
8. FULL_REGRESSION — PENDING
9. PRODUCTION_RECERTIFICATION — PENDING
```

## Estado por journey

### LIQ_001

```text
SEM-8: YES
P8: YES
KERNEL/DETERMINISTIC_EXECUTION: YES
XLSX_DELIVERY: YES
PRODUCTION_CERTIFIED: YES
```

### REN_001

```text
SEM-8: YES
OWNER_RELATIONSHIP_CONFIRMATION: YES
DISCOUNT_UNIT_CONFIRMATION: YES
DERIVED_EVIDENCE: YES
P8: YES
KERNEL: YES
XLSX_DELIVERY: YES
PRODUCTION_CERTIFIED: YES
```

### working_capital

```text
TECHNICAL_E2E_READY: YES
SEM-8: YES
SEMANTIC_SCOPING: SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
COMPONENTS:
- projected_closing_cash_balance
- dso
- current_ratio
COMPOSITE_DELIVERY: NO
PRODUCTION_CERTIFIED: YES
```

## Deuda abierta confirmada

```text
1. run_owner_reentry ya salió del canonical product root; queda aislado en adapter SUPPORT_NECESSARY para compatibilidad CLI/harness históricos.
2. build_computation_plan/ComputationPlanV1: REMOVED_LOCAL_PASS; cobertura migrada a P8 canónico.
3. tres completion slices sandbox sin callers productivos: REMOVED_LOCAL_PASS.
4. compatibilidades P6/reentry restantes: OPEN.
5. documentación histórica: REFERENCE_ONLY, fuera de autoridad activa.
```

Clasificación para cada deuda de código:

```text
KEEP
MIGRATE
DELETE_CANDIDATE
```

`DELETE_CANDIDATE` requiere cero callers productivos en Graphify, búsqueda física consistente y cobertura del camino canónico.

## Congelamiento durante sanidad

```text
NEW_FEATURES: FROZEN
NEW_CAPABILITIES: FROZEN
WORKING_CAPITAL_EXPANSION: FROZEN
DPO_PAYMENT_COLLECTION_GAP: FROZEN
EXTERNAL_LLM_PROVIDER: FROZEN
SERVICE_2_EXPANSION: FROZEN
LANDING_UI: OUT_OF_SCOPE
```

## Invariantes

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_LLM_RUNTIME_AUTHORITY
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
P8_IS_COMPUTABILITY_AUTHORITY
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
```

## Regla de método

```text
una tarea
→ una verificación
→ un resultado
→ una decisión
```

El próximo corte es reducir o retirar el adapter legacy de reentry desde CLI/harness históricos; `run_owner_reentry` ya no pertenece a la canonical product root closure.
