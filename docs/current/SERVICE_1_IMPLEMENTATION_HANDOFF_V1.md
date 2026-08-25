# Servicio 1 — Implementation Handoff V1

**Estado:** `AUTHORITATIVE_EXECUTION_HANDOFF`  
**Fecha:** 2026-08-23  
**Baseline conocido:** `8d5708e9becdddaa5aa24387b310972643d1ef86` + worktree local no committeado  
**Objetivo:** permitir que cualquier LLM técnicamente competente continúe y complete Servicio 1 sin depender del historial de chat, sin rediseñar la arquitectura y sin introducir parches transitorios no gobernados.

---

## 1. Regla de entrada

Antes de modificar una sola línea de runtime, el agente debe leer en este orden:

```text
1. AGENTS.md
2. ARCHITECTURE_GUARDRAILS.md
3. docs/current/README.md
4. docs/current/SERVICE_1_CANONICAL_AXIS.md
5. docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
6. docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md
7. docs/current/SERVICE_1_CODE_DISPOSITION_FINAL_V1.md
8. docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md
9. docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md
10. docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md
```

Documentos de evidencia, no de autoridad:

```text
docs/current/SERVICE_1_FINAL_ARCHITECTURE_DIALECTIC_V1.md
docs/current/SERVICE_1_INTEGRAL_HEALTH_AUDIT_REPORT_V1.md
docs/current/SERVICE_1_INTEGRAL_HEALTH_AUDIT_PLAN_V1.md
_audit/
```

Si un documento de evidencia contradice `SERVICE_1_CANONICAL_AXIS.md` o `SERVICE_1_ARCHITECTURE_LOCK.md`, prevalece la autoridad normativa.

---

## 2. Estado que recibe el agente

La arquitectura objetivo está cerrada.

```text
DIALECTICAL_REVIEW_COMPLETE = PASS
OPEN_ARCHITECTURAL_DECISIONS = 0
TARGET_ARCHITECTURE_CLOSED = YES
```

El código todavía no está reconstruido contra ese target.

```text
CURRENT_WORKTREE_INTEGRAL_CERTIFICATION = NO
RECONSTRUCTION_IMPLEMENTATION = PENDING
LAST_AUDIT_FULL_SUITE = 3806 passed / 77 failed / 7 skipped / 3 errors
REAL_WORKBOOK_E2E_AFTER_RECONSTRUCTION = NOT_OBSERVED
MODULE_REGISTRY_CURRENT_WORKTREE = INCOMPLETE
```

Los tres errores E2E del último full suite fueron asociados a Chromium ausente. No usar ese hecho para ignorar los 77 FAIL ni para declarar salud del sistema.

---

## 3. Arquitectura objetivo inmutable durante la reconstrucción

### 3.1 Ejecución

Existe una sola raíz productiva de ejecución:

```text
service_1_product_pipeline_v1.py
→ target role: ProductExecutionRoot thin dispatcher
```

Acepta exactamente cuatro command contracts:

```text
WorkbookSemanticStartRequest
WorkbookSemanticContinueRequest
WorkbookAnalysisExecuteRequest
SpecializedDomainExecuteRequest
```

No se permite seleccionar workflows por combinación de kwargs, shape, presencia de campos o flags procedurales.

### 3.2 Lectura de resultados

La lectura de ResultSets persistidos NO pasa por ProductExecutionRoot:

```text
Web / CLI
→ Service1ResultQueryV1
→ ResultReadBoundary
→ F13 load
→ persisted projection
```

No reabre XLSX, no usa LLM, no ejecuta SEM/P7/P8/F7/F8/F9 y no recalcula.

### 3.3 Workbook

```text
XLSX
→ source_artifact_ref
→ canonical reader
→ CanonicalIngestionOutput V2
→ D1 → D2 → D3 → D4 → D5 → D6 → D7
→ SemanticStart
→ owner
→ SemanticContinue
→ P6 / CONFIRMED_BINDINGS
→ AnalysisExecute
→ P7
→ P8
→ F7
→ common math kernel
→ declarative classification
→ F9
→ F13
```

### 3.4 Semántica

Una sola FSM productiva provider-neutral:

```text
SemanticStart(det | bounded LLM)
→ deterministic validation
→ explicit owner dialogue
→ SemanticContinue(owner evidence)
→ shared reinjector/P6
→ CONFIRMED_BINDINGS | follow-up
```

El provider determinístico es un provider, no una segunda FSM.

### 3.5 Matemática

Única soberanía matemática:

```text
pymia/contracts/formula_contract.py
FormulaEngineService
MathPrimitiveOperation
formula_rules_v1 / canonical formula catalog
```

F8 coordina matemática F12, pero no es el único caller físico del kernel.

### 3.6 Policy

Classification es declarativa y no calcula.

```text
ClassificationPredicate
ClassificationRule(match=ALL|ANY, predicates=[])
```

SUM/MAX/ratio/percentage/difference/etc. deben llegar ya calculados por el kernel.

### 3.7 Relaciones

```text
D4 = structural relationship authority
Owner = human confirmation evidence
P8 = computability/use + provenance validation
F7 = sole physical join materializer + runtime safety
```

F7 conserva bloqueos runtime de cardinalidad; eso no duplica D4.

### 3.8 Identidad

```text
case_id = opaque workflow identity
source_artifact_ref = xlsx:sha256:<actual bytes>
workbook_ref = digest(source_artifact_ref + ingestion_scope + reader/schema version)
sheet_ref = digest(workbook_ref + exact sheet_name)
filename = provenance/display only
```

No usar filename, basename, path, mtime, size ni `sheet1` como identidad soberana.

---

## 4. Prohibiciones absolutas durante la implementación

El agente NO puede:

- crear una segunda raíz productiva;
- crear un segundo parser XLSX productivo;
- crear un segundo motor matemático;
- introducir un nuevo `PrimitiveEngine`;
- introducir un `PolicyRegistry` global o DSL general de expresiones;
- preservar el pipeline semántico histórico como segunda FSM;
- agregar un wrapper de compatibilidad sin destino de retiro escrito;
- agregar aliases nuevos para hacer pasar tests legacy;
- usar `sheet1` como fallback productivo;
- usar filename como identidad de workbook;
- permitir al LLM calcular, agregar, materializar joins o decidir computabilidad;
- mover matemática empresarial a UI/web/CLI;
- modificar `CanonicalIngestionOutput` después de construirlo;
- cambiar tests para conservar una conducta legacy que contradice el target;
- ejecutar full suite después de cada cambio local;
- commit, push o deploy sin autorización explícita del usuario.

Ante una contradicción no contemplada por los documentos rectores:

```text
STOP_ARCHITECTURE
→ documentar evidencia física
→ no inventar patch
```

---

## 5. Regla de trabajo

Cada ciclo debe seguir:

```text
1 cambio arquitectónicamente acotado
→ L0 syntax/import
→ L1 focal tests
→ L2 architecture guards
→ L3 bounded neighbor regression si corresponde
→ veredicto
→ actualizar ledger/documentación si cambió la verdad física
→ siguiente dependencia
```

No usar la cantidad de tests verdes como sustituto de arquitectura.

Un cambio que haga pasar tests pero aumente cualquiera de estas métricas es `FAIL_ARCHITECTURE`:

```text
productive_paths
compatibility_shims
transitional_aliases
root procedural switches
sheet1 fallbacks
legacy productive callers
inline business math
inline business classification
post-construction envelope mutations
authority collisions
parallel semantic FSMs
```

---

## 6. Política de worktree

El worktree actual contiene cambios valiosos y cambios transitorios. No hacer `git reset --hard` ni restauración masiva.

Clasificar cada cambio usando `SERVICE_1_CODE_DISPOSITION_FINAL_V1.md`:

```text
KEEP
REDESIGN
ABSORB
MIGRATE
DELETE_AFTER_DEPENDENCY_CLOSURE
OFFLINE
```

`_audit/` permanece `OFFLINE / UNCOMMITTED` salvo autorización explícita.

---

## 7. Política de tests

Niveles:

```text
L0 = syntax/import
L1 = focal contract tests
L2 = architecture/authority guards
L3 = bounded neighbors
L4 = integration checkpoint
L5 = full suite only after major convergence
L6 = real XLSX E2E
```

Último full suite conocido:

```text
3806 passed / 77 failed / 7 skipped / 3 errors
```

No usarlo como baseline de aceptación. La aceptación final exige `0 FAIL / 0 ERROR` sobre el SHA final.

---

## 8. Corpus físico obligatorio al final

Como mínimo deben probarse archivos reales existentes:

```text
prueba_excels/cafeteria_abc.xlsx
prueba_excels/pyme_textil_compleja.xlsx
prueba_excels/distribuidora_mayorista_compleja.xlsx
prueba_excels/fabrica_industrial_compleja.xlsx
prueba_excels/PYMIA_CONSORCIO_CABILDO_2026_07.xlsx
prueba_excels/conciliacion_mercado_pago_banco_corregida.xlsx
prueba_excels/S1_A1_SYNTH_013_ventas_aux_sheets.xlsx
prueba_excels/S1_A1_SYNTH_006_ventas_duplicate_columns.xlsx
```

Los positivos deben ejecutar correctamente y los adversariales deben fallar cerrado según contrato.

La cafetería es obligatoria porque fue el caso productivo de referencia y existe una diferencia histórica de totales que debe quedar resuelta por evidencia, no por hardcode.

---

## 9. Definition of Done resumida

Servicio 1 sólo puede marcarse terminado cuando:

```text
OPEN_ARCHITECTURAL_DECISIONS = 0
CURRENT_CODE_MATCHES_TARGET = YES
ONE_PRODUCTIVE_EXECUTION_ROOT = PASS
FOUR_EXPLICIT_EXECUTION_COMMANDS = PASS
ONE_CANONICAL_INGESTION = PASS
CANONICAL_ENVELOPE_IMMUTABLE_AFTER_BUILD = PASS
ONE_PRODUCTIVE_XLSX_READER = PASS
WORKBOOK_D1_D7_MANDATORY = PASS
ONE_PRODUCTIVE_SEMANTIC_FSM = PASS
NO_PRODUCTIVE_LEGACY_SHIMS = PASS
NO_SHEET1_FALLBACK = PASS
CONTENT_ADDRESSED_ARTIFACT_IDENTITY = PASS
D4_P8_F7_PROVENANCE = PASS
F7_RUNTIME_JOIN_SAFETY = PASS
ONE_COMMON_MATH_KERNEL = PASS
NO_INLINE_BUSINESS_MATH = PASS
DECLARATIVE_CLASSIFICATION = PASS
RESULT_READ_NO_RECALCULATION = PASS
MODULE_REGISTRY_COMPLETE = PASS
FULL_SUITE = 0 FAIL / 0 ERROR
REAL_XLSX_E2E = PASS
EXACT_SHA_RECORDED = YES
```

Sólo después puede evaluarse commit/push/deploy, y únicamente con autorización explícita.

---

## 10. Qué hacer si el agente entra sin contexto

No pedir al usuario que reconstruya la historia.

Proceder así:

```text
read authority docs
→ inspect git status
→ compare current code with ARCHITECTURE_TO_CODE_DELTA
→ start first incomplete dependency node in RECONSTRUCTION_PLAN
→ execute prescribed tests
→ record verdict
```

Si un ciclo ya figura físicamente implementado, verificarlo y marcarlo cerrado; no reimplementarlo por asumir que el plan está desactualizado.

---

## 11. Frase de control

```text
No diseñar Servicio 1 mientras se implementa.
La arquitectura ya está cerrada.
El trabajo pendiente es hacer converger el código y demostrarlo.
```

---

## 12. Instrucciones operativas y prompts ejecutables

Los agentes no deben improvisar prompts desde el chat.

Instrucciones permanentes:

```text
docs/current/SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md
```

Prompt ejecutor vigente del próximo nodo autorizado:

```text
docs/current/prompts/SERVICE_1_EXECUTOR_PROMPT_R0_R1_V1.md
```

Prompt verificador independiente correspondiente:

```text
docs/current/prompts/SERVICE_1_VERIFIER_PROMPT_R0_R1_V1.md
```

Regla:

```text
executor PASS
→ independent verifier
→ sólo si verifier PASS, habilitar siguiente nodo
```

No copiar planes de implementación al chat como fuente de continuidad. La continuidad vive en estos archivos del repositorio.
