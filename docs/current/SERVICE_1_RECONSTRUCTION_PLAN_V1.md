# Servicio 1 — Reconstruction Plan V1

**Estado:** `AUTHORITATIVE_IMPLEMENTATION_PLAN`  
**Fecha:** 2026-08-23  
**Principio:** reconstrucción derivada por dependencias; no reabrir arquitectura; no fases artificiales para conservar legacy.

---

## 1. Objetivo

Llevar el código físico desde el worktree actual hasta la arquitectura final de `SERVICE_1_CANONICAL_AXIS.md` / `SERVICE_1_ARCHITECTURE_LOCK.md`, reduciendo entropía en cada ciclo y terminando con certificación integral sobre un único SHA.

No se debe optimizar por cantidad de cambios ni por velocidad de test verde. Se optimiza por:

```text
menos rutas productivas
menos switches
menos aliases
menos legacy
menos fallbacks
una autoridad por decisión
contratos explícitos
fail-closed
```

---

## 2. Grafo de dependencias

```text
R0 baseline/handoff lock
  ↓
R1 identity + canonical envelope foundation
  ↓
R2 D6/D7 single table-scope evidence
  ↓
R3 one semantic FSM + parity proof
  ↓
R4 explicit ProductExecutionRequest + root/surface migration
  ↓
R5 legacy semantic + sheet1 retirement

R1 ───────────────┐
R2 ───────────────┼→ R6 D4→P8→F7 provenance + runtime safety preservation
R4 ───────────────┘

R4 → R7 common math + declarative classification
R7 → R8 specialized Consorcios/reconciliation convergence

R4 → R9 ResultReadBoundary

R5 + R6 + R7 + R8 + R9
  ↓
R10 alias/switch/compat cleanup
  ↓
R11 module registry reconciliation
  ↓
R12 architecture integration checkpoint
  ↓
R13 full suite
  ↓
R14 real XLSX E2E / completion evidence
```

No saltar a R11 para “hacer verde” registry antes de terminar retiros.

---

# R0 — Baseline y lock de reconstrucción

## Objetivo

Garantizar que el agente conoce el estado recibido y no destruye trabajo previo útil.

## Acciones

1. Leer `SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md` completo.
2. Ejecutar `git status --short` y registrar archivos modified/untracked.
3. Registrar `git rev-parse HEAD`.
4. No hacer reset masivo.
5. Confirmar que los documentos rectores dicen:

```text
OPEN_ARCHITECTURAL_DECISIONS = 0
TARGET_ARCHITECTURE_CLOSED = YES
```

6. Confirmar que no existe autorización de commit/push/deploy.

## Veredicto de salida

```text
BASELINE_CAPTURED = YES
ARCHITECTURE_REOPENED = NO
WORKTREE_RESET = NO
```

No requiere tests.

---

# R1 — Identidad física + CanonicalIngestionOutput foundation

## Dependencia

R0.

## Objetivo

Cerrar identidad de artifact/workbook/sheet antes de provenance downstream.

## Archivos primarios

```text
pymia/smartpyme/service_1_web_column_confirmation_intake_boundary_v1.py
pymia/smartpyme/service_1_owner_confirmation_to_canonical_ingestion_output_v1.py
pymia/smartpyme/service_1_workbook_logical_model_v1.py
pymia/smartpyme/service_1_workbook_schema_identity_v1.py
pymia/smartpyme/pipeline_registration.py (reutilizar hash; no duplicar parser)
```

## Implementación requerida

1. `source_artifact_ref = xlsx:sha256:<bytes>` para `uploaded_bytes` y `local_path`.
2. Para local path, hash streaming del archivo real.
3. `workbook_ref = digest(source_artifact_ref + ingestion_scope + canonical reader/schema version)`.
4. Formalizar `sheet_ref = digest(workbook_ref + exact sheet_name)` en lineage/refs donde corresponda.
5. `case_id` queda identidad de workflow, no source identity.
6. `filename` queda provenance/display.
7. Mantener V2 self-contained.
8. No retirar aún aliases que tengan consumers productivos; marcarlos para R10.

## Prohibiciones

```text
NO path+mtime+size identity
NO basename identity
NO second XLSX reader
NO post-build mutation
```

## L1 focal

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_workbook_schema_identity_d3_v1.py
```

## L2 gate nuevo/actualizado

Debe probar:

```text
same basename different bytes => different artifact/workbook refs
same bytes renamed => same artifact ref
different sheet selection => different workbook ref
filename never used as structural identity
missing sheet evidence => fail closed, not sheet1
```

## Exit

```text
CONTENT_ADDRESSED_SOURCE_ARTIFACT = PASS
WORKBOOK_IDENTITY_FROM_ARTIFACT_SCOPE = PASS
SHEET_REF_EXPLICIT = PASS
```

---

# R2 — Table-scoped structural evidence construido una vez

## Dependencia

R1.

## Objetivo

Eliminar doble construcción de `table_scoped_semantics` sin tocar todavía la FSM histórica.

## Archivos

```text
service_1_table_scoped_semantic_context_v1.py
service_1_workbook_logical_model_v1.py
service_1_assisted_semantic_product_wiring_v1.py
```

## Implementación

1. D7 mantiene la única construcción productiva de table-scope.
2. SEM-8 recibe `table_scoped_semantics` ya construido.
3. Eliminar builder call de SEM-8.
4. Ambos providers consumen el mismo packet.
5. D7 conserva authority flags false.

## Tests

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_table_scoped_semantics_d5_v1.py \
  tests/smartpyme/test_service_1_workbook_logical_model_d7_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py
```

## Architecture guard

Búsqueda/call graph debe demostrar:

```text
productive calls to build_service_1_table_scoped_semantic_context_v1 = 1 authority path via D7
```

## Exit

```text
TABLE_SCOPE_BUILT_ONCE = PASS
SEM_CONSUMES_D7_SCOPE = PASS
```

---

# R3 — Una sola FSM semántica + parity proof

## Dependencia

R2.

## Objetivo

Demostrar que SEM-8 con provider determinístico cubre el comportamiento legítimo del pipeline determinístico histórico antes de retirarlo.

## Archivos

```text
service_1_assisted_semantic_product_wiring_v1.py
service_1_deterministic_semantic_proposal_provider_v1.py
service_1_deterministic_semantic_pipeline_v1.py (read as oracle only; no nueva funcionalidad)
service_1_owner_semantic_evidence_reentry_v1.py
service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py
service_1_p6_approval_decision_v1.py
```

## Implementación

1. Formalizar el provider determinístico como provider de la misma FSM.
2. Preservar:
   - explicit owner confirmation;
   - follow-up;
   - correction;
   - skip;
   - decomposition;
   - relationships;
   - P6 decisions;
   - requirement matches;
   - offline reproducibility.
3. Crear parity tests usando mismos inputs/evidencia owner.
4. No borrar pipeline histórico hasta que parity pase.

## Tests

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_deterministic_semantic_pipeline_v1.py \
  tests/smartpyme/test_service_1_deterministic_semantic_computation_plan_v1.py \
  tests/smartpyme/test_service_1_owner_semantic_evidence_reentry_v1.py \
  tests/smartpyme/test_service_1_p6_approval_decision_v1.py
```

Agregar un test explícito de parity de `CONFIRMED_BINDINGS`.

## Exit

```text
ONE_FSM_TARGET_BEHAVIOR_PROVEN = PASS
DETERMINISTIC_PROVIDER_OFFLINE = PASS
FIRST_CONTACT_OWNER_CONFIRMATION = PASS
PARITY_CONFIRMED_BINDINGS = PASS
```

---

# R4 — ProductExecutionRequest + ProductExecutionRoot + surfaces

## Dependencias

R3.

## Objetivo

Reemplazar selección por kwargs/switches con cuatro commands explícitos y migrar todos los callers productivos en el mismo ciclo de integración.

## Contrato objetivo

```text
WorkbookSemanticStartRequest
WorkbookSemanticContinueRequest
WorkbookAnalysisExecuteRequest
SpecializedDomainExecuteRequest
```

## Estrategia de módulos

Crear como máximo un módulo de contracts dedicado si no cabe limpiamente en uno existente, por ejemplo:

```text
service_1_product_execution_contracts_v1.py
```

No crear un módulo por command.

`service_1_request_kind_v1.py` debe ser ABSORB/retirado si queda sin responsabilidad.

## Archivos

```text
service_1_product_pipeline_v1.py
service_1_pipeline_v1.py (legacy First Aid tool path to retire)
service_1_manual_first_aid_delivery_flow_v1.py (demote to support if still useful)
pymia/cli/service_1_product.py
service_1_assisted_web_semantic_reception_v1.py
service_1_assisted_web_v1.py
service_1_semantic_reception_server_v1.py
```

## Implementación

1. Product Root acepta un request discriminado y dependencies separadas.
2. `WorkbookSemanticStartRequest` inicia SEM-8.
3. `WorkbookSemanticContinueRequest` consume previous semantic state + owner responses.
4. `WorkbookAnalysisExecuteRequest` exige canonical ingestion + confirmed bindings + analysis identity + tenant context; vuelve a ejecutar P7/P8 antes de F7/F9.
5. `SpecializedDomainExecuteRequest` exige subtype cerrado.
6. Migrar CLI/Web/HTTP en el mismo ciclo; no dejar wrapper legacy productivo.
7. Eliminar/absorber:

```text
semantic_reception_only
use_assisted_semantics
semantic_run_override productivo
analysis_execution_request dict informal
specialized request kwargs separados
tool_requests branch / run_service_1_pipeline_v1 fifth execution path
```

`semantic_atomic_confirmation` sólo puede sobrevivir como campo explícito de SemanticStart si sigue siendo funcionalmente necesario, no como workflow selector.

## Tests

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_product_pipeline_v1.py \
  tests/smartpyme/test_service_1_request_kind_dispatch_v1.py \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py
```

El test de request kind debe reemplazarse/renombrarse conceptualmente a explicit execution contract discrimination.

## Architecture gates

```text
FOUR_EXPLICIT_EXECUTION_COMMANDS
NO_SHAPE_DISPATCH
NO_PROCEDURAL_ROOT_SWITCHES
ONE_PRODUCTIVE_EXECUTION_ROOT
NO_FIFTH_TOOL_REQUESTS_EXECUTION_PATH
CLI_WEB_ONLY_SURFACES
```

## Exit

Todos PASS y ningún caller productivo usa la firma legacy del root.

---

# R4.5 — Integration checkpoint transversal R0–R4

## Dependencia

R4 verificado PASS en sesión Codex read-only separada.

## Objetivo

Probar que R0–R4 funcionan juntos en el mismo worktree antes de iniciar retiros destructivos de R5. Este checkpoint no crea arquitectura nueva, no reemplaza R12/R13 y no autoriza limpieza adicional.

## Modo

Read-only sobre runtime/tests. Única escritura: evidencia del checkpoint.

## Validación

Ejecutar el prompt operativo vigente:

```text
docs/current/prompts/SERVICE_1_CODEX_R4_5_INTEGRATION_CHECKPOINT_V1.md
```

Debe combinar los focales/guards representativos de identidad, canonical ingestion, D7, SEM/P6, Product Root y Web/HTTP, más verificación estática de los gates R0–R4.

No full suite.

## Exit

```text
R0_R4_COMBINED_INTEGRATION = PASS
R0_R4_ARCHITECTURE_GATES_PRESERVED = PASS
REGRESSION_BETWEEN_R0_R4 = 0
```

Sólo entonces se habilita R5.

---

# R5 — Retiro semantic legacy + sheet1

## Dependencias

R4 + parity R3.

## Objetivo

Eliminar generaciones semánticas que ya no pertenecen al target.

## Archivos

```text
service_1_legacy_semantic_reentry_compat_v1.py
service_1_deterministic_semantic_pipeline_v1.py
pymia/cli/service_1_product.py
service_1_assisted_web_v1.py
semantic/owner modules con fallback sheet1
```

## Implementación

1. Confirmar zero productive callers del shim legacy.
2. Eliminar shim.
3. Confirmar SEM-8 deterministic parity.
4. Eliminar pipeline determinístico histórico como composition root, conservando componentes compartidos.
5. Retirar `sheet1` fallbacks productivos.
6. No eliminar labels de fixtures/documentación por búsqueda ciega.

## Tests

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py \
  tests/smartpyme/test_service_1_owner_semantic_evidence_reentry_v1.py \
  tests/smartpyme/test_service_1_multisheet_parity_guard_v1.py
```

## Exit

```text
PRODUCTIVE_LEGACY_SEMANTIC_CALLERS = 0
PARALLEL_SEMANTIC_FSM = 0
PRODUCTIVE_SHEET1_FALLBACK = 0
```

---

# R6 — D4 → P8 → F7 provenance gobernada

## Dependencias

R1 + R2 + R4.

## Objetivo

Cerrar la identidad del relationship binding sin duplicar autoridades.

## Archivos

```text
service_1_logical_relationship_graph_v1.py
service_1_owner_relationship_confirmation_event_v1.py
service_1_computability_v1.py
service_1_analysis_evidence_preparation_v1.py
```

## Implementación

Definir `governed_relationship_binding` dentro de contracts P8 existentes cuando sea posible; evitar módulo extra salvo necesidad clara.

Debe transportar:

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

P8 valida contra D4/D3/current artifact/workbook y emite binding.

F7:

- valida binding e identidad;
- no redescubre relationship;
- no decide computability;
- conserva runtime checks sobre filas reales.

## Tests

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_logical_relationship_graph_d4_v1.py \
  tests/smartpyme/test_service_1_analysis_computability_f5_v1.py \
  tests/smartpyme/test_service_1_computability_v1.py \
  tests/smartpyme/test_service_1_analysis_evidence_preparation_f7_v1.py \
  tests/smartpyme/test_service_1_semantic_dimensions_relationships_f6_v1.py
```

## Casos negativos obligatorios

```text
binding from other workbook → BLOCK
stale graph_ref → BLOCK
schema mismatch → BLOCK
missing owner event → BLOCK
right duplicate keys → BLOCK
ONE_TO_ONE left duplicate keys → BLOCK
missing join match → BLOCK
join conflict → BLOCK
```

## Exit

```text
D4_P8_F7_PROVENANCE = PASS
F7_ONLY_JOIN_MATERIALIZATION = PASS
F7_RUNTIME_CARDINALITY_SAFETY = PASS
```

---

# R7 — Kernel matemático común + policy declarativa

## Dependencia

R4.

## Objetivo

Eliminar matemática/policy empresarial distribuida en capacidades de workbook.

## Archivos

```text
pymia/contracts/formula_contract.py
pymia/services/formula_engine_service.py
pymia/contracts/formula_rules_v1.json
service_1_capability_contracts_v1.py
service_1_capability_registry_v1.py
service_1_generic_capability_engine_v1.py
service_1_liq_001_evaluator_v1.py
service_1_ren_001_evaluator_v1.py
service_1_liq_002_evaluator_v1.py
service_1_pyme_011_evaluator_v1.py
```

## Implementación

1. Extender classification contract:

```text
ClassificationPredicate
ClassificationRule(match=ALL|ANY, predicates=[])
```

2. Mantener backward compatibility de definiciones simples durante la migración interna, pero sin alias runtime indefinido.
3. El classifier sólo compara; cero aritmética.
4. Migrar row reductions a `MathPrimitiveOperation`.
5. Fórmulas de negocio siguen/entran al catálogo.
6. LIQ/REN dejan de ser specialized de root.
7. No crear nuevo engine.

## Tests

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_generic_capability_kernel_v1.py \
  tests/smartpyme/test_service_1_cycle_044a_generic_capability_kernel_architecture_v1.py \
  tests/smartpyme/test_service_1_liq_001_evaluator_v1.py \
  tests/smartpyme/test_service_1_ren_001_evaluator_v1.py \
  tests/smartpyme/test_service_1_liq_002_productive_root_v1.py \
  tests/smartpyme/test_service_1_pyme_011_productive_root_v1.py \
  tests/smartpyme/test_service_1_analysis_math_execution_f8_v1.py
```

## Nuevos gates

```text
NO_INLINE_BUSINESS_MATH in migrated evaluators
NO_INLINE_BUSINESS_CLASSIFICATION
CLASSIFIER_ARITHMETIC = 0
MATH_KERNEL_AUTHORITY_COUNT = 1
```

## Exit

PASS de todos los anteriores.

---

# R8 — Specialized convergence

## Dependencia

R7.

## Objetivo

Conservar workflows realmente especializados sin darles matemática/policy soberana.

## Archivos

```text
service_1_consorcios_expense_variance_v1.py
service_1_consorcios_collection_aging_v1.py
service_1_reconciliation_product_request_v1.py
service_1_reconciliation_request_gate_v1.py
service_1_reconciliation_candidate_to_assisted_review_v1.py
formula_rules_v1.json
```

## Implementación Consorcios

```text
group SUM → MathPrimitive SUM
budget variance → named formula
historical variance → named formula
MAX deviations → MathPrimitive MAX
aging ratio → named formula
classification → declarative predicates
```

Mantener distinct workflow/output.

## Reconciliation

Conservar matcher/review flow; no convertir confidence en autoridad ni resolver ambigüedad automáticamente.

## Anti-dump test

Un subtype `SPECIALIZED` nuevo debe fallar si no está explícitamente registrado/contratado y no cumple criterios.

## Tests

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_consorcios_expense_variance_v1.py \
  tests/smartpyme/test_service_1_consorcios_collection_aging_v1.py \
  tests/smartpyme/test_service_1_reconciliation_product_wiring_v1.py \
  tests/smartpyme/test_service_1_reconciliation_governed_flow_v1.py
```

## Exit

```text
SPECIALIZED_ANTI_DUMP = PASS
SPECIALIZED_INLINE_BUSINESS_MATH = 0
SPECIALIZED_INLINE_CLASSIFICATION = 0
```

---

# R9 — ResultReadBoundary

## Dependencia

R4; puede desarrollarse en paralelo con R6–R8, pero debe integrarse antes de R10.

## Objetivo

Separar lectura persistida de ejecución.

## Implementación

Crear una frontera mínima, preferentemente un solo módulo:

```text
service_1_result_read_boundary_v1.py
```

con:

```text
Service1ResultQueryV1
ResultReadBoundary
```

Input mínimo:

```text
tenant identity
case_id
result_id
expected integrity digest
```

Validar tenant/case/result/integrity y cargar F13.

No llamar F9.

## Tests

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_result_memory_f13_v1.py
```

Agregar focal para ResultReadBoundary:

```text
same tenant valid result → READY
different tenant → BLOCK
wrong digest → BLOCK
read does not invoke XLSX/SEM/P7/P8/F7/F8/F9/LLM
```

## Exit

```text
RESULT_READ_SEPARATE_FROM_EXECUTION = PASS
F13_READ_NO_RECALCULATION = PASS
```

---

# R10 — Limpieza final de aliases, switches y compatibilidad

## Dependencias

R5 + R6 + R7 + R8 + R9.

## Objetivo

Eliminar deuda transitoria una vez cerrados todos sus consumers.

## Retirar

```text
CanonicalIngestionOutput aliases con zero consumers
CLI normalized_tables reinjection
service_1_request_kind_v1 si absorbido completamente
semantic_reception_only
use_assisted_semantics
semantic_run_override productivo
legacy owner_answers path
specialized kwargs separados
analysis_execution_request dict informal
sheet1 productivo
legacy semantic files ya sin callers
```

## No hacer

No borrar un alias por nombre si todavía es parte de un contrato canónico distinto; demostrar zero consumers primero.

## Gates

Búsquedas/call graph:

```text
PRODUCTIVE_COMPATIBILITY_SHIMS = 0
TRANSITIONAL_ALIAS_WITHOUT_EXIT = 0
PROCEDURAL_ROOT_SWITCHES = 0
POST_CONSTRUCTION_ENVELOPE_MUTATIONS = 0
PRODUCTIVE_SHEET1_FALLBACK = 0
```

## Tests

L2 architecture tests + bounded root/semantic/ingestion suite.

---

# R11 — Registry reconciliation

## Dependencia

R10.

## Objetivo

Hacer que el registry represente el código final, no el estado histórico.

## Acciones

1. Enumerar físicamente todos `pymia/smartpyme/service_1_*.py`.
2. Comparar con `docs/service_1_module_disposition.v1.json`.
3. Aplicar `SERVICE_1_CODE_DISPOSITION_FINAL_V1.md`.
4. Quitar módulos borrados.
5. Agregar módulos canónicos/support faltantes.
6. Recalcular root reachability.
7. Actualizar counts.

## Test

```bash
python -m pytest -q tests/smartpyme/test_service_1_module_disposition_registry_v1.py
```

## Exit

```text
FILESYSTEM_MODULE_SET == REGISTRY_MODULE_SET
MISSING = 0
EXTRA = 0
DUPLICATES = 0
PRODUCTIVE_LEGACY = 0
```

---

# R12 — Integration checkpoint

## Dependencia

R11.

## Objetivo

Probar juntas las fronteras arquitectónicas antes del full suite.

## Suite recomendada

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_architecture_lock_v1.py \
  tests/smartpyme/test_service_1_product_pipeline_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_workbook_logical_model_d7_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_analysis_computability_f5_v1.py \
  tests/smartpyme/test_service_1_analysis_evidence_preparation_f7_v1.py \
  tests/smartpyme/test_service_1_analysis_math_execution_f8_v1.py \
  tests/smartpyme/test_service_1_analysis_result_projection_f9_v1.py \
  tests/smartpyme/test_service_1_result_memory_f13_v1.py \
  tests/smartpyme/test_service_1_module_disposition_registry_v1.py
```

Agregar los nuevos tests de commands/result read/classification/provenance creados en ciclos anteriores.

## Exit

```text
INTEGRATION_CHECKPOINT = PASS
ARCHITECTURE_GATES = PASS
```

Si falla, corregir por contrato; no full suite todavía.

---

# R13 — Full suite final

## Dependencia

R12 PASS.

## Preparación

Instalar/configurar Chromium/Playwright requerido por los 3 E2E errors históricos antes de interpretar resultado.

## Ejecutar una vez

```bash
python -m pytest -q
```

## Exit obligatorio

```text
FAILED = 0
ERRORS = 0
```

Skips sólo si están explícitamente gobernados y no cubren un gate final obligatorio.

Registrar:

```text
exact command
exact HEAD/worktree SHA or candidate commit SHA
passed/failed/skipped/errors
environment notes
```

---

# R14 — Real XLSX E2E y cierre

## Dependencia

R13 0 FAIL / 0 ERROR.

## Corpus mínimo

```text
cafeteria_abc.xlsx
pyme_textil_compleja.xlsx
distribuidora_mayorista_compleja.xlsx
fabrica_industrial_compleja.xlsx
PYMIA_CONSORCIO_CABILDO_2026_07.xlsx
conciliacion_mercado_pago_banco_corregida.xlsx
S1_A1_SYNTH_013_ventas_aux_sheets.xlsx
S1_A1_SYNTH_006_ventas_duplicate_columns.xlsx
```

## Debe probar

```text
real upload/read
content identity
multisheet
D1-D7
semantic deterministic provider
bounded LLM interface when configured
explicit owner confirmation
analysis discovery
P7/P8
relationships/join safety
math kernel
classification
F9
F13 persistence
ResultRead without recalculation
fail-closed adversarial cases
```

## Cafetería

Resolver por evidencia cualquier diferencia histórica de total. No hardcodear el resultado esperado para hacer pasar el caso; verificar fuente, descuentos, unidades y fórmula gobernada.

## Exit

Aplicar `SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`.

Sólo si todos los gates pasan:

```text
SERVICE_1_IMPLEMENTATION_COMPLETE = YES
SERVICE_1_INTEGRAL_HEALTH = PASS
```

Commit/push/deploy siguen requiriendo autorización explícita.

---

## 3. Regla para agentes que retoman a mitad del plan

No asumir el último ciclo completado por la documentación.

Para cada Rn:

```text
inspect physical code
→ run its exit gate
→ if PASS, mark VERIFIED and continue
→ if FAIL, implement only missing delta
```

No reimplementar un ciclo ya convergido.

---

## 4. Stop conditions

Detener y reportar si:

```text
una decisión normativa resulta físicamente imposible sin cambiar arquitectura
un test exige explícitamente conducta prohibida por target y no puede migrarse sin pérdida legítima
se descubre un segundo source of truth no contemplado
se requiere secret/productive infrastructure unavailable para un gate obligatorio
un cambio exigiría nuevo engine/root/FSM
```

No detener por mera dificultad, cantidad de archivos o tests legacy; en esos casos seguir el plan de migración.
