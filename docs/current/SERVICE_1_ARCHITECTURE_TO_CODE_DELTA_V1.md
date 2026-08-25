# Servicio 1 — Architecture-to-Code Delta V1

**Estado:** `AUTHORITATIVE_RECONSTRUCTION_INPUT`  
**Fecha:** 2026-08-23  
**Baseline:** `8d5708e9becdddaa5aa24387b310972643d1ef86` + worktree local no committeado  
**Propósito:** traducir la arquitectura final cerrada a cambios físicos concretos. Este documento no redefine arquitectura; deriva acciones de `SERVICE_1_CANONICAL_AXIS.md` y `SERVICE_1_ARCHITECTURE_LOCK.md`.

---

## 1. Cómo leer este documento

Valores de acción:

```text
KEEP        = responsabilidad actual compatible con target; conservar y proteger
REDESIGN    = responsabilidad legítima, contrato/interfaz actual incompatible
ABSORB      = comportamiento legítimo debe integrarse a una autoridad canónica
MIGRATE     = trasladar consumidores/datos/reglas al contrato canónico existente
DELETE      = no pertenece al target final
DELETE_AFTER_DEPENDENCY_CLOSURE = eliminar sólo cuando callers/gates estén migrados
CREATE      = contrato/frontera exigido por target y aún inexistente
OFFLINE     = evidencia/ingeniería, nunca runtime productivo
```

La existencia de un archivo no obliga a conservarlo. La ausencia de un archivo no autoriza crear una nueva capa si el contrato puede vivir en un módulo existente.

---

# 2. Delta ejecutivo

## D-01 — Product Root procedural → explicit command dispatcher

**Actual:** `service_1_product_pipeline_v1.py` expone una función con una firma amplia que mezcla datos, dependencies, estados semánticos, specialized requests y switches. Se observaron, entre otros:

```text
request_kind
sheet_name="sheet1"
owner_answers
semantic_run_override
requested_capability
deliver_result
reconciliation_request
collection_aging_request
expense_variance_request
semantic_provider
semantic_assistance_state
semantic_dialogue_responses
use_assisted_semantics
semantic_reception_only
semantic_atomic_confirmation
analysis_execution_request
```

El root contiene checks de exclusividad para impedir combinaciones inválidas. Eso demuestra que el tipo de workflow todavía está expresado por combinación de argumentos.

**Target:**

```text
ProductExecutionRequest =
  WorkbookSemanticStartRequest
  | WorkbookSemanticContinueRequest
  | WorkbookAnalysisExecuteRequest
  | SpecializedDomainExecuteRequest
```

**Acción:** `REDESIGN`.

**Archivos primarios:**

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/smartpyme/service_1_request_kind_v1.py
pymia/cli/service_1_product.py
pymia/smartpyme/service_1_assisted_web_semantic_reception_v1.py
pymia/smartpyme/service_1_assisted_web_v1.py
```

**Destino de mecanismos actuales:**

```text
analysis_execution_request   → ABSORB en WorkbookAnalysisExecuteRequest
semantic_reception_only      → DELETE como top-level switch
semantic_atomic_confirmation → ABSORB como opción explícita del SemanticStart contract
semantic_run_override        → DELETE productivo
owner_answers legacy         → DELETE después de migración semántica
use_assisted_semantics       → DELETE como selector de workflow
request_kind WORKBOOK/SPECIALIZED/RESULTSET_REENTRY → REDESIGN; result read sale del execution root
```

**Gate:** ningún branch de Product Root puede seleccionar workflow por presencia/ausencia de kwargs.

---

## D-02 — ResultSet reentry mezclado con execution request

**Actual:** `service_1_request_kind_v1.py` incluye `RESULTSET_REENTRY`; Product Root lo bloquea con `RESULTSET_REENTRY_REQUIRES_F13_REENTRY_CONTRACT`.

**Target:** lectura separada:

```text
Service1ResultQueryV1
→ ResultReadBoundary
→ F13 load
→ persisted projection
```

**Acción:**

```text
service_1_request_kind_v1.py → REDESIGN/ABSORB
ResultReadBoundary           → CREATE mínima frontera
Service1ResultQueryV1        → CREATE contract, preferentemente en la misma frontera para no proliferar módulos
service_1_result_memory_v1.py → KEEP
service_1_result_memory_wiring_v1.py → KEEP
```

**Prohibido:** hacer que ResultReadBoundary ejecute F9 nuevamente.

---

## D-03 — CanonicalIngestionOutput self-contained pero consumers usan aliases/reinyección

**Actual:** el constructor V2 ya contiene `normalized_tables`. CLI vuelve a hacer:

```text
ingestion_output = dict(connector["ingestion_output"])
normalized_tables = boundary.get("normalized_tables")
ingestion_output["normalized_tables"] = normalized_tables
```

La evidencia física demostró que es la misma data canónica, sin transformación.

El envelope todavía expone aliases transitorios como:

```text
case_id
source_kind
filename
source_file_ref
available_data_fields
columns
input_values
normalized_values
column_meaning_confirmations
column_evidence
sheet_name
sheet_names
declared_data_sources
runtime_authorized
product_ready
delivery_authorized
```

**Target:** self-contained e inmutable post-build.

**Acción:**

```text
service_1_owner_confirmation_to_canonical_ingestion_output_v1.py → KEEP + MIGRATE aliases out
pymia/cli/service_1_product.py → DELETE normalized_tables reinjection
web/adapters → MIGRATE consumers a campos canónicos
```

**Gate de retiro de cada alias:** `ZERO_PRODUCTIVE_CONSUMERS`.

No borrar aliases antes de migrar consumers; no crear aliases nuevos.

---

## D-04 — identidad workbook/artifact incorrecta para local_path

**Actual:** `_case_id()` en `service_1_web_column_confirmation_intake_boundary_v1.py` recibe para `local_path`:

```text
source_kind
basename(filename)
selected_sheets/include_all_sheets
```

sin contenido. Dos archivos distintos con el mismo basename y scope pueden colisionar.

Existe ya utilidad de SHA-256 streaming en `pymia/smartpyme/pipeline_registration.py`.

**Target:**

```text
case_id = opaque workflow identity
source_artifact_ref = xlsx:sha256:<actual file bytes>
workbook_ref = digest(source_artifact_ref + ingestion_scope + canonical reader/schema version)
sheet_ref = digest(workbook_ref + exact sheet_name)
filename = display/provenance only
```

**Acción:** `REDESIGN`.

**Archivos:**

```text
service_1_web_column_confirmation_intake_boundary_v1.py
service_1_owner_confirmation_to_canonical_ingestion_output_v1.py
service_1_workbook_logical_model_v1.py
service_1_workbook_schema_identity_v1.py
semantic/owner event contracts que consumen sheet identity
```

**Tests obligatorios:**

```text
same basename + different content → different source_artifact_ref/workbook_ref
same bytes + different filename → same source_artifact_ref
same artifact + different sheet subset → different workbook_ref
same workbook + same exact sheet_name → stable sheet_ref
```

No usar path/mtime/size como sustituto de content identity.

---

## D-05 — `sheet1` fallback

**Actual:** existen literales/fallbacks `sheet1` en capas semánticas/compat. Algunos pertenecen a legacy productivo.

**Target:** `sheet_ref` explícito o fail-closed; nunca sheet fabricated identity.

**Acción:** `MIGRATE + DELETE`.

Eliminar ocurrencias sólo después de distinguir:

```text
physical label real
fixture/test display
legacy compatibility fallback
productive identity fallback
```

Sólo las dos últimas violan target productivo.

**Gate:** búsqueda productiva `sheet1` = 0 salvo fixtures/documentación explícitamente no runtime.

---

## D-06 — dos composiciones semánticas productivas

**Actual:** conviven:

```text
service_1_assisted_semantic_product_wiring_v1.py
service_1_deterministic_semantic_pipeline_v1.py
service_1_legacy_semantic_reentry_compat_v1.py
```

El pipeline determinístico histórico usa el mismo reinjector/P6 que SEM-8. Existe `service_1_deterministic_semantic_proposal_provider_v1.py`, compatible con la frontera provider-neutral.

**Target:** una sola FSM:

```text
SemanticStart(provider=deterministic|bounded_llm)
→ validator
→ owner dialogue
→ SemanticContinue
→ shared reinjector/P6
→ CONFIRMED_BINDINGS
```

**Acción:**

```text
service_1_assisted_semantic_product_wiring_v1.py → KEEP + REDESIGN como FSM única
service_1_deterministic_semantic_proposal_provider_v1.py → KEEP/PRODUCTIVE PROVIDER
service_1_deterministic_semantic_pipeline_v1.py → DELETE_AFTER_PARITY_GATE
service_1_legacy_semantic_reentry_compat_v1.py → DELETE_AFTER_CALLER_MIGRATION
```

**Callers legacy conocidos:**

```text
pymia/cli/service_1_product.py
pymia/smartpyme/service_1_assisted_web_v1.py
```

**Parity gate:** same canonical input + same owner evidence → semantically equivalent `CONFIRMED_BINDINGS` through SEM-8 deterministic provider.

---

## D-07 — table_scoped_semantics se construye dos veces

**Actual:** D7 construye `table_scoped_semantics` en `service_1_workbook_logical_model_v1.py`; SEM-8 vuelve a ejecutar `build_service_1_table_scoped_semantic_context_v1` con los mismos logical tables/relationship graph.

**Target:** construcción única D6/D7; SEM consume.

**Acción:**

```text
service_1_table_scoped_semantic_context_v1.py → KEEP, single builder authority
service_1_workbook_logical_model_v1.py → KEEP; produce packet una vez
service_1_assisted_semantic_product_wiring_v1.py → REDESIGN; aceptar D7.table_scoped_semantics y no reconstruir
```

**Gate:** llamadas productivas a `build_service_1_table_scoped_semantic_context_v1` fuera del D6/D7 coordinator = 0.

---

## D-08 — D4 → P8 → F7 provenance incompleta

**Actual:** D4 existe y produce graph identity/fanout evidence. P8 valida computability pero no cierra todavía toda la provenance contra D4/D3. F7 valida endpoints/kind/owner evidence y materializa, con safety checks runtime reales.

`schema_fingerprint` excluye `business_values`, por lo que no puede demostrar identidad de dataset.

**Target governed_relationship_binding:** ligado a:

```text
source_artifact_ref
workbook_ref
schema_fingerprint
graph_ref / graph_fingerprint
relationship_ref
endpoints
relationship_kind
fanout/cardinality evidence
owner_event_ref
integrity_digest
```

**Acción:**

```text
service_1_logical_relationship_graph_v1.py → KEEP + EXTEND provenance if needed
service_1_computability_v1.py → REDESIGN/EXTEND governed relationship binding
service_1_analysis_evidence_preparation_v1.py → KEEP runtime safety + EXTEND static binding validation
service_1_owner_relationship_confirmation_event_v1.py → KEEP + bind graph/workbook identity as required
```

**F7 safety que debe preservarse:**

```text
duplicate right lookup keys → BLOCK
ONE_TO_ONE duplicate left keys → BLOCK
missing match → BLOCK
join conflict → BLOCK
runtime cardinality violation → BLOCK
```

No mover esos checks a D4; son safety de ejecución sobre filas reales.

---

## D-09 — autoridad matemática distribuida en evaluadores

**Actual:** kernel común existe y es usado ampliamente. Sin embargo se observaron operaciones de negocio inline en:

```text
service_1_liq_001_evaluator_v1.py
service_1_ren_001_evaluator_v1.py
service_1_consorcios_expense_variance_v1.py
service_1_consorcios_collection_aging_v1.py
```

**Target:** toda matemática empresarial productiva pasa por:

```text
FormulaEngineService
MathPrimitiveOperation
formula catalog
```

**Acción:** `MIGRATE`.

Ejemplos:

```text
LIQ/REN row SUM → MathPrimitive SUM
expense actual_by_rubro → MathPrimitive SUM por grupo
budget/historical variance → named canonical formulas
max_positive → MathPrimitive MAX
collection aging ratio → named canonical formula
```

**No crear** segundo engine ni excepción matemática permanente.

---

## D-10 — classification empresarial hardcodeada

**Actual:** `ClassificationRuleV1` soporta una comparación; varios evaluadores implementan if/else inline.

**Target mínimo:** extender contrato existente, sin DSL general:

```text
ClassificationPredicate:
  left_ref = result | named_input | named_derived_value
  comparison = LT | LE | EQ | GE | GT
  right_ref XOR literal

ClassificationRule:
  code
  match = ALL | ANY
  predicates[]
```

**Acción:**

```text
service_1_capability_contracts_v1.py → REDESIGN backward-compatible
service_1_generic_capability_engine_v1.py → REDESIGN classifier to evaluate predicates only
service_1_capability_registry_v1.py → MIGRATE definitions
LIQ_001/REN_001/LIQ_002/PYME_011/Consorcios → MIGRATE classification out of inline if/else
```

El classifier no puede ejecutar MAX, ratio, SUM, difference ni ninguna aritmética.

---

## D-11 — Consorcios specialized legítimo, pero math/policy no convergido

**Actual:** specialized workflows con input/output distinto. Matemática y clasificación todavía parcialmente inline.

**Target:** specialized workflow + common math/policy authorities.

**Acción:** `REDESIGN` en:

```text
service_1_consorcios_expense_variance_v1.py
service_1_consorcios_collection_aging_v1.py
```

Agregar al catálogo canónico las fórmulas de dominio necesarias, no un nuevo engine.

`reconciliation` conserva specialized status bajo su request explícito.

LIQ_001 y REN_001 no son specialized en target.

---

## D-12 — Productive Web/CLI todavía llaman legacy o completan contratos

**Actual:** CLI llama legacy semantic shim y reinyecta envelope. `service_1_assisted_web_v1.py` conserva caller legacy.

**Target:** superficies sólo construyen commands/queries y proyectan respuestas.

**Acción:** `REDESIGN`.

**Archivos:**

```text
pymia/cli/service_1_product.py
service_1_assisted_web_v1.py
service_1_assisted_web_semantic_reception_v1.py
service_1_semantic_reception_server_v1.py
service_1_ui_v1.py (presentation only; no business authority)
```

No colocar matemática ni semántica soberana en web/CLI para simplificar el root.

---

## D-13 — registry incompleto y semánticamente desactualizado

**Actual físico auditado:**

```text
LIVE service_1_*.py = 112
REGISTERED = 101
MISSING = 11
```

Confrontación física contra `docs/service_1_module_disposition.v1.json` reconcilia como faltantes:

```text
service_1_logical_relationship_graph_v1
service_1_logical_table_candidate_v1
service_1_physical_region_detection_v1
service_1_region_evidence_v1
service_1_request_kind_v1
service_1_table_scoped_semantic_context_v1
service_1_tenant_memory_artifact_v1
service_1_tenant_schema_family_memory_store_v1
service_1_tenant_schema_family_memory_v1
service_1_workbook_schema_identity_v1
service_1_workbook_logical_model_v1
```

Además el registry actual todavía clasifica `service_1_deterministic_semantic_pipeline_v1` como PRODUCTIVE, aunque el target final ordena retirarlo tras parity.

**Acción:** NO actualizar registry al inicio. Reconciliarlo al final, después de completar retiros/absorciones, para que represente el closure final y no el estado transitorio.

---

# 3. Worktree actual — decisión explícita

El `git status` observado incluye cambios previos de convergencia. No resetearlos en bloque.

## Docs

```text
docs/adr/ADR-007-documentation-governance.md → KEEP
docs/current/README.md → KEEP
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md → KEEP
docs/current/SERVICE_1_CANONICAL_AXIS.md → KEEP
docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md → KEEP
docs/current/SERVICE_1_STATUS.md → KEEP
```

## Runtime

```text
service_1_assisted_web_semantic_reception_v1.py → REDESIGN against explicit commands
service_1_assisted_web_v1.py → REDESIGN; remove legacy semantic caller
service_1_legacy_semantic_reentry_compat_v1.py → DELETE_AFTER_CALLER_MIGRATION
service_1_owner_confirmation_to_canonical_ingestion_output_v1.py → KEEP/REDESIGN; canonical V2, remove aliases eventually
service_1_product_pipeline_v1.py → REDESIGN to thin dispatcher
service_1_web_column_confirmation_intake_boundary_v1.py → REDESIGN identity
service_1_workbook_logical_model_v1.py → KEEP; D7 target, ensure table scope single-build
service_1_request_kind_v1.py → REDESIGN/ABSORB into explicit command contracts
```

## Tests modified/untracked

Tests no se descartan por estar asociados a una fase vieja. Cada uno se clasifica según si prueba el target final:

```text
test_service_1_assisted_semantic_product_wiring_v1.py → MIGRATE to one-FSM + D7 table scope contract
test_service_1_catalog_expansion_f12_v1.py → KEEP unless asserts old root interface
test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py → MIGRATE to immutable V2/identity
test_service_1_product_pipeline_v1.py → REDESIGN to four command dispatcher
test_service_1_result_memory_f13_v1.py → KEEP; add read-boundary no-recalc coverage
test_service_1_web_column_confirmation_intake_boundary_v1.py → MIGRATE to content-addressed identity
test_service_1_workbook_logical_model_d7_v1.py → KEEP/EXTEND single table-scope build
untracked test_service_1_request_kind_dispatch_v1.py → REDESIGN or replace with explicit execution-contract tests
```

`_audit/` → `OFFLINE / UNCOMMITTED`.

---

# 4. Módulos target por autoridad

## Intake / identity / ingestion

```text
service_1_web_column_confirmation_intake_boundary_v1.py → REDESIGN
service_1_xlsx_to_normalized_table_v1.py → KEEP canonical reader
service_1_normalized_table_v1.py → KEEP contract/support
service_1_owner_confirmation_to_canonical_ingestion_output_v1.py → KEEP/REDESIGN canonical constructor
```

## D1–D7

```text
service_1_workbook_profiler_v1.py → KEEP D1
service_1_physical_region_detection_v1.py → KEEP D2
service_1_region_evidence_v1.py → KEEP D2 evidence
service_1_logical_table_candidate_v1.py → KEEP logical tables
service_1_workbook_schema_identity_v1.py → KEEP D3
service_1_logical_relationship_graph_v1.py → KEEP/EXTEND D4
service_1_table_scoped_semantic_context_v1.py → KEEP D6 evidence builder
service_1_workbook_logical_model_v1.py → KEEP/REDESIGN D7 single coordinator
```

## Semantics

```text
service_1_assisted_semantic_product_wiring_v1.py → KEEP/REDESIGN canonical FSM
service_1_deterministic_semantic_proposal_provider_v1.py → KEEP provider
service_1_pydantic_ai_column_semantic_provider_v1.py → KEEP bounded provider adapter
service_1_llm_semantic_interpreter_v1.py → KEEP provider-neutral interpreter
service_1_semantic_proposal_validator_v1.py → KEEP deterministic validator
service_1_owner_semantic_dialogue_v1.py → KEEP
service_1_owner_semantic_answer_projection_v1.py → KEEP
service_1_owner_semantic_evidence_reentry_v1.py → KEEP
service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py → KEEP shared reinjector/P6 path
service_1_p6_approval_decision_v1.py → KEEP
service_1_deterministic_semantic_pipeline_v1.py → DELETE_AFTER_PARITY_GATE
service_1_legacy_semantic_reentry_compat_v1.py → DELETE_AFTER_CALLER_MIGRATION
```

## Analysis authority

```text
service_1_analysis_plan_v1.py → KEEP
service_1_dynamic_analysis_discovery_v1.py → KEEP P7/discovery support
service_1_computability_v1.py → KEEP/EXTEND P8 provenance binding
service_1_analysis_evidence_preparation_v1.py → KEEP/EXTEND F7
service_1_analysis_math_execution_v1.py → KEEP F8 coordinator
service_1_analysis_result_projection_v1.py → KEEP F9
service_1_result_memory_v1.py → KEEP F13
service_1_result_memory_wiring_v1.py → KEEP
```

## Math / capability / policy

```text
pymia/contracts/formula_contract.py → KEEP math authority
pymia/services/formula_engine_service.py → KEEP math authority
pymia/contracts/formula_rules_v1.json → KEEP/EXTEND canonical formulas
service_1_capability_contracts_v1.py → REDESIGN classification contract
service_1_capability_registry_v1.py → MIGRATE definitions
service_1_generic_capability_engine_v1.py → KEEP/REDESIGN classifier, common kernel usage
service_1_liq_001_evaluator_v1.py → REDESIGN as governed capability adapter, no inline math/policy
service_1_ren_001_evaluator_v1.py → REDESIGN as governed capability adapter, no inline math/policy
service_1_liq_002_evaluator_v1.py → MIGRATE policy/math if productive through capability path
service_1_pyme_011_evaluator_v1.py → MIGRATE policy/math if productive through capability path
```

## Specialized

```text
service_1_consorcios_expense_variance_v1.py → KEEP specialized workflow / REDESIGN math+policy
service_1_consorcios_collection_aging_v1.py → KEEP specialized workflow / REDESIGN math+policy
service_1_reconciliation_request_gate_v1.py → KEEP
service_1_reconciliation_candidate_to_assisted_review_v1.py → KEEP
service_1_reconciliation_product_request_v1.py → KEEP specialized workflow
```

---

# 5. No-delta / preservar

Estos comportamientos están alineados y no deben romperse durante la reconstrucción:

```text
NO_LLM_MATH
explicit owner confirmation on first contact
P7/P8 separation
F7 runtime cardinality fail-closed
D7 evidence-only flags
F13 append-only/content-addressed result integrity
tenant isolation
memory hint-only / no auto-rebind
canonical XLSX reader fail-closed behavior
```

---

# 6. Señales de una reconstrucción incorrecta

Detener el ciclo si aparece cualquiera de estas salidas:

```text
nuevo wrapper para mantener old kwargs
nuevo alias de CanonicalIngestionOutput
nuevo request_kind para un estado que debería ser command explícito
segundo semantic runner productivo
math inline nueva
classification if/else nueva
F7 decidiendo qué relación usar
P8 materializando join
D7 autorizando grain/computability
ResultRead llamando F9/F8
web/CLI calculando
sheet1 agregado para reparar un test
filename usado como workbook key
```

Eso es `FAIL_ARCHITECTURE`, aunque los tests focales pasen.


# 7. Delta adicional físicamente confirmado — legacy First Aid tool path

## D-14 — `tool_requests` / `service_1_pipeline_v1` constituye una quinta vía implícita incompatible con el target

**Evidencia física:** `service_1_product_pipeline_v1.py` llama `run_service_1_pipeline_v1(tool_requests=..., output_dir=...)` cuando no entra por capability/specialized branches. `service_1_pipeline_v1.py` ejecuta un allowlist histórico de First Aid tools (`precio_margen_basico`, `caja_diaria_triage`, `stock_alertas_basicas`, `gastos_triage`, `proveedores_precio_variacion_triage`) y delega a `service_1_manual_first_aid_delivery_flow_v1.py`.

**Problema:** los cuatro command contracts finales no incluyen un `ToolRequestsExecute` genérico. Mantener `tool_requests` como branch residual dejaría una quinta ruta de ejecución elegida por shape/kwargs y rompería `FOUR_EXPLICIT_EXECUTION_COMMANDS`.

**Target:**

```text
service_1_pipeline_v1.py → DELETE_AFTER_GATE del productive closure
service_1_manual_first_aid_delivery_flow_v1.py → SUPPORT_KEEP u OFFLINE según callers finales
first_aid_* tools → soporte histórico/utilidades; no root productivo salvo promoción futura explícita por arquitectura
Product Root tool_requests parameter → DELETE
```

Si alguna capacidad First Aid sigue siendo funcionalmente requerida, debe incorporarse mediante un contrato ya autorizado (governed workbook capability o SpecializedDomainExecuteRequest que satisfaga A16). No se autoriza conservar `tool_requests` como escape hatch genérico.

**Gate:**

```text
PRODUCT_ROOT_TOOL_REQUESTS_BRANCH = 0
PRODUCTIVE_CALLERS_OF_service_1_pipeline_v1 = 0
FIFTH_EXECUTION_PATH = 0
```
