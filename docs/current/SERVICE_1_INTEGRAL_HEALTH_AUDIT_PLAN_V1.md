# Servicio 1 — Plan de Auditoría Integral de Salud y Reconstrucción Arquitectónica V1

**Estado:** `CLOSED_ARCHITECTURE_AUDIT / EVIDENCE_ONLY`  
**Fecha:** 2026-08-23  
**Alcance:** Servicio 1 completo, desde XLSX/entrypoints hasta F13/UI/reentry.  
**Modo:** `AUDIT_CLOSED; RECONSTRUCTION_GOVERNED_BY_SERVICE_1_RECONSTRUCTION_PLAN_V1`  
**Baseline comprometido:** `8d5708e9becdddaa5aa24387b310972643d1ef86`  
**Worktree:** contiene cambios no committeados de convergencia local posteriores al baseline.  

## 1. Propósito

Esta auditoría no busca producir otro inventario de bugs ni validar fases locales. Busca determinar, con evidencia física, si Servicio 1 constituye hoy un único sistema coherente o si todavía conviven generaciones arquitectónicas, rutas legacy, compatibilidades, fallbacks, wrappers, autoridades superpuestas y contratos transitorios.

El resultado debe permitir construir Servicio 1 sanamente a partir de una secuencia mínima de convergencia, eliminación y refactorización.

La pregunta rectora es:

> **¿Cuál es la arquitectura final única de Servicio 1, qué piezas físicas actuales la contradicen y en qué orden mínimo deben retirarse, absorberse o rediseñarse para llegar a una implementación simple, gobernada y certificable?**

## 2. Autoridad documental

Este documento define **cómo se ejecuta la auditoría**. No sustituye ni crea autoridad arquitectónica.

La arquitectura normativa vigente reside en:

- `docs/current/SERVICE_1_CANONICAL_AXIS.md`
- `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md`
- `docs/adr/ADR-007-documentation-governance.md`
- `docs/current/README.md`

Toda conclusión de auditoría que implique una nueva decisión arquitectónica debe incorporarse primero a esos documentos rectores antes de implementarse.

Chats, prompts, `_audit/` y salidas de agentes son evidencia de trabajo, no autoridad normativa.

## 3. Regla de congelamiento

Mientras esta auditoría esté abierta:

```text
NO nuevas features
NO nuevos wrappers
NO nuevos fallbacks
NO nuevos aliases transitorios
NO nuevos compatibility shims
NO expansión de kwargs/modos del Product Root
NO migración de tests para obtener verde
NO commit/push/deploy de la convergencia actual
```

Se permite únicamente:

```text
lectura
inventario
trazado de callers/imports
clasificación
pruebas read-only
full suite
E2E no destructivo
reconciliación documental de decisiones ya aceptadas
```

## 4. Dos baselines obligatorios

La auditoría debe distinguir dos realidades físicas:

### Baseline A — committed

```text
HEAD = 8d5708e9becdddaa5aa24387b310972643d1ef86
```

Representa el último baseline comprometido antes de los cambios locales recientes de convergencia.

### Baseline B — current worktree

```text
HEAD + todos los cambios no committeados actuales
```

Ningún cambio del worktree obtiene derecho a sobrevivir por estar implementado o por haber pasado tests focales.

Cada cambio deberá terminar clasificado como:

```text
KEEP
REDESIGN
ABSORB
REVERT
DELETE
OFFLINE
```

## 5. Unidad de análisis

La unidad principal no es el archivo Python sino la cadena de autoridad y transformación de datos:

```text
usuario
↓
XLSX
↓
intake
↓
CanonicalIngestionOutput
↓
ProductRequest
↓
Product Root
↓
D1 → D2 → D3 → D4 → D5 → D6 → D7
↓
SEM / owner
↓
P7
↓
P8
↓
F7
↓
F8
↓
F9
↓
F13
↓
UI / persistence / reentry / delivery
```

Para cada frontera deben identificarse:

1. productor canónico;
2. contrato de entrada;
3. contrato de salida;
4. consumidores;
5. autoridad;
6. capacidad de bloqueo;
7. provenance/identity transferida;
8. fallbacks;
9. rutas paralelas;
10. tests que prueban la frontera.

Una frontera que no puede responder estas diez preguntas queda marcada como deuda arquitectónica.

## 6. Clasificación obligatoria de módulos y rutas

Cada módulo y ruta productivamente relevante debe recibir exactamente una clasificación:

```text
CANONICAL
NECESSARY_SUPPORT
TRANSITIONAL
LEGACY_PRODUCTIVE
DEAD_OBSOLETE
AUTHORITY_COLLISION
PARALLEL_PATH
PATCH
```

Definiciones:

- `CANONICAL`: pertenece a la arquitectura final aceptada.
- `NECESSARY_SUPPORT`: soporte legítimo sin autoridad paralela.
- `TRANSITIONAL`: pieza temporal con retiro definido.
- `LEGACY_PRODUCTIVE`: arquitectura anterior todavía alcanzable en runtime.
- `DEAD_OBSOLETE`: sin función final; candidato a eliminación.
- `AUTHORITY_COLLISION`: duplica una decisión soberana existente.
- `PARALLEL_PATH`: segunda ruta para el mismo flujo productivo.
- `PATCH`: adaptación local que resuelve una incompatibilidad pero no pertenece a la arquitectura final.

Toda pieza `TRANSITIONAL` debe demostrar:

```text
motivo
callers actuales
destino final
condición de retiro
gate que prueba su desaparición
```

Si no puede hacerlo, se reclasifica como deuda a eliminar o rediseñar.

## 7. Pasada A — Topología física

Reconstruir desde código, no desde documentación:

```text
entrypoints
call graph
import graph
Product Root callers
XLSX readers
semantic callers
owner confirmation paths
P7 callers
P8 callers
join callers
math callers
result projection callers
memory/reentry callers
UI callers
```

### Gates de esta pasada

```text
ONE_PRODUCTIVE_ROOT
NO_PARALLEL_PRODUCTIVE_PIPELINE
ONE_PRODUCTIVE_XLSX_READER
```

Graphify u otras herramientas de grafo pueden asistir, pero no sustituyen la inspección física ni deciden autoridad.

## 8. Pasada B — Flujo de datos y contratos

Seguir físicamente un workbook desde bytes hasta ResultSet:

```text
bytes
→ normalized tables
→ column refs
→ workbook identity
→ physical lineage
→ logical tables
→ relationships
→ semantic bindings
→ grain
→ governed computation input
→ prepared evidence
→ deterministic calculation
→ ResultSet
→ persistence
→ reentry
```

Para cada transformación registrar:

```text
input schema
output schema
campos creados
campos descartados
aliases
identity
provenance
safety flags
consumer inmediato
```

Buscar especialmente callers que:

- completen un envelope después de su constructor canónico;
- reinyecten datos provenientes de un objeto upstream paralelo;
- reconstruyan identity o provenance;
- usen filename como identidad;
- modifiquen el significado del contrato fuera de su autoridad.

## 9. Pasada C — Grafo de autoridades

Construir y verificar físicamente la tabla de soberanía:

| Decisión | Autoridad esperada |
|---|---|
| workbook identity | contrato canónico de intake/ingestion |
| physical structure | D1/D2 |
| schema identity | D3 |
| structural relationships | D4 |
| logical table boundaries | D5 |
| historical/revalidation evidence | D6 |
| logical evidence coordination | D7, evidence-only |
| semantic meaning | SEM + owner evidence |
| grain/requirements | P7 |
| computability | P8 |
| join/evidence materialization | F7 |
| mathematics | F8 / FormulaEngineService |
| result projection | F9 |
| durable result persistence/reentry | F13 |

Buscar cualquier segunda implementación que decida lo mismo.

Toda duplicación de soberanía se clasifica `AUTHORITY_COLLISION`.

## 10. Pasada D — Deuda generacional

Buscar físicamente:

```text
legacy
compat
compatibility
transitional
temporary
fallback
shim
deprecated
obsolete
sheet1
semantic_run_override
owner_answers
analysis_execution_request
semantic_reception_only
semantic_atomic_confirmation
```

No asumir que la palabra implica defecto. Cada ocurrencia productivamente relevante debe clasificarse como:

```text
LEGITIMATE
TRANSITIONAL_WITH_EXIT
LEGACY_PRODUCTIVE
DEAD
PATCH
```

Debe documentarse caller, alcance y destino final.

## 11. Pasada E — Product Root y máquina de estados

Auditar la firma y comportamiento de `run_service_1_product_pipeline_v1` como contrato de producto, no sólo como función.

Identificar estados reales del dominio/producto, por ejemplo:

```text
WORKBOOK_RECEIVED
STRUCTURE_RESOLVED
SEMANTICS_NEED_OWNER
SEMANTICS_CONFIRMED
ANALYSIS_REQUESTED
COMPUTABLE
NOT_COMPUTABLE
EVIDENCE_PREPARED
CALCULATED
RESULT_READY
PERSISTED
REENTERED
```

Determinar si dichos estados están representados por contratos explícitos o por combinaciones accidentales de kwargs/flags.

Una combinación procedural de flags que materializa implícitamente un estado del negocio se clasifica `REDESIGN` salvo demostración contraria.

Especial atención a:

```text
analysis_execution_request
semantic_reception_only
semantic_atomic_confirmation
semantic_run_override
owner_answers
sheet_name
request_kind
```

## 12. Pasada F — Semántica y LLM

Inventariar todas las rutas:

```text
SEM-8
legacy deterministic semantic pipeline
legacy semantic reentry
owner semantic evidence reentry
semantic proposal validator
semantic bridge
semantic compatibility modules
provider/LLM callers
```

Probar si existe una sola state machine semántica productiva.

### Gates

```text
ONE_PRODUCTIVE_SEMANTIC_STATE_MACHINE
NO_LLM_MATH
NO_LLM_COMPUTABILITY_AUTHORITY
NO_LLM_RUNTIME_AUTHORITY
NO_LLM_JOIN_AUTHORITY
```

El LLM puede proponer/interpretar significado; nunca calcular, agregar, decidir fórmula soberanamente, materializar join o autorizar runtime/computability.

## 13. Pasada G — P7/P8/F7/F8/F9

Auditar en secuencia:

```text
SEM/owner
→ P7
→ P8
→ F7
→ F8
→ F9
```

Probar:

```text
P7_ONLY_GRAIN_AUTHORITY
P8_ONLY_COMPUTABILITY_AUTHORITY
F7_ONLY_JOIN_MATERIALIZATION
F8_ONLY_MATH_AUTHORITY
F9_ONLY_RESULT_PROJECTION
```

Buscar recomputación, re-binding, grain alternativo, agregación fuera de F8, joins fuera de F7 o ResultSets construidos por UI/adapters.

## 14. Pasada H — Memoria y reentry

Auditar:

```text
tenant memory
semantic memory
schema-family memory
F13 result memory
```

Probar:

```text
TENANT_ISOLATION
NO_MEMORY_AUTO_REBIND
HISTORICAL_HINTS_ARE_EVIDENCE_ONLY
F13_REENTRY_NO_XLSX
F13_REENTRY_NO_LLM
F13_REENTRY_NO_RECALCULATION
F13_REENTRY_NO_PRODUCT_ROOT_EXECUTION
```

## 15. Pasada I — Entrypoints, CLI, Web y UI

Verificar que sean superficies delgadas.

CLI/Web/UI no pueden:

- completar un CanonicalIngestionOutput;
- construir D7;
- decidir computabilidad;
- preparar joins;
- calcular matemática empresarial;
- fabricar ResultSets;
- usar fallback sintético de identity;
- mantener rutas legacy sólo para compatibilidad histórica.

Analizar especialmente:

```text
pymia/cli/service_1_product.py
service_1_assisted_web_v1.py
service_1_assisted_web_semantic_reception_v1.py
service_1_semantic_reception_server_v1.py
```

## 16. Pasada J — Readers y `sheet1`

Inventariar todos los mecanismos capaces de leer XLSX:

```text
openpyxl
load_workbook
read_excel
xlsx_to_normalized
ExcelLab
BEM
classification readers
helpers indirectos
```

Determinar cuál es el único reader productivo autorizado.

Buscar toda ocurrencia de `sheet1` y clasificar:

```text
file
line
caller
productive reachability
motivo
destino final
```

### Gates

```text
ONE_PRODUCTIVE_XLSX_READER
NO_SHEET1_FALLBACK
```

## 17. Pasada K — Registry y topología documental

Inventariar físicamente todos:

```text
pymia/smartpyme/service_1_*.py
```

Comparar con:

```text
docs/service_1_module_disposition.v1.json
```

Reportar:

```text
LIVE_MODULES
REGISTERED_MODULES
MISSING
DUPLICATES
WRONG_REACHABILITY
WRONG_DISPOSITION
```

No actualizar el registry durante la auditoría. Primero debe conocerse la arquitectura final.

## 18. Pasada L — Verdad de los tests

Clasificar tests relevantes como:

```text
CONTRACT
AUTHORITY
FAIL_CLOSED
UNIT
INTEGRATION
ARCHITECTURE
REGRESSION
E2E
LEGACY_BEHAVIOR
```

Buscar específicamente tests que obligan a conservar runtime legacy.

Regla:

> El contrato arquitectónico definitivo gobierna los tests. Un test histórico no justifica crear o preservar una ruta productiva legacy.

No migrar tests durante esta auditoría.

## 19. Pasada M — Evidencia ejecutable y realidad productiva

Sólo después de entender la arquitectura se ejecutan pruebas. La política de validación es escalonada; la full suite no se ejecuta por cada ciclo ni por cada hallazgo.

### Escalera de validación

```text
L0 — syntax/import check del cambio
L1 — test focal del contrato modificado
L2 — architecture/authority guards del boundary afectado
L3 — regresión vecina acotada a callers/consumers/dependencias reales
L4 — integration checkpoint sobre un conjunto de fronteras ya convergidas
L5 — FULL SUITE sólo en checkpoints mayores y certificación final
L6 — E2E no destructivo con XLSX reales
```

La full suite se reserva para:

```text
- cierre de un bloque arquitectónico que modifica varias fronteras;
- antes de declarar un worktree candidato a certificación;
- certificación final del SHA exacto.
```

No se usa como mecanismo rutinario de debugging ni como respuesta automática a cada cambio local.

Si una prueba focal o de arquitectura falla, se resuelve primero en su scope. No se dispara una full suite para descubrir ruido colateral que todavía no es accionable.

Corpus mínimo para E2E:

```text
XLSX simple
XLSX multisheet
cafetería real
XLSX adversarial
```

El E2E debe observar:

```text
reader
→ D1-D7
→ SEM
→ owner
→ discovery
→ P7/P8
→ F7/F8/F9
→ F13
→ reentry
```

## 19.1 Pasada N — Auditoría de prompts y decisiones inducidas por agentes

Los prompts usados para Codex, OpenCode, Qwen, MCP u otros agentes forman parte de la evidencia de ingeniería y deben auditarse porque pueden introducir arquitectura de facto aunque esa decisión nunca haya sido incorporada a los documentos rectores.

La auditoría debe recopilar, dentro de lo físicamente disponible en el repositorio, artefactos `_audit/`, TaskSpecs, documentos de continuidad y salidas de agentes, los prompts/instrucciones que hayan dirigido cambios de Servicio 1. Cuando un prompt sólo exista fuera del repo, se debe registrar como `EXTERNAL_PROMPT_EVIDENCE_REQUIRED` y no inferir su contenido.

Para cada prompt relevante registrar:

```text
PROMPT_ID_OR_REFERENCE
DATE_OR_CONTEXT
AGENT_TARGET
GOAL
FILES_OR_COMPONENTS_TARGETED
ARCHITECTURAL_DECISIONS_IMPLIED
DOCUMENTED_BEFORE_EXECUTION: YES / NO / NOT_PROVEN
INTRODUCED_RUNTIME_CONTRACTS
INTRODUCED_FLAGS_OR_MODES
INTRODUCED_COMPATIBILITY
REQUESTED_TEST_MIGRATIONS
REQUESTED_LEGACY_RETENTION
REQUESTED_FAIL_CLOSED_BEHAVIOR
CONTRADICTS_CANONICAL_AXIS: YES / NO / NOT_PROVEN
CONTRADICTS_ARCHITECTURE_LOCK: YES / NO / NOT_PROVEN
RESULTING_CODE_EVIDENCE
CLASSIFICATION
```

Clasificaciones posibles:

```text
ALIGNED_WITH_DOCUMENTED_ARCHITECTURE
IMPLEMENTATION_ONLY
ARCHITECTURE_DECISION_NOT_PRE-DOCUMENTED
PATCH_INDUCING
LEGACY_PRESERVING
TEST_DRIVEN_RUNTIME_DISTORTION
CONTRADICTORY
INSUFFICIENT_EVIDENCE
```

Buscar especialmente prompts que hayan ordenado o inducido:

- crear wrappers o shims para conservar callers antiguos;
- agregar flags/modos al Product Root;
- migrar tests antes de demostrar el contrato definitivo;
- clasificar fragmentos legacy como `SPECIALIZED_REQUEST` sólo para mantenerlos ejecutables;
- preservar aliases "temporales" sin gate de retiro;
- introducir un nuevo contrato para resolver un fallo local;
- declarar PASS de fase sin revisar aumento de entropía arquitectónica;
- tomar decisiones de arquitectura que no existían previamente en `CANONICAL_AXIS` / `ARCHITECTURE_LOCK`.

La auditoría de prompts no busca culpar al agente. Busca reconstruir la cadena causal:

```text
prompt
→ decisión inducida
→ cambio físico
→ test adaptado o creado
→ deuda/beneficio arquitectónico resultante
```

Gate de esta pasada:

```text
NO_UNDOCUMENTED_PROMPT_ARCHITECTURE
```

Un prompt no es autoridad. Si un prompt introdujo una decisión normativa antes de ser documentada, se registra como defecto de proceso aunque el código resultante sea técnicamente correcto.

## 20. Artefactos obligatorios de salida

La auditoría debe producir cinco artefactos conceptuales. Sólo se escribirán al repo después de revisar que no introducen nueva autoridad contradictoria.

### 20.1 Canonical Architecture Map

Una vista compacta de:

```text
componentes finales
autoridades
contratos
rutas productivas
```

Las decisiones aceptadas se incorporan posteriormente a `SERVICE_1_CANONICAL_AXIS.md` y `SERVICE_1_ARCHITECTURE_LOCK.md`.

### 20.2 Architecture Delta Ledger

Cada hallazgo estructural debe registrar:

```text
ID
CURRENT
EXPECTED
VIOLATED_INVARIANT
PHYSICAL_EVIDENCE
CLASSIFICATION
DESTINATION
DEPENDENCIES
REMOVAL_GATE
TESTS_REQUIRED
```

### 20.3 Worktree Decision Ledger

Cada cambio no committeado actual debe quedar en:

```text
KEEP
REDESIGN
ABSORB
REVERT
DELETE
OFFLINE
```

Esto incluye expresamente:

```text
request_kind
CanonicalIngestionOutput V2
workbook_ref
analysis_execution_request
semantic_reception_only
semantic_atomic_confirmation
legacy test migrations
Phase 4 partial changes
```

### 20.4 Dependency-Ordered Construction Plan

Debe responder:

```text
qué retirar primero
qué contrato estabilizar después
qué consumers migrar
qué código eliminar
qué gates ejecutar
cuándo puede comenzar el siguiente ciclo
```

No se acepta un roadmap basado sólo en numeración de fases.

### 20.5 Prompt Decision Ledger

Debe vincular instrucciones de agentes con sus efectos arquitectónicos:

```text
PROMPT_REFERENCE
ARCHITECTURAL_DECISION_IMPLIED
PRE_DOCUMENTED
RESULTING_CHANGE
RESULTING_TEST_CHANGE
ENTROPY_EFFECT
CLASSIFICATION
CORRECTIVE_GOVERNANCE_ACTION
```

Este ledger sirve para detectar cuándo la arquitectura fue diseñada accidentalmente dentro de prompts de ejecución en vez de en la autoridad documental.

## 21. Criterio de diseño de los ciclos de reconstrucción

Cada ciclo futuro debe seguir exactamente:

```text
1. DECISIÓN YA DOCUMENTADA
2. DEUDA EXACTA A ELIMINAR
3. CONTRATO FINAL
4. MODIFICACIÓN
5. ELIMINACIÓN DE LEGACY
6. TEST FOCAL
7. TEST DE ARQUITECTURA
8. REGRESIÓN VECINA ACOTADA
9. DOCUMENTACIÓN DEL ESTADO REAL
10. CIERRE
```

`REGRESIÓN VECINA ACOTADA` significa probar únicamente callers, consumers y boundaries realmente afectados. No significa ejecutar la full suite.

La full suite pertenece a checkpoints de integración mayores y a la certificación final, no al cierre rutinario de cada ciclo.

Un ciclo **no puede cerrarse** si aumenta sin justificación la cantidad de:

```text
productive paths
compatibility shims
transitional aliases
Product Root modes
fallbacks
authority collisions
sheet1 fallbacks
legacy productive callers
```

## 22. Métricas de entropía arquitectónica

Medir antes y después de cada ciclo:

```text
productive_paths
compatibility_shims
transitional_aliases
root_modes_or_procedural_switches
authority_collisions
sheet1_fallbacks
legacy_productive_callers
unregistered_modules
```

Tendencia obligatoria durante saneamiento:

```text
↓ rutas
↓ compatibilidad
↓ aliases
↓ switches procedurales
↓ fallbacks
↓ colisiones
↓ legacy productivo
↓ módulos sin clasificar
```

Un ciclo funcionalmente verde pero que aumenta entropía arquitectónica se considera `FAIL_ARCHITECTURE`.

## 23. Hipótesis inicial de ciclos de reconstrucción

Estos ciclos son **hipótesis de trabajo**, no decisiones finales. La auditoría puede fusionarlos, dividirlos o reordenarlos según dependencias físicas.

```text
C0 — Freeze + baseline exacto

C1 — ProductRequest / Product Root contract
     simplificar contrato y eliminar modos procedurales innecesarios

C2 — Canonical ingestion
     un envelope real, cero aliases vencidos, cero callers completándolo

C3 — XLSX / identity / D1-D7
     un reader, cero sheet1, una ruta estructural

C4 — Semantic convergence
     una state machine productiva, retiro de semantic legacy

C5 — Owner / P7 / P8 convergence
     cero rebinding y autoridad duplicada

C6 — D4 / F7 / F8 / F9 closure
     provenance, join, matemática y resultado bajo autoridad única

C7 — Memory / reentry convergence
     F13 reentry sin recalculation ni autoridad histórica

C8 — Entrypoints / UI / CLI simplification
     superficies delgadas

C9 — Dead code / registry / documentation purge

C10 — full suite + real XLSX E2E + exact SHA certification
```

## 24. Gates finales de salud integral

Servicio 1 sólo puede declararse arquitectónicamente sano cuando, sobre el mismo SHA/worktree, se demuestre:

```text
ONE_PRODUCTIVE_ROOT
ONE_PRODUCT_REQUEST_MODEL
ONE_CANONICAL_INGESTION
ONE_PRODUCTIVE_XLSX_READER
WORKBOOK_D1_D7_MANDATORY
D7_EVIDENCE_ONLY
ONE_PRODUCTIVE_SEMANTIC_STATE_MACHINE
P7_ONLY_GRAIN_AUTHORITY
P8_ONLY_COMPUTABILITY_AUTHORITY
F7_ONLY_JOIN_MATERIALIZATION
F8_ONLY_MATH_AUTHORITY
F9_ONLY_RESULT_PROJECTION
NO_LLM_MATH
NO_MEMORY_AUTO_REBIND
F13_NO_RECALCULATION
NO_SHEET1_FALLBACK
NO_PRODUCTIVE_LEGACY_SHIMS
NO_TRANSITIONAL_ALIASES
NO_PARALLEL_PRODUCT_PATHS
NO_AUTHORITY_COLLISIONS
MODULE_REGISTRY_COMPLETE
NO_UNDOCUMENTED_PROMPT_ARCHITECTURE
FULL_SUITE = 0 FAIL
REAL_WORKBOOK_E2E = PASS
CERTIFIED_SHA = exact
```

La arquitectura se evalúa `PASS/FAIL`; no por porcentaje de madurez.

## 25. Formato del veredicto final de auditoría

```text
SERVICE_1_INTEGRAL_HEALTH_VERDICT:

BASELINE_HEAD:
WORKTREE_DIRTY:

PRODUCTIVE_ROOTS:
PRODUCTIVE_WORKBOOK_READERS:
PRODUCTIVE_SEMANTIC_PATHS:
PRODUCTIVE_JOIN_AUTHORITIES:
PRODUCTIVE_MATH_AUTHORITIES:
PRODUCTIVE_RESULT_AUTHORITIES:
PRODUCTIVE_MEMORY_REENTRY_PATHS:

CANONICAL_MODULES:
NECESSARY_SUPPORT_MODULES:
TRANSITIONAL_MODULES:
LEGACY_PRODUCTIVE_MODULES:
DEAD_OBSOLETE_MODULES:
AUTHORITY_COLLISIONS:
PARALLEL_PATHS:
PATCHES:

TRANSITIONAL_ALIASES:
LEGACY_CALLERS:
SHEET1_PRODUCTIVE_OCCURRENCES:

REGISTRY_LIVE:
REGISTRY_REGISTERED:
REGISTRY_MISSING:
REGISTRY_WRONG:

PROMPTS_AUDITED:
PROMPT_ARCHITECTURE_DECISIONS_NOT_PRE_DOCUMENTED:
PATCH_INDUCING_PROMPTS:
LEGACY_PRESERVING_PROMPTS:
TEST_DRIVEN_RUNTIME_DISTORTION_PROMPTS:
NO_UNDOCUMENTED_PROMPT_ARCHITECTURE:

ONE_PRODUCTIVE_ROOT:
ONE_CANONICAL_INGESTION:
ONE_PRODUCTIVE_XLSX_READER:
WORKBOOK_D1_D7_MANDATORY:
D7_EVIDENCE_ONLY:
ONE_PRODUCTIVE_SEMANTIC_STATE_MACHINE:
D5_TABLE_SCOPE:
P7_ONLY_GRAIN_AUTHORITY:
P8_ONLY_COMPUTABILITY_AUTHORITY:
F7_ONLY_JOIN_MATERIALIZATION:
F8_ONLY_MATH_AUTHORITY:
NO_LLM_MATH:
NO_MEMORY_AUTO_REBIND:
F13_NO_RECALCULATION:
NO_SHEET1_FALLBACK:
MODULE_REGISTRY_COMPLETE:

FULL_SUITE:
REAL_WORKBOOK_E2E:

CRITICAL_FINDINGS:
HIGH_FINDINGS:
MEDIUM_FINDINGS:

WORKTREE_KEEP:
WORKTREE_REDESIGN:
WORKTREE_ABSORB:
WORKTREE_REVERT:
WORKTREE_DELETE:
WORKTREE_OFFLINE:

FINAL_CANONICAL_ARCHITECTURE:
RETIRE:
ABSORB:
KEEP:
REFACTOR:

RECOMMENDED_SANITIZATION_ORDER:

BLOCKERS:

COMMIT: NO
PUSH: NO
DEPLOY: NO
```

## 26. Regla de cierre de auditoría

La auditoría se considera cerrada sólo cuando existen simultáneamente:

1. topología física completa;
2. flujo de datos completo;
3. grafo de autoridades completo;
4. clasificación de deuda generacional;
5. clasificación total del worktree actual;
6. delta CURRENT → TARGET;
7. dependency graph de saneamiento;
8. construcción por ciclos propuesta;
9. evidencia de suites ejecutadas sin alterar tests;
10. auditoría de prompts relevantes y Prompt Decision Ledger;
11. decisiones arquitectónicas nuevas incorporadas a documentos rectores antes de cualquier implementación.

Hasta entonces:

```text
SERVICE_1_INTEGRAL_HEALTH = NOT_CERTIFIED
```


## 27. Protocolo dialéctico obligatorio para cerrar arquitectura final

Las decisiones arquitectónicas críticas de Servicio 1 no pueden cerrarse por una única IA ni por una sola lectura del repositorio.

Para este frente de convergencia, toda decisión que altere soberanía, contratos canónicos, rutas productivas, compatibilidad, identidad, semántica, matemática, provenance o límites del Product Root debe atravesar este ciclo:

```text
EVIDENCIA FÍSICA
→ TESIS ARQUITECTÓNICA FUNDADA (ChatGPT)
→ ANTÍTESIS / REFUTACIÓN INDEPENDIENTE (Qwen)
→ CONTRARRÉPLICA SOBRE EVIDENCIA
→ SÍNTESIS EXPLÍCITA
→ DECISIÓN DOCUMENTADA EN AUTORIDAD RECTORA
→ RECIÉN DESPUÉS IMPLEMENTACIÓN
```

### Reglas del intercambio

- Ningún agente puede usar cantidad de tests verdes como sustituto de coherencia arquitectónica.
- Qwen debe intentar refutar la tesis, no simplemente confirmarla ni proponer parches.
- ChatGPT debe responder a las objeciones con evidencia física o degradar la tesis a `NOT_PROVEN`.
- Una diferencia no se resuelve por mayoría ni por autoridad del modelo; se resuelve por contrato, invariantes y evidencia reproducible.
- Si dos diseños permanecen plausibles, la decisión queda `OPEN_ARCHITECTURAL_DECISION` y no se implementa.
- La síntesis no puede introducir una tercera arquitectura improvisada fuera de los documentos rectores.
- Cada cierre debe registrar: problema, tesis, antítesis, evidencia decisiva, síntesis, decisión final, consecuencias y gates.

### Decisiones que requieren este protocolo en el cierre actual

```text
MATH_AUTHORITY_SCOPE
SEMANTIC_PRODUCTIVE_PATH
PRODUCT_REQUEST_AND_ROOT_CONTRACT
CANONICAL_INGESTION_ALIAS_RETIREMENT
WORKBOOK_AND_SHEET_IDENTITY
D4_TO_F7_PROVENANCE_CONTRACT
SPECIALIZED_REQUEST_SCOPE
RESULTSET_REENTRY_BOUNDARY
```

### Gate

```text
DIALECTICAL_ARCHITECTURE_REVIEW_COMPLETE
```

Este gate sólo puede ser `PASS` cuando no queden decisiones críticas resueltas unilateralmente y todas las síntesis aceptadas hayan sido incorporadas a `SERVICE_1_CANONICAL_AXIS.md` y/o `SERVICE_1_ARCHITECTURE_LOCK.md`.

Mientras el gate sea `FAIL` o `NOT_PROVEN`:

```text
TARGET_ARCHITECTURE = OPEN
RECONSTRUCTION = FROZEN
```
