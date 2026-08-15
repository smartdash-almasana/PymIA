# PymIA — autoridad documental actual

**Fecha de reconciliación:** 2026-08-14

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

EXTERNAL_LLM_PROVIDER: NOT_CONNECTED
SAFE_DETERMINISTIC_SEMANTIC_PROVIDER: ACTIVE
NEW_PRODUCTIVE_CAPABILITY_AUTHORIZED: NO
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1: CLOSED_PASS
SERVICE_1_FINAL_SANITATION_REGRESSION_AND_CLOSURE_V1: PASS
SERVICE_1_TECHNICAL_CLOSURE: PASS
```

## Núcleo documental rector

Estos documentos forman la superficie de continuidad de Servicio 1:

- `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md` — estado productivo vigente, journeys certificados y deuda abierta.
- `docs/current/SERVICE_1_STATUS.md` — inventario técnico resumido y verificable.
- `docs/current/SERVICE_1_CANONICAL_AXIS.md` — eje canónico e invariantes permanentes.
- `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md` — prohibiciones y límites de autoridad.
- `docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md` — mapa de componentes y carriles actuales.
- `docs/current/ACTIVE_ROADMAP.md` — única secuencia de trabajo autorizada.
- `docs/current/SERVICE_1_OPERABILITY_PACKET.md` — operación local/producción y política de certificación.
- `docs/current/SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1.md` — contrato de despliegue Cloud Run/Supabase.
- `docs/current/SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1.md` — contrato del producto vendible vigente.

Gobierno de presentación únicamente:

- `SERVICE_1_ENTERPRISE_VISUAL_SYSTEM_V1.md` — UX/presentación; nunca autoridad de cálculo, semántica o ejecución.

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
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
P8_REMAINS_COMPUTABILITY_AUTHORITY
```

## Frente vigente

```text
SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1: CLOSED_PASS
SERVICE_1_FINAL_SANITATION_REGRESSION_AND_CLOSURE_V1: PASS
SERVICE_1_TECHNICAL_CLOSURE: PASS
```

El cierre técnico de Servicio 1 está declarado con evidencia (full suite 3602/0/7, baseline BLOCKERS NONE, smoke final PASS, LIQ_001/REN_001/WORKING_CAPITAL re-certificados en producción). Permanecen congelados nuevas features, nuevas capabilities, provider externo, expansión de `working_capital`, DPO/payment_collection_gap y Servicio 2 hasta nueva autorización de ciclo.

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
