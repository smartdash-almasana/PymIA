# Servicio 1 — architecture lock

**Status:** `ACTIVE`  
**Reconciled on:** `2026-08-23`  
**Scope:** product authority, execution boundaries, support-layer boundaries and promotion rules.

## 1. Software objetivo

Servicio 1 es un microservicio determinístico para evidencia PyME con XLSX como fuente productiva principal actual. Lee archivos reales, conserva evidencia estructural, pregunta al dueño cuando el significado operativo no está cerrado, construye estado canónico, aplica gates determinísticos, ejecuta sólo capacidades explícitamente autorizadas y produce outcomes/archivos trazables.

```text
La capa conversacional conversa.
La FSM y los contratos gobiernan.
Las tools determinísticas ejecutan.
El dueño confirma significado.
La evidencia manda.
```

## 2. Superficies productivas y raíz de ejecución

Superficies productivas autorizadas:

```text
CLI / adapters de entrada
Web / HTTP semantic reception
```

Estas superficies sólo construyen requests, transportan evidencia y proyectan respuestas. No coordinan D1–D7, semántica, P7/P8, joins ni matemática por fuera de los contracts canónicos.

Raíz canónica única de **ejecución**:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
→ target role: ProductExecutionRoot thin dispatcher
```

No se autoriza una segunda raíz de ejecución. `ResultReadBoundary` es una superficie de lectura sobre F13 y no constituye una segunda raíz productiva de ejecución.

## 3. Clasificación física obligatoria

Fuente:

```text
docs/service_1_module_disposition.v1.json
```

Estado observado al reconciliar este lock contra el registry físico:

```text
TOTAL_SERVICE_1_MODULES = 111
PRODUCTIVE = 63
SUPPORT_NECESSARY = 47
EXPERIMENTAL_FROZEN = 1
```

Sólo los módulos `PRODUCTIVE` pueden integrar el closure ejecutable de la raíz canónica.

`SUPPORT_NECESSARY` puede contener ingesta auxiliar, contratos, auditoría, delivery, corpus, quality gates, web asistida, dominio u otras piezas necesarias, pero no adquiere autoridad de ejecución por clasificación de soporte.

## 4. Cadena de autoridad P0–P10

```text
P0 intake
→ P1 canonical XLSX ingestion
→ P2 profiling / physical evidence
→ P3 semantic hypothesis
→ P4 contextual evidence
→ P5 OwnerConfirmationEvent
→ P6 ApprovalDecision
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision + GovernedComputationInput
→ P9 deterministic execution
→ P10 QA / delivery
```

Invariantes:

```text
EVENT ≠ DECISION
HYPOTHESIS ≠ APPROVAL
APPROVAL ≠ COMPUTABILITY
COMPUTABILITY ≠ EXECUTION
EXECUTION ≠ DELIVERY
```

## 5. Ejecución productiva

### Workbook analysis

LIQ_001 y REN_001 son **governed workbook capabilities**, no `SPECIALIZED_REQUEST`. Su matemática debe converger al kernel canónico y su clasificación al contrato declarativo común.

Las capacidades registry-governed siguen:

```text
CapabilityDefinitionV1
→ CapabilityRegistry
→ P8 governed input
→ evidence preparation / execution coordination
→ FormulaEngineService + MathPrimitiveOperation + formula catalog
→ declarative classification policy
→ governed outcome
```

Agregar una capacidad de workbook no autoriza agregar una rama identitaria nueva en la raíz.

### SpecializedDomainExecuteRequest

Un workflow especializado sólo se admite cuando cumple simultáneamente el criterio anti-basurero normativo: input no representable sin pérdida como workbook analysis, workflow/output materialmente distinto, subtype explícito, sin bypass D1–D7 para workbook encubierto, sin semántica legacy, matemática/policy bajo autoridades canónicas y gate que impida usar `SPECIALIZED` como escape hatch.

Estado normativo actual:

```text
expense_variance = specialized candidato legítimo
collection_aging = specialized candidato legítimo
reconciliation   = specialized candidato legítimo
LIQ_001          = NO specialized
REN_001          = NO specialized
legacy semantic compat = DELETE
```

## 6. Fundaciones de plataforma integradas

Después de Stage 2 se integraron fundaciones generales:

```text
pymia/domain/*
pymia/pipeline/admission/v1/*
pymia/faithful_operator.py
pymia/application/vertical_pipeline.py
pymia/diagnostic_core/*
pymia/narrative/*
pymia/operational_harness/*
pymia/pipeline_radiography/*
```

Estas piezas están dentro del repositorio, pero la integración al repositorio no equivale a integración a la raíz productiva de Servicio 1.

### Domain lock

`pymia/domain/*` puede expresar entidades, relaciones, snapshots y tipos de dominio.

No puede:

- autorizar ejecución;
- decidir computabilidad;
- promover patologías productivas;
- reemplazar contratos de Servicio 1.

### Admission lock

La admisión puede convertir narrativa en síntomas, hipótesis y pedidos de evidencia.

Sus heurísticas y `confidence_score` sirven para priorización preanalítica.

No pueden:

- confirmar semántica;
- decidir matching;
- saltar owner confirmation;
- autorizar P8/P9;
- declarar diagnóstico final.

### Faithful Operator lock

El operador fiel puede recibir mensajes, pedir evidencia, presentar candidatos y gestionar confirmación/corrección del dueño mediante una FSM determinística.

No es una segunda raíz productiva.

Un estado `CLOSED` del operador fiel no equivale automáticamente a P6/P7/P8 satisfechos.

### Diagnostic Core lock

Un cálculo disponible puede producir un candidato o un bloqueo.

```text
CALCULATED ≠ DIAGNOSED
```

El diagnostic core no puede declarar verdad operacional por fuera de la evidencia ni convertirse en ruta paralela al producto.

### Narrative lock

La capa narrativa puede ordenar y explicar claims anclados en evidencia.

```text
NARRATIVE ≠ EVIDENCE
NARRATIVE ≠ COMPUTABILITY
NARRATIVE ≠ AUTHORIZATION
```

### Harness lock

Operational Harness y Pipeline Radiography son herramientas de observación/ingeniería.

Un estado `GREEN` significa estado de medición según sus criterios; no significa autorización de producto, runtime o delivery.

## 7. Contabilidad y conciliación

La familia contable existe como soporte contractual.

```text
service_1_accounting_contracts_v1 = SUPPORT_NECESSARY
```

El matcher algorítmico de conciliación existente está en:

```text
service_2_reconciliation_match_candidates_v1
```

El acceso productivo controlado ocurre únicamente por:

```text
service_1_reconciliation_request_gate_v1
→ service_1_reconciliation_candidate_to_assisted_review_v1
→ service_1_reconciliation_product_request_v1
→ service_1_product_pipeline_v1
```

Reglas vigentes para el wiring productivo controlado:

```text
fecha + importe no demuestra identidad
referencia es evidencia, no verdad
confidence float no decide conciliación
ambigüedad debe ser explícita
1:N / N:1 / N:M no se resuelve codiciosamente
no-imputados no se ocultan por diferencias parciales
AMBIGUOUS escala a revisión humana
```

No crear:

```text
reconciliation_core_v1 paralelo
uncertainty_resolution_v1 global
event bus
colas
microservicios distribuidos para este frente
API de conciliación antes de madurar matcher/contratos
```

## 8. Delivery lock

Delivery sólo ocurre por autorización explícita y capacidad habilitada.

La existencia de un outcome, un reporte narrativo, un workpaper o un cálculo no autoriza entrega automática.

```text
OUTCOME_READY ≠ DELIVERY_AUTHORIZED
```

## 9. Prohibiciones de arquitectura

- No nueva raíz de ejecución fuera de `service_1_product_pipeline_v1`.
- Web/CLI pueden existir como superficies productivas, pero no pueden coordinar ejecución por fuera de `ProductExecutionRoot` ni crear una ruta analítica paralela.
- `ResultReadBoundary` sólo lee F13 y no es una segunda raíz de ejecución.
- No segundo parser XLSX productivo.
- No cadena productiva paralela a P0–P10.
- No selección soberana de capacidad desde texto libre.
- No LLM runtime authority.
- No diagnóstico causal automático.
- No runtime autorizado por un score.
- No promoción automática de módulos SUPPORT.
- No web/UI con fórmulas o verdad de negocio propia.
- No owner confirmation interpretada como permiso universal.
- No harness/radiography gobernando runtime.
- No narrative layer inventando hechos.
- No componente histórico gobernando arquitectura por estar todavía presente en Git.

## 10. Regla de promoción

Antes de promover soporte a autoridad productiva deben existir:

```text
contrato explícito
ubicación en P0–P10
caller productivo legítimo
prueba de ausencia de autoridad paralela
fail-closed
focal tests
neighbor tests
architecture guards
module_disposition actualizado
documentación rectora actualizada
```

La promoción debe ser focal y verificable.

## 11. Evidencia verificable

```text
docs/service_1_architecture_lock.v1.json
docs/service_1_module_disposition.v1.json
tests/smartpyme/test_service_1_architecture_lock_v1.py
tests/smartpyme/test_service_1_product_pipeline_v1.py
docs/current/SERVICE_1_STAGE2_CLOSEOUT_V1.md
docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
```

## 12. Frase rectora

```text
Servicio 1 puede ampliar su plataforma sin ampliar su soberanía.
La autoridad productiva sólo cambia por contrato, integración explícita y evidencia.
```


## 13. Convergence lock — 2026-08-23

Esta sección prevalece sobre cualquier regla anterior incompatible respecto de la convergencia actual de Servicio 1.

### 13.1 Prohibición de decisiones sólo conversacionales

Ninguna decisión de arquitectura se considera aceptada si sólo existe en chat, prompt, `_audit/`, comentario temporal o memoria de sesión. Antes de implementar una decisión normativa deben estar actualizados los documentos rectores correspondientes.

### 13.2 Prohibición de parche arquitectónico

Queda prohibido resolver una incompatibilidad local mediante un nuevo wrapper, fallback, alias, branch o flag si esa pieza no pertenece a la arquitectura final definida.

En particular, un test legacy no justifica introducir runtime legacy.

### 13.3 Prohibición de deuda transitoria indefinida

Toda pieza marcada `transitional`, `legacy compatibility`, `temporary`, `shim` o equivalente debe tener destino explícito:

```text
ABSORB
DELETE
OFFLINE
```

No existe como destino válido `KEEP_TEMPORARILY_WITHOUT_RETIREMENT_GATE`.

### 13.4 ProductExecutionRoot lock

La raíz de ejecución debe converger a un dispatcher/coordinador delgado sobre un `ProductExecutionRequest` discriminado explícitamente:

```text
WorkbookSemanticStartRequest
WorkbookSemanticContinueRequest
WorkbookAnalysisExecuteRequest
SpecializedDomainExecuteRequest
```

No se acepta como diseño final una firma amplia de kwargs combinables ni switches procedurales para seleccionar workflow.

Destino normativo de mecanismos actuales:

```text
analysis_execution_request   → ABSORB en WorkbookAnalysisExecuteRequest
semantic_reception_only      → DELETE como switch top-level
semantic_atomic_confirmation → ABSORB en contrato semántico explícito
semantic_run_override        → DELETE productivo
owner_answers legacy         → DELETE tras migración
use_assisted_semantics       → DELETE como selector top-level
```

La lectura de ResultSets persistidos no entra por este root.

### 13.5 Workbook lock

Para `WORKBOOK`:

```text
CanonicalIngestionOutput
→ D1 → D2 → D3 → D4 → D5 → D6 → D7
→ SEM/owner
→ P7
→ P8
→ F7
→ F8
→ F9
→ F13
```

No se permite:

- inferir workbook por shape;
- completar el envelope en CLI/UI después de su construcción canónica;
- usar filename como identidad del workbook;
- fabricar `sheet1` cuando falta evidencia de sheet;
- construir D7 desde web/UI/CLI;
- saltar D1–D7 para un workbook productivo.

### 13.6 Authority lock

```text
D7     = evidence only
SEM    = semantic interpretation coordinator; provider-neutral
OWNER  = human semantic/relationship evidence
P7     = grain/requirement authority
P8     = computability/use + governed provenance validation
F7     = sole physical join materialization + runtime safety
MATH   = formula_contract + FormulaEngineService + MathPrimitiveOperation + formula catalog
F8     = F12 math coordinator; NOT sole physical caller of MATH
POLICY = declarative boolean classification over kernel-computed values; no arithmetic
F9     = result projection authority
F13    = persistence/load authority; no recalculation
```

Ninguna capa de compatibilidad, UI, CLI, LLM o memoria puede adquirir esas autoridades indirectamente.

### 13.7 Integral-health gate

No se declara Servicio 1 arquitectónicamente sano por acumulación de PASS locales. La certificación integral requiere, sobre el mismo worktree/SHA:

```text
single productive execution root
four explicit execution command contracts
result read separated from execution
single canonical workbook ingestion
single productive XLSX reader
WORKBOOK mandatory D1-D7
D7 evidence-only
single productive semantic state machine
table-scoped evidence built once in D6/D7
P7/P8 authority separation
F7-only join materialization + runtime safety
single common math kernel via FormulaEngineService / formula_contract
no inline business math after migration
declarative classification with no arithmetic
no LLM math/runtime authority
no memory auto-rebind
F13 result read without recalculation
content-addressed source artifact identity
no filename workbook identity
no sheet1 fallback
no productive legacy semantic shim
complete module registry
full suite with 0 FAIL / 0 ERROR
real workbook E2E PASS
```

Hasta entonces, los PASS parciales son evidencia local y no equivalen a certificación del sistema.


## 14. Final architecture lock — dialectical closure 2026-08-23

Esta sección cierra normativamente la deliberación arquitectónica final de Servicio 1.

```text
OPEN_ARCHITECTURAL_DECISIONS = 0
DIALECTICAL_REVIEW_COMPLETE = PASS
TARGET_ARCHITECTURE_CLOSED = YES
```

La implementación sigue separada de este cierre documental: el worktree actual no queda certificado por actualizar estos documentos.

### 14.1 Identity lock

```text
case_id = opaque workflow/case identity; never structural identity
source_artifact_ref = xlsx:sha256:<hash of actual XLSX bytes>
workbook_ref = digest(source_artifact_ref + ingestion_scope + canonical reader/schema version)
sheet_ref = digest(workbook_ref + exact sheet_name)
filename = provenance/display only
sheet_name = physical label only
```

Para `local_path`, el SHA-256 se calcula sobre los bytes reales del archivo mediante lectura streaming. Quedan prohibidos como identidad soberana:

```text
basename
absolute path
mtime + size
filename
sheet1 fabricated fallback
```

### 14.2 Canonical ingestion immutability lock

`CanonicalIngestionOutput V2` es self-contained. CLI, web, UI y adapters no pueden completar o mutar su contenido post-construction.

La reinyección CLI de `normalized_tables` debe desaparecer. Los aliases legacy/transitorios sólo sobreviven hasta que todos sus consumers migren; el gate de retiro es `ZERO_PRODUCTIVE_CONSUMERS`.

### 14.3 Semantic FSM lock

Existe una sola FSM semántica productiva:

```text
SemanticStart(det | bounded LLM)
→ deterministic validation
→ explicit owner dialogue
→ SemanticContinue(owner evidence)
→ shared reinjector/P6
→ CONFIRMED_BINDINGS | follow-up
```

El provider determinístico es un provider de la misma frontera, no una segunda FSM. El pipeline determinístico histórico se retira después de un gate de paridad. El legacy semantic compatibility wrapper se elimina después de migrar callers.

Primera interacción semántica requiere evidencia explícita del dueño; no se autoriza auto-confirmación por confidence.

### 14.4 Table-scoped evidence lock

`table_scoped_semantics` se construye una sola vez como evidencia estructural D6/D7:

```text
D1 → D2 → D3 → D4 → D5
→ D6 table-scoped structural evidence
→ D7 Workbook Logical Model
→ SemanticStart consumes D7.table_scoped_semantics
```

SEM no reconstruye table scope. Deterministic provider y bounded LLM consumen el mismo packet estructural.

### 14.5 Math kernel lock

La única soberanía matemática es el kernel existente:

```text
formula_contract.py
FormulaEngineService
MathPrimitiveOperation
formula_rules_v1 / canonical formula catalog
```

Toda matemática empresarial productiva, incluida la de workflows especializados, debe pasar por ese kernel. No se autorizan nuevas fórmulas o reducciones inline como segunda autoridad.

No se crean:

```text
second math engine
PrimitiveEngine paralelo
PolicyRegistry matemático
```

### 14.6 Classification policy lock

La clasificación empresarial es declarativa y no hace aritmética.

Contrato objetivo mínimo:

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

Cualquier SUM, MAX, ratio, percentage, difference, average u otro valor derivado debe calcularse previamente por MATH. Quedan prohibidos, después de migración, los `if/else` de policy empresarial distribuidos por evaluadores.

### 14.7 Specialized lock

`SpecializedDomainExecuteRequest` sólo se admite si cumple los siete criterios normativos definidos en `SERVICE_1_CANONICAL_AXIS.md`.

Estado target:

```text
expense_variance = specialized legitimate after math/policy convergence
collection_aging = specialized legitimate after math/policy convergence
reconciliation   = specialized legitimate
LIQ_001          = governed workbook capability
REN_001          = governed workbook capability
legacy semantic compat = delete
```

Specialized nunca puede usarse para saltar D1–D7 de un workbook encubierto ni para preservar semántica legacy.

### 14.8 Relationship provenance and join lock

```text
D4 = structural relationship evidence authority
Owner = explicit human confirmation evidence
P8 = computability/use + provenance validation authority
F7 = sole physical join materializer + runtime safety
```

El governed relationship binding debe quedar ligado a:

```text
current source_artifact_ref
current workbook_ref
current schema_fingerprint
current D4 graph_ref / graph_fingerprint
relationship_ref
endpoints
relationship_kind
fanout/cardinality evidence
owner event reference
integrity digest over binding fields
```

`schema_fingerprint` prueba estructura y excluye business values. No puede sustituir artifact/workbook identity.

F7 conserva obligatoriamente safety checks sobre los datos reales de materialización:

```text
duplicate right lookup keys → BLOCK
ONE_TO_ONE duplicate left keys → BLOCK
missing match → BLOCK
join conflict → BLOCK
runtime cardinality violation → BLOCK
```

Estos checks no redescubren relaciones ni deciden computability; validan que la ejecución física no contradiga el binding gobernado.

### 14.9 Result read lock

La lectura de resultados persistidos usa una frontera separada de la ejecución:

```text
Web / CLI
→ Service1ResultQueryV1
→ ResultReadBoundary
→ tenant/case/result/integrity validation
→ F13 load
→ persisted projection/presentation
```

Esta ruta no puede ejecutar o reejecutar:

```text
ProductExecutionRoot
SEM
P7
P8
F7
F8
F9
LLM
XLSX ingestion
calculation
```

### 14.10 Entropy lock

Cada ciclo de reconstrucción debe reducir o mantener en cero:

```text
productive_paths
compatibility_shims
transitional_aliases
procedural root switches
sheet1 fallbacks
legacy productive callers
inline business math
inline business classification
authority collisions
parallel semantic FSMs
post-construction envelope mutations
```

Un PASS funcional que aumente cualquiera de estas deudas sin justificación normativa es `FAIL_ARCHITECTURE`.
