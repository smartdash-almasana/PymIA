# SERVICE_1_CURRENT_PRODUCT_STATE_V1

**Fecha de corte:** 2026-08-14
**Estado:** `CURRENT_AUTHORITY`

## 1. Estado ejecutivo

```text
CANONICAL_PRODUCT_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
SERVICE_1_TECHNICAL_BASELINE: CLOSED
LAST_DEPLOYED_PRODUCTION_SMOKE: PASS (2026-08-13)
CURRENT_FRONT: SEMANTIC_PRODUCT_INTEGRATION_AND_RELEASE_HARDENING
NEW_PRODUCTIVE_CAPABILITY_AUTHORIZED: NO
```

Hay dos estados que no deben mezclarse:

```text
A. LAST_DEPLOYED_PRODUCTION_CUT
   Cloud Run desplegado y smokeado con PASS.

B. CURRENT_WORKTREE_CUT
   SEM-1→SEM-9 + Derived Evidence + REN_001 kernel convergence.
   Todavía sin commit, sin deploy y sin production smoke propio.
```

## 2. Worktree actual verificado

```text
SEM-0 ADR-029 boundary                         CLOSED
SEM-1 WorkbookProfilerV1                       CLOSED
SEM-2 provider-neutral semantic contract       CLOSED
SEM-3 deterministic semantic validator         CLOSED
SEM-4 OwnerDialoguePlanV1                      CLOSED
SEM-5 owner semantic evidence                  CLOSED
SEM-6 owner evidence reentry → existing P6     CLOSED
SEM-7 tenant structural compatibility          CLOSED
SEM-8 canonical product-root semantic wiring   CLOSED
SEM-9 assisted web → SEM-8                     CLOSED_FOR_COBROS_AND_MARGIN
```

Además:

```text
DERIVED_EVIDENCE_ENGINE_REN_001: IMPLEMENTED
REN_001_FORMULA_EXECUTION_AUTHORITY: FormulaEngineService/kernel
PARALLEL_WEB_MARGIN_CALCULATION: REMOVED
OWNER_CONFIRMED_PRODUCT_RELATIONSHIP: REQUIRED
DISCOUNT_UNIT_OWNER_EVIDENCE: IMPLEMENTED
IMPLICIT_TAX_ZERO: FORBIDDEN
TENANT_MEMORY_SILENT_REUSE: FORBIDDEN
```

## 3. Evidencia de tests del worktree

Regresión focal/integrada previa:

```text
297 passed in 34.30s
```

Cobertura completa del árbol `tests/` obtenida mediante shards exhaustivos por límite de transporte del MCP:

```text
FULL_SUITE_COVERAGE: PASS_BY_EXHAUSTIVE_SHARDS
PASS: 3614
SKIPPED: 7
FAILED: 0
MONOLITHIC_MCP_RUNNER: HTTP_502_TIMEOUT
```

Los shards cubrieron todos los directorios top-level, todos los tests raíz, `tests/smartpyme` completo y los 151 archivos `test_service_1_*.py` inventariados físicamente. No se añadieron exclusiones ni skips. La única limitación es que no existe una observación monolítica en un único proceso porque el wrapper MCP excede su ventana de transporte.

## 4. Provider semántico

La arquitectura acepta un provider inyectado:

```text
semantic_provider=<callable>
```

Estado:

```text
EXTERNAL_LLM_PROVIDER: NOT_CONNECTED
DETERMINISTIC_SAFE_BASELINE_PROVIDER: ACTIVE
```

La baseline determinística proyecta únicamente evidencia e hipótesis gobernadas al contrato SEM-2. No adquiere autoridad semántica, matemática, de runtime o delivery.

Un provider externo futuro debe entrar desde infraestructura/bootstrap; los SDK de OpenAI/Anthropic/Gemini siguen prohibidos dentro de `pymia/` por la política arquitectónica actual.

## 5. Recorrido actual de Margen Real

```text
XLSX canónico
→ WorkbookProfiler
→ propuesta semántica provider-neutral
→ validator determinístico
→ diálogo owner material
→ SEM-5 evidence
→ SEM-6 / P6 existente
→ relación owner-confirmed
→ Derived Evidence Engine
→ P8
→ GovernedComputationInput
→ FormulaEngineService / kernel
→ REN_001 outcome
→ delivery autorizado
```

La semántica decide significado. Derived Evidence transforma evidencia confirmada en variables canónicas. El kernel es la única autoridad de ejecución matemática.

## 6. Superficie web

```text
sold_vs_collected_gap: SEM-8 assisted semantics
net_margin_real:       SEM-8 assisted semantics
working_capital:       legacy pilot semantic scoping retained
```

La retención del piloto `working_capital` es explícita y acotada. No se debe presentar como SEM-9 completo para toda la web.

## 7. Producción

El corte previamente desplegado en Google Cloud Run conserva smoke real PASS con autenticación Supabase, upload autenticado, confirmación owner, ejecución/persistencia, download y reentry.

Ese resultado pertenece al corte desplegado anterior. El worktree actual necesita, en este orden:

```text
1. revisar la clasificación final del worktree
2. commit(s) temáticos autorizados
3. deploy del nuevo corte
4. production smoke del nuevo SHA
```

## 8. Invariantes

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

## 9. Siguiente gate

```text
NEXT_GATE: THEMATIC_COMMIT_CUT_AWAITING_APPROVAL
```

No conectar un provider LLM externo, no ampliar capacidades ni desplegar el worktree actual antes de separar los cambios runtime/documentación de los cambios landing/visual y realizar los commits temáticos autorizados.

## 10. Clasificación del worktree para commit hygiene

Estado físico observado el 2026-08-14:

### A. Runtime/semántica Servicio 1 — mismo corte lógico

```text
pymia/services/formula_engine_service.py
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/smartpyme/service_1_assisted_web_v1.py
pymia/smartpyme/service_1_computability_v1.py
pymia/smartpyme/service_1_ren_001_evaluator_v1.py
pymia/smartpyme/service_1_ren_001_normalized_evidence_v1.py
pymia/smartpyme/service_1_*semantic*
pymia/smartpyme/service_1_derived_evidence_v1.py
pymia/smartpyme/service_1_owner_unit_confirmation_event_v1.py
pymia/smartpyme/service_1_*tenant*
corresponding tests/smartpyme/test_service_1_*.py
```

Este grupo representa SEM-1→SEM-9, tenant compatibility/persistence, Derived Evidence y convergencia REN_001/kernel.

### B. Documentación de autoridad — corte separado

```text
docs/README.md
docs/current/README.md
docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
docs/current/ACTIVE_ROADMAP.md
docs/current/SERVICE_1_OPERABILITY_PACKET.md
docs/current/SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1.md
docs/adr/ADR-029-service-1-llm-semantic-assistance-boundary.md
```

### C. Landing / visual — preservar fuera del commit runtime

```text
landing/src/components/*
landing/src/styles/global.css
landing/DESIGN.md
docs/current/SERVICE_1_ENTERPRISE_VISUAL_SYSTEM_V1.md
```

Este grupo no gobierna runtime y no debe mezclarse con el commit técnico SEM-1→SEM-9.

### D. Documentación histórica tocada por reconciliación

```text
docs/current/SERVICE_1_DOCUMENTARY_PURGE_AUDIT_V2.md
docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md
```

Se modificaron sólo para marcar su estado `SUPERSEDED_REFERENCE_ONLY` y evitar que vuelvan a gobernar decisiones.

### Regla de commit

```text
A ≠ C
B puede acompañar A sólo si describe exactamente ese mismo corte.
D es hygiene documental y puede mantenerse separado.
NO_PUSH_WITH_DIRTY_UNRELATED_LANDING
```

No se hizo commit ni push durante `REPO_AND_DOCUMENTATION_HYGIENE_V1`.
