# Servicio 1 — mapa actual de arquitectura y componentes V1

**Estado:** `ACTIVE_ARCHITECTURE_MAP`
**Fecha de corte:** 2026-08-19

## 1. Autoridad productiva

```text
WEB:  adapter de interacción
ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
MATH: pymia/services/formula_engine_service.py
```

Sólo `service_1_product_pipeline_v1.py` es raíz productiva. La Web solicita y presenta; no coordina F7/F8/F9 desde RC1.

## 2. Estado de release

```text
RC3_COMMIT: 07f1f9b85591f99dc72d94271b117dfcb6ef6582
TENANT_REENTRY_HARDENING_COMMIT: c9de7497a9e61cfa575975a4c5f5d9815c4855de
RC1: CLOSED_COMMITTED_FROZEN
RC2: CLOSED_COMMITTED_FROZEN
RC3: CLOSED_COMMITTED_FROZEN
TENANT_REENTRY_HARDENING: CLOSED_COMMITTED
RC4: CLOSED_BY_DOCUMENTATION_SYNC

SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
PRODUCTION_APP_SHA: d2c9c24
CLOUD_RUN_REVISION: pymia-service1-00008-mtf
TRAFFIC: 100%
```

El corte certificado documentado y el RC actual son estados distintos.

## 3. Mapa canónico general

```text
XLSX
↓
canonical ingestion / normalized_tables
↓
WorkbookProfiler
↓
semantic provider bounded
↓
deterministic semantic validation
↓
DUEÑO PYME confirma/corrige
↓
P6
↓
AnalysisPlan
↓
P7 RequirementMatch + ResolvedGrain
↓
P8 ComputabilityDecision + GovernedAnalysisInput
↓
F7 Governed Evidence Preparation
↓
F8 / FormulaEngineService
↓
F9 Governed ResultSet
↓
F13 immutable result memory
↓
UI
```

## 4. División de autoridad

### Provider / LLM

Propone significado y puede formular preguntas. No calcula, no confirma por el dueño y no autoriza runtime, tools ni delivery.

### Dueño

Confirma o corrige significado empresarial material. Esa confirmación es evidencia.

### P6

Cierra la evidencia semántica gobernada.

### P7

Resuelve requisitos, dimensiones y grain.

### P8

Única autoridad de computabilidad.

### F7

Selecciona filas, resuelve joins confirmados, grupos, filtros y provenance. No suma ni aplica fórmulas.

### F8 / FormulaEngineService

Única autoridad matemática. Ejecuta agregaciones y fórmulas gobernadas.

### F9

Construye ResultSet, findings factuales, outcome e integridad. No inventa causalidad.

### F13

Conserva snapshots históricos inmutables y tenant-scoped. No recalcula ni reinterpreta.

### UI

Presenta ResultSets y estados. No hace matemática empresarial.

## 5. F12 — catálogo analítico

F12 declara AnalysisPlans para análisis escalares, agrupados, rankings y series. La incorporación de un análisis no debe crear una nueva raíz, parser o engine.

Sobre `cafeteria_abc.xlsx` se observaron 21 análisis computables y un bloqueo correcto de `catalog_price_variance_by_product` por falta de `list_price` gobernado.

## 6. RC1 — convergencia de ejecución

Antes de RC1 la Web coordinaba F7/F8/F9 directamente. RC1 dejó:

```text
WEB
→ run_service_1_governed_analysis_v1
→ product root
→ F10/P7/P8
→ F7
→ F8
→ F9
→ F13
→ packet
→ WEB render
```

Gate:

```text
WEB_DIRECT_F7_CALLS = 0
WEB_DIRECT_F8_CALLS = 0
WEB_DIRECT_F9_CALLS = 0
ONE_CANONICAL_PRODUCT_ROOT = PASS
NO_PARALLEL_PRODUCTIVE_PIPELINE = PASS
```

## 7. Memoria y reentrada

F13 ya posee persistencia durable con:

```text
persist_result_memory
list_result_memory
load_result_memory_record
```

RC3 implementa la superficie de producto:

```text
/cases
→ tenant
→ list_result_memory
→ memory_record_id
→ load_result_memory_record
→ validate tenant + identity + digest
→ render persisted ResultSet
```

RC3 quedó committeado y congelado sin volver a cargar XLSX, sin LLM, sin semantic rebind y sin recalculación. La prueba online tras restart real permanece pendiente para RC7.

## 8. Journeys legacy certificados

El último corte productivo documentado mantiene:

```text
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: PRODUCTION_CERTIFIED
WORKING_CAPITAL_SEMANTICS: SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
```

Estos journeys coexisten con la arquitectura analítica general F0–F13. La existencia del catálogo F12 no amplía automáticamente el contrato comercial.

## 9. Memoria tenant semántica

```text
owner evidence
→ TenantSemanticContractV1
→ append-only tenant store
→ structural compatibility
→ compatible hint only
→ semantic context
```

No hay auto-confirmación ni semantic rebind por memoria.

## 10. Invariantes

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_SECOND_MATH_AUTHORITY
NO_LLM_RUNTIME_AUTHORITY
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
P6_P7_P8_REMAIN_SEPARATE
P8_IS_COMPUTABILITY_AUTHORITY
NO_UI_BUSINESS_MATH
FAIL_CLOSED
NO_CAFETERIA_HARDCODE
NO_RUBRO_HARDCODE
```

## 11. Frente actual

```text
full suite current RC
→ deploy exact SHA + real external LLM
→ online cafeteria acceptance
→ online F13 reentry after restart
→ final production smoke
```
