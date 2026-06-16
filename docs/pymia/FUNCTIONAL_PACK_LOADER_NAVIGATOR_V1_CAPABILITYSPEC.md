# FUNCTIONAL PACK LOADER NAVIGATOR V1 CAPABILITYSPEC

## Estado

```text
DRAFT_CAPABILITYSPEC
READY_FROM_DOCUMENTAL_AUDIT
NO_RUNTIME_CHANGE
NO_CODE_AUTHORIZATION
NO_IMPLEMENTATION_AUTHORIZATION
NO_TEST_AUTHORIZATION
MODULECONTRACT_REQUIRED_BEFORE_CODE
```

## Propósito

Definir la capacidad mínima futura para cargar, validar y navegar un pack funcional declarativo de PyME en un único ciclo controlado.

La capacidad nace después del bloque documental:

```text
ROTOR_DIAGNOSTICO_PYME_GENERICO_V1
PYME_BASE_ROUTING_PACK_CONTRACT_V1
ORGANIZATIONAL_FUNCTION_GRAPH_CONTRACT_V1
CASH_LIQUIDITY_GRAPH_SIMULATION_SPEC_V1
DOCUMENTATION_INDEX governance entry
```

La auditoría de madurez del frente dictaminó:

```text
READY_FOR_CAPABILITYSPEC
```

## Alcance estricto V1

La capacidad V1 se limita a:

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
- distancia funcional algorítmica;
- confidence_label;
- structural_coverage_label;
- selección autónoma multi-ciclo;
- diferimiento automático inteligente;
- ranking de incógnitas;
- scoring;
- cálculo matemático;
- diagnóstico;
- interpretación patológica;
- tratamiento;
- owner-facing output;
- runtime productivo;
- parser universal de packs;
- edición o creación de packs;
- integración con PymIA-Live;
- integración con FormulaEngine;
- integración con EvidenceSufficiency;
- integración con QuestionAlignmentGate;
- integración con PathologyInterpreter;
- integración con OwnerFacingReport.
```

## Fuentes rectoras

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

## Problema que resuelve

Actualmente existen contratos documentales que describen:

```text
- un rotor declarativo;
- un routing pack base;
- un grafo funcional organizacional;
- una simulación del micrografo de liquidez.
```

Pero todavía no existe una capacidad formal que diga cuál sería el primer corte implementable sin invadir el kernel, sin convertir el grafo en meta-orquestador y sin transformar conocimiento declarativo en lógica hardcodeada.

Esta CapabilitySpec define ese primer corte futuro.

## Capacidad autorizable futura

```text
FunctionalPackLoaderNavigatorV1
```

Capacidad compuesta por dos responsabilidades mínimas:

```text
1. FunctionalPackLoader
2. SingleCycleFunctionalNavigator
```

### FunctionalPackLoader

Responsabilidad conceptual:

```text
Cargar un pack funcional declarativo ya existente y validar su anatomía mínima.
```

Debe validar sólo estructura mínima:

```text
pack_id
pack_version
nodes
formula_references
signal_routes
unknowns
evidence_candidates
```

No debe validar:

```text
- veracidad económica;
- suficiencia de evidencia;
- resultado de fórmulas;
- patologías;
- tratamientos;
- lenguaje owner-facing;
- taxonomía sectorial completa;
- distancia funcional compleja.
```

### SingleCycleFunctionalNavigator

Responsabilidad conceptual:

```text
Tomar una señal normalizada y un pack validado, activar un subgrafo mínimo y declarar una sola incógnita candidata.
```

Debe emitir un estado estructurado.

No debe ejecutar flujo conversacional, no debe repreguntar al dueño y no debe renderizar mensajes.

## Input conceptual mínimo

```yaml
normalized_signal:
  signal_id: string
  signal_family: string
  source: string
  text_ref: string | null

functional_pack:
  pack_id: string
  pack_version: string
  nodes: list
  formula_references: list
  signal_routes: list
  unknowns: list
  evidence_candidates: list
```

## Output conceptual mínimo

```yaml
status: string
pack_id: string
pack_version: string
signal_id: string
dominant_node: string | null
active_subgraph: list[string]
current_formula_reference: string | null
current_unknown: string | null
minimal_evidence_candidate: list[string]
reason_code: string
boundary_check:
  loaded_pack: true
  validated_anatomy: true
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

`PACK_LOADED` y `PACK_VALIDATED` son estados de resultado documental de la capacidad, no fases de workflow, no estados persistentes de runtime y no pasos de orquestación.

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

## Reglas de capacidad

### Regla 0 — dominant_node no es diagnóstico

`dominant_node` significa nodo seleccionado por lookup explícito de ruta dentro del pack validado.

No expresa prioridad de negocio, severidad, diagnóstico, patología dominante ni decisión autónoma del sistema.

### Regla 1 — Pack externo

El pack funcional debe entrar como dato declarativo externo.

Prohibido hardcodear en Python:

```text
- nodos funcionales;
- rutas;
- fórmulas;
- incógnitas;
- evidencia candidata;
- patologías;
- tratamientos;
- sectores.
```

### Regla 2 — Validación anatómica mínima

La validación V1 sólo confirma que el pack tiene anatomía mínima navegable.

No confirma que el pack sea económicamente verdadero, suficiente o completo.

### Regla 3 — Señal normalizada obligatoria

El navegador no procesa texto libre.

Debe recibir una señal ya normalizada por una frontera anterior.

Si la señal es ambigua o abierta, debe responder:

```text
NEEDS_NORMALIZED_SIGNAL
```

### Regla 4 — Un solo ciclo

V1 sólo permite un ciclo:

```text
normalized signal
→ route lookup
→ dominant node
→ active subgraph mínimo
→ formula reference
→ current unknown
→ minimal evidence candidate
→ state
```

No permite navegación multi-ciclo.

### Regla 5 — Una sola incógnita

Debe existir una sola `current_unknown` candidata por salida válida.

Si hay más de una candidata dominante, el estado debe ser bloqueado.

### Regla 6 — Evidencia candidata no es suficiencia

`minimal_evidence_candidate` no certifica suficiencia.

Sólo declara qué evidencia podría despejar la incógnita candidata.

### Regla 7 — Sin distancia funcional V1

La V1 no implementa algoritmo de distancia funcional.

Sólo puede activar el subgrafo explícitamente declarado en la ruta del pack.

### Regla 8 — Sin confianza estructural V1

La V1 no emite `confidence_label`, `structural_coverage_label` ni scoring equivalente.

Sólo emite estados discretos y reason codes.

### Regla 9 — Fail-closed

Ante falta de nodo, ruta, fórmula referenciada, incógnita o evidencia candidata, la capacidad debe bloquear.

No debe inventar defaults.

### Regla 10 — Sin salida owner-facing

La capacidad no redacta preguntas, reportes ni mensajes para el dueño.

Cualquier salida owner-facing pertenece a fronteras posteriores existentes.

## Anatomy mínima de pack funcional

```yaml
pack_id: CASH_LIQUIDITY_GRAPH_V1
pack_version: 1.0.0
nodes:
  - node_id: cash
  - node_id: sales
  - node_id: collections
signal_routes:
  - signal_family: SALES_CASH_GAP
    dominant_node: cash
    active_subgraph:
      - sales
      - collections
      - cash
    formula_reference: ratio_cobranza
    current_unknown: cobranzas_del_periodo
    minimal_evidence_candidate:
      - cobranzas_del_periodo
formula_references:
  - formula_id: ratio_cobranza
unknowns:
  - unknown_id: cobranzas_del_periodo
evidence_candidates:
  - evidence_id: cobranzas_del_periodo
```

Este ejemplo no es un pack activo. Es una anatomía mínima para orientar el futuro ModuleContract.

## Acceptance criteria futuros

Una futura implementación sólo podrá considerarse aceptable si:

```text
- carga un pack declarativo desde input controlado;
- valida anatomía mínima;
- rechaza packs inválidos;
- recibe señal normalizada;
- no interpreta texto libre;
- activa sólo subgrafo declarado;
- emite una sola current_unknown;
- emite minimal_evidence_candidate sin certificar suficiencia;
- no calcula fórmula;
- no diagnostica;
- no interpreta patología;
- no selecciona tratamiento;
- no renderiza owner-facing output;
- no ejecuta runtime;
- no muta el pack;
- no usa distancia funcional algorítmica;
- no usa scoring ni confidence label;
- deja boundary_check explícito.
```

## Rejection criteria futuros

La implementación deberá rechazarse si:

```text
- hardcodea nodos, rutas, incógnitas o evidencia;
- calcula una fórmula;
- llama a FormulaEngine;
- llama a EvidenceSufficiency;
- llama a QuestionAlignmentGate;
- llama a PathologyInterpreter;
- llama a OwnerFacingReport;
- procesa texto libre;
- elige entre múltiples incógnitas con scoring;
- implementa distancia funcional;
- genera confidence label;
- interpreta patología;
- propone tratamiento;
- produce texto visible al dueño;
- abre navegación multi-ciclo;
- usa defaults silenciosos;
- crea o modifica packs.
```

## Frontera con módulos existentes

| Módulo / frontera | Relación V1 |
|---|---|
| Rotor | Puede aportar signal_family o ruta inicial normalizada. No es reemplazado. |
| Routing Pack | Fuente declarativa. No es ejecutado como lógica hardcodeada. |
| FormulaEngine | No se invoca. Fórmulas sólo son referencias. |
| EvidenceSufficiency | No se invoca. Evidencia candidata no certifica suficiencia. |
| QuestionAlignmentGate | No se invoca. Texto libre debe venir normalizado antes. |
| PathologyInterpreter | No se invoca. No hay interpretación patológica. |
| OwnerFacingReport | No se invoca. No hay salida visible al dueño. |
| PymIA-Live | No se modifica. |

## Próximo paso metodológico

```text
AUDITORIA_FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_CAPABILITYSPEC
```

Sólo si esta CapabilitySpec recibe PASS, podrá redactarse un ModuleContract futuro.

Esta CapabilitySpec no autoriza código, tests, schemas, runtime, modificación de PymIA-Live, integración con servicios existentes ni creación de packs activos.
