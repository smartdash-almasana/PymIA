# Servicio 1 — Code Disposition Final V1

**Estado:** `AUTHORITATIVE_TARGET_DISPOSITION`  
**Fecha:** 2026-08-23  
**Alcance:** todos los módulos Python `service_1_*` físicamente observados bajo `pymia/smartpyme` al baseline de auditoría.

Este documento define el destino objetivo de código para la reconstrucción. No sustituye el registry ejecutable `docs/service_1_module_disposition.v1.json`; indica cómo debe quedar ese registry al cierre.

---

## 1. Universo físico y regla de cobertura

Auditoría física:

```text
LIVE_SERVICE_1_PYTHON_MODULES = 112
REGISTERED_IN_CURRENT_JSON = 101
MISSING_FROM_CURRENT_JSON = 11
```

Todos los módulos quedan cubiertos por una de estas dos reglas:

### Regla A — módulos ya registrados

Todo módulo incluido actualmente en `docs/service_1_module_disposition.v1.json` **hereda su disposición actual** salvo que aparezca en la tabla de overrides de este documento.

Esto evita recategorizar soporte estable sin evidencia de cambio arquitectónico.

### Regla B — módulos faltantes del registry

Los 11 módulos físicamente reconciliados en §4 reciben aquí una disposición target explícita.

Por tanto:

```text
101 registrados
+ 11 faltantes clasificados aquí
= 112 módulos cubiertos
UNKNOWN_TARGET_DISPOSITION = 0
```

---

## 2. Vocabulario target

```text
CANONICAL_KEEP
  pertenece al target final y conserva responsabilidad principal

CANONICAL_REDESIGN
  pertenece al target, pero su contrato/interfaz debe cambiar

SUPPORT_KEEP
  soporte legítimo, sin autoridad productiva soberana

ABSORB
  comportamiento útil se integra a otra autoridad; archivo puede desaparecer luego

MIGRATE
  módulo permanece, pero datos/reglas/callers se mueven al contrato canónico

DELETE_AFTER_GATE
  no pertenece al target; sólo puede borrarse después del gate indicado

DELETE
  no pertenece al target y no necesita preservar comportamiento productivo

OFFLINE
  auditoría/ingeniería/evidencia; no runtime productivo
```

Para el registry final, `CANONICAL_KEEP`, `CANONICAL_REDESIGN`, `ABSORB` todavía activo y `MIGRATE` todavía activo se mapean temporalmente a `PRODUCTIVE` sólo mientras sean alcanzables desde el closure final. `SUPPORT_KEEP` mapea a `SUPPORT_NECESSARY`. Los `DELETE*` deben desaparecer del registry cuando el archivo desaparezca.

---

## 3. Overrides obligatorios sobre el registry actual

| Módulo | Registry actual | Target disposition | Motivo / gate |
|---|---|---|---|
| `service_1_product_pipeline_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | converger a ProductExecutionRoot thin dispatcher con 4 commands |
| `service_1_pipeline_v1` | PRODUCTIVE | `DELETE_AFTER_GATE` | ruta First Aid histórica invocada por `tool_requests`; no existe quinto command final |
| `service_1_manual_first_aid_delivery_flow_v1` | PRODUCTIVE | `MIGRATE` → `SUPPORT_KEEP` | puede sobrevivir como soporte histórico si tiene callers no productivos; no root execution authority |
| `service_1_assisted_semantic_product_wiring_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | única FSM; consumir D7.table_scoped_semantics; no reconstruir scope |
| `service_1_deterministic_semantic_pipeline_v1` | PRODUCTIVE | `DELETE_AFTER_GATE` | retirar tras parity SEM-8 deterministic provider → CONFIRMED_BINDINGS |
| `service_1_legacy_semantic_reentry_compat_v1` | SUPPORT_NECESSARY | `DELETE_AFTER_GATE` | cero callers CLI/web productivos |
| `service_1_owner_confirmation_to_canonical_ingestion_output_v1` | SUPPORT_NECESSARY | `CANONICAL_REDESIGN` | constructor canónico V2; aliases transitorios se retiran con zero consumers |
| `service_1_web_column_confirmation_intake_boundary_v1` | SUPPORT_NECESSARY | `CANONICAL_REDESIGN` | identidad content-addressed para local_path/uploaded bytes |
| `service_1_canonical_ingestion_output_to_semantic_bridge_v1` | PRODUCTIVE | `MIGRATE` | consumir campos canónicos; dejar de depender de aliases retirados |
| `service_1_capability_contracts_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | ClassificationPredicate + ALL/ANY sin aritmética |
| `service_1_capability_registry_v1` | PRODUCTIVE | `MIGRATE` | mover classification definitions al nuevo contrato declarativo |
| `service_1_generic_capability_engine_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | classifier declarativo; mantener math kernel común |
| `service_1_liq_001_evaluator_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | governed workbook capability; no specialized branch, no inline business math/policy |
| `service_1_ren_001_evaluator_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | governed workbook capability; no inline business math/policy |
| `service_1_liq_002_evaluator_v1` | SUPPORT_NECESSARY | `MIGRATE` | si queda consumido, math/policy deben converger; no excepción inline |
| `service_1_pyme_011_evaluator_v1` | SUPPORT_NECESSARY | `MIGRATE` | idem clasificación declarativa/kernel |
| `service_1_consorcios_expense_variance_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | specialized legítimo; math/policy convergen al kernel/contract |
| `service_1_consorcios_collection_aging_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | specialized legítimo; math/policy convergen al kernel/contract |
| `service_1_computability_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | P8 valida D4/D3/artifact/workbook provenance y emite governed relationship binding |
| `service_1_analysis_evidence_preparation_v1` | PRODUCTIVE | `CANONICAL_REDESIGN` | F7 verifica binding + conserva runtime join safety |
| `service_1_owner_relationship_confirmation_event_v1` | PRODUCTIVE | `MIGRATE` | ligar evidencia a relationship_ref + graph/workbook identity según binding final |
| `service_1_result_memory_v1` | PRODUCTIVE | `CANONICAL_KEEP` | F13 persistence/load; no recalculation |
| `service_1_result_memory_wiring_v1` | PRODUCTIVE | `CANONICAL_KEEP` | persist post-F9; read boundary separado |
| `service_1_assisted_web_v1` | SUPPORT_NECESSARY | `MIGRATE` | superficie; eliminar legacy semantic caller y usar commands/query |
| `service_1_assisted_web_semantic_reception_v1` | SUPPORT_NECESSARY | `MIGRATE` | superficie; explicit commands, sin coordinación paralela |
| `service_1_semantic_reception_server_v1` | SUPPORT_NECESSARY | `SUPPORT_KEEP` | servidor/surface only |
| `service_1_ui_v1` | SUPPORT_NECESSARY | `SUPPORT_KEEP` | presentation only; sin business math |

---

## 4. Los 11 módulos físicamente faltantes del registry actual

La comparación física del directorio con `docs/service_1_module_disposition.v1.json` reconcilia exactamente:

| Módulo faltante | Target disposition | Rol final |
|---|---|---|
| `service_1_logical_relationship_graph_v1` | `CANONICAL_REDESIGN` | D4 structural relationship authority; provenance completa |
| `service_1_logical_table_candidate_v1` | `CANONICAL_KEEP` | logical table evidence |
| `service_1_physical_region_detection_v1` | `CANONICAL_KEEP` | D2 physical region detection |
| `service_1_region_evidence_v1` | `CANONICAL_KEEP` | D2 region evidence |
| `service_1_request_kind_v1` | `ABSORB` | sustituir por explicit ProductExecutionRequest contracts; result read sale del root |
| `service_1_table_scoped_semantic_context_v1` | `CANONICAL_KEEP` | D6/D7 single structural table-scope builder |
| `service_1_tenant_memory_artifact_v1` | `SUPPORT_KEEP` | tenant memory artifact support, sin auto-rebind |
| `service_1_tenant_schema_family_memory_store_v1` | `SUPPORT_KEEP` | persistence support |
| `service_1_tenant_schema_family_memory_v1` | `SUPPORT_KEEP` | schema-family hint/revalidation support |
| `service_1_workbook_schema_identity_v1` | `CANONICAL_KEEP` | D3 structural schema identity |
| `service_1_workbook_logical_model_v1` | `CANONICAL_REDESIGN` | D7 coordinator; table scope una vez; evidence-only |

El registry final debe incluir los módulos que sobrevivan y eliminar `service_1_request_kind_v1` si el ABSORB termina físicamente en un nuevo contrato y el archivo deja de tener responsabilidad legítima.

---

## 5. Módulos canónicos que deben preservarse explícitamente

Además de la herencia del registry, estos módulos representan autoridades/contratos que no deben ser reemplazados por paralelos:

### Workbook / D1–D7

```text
service_1_xlsx_to_normalized_table_v1
service_1_workbook_profiler_v1
service_1_physical_region_detection_v1
service_1_region_evidence_v1
service_1_logical_table_candidate_v1
service_1_workbook_schema_identity_v1
service_1_logical_relationship_graph_v1
service_1_table_scoped_semantic_context_v1
service_1_workbook_logical_model_v1
```

### Semantic

```text
service_1_deterministic_semantic_proposal_provider_v1
service_1_llm_semantic_contract_v1
service_1_llm_semantic_interpreter_v1
service_1_pydantic_ai_column_semantic_provider_v1
service_1_semantic_proposal_validator_v1
service_1_owner_semantic_dialogue_v1
service_1_owner_semantic_answer_projection_v1
service_1_owner_semantic_evidence_reentry_v1
service_1_owner_confirmation_reinjection_to_semantic_gate_v1
service_1_p6_approval_decision_v1
```

### Analysis

```text
service_1_analysis_plan_v1
service_1_dynamic_analysis_discovery_v1
service_1_computability_v1
service_1_analysis_evidence_preparation_v1
service_1_analysis_math_execution_v1
service_1_analysis_result_projection_v1
service_1_result_memory_v1
service_1_result_memory_wiring_v1
```

### Math authority outside service_1 namespace

```text
pymia/contracts/formula_contract.py
pymia/contracts/formula_rules_v1.json
pymia/services/formula_engine_service.py
```

No crear reemplazos de estos tres para resolver casos locales.

---

## 6. Specialized target

```text
service_1_consorcios_expense_variance_v1 → CANONICAL_REDESIGN specialized
service_1_consorcios_collection_aging_v1 → CANONICAL_REDESIGN specialized
service_1_reconciliation_request_gate_v1 → CANONICAL_KEEP
service_1_reconciliation_candidate_to_assisted_review_v1 → CANONICAL_KEEP
service_1_reconciliation_product_request_v1 → CANONICAL_KEEP specialized
```

No convertir en specialized:

```text
LIQ_001
REN_001
legacy semantic compatibility
cualquier workbook analysis que sólo necesite una capability nueva
```

---

## 7. Tenant memory target

Los módulos de tenant identity / semantic memory / schema family memory se conservan como soporte o evidencia compatible bajo estas prohibiciones:

```text
NO automatic semantic reuse
NO memory auto-rebind
NO memory as runtime authority
NO cross-tenant lookup leakage
memory hints must be revalidated against current workbook/schema
```

No eliminar estos módulos sólo porque no sean root-reachable; su rol de soporte es legítimo.

---

## 8. Tests: disposition policy

Los tests no se clasifican por antigüedad sino por contrato.

```text
KEEP
  prueba un invariante final compatible

MIGRATE
  prueba una capacidad legítima mediante una interfaz vieja

DELETE/REPLACE
  exige conducta explícitamente prohibida por arquitectura final
```

Ejemplos:

```text
test_service_1_deterministic_semantic_pipeline_v1.py
→ MIGRATE su evidencia de comportamiento a parity tests de SEM-8; luego retirar tests del módulo eliminado

test_service_1_request_kind_dispatch_v1.py
→ REDESIGN/REPLACE por ProductExecutionRequest discrimination

test_service_1_result_memory_f13_v1.py
→ KEEP + ampliar con ResultReadBoundary no-recalc

test_service_1_analysis_evidence_preparation_f7_v1.py
→ KEEP + ampliar provenance binding
```

No mantener un módulo legacy sólo porque tenga muchos tests.

---

## 9. Regla final del registry

El ciclo de registry ocurre después de los retiros.

El registry final debe satisfacer:

```text
filesystem service_1_*.py set == registry module set
registry duplicates = 0
unregistered modules = 0
registered missing files = 0
PRODUCTIVE closure contains no DELETE/legacy module
SUPPORT modules do not acquire runtime authority
```

Si al final un módulo no encaja en ninguna disposición de este documento, eso es `STOP_ARCHITECTURE`, no autorización para inventar una categoría nueva.
