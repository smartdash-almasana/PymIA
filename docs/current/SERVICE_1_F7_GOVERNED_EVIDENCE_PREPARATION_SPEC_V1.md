# Servicio 1 — F7 Governed Evidence Preparation Spec v1

**Estado:** FROZEN  
**Alcance:** preparación material gobernada de evidencia para `AnalysisPlanV1` ya declarado `COMPUTABLE` por P8  
**Fuera de alcance:** agregación F8, ejecución de fórmulas F8, ranking de resultados, `ResultSet` F9, discovery F10, UI y product root

## Decisión F7

```text
ANALYSIS_PLAN = declarative intent
P7 = requirements + resolved grain
P8 = computability + GovernedAnalysisInputV1
F7 = row evidence preparation + relationship materialization + group membership
F8 = mathematical execution
```

F7 crea una única superficie nueva:

```text
pymia/smartpyme/service_1_analysis_evidence_preparation_v1.py
```

No crea un `AnalysisEngine`, no duplica P7/P8, no abre XLSX y no introduce una segunda autoridad matemática.

## Entrada

```text
case_id
Service1GovernedAnalysisInputV1 emitted by P8
canonical ingestion_output.normalized_tables
```

F7 no vuelve a interpretar semántica. Consume únicamente los `source_bindings`, `relationship_bindings`, `grain` y `AnalysisPlan` ya gobernados por P8 y los contrasta con las tablas normalizadas canónicas.

## Salida

Cuando la evidencia puede prepararse de forma segura:

```text
Service1EvidencePreparationDecisionV1
status = PREPARED
↓
Service1PreparedAnalysisEvidenceV1
```

La evidencia preparada contiene:

```text
case_id
analysis_id
analysis_plan
resolved grain
source_sheet_refs
prepared_rows
groups
materialized_relationships
applied_filters
provenance
```

Cada `Service1PreparedRowV1` mantiene:

```text
row_ref
base_sheet_ref
role_values
role_source_refs
source_row_refs
relationship_refs
```

Esto preserva lineage hasta fila/hoja/columna sin producir todavía resultados empresariales.

## Estados F7

```text
PREPARED
NEEDS_EVIDENCE
UNSUPPORTED
BLOCKED
```

Criterio:

- `PREPARED`: las filas necesarias pueden identificarse y organizarse sin ambigüedad;
- `NEEDS_EVIDENCE`: faltan valores, matches de relación o evidencia física requerida;
- `UNSUPPORTED`: el plan usa una transformación estructural aún fuera del contrato F7;
- `BLOCKED`: existe drift, ambigüedad o contradicción material que hace inseguro preparar evidencia.

## Selección de tabla base

F7 no hardcodea `Ventas`, cafetería ni rubro.

Reglas:

1. si existen relaciones `MANY_TO_ONE`/`ONE_TO_ONE` confirmadas con un único left sheet común, ese left sheet es el candidato de grain base;
2. en ausencia de relación, se selecciona determinísticamente la única tabla con mayor cobertura de `source_bindings`;
3. empate material => `BASE_SHEET_AMBIGUOUS`;
4. evidencia requerida en múltiples hojas sin relación gobernada => `CROSS_SHEET_SOURCE_REQUIRES_RELATIONSHIP`.

## Relationship materialization

F7 materializa exclusivamente relaciones ya transportadas por P8 como evidencia owner-confirmada.

No descubre relaciones nuevas.
No reinterpreta endpoints.
No inventa joins.

Relaciones materializables F7:

```text
MANY_TO_ONE
ONE_TO_ONE
```

`STRUCTURAL_OVERLAP` u otra topología no join-safe => `UNSUPPORTED`.

Para `MANY_TO_ONE`:

- el lado derecho debe tener key no duplicada para las keys usadas;
- duplicate lookup key => `BLOCKED / RELATIONSHIP_CARDINALITY_VIOLATION`;
- left key vacía => `NEEDS_EVIDENCE`;
- left key sin match => `NEEDS_EVIDENCE`.

Para `ONE_TO_ONE`, la unicidad se exige en ambos lados materiales.

Cada relación preparada conserva pares de lineage:

```text
Ventas!row:2 → Productos!row:2
Ventas!row:3 → Productos!row:3
```

La salida distingue explícitamente:

```text
evidence_join_materialized = True
join_runtime_execution_authorized = False
```

La materialización sólo prepara evidencia para F8; no autoriza ejecución productiva por sí misma.

## Source bindings

Cada semantic role gobernado por P8 se proyecta a una única fuente física.

Reglas:

```text
role → one physical column
one role source ambiguous → BLOCKED
missing role value → NEEDS_EVIDENCE
```

Cuando una columna existe tanto en la tabla base como en una tabla relacionada, F7 usa la fuente de la tabla base para ese role. Esto permite que claves como `ProductoID` o `SucursalID` preserven el grain transaccional del análisis sin convertir la tabla lookup en autoridad de fila.

## Filters

F7 sí puede seleccionar filas porque row selection es preparación de evidencia, no matemática empresarial.

Operadores soportados:

```text
EQ
NE
IN
NOT_IN
GT
GTE
LT
LTE
BETWEEN
```

Operador desconocido => `UNSUPPORTED`.
Comparación incompatible => `BLOCKED` fail-closed.
Filtro que no selecciona ninguna fila => `NEEDS_EVIDENCE`.

Los filtros nunca producen una métrica; sólo determinan qué filas pasan al paquete F8.

## Temporal preparation

F7 puede producir claves temporales de membership:

```text
DAY   → YYYY-MM-DD
WEEK  → YYYY-Www
MONTH → YYYY-MM
HOUR  → HH:00
```

Esto no agrega valores. Sólo etiqueta cada fila con el bucket temporal al que pertenece.

Fecha/hora requerida pero no parseable => `NEEDS_EVIDENCE`.

## Group membership

F7 prepara membership, no resultados.

Ejemplo:

```text
group:product=P1
members:
  Ventas!row:2
  Ventas!row:4
```

Para `SINGLE_VALUE`:

```text
group:ALL
```

Para `GROUPED`, `SERIES` y `RANKED`, F7 crea los grupos de filas correspondientes a las dimensiones del plan.

No calcula:

```text
SUM
AVG
COUNT
RANK
margen
total
ratio
```

`RANKED` sólo prepara los grupos. `order_by` y `limit` quedan diferidos; F7 no ordena por una métrica que aún no existe.

## Formula refs

F7 transporta los roles/evidencia necesarios para una futura fórmula, pero no usa `FormulaEngineService` y no evalúa `formula_refs`.

Ejemplo margen bruto por producto:

```text
sales_amount
quantity
unit_cost_candidate
product_identifier
confirmed product relationship
↓
prepared row evidence
```

El costo derivado, la agregación de ventas/costos y la fórmula final pertenecen a F8.

## Autoridad

Siempre:

```text
runtime_authorized = False
tool_execution_authorized = False
product_ready = False
delivery_authorized = False
diagnosis_generated = False
analysis_execution_authorized = False
aggregation_execution_authorized = False
formula_execution_authorized = False
ranking_execution_authorized = False
```

F7 no importa ni llama:

```text
FormulaEngineService
GenericCapabilityEngine
service_1_product_pipeline_v1
```

## Gate F7

```text
F7_SINGLE_PREPARATION_SURFACE = PASS
CANONICAL_NORMALIZED_TABLES_ONLY = PASS
GROUP_MEMBERSHIP_WITHOUT_AGGREGATION = PASS
FILTER_PREPARATION = PASS
TEMPORAL_BUCKET_PREPARATION = PASS
CONFIRMED_RELATIONSHIP_MATERIALIZATION = PASS
RELATIONSHIP_CARDINALITY_FAIL_CLOSED = PASS
ROW_LINEAGE_PRESERVED = PASS
RANKING_DEFERRED = PASS
FORMULA_EXECUTION = 0
AGGREGATION_EXECUTION = 0
BUSINESS_RESULT_GENERATION = 0
NO_PRODUCT_ROOT_CHANGE = REQUIRED
NO_P8_AUTHORITY_CHANGE = REQUIRED
NO_MATH_AUTHORITY_CHANGE = REQUIRED
```
