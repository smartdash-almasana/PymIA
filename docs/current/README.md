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

LAST_DEPLOYED_PRODUCTION_CUT:
  CLOUD_RUN: DEPLOYED
  PRODUCTION_SMOKE: PASS (2026-08-13)

CURRENT_WORKTREE_CUT:
  SEM_1_TO_SEM_9: IMPLEMENTED
  DERIVED_EVIDENCE_REN_001: IMPLEMENTED
  REN_001_FORMULA_AUTHORITY: KERNEL_ONLY
  ASSISTED_WEB_COBROS_AND_MARGIN: SEM_8_WIRED
  EXTERNAL_LLM_PROVIDER: NOT_CONNECTED
  SAFE_DETERMINISTIC_SEMANTIC_PROVIDER: ACTIVE_FALLBACK
  WORKING_CAPITAL_SEMANTICS: LEGACY_PILOT_RETAINED
  RELEVANT_REGRESSION: 297 passed
  FULL_SUITE_COVERAGE: PASS_BY_EXHAUSTIVE_SHARDS
  FULL_SUITE_RESULT: 3614 passed / 7 skipped / 0 failed
  MONOLITHIC_MCP_RUNNER: HTTP_502_TIMEOUT
  COMMIT: NOT_DONE
  DEPLOYMENT: NOT_DONE
```

Nunca usar el smoke del corte desplegado para afirmar que el worktree SEM-1→SEM-9 ya está certificado en producción.

## Núcleo documental rector

Estos documentos forman la superficie de continuidad de Servicio 1:

- `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md` — estado vigente, diferencia entre baseline desplegado y worktree actual, gates y deuda real.
- `docs/current/SERVICE_1_STATUS.md` — inventario técnico resumido y verificable.
- `docs/current/SERVICE_1_CANONICAL_AXIS.md` — eje canónico e invariantes permanentes.
- `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md` — prohibiciones y límites de autoridad.
- `docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md` — mapa de componentes actuales, incluida la cadena SEM-1→SEM-9 y Derived Evidence.
- `docs/current/ACTIVE_ROADMAP.md` — única secuencia de trabajo autorizada.
- `docs/current/SERVICE_1_OPERABILITY_PACKET.md` — operación local/producción y gates de release.
- `docs/current/SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1.md` — contrato de despliegue Cloud Run/Supabase.
- `docs/current/SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1.md` — contrato del producto vendible vigente.

Gobierno de presentación únicamente:

- `SERVICE_1_ENTERPRISE_VISUAL_SYSTEM_V1.md` — UX/presentación; nunca autoridad de cálculo, semántica o ejecución.

## Documentos subordinados

Algunas evidencias y decisiones previas siguen indexadas porque tests y operación las usan como referencias acotadas, pero **no gobiernan el próximo paso**:

- `SERVICE_1_CONTROLLED_PILOT_SERIES_PLAN.md` — evidencia/plan de la serie controlada histórica.
- `SERVICE_1_FIRST_OPERATORLESS_CASE.md` — evidencia del primer caso operatorless certificado en su corte.
- `SERVICE_1_NEXT_PRODUCTIVE_CAPABILITY_DECISION.md` — conserva la decisión de no promover nuevas capabilities antes de hardening/certificación.
- `SERVICE_1_PRODUCT_COMPLETION_GATE.md` — evidencia del cierre MVP del corte histórico que lo certificó; no sustituye el estado worktree actual.
- `SERVICE_1_PILOT_003_TEXTIL_COMPLEJA.md` — evidencia del piloto 003.
- `SERVICE_1_PILOT_004_DISTRIBUIDORA_MAYORISTA.md` — evidencia del piloto 004.
- `SERVICE_1_PILOT_005_FABRICA_INDUSTRIAL.md` — evidencia del piloto 005.
- `SERVICE_1_PILOT_006_TALLER_MECANICO.md` — evidencia del piloto 006.
- `SERVICE_1_PILOT_007_CONSTRUCTORA.md` — evidencia del piloto 007.
- `SERVICE_1_PILOT_008_TEXTIL_COMPLETA.md` — evidencia del piloto 008.

Todo otro archivo en `docs/current/` se clasifica, hasta su eliminación física, como una de estas categorías:

```text
EVIDENCE_ONLY
HISTORICAL_CLOSEOUT
CONSUMED_TASKSPEC
SUPERSEDED_AUDIT
PILOT_RECORD
REFERENCE_ONLY
```

No puede definir el “próximo paso” ni contradecir el núcleo rector anterior.

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

No hacer commit ni push como parte de una limpieza documental salvo autorización explícita.
