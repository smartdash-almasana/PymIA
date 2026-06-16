# FUNCTIONAL PACK LOADER NAVIGATOR V1 MODULECONTRACT

## Estado

```text
DRAFT_MODULECONTRACT
DERIVED_FROM_FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_CAPABILITYSPEC
NO_RUNTIME_CHANGE
NO_CODE_AUTHORIZATION
NO_IMPLEMENTATION_AUTHORIZATION
NO_TEST_AUTHORIZATION
NO_SCHEMA_AUTHORIZATION
TASKSPEC_REQUIRED_BEFORE_CODE
```

## Propósito

Definir la frontera modular futura de `FunctionalPackLoaderNavigatorV1` como módulo puro para cargar, validar y navegar un pack funcional declarativo de PyME en un único ciclo controlado.

Este ModuleContract no implementa la capacidad. Sólo fija responsabilidades, entradas, salidas, errores, dependencias permitidas/prohibidas y reglas de frontera antes de cualquier TaskSpec o código.

## Fuente autorizante

```text
docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_CAPABILITYSPEC.md
```

Fuentes rectoras adicionales:

```text
AGENTS.md
docs/DOCUMENTATION_INDEX.md
docs/adr/ADR-024-pack-system-foundation.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
docs/contracts/ROTOR_DIAGNOSTICO_PYME_GENERICO_V1.md
docs/contracts/PYME_BASE_ROUTING_PACK_CONTRACT_V1.md
docs/contracts/ORGANIZATIONAL_FUNCTION_GRAPH_CONTRACT_V1.md
docs/contracts/CASH_LIQUIDITY_GRAPH_SIMULATION_SPEC_V1.md
```

## Nombre lógico del módulo futuro

```text
FunctionalPackLoaderNavigatorV1
```

Nombre físico sugerido, no autorizado todavía:

```text
pymia/smartpyme/functional_pack_loader_navigator.py
```

El nombre físico es sólo referencia documental. Este contrato no autoriza crear el archivo Python.

## Alcance V1

El módulo futuro queda limitado a:

```text
load pack
validate anatomy
receive normalized signal
activate subgraph
declare candidate unknown
emit state
```

No incluye:

```text
- código en este hito;
- tests en este hito;
- schemas Pydantic;
- runtime;
- integración con PymIA-Live;
- parser universal de packs;
- edición o creación de packs;
- distancia funcional algorítmica;
- confidence_label;
- structural_coverage_label;
- scoring;
- ranking;
- navegación multi-ciclo;
- cálculo de fórmulas;
- diagnóstico;
- interpretación patológica;
- tratamiento;
- salida owner-facing;
- llamadas a servicios existentes del diagnóstico.
```

## Responsabilidades del módulo futuro

### Regla 0 — dominant_node no es diagnóstico

`dominant_node` significa nodo seleccionado por lookup explícito de ruta dentro del pack validado.

No expresa prioridad de negocio, severidad, diagnóstico, patología dominante ni decisión autónoma del sistema.

### 1. Cargar pack declarativo recibido como input

El módulo podrá recibir una estructura ya cargada desde una frontera externa futura.

En V1 documental, `load pack` significa aceptar un objeto/dict declarativo controlado, no leer archivos, no consultar base de datos y no invocar red.

### 2. Validar anatomía mínima

Debe validar que existan las secciones mínimas:

```text
pack_id
pack_version
nodes
formula_references
signal_routes
unknowns
evidence_candidates
```

Debe bloquear si falta alguna sección obligatoria.

### 3. Recibir señal normalizada

Debe recibir una señal ya normalizada.

No debe interpretar texto libre.

### 4. Resolver ruta por lookup explícito

Debe buscar una única ruta por `signal_family` dentro de `signal_routes`.

Si no existe ruta para la `signal_family`, debe bloquear.

Si existe más de una ruta para la misma `signal_family`, debe bloquear por ambigüedad contractual.

No debe inferir rutas por similitud, embeddings, LLM, heurística blanda ni scoring.

### 5. Activar subgrafo declarado

Debe copiar el `active_subgraph` declarado en la ruta encontrada.

No debe calcular distancia funcional.

### 6. Declarar una incógnita candidata

Debe emitir una sola `current_unknown` declarada por la ruta encontrada.

Si la ruta no tiene incógnita, debe bloquear.

Si la ruta declara más de una incógnita dominante, debe bloquear.

### 7. Emitir estado estructurado

Debe emitir un estado técnico estructurado, no texto visible para el dueño.

## Entradas conceptuales

### NormalizedSignal

```yaml
signal_id: string
signal_family: string
source: string
text_ref: string | null
metadata: dict | null
```

Reglas:

```text
- signal_id obligatorio;
- signal_family obligatorio;
- source obligatorio;
- text_ref opcional;
- metadata opcional;
- no se permite usar text_ref como texto libre para inferir rutas.
```

### FunctionalPack

```yaml
pack_id: string
pack_version: string
nodes: list[FunctionalNode]
formula_references: list[FormulaReference]
signal_routes: list[SignalRoute]
unknowns: list[UnknownDefinition]
evidence_candidates: list[EvidenceCandidateDefinition]
```

## Estructuras internas conceptuales

### FunctionalNode

```yaml
node_id: string
label: string | null
```

Reglas:

```text
- node_id obligatorio;
- label opcional;
- label no se usa para inferencia.
```

### FormulaReference

```yaml
formula_id: string
```

Reglas:

```text
- formula_id obligatorio;
- no se ejecuta;
- no se valida contra FormulaEngine;
- sólo se verifica existencia declarativa dentro del pack.
```

### UnknownDefinition

```yaml
unknown_id: string
```

Reglas:

```text
- unknown_id obligatorio;
- no se resuelve;
- no se calcula;
- no se interpreta como diagnóstico.
```

### EvidenceCandidateDefinition

```yaml
evidence_id: string
```

Reglas:

```text
- evidence_id obligatorio;
- no certifica suficiencia;
- no se convierte en EvidenceRecord;
- no se solicita directamente al dueño.
```

### SignalRoute

```yaml
signal_family: string
dominant_node: string
active_subgraph: list[string]
formula_reference: string
current_unknown: string
minimal_evidence_candidate: list[string]
reason_code: string
```

Reglas:

```text
- signal_family obligatorio;
- dominant_node obligatorio;
- active_subgraph obligatorio y no vacío;
- formula_reference obligatorio;
- current_unknown obligatorio y único;
- minimal_evidence_candidate obligatorio y no vacío;
- reason_code obligatorio;
- todos los node ids del active_subgraph deben existir en nodes;
- dominant_node debe existir en nodes;
- formula_reference debe existir en formula_references;
- current_unknown debe existir en unknowns;
- cada evidence id debe existir en evidence_candidates.
```

## Salida conceptual

### FunctionalNavigationState

```yaml
status: string
pack_id: string | null
pack_version: string | null
signal_id: string | null
dominant_node: string | null
active_subgraph: list[string]
current_formula_reference: string | null
current_unknown: string | null
minimal_evidence_candidate: list[string]
reason_code: string
boundary_check:
  loaded_pack: bool
  validated_anatomy: bool
  calculated_formula: false
  diagnosed_pathology: false
  interpreted_pathology: false
  certified_evidence_sufficiency: false
  selected_treatment: false
  rendered_owner_message: false
  executed_runtime: false
  became_orchestrator: false
```

## Estados permitidos

```text
PACK_LOADED
PACK_VALIDATED
SINGLE_CYCLE_ROUTE_CANDIDATE
NEEDS_EVIDENCE
NEEDS_NORMALIZED_SIGNAL
BLOCKED_BY_INVALID_PACK
BLOCKED_BY_MISSING_NODE
BLOCKED_BY_MISSING_ROUTE
BLOCKED_BY_MISSING_UNKNOWN
BLOCKED_BY_MISSING_EVIDENCE_CANDIDATE
BLOCKED_BY_CONTRACT_BOUNDARY
```

`PACK_LOADED` y `PACK_VALIDATED` son estados de resultado técnico del módulo futuro. No son fases persistentes de runtime, no workflow y no orquestación.

## Estados prohibidos

```text
FORMULA_EXECUTED
EVIDENCE_SUFFICIENT_CERTIFIED
PATHOLOGY_INTERPRETED
PATHOLOGY_CONFIRMED
TREATMENT_SELECTED
OWNER_MESSAGE_RENDERED
RUNTIME_EXECUTED
MULTI_CYCLE_NAVIGATION_COMPLETED
```

## Funciones conceptuales futuras

Estas firmas son contractuales. No autorizan implementación.

```python
validate_functional_pack(pack: dict) -> FunctionalPackValidationResult
navigate_single_cycle(signal: dict, pack: dict) -> FunctionalNavigationState
```

### validate_functional_pack

Responsabilidad:

```text
Validar anatomía mínima y referencias internas del pack.
```

Debe devolver:

```text
PACK_VALIDATED
```

O bloquear con alguno de:

```text
BLOCKED_BY_INVALID_PACK
BLOCKED_BY_MISSING_NODE
BLOCKED_BY_MISSING_ROUTE
BLOCKED_BY_MISSING_UNKNOWN
BLOCKED_BY_MISSING_EVIDENCE_CANDIDATE
BLOCKED_BY_CONTRACT_BOUNDARY
```

No debe navegar señal.

### navigate_single_cycle

Responsabilidad:

```text
Dado un pack válido y una señal normalizada, emitir una salida de navegación de un único ciclo.
```

Debe devolver:

```text
SINGLE_CYCLE_ROUTE_CANDIDATE
```

O bloquear con:

```text
NEEDS_NORMALIZED_SIGNAL
BLOCKED_BY_MISSING_ROUTE
BLOCKED_BY_CONTRACT_BOUNDARY
```

No debe validar económicamente el caso.

## Imports permitidos futuros

Sólo podrán permitirse dependencias estándar y contratos puros si el futuro TaskSpec lo autoriza.

Permitidos conceptualmente:

```text
typing
dataclasses
```

Permitidos sólo si el TaskSpec futuro lo justifica:

```text
pydantic
```

Pero este ModuleContract no autoriza schemas Pydantic.

## Imports prohibidos futuros

```text
pymia.services.formula_engine_service
pymia.diagnostic_core
pymia.audit_result.core_delivery_bridge
pymia.smartpyme.owner_questions_builder
pymia.smartpyme.owner_answers_evaluator
pymia.smartpyme.owner_action_pipeline
pymia.orchestration.graph
pymia.contracts.owner_questions
pymia.contracts.owner_answers
pymia.contracts.owner_evaluation
pymia.contracts.owner_actions
pymia.contracts.owner_resolved_actions
pymia.services.pathology_knowledge_tank
```

También prohibido:

```text
requests
httpx
openai
langchain
langgraph
subprocess
sqlite3
sqlalchemy
pandas
polars
```

## Reglas de error

El módulo futuro debe fallar cerrado.

Prohibido:

```text
- defaults silenciosos;
- rutas fallback por similitud;
- selección de primera ruta disponible;
- corrección automática de ids;
- creación automática de nodos;
- inferencia por label;
- inferencia por texto_ref;
- uso de LLM;
- scoring.
```

## Boundary checks obligatorios

Toda salida válida o bloqueada debe preservar:

```yaml
calculated_formula: false
diagnosed_pathology: false
interpreted_pathology: false
certified_evidence_sufficiency: false
selected_treatment: false
rendered_owner_message: false
executed_runtime: false
became_orchestrator: false
```

## Relación con módulos existentes

| Módulo | Relación |
|---|---|
| Rotor | Puede aportar una señal normalizada o familia de señal. No es reemplazado. |
| Routing Pack | Es conocimiento declarativo consumido como dato. No se hardcodea. |
| FormulaEngine | No se invoca. Fórmulas sólo son ids declarativos. |
| EvidenceSufficiency | No se invoca. Evidencia candidata no certifica suficiencia. |
| QuestionAlignmentGate | No se invoca. La señal debe venir normalizada antes. |
| PathologyInterpreter | No se invoca. No hay patologías interpretadas. |
| OwnerFacingReport | No se invoca. No hay texto visible al dueño. |
| PymIA-Live | No se modifica. |

## Acceptance criteria futuros

El futuro módulo será aceptable sólo si:

```text
- implementa validate_functional_pack como función pura;
- implementa navigate_single_cycle como función pura;
- no tiene side effects;
- no lee archivos;
- no escribe archivos;
- no invoca red;
- no usa base de datos;
- no llama servicios diagnósticos;
- no procesa texto libre;
- valida referencias internas;
- bloquea rutas ambiguas o inexistentes;
- emite una sola current_unknown;
- conserva boundary_check;
- no calcula;
- no diagnostica;
- no renderiza.
```

## Rejection criteria futuros

Debe rechazarse si:

```text
- hardcodea el pack CASH_LIQUIDITY_GRAPH_V1;
- hardcodea nodos de negocio;
- importa FormulaEngine;
- importa EvidenceSufficiency;
- importa QAG;
- importa PathologyInterpreter;
- importa OwnerFacingReport;
- usa embeddings, LLM o fuzzy matching;
- implementa distancia funcional;
- emite confidence/scoring;
- soporta multi-ciclo;
- muta el pack;
- solicita evidencia al dueño;
- genera mensajes owner-facing;
- crea EvidenceRecord;
- promueve evidencia candidata a evidencia suficiente.
```

## Próximo paso metodológico

```text
AUDITORIA_FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_MODULECONTRACT
```

Sólo si este ModuleContract recibe PASS podrá redactarse un TaskSpec futuro.

Este ModuleContract no autoriza código, tests, schemas, runtime, modificación de PymIA-Live, creación de packs activos ni integración con módulos existentes.
