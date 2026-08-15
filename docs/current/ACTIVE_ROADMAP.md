# Active Roadmap — Servicio 1

**Fecha de corte:** 2026-08-14
**Autoridad:** `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

## Estado

```text
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
PRODUCTION_APP_SHA: 53a0016085c864eb4ddbd3baa42dba48f2d7173d
PRODUCTION_REVISION: pymia-service1-00005-d5l
PRODUCTION_TRAFFIC: 100%
RUNNER_HEAD: e26f7acfaf5c68c1e5aaad1380992d5f4034883c
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: TECHNICAL_E2E_READY / NOT_PRODUCTION_CERTIFIED
WORKING_CAPITAL_SEMANTICS: SEM8_COMPOSITE_SCOPE_LOCAL_PASS
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
1. DOCUMENTATION_AUTHORITY_SYNC
2. PHYSICAL_JOURNEY_MAP
3. LEGACY_DEPENDENCY_INVENTORY
4. CONVERGE_WEB_JOURNEYS
5. NORMALIZE_PERSISTENCE_REENTRY_DELIVERY
6. DELETE_PROVEN_DEAD_PATHS
7. FULL_REGRESSION
8. PRODUCTION_RECERTIFICATION
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
SEM-8: NO
SEMANTIC_SCOPING: SEM8_COMPOSITE_SCOPE_LOCAL_PASS
COMPONENTS:
- projected_closing_cash_balance
- dso
- current_ratio
COMPOSITE_DELIVERY: NO
PRODUCTION_CERTIFIED: NO
```

## Deuda abierta confirmada

```text
1. fork semántico legacy de working_capital cerrado localmente; pendiente certificación productiva
2. múltiples mecanismos/superficies de reentry
3. proyecciones legacy de compatibilidad P8/P6
4. slices/sandboxes sin callers productivos pendientes de clasificación
5. documentación histórica que no debe gobernar estado actual
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

El próximo paso después de esta sincronización documental es `PHYSICAL_JOURNEY_MAP`, usando Graphify como evidencia primaria y grep/tests como verificación puntual.
