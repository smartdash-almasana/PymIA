# Servicio 1 — mapa actual de arquitectura y componentes V1

**Estado:** `ACTIVE_ARCHITECTURE_MAP`
**Fecha de corte:** 2026-08-14

## 1. Autoridad productiva

```text
CLI:  pymia/cli/service_1_product.py
WEB:  pymia/smartpyme/service_1_assisted_web_v1.py
ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
```

Sólo `service_1_product_pipeline_v1.py` es raíz productiva. CLI y web son adaptadores.

## 2. Producción vigente

```text
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
APP_SHA: 225f2c4
CLOUD_RUN_REVISION: pymia-service1-00006-h45
TRAFFIC: 100%
RUNNER_HEAD: e26f7acfaf5c68c1e5aaad1380992d5f4034883c
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: PRODUCTION_CERTIFIED / SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
```

## 3. Mapa canónico de alto nivel

```text
XLSX
↓
canonical ingestion / normalized_tables
↓
SEM-1 WorkbookProfiler
↓
SEM-2 provider-neutral semantic context
↓
semantic provider
↓
SEM-3 deterministic validator
↓
SEM-4 OwnerDialoguePlan
↓
DUEÑO PYME
↓
SEM-5 owner evidence
↓
SEM-6 reentry
↓
P6 ApprovalDecision
↓
P7 RequirementMatch + Grain
↓
P8 ComputabilityDecision + GovernedComputationInput
↓
Derived Evidence cuando la capability lo requiere
↓
KERNEL / FormulaEngineService
↓
bounded outcome
↓
controlled delivery
```

Este es el carril canónico de LIQ_001, REN_001 y `working_capital`. La composición usa un scope SEM-8 compuesto sobre sus tres capabilities existentes y está certificada en producción.

## 4. SEM-1 → SEM-9

```text
SEM-1  WorkbookProfilerV1
SEM-2  provider-neutral closed semantic contract
SEM-3  deterministic semantic proposal validator
SEM-4  minimal owner dialogue planner
SEM-5  canonical owner evidence projection
SEM-6  owner evidence reentry to existing semantic gate/P6
SEM-7  tenant structural compatibility
SEM-8  assisted semantic wiring into canonical product root
SEM-9  assisted web wiring for LIQ_001 / REN_001
```

`working_capital` ya no usa semantic scoping legacy y su scope compuesto SEM-8 está certificado en producción. La deuda abierta se concentra en compatibilidad legacy de reentry/P6 y en superficies muertas probadamente aisladas.

## 5. División de autoridad

### Semantic provider

Puede proponer significado, relaciones e incertidumbre basada en evidencia real. No puede confirmar por el owner, crear owner evidence, autorizar runtime/delivery ni calcular fórmulas.

### Owner

Confirma o corrige significado empresarial material. Su confirmación es evidencia, no permiso.

### P6/P7/P8

```text
P6 = aprobación semántica gobernada
P7 = match de requisitos + grain
P8 = única autoridad de computabilidad
```

### Derived Evidence

Transforma evidencia confirmada en variables canónicas cuando el workbook no trae directamente el agregado requerido. No ejecuta la fórmula final ni inventa inputs materiales ausentes.

### Kernel

```text
pymia/services/formula_engine_service.py
```

Única autoridad matemática ejecutable.

## 6. Journeys

### LIQ_001

```text
upload
→ SEM-8
→ owner confirmation
→ P6/P7/P8
→ deterministic execution
→ bounded outcome
→ XLSX delivery
→ persisted owner evidence / durable case reentry
```

### REN_001

```text
upload
→ SEM-8
→ owner semantic confirmation
→ owner-confirmed product relationship
→ discount unit confirmation cuando corresponde
→ Derived Evidence
→ P8
→ FormulaEngineService/kernel
→ bounded outcome
→ XLSX delivery
→ persisted owner evidence / durable case reentry
```

### working_capital

```text
upload
→ legacy semantic scoping
→ projected_closing_cash_balance
→ dso
→ current_ratio
→ web composition
→ result page
```

Estado:

```text
TECHNICAL_E2E_READY: YES
SEM8_CONVERGED: NO
PRODUCTION_CERTIFIED: NO
COMPOSITE_XLSX_DELIVERY: NO
```

## 7. Persistencia y reentry

Producción certificada:

```text
PERSISTED_CASE_LISTING: PASS
PERSISTED_CASE_REENTRY: PASS
DURABLE_REENTRY_SCOPE: OWNER_EVIDENCE_ONLY
```

La auditoría de sanidad detectó múltiples mecanismos/superficies de reentry. Deben clasificarse y converger sin ampliar claims de durabilidad.

## 8. Memoria tenant

```text
owner evidence
→ TenantSemanticContractV1
→ append-only tenant store
→ structural signature
→ SEM-7 compatibility classification
→ compatible hint only
→ SEM-2 context
```

La memoria no autoriza reuse automático ni semantic rebind.

## 9. Deuda arquitectónica abierta

```text
SEMANTIC_FORK_WORKING_CAPITAL: CLOSED_PRODUCTION_PASS
MULTIPLE_REENTRY_MECHANISMS: OPEN
LEGACY_P8/P6_COMPATIBILITY_PROJECTIONS: OPEN
UNUSED_SANDBOX_SLICES: NEEDS_CLASSIFICATION
```

Graphify es evidencia primaria para dependency/journey mapping; grep físico y tests verifican decisiones KEEP/MIGRATE/DELETE_CANDIDATE.

## 10. Invariantes arquitectónicos

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_LLM_RUNTIME_AUTHORITY
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
NO_SEMANTIC_REBIND_AFTER_P6
P7_AND_P8_REMAIN_SEPARATE
P8_IS_COMPUTABILITY_AUTHORITY
DERIVED_EVIDENCE_IS_NOT_FORMULA_AUTHORITY
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
FAIL_CLOSED
```

## 11. Frente actual

```text
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1
```

No ampliar producto hasta cerrar convergencia, regresión y recertificación.
