# PYMIA — autoridad documental actual de Servicio 1

**Fecha de reconciliación:** 2026-08-23
**Estado:** `CURRENT_AUTHORITY_INDEX`

Esta carpeta contiene documentos vigentes y evidencia histórica. La presencia física en `docs/current/` no concede autoridad por sí sola.

## Jerarquía de verdad

1. código físico del checkout;
2. tests realmente observados;
3. `AGENTS.md` y `ARCHITECTURE_GUARDRAILS.md`;
4. este índice y los documentos rectores enumerados abajo;
5. evidencia histórica sólo dentro del alcance que certificó.

## Convergencia integral vigente — 2026-08-23

La **arquitectura objetivo de Servicio 1 quedó cerrada dialécticamente** después de cuatro rondas adversariales y una micro-ronda final. Esto cierra decisiones de diseño; **no certifica el código actual** ni autoriza por sí solo commit/push/deploy.

Documentos de evidencia y método:

- `SERVICE_1_INTEGRAL_HEALTH_AUDIT_PLAN_V1.md` — método de auditoría y reconstrucción; no crea autoridad.
- `SERVICE_1_FINAL_ARCHITECTURE_DIALECTIC_V1.md` — dossier no normativo de la deliberación ChatGPT ↔ Qwen; la deliberación quedó cerrada con `OPEN_ARCHITECTURAL_DECISIONS = 0`.
- `SERVICE_1_INTEGRAL_HEALTH_AUDIT_REPORT_V1.md` — evidencia de auditoría física; no sustituye los documentos rectores.

Autoridad normativa final:

```text
ONE_PRODUCTIVE_EXECUTION_ROOT
FOUR_EXPLICIT_EXECUTION_COMMANDS
RESULT_READ_SEPARATE_FROM_EXECUTION
ONE_CANONICAL_WORKBOOK_ENVELOPE
CANONICAL_ENVELOPE_POST_CONSTRUCTION_IMMUTABILITY
WORKBOOK_D1_D7_MANDATORY
D7_EVIDENCE_ONLY
ONE_PRODUCTIVE_SEMANTIC_FSM
TABLE_SCOPED_SEMANTICS_BUILT_ONCE_IN_D6_D7
P7_GRAIN_REQUIREMENT_AUTHORITY
P8_COMPUTABILITY_AND_PROVENANCE_AUTHORITY
F7_ONLY_JOIN_MATERIALIZATION_WITH_RUNTIME_SAFETY
ONE_COMMON_MATH_KERNEL_FORMULA_ENGINE_SERVICE
DECLARATIVE_CLASSIFICATION_WITHOUT_ARITHMETIC
CONTENT_ADDRESSED_SOURCE_ARTIFACT_IDENTITY
NO_FILENAME_AS_WORKBOOK_IDENTITY
NO_SHEET1_FALLBACK
SPECIALIZED_REQUEST_ANTI_DUMP_CRITERIA
F13_RESULT_READ_NO_RECALCULATION
NO_LLM_MATH_OR_RUNTIME_AUTHORITY
NO_IMPLICIT_SHAPE_DISPATCH
NO_INDEFINITE_COMPATIBILITY_SHIMS
```

Regla documental obligatoria: una decisión arquitectónica no es autoridad si sólo vive en chat, prompt o `_audit/`. Las decisiones finales ya fueron incorporadas a `SERVICE_1_CANONICAL_AXIS.md` y `SERVICE_1_ARCHITECTURE_LOCK.md`.

Estado actual:

```text
DIALECTICAL_REVIEW_COMPLETE: PASS
OPEN_ARCHITECTURAL_DECISIONS: 0
TARGET_ARCHITECTURE_CLOSED: YES
ARCHITECTURE_NORMATIVE_DOCUMENTATION: UPDATED
RECONSTRUCTION_IMPLEMENTATION: IN_PROGRESS
R0_R1: CLOSED_PASS
R2: CLOSED_PASS
R3: CLOSED_PASS
NEXT_ALLOWED_NODE: R4
CURRENT_WORKTREE_INTEGRAL_CERTIFICATION: NO
FULL_SUITE_AFTER_RECONSTRUCTION: NOT_YET_RUN
REAL_WORKBOOK_E2E_AFTER_RECONSTRUCTION: NOT_YET_RUN
LAST_AUDIT_FULL_SUITE: 3806 passed / 77 failed / 7 skipped / 3 errors
MODULE_REGISTRY_CURRENT_WORKTREE: NOT_RECONCILED
COMMIT_PUSH_DEPLOY: NOT_AUTHORIZED
```

This checkpoint distinguishes the closed target architecture from the in-progress reconstruction, integral certification, and release authorization. R0/R1, R2, and R3 are closed PASS; R4 is the only next authorized node.

Los antiguos Phase 1–4 quedan como historia de la convergencia que motivó la auditoría; **no gobiernan el próximo plan de implementación**. El plan nuevo se deriva del delta entre código actual y arquitectura final, ordenado por dependencias.

## Paquete de handoff ejecutable — lectura obligatoria para cualquier LLM

El handoff de implementación queda cerrado en este conjunto:

```text
SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md
SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md
SERVICE_1_CODE_DISPOSITION_FINAL_V1.md
SERVICE_1_RECONSTRUCTION_PLAN_V1.md
SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md
```

Función de cada archivo:

- `SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md` — punto de entrada, orden de lectura, reglas de continuidad y estado recibido.
- `SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md` — instrucciones operativas permanentes para ejecutores y verificadores.
- `prompts/SERVICE_1_EXECUTOR_PROMPT_R0_R1_V1.md` — prompt ejecutor vigente del próximo nodo autorizado.
- `prompts/SERVICE_1_VERIFIER_PROMPT_R0_R1_V1.md` — prompt read-only de verificación independiente correspondiente.
- `SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md` — diferencia física entre código actual y target final, con archivos y acciones concretas.
- `SERVICE_1_CODE_DISPOSITION_FINAL_V1.md` — destino de los 112 módulos Service 1 mediante registry heredado + overrides + los 11 faltantes reconciliados; `UNKNOWN_TARGET_DISPOSITION = 0`.
- `SERVICE_1_RECONSTRUCTION_PLAN_V1.md` — orden de implementación por dependencias R0–R14, tests por ciclo, gates y stop conditions.
- `SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md` — Definition of Done objetiva; ningún agente puede declarar Servicio 1 terminado fuera de esos gates.

Un agente nuevo **no necesita reconstruir el historial de este chat**. Debe leer el paquete en el orden indicado por el handoff, verificar el estado físico y continuar desde el primer nodo de reconstrucción cuyo exit gate no pase.

Cualquier certificación o despliegue de SHA anteriores permanece como evidencia histórica de ese corte y no certifica el worktree actual.

## Último corte técnico documentado — evidencia histórica, no certificación del worktree actual

Los estados siguientes pertenecen al último corte que los documentó. Se conservan por trazabilidad y **no prevalecen sobre el bloque de convergencia integral 2026-08-23**.

```text
CANONICAL_PRODUCT_ROOT: pymia/smartpyme/service_1_product_pipeline_v1.py
ONE_CANONICAL_PRODUCT_ROOT: ENFORCED
NO_SECOND_XLSX_PARSER: ENFORCED
NO_PARALLEL_PRODUCTIVE_PIPELINE: ENFORCED
NO_SECOND_MATH_AUTHORITY: ENFORCED
NO_LLM_RUNTIME_AUTHORITY: ENFORCED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION: ENFORCED
P8_IS_COMPUTABILITY_AUTHORITY: ENFORCED

RC1_COMMIT: 8a4b6ac21293b5e3803c9d2792d0f5017e2c579c
RC2_COMMIT: f57d0ab715b4fd3bb923dceb67c93c97115e1cbc
RC3_COMMIT: 07f1f9b85591f99dc72d94271b117dfcb6ef6582
TENANT_REENTRY_HARDENING_COMMIT: c9de7497a9e61cfa575975a4c5f5d9815c4855de
RC1: CLOSED_COMMITTED_FROZEN
RC2: CLOSED_COMMITTED_FROZEN
RC3: CLOSED_COMMITTED_FROZEN
TENANT_REENTRY_HARDENING: CLOSED_COMMITTED
RC4: CLOSED_BY_DOCUMENTATION_SYNC

F0_F13: CLOSED_COMMITTED
F12_GENERAL_ANALYTICS: IMPLEMENTED
F13_DURABLE_RESULT_MEMORY: IMPLEMENTED
F13_RESULTSET_REENTRY: CLOSED_COMMITTED_FROZEN

SERVICE_1_RELEASE_CANDIDATE_ACCEPTED: NO
FULL_SUITE_CURRENT_RC: NOT_OBSERVED
ONLINE_EXTERNAL_LLM_CURRENT_RC: NOT_PROVEN
ONLINE_CAFETERIA_ACCEPTANCE_CURRENT_RC: NOT_PROVEN
ONLINE_F13_REENTRY_AFTER_RESTART: NOT_PROVEN
PRODUCTION_SMOKE_CURRENT_RC: NOT_PROVEN

SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS
PRODUCTION_APP_SHA: d2c9c24
PRODUCTION_CLOUD_RUN_REVISION: pymia-service1-00008-mtf
PRODUCTION_TRAFFIC: 100%
```

Los datos de producción anteriores son el último corte certificado documentado. No equivalen a que el release candidate actual esté desplegado.

## Qué está construido

Servicio 1 ya posee:

```text
XLSX canónico
→ perfilado de workbook
→ interpretación semántica acotada
→ confirmación/corrección del dueño
→ P6
→ AnalysisPlan
→ P7 grain/requisitos
→ P8 computabilidad
→ F7 preparación de evidencia
→ F8 matemática bajo FormulaEngineService
→ F9 ResultSet gobernado
→ F10 discovery dinámico
→ F12 catálogo analítico
→ F13 memoria durable de ResultSets
```

RC1 hizo converger la ejecución F12 detrás de la única raíz productiva. RC2 eliminó estado stale entre análisis. RC3 implementa la reentrada de ResultSets persistidos sin recalcular, sin volver a abrir XLSX y sin LLM.

## Frontera comercial

La existencia técnica de AnalysisPlans F12 no autoriza por sí sola ampliar el portfolio vendible. El contrato comercial vigente sigue en `SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1.md` hasta completar acceptance online y sincronización final de release.

## Núcleo documental rector

- `docs/adr/ADR-007-documentation-governance.md` — gobierno documental: ninguna decisión arquitectónica existe como autoridad si sólo vive en chat/prompt/audit.
- `SERVICE_1_CURRENT_PRODUCT_STATE_V1.md` — estado real del producto y release candidate.
- `SERVICE_1_STATUS.md` — resumen técnico verificable.
- `ACTIVE_ROADMAP.md` — secuencia RC vigente.
- `SERVICE_1_CANONICAL_AXIS.md` — eje canónico e invariantes permanentes.
- `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md` — prohibiciones y límites de autoridad.
- `SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md` — mapa actual de componentes y flujo.
- `SERVICE_1_F1_MATHEMATICAL_AUTHORITY_SPEC_V1.md` — autoridad matemática.
- `SERVICE_1_F2_CANONICAL_FORMULA_SOURCE_SPEC_V1.md` — fuente canónica de fórmulas.
- `SERVICE_1_F3_ANALYSIS_PLAN_SPEC_V1.md` — AnalysisPlan.
- `SERVICE_1_F4_P7_ANALYSIS_GRAIN_SPEC_V1.md` — P7 grain/requisitos.
- `SERVICE_1_F5_P8_ANALYSIS_COMPUTABILITY_SPEC_V1.md` — P8 computabilidad.
- `SERVICE_1_F6_SEMANTIC_DIMENSIONS_AND_RELATIONSHIPS_SPEC_V1.md` — dimensiones y relaciones.
- `SERVICE_1_F7_GOVERNED_EVIDENCE_PREPARATION_SPEC_V1.md` — evidencia gobernada.
- `SERVICE_1_F8_MATHEMATICAL_AGGREGATION_RUNTIME_SPEC_V1.md` — agregación matemática.
- `SERVICE_1_F9_RESULT_SET_OUTCOMES_FINDINGS_SPEC_V1.md` — ResultSet y findings factuales.
- `SERVICE_1_F10_DYNAMIC_ANALYSIS_DISCOVERY_SPEC_V1.md` — discovery dinámico.
- `SERVICE_1_F11_CAFETERIA_GENERALIZATION_GATE_V1.md` — generalización física cafetería.
- `SERVICE_1_F12_COMMERCIAL_ANALYSIS_CATALOG_EXPANSION_V1.md` — catálogo declarativo F12.
- `SERVICE_1_F13_LONGITUDINAL_RESULT_MEMORY_V1.md` — memoria longitudinal F13.
- `SERVICE_1_OPERABILITY_PACKET.md` — operación y gates de release.
- `SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1.md` — contrato de despliegue.
- `SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1.md` — frontera comercial.

Modelo conceptual subordinado:

- `PYMIA_FIVE_BRAINS_AND_COHERENCE_SOVEREIGNTY_V1.md`.

## Documentación histórica

Pilots, closeouts, roadmaps consumidos, TaskSpecs terminados, auditorías anteriores y documentos de ciclos pasados son `EVIDENCE_ONLY`, `HISTORICAL_CLOSEOUT`, `CONSUMED_TASKSPEC`, `SUPERSEDED_AUDIT`, `PILOT_RECORD` o `REFERENCE_ONLY`.

Índice histórico explícito exigido por los contratos de continuidad:

- `SERVICE_1_CONTROLLED_PILOT_SERIES_PLAN.md` — `EVIDENCE_ONLY`.
- `SERVICE_1_FIRST_OPERATORLESS_CASE.md` — `HISTORICAL_CLOSEOUT`.
- `SERVICE_1_NEXT_PRODUCTIVE_CAPABILITY_DECISION.md` — `REFERENCE_ONLY`.
- `SERVICE_1_PRODUCT_COMPLETION_GATE.md` — `HISTORICAL_CLOSEOUT`.
- `SERVICE_1_PILOT_003_TEXTIL_COMPLEJA.md` — `PILOT_RECORD`.
- `SERVICE_1_PILOT_004_DISTRIBUIDORA_MAYORISTA.md` — `PILOT_RECORD`.
- `SERVICE_1_PILOT_005_FABRICA_INDUSTRIAL.md` — `PILOT_RECORD`.
- `SERVICE_1_PILOT_006_TALLER_MECANICO.md` — `PILOT_RECORD`.
- `SERVICE_1_PILOT_007_CONSTRUCTORA.md` — `PILOT_RECORD`.
- `SERVICE_1_PILOT_008_TEXTIL_COMPLETA.md` — `PILOT_RECORD`.

Este índice preserva trazabilidad histórica; **ninguno de estos documentos recupera autoridad de implementación sobre el release candidate actual**.

No pueden definir el próximo paso ni contradecir los documentos rectores actuales.

## Frente vigente

```text
RC1 = CLOSED
RC2 = CLOSED
RC3 = CLOSED
TENANT_REENTRY_HARDENING = CLOSED
RC4 = CLOSED
RC5 = DEPLOY EXACT RC + REAL LLM
RC6 = ONLINE CAFETERIA ACCEPTANCE
RC7 = ONLINE RESULT MEMORY REENTRY
```

No crear F14. No reabrir F0–F13 por inercia.

## Regla operativa

```text
una tarea
→ una verificación
→ un resultado
→ una decisión
→ actualización documental si cambia la verdad
→ commit temático
```
