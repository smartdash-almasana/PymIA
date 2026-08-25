# Servicio 1 — Dossier Dialéctico para Arquitectura Final V1

**Estado:** `CLOSED_DIALECTIC / EVIDENCE_ONLY / NON_NORMATIVE`
**Fecha:** 2026-08-23
**Baseline:** `8d5708e9becdddaa5aa24387b310972643d1ef86` + worktree local no committeado
**Propósito:** preservar la evidencia de la deliberación adversarial que llevó al cierre de la arquitectura final.

```text
OPEN_ARCHITECTURAL_DECISIONS = 0
DIALECTICAL_REVIEW_COMPLETE = PASS
TARGET_ARCHITECTURE_CLOSED = YES
```

> Este documento NO gobierna implementación. La síntesis final ya fue incorporada a `SERVICE_1_CANONICAL_AXIS.md` y `SERVICE_1_ARCHITECTURE_LOCK.md`; esos documentos son la autoridad normativa. El contenido previo de este dossier permanece como trazabilidad del razonamiento y de las refutaciones.

## 1. Método

Cada asunto se cierra mediante:

```text
EVIDENCIA FÍSICA
→ TESIS PROVISIONAL
→ ANTÍTESIS / REFUTACIÓN QWEN
→ CONTRARRÉPLICA
→ SÍNTESIS
→ DECISIÓN DOCUMENTADA
```

Estados posibles por asunto:

```text
OPEN
THESIS_SUPPORTED
THESIS_REFUTED
SYNTHESIS_REQUIRED
CLOSED_DOCUMENTED
```

No se implementa mientras el asunto no esté `CLOSED_DOCUMENTED`.

---

# DA-01 — Autoridad matemática

## Evidencia de conflicto

- `SERVICE_1_ARCHITECTURE_LOCK.md` conserva históricamente LIQ_001 y REN_001 como evaluadores especializados.
- La sección de convergencia declara `F8 = math authority`.
- F8 usa `FormulaEngineService`.
- LIQ_001 y REN_001 hacen parsing/agregación y delegan fórmulas a la familia del formula engine.
- Consorcios `expense_variance` y `collection_aging` realizan matemática de negocio propia fuera de F8/FormulaEngineService.

## Tesis provisional T-MATH-01

Servicio 1 debe tener **una sola autoridad canónica de evaluación de fórmulas de negocio**, definida por el `FormulaEngineService` + catálogo/contrato canónico de fórmulas, no por la mera presencia física del módulo F8.

Distinciones normativas propuestas:

```text
numeric parsing / type validation        ≠ math authority
evidence normalization                   ≠ math authority
bounded evidence aggregation             ≠ necesariamente math sovereignty
business formula evaluation              = canonical math authority required
business threshold/classification policy = policy authority separable de math
```

F8 debe ser la ruta canónica de ejecución matemática para la analítica gobernada general. Un evaluador especializado puede preparar evidencia, adaptar un contrato o clasificar outcomes, pero **no debe mantener una segunda implementación soberana de fórmulas de negocio**. Si calcula una fórmula empresarial, debe delegarla al motor/catálogo canónico.

Consecuencia provisional: LIQ_001/REN_001 pueden sobrevivir como adapters/evaluators especializados si delegan toda fórmula soberana. Los evaluadores Consorcios con fórmulas propias requieren convergencia o justificación normativa explícita.

## Pregunta adversarial

¿Esta definición realmente elimina autoridad matemática duplicada o sólo cambia el nombre de la duplicación? ¿La agregación de filas constituye ya una fórmula de negocio en ciertos casos? ¿Debe F8 ser el módulo único o basta con un único kernel/FormulaEngineService compartido?

**Estado:** `OPEN`

---

# DA-02 — Arquitectura semántica productiva

## Evidencia de conflicto

Hoy conviven:

- SEM-8 / assisted semantic flow;
- deterministic semantic pipeline;
- `semantic_run_override`;
- `service_1_legacy_semantic_reentry_compat_v1` con callers productivos CLI/web;
- owner semantic evidence reentry;
- provider LLM y provider determinístico.

## Tesis provisional T-SEM-01

Servicio 1 debe tener **una sola máquina de estados semántica productiva**.

La ruta final propuesta conceptualmente es:

```text
canonical workbook evidence
→ semantic proposal provider
   ├─ LLM acotado
   └─ deterministic safe provider
→ deterministic semantic validation
→ owner confirmation/correction
→ canonical owner semantic evidence
→ governed semantic reentry
```

LLM y provider determinístico son **proveedores de propuestas**, no máquinas productivas paralelas. El validator y owner evidence gobiernan la transición de estado. `semantic_run_override`, el shim legacy y cualquier segunda orquestación semántica productiva deben desaparecer/ser absorbidos.

El LLM jamás calcula ni autoriza runtime/computability. El provider determinístico puede existir como fallback seguro sin constituir una segunda arquitectura.

## Pregunta adversarial

¿SEM-8 realmente puede absorber todas las responsabilidades legítimas del deterministic semantic pipeline sin degradar fail-closed, tests o funcionamiento offline? ¿Qué funciones del pipeline determinístico son provider-level y cuáles son state-machine-level?

**Estado:** `OPEN`

---

# DA-03 — ProductRequest y Product Root

## Evidencia de conflicto

El Product Root actual expone una firma amplia con inputs de dominio, dependencies, requests especializados, legacy inputs y switches procedurales, incluyendo `semantic_reception_only`, `semantic_atomic_confirmation`, `analysis_execution_request`, `semantic_run_override` y otros.

## Tesis provisional T-ROOT-01

La frontera productiva debe converger a un **ProductRequest discriminado explícitamente**, evitando combinaciones procedurales de kwargs.

Conceptualmente:

```text
ProductRequest
├── WorkbookRequest
├── SpecializedRequest
└── ResultSetReentryRequest
```

`run_service_1_product_pipeline_v1` debe recibir un request explícito y dependencies/context claramente separados. Los estados internos del workflow deben expresarse como estados/contratos, no mediante combinaciones de boolean flags.

`ResultSetReentryRequest` puede entrar por la misma frontera productiva, pero debe delegar a F13 read-only y no atravesar el pipeline de cálculo.

## Pregunta adversarial

¿Un discriminated union reduce realmente complejidad o sólo empaqueta los mismos 26 parámetros? ¿Qué parámetros son legítimas dependencies y deben permanecer externos? ¿Debe ResultSet reentry compartir la misma root function o una frontera de lectura separada violaría `ONE_PRODUCTIVE_ROOT`?

**Estado:** `OPEN`

---

# DA-04 — CanonicalIngestionOutput y aliases

## Evidencia de conflicto

Existe `CanonicalIngestionOutput V2`, pero conserva aliases top-level transitorios y el CLI recompone `normalized_tables` después de su construcción.

## Tesis provisional T-ING-01

Debe existir **un único CanonicalIngestionOutput inmutable por contrato después de su construcción**, con sólo campos canónicos:

```text
schema_version
request_kind
workbook_context
normalized_tables
column_refs
physical_lineage
provenance
safety_flags
```

Los aliases top-level no pertenecen al contrato final. Todos los consumers deben migrar a los campos canónicos y los aliases retirarse con un gate físico de cero consumers productivos.

Ningún CLI/UI/adapter puede completar, reinyectar o recomponer el envelope después de su constructor.

## Pregunta adversarial

¿Algún alias transporta semántica que todavía no está representada en los campos V2? ¿La lista propuesta de campos es suficiente para todas las rutas productivas o eliminar aliases ahora revelaría un contrato incompleto?

**Estado:** `OPEN`

---

# DA-05 — Identidad de workbook y sheet

## Evidencia de conflicto

- `filename` fue usado históricamente como referencia contextual.
- `sheet1` sigue apareciendo como fallback en rutas semánticas.
- `workbook_ref` y `source_file_ref` aparecen asociados/aliased en la transición V2.

## Tesis provisional T-ID-01

La identidad debe ser explícita y separada de etiquetas humanas:

```text
workbook_ref  = identidad inmutable del workbook ingerido
sheet_ref     = identidad inmutable de una hoja dentro de ese workbook
filename      = provenance/display only
sheet_name    = label físico/display; no identidad soberana
source_file_ref = referencia al artefacto fuente; conceptualmente distinta de workbook_ref
```

`workbook_ref` no deriva de filename. `sheet_ref` debe provenir de la ingesta/profiling real y jamás fabricarse como `sheet1`. `source_file_ref` y `workbook_ref` pueden coincidir físicamente en un caso simple, pero el contrato no debe tratarlos como el mismo concepto salvo decisión explícita.

## Pregunta adversarial

¿Necesitamos realmente separar `source_file_ref` y `workbook_ref`, o eso agrega identidad artificial? ¿Cuál es la definición mínima y estable de `sheet_ref` frente a renombrados/reordenamientos de hojas? ¿Debe ser content-addressed, ordinal, o derivado de workbook identity + evidencia física?

**Estado:** `OPEN`

---

# DA-06 — Provenance D4 → F7

## Evidencia de conflicto

F7 materializa joins y valida bindings básicos, pero no se ha probado enforcement completo de `d4_graph_ref`, schema fingerprint, relationship status, fanout certificate ni read-only dereference contra el grafo D4 autoritativo.

## Tesis provisional T-REL-01

La relación utilizable para cálculo debe preservar una cadena verificable:

```text
D3 schema identity
→ D4 relationship graph
→ resolved relationship_ref
→ D7 evidence projection
→ owner relationship confirmation event
→ P8 use authorization
→ GovernedAnalysisInput
→ F7 read-only dereference against exact D4 graph
→ provenance/fanout validation
→ join materialization
```

D4 define evidencia estructural; owner confirma significado/uso humano; P8 autoriza computabilidad; F7 es el único materializador físico. No existe un segundo relationship registry.

F7 no acepta un binding autocontenido como verdad suficiente: debe poder demostrar que corresponde al grafo D4 exacto del schema/workbook gobernado.

## Pregunta adversarial

¿Cuál es el mínimo conjunto de identifiers/certificates necesario para evitar duplicar todo D4 dentro de `GovernedAnalysisInput`? ¿Qué valida P8 y qué debe validar F7 para no duplicar autoridad?

**Estado:** `OPEN`

---

# DA-07 — Alcance de SPECIALIZED_REQUEST

## Evidencia de conflicto

`SPECIALIZED_REQUEST` se usa para consorcios/reconciliation y también fue aplicado en compatibilidad semántica legacy durante la migración.

## Tesis provisional T-SPEC-01

`SPECIALIZED_REQUEST` sólo es legítimo para capacidades cuyo **input contract y workflow son realmente distintos del flujo WORKBOOK canónico** y no pueden representarse sin pérdida como un análisis gobernado sobre workbook.

No puede funcionar como contenedor residual para:

```text
legacy semantics
tests antiguos
workbook fragments incompletos
bypass de D1-D7
compatibility shims
```

Cada subtype especializado debe tener payload explícito, autoridad y gates propios, y no adquirir matemática/semántica paralela por conveniencia.

## Pregunta adversarial

¿Consorcios y reconciliation son realmente requests especializados o deberían converger también a WORKBOOK + analysis request? ¿Qué criterio objetivo separa un specialized request legítimo de un bypass histórico?

**Estado:** `OPEN`

---

# DA-08 — RESULTSET_REENTRY

## Evidencia de conflicto

F13 ya tiene una ruta de reentry persistido sin XLSX/LLM/recalculation, mientras el Product Root actualmente reconoce el kind pero falla cerrado y la web puede reabrir resultados directamente.

## Tesis provisional T-REENTRY-01

`RESULTSET_REENTRY` es una operación productiva **read-only sobre un ResultSet persistido**, no una nueva ejecución analítica.

Contrato final propuesto:

```text
ResultSetReentryRequest
→ tenant/case/result identity validation
→ integrity digest validation
→ exact F13 load
→ presentation projection
```

Prohibido:

```text
XLSX reload
semantic reentry
P7/P8 recomputation
F7 join
F8 math
F9 recalculation
LLM call
memory rebind
```

Puede compartir la frontera `ProductRequest`, pero debe evitar completamente el pipeline computacional.

## Pregunta adversarial

¿Hacer pasar reentry por `run_service_1_product_pipeline_v1` aunque sólo despache a F13 mejora la unicidad de root o mezcla command/query innecesariamente? ¿Debe `ONE_PRODUCTIVE_ROOT` aplicarse también a read-only result retrieval?

**Estado:** `OPEN`

---

# 2. Condición de cierre

Este dossier sólo puede convertirse en arquitectura final cuando, para cada DA-01…DA-08, exista:

```text
THESIS
ANTITHESIS
EVIDENCE_DECIDING
SYNTHESIS
FINAL_DECISION
CONSEQUENCES
RETIREMENTS
GATES
```

Cierre global requerido:

```text
OPEN_ARCHITECTURAL_DECISIONS = 0
DIALECTICAL_ARCHITECTURE_REVIEW_COMPLETE = PASS
```

Hasta entonces:

```text
TARGET_ARCHITECTURE = OPEN
RECONSTRUCTION = FROZEN
```


---

# Ronda dialéctica 1 — Antítesis Qwen y contrarréplica ChatGPT

**Estado:** `COUNTERREPLY_RECORDED / NON_NORMATIVE`

La Ronda 1 de Qwen fue adversarial y útil, pero no cierra ninguna decisión. Varias antítesis se sostienen; otras contienen inferencias o afirmaciones físicas que deben corregirse antes de sintetizar.

## DA-01 — Contrarréplica a Qwen

### Punto concedido

Qwen demuestra correctamente que no puede definirse `math authority` por mera presencia de `Decimal` ni por nombre de módulo. También demuestra que LIQ_001/REN_001 realizan agregación de filas y que Consorcios ejecuta aritmética de negocio propia.

### Punto no concedido

La alternativa Qwen —"Formula primitives authority + agregación dentro de cada evaluator + clasificación dentro de cada evaluator"— conserva múltiples implementaciones productivas de primitivas de negocio. Eso puede ser una taxonomía descriptiva del AS-IS, pero todavía no demuestra ser arquitectura final sana.

### Síntesis candidata S-MATH-01

Distinguir cuatro responsabilidades:

```text
A. numeric parsing/type validation          = no soberanía matemática
B. governed evidence reduction             = primitivas determinísticas declaradas
C. business formula evaluation              = kernel matemático canónico
D. outcome/policy classification            = autoridad de policy separada
```

La pregunta a cerrar no es "¿todo pasa físicamente por F8?" sino:

> ¿Puede existir alguna aritmética que afecte un resultado empresarial productivo fuera de primitivas/kernel/policies canónicamente declarados?

Tesis de síntesis provisional: `F8` puede ser coordinador de analítica, no necesariamente módulo físico único; pero ninguna rama especializada debería conservar fórmulas o reducciones empresariales ad-hoc no gobernadas por el cerebro matemático común.

**Estado:** `SYNTHESIS_REQUIRED`

## DA-02 — Contrarréplica a Qwen

### Error factual relevante en la antítesis

Qwen afirma que una única FSM semántica implicaría perder el modo offline/no-LLM. El código actual demuestra que esa conclusión no es necesaria:

- `service_1_llm_semantic_interpreter_v1.py` es provider-neutral; no realiza I/O de red por sí mismo y recibe un callable inyectado.
- `service_1_deterministic_semantic_proposal_provider_v1.py` implementa exactamente un provider determinístico que produce el contrato cerrado de proposal sin I/O/LLM.
- `service_1_assisted_web_v1.py` usa ese provider determinístico por defecto cuando no se inyecta otro provider.
- SEM-8 posee además `run_service_1_assisted_semantic_reentry_v1`, que aplica respuestas del owner sin volver a llamar al LLM.

Por tanto:

```text
ONE SEMANTIC FSM
≠
LLM obligatorio
```

La capacidad offline puede preservarse mediante provider determinístico dentro de una única máquina de estados.

### Punto concedido

El viejo deterministic semantic pipeline contiene una FSM completa y no puede eliminarse por decreto. Debe demostrarse paridad funcional antes de retirarlo.

### Síntesis candidata S-SEM-01

Una única FSM semántica canónica, provider-neutral:

```text
canonical evidence
→ provider interface
   ├─ deterministic provider (offline)
   └─ bounded LLM provider
→ deterministic validator
→ owner dialogue/evidence
→ semantic reentry
→ CONFIRMED_BINDINGS
```

El deterministic pipeline histórico sólo puede sobrevivir como ruta productiva separada si Qwen demuestra una responsabilidad state-machine-level que la FSM canónica no puede representar sin degradación. El mero requisito offline no alcanza, porque ya existe provider offline.

**Estado:** `SYNTHESIS_REQUIRED` — la refutación Qwen de DA-02 no se acepta como cierre.

## DA-03 — Contrarréplica a Qwen

### Error factual relevante

Qwen afirma que `analysis_execution_request` salta P7/P8. Físicamente `run_service_1_governed_analysis_v1` vuelve a ejecutar dynamic discovery/computability y exige `governed_analysis_input` antes de F7/F8/F9. Por tanto:

```text
analysis_execution_request bypasses SEM stage: YES, porque recibe CONFIRMED_BINDINGS
analysis_execution_request bypasses P7/P8: NO
```

Eso cambia la clasificación: puede ser un comando de continuación de workflow después de owner semantics, no necesariamente un bypass de gobernanza.

### Punto concedido

Qwen tiene razón en que empaquetar 26 kwargs en una dataclass no resuelve por sí mismo la entropía, y en que `RESULTSET_REENTRY` no debe forzarse dentro del execution root sólo para sostener una consigna de “one root”.

### Síntesis candidata S-ROOT-01

Separar **execution commands** de **dependencies**, y expresar estados externos del workflow mediante contratos explícitos, no flags. Posibles commands conceptuales:

```text
WorkbookSemanticStart
WorkbookSemanticContinue
WorkbookAnalysisExecute
SpecializedDomainExecute
```

`ResultSetReentry` queda fuera del execution Product Root y se trata como query/read boundary (sujeto a DA-08).

La decisión pendiente es cuántos commands son realmente necesarios y si `analysis_execution_request` debe transformarse en un contrato explícito de continuación en vez de desaparecer.

**Estado:** `SYNTHESIS_REQUIRED`

## DA-04 — Contrarréplica a Qwen

### Error factual importante

Qwen afirma que el constructor de `CanonicalIngestionOutput V2` no incluye `normalized_tables` y que por eso el CLI debe reinyectarlas. El código actual contradice esa afirmación:

`_canonical_ingestion_envelope(...)` incluye explícitamente:

```text
normalized_tables
column_refs
physical_lineage
provenance
safety_flags
```

Por tanto la mutación CLI de `normalized_tables` no prueba que V2 carezca de ese dato. Es, al menos provisionalmente, una recomposición redundante/contract violation cuya necesidad debe demostrarse comparando ambos valores.

También `source_kind`, `filename` y `sheet_names` ya están representados en `provenance`; no son evidencia suficiente de que los aliases deban sobrevivir.

### Punto concedido

No todos los aliases pueden borrarse mecánicamente. Debe trazarse consumer por consumer y DA-05 debe cerrar semántica de sheet identity antes de retirar `sheet_name`.

### Síntesis candidata S-ING-01

Mantener un único envelope V2 self-contained e inmutable. Para cada alias se exige:

```text
canonical replacement
productive consumers
migration target
zero-consumer retirement gate
```

No se presume que V2 está completo ni incompleto: se prueba campo por campo. La reinyeción CLI debe justificarse por desigualdad física; si los valores son equivalentes, es deuda a retirar.

**Estado:** `SYNTHESIS_REQUIRED`

## DA-05 — Contrarréplica a Qwen

### Corrección de evidencia

Qwen describe `workbook_ref` como derivado de un `case_id` puramente administrativo. El `case_id` actual es un SHA-256 truncado sobre:

```text
source_kind
filename
sheet selection
uploaded content (cuando está disponible)
```

Por tanto no es simplemente una identidad administrativa. A la vez, tampoco es un puro content hash porque incorpora filename y selección. `workbook_ref` deriva de ese `case_id`.

Esto demuestra que la identidad actual mezcla conceptos y que la decisión sigue abierta.

Además, `sheet_ref` ya existe ampliamente en contratos downstream, pero muchas veces semánticamente equivale al `sheet_name`; el problema no es inexistencia del término sino ausencia de una definición canónica estable en ingestion.

### Síntesis candidata S-ID-01

Definir sólo identidades que puedan demostrarse físicamente:

```text
workbook_ref       = identidad de la instancia canónica de workbook ingerida
source_artifact_ref= referencia estable al artefacto físico, sólo si existe
sheet_ref          = identidad canónica de sheet dentro de esa instancia
filename           = provenance/display
sheet_name         = label físico
```

No se decide todavía que `source_artifact_ref` deba ser content-addressed ni que `sheet_ref` sea ordinal/hash/name-derived. Qwen debe comparar alternativas respecto de renombrado, reupload, multisheet y provenance antes de cerrar.

**Estado:** `SYNTHESIS_REQUIRED`

## DA-06 — Contrarréplica a Qwen

### Error factual crítico en la alternativa Qwen

Qwen propone que P8 valide `d4_graph_ref` contra el grafo actual y que F7 confíe en P8, pero el P8 físico actual NO hace esa validación. `service_1_computability_v1.py` sólo valida actualmente binding ref, declaración/requerimiento, forbidden authority flags y `confirmed_by_owner`, y copia el binding a `GovernedAnalysisInput`.

Por tanto la frase “P8 ya valida computabilidad contra el grafo actual” no está demostrada.

### Punto concedido

Qwen sí identifica un riesgo real: obligar a F7 a reconstruir/revalidar todo D4 puede duplicar autoridad y acoplar demasiado execution con structural discovery.

### Síntesis candidata S-REL-01

Mover la validación soberana de provenance a la frontera P8 y hacer que F7 verifique un **governed relationship certificate** mínimo, sin recomputar D4:

```text
D4 -> relationship evidence + graph identity/digest
owner -> confirmation event bound to relationship_ref + graph identity
P8 -> verifies D4/current schema/owner/fanout and emits governed relationship binding
F7 -> verifies certificate identity/integrity + endpoints/kind, then materializes join only
```

F7 no vuelve a decidir si la relación existe o es computable. Sólo rechaza un certificado inconsistente/stale y materializa el join autorizado.

**Estado:** `SYNTHESIS_REQUIRED`

## DA-07 — Contrarréplica a Qwen

Qwen aporta un criterio útil pero todavía insuficiente: “input distinto a workbook” puede legitimar demasiado fácilmente excepciones históricas.

### Síntesis candidata S-SPEC-01

`SPECIALIZED_REQUEST` sólo puede existir si se prueban simultáneamente:

```text
1. input contract no representable sin pérdida como CanonicalIngestionOutput + governed analysis request;
2. workflow/output materialmente distinto del análisis workbook;
3. subtype explícito y cerrado;
4. no bypass de D1-D7 para un workbook encubierto;
5. no semántica legacy;
6. math/policy bajo las autoridades canónicas definidas en DA-01;
7. tests de anti-basurero.
```

Consorcios y reconciliation quedan `CANDIDATE_SPECIALIZED`, no aceptados automáticamente. Legacy semantic compat queda excluido.

**Estado:** `SYNTHESIS_REQUIRED`

## DA-08 — Contrarréplica a Qwen

La antítesis de Qwen es fuerte y consistente con el estado físico actual: Product Root ya fail-closes `RESULTSET_REENTRY`, mientras F13 tiene load/integrity/reentry propio.

### Síntesis candidata S-REENTRY-01

Reformular el invariant:

```text
ONE_PRODUCTIVE_EXECUTION_ROOT
```

no

```text
ONE_FUNCTION_FOR_EXECUTION_AND_READS
```

La reentrada de ResultSet es una query/read boundary delgada sobre F13 con cero autoridad analítica y cero recalculation. No pertenece al ProductRequest de ejecución.

Esta síntesis todavía debe ser atacada respecto de identidad, tenant isolation, F9 presentation projection y riesgo de crear otra “segunda root” semánticamente ambigua.

**Estado:** `SYNTHESIS_REQUIRED`

## Dependencias de síntesis después de Ronda 1

```text
DA-05 identity
   -> DA-04 ingestion aliases
   -> DA-06 relationship provenance

DA-02 semantic state machine
   -> DA-03 execution commands/root

DA-01 math authority
   -> DA-07 specialized legitimacy

DA-03 execution root
   -> DA-08 read-boundary invariant wording
```

## Errores/fisuras de la Ronda 1 que deben ser atacados nuevamente

```text
Q1: una FSM única implica LLM/red                = físicamente refutado
Q2: analysis_execution_request salta P7/P8       = físicamente refutado
Q3: CanonicalIngestionOutput V2 carece normalized_tables = físicamente refutado
Q4: P8 ya valida D4 graph provenance             = físicamente refutado
Q5: case_id/workbook_ref es sólo administrativo  = descripción incompleta
```

Ninguna síntesis anterior es normativa todavía.

```text
OPEN_ARCHITECTURAL_DECISIONS = 8
TARGET_ARCHITECTURE = OPEN
RECONSTRUCTION = FROZEN
```


---

# Ronda dialéctica 2 — Red-team Qwen y contrarréplica ChatGPT

## Estado de la ronda

La Ronda 2 de Qwen corrigió expresamente cinco errores de su Ronda 1 y dejó seis decisiones abiertas. La revisión física posterior reduce y redefine esos bloqueos. Ninguna conclusión de esta sección es todavía autoridad normativa.

## CR-2.1 — DA-01: no crear `PrimitiveEngine` ni `PolicyRegistry` sin necesidad

Qwen dejó abierta la ubicación física de agregaciones y policy y propuso como posibilidad `PrimitiveEngine` / `PolicyRegistry`.

Cross-check físico:

- `service_1_generic_capability_engine_v1.py` instancia `FormulaEngineService`.
- El mismo engine usa `MathPrimitiveInput` + `MathPrimitiveOperation.SUM/SINGLE_VALUE` mediante `calculate_math_primitive` para reducción de evidencia.
- El contrato `CapabilityDefinitionV1` ya contiene `AggregationMode`, `ClassificationRuleV1` y `OutcomePolicyV1`.
- El generic capability engine ejecuta fórmula mediante `calculate_formula` y clasificación declarada mediante las reglas del capability contract.

Conclusión provisional:

```text
NO_NEW_PRIMITIVE_ENGINE_REQUIRED
NO_NEW_POLICY_REGISTRY_REQUIRED
```

Síntesis candidata revisada `S-MATH-02`:

```text
UN SOLO CEREBRO MATEMÁTICO
=
formula_contract + FormulaEngineService

Responsabilidades:
A. parse/type validation: fuera de soberanía matemática;
B. reductions SUM/SINGLE_VALUE/etc: MathPrimitiveOperation del kernel común;
C. business formulas: calculate_formula / FormulaEngineService;
D. classification thresholds/outcome policy: definición declarativa de capability/domain policy, no aritmética inline soberana.
```

F8 no necesita ser el único módulo caller; debe ser coordinador del flujo analítico F12. Cualquier evaluador especializado que sobreviva debe consumir las mismas primitivas/fórmulas declaradas y no implementar aritmética empresarial paralela.

Implicación:

- LIQ_001/REN_001: conservar sólo si convergen completamente al kernel existente para reductions/formulas y policy declarativa.
- Consorcios: no se justifica crear una excepción matemática permanente sólo por ser specialized; sus operaciones deben delegarse al mismo kernel común o quedar demostradas como no-formula domain transformation.

Esto transforma DO-01 desde una decisión de "crear motor" a una decisión de **migración hacia autoridad ya existente**.

Estado provisional DA-01: `DIALECTICAL_CANDIDATE_PENDING_QWEN_R3`.

## CR-2.2 — DA-02: la paridad semántica está más avanzada que lo descrito

Qwen mantuvo DO-05 por falta de prueba exacta del owner loop.

Cross-check físico adicional:

- `run_service_1_assisted_semantic_reentry_v1` soporta follow-up multi-turn, targeted correction, skip y respuestas agrupadas.
- Una vez consolidada la evidencia owner, SEM-8 llama `build_service_1_owner_semantic_evidence_reentry_v1`.
- `service_1_owner_semantic_evidence_reentry_v1` declara explícitamente `SEM-5 owner evidence -> existing semantic reinjection/P6`.
- Este adapter llama al mismo `build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1` usado por la ruta determinística histórica.
- El packet resultante conserva `p6_decisions`, `requirement_matches`, `confirmed_candidate` y confirmed relationships.
- SEM-8 construye luego un `semantic_run` compatible con `STATUS_CONFIRMED_BINDINGS`.
- El provider determinístico real ya existe y es compatible con la frontera provider-neutral de SEM-8.

Por tanto, el post-owner authority path no necesita dos FSM soberanas: SEM-8 ya converge materialmente al mismo reinjector/P6.

Queda por demostrar mediante tests de paridad, no mediante otra decisión conceptual, que los estados observables necesarios del owner loop histórico quedan cubiertos.

Síntesis candidata revisada `S-SEM-02`:

```text
ONE_PRODUCTIVE_SEMANTIC_FSM

SemanticStart(provider = deterministic | bounded_llm)
→ validator
→ owner dialogue
→ SemanticContinue(owner evidence)
→ existing canonical reinjection/P6
→ CONFIRMED_BINDINGS
```

El deterministic semantic pipeline histórico pasa a `RETIRE_AFTER_PARITY_GATE`, no a segunda FSM final.

El legacy compat wrapper pasa a `DELETE_AFTER_CALLER_MIGRATION`.

Estado provisional DA-02: `DIALECTICAL_CANDIDATE_PENDING_QWEN_R3`.

## CR-2.3 — DA-03: no minimizar artificialmente el número de commands

Qwen propone tres commands pero su propia cadena requiere semantic start y semantic continue como transiciones externas distintas.

No debe optimizarse por cantidad de nombres sino por ausencia de combinaciones implícitas.

Síntesis candidata revisada `S-ROOT-02`:

```text
ProductExecutionRequest = discriminated union of:

1. WorkbookSemanticStartRequest
2. WorkbookSemanticContinueRequest
3. WorkbookAnalysisExecuteRequest
4. SpecializedDomainExecuteRequest
```

`ResultSetReentry` NO pertenece a esta unión.

Product Root = thin execution dispatcher/coordinator, no giant function.

Dependencies (providers, stores, persistence adapters) no son campos de dominio del request.

Los requests deben ser mutuamente exclusivos por tipo, no por chequeos combinatorios sobre 20+ kwargs.

`analysis_execution_request` demuestra físicamente que AnalysisExecute es una continuación válida siempre que exija canonical ingestion + CONFIRMED_BINDINGS y re-ejecute discovery/P7/P8.

`semantic_reception_only` y `semantic_atomic_confirmation` no sobreviven como booleans top-level del root; cualquier diferencia legítima debe pertenecer al contrato de la transición semántica o desaparecer.

Estado provisional DA-03: `DIALECTICAL_CANDIDATE_PENDING_QWEN_R3`.

## CR-2.4 — DA-04: DO-03 queda físicamente resuelto

Qwen pidió probar si `normalized_tables` del connector y el que CLI reinyecta podían divergir.

Cross-check:

- Boundary produce `normalized_tables`.
- `_normalized_tables(packet)` en el constructor canónico devuelve directamente `packet["normalized_tables"]` filtrando sólo elementos no-dict; para el boundary válido, son los mismos dicts.
- `_canonical_ingestion_envelope(... normalized_tables=normalized_tables ...)` coloca esa lista en `ingestion_output["normalized_tables"]`.
- CLI toma `boundary.get("normalized_tables")` y vuelve a asignarlo sobre `connector["ingestion_output"]["normalized_tables"]`.

No existe transformación intermedia que justifique esa reinyección en el path válido actual.

Por tanto:

```text
DO-03 = RESOLVED_PHYSICALLY
CLI_NORMALIZED_TABLES_REINJECTION = REDUNDANT_CONTRACT_VIOLATION
```

No indica que V2 esté incompleto.

Sobre aliases, `column_refs` confirmado contiene `question_id`, `field_id`, `sheet_name`, `column_name`, `normalized_column_name` y `owner_meaning`; por ello una parte importante de `available_data_fields`, `columns`, `input_values`, `normalized_values` y confirmations es derivable. `column_evidence` es regenerable determinísticamente desde normalized_tables + column_refs pero sus consumers deben verificarse antes del retiro.

El único problema conceptual todavía bloqueante para aliases es identidad/provenance (DA-05), no `normalized_tables`.

Estado provisional DA-04: `SYNTHESIS_NEEDS_DA05_ONLY_PLUS_ALIAS_CONSUMER_GATE`.

## CR-2.5 — DA-05: la identidad actual tiene un defecto no capturado por Qwen

Qwen modeló `case_id`/`workbook_ref` como una identidad mixta y afirmó que reupload del mismo archivo produciría otro workbook. Esa afirmación no es correcta en general.

Cross-check exacto:

### uploaded bytes

`_case_id` hashea:

```text
source_kind
filename
sheet selection mode
uploaded bytes
```

Con los mismos bytes, filename y selección, el valor es determinístico: un reupload idéntico produce el mismo case_id/workbook_ref.

### local_path

Para local path, `_case_id` se invoca SIN `content`.
Además `filename = os.path.basename(path)`.

Por tanto dos archivos locales distintos con:

```text
same basename
same selected-sheet mode
same source_kind=local_path
```

pueden producir el mismo `case_id`/`workbook_ref` aunque su contenido sea completamente distinto.

Esto invalida el modelo actual como identidad canónica fuerte del workbook.

Asimismo, el valor actual mezcla filename con contenido para uploads: renombrar exactamente el mismo artefacto cambia identidad aunque los bytes sean iguales.

Síntesis candidata revisada `S-ID-02`:

Separar estrictamente:

```text
case_id = identidad de caso/interacción, no evidencia física del workbook
source_artifact_ref = identidad inmutable del artefacto fuente basada en contenido cuando existe un archivo
workbook_ref = identidad del workbook ingerido, ligada al source artifact + canonical ingestion scope
filename = provenance/display only
sheet_name = etiqueta física dentro del artefacto
sheet_ref = identidad calificada dentro del workbook_ref
```

Para un workbook inmutable ingerido no se exige que un `sheet_ref` sobreviva a una edición/renombrado del archivo: eso constituye otro artefacto/workbook. Por tanto no hace falta resolver identidad longitudinal de una sheet entre versiones.

Modelo mínimo candidato:

```text
source_artifact_ref = content hash del XLSX
workbook_ref = deterministic ref sobre source_artifact_ref + ingestion scope/version
sheet_ref = deterministic ref sobre workbook_ref + exact sheet_name
```

Esto evita ordinales frágiles y evita usar sheet_name sin qualification como identidad global.

Debe discutirse con Qwen si `workbook_ref` puede simplificarse a `source_artifact_ref` cuando el scope siempre representa el workbook completo, o si la selección/subset requiere identidad distinta.

Estado provisional DA-05: `DIALECTICAL_CANDIDATE_PENDING_QWEN_R3`.

## CR-2.6 — DA-06: no introducir firmas secretas sin threat model

Qwen acepta mover la validación de provenance a P8 pero propone certificate con `signature/integrity_hash` y menciona hash + secret.

No existe evidencia de un boundary hostil que requiera firma criptográfica con secreto entre P8 y F7 dentro del mismo proceso. Introducir signing keys sería arquitectura nueva no justificada.

Síntesis candidata revisada `S-REL-02`:

```text
D4
→ produce content-addressed graph_ref / graph_digest
→ relationship_ref + endpoints + kind + structural/fanout evidence + schema identity

Owner
→ event ligado a relationship_ref + graph_ref + owner identity

P8
→ valida que relationship/owner evidence corresponda al D4 actual y schema/workbook actual
→ valida computability/fanout requirements
→ emite immutable governed relationship binding con provenance refs

F7
→ acepta sólo governed binding emitido por P8
→ verifica identidad/consistencia estructural mínima del binding
→ materializa join
→ NO vuelve a descubrir relaciones
→ NO vuelve a decidir computability/fanout
```

La integridad puede ser content-addressed/deterministic digest; no requiere secret signing salvo que aparezca un threat boundary real.

F7 no necesita D4 completo si el governed binding contiene los refs/digests que P8 ya validó.

Estado provisional DA-06: `DIALECTICAL_CANDIDATE_PENDING_QWEN_R3`.

## CR-2.7 — DA-07 y DA-08

Qwen marcó ambas síntesis como `THESIS_SUPPORTED`.

No se cierran todavía por unilateralidad, pero se elevan a candidatas fuertes:

```text
DA-07 STRONG_CANDIDATE:
SPECIALIZED_REQUEST requiere criterio cerrado anti-dump.
LIQ/REN no son SPECIALIZED por ser derivables de workbook.
legacy semantic compat nunca es SPECIALIZED legítimo.
Consorcios/reconciliation sólo sobreviven si cumplen el criterio y autoridades comunes.

DA-08 STRONG_CANDIDATE:
ONE_PRODUCTIVE_EXECUTION_ROOT no incluye read/query reentry.
ResultReadBoundary delgado → F13 persisted result.
No recalculation, no SEM, no P7/P8, no F7/F8.
```

## Bloqueos después del cross-check R2

La lista original de seis blockers se reduce:

```text
DO-01 PrimitiveEngine/PolicyRegistry       RESOLVED_DIRECTION: reuse existing FormulaEngineService + capability contracts
DO-02 sheet identity                       REFRAMED: qualified deterministic sheet_ref within immutable workbook
DO-03 CLI normalized_tables equality       RESOLVED_PHYSICALLY
DO-04 workbook identity                    REFRAMED with discovered local_path collision
DO-05 semantic parity                      MOSTLY_PROVEN structurally; parity tests remain removal gate
DO-06 Consorcios math                      depends on S-MATH-02, not on a new engine
```

No implementation is authorized.

Próxima ronda debe intentar refutar únicamente las síntesis revisadas S-MATH-02, S-SEM-02, S-ROOT-02, S-ID-02 y S-REL-02, y confirmar si DA-04/07/08 pueden pasar a final-candidate state.


---

# Ronda dialéctica 3 — Qwen y contrarréplica ChatGPT

## Estado de entrada

Qwen Ronda 3 produjo cinco `FINAL_CANDIDATE` y dejó tres decisiones abiertas: clasificación/policy matemática, identidad `local_path` y supuesta auto-confirmación del pipeline semántico determinístico.

El cross-check físico posterior encontró además una premisa incorrecta en la síntesis de provenance/fanout de Qwen: `schema_fingerprint` no cubre valores de negocio y, por tanto, no puede por sí solo detectar cambios de datos/fanout.

Ninguna decisión de esta sección es todavía normativa. Se prepara una última ronda de falsación.

## R3-C1 — Kernel matemático existente

Confirmado físicamente:

- `pymia/contracts/formula_contract.py` ya define `MathPrimitiveOperation` con `SINGLE_VALUE`, `SUM`, `COUNT`, `AVG`, `MIN`, `MAX`, `SUM_PRODUCT`, `MULTIPLY`, `SUBTRACT`, `PERCENT_OF`.
- `FormulaEngineService` ejecuta esas primitivas.
- `service_1_generic_capability_engine_v1.py` ya usa `calculate_math_primitive` para agregación y `calculate_formula` para fórmulas de negocio.
- `CapabilityDefinitionV1` ya contiene `AggregationMode`, `ClassificationRuleV1` y `OutcomePolicyV1`.

Conclusión provisional reforzada:

```text
NO_NEW_MATH_ENGINE_REQUIRED
NO_NEW_PRIMITIVE_ENGINE_REQUIRED
NO_GLOBAL_POLICY_ENGINE_REQUIRED_BY_DEFAULT
```

### Síntesis candidata S-MATH-03

La soberanía matemática de Servicio 1 reside en el kernel común existente:

```text
formula_contract
+ FormulaEngineService
+ formula catalog/rules
+ MathPrimitiveOperation
```

Reglas propuestas:

1. parsing/type validation no es autoridad matemática;
2. toda reducción numérica productiva que afecte el resultado (`SUM`, `MAX`, etc.) usa `MathPrimitiveOperation` o una fórmula registrada;
3. toda fórmula empresarial usa `calculate_formula`/catálogo canónico;
4. la clasificación de dominio es **policy**, no fórmula matemática;
5. `ClassificationRuleV1` continúa como contrato genérico simple; no se introduce un DSL global de expresiones sólo para absorber casos especializados;
6. un workflow especializado puede tener policy determinística propia, pero esa policy sólo puede comparar/combinar lógicamente inputs gobernados y outputs del kernel. Si necesita derivar otro valor numérico (`MAX`, ratio, deviation), esa derivación vuelve al kernel matemático;
7. por tanto LIQ/REN pueden conservar branching de policy, pero no agregación/fórmula ad-hoc; Consorcios debe migrar sus reducciones y fórmulas al kernel/catálogo existente y puede conservar su policy de clasificación acotada.

Esto preserva una sola autoridad matemática sin crear un `PrimitiveEngine`, `PolicyRegistry` o DSL innecesario.

Estado: `SYNTHESIS_REQUIRED_FINAL_ATTACK`.

## R3-C2 — Identidad content-addressed también para local_path

Se confirmó la colisión actual:

```text
C:\A\ventas.xlsx
C:\B\ventas.xlsx
```

con igual basename y selección pueden producir el mismo `case_id/workbook_ref` porque el path `local_path` no incorpora contenido.

También existe ya una utilidad física de hashing streaming (`pipeline_registration.calculate_sha256(Path)`), por lo que obtener SHA-256 del archivo local no requiere un segundo parser XLSX ni cargar todo el archivo en memoria.

### Síntesis candidata S-ID-03

```text
case_id
= identidad opaca del caso/workflow; NO identidad del archivo ni del workbook

source_artifact_ref
= content-addressed identity del XLSX físico
  xlsx:sha256:<sha256 bytes>
  tanto uploaded bytes como local_path

workbook_ref
= identidad determinística de la vista ingerida
  digest(source_artifact_ref + ingestion_scope + canonical_reader/schema_version)

sheet_name
= etiqueta física humana dentro del artefacto

sheet_ref
= identidad calificada de hoja dentro de la vista
  digest(workbook_ref + exact sheet_name)

filename
= provenance/display only
```

`local_path` debe hashear bytes del archivo. No se acepta `basename`, `absolute_path+mtime+size` ni proxy filesystem como identidad del artefacto cuando el archivo es legible.

La selección de sheets forma parte de `ingestion_scope`, por lo que `source_artifact_ref` identifica el XLSX completo y `workbook_ref` identifica la vista efectivamente ingerida.

Estado: `SYNTHESIS_REQUIRED_FINAL_ATTACK`.

## R3-C3 — No existe auto-confirmación semántica inicial que justifique segunda FSM

Cross-check físico:

- `service_1_canonical_ingestion_output_to_semantic_bridge_v1.py` construye owner question views con `require_explicit_owner_confirmation=True`.
- el bridge no fabrica `owner_confirmation_events`;
- `service_1_p6_approval_decision_v1.py`, cuando no existe evento del dueño, termina en `FIRST_CONTACT_OWNER_CONFIRMATION_REQUIRED` incluso cuando hay un único/primary role aprobable;
- el deterministic gate sólo puede quedar `READY` cuando las decisiones P6 ya están aprobadas;
- SEM-8 reentry usa `build_service_1_owner_semantic_evidence_reentry_v1`, que a su vez utiliza el mismo `build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1`/P6 histórico.

Por tanto la supuesta feature exclusiva de “initial automatic confirmation” no está demostrada en la arquitectura productiva actual.

### Síntesis candidata S-SEM-03

Servicio 1 converge a una sola FSM semántica provider-neutral:

```text
SemanticStart
  → canonical bridge/profile/table scope
  → provider(det | bounded LLM)
  → deterministic validator
  → explicit owner dialogue

SemanticContinue
  → owner evidence
  → shared reinjector/P6
  → CONFIRMED_BINDINGS / follow-up
```

El provider determinístico conserva operación offline/reproducible. El pipeline determinístico histórico se retira cuando tests de paridad prueben outputs/fail-closed relevantes. El shim legacy se elimina después de migrar CLI/web callers.

Estado: `SYNTHESIS_REQUIRED_FINAL_ATTACK`.

## R3-C4 — Corrección de DA-06: schema fingerprint no protege fanout de datos

Qwen Ronda 3 sostuvo que un cambio de normalized data entre P8 y F7 podría detectarse por `schema_fingerprint`. Esto es incorrecto.

`service_1_workbook_schema_identity_v1.py` declara explícitamente en `fingerprint_exclusions`:

```text
business_values
```

El fingerprint D3 es estructural, no una identidad del dataset.

D4 sí produce actualmente `graph_ref == graph_fingerprint`, construido a partir de nodos y relationship identity incluyendo `cardinality` y `state`, y produce `fanout_certificate`. Sin embargo su provenance también identifica el grafo como evidencia estructural y no como digest completo de business values.

Además, F7 ya ejecuta un safety check físico de cardinalidad durante join materialization:

- construye índice del lado lookup;
- detecta duplicate right keys;
- bloquea `RELATIONSHIP_CARDINALITY_VIOLATION`;
- para `ONE_TO_ONE` verifica duplicados del lado izquierdo;
- bloquea conflictos y missing matches.

Esto es validación de seguridad de materialización, no rediscovery de D4 ni segunda computability authority.

### Síntesis candidata S-REL-03

```text
D4
= structural relationship evidence authority
  graph_ref/fingerprint
  relationship_ref
  endpoints/kind
  structural cardinality/fanout evidence
  schema_fingerprint
  workbook/source identity provenance

Owner
= human confirmation bound to relationship_ref + graph_ref + case/owner identity

P8
= computability/use authority
  verifies current workbook_ref/source_artifact_ref
  verifies current D4 graph_ref + schema_fingerprint
  verifies owner event
  verifies D4 fanout evidence is acceptable
  emits immutable governed_relationship_binding

F7
= sole materializer
  verifies binding identity/provenance against current ingestion identity
  verifies endpoints/kind
  MUST retain runtime cardinality/fanout safety checks on actual rows
  blocks if actual materialization contradicts governed relationship
  does not rediscover relationships or decide computability
```

Clave: `schema_fingerprint` prueba estructura; `workbook_ref/source_artifact_ref` prueba dataset/ingestion identity; F7 runtime cardinality checks protegen la materialización concreta.

No se requiere secret signing. Un digest determinístico del governed binding puede proteger integridad interna, pero no sustituye los tres niveles anteriores.

Estado: `SYNTHESIS_REQUIRED_FINAL_ATTACK`.

## R3-C5 — DA-04, DA-07, DA-08

Se mantienen como candidatos fuertes para ronda final:

- DA-04: CanonicalIngestionOutput V2 self-contained; CLI reinjection de normalized_tables es redundante; aliases se retiran tras consumer migration y sheet identity final.
- DA-07: SPECIALIZED sólo bajo criterio anti-dump; LIQ/REN no son SPECIALIZED; legacy semantic compat no es SPECIALIZED; Consorcios/reconciliation pueden serlo con math authority común.
- DA-08: one productive execution root + read boundary separado sobre F13; reentry no recalcula ni pasa por Product Root.

## Estado previo a Ronda 4

```text
DA-01: FINAL_ATTACK_REQUIRED
DA-02: FINAL_ATTACK_REQUIRED
DA-03: FINAL_ATTACK_REQUIRED
DA-04: FINAL_CANDIDATE
DA-05: FINAL_ATTACK_REQUIRED
DA-06: FINAL_ATTACK_REQUIRED (corregida por runtime fanout)
DA-07: FINAL_CANDIDATE
DA-08: FINAL_CANDIDATE

TARGET_ARCHITECTURE: NOT_YET_CLOSED
RECONSTRUCTION: FROZEN
```


---

# Post-Ronda 4 — revisión ChatGPT y tres síntesis finales pendientes

La Ronda 4 de Qwen corrigió expresamente una respuesta previa alucinada y volvió a contrastar la arquitectura con evidencia física. Se aceptan como evidencia los cross-checks F4-C1..F4-C4 y la supervivencia provisional de DA-01..DA-08, pero **no se acepta todavía** `DIALECTICAL_REVIEW_COMPLETE: PASS` porque el propio resultado conserva tres decisiones arquitectónicas abiertas. Conforme al criterio de este dossier, el cierre requiere `OPEN_ARCHITECTURAL_DECISIONS = 0`.

## OD-01 — Classification / policy

### Evidencia física adicional

- `ClassificationRuleV1` es declarativo pero sólo representa una comparación atómica (`LT/LE/EQ/GE/GT`).
- LIQ_001 contiene clasificación compuesta (`sold == 0 AND collected == 0`, etc.).
- Consorcios expense variance deriva `max_positive` y luego aplica umbrales.
- El kernel matemático ya posee `MathPrimitiveOperation.MAX`, SUM y otras primitivas.
- Crear un `PolicyRegistry` global o un expression DSL general no está justificado por evidencia.

### Síntesis candidata OD-01-S

No se aceptan excepciones de policy empresarial hardcodeada como estado final. Tampoco se crea un segundo engine o DSL general.

Se amplía el contrato declarativo de clasificación existente de forma **acotada**:

```text
ClassificationPredicate
- left_ref: result | named_input | named_derived_value
- comparison: LT | LE | EQ | GE | GT
- right_ref OR literal

ClassificationRule
- code
- match: ALL | ANY
- predicates: tuple[ClassificationPredicate, ...]
```

Reglas:

1. El clasificador **no realiza aritmética**.
2. Cualquier `MAX`, ratio, porcentaje, diferencia, SUM, etc. se calcula antes mediante el kernel matemático y entra como `named_derived_value`.
3. La policy sólo combina comparaciones booleanas sobre inputs/resultados ya gobernados.
4. Las definiciones de policy pueden ser capability-specific o specialized-subtype-specific, pero son declarativas y versionadas.
5. No se admite una expresión Python/string arbitraria ni un DSL matemático paralelo.

Esto permite representar LIQ_001 mediante conjunciones de predicados y Consorcios expense variance mediante un `max_positive` calculado por `MathPrimitiveOperation.MAX` seguido de comparaciones declarativas.

**Estado:** `SYNTHESIS_CANDIDATE / QWEN_FINAL_FALSIFICATION_REQUIRED`

## OD-02 — Consorcios math convergence

### Evidencia física adicional

Consorcios posee aritmética empresarial inline que no usa todavía el kernel común:

- sumas por rubro;
- variación porcentual respecto de presupuesto/promedio;
- `MAX` de desvíos;
- ratio de aging.

El kernel actual ya cubre SUM y MAX. No posee primitive DIVIDE genérica, pero el catálogo de fórmulas soporta fórmulas empresariales con división mediante `FormulaEngineService.calculate` para fórmulas registradas.

### Síntesis candidata OD-02-S

**No se autorizan excepciones matemáticas normativas para Consorcios.**

Consorcios sigue siendo workflow `SPECIALIZED`, pero toda matemática de negocio converge al cerebro matemático común:

```text
SUM por rubro              -> MathPrimitive SUM
MAX de desvíos             -> MathPrimitive MAX
variación vs presupuesto   -> fórmula canónica versionada
variación vs histórico     -> fórmula canónica versionada
aging ratio                -> fórmula canónica versionada
```

Si una fórmula de dominio no existe en `formula_rules_v1.json`, se agrega al catálogo canónico con su contrato/versionado y se ejecuta por `FormulaEngineService`; no se conserva aritmética inline como excepción.

La clasificación posterior usa la policy declarativa de OD-01-S y no introduce cálculo nuevo.

**Estado:** `SYNTHESIS_CANDIDATE / QWEN_FINAL_FALSIFICATION_REQUIRED`

## OD-03 — ubicación de table-scoped semantic context

### Evidencia física adicional

Hay dos ejecuciones físicas del mismo builder:

1. D7 `service_1_workbook_logical_model_v1.py` construye `table_scoped_semantics` a partir de `column_refs`, `logical_tables` y `relationship_graph`, y lo incluye explícitamente en el Workbook Logical Model.
2. SEM-8 `service_1_assisted_semantic_product_wiring_v1.py` vuelve a construir un `semantic_scope_packet` cuando recibe `logical_table_candidates` y `logical_relationship_graph`.
3. Product Root ya construye D7 primero y luego pasa a SEM-8 `workbook_logical_model.get("logical_tables")` y `relationship_graph`, provocando recomputación de evidencia ya producida.

### Síntesis candidata OD-03-S

`table_scoped_semantics` pertenece a la producción de **evidencia estructural D6/D7**, no a un provider semántico particular.

Cadena final:

```text
D1..D5
→ D6 table-scoped semantic context evidence
→ D7 Workbook Logical Model
→ SemanticStart consumes table_scoped_semantics
→ provider(det | LLM)
```

SEM-8 no vuelve a construir table scope. Tanto el provider determinístico como el LLM reciben la misma evidencia D7 ya gobernada. Esto evita divergencia entre providers y elimina computación paralela del mismo contexto.

D7 sigue siendo `evidence-only`: producir/proyectar table scope no le otorga autoridad para decidir significado, computabilidad o runtime.

**Estado:** `SYNTHESIS_CANDIDATE / QWEN_FINAL_FALSIFICATION_REQUIRED`

## Corrección adicional DA-06 — stale binding y fanout

La Ronda 4 confirma que `schema_fingerprint` es estructural y excluye `business_values`; por tanto no prueba por sí solo que los datos concretos sean los mismos entre P8 y F7.

La síntesis DA-06 queda refinada:

- el governed relationship binding debe quedar ligado a `workbook_ref` y, con DA-05, al `source_artifact_ref` content-addressed;
- `graph_ref/schema_fingerprint` prueban identidad estructural;
- `workbook_ref/source_artifact_ref` prueban identidad del artefacto/ingestion view;
- F7 conserva obligatoriamente sus checks de cardinalidad sobre filas reales durante materialización (`duplicate lookup keys`, `ONE_TO_ONE duplicate left keys`, missing matches, join conflicts);
- esos checks son safety invariants de ejecución, no segunda autoridad D4.

No se requiere firma criptográfica con secreto para el threat model actual; un digest determinístico sirve para integridad accidental, mientras la identidad content-addressed del artefacto y los checks de F7 aseguran consistencia física.

## Estado previo a micro-ronda final

```text
DA-01..DA-08: FINAL_CANDIDATES, pendientes de cierre documental
OD-01: SYNTHESIS_CANDIDATE
OD-02: SYNTHESIS_CANDIDATE
OD-03: SYNTHESIS_CANDIDATE
OPEN_ARCHITECTURAL_DECISIONS: 3
TARGET_ARCHITECTURE: NOT_YET_CLOSED
IMPLEMENTATION: FROZEN
```

La siguiente intervención externa debe ser una **micro-ronda final de falsación de OD-01-S, OD-02-S y OD-03-S**, no una nueva auditoría global.
