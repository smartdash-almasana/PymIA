# SERVICE_1_CURRENT_PRODUCT_STATE_V1

**Fecha de corte:** 2026-08-14
**Estado:** `CURRENT_AUTHORITY`

## 1. Estado ejecutivo

```text
CANONICAL_PRODUCT_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
SERVICE_1_TECHNICAL_BASELINE: CLOSED
SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
PRODUCTION_APP_SHA: 225f2c4
PRODUCTION_CLOUD_RUN_REVISION: pymia-service1-00006-h45
PRODUCTION_TRAFFIC: 100%
SERVICE_1_PRODUCTION_SMOKE: PASS
LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED
WORKING_CAPITAL: PRODUCTION_CERTIFIED
WORKING_CAPITAL_SEMANTICS: SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
LOCAL_SANITATION_CUT: LEGACY_COMPUTATION_PLAN_PROJECTION_REMOVED / 3_DEAD_SANDBOX_SLICES_REMOVED
LOCAL_SANITATION_DEPLOYED: NO
NEW_PRODUCTIVE_CAPABILITY_AUTHORIZED: NO
```

Servicio 1 ya no está en estado de worktree pendiente de release. El corte SEM-1→SEM-9 para Cobros/Margen, Derived Evidence REN_001, persistencia durable de owner evidence y hardening SEM-8 está integrado, desplegado y certificado en producción.

## 2. Cadena canónica vigente

```text
canonical XLSX ingestion
→ WorkbookProfiler / physical evidence
→ semantic assistance proposal
→ deterministic validation
→ owner material confirmation
→ canonical owner evidence
→ P6 ApprovalDecision
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision + GovernedComputationInput
→ Derived Evidence cuando corresponde
→ deterministic execution / kernel
→ bounded outcome
→ controlled delivery
```

Autoridades:

```text
provider/LLM → propone
owner        → confirma significado empresarial
P6/P7/P8    → gobiernan aprobación/requisitos/computabilidad
Derived Evidence → transforma evidencia confirmada en inputs canónicos
kernel       → única autoridad matemática
P10/delivery → controla salida autorizada
```

## 3. SEM-1 → SEM-9

```text
SEM-0 ADR boundary                         CLOSED
SEM-1 WorkbookProfilerV1                  CLOSED
SEM-2 provider-neutral semantic contract  CLOSED
SEM-3 deterministic semantic validator    CLOSED
SEM-4 OwnerDialoguePlanV1                 CLOSED
SEM-5 owner semantic evidence             CLOSED
SEM-6 owner evidence reentry → P6         CLOSED
SEM-7 tenant structural compatibility     CLOSED
SEM-8 canonical product-root wiring       CLOSED
SEM-9 assisted web                        CLOSED_FOR_LIQ_001_AND_REN_001
```

`working_capital` está desplegado y certificado en producción sobre SEM-8 mediante un scope compuesto que reutiliza una única confirmación owner para `projected_closing_cash_balance`, `dso` y `current_ratio`.

## 4. Estado productivo por journey

### LIQ_001 — Control de Cobros y Conciliación

```text
PRODUCTION_CERTIFIED: YES
AUTH_FAIL_CLOSED: PASS
AUTHENTICATED_UPLOAD: PASS
SEM8_OWNER_FLOW: PASS
OWNER_CONFIRMATION: PASS
DETERMINISTIC_EXECUTION: PASS
XLSX_DELIVERY: PASS
```

### REN_001 — Margen Real

```text
PRODUCTION_CERTIFIED: YES
MISSING_TAXES_FAIL_CLOSED: PASS
SEM8_OWNER_FLOW: PASS
RELATIONSHIP_DEDUPLICATION: PASS
DISCOUNT_UNIT_CONFIRMATION: PASS
DERIVED_EVIDENCE: PASS
DETERMINISTIC_EXECUTION: PASS
XLSX_DELIVERY: PASS
```

La fórmula permanece gobernada por `FormulaEngineService/kernel`. Derived Evidence no inventa impuestos ni interpreta descuentos no confirmados.

### working_capital — Caja y Capital de Trabajo

```text
TECHNICAL_E2E_READY: YES
PRODUCTION_CERTIFIED: YES
SEMANTIC_SCOPING: SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
COMPONENTS:
- projected_closing_cash_balance
- dso
- current_ratio
OWN_COMPOSITE_DELIVERY: NO
```

No incorporar DPO ni `payment_collection_gap` durante el frente de sanidad; no forman parte del corte certificado.

## 5. Persistencia y reentry

Producción certificó:

```text
PERSISTED_CASE_LISTING: PASS
PERSISTED_CASE_REENTRY: PASS
DURABLE_REENTRY_SCOPE: OWNER_EVIDENCE_ONLY
```

La reentrada durable actual prueba evidencia semántica persistida del owner. No implica restauración durable del XLSX ni del snapshot completo de resultado tras reinicio.

## 6. Tenant semantics

```text
TENANT_SEMANTIC_CONTRACT: IMPLEMENTED
TENANT_STORE: APPEND_ONLY / TENANT_ISOLATED
STRUCTURAL_COMPATIBILITY: IMPLEMENTED
COMPATIBLE_MEMORY: HINT_ONLY
AUTOMATIC_REUSE: FORBIDDEN
SEMANTIC_REBIND: FORBIDDEN
```

## 7. Provider semántico

```text
EXTERNAL_LLM_PROVIDER: NOT_CONNECTED
DETERMINISTIC_SAFE_BASELINE_PROVIDER: ACTIVE
semantic_provider=<callable>
```

La frontera de provider no posee autoridad semántica final, matemática, de runtime ni de delivery.

## 8. Deuda arquitectónica abierta

```text
1. run_owner_reentry ya no es caller del canonical product root; queda aislado en un adapter SUPPORT_NECESSARY para compatibilidad CLI/harness históricos.
2. la proyección legacy build_computation_plan/ComputationPlanV1 fue removida localmente; P8 canónico conserva la cobertura.
3. tres completion slices sandbox sin callers productivos fueron removidos localmente junto con sus tests directos.
4. persisten compatibilidades P6/reentry que requieren clasificación antes de eliminación.
5. la documentación histórica debe permanecer fuera de autoridad activa.
```

Estas deudas no invalidan la certificación productiva de LIQ_001/REN_001, pero son el frente prioritario de sanidad antes de ampliar producto.

## 9. Invariantes

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_LLM_RUNTIME_AUTHORITY
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
P7_REQUIREMENT_MATCH_PRECEDES_P8
P8_IS_COMPUTABILITY_AUTHORITY
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
DERIVED_EVIDENCE_NEVER_INVENTS_MISSING_MATERIAL_INPUTS
```

## 10. Frente actual

```text
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1
```

Secuencia:

```text
1. documentation authority sync
2. physical journey map
3. legacy dependency inventory
4. converge web journeys
5. normalize persistence/reentry/delivery policies
6. delete proven dead paths
7. full regression
8. production recertification
```

Features, nuevas capabilities, provider externo y expansión de `working_capital` permanecen congelados hasta cerrar este frente.
