# ADR-029 — Service 1 LLM Semantic Assistance Boundary V1

**Date:** 2026-08-14  
**Status:** ACCEPTED FOR IMPLEMENTATION  
**Scope:** Servicio 1 — lectura semántica y confirmación asistida de columnas/relaciones de workbook  
**Decision type:** Architectural boundary  
**Implementation cut:** SEM-0  
**Supersedes:** Ningún contrato de autoridad existente  
**Must reconcile with:** ADR-026 / Tenant Semantic Contract y la raíz productiva canónica de Servicio 1

---

## 1. Contexto

Servicio 1 ya posee:

- una ingesta XLSX canónica;
- un `service_1_column_understanding_engine_v1.py` determinístico y puro;
- semantic bridge;
- P6 / controlled execution gate;
- owner confirmation loop;
- reinyección de confirmaciones;
- confirmed bindings;
- tenant semantic contract y persistencia;
- una única raíz productiva: `pymia/smartpyme/service_1_product_pipeline_v1.py`.

El problema de producto no es la ausencia de lectura de columnas. El problema es que la comprensión empresarial del workbook quedó absorbida por reglas determinísticas, aliases y preguntas columna-por-columna.

Ese modelo provoca:

- preguntas repetidas;
- interpretación local de columnas sin comprender relaciones entre hojas;
- ramas específicas por capacidad;
- crecimiento de listas de headers;
- UX de homologación en lugar de asistencia;
- riesgo de introducir lógica semántica dentro de la capa web;
- dificultad para generalizar sobre Excel reales.

La arquitectura debe permitir asistencia LLM para comprender y conversar sin conceder autoridad de ejecución, cálculo, persistencia semántica autónoma ni delivery.

---

## 2. Decisión

Servicio 1 adopta esta separación obligatoria:

```text
IA PARA INTERPRETAR Y CONVERSAR
OWNER PARA CONFIRMAR SIGNIFICADO EMPRESARIAL
CÓDIGO DETERMINÍSTICO PARA VALIDAR, PLANIFICAR Y CALCULAR
```

Se formalizan las siguientes políticas:

```text
LLM_RUNTIME_SEMANTIC_ASSISTANCE = ALLOWED
LLM_RUNTIME_AUTHORITY = FORBIDDEN

OWNER_SEMANTIC_AUTHORITY = REQUIRED
DETERMINISTIC_VALIDATION = REQUIRED
DETERMINISTIC_EXECUTION_AUTHORITY = REQUIRED
OWNER_CONFIRMATION_FOR_MATERIAL_SEMANTICS = REQUIRED
```

La LLM puede:

- proponer significados;
- proponer relaciones entre columnas/hojas;
- detectar posibles duplicados semánticos;
- proponer relevancia respecto de la capacidad solicitada;
- expresar incertidumbre;
- interpretar lenguaje natural del owner como propuesta de corrección.

La LLM no puede:

- confirmar significado en nombre del owner;
- crear columnas inexistentes;
- inventar evidencia;
- autorizar runtime;
- autorizar tool execution;
- autorizar product readiness;
- autorizar delivery;
- producir resultados financieros con autoridad;
- persistir por sí sola una interpretación como verdad;
- modificar contratos;
- crear un segundo parser XLSX;
- crear una segunda raíz productiva.

---

## 3. Invariantes preservados

Este ADR no elimina ni debilita:

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
NO_LLM_RUNTIME_AUTHORITY
```

Interpretación normativa:

`NO_LLM_RUNTIME_AUTHORITY` no significa `NO_LLM_RUNTIME`.

La asistencia LLM en runtime queda permitida sólo en la frontera semántica, antes de los gates determinísticos.

---

## 4. Arquitectura de referencia

```text
XLSX
 │
 ▼
CANONICAL XLSX PARSER
existente
 │
 ▼
CANONICAL INGESTION OUTPUT
normalized_tables + column_refs + column_evidence
 │
 ▼
WORKBOOK PROFILER V1
determinístico
 │
 ├── estadísticas por columna
 ├── evidence_registry
 ├── candidate keys
 └── candidate cross-sheet relationships
 │
 ▼
DETERMINISTIC COLUMN UNDERSTANDING
existente
 │
 ▼
SEMANTIC CONTEXT PACKET V1
 │
 ▼
LLM SEMANTIC INTERPRETER V1
sólo propuestas
 │
 ▼
STRICT SEMANTIC PROPOSAL VALIDATOR V1
 │
 ▼
VALIDATED SEMANTIC PROPOSALS
 │
 ▼
OWNER DIALOGUE PLANNER V1
 │
 ├── irrelevantes → fuera de diálogo
 ├── compatibles → agrupación
 ├── relaciones → una decisión
 └── ambiguos → pregunta específica
 │
 ▼
OWNER
 │
 ├── YES → confirmar
 │
 ├── NO → degradar a granular
 │
 └── CORRECTION → targeted correction / granular fallback
 │
 ▼
CANONICAL OWNER EVIDENCE
 │
 ├── column confirmation events
 └── relationship confirmation events
 │
 ▼
P6 + REINJECTION
existentes
 │
 ▼
CONFIRMED_BINDINGS
+
CONFIRMED_RELATIONSHIPS
```

---

## 5. Regla del parser y profiling

El `WorkbookProfilerV1` no abre nuevamente el XLSX.

Consume exclusivamente la salida de la ingesta canónica existente:

```text
canonical ingestion_output
├── normalized_tables
├── column_refs
└── column_evidence
```

El profiler es un enriquecimiento determinístico post-ingesta.

Debe poder calcular:

### Por columna

- tipo observado;
- row count;
- non-null count;
- null ratio;
- cardinalidad;
- unique ratio;
- uniqueness class;
- rango numérico o fecha cuando aplique;
- muestras acotadas;
- normalized header.

### Entre columnas/hojas

- overlap de valores;
- subset/superset;
- same-normalized-header;
- candidate primary key;
- candidate foreign key;
- candidate relationship direction;
- duplicate structural semantics.

Si el journey no contiene las tablas necesarias:

```text
BLOCK_PROFILE_SOURCE_TABLES_MISSING
```

No se reabre el archivo ni se crea otro parser.

---

## 6. Evidence Registry

`WorkbookProfileV1` debe construir un registro cerrado de evidencia:

```text
evidence_registry
```

Ejemplos:

```text
ev:column:Ventas.ProductoID:type
ev:column:Productos.ProductoID:uniqueness
ev:relationship:Ventas.ProductoID->Productos.ProductoID:overlap
ev:column:Ventas.Descuento:range
```

Toda propuesta LLM que declare `evidence_refs` debe referenciar exclusivamente entradas existentes.

Si una referencia no existe:

```text
BLOCKED_EVIDENCE_REF_NOT_FOUND
```

La salida completa del modelo se considera inválida para ese pass.

No se corrige silenciosamente una referencia inventada.

---

## 7. Semantic Context Packet

La LLM no recibe el workbook como autoridad libre.

Recibe un paquete acotado:

```text
case_id
requested_capability
workbook_profile
deterministic_hypotheses
allowed_semantic_roles
capability_relevant_roles
compatible_tenant_memory_hints
evidence_registry
```

No recibe:

- workbook bytes;
- credenciales;
- tokens;
- flags de autoridad;
- delivery permissions;
- datos no necesarios para el contexto semántico.

Las muestras de valores deben estar acotadas.

---

## 8. Contrato de salida LLM

La salida debe ajustarse a un esquema cerrado equivalente a:

```json
{
  "concept_proposals": [],
  "relationship_proposals": [],
  "duplicate_semantics": [],
  "irrelevant_refs": [],
  "material_ambiguities": []
}
```

Una propuesta de concepto debe contener como mínimo:

```text
proposal_id
target_column_refs[]
semantic_role
variable_name
confidence
rationale
evidence_refs[]
```

Una propuesta de relación:

```text
relationship_id
left_column_ref
right_column_ref
relationship_type
confidence
evidence_refs[]
```

Campos prohibidos:

```text
owner_confirmed
runtime_authorized
tool_execution_authorized
product_ready
delivery_authorized
diagnosis_generated
calculation_result
```

La presencia de autoridad prohibida invalida la salida.

---

## 9. Semantic Proposal Validator

Ninguna salida LLM entra directamente al semantic gate.

El validador determinístico comprueba:

- existencia de cada `column_ref`;
- existencia de cada `sheet_ref`;
- existencia de cada `evidence_ref`;
- pertenencia de `semantic_role` a la ontología permitida;
- compatibilidad de `variable_name`;
- validez de relaciones;
- consistencia con evidencia estructural;
- `confidence` dentro de rango;
- ausencia de flags de autoridad;
- ausencia de valores o columnas inventadas.

Estados mínimos:

```text
MATERIAL_CONFIDENT
MATERIAL_AMBIGUOUS
IRRELEVANT_FOR_CAPABILITY
CONFLICTING_EVIDENCE
BLOCKED
```

La confianza declarada por la LLM nunca es evidencia suficiente por sí sola.

---

## 10. Owner Dialogue Plan

La unidad de interacción no es obligatoriamente una columna.

Puede ser:

```text
SEMANTIC_GROUP
RELATIONSHIP
UNIT_MEANING
CONFLICT
NOT_APPLICABLE
```

Un `OwnerDialogueDecisionV1` debe contener:

```text
decision_id
decision_kind
proposal_refs[]
column_refs[]
relationship_refs[]
presentation_text
materiality_reason
accept_action
reject_action
correction_action
fallback_strategy
```

Reglas:

### Irrelevante

Si una columna no participa materialmente en la capacidad solicitada:

```text
→ no preguntar
→ no crear falsa confirmación owner
```

### Grupo semántico

Varias propuestas compatibles pueden agruparse en una única interacción.

Ejemplo:

> Interpreto `Cantidad` como unidades vendidas, `PrecioUnitario` como precio de venta y `Costo` como costo unitario. ¿Es correcto?

Una respuesta afirmativa puede proyectarse a varios eventos canónicos.

### Relación

La misma relación se pregunta una sola vez.

Ejemplo:

> `ProductoID` en Ventas y Productos parece identificar el mismo producto y permitir relacionar ambas hojas. ¿Es correcto?

No se hacen dos preguntas independientes sobre `ProductoID`.

---

## 11. Fallback obligatorio de propuestas agrupadas

Toda agrupación debe declarar explícitamente un fallback.

Estrategias permitidas:

```text
DECOMPOSE_TO_ATOMIC
REQUIRE_TARGETED_CORRECTION
BLOCK_IF_UNRESOLVABLE
```

### Owner responde YES

```text
GROUP_PROPOSED
→ GROUP_CONFIRMED
→ N owner confirmation events
```

### Owner responde NO

Un `NO` genérico no puede interpretarse como rechazo individual de todas las propuestas.

Debe ocurrir:

```text
GROUP_PROPOSED
→ GROUP_REJECTED_REQUIRES_DECOMPOSITION
→ DECOMPOSE_TO_ATOMIC
→ NEEDS_GRANULAR_CONFIRMATION
```

No se permiten confirmaciones parciales silenciosas.

### Owner corrige

Ejemplo:

> No, `Precio` es precio de lista. El que realmente cobro es `PrecioUnitario`.

La corrección puede ser interpretada por LLM sólo como propuesta estructurada.

Luego:

```text
owner free text
→ LLM correction proposal
→ deterministic validator
→ targeted confirmation / granular fallback
```

Nunca:

```text
free text
→ LLM interpretation
→ confirmed binding automático
```

Si no puede atribuirse inequívocamente la corrección:

```text
→ DECOMPOSE_TO_ATOMIC
```

---

## 12. Evidencia de relaciones

El contrato actual de confirmación por columna no debe deformarse para representar relaciones.

Se introduce un contrato separado:

```text
Service1OwnerRelationshipConfirmationEventV1
```

Campos mínimos:

```text
case_id
file_ref
left_sheet_ref
left_column_ref
right_sheet_ref
right_column_ref
relationship_kind
owner_answer
confirmed_by_owner
question_ref
timestamp
provenance
runtime_authorized = False
tool_execution_authorized = False
delivery_authorized = False
```

Este evento es evidencia, no permiso.

No habilita cálculo por sí solo.

---

## 13. Tenant semantic continuity

La memoria tenant continúa siendo:

```text
EVIDENCE / HINT
```

y no:

```text
AUTOMATIC AUTHORITY
```

Una memoria histórica sólo puede presentarse como hint si la estructura actual es compatible.

Se define conceptualmente:

```text
StructuralCompatibilitySignatureV1
```

No debe depender de cardinalidades absolutas que cambian naturalmente.

Debe usar propiedades estables:

```text
data_type_family
uniqueness_class
nullability_class
relationship_direction
key_role
overlap_band
source_context
schema_version
```

Regla:

```text
current signature compatible with memory
→ memory may be used as HINT

current signature incompatible
→ memory = OBSOLETE_HINT
→ no reutilización semántica
```

Aun cuando sea compatible, la memoria no reemplaza confirmación owner material requerida por V1.

---

## 14. Fallback ante fallo LLM

La disponibilidad del modelo no puede degradar la seguridad.

```text
LLM valid
→ validated semantic proposals

LLM invalid
→ discard model output
→ fallback

LLM unavailable
→ deterministic baseline
→ owner confirmation explícita
```

Nunca:

```text
LLM unavailable
→ asumir significado
```

El fallback aceptado es más interacción humana, no menor gobernanza.

---

## 15. Integración con componentes existentes

Se preservan como downstream canónico:

```text
service_1_semantic_bridge_to_controlled_execution_gate_v1.py
P6 approval decisions
service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1.py
service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py
service_1_deterministic_semantic_pipeline_v1.py
service_1_product_pipeline_v1.py
```

El nuevo subsistema debe producir candidatos compatibles con el gate existente.

No se crea:

```text
LLMConfirmedBindings
LLMAuthorizedCandidate
LLMProductRoot
```

La asistencia LLM termina antes de la autoridad determinística.

---

## 16. Web boundary

`service_1_assisted_web_v1.py` no debe ser autoridad de comprensión semántica.

La web puede:

- renderizar el diálogo;
- recibir respuestas;
- conservar estado de sesión;
- mostrar memoria como hint;
- mostrar resultados de validación.

La web no debe contener:

- listas autoritativas de headers por capacidad;
- cálculo semántico por capacidad;
- branches de interpretación específicos;
- joins financieros;
- reglas para decidir qué concepto es relevante.

El `OwnerDialoguePlanV1` debe llegar ya resuelto desde dominio.

---

## 17. Casos de aceptación mínimos

### Cafetería / maestro + transacciones

Debe detectar estructuralmente:

```text
Productos.ProductoID = candidate unique key
Ventas.ProductoID → Productos.ProductoID = candidate relationship
```

El owner ve una sola decisión relacional.

### Headers distintos, misma estructura

Dos workbooks con nombres distintos pero evidencia equivalente deben generar propuestas semánticas equivalentes, sin branches por filename o tenant.

### Corrección del owner

LLM propone:

```text
Productos.Precio → unit_sale_price
```

Owner corrige:

```text
Productos.Precio → list_price
Ventas.PrecioUnitario → unit_sale_price
```

El sistema conserva la corrección como evidencia owner y continúa sin hardcode.

### Evidence ref inexistente

```text
→ BLOCKED_EVIDENCE_REF_NOT_FOUND
```

### Relación estructural incompatible con memoria

```text
→ memory OBSOLETE_HINT
→ no reutilización silenciosa
```

### Rechazo de grupo

```text
→ NEEDS_GRANULAR_CONFIRMATION
```

sin perder las propuestas ni fabricar rechazos individuales.

---

## 18. Orden de implementación autorizado

Este ADR habilita únicamente el siguiente orden:

```text
SEM-1  WorkbookProfilerV1 + evidence_registry
SEM-2  LLM semantic contracts + provider-neutral adapter
SEM-3  deterministic semantic proposal validator
SEM-4  OwnerDialoguePlanV1 + grouped fallback
SEM-5  owner answer projection + relationship confirmation event
SEM-6  integration/reentry into existing gates
SEM-7  tenant structural compatibility
SEM-8  product-root wiring
SEM-9  removal of transient semantic logic from web
```

No se conecta LLM al product runtime antes de tener:

```text
WorkbookProfileV1
+
closed LLM contract
+
strict validator
+
grouped fallback
```

---

## 19. Fuera de alcance de este ADR

No autoriza:

```text
NO Capability Evidence Planner
NO Derived Evidence Engine
NO nuevas capacidades
NO cálculo financiero por LLM
NO joins comerciales por LLM
NO LearningMemory general
NO automatic contract mutation
NO segundo parser
NO segunda raíz productiva
NO regla específica cafeteria_abc
NO refactor masivo de Servicio 1
```

Estos elementos pertenecen a cortes posteriores del plan general de cierre.

---

## 20. Definition of Done del boundary

El boundary queda cerrado cuando:

- el parser XLSX canónico sigue siendo único;
- el profiler consume `canonical ingestion_output`;
- la LLM recibe sólo contexto acotado;
- toda salida LLM se valida determinísticamente;
- evidencia inexistente se rechaza;
- la LLM no puede emitir autoridad;
- grupos rechazados degradan a granular;
- relaciones tienen evidencia propia;
- memoria incompatible se invalida como hint;
- owner continúa siendo la única fuente de confirmación empresarial;
- downstream P6/reinjection/bindings se reutilizan;
- la web deja de decidir semántica de capacidad;
- existe fallback determinístico si la LLM falla;
- tests focales y de contrato pasan.

---

## 21. Regla rectora

```text
EL PARSER LEE.
EL PROFILER MIDE.
LA LLM PROPONE.
EL VALIDADOR LIMITA.
EL OWNER CONFIRMA.
LOS GATES GOBIERNAN.
EL CÓDIGO DETERMINÍSTICO EJECUTA.
```

Ninguna capa puede apropiarse de la autoridad de otra.
