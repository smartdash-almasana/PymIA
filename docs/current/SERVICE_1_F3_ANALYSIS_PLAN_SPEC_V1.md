# Servicio 1 — F3 Analysis Plan Spec v1

**Estado:** FROZEN  
**Alcance:** contrato declarativo de intención analítica  
**Fuera de alcance:** ejecución, F4/F5/F7/F8, P6/P7/P8, UI y product root

## Autoridad y rol

```text
ANALYSIS_PLAN_ROLE = DECLARATIVE_ANALYTIC_INTENT
REQUESTED_GRAIN_IS_NOT_RESOLVED_GRAIN
P7_REMAINS_GRAIN_RESOLUTION_AUTHORITY
P8_REMAINS_COMPUTABILITY_AUTHORITY
FORMULA_ENGINE_REMAINS_MATH_AUTHORITY
ANALYSIS_PLAN_EXECUTION_AUTHORITY = NONE
```

`AnalysisPlanV1` expresa qué análisis se solicita, sus medidas, dimensiones,
relaciones, filtros, orden y límite. Es un contrato inmutable y fail-closed.
No se conecta al product root y no crea una ruta de ejecución.

## Contrato

El contrato vive en:

```text
pymia/smartpyme/service_1_analysis_plan_v1.py
```

Incluye `AnalysisKind` (`SINGLE_VALUE`, `GROUPED`, `SERIES`, `RANKED`),
`Service1RequestedAnalysisGrainV1`, filtros, orden y `limit` positivo opcional.
`measures`, `dimensions` y `relationship_refs` son IDs analíticos, nunca
columnas físicas.

Reglas congeladas:

- `SINGLE_VALUE`: dimensiones vacías y `aggregation_grain=AGGREGATED`.
- `GROUPED`: al menos una dimensión y `aggregation_grain=GROUPED`.
- `SERIES`: dimensión `time`, temporal distinto de `NONE`/`PERIOD` y agregación `GROUPED`.
- `RANKED`: al menos una dimensión y `order_by` no vacío.
- No se permiten IDs vacíos ni duplicados.
- `limit` es `None` o entero mayor que cero.
- El contrato no contiene `source_bindings`, columnas físicas, expresión de fórmula,
  evidencia, valores calculados ni estado de computabilidad.

La serialización siempre expone `runtime_authorized`, `tool_execution_authorized`,
`product_ready`, `delivery_authorized` y `diagnosis_generated` como `False`.
Cualquier intento de activar una autoridad se rechaza.

## Referencias mínimas

Se validan cuatro instancias del contrato, sin registry ni catálogo productivo:

```text
sales_total             SINGLE_VALUE  NONE / PERIOD / AGGREGATED
sales_by_product        GROUPED       PRODUCT / PERIOD / GROUPED
sales_by_branch         GROUPED       BRANCH / PERIOD / GROUPED
sales_series_by_day     SERIES        NONE / DAY / GROUPED, time ASC
```

Estas instancias prueban representación, no ejecución ni discovery dinámico.

## Fronteras

F3 no modifica `service_1_product_pipeline_v1.py`, P6, P7, P8 ni
`FormulaEngineService`; no agrega runtime de agregación, `ResultSet`, UI,
parsers, lógica de cafetería ni una segunda autoridad matemática.
