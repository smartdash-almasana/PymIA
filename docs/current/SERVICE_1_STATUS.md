# Servicio 1 — estado técnico actual

**Fecha de corte:** 2026-08-14
**Autoridad de continuidad:** `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

## Resumen

```text
CANONICAL_PRODUCT_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO
LAST_DEPLOYED_PRODUCTION_SMOKE: PASS (2026-08-13)
CURRENT_WORKTREE_SEM_1_TO_9: IMPLEMENTED
DERIVED_EVIDENCE_REN_001: IMPLEMENTED
REN_001_FORMULA_AUTHORITY: KERNEL_ONLY
EXTERNAL_LLM_PROVIDER: NOT_CONNECTED
SAFE_DETERMINISTIC_PROVIDER: ACTIVE
KERNEL GENÉRICO PRODUCTIVO: ACTIVO
SIN DIAGNÓSTICO CAUSAL
WORKING_CAPITAL_SEMANTICS: LEGACY_PILOT
RELEVANT_REGRESSION: 297 PASS
FULL_SUITE_COVERAGE: PASS_BY_EXHAUSTIVE_SHARDS
FULL_SUITE_RESULT: 3614 PASS / 7 SKIPPED / 0 FAILED
MONOLITHIC_MCP_RUNNER: HTTP_502_TIMEOUT
CURRENT_WORKTREE_COMMIT: NO
CURRENT_WORKTREE_DEPLOYED: NO
12/12 PATOLOGÍAS PRODUCTIVAS CONECTADAS: CONSERVADAS
```

## Autoridad productiva

Entrada CLI canónica:

```text
pymia/cli/service_1_product.py
```

Raíz productiva única:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

Web productiva:

```text
pymia/smartpyme/service_1_assisted_web_v1.py
```

La web es superficie de interacción; no es autoridad matemática ni segunda raíz de negocio.

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
→ deterministic execution/kernel
→ bounded outcome
→ controlled delivery
```

Autoridades separadas:

```text
provider/LLM → propone
owner        → confirma significado empresarial
P6/P7/P8    → gobiernan aprobación/requisitos/computabilidad
Derived Evidence → transforma evidencia confirmada en inputs canónicos
kernel       → ejecuta fórmulas
P10/delivery → controla salida autorizada
```

## SEM-1 → SEM-9

| Corte | Estado | Responsabilidad |
|---|---|---|
| SEM-1 | PASS | WorkbookProfilerV1 sobre normalized_tables canónicas |
| SEM-2 | PASS | contrato provider-neutral, sin SDK |
| SEM-3 | PASS | validator determinístico, fail-closed |
| SEM-4 | PASS | diálogo owner mínimo y agrupado |
| SEM-5 | PASS | proyección a evidencia owner canónica |
| SEM-6 | PASS | reentry hacia reinjection/P6 existente |
| SEM-7 | PASS | compatibilidad estructural de memoria tenant |
| SEM-8 | PASS | wiring a la raíz productiva canónica |
| SEM-9 | PASS acotado | web de Cobros y Margen usa SEM-8; Working Capital conserva piloto legacy |

## REN_001

Fórmula gobernada:

```text
REN_001_margen_neto_real
((sale_price - costs - taxes) / sale_price) * 100
```

Autoridad ejecutable única:

```text
pymia/services/formula_engine_service.py
```

`service_1_ren_001_evaluator_v1.py` valida/proyecta, pero no mantiene otra implementación matemática.

Derived Evidence puede construir `sale_price` y `costs` desde líneas/relaciones confirmadas. No pone `taxes=0` por ausencia y no interpreta descuentos no nulos sin evidencia owner de unidad.

## Tenant semantics

```text
TENANT_SEMANTIC_CONTRACT: IMPLEMENTED
TENANT_STORE: APPEND_ONLY / TENANT_ISOLATED
STRUCTURAL_COMPATIBILITY: IMPLEMENTED
COMPATIBLE_MEMORY: HINT_ONLY
AUTOMATIC_REUSE: FORBIDDEN
SEMANTIC_REBIND: FORBIDDEN
```

## Provider externo

No hay SDK externo empaquetado ni provider de red productivo conectado en el worktree actual.

```text
semantic_provider=<callable>
```

es una frontera de inyección. La baseline determinística segura permite operar el contrato SEM-2 sin convertir una heurística en autoridad.

## Producción

El último corte desplegado conserva evidencia de smoke PASS. El worktree SEM-1→SEM-9 ya cerró cobertura completa por shards exhaustivos y todavía necesita commit, deploy y smoke propios antes de reemplazar esa baseline en producción.

## Gate de release actual

```text
1. REVIEW WORKTREE CLASSIFICATION
2. AUTHORIZED THEMATIC COMMITS
3. DEPLOY NEW SHA
4. PRODUCTION_SMOKE NEW SHA
```

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
