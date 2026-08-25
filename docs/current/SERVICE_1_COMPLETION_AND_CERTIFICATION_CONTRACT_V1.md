# Servicio 1 — Completion and Certification Contract V1

**Estado:** `AUTHORITATIVE_DEFINITION_OF_DONE`  
**Fecha:** 2026-08-23  
**Propósito:** definir objetivamente cuándo Servicio 1 puede considerarse reconstruido, sano y listo para evaluación de release. Ningún LLM puede declarar “terminado” usando criterio propio.

---

## 1. Regla principal

```text
FUNCTIONAL_PASS ≠ ARCHITECTURAL_PASS
ARCHITECTURAL_PASS ≠ INTEGRAL_CERTIFICATION
LOCAL_TESTS_PASS ≠ SERVICE_1_COMPLETE
```

Servicio 1 sólo está terminado si **todos** los gates de este documento pasan sobre el mismo estado físico/SHA candidato.

---

## 2. Identidad del candidato

Antes de certificar registrar:

```text
BRANCH
HEAD / candidate SHA
WORKTREE_STATUS
PYTHON_VERSION
OS / environment
PLAYWRIGHT/CHROMIUM_AVAILABLE
EXTERNAL_LLM_PROVIDER_CONFIGURATION_STATUS
DATABASE/PERSISTENCE_TEST_MODE
```

No mezclar resultados de distintos SHA/worktrees.

---

# 3. Gates de arquitectura — todos obligatorios

## A01 — One Productive Execution Root

```text
PASS si:
- ProductExecutionRoot único;
- Web/CLI son surfaces;
- ResultReadBoundary no ejecuta análisis;
- no second root reachable.
```

## A02 — Four Explicit Execution Commands

```text
WorkbookSemanticStartRequest
WorkbookSemanticContinueRequest
WorkbookAnalysisExecuteRequest
SpecializedDomainExecuteRequest
```

PASS si workflow no se infiere por kwargs/shape/flags.

## A03 — Result Read Separate from Execution

PASS si `Service1ResultQueryV1 → ResultReadBoundary → F13` no toca execution root ni recalcula.

## A04 — One Canonical Workbook Envelope

PASS si existe un único `CanonicalIngestionOutput` self-contained y todos los productive consumers usan ese contrato.

## A05 — Canonical Envelope Immutable after Construction

PASS si CLI/Web/UI/adapters no agregan/corrigen/reinyectan campos post-build.

## A06 — One Productive XLSX Reader

PASS si todo workbook productivo usa el reader canónico; CSV/document support no cuenta como segundo XLSX reader.

## A07 — WORKBOOK D1–D7 Mandatory

PASS si ningún workbook puede llegar a SEM/P7/P8 saltando D1–D7.

## A08 — D7 Evidence Only

PASS si D7 no otorga runtime, grain, computability, join, delivery ni semantic rebind authority.

## A09 — One Productive Semantic FSM

PASS si:

```text
SEM-8 / canonical FSM = 1
historical deterministic composition root = retired
legacy semantic compat = retired
provider deterministic + LLM = providers, not FSMs
```

## A10 — Explicit Owner Confirmation

PASS si first contact no auto-confirma significado por confidence y P6 requiere owner evidence donde corresponde.

## A11 — Table Scope Built Once

PASS si `table_scoped_semantics` se produce en D6/D7 y SEM sólo consume.

## A12 — P7 Authority

PASS si P7 es única autoridad de requirement/grain y no queda bypass.

## A13 — P8 Authority + Provenance

PASS si P8 decide computability/use y valida artifact/workbook/schema/D4/owner provenance antes de emitir governed relationship binding.

## A14 — F7 Only Join Materializer

PASS si F7 es único lugar que materializa joins y no existe join materialization en D4/P8/UI/evaluator.

## A15 — F7 Runtime Safety Preserved

Todos obligatorios:

```text
duplicate right key → BLOCK
ONE_TO_ONE duplicate left key → BLOCK
missing match → BLOCK
join conflict → BLOCK
cardinality violation → BLOCK
```

## A16 — One Common Math Kernel

PASS si matemática empresarial productiva usa:

```text
formula_contract.py
FormulaEngineService
MathPrimitiveOperation
formula catalog
```

No segundo engine.

## A17 — No Inline Business Math

PASS si evaluadores migrados no conservan SUM/MAX/ratio/percentage/difference/business formula ad-hoc fuera del kernel.

Parsing/type validation no se considera business math.

## A18 — Declarative Classification without Arithmetic

PASS si classification usa el contrato declarativo final y el classifier sólo compara valores ya calculados.

## A19 — Specialized Anti-Dump

PASS si `SPECIALIZED` sólo acepta subtypes explícitos que cumplen los siete criterios normativos; LIQ/REN no entran por specialized y legacy semantics no usa specialized.

## A20 — Content-Addressed Artifact Identity

PASS si:

```text
uploaded bytes → source_artifact_ref from bytes
local path → source_artifact_ref from bytes
same content different filename → same artifact ref
different content same basename → different artifact ref
```

## A21 — Workbook / Sheet Identity

PASS si workbook_ref depende de artifact + ingestion scope + reader/schema version y sheet_ref está calificado por workbook + exact sheet name.

## A22 — No Filename Identity

PASS si filename no participa como identidad estructural soberana.

## A23 — No Productive `sheet1` Fallback

PASS si no se fabrica sheet identity cuando falta evidencia.

## A24 — No Productive Legacy Shims

PASS si productive caller count de legacy semantic compatibility = 0.

## A25 — No Indefinite Compatibility

PASS si cada alias/shim/compat restante tiene exit gate o ya fue retirado; target final esperado = 0 productive indefinite compatibility.

## A26 — No LLM Math / Runtime Authority

PASS si LLM sólo propone semántica y nunca:

```text
calcula
agrega
materializa join
decide computability
autoriza runtime/delivery
```

## A27 — Tenant Memory Hint-Only

PASS si no hay auto-rebind, cross-tenant leakage ni memory authority.

## A28 — F9 Result Projection Only

PASS si F9 proyecta ResultSet/findings/outcome y no adquiere math/join/computability authority.

## A29 — F13 Persistence/Read without Recalculation

PASS si F13 guarda/carga snapshots con integridad y read no recalcula.

## A30 — Module Registry Complete

PASS si filesystem y registry coinciden exactamente.

---

# 4. Gates de entropía — todos obligatorios

Medir sobre closure productivo final:

```text
SECOND_EXECUTION_ROOTS = 0
FIFTH_TOOL_REQUESTS_EXECUTION_PATHS = 0
PARALLEL_SEMANTIC_FSMS = 0
PRODUCTIVE_LEGACY_SHIMS = 0
PRODUCTIVE_SHEET1_FALLBACKS = 0
POST_BUILD_ENVELOPE_MUTATIONS = 0
PROCEDURAL_ROOT_WORKFLOW_SWITCHES = 0
INDEFINITE_TRANSITIONAL_ALIASES = 0
SECOND_MATH_ENGINES = 0
INLINE_BUSINESS_MATH_SITES = 0 en componentes migrados
INLINE_BUSINESS_CLASSIFICATION_SITES = 0 en componentes migrados
UNREGISTERED_SERVICE_1_MODULES = 0
AUTHORITY_COLLISIONS = 0
```

Un valor >0 bloquea completion aunque full suite sea verde.

---

# 5. Test ladder de certificación

## L0 — Syntax / Import

Todos los módulos modificados importan correctamente.

## L1 — Focal

Cada nodo R1–R11 del Reconstruction Plan tiene focal PASS registrado.

## L2 — Architecture guards

Deben existir/actualizarse tests que hagan fallar regresiones de:

```text
second root
shape dispatch
sheet1 fallback
legacy semantic caller
inline math/policy
post-build envelope mutation
D4/P8/F7 provenance bypass
ResultRead recalculation
registry drift
```

## L3 — Bounded neighbors

Todas las suites vecinas de módulos modificados pasan antes de integración.

## L4 — Integration checkpoint

El conjunto definido en R12 debe pasar completo.

## L5 — Full suite

Ejecutar:

```bash
python -m pytest -q
```

Condición:

```text
FAILED = 0
ERRORS = 0
```

No aceptar `known failure` si toca un gate obligatorio.

Playwright/Chromium debe estar disponible antes de interpretar E2E browser errors.

## L6 — Real XLSX E2E

Corpus mínimo obligatorio en §7.

---

# 6. Resultados funcionales obligatorios

## Workbook path

Debe demostrarse:

```text
upload/read
identity
D1-D7
semantic proposal
owner confirmation
CONFIRMED_BINDINGS
analysis discovery
P7/P8
F7
math
classification
F9
F13
read persisted result
```

## Deterministic semantic provider

Debe funcionar sin red/LLM y producir flujo completo hasta owner confirmation/bindings.

## Bounded LLM provider

Cuando exista credencial/configuración del entorno, debe probarse una interfaz real sin concederle math/runtime authority.

La ausencia temporal de credenciales no habilita hardcodear semántica para “simular” el provider.

## Specialized path

Consorcios/reconciliation deben usar request subtype explícito y common math/policy authorities.

---

# 7. Corpus XLSX físico mínimo

## Principal

```text
prueba_excels/cafeteria_abc.xlsx
```

Debe cubrir análisis reales de ventas/margen y resolver cualquier discrepancia histórica de totales desde evidencia y fórmulas gobernadas.

## Generalización

```text
prueba_excels/pyme_textil_compleja.xlsx
prueba_excels/distribuidora_mayorista_compleja.xlsx
prueba_excels/fabrica_industrial_compleja.xlsx
```

## Specialized

```text
prueba_excels/PYMIA_CONSORCIO_CABILDO_2026_07.xlsx
prueba_excels/conciliacion_mercado_pago_banco_corregida.xlsx
```

## Multisheet

```text
prueba_excels/S1_A1_SYNTH_013_ventas_aux_sheets.xlsx
```

## Adversarial fail-closed

```text
prueba_excels/S1_A1_SYNTH_006_ventas_duplicate_columns.xlsx
prueba_excels/S1_A1_SYNTH_003_ventas_missing_columns.xlsx
prueba_excels/S1_A1_SYNTH_004_ventas_ambiguous_names.xlsx
```

Un adversarial PASS no significa ejecutar: significa bloquear correctamente con reason estable y sin fallback.

---

# 8. Cafetería acceptance específica

El caso `cafeteria_abc.xlsx` debe registrar, como mínimo:

```text
source_artifact_ref
workbook_ref
sheet refs
column refs
owner-confirmed semantic bindings
computable analysis list
analysis selected
formula refs / primitive operations
result set
integrity digest
persisted memory ref
read-back result
```

Existe una diferencia histórica observada entre totales de ventas reportados en distintos momentos. El cierre debe explicar cuál es el total correcto para el contrato actual y por qué, identificando:

```text
rows included/excluded
quantity × price semantics
discount semantics if present
catalog vs transactional price
formula/aggregation path
```

Está prohibido codificar el total esperado dentro del runtime.

---

# 9. Persistence / tenant acceptance

Obligatorio:

```text
same tenant result read = PASS
other tenant read = BLOCK
wrong result id = BLOCK
wrong integrity digest = BLOCK
restart/reentry does not reopen XLSX = PASS
restart/reentry does not invoke LLM = PASS
restart/reentry does not recalculate = PASS
append-only result memory = PASS
```

---

# 10. Documentation consistency gate

Antes de declarar completion, actualizar si cambió la verdad física:

```text
docs/current/README.md
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md
docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md
docs/current/SERVICE_1_CODE_DISPOSITION_FINAL_V1.md
docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md
```

No cambiar `CANONICAL_AXIS`/`ARCHITECTURE_LOCK` por decisiones de implementación salvo que se descubra una contradicción material que obligue a reabrir arquitectura mediante proceso explícito. En ese caso completion se detiene.

---

# 11. Evidence packet final obligatorio

Crear/actualizar un cierre verificable con:

```text
FINAL_SHA
BRANCH
WORKTREE_CLEAN_OR_EXPECTED_DIRTY_STATE
ARCHITECTURE_GATE_RESULTS
ENTROPY_METRICS
REGISTRY_COUNTS
FULL_SUITE_COMMAND
FULL_SUITE_RESULT
REAL_XLSX_CASES + RESULTS
CAFETERIA_RESULT_TRACE
F13_READ_TRACE
LLM_INTERFACE_RESULT if environment available
KNOWN_SKIPS
UNRESOLVED_BLOCKERS
```

`UNRESOLVED_BLOCKERS` debe ser vacío para declarar completion.

---

# 12. Veredicto final permitido

Sólo existen estos estados finales:

```text
BLOCKED
NOT_CERTIFIED
PASS_READY_FOR_RELEASE_DECISION
```

`PASS_READY_FOR_RELEASE_DECISION` significa:

```text
architecture match = PASS
all required tests = PASS
real XLSX = PASS
registry = PASS
no blockers
exact SHA recorded
```

No significa autorización automática de commit/push/deploy.

---

# 13. Plantilla de salida para cualquier LLM

```text
SERVICE_1_COMPLETION_VERDICT:
PASS_READY_FOR_RELEASE_DECISION | NOT_CERTIFIED | BLOCKED

SHA:
BRANCH:

ARCHITECTURE_GATES:
<30 gates, PASS/FAIL>

ENTROPY:
SECOND_ROOTS:
PARALLEL_SEMANTIC_FSMS:
LEGACY_SHIMS:
SHEET1_FALLBACKS:
POST_BUILD_MUTATIONS:
ROOT_SWITCHES:
INLINE_BUSINESS_MATH:
INLINE_CLASSIFICATION:
UNREGISTERED_MODULES:
AUTHORITY_COLLISIONS:

TESTS:
L0:
L1:
L2:
L3:
L4:
L5_FULL_SUITE:
L6_REAL_XLSX:

CAFETERIA:
status:
result trace:

RESULT_READ:
status:
no recalculation proven:

BLOCKERS:

FILES_CHANGED:
COMMIT:
PUSH:
DEPLOY:
```

No usar prosa ambigua en lugar de este veredicto.
