# Servicio 1 — F10 Dynamic Analysis Discovery Spec v1

**Estado:** FROZEN  
**Alcance:** discovery dinámico de `AnalysisPlan` técnicamente elegibles desde semántica confirmada, con separación explícita entre disponibilidad técnica y exposición comercial.  
**Fuera de alcance:** ejecución matemática, findings, product wiring F11, expansión de catálogo F12, persistencia longitudinal F13, UI business logic y retiro total del launch legacy.

## Decisión congelada

```text
F10_IS_DISCOVERY_ONLY
P7_REMAINS_REQUIREMENT_AND_GRAIN_AUTHORITY
P8_REMAINS_COMPUTABILITY_AUTHORITY
F10_DOES_NOT_EXECUTE_ANALYSIS
F10_DOES_NOT_EXECUTE_MATH
F10_DOES_NOT_EXECUTE_JOINS
F10_DOES_NOT_GENERATE_FINDINGS
TECHNICAL_AVAILABILITY != COMMERCIAL_EXPOSURE
```

F10 reemplaza el hardcode de disponibilidad para el nuevo camino `AnalysisPlan` por una evaluación real sobre P6/P7/P8.

## Flujo

```text
CONFIRMED_BINDINGS
↓
P6 APPROVED evidence
↓
F10 analysis discovery catalog
↓
candidate AnalysisPlan
↓
P7 requirement/grain resolution
↓
confirmed relationship-path resolution when cross-sheet evidence is required
↓
P8 computability
↓
TECHNICALLY_AVAILABLE
TECHNICALLY_NEEDS_EVIDENCE
TECHNICALLY_UNSUPPORTED
TECHNICALLY_BLOCKED
↓
optional commercial exposure policy
↓
generic menu projection
```

F10 nunca considera una opción disponible sólo porque exista una tarjeta o un `if` en la UI.

## Catálogo F10 actual

La primera versión contiene únicamente shapes ya soportados por F3–F9:

```text
sales_total
sales_by_product
gross_margin_by_product
sales_by_branch
sales_series_day
sales_series_month
dso
projected_cash_balance
```

Cada entrada declara sólo:

```text
analysis_id
title
question
kind
measures
dimensions
requested grain
order_by / limit cuando corresponda
preferred_roles cuando el análisis requiere una fuente de dimensión específica
commercially_exposed_by_default
```

No contiene fórmulas, SQL, joins ejecutables, lógica por rubro ni branches por cafetería.

## Disponibilidad técnica

Un análisis queda `TECHNICALLY_AVAILABLE` sólo si:

1. existe semántica confirmada;
2. los P6 relevantes están `APPROVED`;
3. P7 resuelve todos los role-groups y el grain;
4. si los roles viven en más de una hoja, existe un camino de relaciones owner-confirmadas y join-safe;
5. el `AnalysisPlan` final contiene esas `relationship_refs`;
6. P8 devuelve `COMPUTABLE`.

F11 refinó la selección de fuente: cuando múltiples columnas P6 aprobadas pueden satisfacer el mismo role-group, F10 proyecta un subconjunto coherente antes de P8. La selección prioriza `preferred_roles` declarados por el template y, a igualdad semántica, la fuente del lado fact de relaciones confirmadas. No rebindea roles ni crea semántica nueva. Si la mejor selección sigue siendo ambigua, bloquea.

Cuando P8 devuelve `COMPUTABLE`, F10 conserva el `Service1GovernedAnalysisInputV1` exacto dentro del item descubierto como pass-through no ejecutable para que F11/F7 consuman la misma decisión de computabilidad; F10 no obtiene por ello autoridad de ejecución.

Por tanto:

```text
UI presence != technical availability
catalog presence != technical availability
semantic similarity != technical availability
P8 COMPUTABLE + relationship evidence = technical availability
```

## Relaciones cross-sheet

F10 no crea relaciones.

Consume exclusivamente `confirmed_relationships` con:

```text
confirmed_by_owner = True
relationship_kind = MANY_TO_ONE | ONE_TO_ONE
```

Para evidencia distribuida entre hojas:

```text
P6 selected source sheets
↓
directed confirmed relationship graph
↓
unique shortest join-safe path
↓
relationship_refs added to AnalysisPlan
↓
P7 rerun
↓
P8 with exact bindings
```

Si no existe camino confirmado:

```text
TECHNICALLY_NEEDS_EVIDENCE
p8_reason = CROSS_SHEET_RELATIONSHIP_EVIDENCE_REQUIRED
```

F10 es deliberadamente más conservador que una evaluación P8 que no pueda ver el layout físico de hojas. Nunca promueve a AVAILABLE un análisis cross-sheet sin relación gobernada.

## Técnico vs comercial

F10 mantiene tres conceptos separados:

```text
technically_available
commercially_requested
commercially_exposed
```

Regla:

```text
commercially_exposed
= technically_available AND commercially_requested
```

Un análisis puede ser técnicamente computable sin estar todavía habilitado en producto.

Esto permite que F11 cablee productivamente un subconjunto sin falsear el estado técnico del resto.

## Proyección genérica a UI

`project_service_1_dynamic_discovery_menu_v1()` proyecta análisis comercialmente solicitados al shape ya aceptado por `render_analysis_menu_v1`:

```text
available:
  (analysis_id, title, question)

blocked:
  name
  question
  missing_evidence
  why_needed
  technical_status
  p7_status
  p8_status
  p8_reason
```

El renderer no conoce ids específicos.

Gate:

```text
ADD_NEW_ANALYSIS_REQUIRES_UI_CHANGE = NO
```

Un template adicional puede atravesar F10 y aparecer en el renderer existente sin modificar `service_1_ui_v1.py`.

## Integración con recepción semántica

`service_1_assisted_web_semantic_reception_v1.py` incorpora ahora el F10 canónico dentro de `build_service_1_post_semantic_analysis_discovery_v1()`.

El packet expone:

```text
analysis_plans
technically_available_analysis_ids
commercially_exposed_analysis_ids
```

La superficie previa:

```text
available
blocked
```

se conserva temporalmente para los launch routes legacy ya productivos.

Por tanto:

```text
_LAUNCH_REVIEW_OPTIONS
= LEGACY COMMERCIAL COMPATIBILITY
!= F10 TECHNICAL SOURCE OF TRUTH
```

El retiro del launch legacy no pertenece a F10 porque F11 debe cablear primero los análisis nuevos a la ruta productiva completa F3→F9.

## Fail-closed

F10 bloquea o degrada disponibilidad ante:

```text
CONFIRMED_BINDINGS_REQUIRED
CONFIRMED_BINDINGS_AUTHORITY_FORBIDDEN
CASE_ID_REQUIRED
APPROVED_P6_EVIDENCE_REQUIRED
P6_CASE_ID_MISMATCH
DISCOVERY_AMBIGUOUS_REQUIRED_ROLE_GROUP
DISCOVERY_AMBIGUOUS_SOURCE_COLUMN
DISCOVERY_AMBIGUOUS_RELATIONSHIP_PATH
CROSS_SHEET_RELATIONSHIP_EVIDENCE_REQUIRED
P7 blocked/missing/not observed
P8 blocked/unsupported/needs evidence
unknown commercial exposure analysis id
```

No intenta resolver ambigüedad semántica en discovery.

## Autoridades preservadas

```text
P6 = semantic meaning authority
P7 = requirements + resolved grain
P8 = computability authority
F7 = evidence materialization
F8 = mathematical authority/runtime
F9 = ResultSet/findings
F10 = discovery only
```

No se crea:

```text
second P8
second capability engine
second math engine
second semantic authority
UI preflight authority
```

## No hardcode por rubro

F10 no contiene decisiones para:

```text
cafetería
retail
consorcio
distribuidora
Mercado Libre
```

La disponibilidad depende exclusivamente de semántica confirmada y contratos analíticos.

## Gate F10

```text
CONFIRMED_BINDINGS_TO_CANDIDATE_PLANS = PASS
P7_REAL_GATE = PASS
P8_REAL_GATE = PASS
CROSS_SHEET_RELATIONSHIP_FAIL_CLOSED = PASS
OWNER_CONFIRMED_RELATIONSHIP_TO_PLAN = PASS
TECHNICAL_COMMERCIAL_SEPARATION = PASS
GENERIC_MENU_PROJECTION = PASS
ADD_NEW_ANALYSIS_REQUIRES_UI_CHANGE = NO
NO_MATH_EXECUTION = PASS
NO_JOIN_EXECUTION = PASS
NO_FINDING_GENERATION = PASS
NO_RUBRO_HARDCODE = PASS
NO_CAFETERIA_HARDCODE = PASS
LEGACY_LAUNCH_OPTIONS_TECHNICAL_AUTHORITY = NO
```

F10 se congela sólo si F0–F9 permanecen verdes y el diff queda limitado a discovery, su integración de recepción, documentación y tests.

## Siguiente gate

F11 debe probar físicamente sobre `cafeteria_abc.xlsx` que seis análisis distintos atraviesan la misma cadena:

```text
semantic system
P6
P7
P8
AnalysisPlan
F7
F8
F9
```

sin branches especiales por análisis ni por cafetería.
