# PymIA — Servicio 1 — Auditoría externa integral de arquitectura, producto y capacidad de generalización

**Fecha:** 2026-08-17
**Auditor:** auditor principal externo (read-only)
**Alcance:** worktree `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`, branch `work/service1-cafeteria-flow-v1`, HEAD `4cda16d42fe804db50daa73aa13c68a144c785c0` + modificaciones F2/F3 no committeadas.
**Estado:** READ-ONLY. No se modificó código, no se commit, no se push.

> TODAS las citas usan `SOURCE / FILE / SYMBOL / LINE / EVIDENCE_TYPE`. Las inferencias se etiquetan explícitamente como `INFERENCE: YES`.

---

## 1. Executive Verdict

```text
VERDICT GENERAL: TARGETED_EVOLUTION_REQUIRED
ARQUITECTURA:     ARCHITECTURE_GENERALIZABLE_WITH_TARGETED_EVOLUTION
```

El sistema NO es una colección de verticales hardcodeadas que exijan reescribir una miniaplicación por capability. Existe una arquitectura real de cinco cerebros con autoridades separadas (P6/P7/P8, Kernel, Derived Evidence, owner evidence, delivery), y el camino workbook-first de F2 abre la posibilidad de generalización. Pero:

1. El modelo de capability actual está diseñado en torno a capabilities ATOMIC escalares con inputs agregados, y NINGUNA de las capacidades del catálogo posee grain multidimensional (producto × período, sucursal × día, categoría × hora).
2. No existe un carril matemático productivo para agregaciones grupadas. Todo lo que entra al Kernel/generic engine es un único valor por variable; no hay `GROUP BY` gobernado, ni join multidimensional, ni serie temporal.
3. P7 (RequirementMatch) declara grain en cada familia, pero P8 y los evaluadores lo ignoran; el `grain` viaja en el `GovernedComputationInput` pero el generic engine y LIQ/REN consumen sólo `source_bindings` y agregan una columna entera.
4. Existen dos caminos semánticos productivos: el determinístico legacy y el asistido F2 (provider capacité-neutral). Conviven en el mismo root y en la misma web. No hay ruta paralela de cálculo, pero hay coexistencia de rutas semánticas.
5. El Kernel es una autoridad matemática real para fórmulas escalares, pero su `SUPPORTED_FORMULAS` y el generic engine cubren ~18 fórmulas y 11 abilities; ninguna de las ~28 capacidades analíticas de la matriz cafeteria tiene fórmula ni evaluador.
6. Derived Evidence es ORTOGONAL a la matemática (join + agrega filas) pero SÓLO implementa 2 derivaciones (REN_001 sales/costs) y está hardcodeada por capability. No es la causa de la tensión con el Kernel; el Kernel no puede hacer esas agregaciones todavía.
7. El blast radius de agregar un análisis en el café es alto porque hoy requiere: semantic support + family/registry + formula + evaluador + outcome + wiring de root + UI. De las 12 opciones del menú, 3 llegan a un evaluador real.
8. Tres fallos físicos de test reproducidos por esta auditoría: fixtures ausentes (`S1-PHY-005/006/007`, `S1-POS-001/002/003`) y drift documento/catálogo. En gran parte por fixtures faltantes en el worktree, no por lógica; pero señalan un gap de gobernanza de corpus físico.
9. Ninguna afirmación de producto certificado (LIQ_001, REN_001, working_capital) es demostrable para HEAD 4cda16d: los claims históricos certifican los cortes `d2c9c24`/`26ef6c8`, anteriores a 4cda16d; el `MAIN_HEAD` documentado es anterior a los 5 commits de F2.

---

## 2. Audit Scope

Unidad auditada:

- Repositorio local `PymIA` (worktree `PymIA-service1-cafeteria`), branch `work/service1-cafeteria-flow-v1`.
- HEAD committed base: `4cda16d42fe804db50daa73aa13c68a144c785c0`.
- Diffs no committeados F2/F3 (7 archivos: 5 productivos + 2 tests).
- Código productivo: `pymia/smartpyme/*.py`, `pymia/contracts/formula_contract.py`, `pymia/services/formula_engine_service.py`, `pymia/cli/service_1_product.py`.
- Catálogos: `docs/formula_catalog.v1.json`, `docs/service_1_formula_pathology_evidence_matrix.v2.json`, `docs/service_1_semantic_variable_catalog.v1.json`, `docs/pathology_catalog.enriched.v2.json`.
- Documentación rectora: `docs/current/README.md`, `PYMIA_FIVE_BRAINS_AND_COHERENCE_SOVEREIGNTY_V1.md`, `SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`, `SERVICE_1_STATUS.md`, `SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1.md`, `ACTIVE_ROADMAP.md`, `SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md`.
- Fixture físico: `prueba_excels/cafeteria_abc.xlsx` (+ corpus).
- Ejecución de tests: colector 3669 tests; suites focales (ver §3).

NO auditado (fuera de alcance): landing, Excel Reality Lab, LLM provider externo real, RADAR futuro, otros worktrees.

---

## 3. Sources and Evidence

### 3.1 Documentos leídos

| Fuente | Ruta | Tipo |
|---|---|---|
| README rector actual | `docs/current/README.md` | DOC |
| Five Brains | `docs/current/PYMIA_FIVE_BRAINS_AND_COHERENCE_SOVEREIGNTY_V1.md` | DOC |
| Product state | `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md` | DOC |
| Status técnico | `docs/current/SERVICE_1_STATUS.md` | DOC |
| Deployment target | `docs/current/SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1.md` | DOC |
| Roadmap activo | `docs/current/ACTIVE_ROADMAP.md` + `docs/current/README.md` (deuda abierta) | DOC |
| Component map | `docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md` | DOC |
| Semantic variable catalog | `docs/service_1_semantic_variable_catalog.v1.json` | DOC (JSON) |
| Formula catalog | `docs/formula_catalog.v1.json` (18 fórmulas) | DOC (JSON) |
| Evidence matrix | `docs/service_1_formula_pathology_evidence_matrix.v2.json` (14 entries) | DOC (JSON) |
| AGENTS.md (root) | `E:\BuenosPasos\smartbridge\PymIA\AGENTS.md` | DOC |
| pymia-operating-system skill | `C:\Users\PC\.agents\skills\pymia-operating-system\SKILL.md` | SKILL |

### 3.2 Código leído (archivo → símbolo → evidencia)

| Archivo | Símbolos clave | Evidencia |
|---|---|---|
| `service_1_product_pipeline_v1.py` | `run_service_1_product_pipeline_v1`, branches `LIQ_001_CAPABILITY_REF` (L482), `REN_001_CAPABILITY_REF` (L525), `elif capability_definition is not None` (L570), `_delivery_block_reason` (L641) | CODE |
| `formula_engine_service.py` | `FormulaEngineService.calculate`, 17 ramas de fórmula, `_calculate_*` | CODE |
| `formula_contract.py` | `SUPPORTED_FORMULAS` (18 entries), `FormulaInput/Result` (escalar `value: float`) | CODE |
| `service_1_computability_v1.py` | `Service1GovernedComputationInputV1` (grain dict, source_bindings), `build_service_1_computability_decision_v1`, `build_service_1_composite_governed_computation_input_v1` | CODE |
| `service_1_derived_evidence_v1.py` | `CAPABILITY_NET_MARGIN`, `DERIVATION_PERIOD_SALES`, `DERIVATION_PERIOD_COSTS`, `_apply_discount`, `_confirmed_discount_unit` | CODE |
| `service_1_capability_registry_v1.py` | `_REGISTRY` (11 ATOMIC/COMPOSITE), `VariableRequirementV1`, `FormulaNodeV1` | CODE |
| `service_1_generic_capability_engine_v1.py` | `execute_generic_capability_v1`, `_resolve_atomic_inputs` (agrega columna entera), `_evaluate_formula`, `_classify` | CODE |
| `service_1_variable_family_bindings_v1.py` | `VARIABLE_FAMILY_DEFINITIONS` (14), `Service1GrainV1` (4 ejes), `Service1RequirementMatchV1` | CODE |
| `service_1_p6_approval_decision_v1.py` | `build_service_1_p6_approval_decision_v1`, `STATUS_APPROVED` | CODE |
| `service_1_liq_001_evaluator_v1.py` | `evaluate_liq_001_from_normalized_tables_v1` (agrega columna entera) | CODE |
| `service_1_liq_001_outcome_v1.py` | `build_liq_001_outcome_v1`, `deliver_liq_001_outcome_xlsx_v1` | CODE |
| `service_1_ren_001_evaluator_v1.py` | `evaluate_ren_001_v1` (usa kernel `calculate_formula`) | CODE |
| `service_1_ren_001_outcome_v1.py` | `build_ren_001_outcome_v1`, `deliver_ren_001_outcome_xlsx_v1` | CODE |
| `service_1_xlsx_delivery_v1.py` | `build_service_1_xlsx_delivery_v1`, sheets fijos | CODE |
| `service_1_xlsx_to_normalized_table_v1.py` | `read_xlsx_to_normalized_tables_v1` (único parser), returns `NormalizedTableV1` con `blocking_errors` | CODE |
| `service_1_web_column_confirmation_intake_boundary_v1.py` | `build_service_1_web_column_confirmation_intake_boundary_v1`, `BLOCK_READER_FAILED = "CANONICAL_READER_FAILED"` | CODE |
| `service_1_workbook_profiler_v1.py` | `build_service_1_workbook_profile_v1`, `_candidate_relationship` | CODE |
| `service_1_column_understanding_engine_v1.py` | `_ROLE_RULES` (~37 roles determinísticos) | CODE |
| `service_1_deterministic_semantic_pipeline_v1.py` | `run_initial_pass`, `run_owner_reentry`, `build_computability_decision_from_confirmed_bindings_v1` | CODE |
| `service_1_assisted_semantic_product_wiring_v1.py` | `run_service_1_assisted_semantic_initial_v1` (capability-neutral), `_capability_relevant_roles` | CODE |
| `service_1_assisted_web_semantic_reception_v1.py` | `build_service_1_post_semantic_analysis_discovery_v1`, `_confirm_workbook_first_semantics` | CODE |
| `service_1_assisted_web_v1.py` | `_REVIEW_OPTIONS`/`_LAUNCH_REVIEW_OPTIONS`, `run_working_capital`, `_persist_owner_confirmation_events` (L2134) | CODE |
| `service_1_tenant_confirmation_persistence_wiring_v1.py` | `persist_service_1_owner_confirmation_v1` | CODE |
| `service_1_assisted_web_tenant_wiring_v1.py` | `persist_service_1_assisted_web_owner_events_v1` | CODE |

### 3.3 Evidencia de ejecución (esta auditoría)

```text
colector pytest: 3669 tests collected (37.87s)   RUNTIME

suites ejecutadas (todos por este agente, read-only):
- assisted_semantic_product_wiring + llm_semantic_interpreter + sequential_reception -> 33 passed (6.89s)
- cafeteria_semantic_scope + deterministic_semantic_pipeline + deterministic_computation_plan -> 18 passed (3.50s)
- reception -> 2 passed (0.65s)
- computability + derived_evidence + variable_family_bindings + liq_001_evaluator +
  ren_001_evaluator + p6_approval + workbook_profiler + xlsx_to_normalized + capability_registry -> 98 passed (14.01s)
- generic_capability_kernel + generic_kernel_promotion + generic_shadow_equivalence +
  cycle_044a_generic_capability_kernel_architecture + physical_p6_p7_p8_readiness +
  liq_001_product_wiring + ren_001_productive_root -> 51 passed, 3 FAILED (8.43s)   [ver §10]
- physical_computable_positive_controls + bounded_six_physical -> 3 passed, 1 FAILED (6.90s)   [ver §10]
- product_pipeline + ren_001_productive_root + liq_001_product_wiring -> 16 passed (2.89s)
- deterministic_semantic_pipeline + canonical_ingestion_bridge + owner_semantic_dialogue -> 35 passed (2.71s)

sonda física cafeteria_abc.xlsx (app web + provider determinístico):
- intake: NEEDS_OWNER_CONFIRMATION, sheets [Ventas, Sucursales, Productos]
- workbook-first: 2 preguntas owner; tras ACCEPT -> CONFIRMED_BINDINGS
- menu: available=[] , blocked=[sold_vs_collected_gap (NEEDS_EVIDENCE),
  net_margin_real (NEEDS_EVIDENCE), working_capital (NEEDS_EVIDENCE)]
- 15 owner_confirmation_events en semantic_run
- persist_tenant_confirmation=None; require_tenant_persistence=False
```

### 3.4 Límites de evidencia

- No se ejecutó ningún provider LLM externo (requiere e2e Playwright + credenciales; fuera de alcance read-only).
- No se ejecutó la suite completa (3669) por costo; se ejecutaron ~270 tests focales.
- No se pudo verificar el estado de producción desplegada (Cloud Run `d2c9c24`); se verificó sólo el estado del repo local (main `4cda16d`).

---

## 4. What PymIA Is Today

PymIA es una capa determinística de interpretación/control sobre archivos reales de PyMEs (Excel especialmente), con una frontera semántica asistida por IA cuyo uso en producción NO está activado (`EXTERNAL_LLM_RUNTIME_ACTIVATION: NOT_PROVEN`).

Hecho físico:

- `pymia/smartpyme/` contiene ~100 módulos Servicio 1; el root productivo es `service_1_product_pipeline_v1.py`.
- Existen exactamente un parser XLSX (`service_1_xlsx_to_normalized_table_v1.py`) y una sola autoridad matemática (`FormulaEngineService`).
- Existe capability registry genérico con 11 refs + 2 evaluadores especializados (LIQ_001, REN_001) que NO pasan por el registry.
- Existen 14 familias de variable y ~37 roles semánticos determinísticos que permiten proponer significado sin LLM.

La pregunta central de la auditoría (¿arquitectura generalizable o colección de verticales?) se responde en §33, §17 y §9.

---

## 5. Intended Five-Brain Architecture

La arquitectura conceptual documentada en `PYMIA_FIVE_BRAINS...V1.md` y en `SERVICE_1_CURRENT_PRODUCT_STATE_V1.md` define:

```text
Cerebro Determinístico / Gobierno   -> P6/P7/P8, fail-closed, contracts
Cerebro Matemático                   -> FormulaEngineService (Kernel)
Cerebro Semántico                    -> SEM-1..SEM-9, owner evidence, TenantSemanticContractV1
Cerebro Memoria                      -> memoria semántica durable (A), ejecución/resultados (B), longitudinal (C)
Cerebro Cognitivo / IA               -> provider-neutral semantic boundary; NO runtime authority
```

Invariantes declarados en `README.md`:

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_LLM_RUNTIME_AUTHORITY
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
SEMANTIC_ASSISTANCE_IS_NOT_AUTHORITY
DERIVED_EVIDENCE_IS_NOT_FORMULA_AUTHORITY
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
P8_REMAINS_COMPUTABILITY_AUTHORITY
```

---
