# FUNCTIONAL PACK LOADER NAVIGATOR V1 TASKSPEC

## Estado

```text
DRAFT_TASKSPEC
DERIVED_FROM_FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_MODULECONTRACT
IMPLEMENTATION_AUTHORIZATION_CANDIDATE
NO_RUNTIME_CHANGE
NO_PYMIA_LIVE_CHANGE
NO_INTEGRATION_AUTHORIZATION
NO_SCHEMA_AUTHORIZATION
NO_PRODUCTION_AUTHORIZATION
```

## Propósito

Definir el hito implementativo mínimo para materializar `FunctionalPackLoaderNavigatorV1` como módulo puro, local, sin IO, sin runtime, sin integración y sin efectos colaterales.

Este TaskSpec autoriza únicamente la futura creación de un módulo puro y sus tests focales, si es aprobado por auditoría.

No autoriza ejecutar el hito en este documento.

## Fuente autorizante

```text
docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_CAPABILITYSPEC.md
docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_MODULECONTRACT.md
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

## Objetivo implementativo mínimo futuro

Crear una implementación pura de:

```text
FunctionalPackLoaderNavigatorV1
```

con dos funciones:

```python
validate_functional_pack(pack: dict) -> dict
navigate_single_cycle(signal: dict, pack: dict) -> dict
```

La implementación futura debe ser determinística, sin IO y sin imports de servicios PymIA existentes.

## Archivos autorizables futuros

Sólo estos archivos podrían crearse en el hito implementativo futuro:

```text
pymia/smartpyme/functional_pack_loader_navigator.py
tests/smartpyme/test_functional_pack_loader_navigator.py
```

No se autorizan otros archivos.

## Archivos prohibidos

No modificar:

```text
pymia/cli/vertical_slice.py
pymia/orchestration/graph.py
pymia/audit_result/core_delivery_bridge.py
pymia/diagnostic_core/
pymia/services/
pymia/contracts/owner_questions.py
pymia/contracts/owner_answers.py
pymia/contracts/owner_evaluation.py
pymia/contracts/owner_actions.py
pymia/contracts/owner_resolved_actions.py
PymIA-Live/
docs/contracts/
docs/DOCUMENTATION_INDEX.md
```

No crear:

```text
schemas Pydantic
JSON schemas
YAML packs activos
runtime loaders
CLI commands
FastAPI endpoints
Telegram handlers
Hermes tools
MCP tools
PDF renderers
DB tables
```

## Alcance funcional autorizado futuro

### Regla 0 — dominant_node no es diagnóstico

`dominant_node` significa nodo seleccionado por lookup explícito de ruta dentro del pack validado.

No expresa prioridad de negocio, severidad, diagnóstico, patología dominante ni decisión autónoma del sistema.

### A. validate_functional_pack

Debe:

```text
- aceptar un dict;
- validar presencia de pack_id;
- validar presencia de pack_version;
- validar nodes;
- validar formula_references;
- validar signal_routes;
- validar unknowns;
- validar evidence_candidates;
- validar que cada route tenga signal_family;
- validar que cada route tenga dominant_node;
- validar que cada route tenga active_subgraph no vacío;
- validar que cada route tenga formula_reference;
- validar que cada route tenga current_unknown;
- validar que current_unknown sea string único, no lista;
- validar que minimal_evidence_candidate sea lista no vacía;
- validar que reason_code exista;
- validar referencias internas;
- bloquear signal_family duplicada;
- devolver estado PACK_VALIDATED si todo es válido;
- devolver estado bloqueado si falla.
```

No debe:

```text
- leer archivos;
- escribir archivos;
- mutar el pack;
- llamar servicios;
- validar economía real;
- calcular fórmulas;
- inferir nodos;
- inferir rutas;
- usar labels para lógica;
- usar text_ref;
- usar LLM;
- usar fuzzy matching;
- usar scoring;
- usar distancia funcional.
```

### B. navigate_single_cycle

Debe:

```text
- aceptar signal dict;
- aceptar pack dict;
- validar o reutilizar validación del pack sin side effects;
- exigir signal_id;
- exigir signal_family;
- exigir source;
- rechazar señal sin signal_family;
- buscar exactamente una route por signal_family;
- bloquear si no existe route;
- bloquear si existe más de una route;
- copiar dominant_node declarado;
- copiar active_subgraph declarado;
- copiar formula_reference como current_formula_reference;
- copiar current_unknown declarado;
- copiar minimal_evidence_candidate declarado;
- emitir status SINGLE_CYCLE_ROUTE_CANDIDATE;
- preservar boundary_check;
- no ejecutar segundo ciclo.
```

No debe:

```text
- procesar texto libre;
- usar text_ref para inferir;
- calcular fórmula;
- llamar FormulaEngine;
- llamar EvidenceSufficiency;
- llamar QuestionAlignmentGate;
- llamar PathologyInterpreter;
- llamar OwnerFacingReport;
- generar pregunta al dueño;
- crear EvidenceRecord;
- diagnosticar;
- interpretar patología;
- seleccionar tratamiento;
- generar owner-facing output;
- ejecutar runtime.
```

## Estados esperados

Estados válidos de salida:

```text
PACK_VALIDATED
SINGLE_CYCLE_ROUTE_CANDIDATE
NEEDS_NORMALIZED_SIGNAL
BLOCKED_BY_INVALID_PACK
BLOCKED_BY_MISSING_NODE
BLOCKED_BY_MISSING_ROUTE
BLOCKED_BY_MISSING_UNKNOWN
BLOCKED_BY_MISSING_EVIDENCE_CANDIDATE
BLOCKED_BY_CONTRACT_BOUNDARY
```

Estados no implementables:

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

## Output mínimo requerido

Toda salida debe ser dict serializable con esta anatomía mínima:

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

## Boundary check obligatorio

Toda salida válida o bloqueada debe contener:

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

## Tests focales autorizables futuros

La suite futura debe cubrir como mínimo:

### validate_functional_pack

```text
1. PASS con pack mínimo válido.
2. BLOCKED_BY_INVALID_PACK si falta pack_id.
3. BLOCKED_BY_INVALID_PACK si falta pack_version.
4. BLOCKED_BY_MISSING_NODE si active_subgraph referencia nodo inexistente.
5. BLOCKED_BY_MISSING_NODE si dominant_node no existe.
6. BLOCKED_BY_MISSING_ROUTE si signal_routes está vacío.
7. BLOCKED_BY_MISSING_ROUTE si hay signal_family duplicada.
8. BLOCKED_BY_CONTRACT_BOUNDARY si current_unknown es lista.
9. BLOCKED_BY_MISSING_UNKNOWN si current_unknown no existe en unknowns.
10. BLOCKED_BY_MISSING_EVIDENCE_CANDIDATE si minimal_evidence_candidate referencia evidencia inexistente.
11. No muta el pack original.
12. No emite confidence/scoring.
```

### navigate_single_cycle

```text
13. PASS con señal normalizada y pack válido.
14. NEEDS_NORMALIZED_SIGNAL si falta signal_family.
15. NEEDS_NORMALIZED_SIGNAL si falta signal_id.
16. NEEDS_NORMALIZED_SIGNAL si falta source.
17. BLOCKED_BY_MISSING_ROUTE si no hay ruta para signal_family.
18. BLOCKED_BY_MISSING_ROUTE si hay ruta duplicada.
19. Copia active_subgraph declarado sin calcular distancia.
20. Emite una sola current_unknown.
21. Preserva formula_reference como referencia, no cálculo.
22. Preserva minimal_evidence_candidate sin certificar suficiencia.
23. Preserva boundary_check completo.
24. No usa text_ref para inferencia.
25. No muta signal ni pack.
```

### Imports / frontera

```text
25. El módulo no importa FormulaEngine.
26. El módulo no importa EvidenceSufficiency.
27. El módulo no importa QAG.
28. El módulo no importa PathologyInterpreter.
29. El módulo no importa OwnerFacingReport.
30. El módulo no importa openai, langchain, langgraph, requests, httpx, pandas, polars, sqlite3, sqlalchemy ni subprocess.
```

## Imports permitidos

Permitidos:

```text
typing
copy
```

Opcional si se justifica en implementación futura:

```text
dataclasses
```

No usar Pydantic en este hito.

## Imports prohibidos

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

## Criterios de aceptación del hito futuro

El hito implementativo futuro sólo podrá cerrarse si:

```text
- sólo modifica los dos archivos autorizados;
- implementa funciones puras;
- todos los tests focales pasan;
- no hay imports prohibidos;
- no hay IO;
- no hay runtime;
- no hay integración;
- no hay schemas;
- no hay diagnóstico;
- no hay owner-facing output;
- no hay cálculo de fórmulas;
- no hay distancia funcional;
- no hay confidence/scoring;
- no hay multi-ciclo;
- no muta inputs;
- preserva fail-closed;
- deja evidencia de validación.
```

## Criterios de rechazo del hito futuro

Rechazar si:

```text
- modifica archivos no autorizados;
- toca PymIA-Live;
- toca vertical_slice.py;
- toca orchestration graph;
- toca core_delivery_bridge;
- crea schemas;
- crea pack activo;
- lee archivos;
- escribe archivos;
- usa DB;
- invoca red;
- usa LLM;
- usa fuzzy matching;
- usa scoring;
- usa distancia funcional;
- calcula una fórmula;
- diagnostica;
- interpreta patología;
- propone tratamiento;
- solicita evidencia al dueño;
- genera owner-facing output;
- crea EvidenceRecord;
- promueve evidencia candidata a evidencia suficiente.
```

## Secuencia implementativa futura

```text
1. Crear tests focales primero.
2. Crear módulo puro vacío o mínimo.
3. Implementar validate_functional_pack.
4. Implementar navigate_single_cycle.
5. Ejecutar sólo tests focales autorizados.
6. Auditar imports y diff.
7. Commit focal.
```

No ejecutar suite global salvo autorización explícita.

## Próximo paso metodológico

```text
AUDITORIA_FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_TASKSPEC
```

Sólo si este TaskSpec recibe PASS podrá usarse como prompt implementativo futuro.

Este TaskSpec no ejecuta implementación por sí mismo y no autoriza cambios fuera del hito focal descrito.
