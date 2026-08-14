# Servicio 1 — mapa actual de arquitectura y componentes V1

**Estado:** `ACTIVE_ARCHITECTURE_MAP`  
**Fecha de corte:** 2026-08-14

## 1. Autoridad productiva

```text
CLI:  pymia/cli/service_1_product.py
WEB:  pymia/smartpyme/service_1_assisted_web_v1.py
ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
```

Sólo `service_1_product_pipeline_v1.py` es raíz productiva. La CLI y la web son entradas/adaptadores hacia esa raíz.

## 2. Mapa de alto nivel

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
  ├─ baseline determinística segura actual
  └─ provider externo futuro, inyectado desde infraestructura
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

## 3. SEM-1 → SEM-9

```text
SEM-1  WorkbookProfilerV1
SEM-2  provider-neutral closed semantic contract
SEM-3  deterministic semantic proposal validator
SEM-4  minimal owner dialogue planner
SEM-5  canonical owner evidence projection
SEM-6  owner evidence reentry to existing semantic gate/P6
SEM-7  tenant structural compatibility
SEM-8  assisted semantic wiring into canonical product root
SEM-9  assisted web wiring for sellable Cobros/Margen journeys
```

SEM-9 no está completo para toda la web: `working_capital` conserva el piloto semántico legacy en el worktree actual.

## 4. División de autoridad

### Semantic provider

Puede:

```text
proponer significado
proponer relaciones basadas en refs reales
marcar ambigüedad
usar hints tenant compatibles como evidencia histórica
```

No puede:

```text
confirmar por el dueño
crear owner evidence falsa
autorizar runtime/tool/delivery
calcular fórmulas
inventar columnas o relaciones
```

### Owner

Confirma o corrige significado empresarial material. Su confirmación es evidencia, no permiso de ejecución.

### P6/P7/P8

```text
P6 = aprobación semántica gobernada
P7 = match de requisitos + grain
P8 = única autoridad de computabilidad
```

### Derived Evidence

Transforma evidencia confirmada en variables canónicas cuando el workbook no trae directamente el agregado requerido por la fórmula.

Ejemplo REN_001:

```text
Ventas.Cantidad
Ventas.PrecioUnitario
Ventas.Descuento
Ventas.ProductoID
Productos.ProductoID
Productos.Costo
↓
relación owner-confirmed + unidad owner-confirmed
↓
period_sales_total / sale_price
period_costs_total / costs
```

Derived Evidence no ejecuta la fórmula final y no inventa impuestos ausentes.

### Kernel

```text
pymia/services/formula_engine_service.py
```

Es la autoridad de ejecución matemática. Los evaluators validan/adaptan y proyectan resultados; no deben mantener implementaciones matemáticas paralelas.

## 5. REN_001 actual

```text
formula_id: REN_001_margen_neto_real
expression: ((sale_price - costs - taxes) / sale_price) * 100
```

La fórmula se ejecuta en el kernel.

La web ya no posee un cálculo manual de margen disponible. La ausencia de impuestos o unidad de descuento material bloquea/solicita evidencia; no genera defaults silenciosos.

## 6. Memoria tenant

```text
owner evidence
→ TenantSemanticContractV1
→ append-only tenant store
→ structural signature
→ SEM-7 compatibility classification
→ compatible hint only
→ SEM-2 context
```

Estados:

```text
COMPATIBLE_HINT
OBSOLETE_HINT
LEGACY_UNVERIFIED_HINT
```

Ninguno autoriza reutilización automática.

## 7. Provider actual

```text
EXTERNAL_LLM_PROVIDER: NOT_CONNECTED
DEFAULT_SAFE_PROVIDER: service_1_deterministic_semantic_proposal_provider_v1.py
```

El default seguro sólo proyecta hipótesis determinísticas relevantes y relaciones estructurales verificables al contrato SEM-2.

Los SDK de providers externos no deben importarse dentro de `pymia/` bajo la política actual. La integración futura entra desde bootstrap/infraestructura por callable inyectado.

## 8. Superficie web

```text
Cobros:         SEM-8 assisted semantics
Margen Real:    SEM-8 assisted semantics + Derived Evidence
Working Capital: legacy pilot semantics retained
Consorcios/reconciliation/RADAR: superficies acotadas ya existentes; no son segunda raíz
```

## 9. Invariantes arquitectónicos

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

## 10. Estado de certificación

```text
LAST_DEPLOYED_PRODUCTION_CUT: smoke PASS
CURRENT_WORKTREE_CUT: 297 relevant tests PASS
CURRENT_WORKTREE_FULL_SUITE: PASS_BY_EXHAUSTIVE_SHARDS (3614 PASS / 7 SKIPPED / 0 FAILED)
CURRENT_WORKTREE_DEPLOYED: NO
```

No ampliar claims más allá de esas fronteras.
