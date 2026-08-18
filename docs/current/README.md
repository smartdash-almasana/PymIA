# PymIA — autoridad documental actual

**Fecha de reconciliación:** 2026-08-16

Esta carpeta contiene documentación vigente, evidencia histórica y documentos de cortes anteriores. **La presencia física en `docs/current/` no concede autoridad.** Sólo gobiernan los documentos enumerados en este índice, subordinados siempre al código físico y a los tests observados.

## Jerarquía de verdad

1. Código físico del checkout y evidencia de tests realmente ejecutados.
2. `AGENTS.md` y `ARCHITECTURE_GUARDRAILS.md`.
3. Este índice y los documentos rectores enumerados abajo.
4. ADR/contratos citados explícitamente por un documento rector.
5. Evidencia técnica histórica, únicamente dentro del alcance que certificó.

Landing, conversaciones, pilots, closeouts, roadmaps vencidos, TaskSpecs consumados y auditorías históricas no gobiernan implementación por sí mismos.

## Estado de autoridad actual

```text
CANONICAL_PRODUCT_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
ONE_CANONICAL_PRODUCT_ROOT: ENFORCED
NO_SECOND_XLSX_PARSER: ENFORCED
NO_LLM_RUNTIME_AUTHORITY: ENFORCED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION: ENFORCED

MAIN_HEAD: 26ef6c8c57bb201da1a36a1073147c641d1309f4
LLM_COLUMN_INTERPRETER_IMPLEMENTATION: MERGED_IN_MAIN
SEQUENTIAL_OWNER_CORROBORATION: MERGED_IN_MAIN
PRODUCTION_DEPLOYMENT_OF_SEMANTIC_RECEPTION_CUT: PENDING
EXTERNAL_LLM_RUNTIME_ACTIVATION: NOT_PROVEN
DETERMINISTIC_SEMANTIC_FALLBACK: PRESERVED
LLM_AUTHORITY: NONE

SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
PRODUCTION_APP_SHA: d2c9c24
PRODUCTION_CLOUD_RUN_REVISION: pymia-service1-00008-mtf
PRODUCTION_TRAFFIC: 100%
PRODUCTION_SMOKE_RUNNER_HEAD: e26f7acfaf5c68c1e5aaad1380992d5f4034883c

LIQ_001: PRODUCTION_CERTIFIED
REN_001: PRODUCTION_CERTIFIED

WORKING_CAPITAL:
  TECHNICAL_E2E_READY: YES
  SEMANTIC_SCOPING: SEM8_COMPOSITE_SCOPE_PRODUCTION_PASS
  PRODUCTION_CERTIFIED: YES

NEW_PRODUCTIVE_CAPABILITY_AUTHORIZED: NO
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1: CLOSED_PASS
SERVICE_1_FINAL_SANITATION_REGRESSION_AND_CLOSURE_V1: PASS
SERVICE_1_TECHNICAL_CLOSURE: PASS

PYMIARADAR: FUTURE_REFERENCE_ONLY / OUT_OF_CURRENT_SERVICE_1_SCOPE
```

El estado de `main` y el estado de producción no deben confundirse: el corte de recepción semántica secuencial con provider PydanticAI está integrado en `main`, pero todavía no está certificado como desplegado en producción. La implementación conserva fallback determinístico y el LLM no adquiere autoridad matemática, de runtime, tools, persistencia ni delivery.

## Núcleo documental rector

Estos documentos forman la superficie de continuidad de Servicio 1:

- `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md` — estado productivo vigente, journeys certificados y deuda abierta.
- `docs/current/SERVICE_1_STATUS.md` — inventario técnico resumido y verificable.
- `docs/current/SERVICE_1_CANONICAL_AXIS.md` — eje canónico e invariantes permanentes.
- `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md` — prohibiciones y límites de autoridad.
- `docs/current/SERVICE_1_F1_MATHEMATICAL_AUTHORITY_SPEC_V1.md` — autoridad matemática F1 congelada, deuda de agregación explícitamente diferida a F8.
- `docs/current/SERVICE_1_F2_CANONICAL_FORMULA_SOURCE_SPEC_V1.md` — fuente canónica F2 de reglas de fórmula, proyección de catálogo y deuda de agregación.
- `docs/current/SERVICE_1_F3_ANALYSIS_PLAN_SPEC_V1.md` — contrato declarativo F3 de intención analítica, sin autoridad de ejecución.
- `docs/current/SERVICE_1_F4_P7_ANALYSIS_GRAIN_SPEC_V1.md` — extensión F4 del P7 canónico para requisitos analíticos y grain resuelto, sin computabilidad ni ejecución.
- `docs/current/SERVICE_1_F5_P8_ANALYSIS_COMPUTABILITY_SPEC_V1.md` — extensión F5 del P8 canónico para computabilidad de `AnalysisPlan`, sin ejecución analítica.
- `docs/current/SERVICE_1_F6_SEMANTIC_DIMENSIONS_AND_RELATIONSHIPS_SPEC_V1.md` — semántica dimensional F6 y relaciones owner-confirmables generales, sin joins ni ejecución.
- `docs/current/SERVICE_1_F7_GOVERNED_EVIDENCE_PREPARATION_SPEC_V1.md` — preparación gobernada F7 de filas, filtros, joins confirmados y membership de grupos, sin agregación ni fórmulas.
- `docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md` — mapa de componentes y carriles actuales.
- `docs/current/ACTIVE_ROADMAP.md` — única secuencia de trabajo autorizada.
- `docs/current/SERVICE_1_OPERABILITY_PACKET.md` — operación local/producción y política de certificación.
- `docs/current/SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1.md` — contrato de despliegue Cloud Run/Supabase.
- `docs/current/SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1.md` — contrato del producto vendible vigente.

Gobierno de presentación únicamente:

- `SERVICE_1_ENTERPRISE_VISUAL_SYSTEM_V1.md` — UX/presentación; nunca autoridad de cálculo, semántica o ejecución.

Modelo arquitectónico conceptual subordinado:

- `PYMIA_FIVE_BRAINS_AND_COHERENCE_SOVEREIGNTY_V1.md` — organiza la arquitectura en cinco cerebros (determinístico, matemático, semántico, memoria y cognitivo) y explicita la soberanía por coherencia del conjunto. No reemplaza P6/P7/P8, kernel ni la raíz productiva canónica.

Referencia futura fuera del frente vigente:

- `docs/PYMIARADAR_PRODUCT_ARCHITECTURE_V1.md` — definición conceptual futura. `REFERENCE_ONLY`; no gobierna Servicio 1, no autoriza implementación de Radar y queda fuera del camino crítico hasta finalizar Servicio 1.

## Documentos subordinados

Algunas evidencias y decisiones previas siguen indexadas porque tests y operación las usan como referencias acotadas, pero **no gobiernan el próximo paso**:

- `SERVICE_1_CONTROLLED_PILOT_SERIES_PLAN.md`
- `SERVICE_1_FIRST_OPERATORLESS_CASE.md`
- `SERVICE_1_NEXT_PRODUCTIVE_CAPABILITY_DECISION.md`
- `SERVICE_1_PRODUCT_COMPLETION_GATE.md`
- `SERVICE_1_PILOT_003_TEXTIL_COMPLEJA.md`
- `SERVICE_1_PILOT_004_DISTRIBUIDORA_MAYORISTA.md`
- `SERVICE_1_PILOT_005_FABRICA_INDUSTRIAL.md`
- `SERVICE_1_PILOT_006_TALLER_MECANICO.md`
- `SERVICE_1_PILOT_007_CONSTRUCTORA.md`
- `SERVICE_1_PILOT_008_TEXTIL_COMPLETA.md`

Todo otro archivo en `docs/current/` se clasifica, hasta su eliminación física, como una de estas categorías:

```text
EVIDENCE_ONLY
HISTORICAL_CLOSEOUT
CONSUMED_TASKSPEC
SUPERSEDED_AUDIT
PILOT_RECORD
REFERENCE_ONLY
```

No puede definir el próximo paso ni contradecir el núcleo rector anterior.

## Deuda arquitectónica abierta

```text
SEMANTIC_FORK_WORKING_CAPITAL: CLOSED_PRODUCTION_PASS
MULTIPLE_REENTRY_MECHANISMS: OPEN
LEGACY_P8/P6_COMPATIBILITY_PROJECTIONS: OPEN
UNUSED_SANDBOX_SLICES: NEEDS_CLASSIFICATION
```

La deuda se clasifica con Graphify + búsqueda física + tests en `KEEP / MIGRATE / DELETE_CANDIDATE`. No se elimina código por nombre o antigüedad.

## Política de saneamiento

La política vigente es la de `docs/README.md`:

```text
NO_MUSEUM_DIRECTORY
NO_ARCHIVE_DIRECTORY
GIT_PRESERVES_HISTORY
CORRECT_EXISTING_CANONICAL_DOCS_BEFORE_CREATING_NEW_ONES
```

La documentación obsoleta se elimina del árbol activo sólo con prueba de que no es dependencia vigente. No se crea un museo paralelo.

## Fronteras explícitas

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_LLM_RUNTIME_AUTHORITY
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
SEMANTIC_ASSISTANCE_IS_NOT_AUTHORITY
DERIVED_EVIDENCE_IS_NOT_FORMULA_AUTHORITY
FORMULA_ENGINE_IS_FORMULA_EXECUTION_AUTHORITY
P8_REMAINS_COMPUTABILITY_AUTHORITY
ANALYSIS_PLAN_EXECUTION_AUTHORITY_NONE
```

## Frente vigente

```text
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1: CLOSED_PASS
SERVICE_1_FINAL_SANITATION_REGRESSION_AND_CLOSURE_V1: PASS
SERVICE_1_TECHNICAL_CLOSURE: PASS
SEMANTIC_RECEPTION_SEQUENTIAL_CUT: MERGED_IN_MAIN
PRODUCTION_DEPLOYMENT_OF_SEMANTIC_RECEPTION_CUT: PENDING
PRODUCTION_SMOKE_OF_SEMANTIC_RECEPTION_CUT: PENDING
PYMIARADAR: OUT_OF_SCOPE_UNTIL_SERVICE_1_FINALIZED
```

La prioridad inmediata es desplegar y certificar en producción el corte ya integrado de recepción semántica secuencial. No se autoriza ninguna expansión adicional de producto durante ese cierre.

## Regla operativa de mantenimiento

```text
una tarea
→ una verificación
→ un resultado
→ una decisión
→ documento rector actualizado si cambia la verdad
→ commit temático
→ worktree limpio
```
