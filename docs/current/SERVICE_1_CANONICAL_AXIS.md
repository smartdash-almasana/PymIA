# Servicio 1 — eje canónico actual

**Estado:** `ACTIVE`  
**Reconciliado:** 2026-08-23

## Propósito

Este documento define una sola orientación para Servicio 1. Sustituye cadenas documentales paralelas, checkpoints superados y cualquier proyección legacy que pretenda gobernar runtime.

Servicio 1 evolucionó después del cierre de Stage 2: el repositorio incorporó fundaciones de dominio, admisión, narrativa, radiografía operacional, harness y operador fiel. Esas capas amplían la plataforma, pero no alteran la autoridad productiva salvo integración explícita y clasificación `PRODUCTIVE`.

## Definición

Servicio 1 es el laboratorio operacional determinístico de PymIA para evidencia PyME, con XLSX como fuente productiva principal actual. El dueño aporta datos y significado operativo; PymIA conserva evidencia, comprende, valida, decide computabilidad, calcula y produce salidas gobernadas.

```text
La capa conversacional conversa y pregunta.
PymIA gobierna estados y evidencia.
Las tools determinísticas calculan.
Los archivos son una forma de producto.
El dueño confirma significado durante la lectura.
```

La confirmación del dueño es evidencia de entrada y reentry. No es autorización autónoma de ejecución, diagnóstico ni delivery.

## Única raíz productiva de ejecución

```text
Web / HTTP / CLI / adapters
→ ProductExecutionRequest explícito
→ pymia/smartpyme/service_1_product_pipeline_v1.py
  (target role: ProductExecutionRoot thin dispatcher)
```

No existe segunda raíz de ejecución autorizada. La lectura de ResultSets usa un `ResultReadBoundary` separado sobre F13 y no constituye una segunda raíz de ejecución.

La presencia de otros flujos locales o de aplicación, incluidos `vertical_slice`, `faithful_operator`, admission, diagnostic core, narrative u operational harness, no crea autoridad productiva paralela.

## Secuencia canónica

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

P0–P10 expresa orden y autoridad, no una obligación de once módulos físicos.

## Separación de decisiones

```text
hipótesis
≠ evidencia
≠ confirmación del dueño
≠ aprobación semántica
≠ match de requisitos
≠ computabilidad
≠ ejecución
≠ delivery
```

En particular:

- una hipótesis de admisión no confirma semántica;
- un `confidence_score` no autoriza matching ni ejecución;
- una respuesta del dueño no elimina P6/P7/P8;
- un cálculo disponible no equivale a diagnóstico final;
- una narrativa no crea evidencia;
- un estado GREEN del harness no autoriza runtime de producto.

## Arquitectura por planos

### Plano A — producto

```text
service_1_product_pipeline_v1
+ módulos PRODUCTIVE
+ P0–P10
```

Es la única autoridad de ejecución del producto.

### Plano B — plataforma y soporte

Incluye componentes integrados que pueden asistir recepción, evidencia, dominio, presentación o medición:

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

Estos componentes no reemplazan la raíz productiva ni los gates P0–P10.

### Plano C — contratos y capacidades con integración acotada

La familia contable general continúa como soporte, pero la revisión asistida de conciliación ya tiene acceso controlado desde la raíz productiva:

```text
service_1_accounting_contracts_v1 = SUPPORT_NECESSARY
service_1_reconciliation_request_gate_v1 = PRODUCTIVE
service_1_reconciliation_candidate_to_assisted_review_v1 = PRODUCTIVE
service_1_reconciliation_product_request_v1 = PRODUCTIVE
service_2_reconciliation_match_candidates_v1 = matcher determinístico reutilizado
```

Esta integración sólo prepara resultados para revisión humana. No autoriza cierre contable, aceptación automática ni modificación de movimientos.

## Ejecución

La raíz canónica distingue requests explícitos, no identidades hardcodeadas:

```text
WorkbookSemanticStartRequest
WorkbookSemanticContinueRequest
WorkbookAnalysisExecuteRequest
SpecializedDomainExecuteRequest
```

LIQ_001 y REN_001 son capacidades gobernadas de workbook, no requests especializados. Su matemática converge al kernel común y su clasificación al contrato declarativo de policy.

Las capacidades de workbook se incorporan por contratos, registry, P7/P8 y kernel; no mediante proliferación de branches identitarios en la raíz. Los workflows realmente especializados sólo entran por `SpecializedDomainExecuteRequest` y deben satisfacer el criterio anti-basurero A16.

## Estado de clasificación Service 1

Fuente física:

```text
docs/service_1_module_disposition.v1.json
```

Estado observado al 2026-07-29:

```text
TOTAL = 60
PRODUCTIVE = 30
SUPPORT_NECESSARY = 30
CANONICAL_PRODUCT_ROOT = service_1_product_pipeline_v1
```

`SUPPORT_NECESSARY` no significa productivo.

## Fundaciones integradas después de Stage 2

```text
039f0cd  domain model foundation
1b62053  deterministic narrative layer
05cf07b  admission pipeline foundation
bc2fabf  pipeline radiography + operational harness
c240080  removal of live-root dependency / legacy evidence bridge
9181abf  faithful operator + document parsing support
48aa4a0  documentary authority reconciliation / Hermes retirement
17e36a2  regression coverage and local tooling retention
```

Estas integraciones forman la nueva envolvente arquitectónica de PymIA alrededor de Servicio 1. Ninguna de ellas, por sí sola, crea una segunda ejecución soberana.

## Conciliación

La conciliación bancaria y Mercado Pago están integradas a Servicio 1 como preparación gobernada para revisión humana.

Principios cerrados:

```text
fecha + importe = evidencia fuerte, no identidad
referencia = evidencia, no verdad absoluta
confidence score = no autoridad
ambigüedad = estado explícito
1:N / N:1 / N:M = no resolver codiciosamente
movimientos no imputados = nunca ocultar por diferencias parciales
caso ambiguo = escalar a humano
```

El matcher existente debe madurar dentro de su módulo actual. No se crea un core paralelo.

## Reglas obligatorias

- Una sola raíz productiva.
- Un solo lector/normalizador XLSX productivo canónico.
- Ninguna respuesta libre desbloquea un rol semántico desconocido.
- `unknown` permanece bloqueado hasta evidencia o elección canónica suficiente.
- La confirmación del dueño no sustituye P6/P7/P8.
- Un componente SUPPORT no ejecuta por existir.
- No LLM como autoridad de cálculo, diagnóstico, estado o computabilidad.
- No event bus, colas ni microservicios distribuidos para resolver fronteras internas actuales.
- No API productiva antes de cerrar las capacidades y contratos correspondientes.
- No documentación histórica, Hermes, Conversa, `PymIA-Live` ni landings como autoridad runtime.

## Documentación rectora relacionada

```text
docs/current/README.md
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/current/SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1.md
docs/service_1_module_disposition.v1.json
docs/service_1_architecture_lock.v1.json
```


## Reconciliación arquitectónica 2026-08-23 — autoridad vigente

Esta sección **sustituye cualquier formulación anterior incompatible** de este documento respecto de la topología y contratos de Servicio 1. Las decisiones A1–A8 son normativas dentro de su alcance; el cierre dialéctico posterior A9–A18 prevalece cuando refina o sustituye esas formulaciones. La presencia física de mecanismos transitorios en el worktree no les concede autoridad.

### Decisiones aceptadas

#### A1 — una sola raíz productiva

```text
PRODUCTIVE_ROOT = pymia/smartpyme/service_1_product_pipeline_v1.py
```

Web, CLI, UI y adapters transportan requests y proyectan respuestas. No coordinan por su cuenta D1–D7, P7/P8, F7/F8/F9 ni crean un segundo root.

#### A2 — request de ejecución explícito y lectura separada

La frontera productiva se divide en **ejecución** y **lectura de resultados persistidos**.

El `ProductExecutionRoot` acepta exclusivamente un `ProductExecutionRequest` discriminado en uno de estos cuatro comandos:

```text
WorkbookSemanticStartRequest
WorkbookSemanticContinueRequest
WorkbookAnalysisExecuteRequest
SpecializedDomainExecuteRequest
```

La lectura/reentrada de ResultSets **no pertenece** al `ProductExecutionRequest` ni al root de ejecución. Usa un `Service1ResultQueryV1` a través de un `ResultReadBoundary` delgado sobre F13.

Ningún request puede inferirse por shape, presencia de `normalized_tables`, `column_refs`, `sheet_name`, filename, capability, combinación de booleanos ni otros indicios implícitos.

#### A3 — único contrato de workbook canónico

Un request `WORKBOOK` entra mediante un único `CanonicalIngestionOutput` con identidad de workbook explícita, tablas normalizadas, column refs, lineage físico, provenance y safety flags fail-closed.

`filename` es provenance/presentación; **no es identidad estructural del workbook**.

Un caller productivo no puede “terminar”, reinyectar o recomponer el envelope después de que el constructor canónico lo produjo.

#### A4 — D1–D7 obligatorios para WORKBOOK

```text
CanonicalIngestionOutput
→ D1 workbook profile
→ D2 region evidence
→ D3 schema identity
→ D4 relationship graph
→ D5 logical-table scope
→ D6 semantic/revalidation evidence
→ D7 Workbook Logical Model
```

Para `WORKBOOK`, D1–D7 son obligatorios. Un workbook incompleto falla cerrado. Un fragmento no se trata como workbook por conveniencia de tests o compatibilidad.

#### A5 — D7 es evidencia, no autoridad

D7 no puede otorgar:

```text
runtime authority
product authority
delivery authority
grain authority
computability authority
join authority
semantic rebind authority
automatic reuse authority
```

D7 organiza evidencia. La autoridad downstream permanece separada.

#### A6 — separación de autoridades downstream

```text
D7        = evidencia integrada; no autoriza ejecución
SEM/owner = significado confirmado y evidencia humana
P7        = requirement match + grain authority
P8        = computability/use authority y validación de provenance gobernada
F7        = única materialización física de joins + safety checks runtime
MATH      = formula_contract + FormulaEngineService + catálogo canónico
F8        = coordinador matemático de analítica F12; no es el único caller físico del kernel
POLICY    = clasificación declarativa sobre valores ya calculados; no hace aritmética
F9        = proyección de ResultSet/findings/outcome
F13       = persistencia de resultados y lectura; no recalcula
```

El LLM nunca calcula, agrega, materializa joins, elige fórmulas soberanamente ni autoriza computabilidad/runtime. Ningún evaluator productivo puede conservar matemática empresarial ad-hoc por fuera del kernel canónico.

#### A7 — no fallbacks sintéticos de identidad

No se autoriza fabricar identidad mediante:

```text
sheet1
filename como workbook identity
shape heuristics
memory auto-rebind
```

La ausencia de evidencia necesaria produce bloqueo explícito.

#### A8 — compatibilidad no es arquitectura permanente

Un shim, alias, flag o wrapper transitorio sólo puede existir durante una migración explícita si tiene:

```text
motivo
callers conocidos
destino final
condición de retiro
gate que pruebe su desaparición productiva
```

No se autoriza acumular `compatibility for now` como estado indefinido.

### Cierre dialéctico de arquitectura — 2026-08-23

La deliberación arquitectónica adversarial quedó cerrada con:

```text
OPEN_ARCHITECTURAL_DECISIONS = 0
TARGET_ARCHITECTURE_CLOSED = YES
READY_TO_DOCUMENT_FINAL_ARCHITECTURE = YES
READY_FOR_IMPLEMENTATION = NO, hasta completar esta incorporación normativa
```

Las decisiones siguientes sustituyen el estado `UNDER_REVIEW` anterior y son **normativas**.

#### A9 — ProductExecutionRoot como dispatcher explícito

`service_1_product_pipeline_v1.py` debe converger a un dispatcher/coordinador delgado sobre cuatro contratos de ejecución mutuamente excluyentes:

```text
WorkbookSemanticStartRequest
WorkbookSemanticContinueRequest
WorkbookAnalysisExecuteRequest
SpecializedDomainExecuteRequest
```

Las dependencies se inyectan separadamente del request. No son diseño final los 20+ kwargs combinables, los modos inferidos por presencia de argumentos ni los switches procedurales.

Destino de mecanismos actuales:

```text
analysis_execution_request      → ABSORB en WorkbookAnalysisExecuteRequest
semantic_reception_only         → DELETE como switch top-level
semantic_atomic_confirmation    → ABSORB en contrato semántico explícito, no como selector de workflow
semantic_run_override           → DELETE de runtime productivo
owner_answers legacy            → DELETE después de migración de callers
use_assisted_semantics          → DELETE como selector top-level
```

#### A10 — una sola FSM semántica productiva

La arquitectura semántica final es provider-neutral:

```text
WorkbookSemanticStartRequest
→ canonical bridge/profile
→ D7.table_scoped_semantics
→ provider: deterministic | bounded LLM
→ deterministic validator
→ owner dialogue

WorkbookSemanticContinueRequest
→ owner responses/evidence
→ shared reinjector/P6
→ CONFIRMED_BINDINGS | follow-up
```

El provider determinístico conserva operación offline y reproducible. El pipeline semántico determinístico histórico no conserva una segunda FSM: se retira después de un gate de paridad que pruebe equivalencia observable de `CONFIRMED_BINDINGS`. `service_1_legacy_semantic_reentry_compat_v1.py` se elimina después de migrar CLI/web callers.

La confirmación explícita de primer contacto sigue siendo obligatoria; no existe auto-confirmación semántica productiva por confianza.

#### A11 — table-scoped semantics se produce una sola vez

`table_scoped_semantics` es evidencia estructural D6/D7. Se construye una sola vez dentro del Workbook Logical Model:

```text
D1 → D2 → D3 → D4 → D5
→ D6 table-scoped structural semantic evidence
→ D7 Workbook Logical Model
→ SemanticStart consume D7.table_scoped_semantics
```

SEM-8 no vuelve a ejecutar `build_service_1_table_scoped_semantic_context_v1`. Tanto el provider determinístico como el LLM consumen el mismo packet provider-neutral.

#### A12 — CanonicalIngestionOutput V2 es self-contained e inmutable para callers

El envelope canónico contiene como autoridad:

```text
schema_version
request_kind / execution context explícito
workbook_context
normalized_tables
column_refs
physical_lineage
provenance
safety_flags
```

CLI, web, UI y adapters no pueden recomponer ni mutar el envelope después de su construcción. La reinyección CLI de `normalized_tables` es deuda y debe eliminarse.

Aliases transitorios se retiran con gate `ZERO_PRODUCTIVE_CONSUMERS`. Ningún alias puede convertirse en contrato permanente por conveniencia de un caller.

#### A13 — identidad física y de ingestion view

La identidad final separa interacción, artefacto, vista ingerida y hoja:

```text
case_id
= identidad opaca del caso/workflow; NO identidad estructural

source_artifact_ref
= xlsx:sha256:<SHA-256 de bytes reales del XLSX>
  tanto para uploaded_bytes como para local_path

workbook_ref
= digest(source_artifact_ref + ingestion_scope + canonical_reader/schema_version)

ingestion_scope
= selección explícita de sheets / all-sheets según contrato

sheet_ref
= digest(workbook_ref + exact sheet_name)

filename
= provenance/display only

sheet_name
= label física, no fallback de identidad
```

Para `local_path` se hashean los bytes del archivo por streaming. Basename, path, mtime y size no sustituyen la identidad content-addressed. Dos archivos distintos con el mismo basename deben producir artefactos distintos.

#### A14 — autoridad matemática única en el kernel existente

La soberanía matemática productiva reside en:

```text
pymia/contracts/formula_contract.py
+ FormulaEngineService
+ MathPrimitiveOperation
+ formula_rules_v1 / catálogo canónico versionado
```

F8 coordina la matemática del flujo analítico F12, pero no es el único caller físico del kernel.

Toda matemática empresarial que afecte un resultado debe ejecutarse mediante primitivas o fórmulas canónicas. Esto incluye reducciones, ratios, porcentajes, diferencias, máximos y demás valores derivados. Parsing/type validation no es math authority.

LIQ_001, REN_001 y cualquier workflow especializado deben converger su matemática inline al kernel común. No se crean `PrimitiveEngine`, `PolicyRegistry` ni segundo motor matemático.

#### A15 — clasificación empresarial declarativa sin aritmética

La policy de clasificación se expresa mediante un contrato declarativo acotado, determinístico y versionable:

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

El clasificador sólo combina predicates booleanos. No ejecuta SUM, MAX, ratios, porcentajes, diferencias ni otras operaciones numéricas; esos valores deben llegar previamente calculados por el kernel matemático.

No se autorizan `if/else` de clasificación empresarial permanentes distribuidos por evaluadores una vez migrados al contrato común. No se crea un DSL general de expresiones.

#### A16 — SPECIALIZED_REQUEST tiene criterio cerrado anti-basurero

Un `SpecializedDomainExecuteRequest` sólo es legítimo si cumple simultáneamente:

```text
1. input no representable sin pérdida como workbook analysis;
2. workflow/output materialmente distinto;
3. subtype explícito y cerrado;
4. no bypass D1–D7 para un workbook encubierto;
5. no semántica legacy;
6. matemática bajo kernel común y policy bajo contrato canónico;
7. gate/test que impida usar SPECIALIZED como escape hatch.
```

Aplicación normativa actual:

```text
expense_variance   = SPECIALIZED candidato legítimo, sujeto a convergencia math/policy
collection_aging   = SPECIALIZED candidato legítimo, sujeto a convergencia math/policy
reconciliation     = SPECIALIZED candidato legítimo
LIQ_001            = NO SPECIALIZED; governed workbook capability
REN_001            = NO SPECIALIZED; governed workbook capability
legacy semantic compat = NO SPECIALIZED; DELETE
```

#### A17 — D4 → P8 → F7 con provenance completa y safety runtime

La relación gobernada sigue esta separación:

```text
D4
= autoridad de evidencia estructural de relaciones
→ graph_ref / graph_fingerprint
→ relationship_ref
→ endpoints / kind
→ fanout/cardinality structural evidence
→ schema_fingerprint
→ workbook/source provenance

Owner
= confirma relationship_ref ligado a graph_ref + identidad de caso/owner

P8
= autoridad de computability/use
→ valida current workbook_ref/source_artifact_ref
→ valida D4 graph_ref/fingerprint
→ valida schema_fingerprint
→ valida owner evidence
→ valida fanout/computability
→ emite immutable governed_relationship_binding

F7
= única materialización física del join
→ verifica binding e identidad de ingestion
→ verifica endpoints/kind
→ mantiene safety checks sobre filas reales
→ materializa o bloquea
```

`schema_fingerprint` es identidad estructural y **no** demuestra igualdad de business values. Por eso el binding debe quedar ligado a `workbook_ref/source_artifact_ref`.

Los checks runtime de F7 sobre duplicate lookup keys, duplicate left keys en `ONE_TO_ONE`, missing matches, join conflicts y cardinality violations son invariantes de seguridad de materialización. No convierten F7 en segunda autoridad D4 ni en autoridad de computability.

#### A18 — ResultReadBoundary separado del execution root

La lectura de resultados persistidos sigue:

```text
Web / CLI
→ Service1ResultQueryV1
→ ResultReadBoundary
→ tenant + case + result + integrity validation
→ F13 load
→ persisted presentation
```

Esta ruta no ejecuta ProductExecutionRoot, SEM, P7, P8, F7, F8 ni F9 nuevamente. No reabre XLSX, no llama LLM y no recalcula.

`RESULTSET_REENTRY` deja de ser request de ejecución. La existencia de una superficie de lectura separada no crea una segunda raíz de ejecución.

### Regla de convergencia final

La reconstrucción debe disminuir, nunca aumentar, estas métricas:

```text
productive_paths
compatibility_shims
transitional_aliases
root_modes_or_procedural_switches
authority_collisions
sheet1_fallbacks
legacy_productive_callers
unregistered_modules
inline_business_math
inline_business_classification
```

Un cambio que haga pasar tests pero aumente entropía arquitectónica es `FAIL_ARCHITECTURE`.

Los tests se alinean al contrato definitivo; no se crean contratos runtime para sostener fixtures legacy.
