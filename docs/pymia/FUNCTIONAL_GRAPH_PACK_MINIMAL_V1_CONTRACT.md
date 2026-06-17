# FUNCTIONAL GRAPH PACK MINIMAL V1 CONTRACT

## Estado

```text
DRAFT_CONTRACT
DOCUMENTATION_ONLY
NO_CODE_AUTHORIZATION
NO_RUNTIME_AUTHORIZATION
NO_INTEGRATION_AUTHORIZATION
NO_PYMIA_LIVE_CHANGE
NO_OWNER_FACING_OUTPUT
NO_DIAGNOSTIC_AUTHORIZATION
```

## Propósito

Definir el primer contrato mínimo para un `FunctionalGraphPack` real, declarativo y versionado, consumible en el futuro por `FunctionalPackLoaderNavigatorV1` sin modificar el kernel de PymIA.

Este contrato no crea un pack activo productivo. Define la anatomía mínima que deberá tener un pack funcional para representar una ruta organizacional simple:

```text
signal_family
→ dominant_node
→ active_subgraph
→ formula_reference
→ current_unknown
→ minimal_evidence_candidate
→ reason_code
```

## Principio rector

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

Un `FunctionalGraphPack` es conocimiento declarativo externo. El kernel sólo puede cargarlo, validar su anatomía, navegar una ruta explícita y rechazarlo si viola contrato.

## Fuentes rectoras

```text
docs/adr/ADR-024-pack-system-foundation.md
docs/contracts/ROTOR_DIAGNOSTICO_PYME_GENERICO_V1.md
docs/contracts/PYME_BASE_ROUTING_PACK_CONTRACT_V1.md
docs/contracts/ORGANIZATIONAL_FUNCTION_GRAPH_CONTRACT_V1.md
docs/contracts/CASH_LIQUIDITY_GRAPH_SIMULATION_SPEC_V1.md
docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_CAPABILITYSPEC.md
docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_MODULECONTRACT.md
docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_TASKSPEC.md
```

## Pack mínimo objetivo

El primer pack funcional mínimo será:

```text
CASH_LIQUIDITY_GRAPH_MINIMAL_V1
```

Dominio funcional:

```text
liquidez operativa / brecha ventas-caja / cobranzas
```

Circuito PyME asociado:

```text
CIRCUIT_LIQUIDEZ_OPERATIVA
```

Signal family inicial:

```text
SALES_CASH_GAP
```

## Anatomía mínima obligatoria

Todo `FunctionalGraphPack` mínimo debe incluir:

```yaml
pack_id: string
pack_version: string
pack_kind: FunctionalGraphPack
status: DRAFT_PACK
circuit_id: string
nodes: list[FunctionalNode]
formula_references: list[FormulaReference]
signal_routes: list[SignalRoute]
unknowns: list[UnknownDefinition]
evidence_candidates: list[EvidenceCandidateDefinition]
boundary_policy: BoundaryPolicy
```

## Campos raíz

### pack_id

Identificador estable del pack.

Ejemplo:

```yaml
pack_id: CASH_LIQUIDITY_GRAPH_MINIMAL_V1
```

### pack_version

Versión semántica del pack.

Ejemplo:

```yaml
pack_version: 1.0.0
```

### pack_kind

Debe ser exactamente:

```yaml
pack_kind: FunctionalGraphPack
```

### status

Para V1 debe ser:

```yaml
status: DRAFT_PACK
```

Este estado impide tratarlo como pack productivo.

### circuit_id

Debe referenciar un circuito PyME declarado.

Ejemplo:

```yaml
circuit_id: CIRCUIT_LIQUIDEZ_OPERATIVA
```

## FunctionalNode

Cada nodo representa una función organizacional mínima, no un diagnóstico.

Anatomía:

```yaml
node_id: string
node_kind: string
label: string
allowed_roles: list[string]
```

Campos permitidos:

```text
node_id
node_kind
label
allowed_roles
```

`node_id` debe ser estable y usable por rutas internas.

`node_kind` puede ser:

```text
functional_area
operational_variable
financial_variable
commercial_variable
```

`allowed_roles` puede incluir:

```text
dominant_node
subgraph_node
context_node
```

## FormulaReference

Una fórmula se declara como referencia externa, no como cálculo.

Anatomía:

```yaml
formula_id: string
formula_family: string
formula_role: string
execution_policy: REFERENCE_ONLY
```

Regla obligatoria:

```yaml
execution_policy: REFERENCE_ONLY
```

El pack no puede contener:

```text
- expresión matemática ejecutable
- código
- pseudocódigo ejecutable
- función Python
- SQL
- fórmula spreadsheet activa
```

## UnknownDefinition

Una incógnita representa el dato funcional que falta para avanzar una ruta.

Anatomía:

```yaml
unknown_id: string
unknown_kind: string
label: string
resolves_formula_reference: string
```

`unknown_id` debe ser único dentro del pack.

`resolves_formula_reference` debe apuntar a una `formula_reference` existente.

## EvidenceCandidateDefinition

Una evidencia candidata representa el dato mínimo que podría solicitarse o buscarse en una capa posterior.

Anatomía:

```yaml
evidence_id: string
evidence_kind: string
label: string
supports_unknown: string
promotion_policy: CANDIDATE_ONLY
```

Regla obligatoria:

```yaml
promotion_policy: CANDIDATE_ONLY
```

Esto impide confundir evidencia candidata con evidencia suficiente.

## SignalRoute

La ruta es el núcleo navegable del pack.

Anatomía:

```yaml
signal_family: string
dominant_node: string
active_subgraph: list[string]
formula_reference: string
current_unknown: string
minimal_evidence_candidate: list[string]
reason_code: string
route_policy: SINGLE_CYCLE_ONLY
```

### signal_family

Debe ser un identificador normalizado. No puede ser texto libre.

Ejemplo:

```yaml
signal_family: SALES_CASH_GAP
```

### dominant_node

Regla obligatoria:

```text
dominant_node no es diagnóstico.
```

`dominant_node` significa únicamente nodo seleccionado por lookup explícito de ruta dentro del pack validado.

No expresa:

```text
- prioridad de negocio
- severidad
- patología dominante
- diagnóstico
- tratamiento
- decisión autónoma del sistema
```

### active_subgraph

Debe ser una lista no vacía de nodos existentes.

No representa distancia funcional calculada. Es un subgrafo declarado.

### formula_reference

Debe apuntar a una fórmula existente dentro de `formula_references`.

No ejecuta cálculo.

### current_unknown

Debe ser una única string.

Prohibido:

```yaml
current_unknown:
  - unknown_a
  - unknown_b
```

### minimal_evidence_candidate

Debe ser una lista no vacía de evidencias candidatas existentes.

No certifica suficiencia.

### reason_code

Debe explicar la razón estructural de la ruta en código estable, no en narrativa owner-facing.

Ejemplo:

```yaml
reason_code: SALES_CASH_SYMPTOM_REQUIRES_COLLECTIONS_UNKNOWN_FIRST
```

### route_policy

Para V1 debe ser:

```yaml
route_policy: SINGLE_CYCLE_ONLY
```

## BoundaryPolicy

Todo pack mínimo debe declarar explícitamente sus límites.

Anatomía:

```yaml
boundary_policy:
  allows_formula_execution: false
  allows_pathology_diagnosis: false
  allows_treatment_selection: false
  allows_owner_facing_output: false
  allows_runtime_execution: false
  allows_pymia_live_integration: false
  allows_multi_cycle_navigation: false
  allows_llm_inference: false
  allows_fuzzy_matching: false
  allows_scoring: false
  allows_functional_distance_calculation: false
```

Cualquier valor `true` en esos campos bloquea el pack para V1.

## Ejemplo contractual mínimo

Este ejemplo es documental. No es pack activo.

```yaml
pack_id: CASH_LIQUIDITY_GRAPH_MINIMAL_V1
pack_version: 1.0.0
pack_kind: FunctionalGraphPack
status: DRAFT_PACK
circuit_id: CIRCUIT_LIQUIDEZ_OPERATIVA

nodes:
  - node_id: sales
    node_kind: commercial_variable
    label: ventas
    allowed_roles: [subgraph_node]
  - node_id: collections
    node_kind: financial_variable
    label: cobranzas
    allowed_roles: [subgraph_node]
  - node_id: cash
    node_kind: financial_variable
    label: caja
    allowed_roles: [dominant_node, subgraph_node]

formula_references:
  - formula_id: ratio_cobranza
    formula_family: liquidity
    formula_role: collections_efficiency_reference
    execution_policy: REFERENCE_ONLY

unknowns:
  - unknown_id: cobranzas_del_periodo
    unknown_kind: monetary_period_value
    label: cobranzas del período
    resolves_formula_reference: ratio_cobranza

evidence_candidates:
  - evidence_id: cobranzas_del_periodo
    evidence_kind: monetary_period_value
    label: total cobrado en el período
    supports_unknown: cobranzas_del_periodo
    promotion_policy: CANDIDATE_ONLY

signal_routes:
  - signal_family: SALES_CASH_GAP
    dominant_node: cash
    active_subgraph: [sales, collections, cash]
    formula_reference: ratio_cobranza
    current_unknown: cobranzas_del_periodo
    minimal_evidence_candidate: [cobranzas_del_periodo]
    reason_code: SALES_CASH_SYMPTOM_REQUIRES_COLLECTIONS_UNKNOWN_FIRST
    route_policy: SINGLE_CYCLE_ONLY

boundary_policy:
  allows_formula_execution: false
  allows_pathology_diagnosis: false
  allows_treatment_selection: false
  allows_owner_facing_output: false
  allows_runtime_execution: false
  allows_pymia_live_integration: false
  allows_multi_cycle_navigation: false
  allows_llm_inference: false
  allows_fuzzy_matching: false
  allows_scoring: false
  allows_functional_distance_calculation: false
```

## Reglas de validación futura

Un pack mínimo será válido sólo si:

```text
- tiene pack_id;
- tiene pack_version;
- tiene pack_kind = FunctionalGraphPack;
- tiene status = DRAFT_PACK;
- tiene circuit_id declarado;
- tiene nodes no vacío;
- tiene formula_references no vacío;
- tiene unknowns no vacío;
- tiene evidence_candidates no vacío;
- tiene signal_routes no vacío;
- cada route tiene signal_family único;
- cada dominant_node existe en nodes;
- cada active_subgraph referencia nodos existentes;
- cada formula_reference existe;
- cada current_unknown existe;
- current_unknown es string única;
- cada minimal_evidence_candidate existe;
- boundary_policy existe;
- todos los campos restrictivos de boundary_policy son false.
```

## Reglas de rechazo futuro

Rechazar pack si:

```text
- contiene código ejecutable;
- contiene fórmula ejecutable;
- contiene diagnóstico;
- contiene patología interpretada;
- contiene tratamiento;
- contiene owner-facing output;
- contiene prompts LLM;
- contiene fuzzy matching;
- contiene scoring;
- contiene distancia funcional calculada;
- contiene rutas multi-ciclo;
- habilita PymIA-Live;
- habilita runtime;
- promueve evidencia candidata a evidencia suficiente;
- usa texto libre como signal_family;
- declara más de un current_unknown por ruta.
```

## Relación con FunctionalPackLoaderNavigatorV1

Este contrato debe ser compatible con:

```python
validate_functional_pack(pack: dict) -> dict
navigate_single_cycle(signal: dict, pack: dict) -> dict
```

Pero no modifica esas funciones.

Cualquier adaptación futura del navigator requerirá:

```text
- TaskSpec propio;
- tests focales;
- auditoría;
- commit separado.
```

## Relación con EvidenceSufficiency

Este contrato no certifica evidencia suficiente.

Sólo declara:

```text
minimal_evidence_candidate
```

La promoción de candidato a evidencia suficiente pertenece a otra capa.

## Relación con FormulaEngine

Este contrato no ejecuta fórmulas.

Sólo declara:

```text
formula_reference
```

La ejecución pertenece a FormulaEngine o servicio equivalente ya existente.

## Relación con owner-facing output

Este contrato no genera texto para el dueño.

No contiene:

```text
- preguntas humanizadas;
- recomendaciones;
- diagnóstico narrativo;
- plan de acción;
- mensaje final.
```

## Criterios de aceptación del contrato

```text
- define anatomía mínima del pack;
- preserva conocimiento enchufable;
- mantiene kernel estable;
- no autoriza código;
- no autoriza runtime;
- no autoriza integración;
- no autoriza PymIA-Live;
- no autoriza owner-facing output;
- no autoriza diagnóstico;
- es compatible con FunctionalPackLoaderNavigatorV1;
- permite crear luego un fixture documental mínimo.
```

## Próximo paso metodológico

```text
AUDITORIA_FUNCTIONAL_GRAPH_PACK_MINIMAL_V1_CONTRACT
```

Sólo si este contrato recibe PASS podrá crearse un fixture documental mínimo del pack.
