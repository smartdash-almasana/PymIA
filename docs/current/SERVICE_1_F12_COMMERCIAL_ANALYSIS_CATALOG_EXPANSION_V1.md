# Servicio 1 — F12 Commercial Analysis Catalog Expansion V1

**Estado:** FROZEN + COMMITTED  
**Base:** F11 Cafeteria Generalization Gate = PASS  
**Objetivo:** ampliar sistemáticamente el catálogo comercial de análisis sobre la arquitectura general F3→F10→F7→F8→F9, sin crear mini-engines, parsers, evaluators por rubro ni matemática en UI.

## Alcance del roadmap

F12 cubre las familias previstas por la hoja de ruta vigente:

```text
categorías
descuentos
empleados
canales
medios de pago
hora/día
precio catálogo
demanda observada
data quality
rankings
cross-dimensions
```

La expansión se expresa mediante nuevos `AnalysisPlan` declarativos y un número mínimo de medidas matemáticas genéricas.

## Catálogo comercial F12

`F12_COMMERCIAL_ANALYSIS_IDS` define la política explícita de exposición comercial del camino workbook-first. La presencia en el catálogo no reemplaza P7/P8: cada opción se muestra como ejecutable sólo si P8 devuelve `COMPUTABLE`.

El catálogo incluye:

```text
sales_total
sales_by_product
gross_margin_by_product
sales_by_branch
sales_by_category
sales_by_employee
sales_by_channel
sales_by_payment_method
units_by_product
rows_by_product
top_products_by_sales
top_products_by_units
product_sales_concentration
discounted_rows
discounted_rows_by_product
catalog_price_variance_by_product
transaction_id_multiplicity
sales_by_product_branch
sales_by_category_branch
sales_series_day
sales_series_hour
sales_series_month
```

`dso` y `projected_cash_balance` permanecen en el catálogo técnico F10, pero no se incorporan a la política comercial F12. Los servicios legacy de ventas/cobranzas, margen real y flujo de caja continúan visibles y ejecutables por compatibilidad; F12 no los elimina ni los sustituye.

## Dimensiones P7 agregadas al camino AnalysisPlan

F12 hace first-class:

```text
category       -> commercial_category       -> CATEGORY
employee       -> employee_identifier | employee_name -> EMPLOYEE
channel        -> sales_channel              -> CHANNEL
payment_method -> payment_method             -> PAYMENT_METHOD
transaction    -> transaction_identifier     -> TRANSACTION
```

F7 ya poseía preparación genérica para categoría, empleado, canal, medio de pago y tiempo. F12 agrega `transaction` al mismo registro dimensional.

No existe lógica por cafetería o rubro.

## Medidas matemáticas nuevas

### units

```text
SUM(quantity)
```

Unidad de salida: `units`.

### row_count

```text
COUNT(governed rows carrying transaction_identifier evidence)
```

`row_count` cuenta filas gobernadas, no transacciones únicas. Por eso los análisis comerciales usan los términos `registros` o `filas`, no `operaciones únicas`.

### catalog_price_variance_pct

Requiere evidencia explícita:

```text
quantity
unit_sale_price
list_price
```

El precio observado del grupo se pondera por unidades:

```text
observed_sales = SUM_PRODUCT(quantity, unit_sale_price)
observed_units = SUM(quantity)
observed_price = observed_sales / observed_units
```

La fórmula empresarial canónica es:

```text
precio_catalogo_variacion_pct
=
((observed_sales / observed_units) - catalog_price)
/ catalog_price
* 100
```

La definición vive en `pymia/contracts/formula_rules_v1.json` y la ejecuta exclusivamente `FormulaEngineService`.

Bloquea si:

```text
observed_units = 0
catalog_price = 0
```

F8 sólo declara inputs/primitivas y delega la fórmula al Cerebro Matemático.

## Precio catálogo: fail-closed semántico

F12 no rebautiza un precio genérico como precio de lista.

En `cafeteria_abc.xlsx`:

```text
Ventas.PrecioUnitario -> unit_sale_price
Productos.Precio      -> unit_sale_price
```

No existe `list_price` confirmado. Por tanto:

```text
catalog_price_variance_by_product
→ TECHNICALLY_NEEDS_EVIDENCE
→ missing list_price
```

Un control independiente con `PrecioLista -> list_price` explícito demuestra que el mismo AnalysisPlan pasa a `COMPUTABLE` y se ejecuta por F7→F8→F9.

## Descuentos: incidencia, no unidad inventada

`discount_candidate` puede representar porcentaje, fracción o importe. F12 no interpreta esa unidad.

Los análisis F12 son exclusivamente factuales:

```text
discounted_rows
  filter discount_candidate > 0
  COUNT rows

discounted_rows_by_product
  filter discount_candidate > 0
  GROUP BY product
  COUNT rows
  RANK
```

F12 NO certifica:

```text
net sales after discount
discount amount
discount percentage
financial impact of discount
```

Esos cálculos requieren evidencia de unidad gobernada.

## Demanda observada

F12 usa `units` y `row_count` únicamente sobre hechos ya registrados.

```text
units_by_product
top_products_by_units
rows_by_product
```

`demanda observada` significa volumen efectivamente registrado. No es forecast, proyección ni recomendación de inventario.

## Data quality factual

`transaction_id_multiplicity` produce:

```text
GROUP BY transaction_identifier
COUNT rows
RANK DESC
```

Esto permite observar multiplicidad de filas por identificador sin convertirla automáticamente en:

```text
duplicado
error
fraude
severity
recommendation
```

F9 conserva `classification=None` y `severity=None` mientras no exista otra evidencia gobernada.

## Rankings

Los rankings reutilizan F8; no introducen motor de ranking separado:

```text
top_products_by_sales
top_products_by_units
product_sales_concentration
discounted_rows_by_product
transaction_id_multiplicity
```

`RANKED` sigue siendo shape de `AnalysisPlan`; F8 ordena/rankea después de calcular medidas gobernadas.

## Cross-dimensions

F12 agrega:

```text
sales_by_product_branch
  PRODUCT + BRANCH

sales_by_category_branch
  CATEGORY + BRANCH
```

Las relaciones no se inventan. En el fixture cafetería se materializan las owner-confirmed:

```text
Ventas.ProductoID -> Productos.ProductoID
Ventas.SucursalID -> Sucursales.SucursalID
```

F7 realiza los joins; F8 sólo calcula sobre los grupos preparados.

## Hora y día

El mismo `AnalysisPlan` temporal soporta:

```text
sales_series_day   -> DAY
sales_series_hour  -> HOUR
sales_series_month -> MONTH
```

F7 crea buckets temporales; F8 agrega ventas. No existe runtime temporal paralelo.

## Medio de pago

F12 amplía la regla semántica existente de `payment_method` para reconocer también:

```text
metodo_pago
metodopago
```

Esto permite que `cafeteria_abc.xlsx` proyecte:

```text
Ventas.MetodoPago -> payment_method
```

sin agregar regla específica del fixture.

## Wiring comercial workbook-first

Antes de F12, F10 podía descubrir AnalysisPlans pero el menú y `/run-review` seguían ligados a `_LAUNCH_REVIEW_OPTIONS` legacy.

F12 introduce el camino productivo genérico:

```text
confirmed semantic bindings
↓
F10 discovery
↓
F12 commercial exposure policy
↓
generic analysis menu
↓
analysis_id selected by owner
↓
exact P8 GovernedAnalysisInput
↓
F7
↓
F8 / FormulaEngineService
↓
F9 ResultSet + findings + bounded outcome
↓
generic ResultSet renderer
```

El renderer sólo presenta valores, grupos, ranks y trazabilidad del ResultSet. No contiene fórmulas ni branches de negocio.

El POST `/run-review` recolecta genéricamente campos `review_<analysis_id>`; la aplicación valida cada ID nuevamente contra discovery antes de ejecutar.

## Compatibilidad legacy

Los launch routes existentes se preservan:

```text
sold_vs_collected_gap
net_margin_real
working_capital
```

En el menú workbook-first aparecen junto a F12 cuando corresponda. No son fuente de verdad de disponibilidad para AnalysisPlan, pero tampoco se eliminan ni se estrangulan.

No se permite mezclar en el mismo bundle IDs F12 y revisiones legacy; cada carril conserva su contrato mientras continúa la convergencia.

## Persistencia

F12 NO introduce memoria longitudinal de ResultSets.

```text
RESULTSET_PERSISTENCE = F13
TENANT_LONGITUDINAL_MEMORY = F13
```

F12 sólo mantiene el resultado de sesión necesario para renderizar la respuesta actual.

## Autoridades preservadas

```text
P6 = semántica confirmada
P7 = requirements + grain
P8 = computabilidad
F7 = evidence preparation / joins / groups
FormulaEngineService = única autoridad matemática
F8 = runtime analítico bajo FormulaEngineService
F9 = ResultSet/findings/outcome
F10 = discovery
F12 = catálogo + política comercial + wiring genérico
UI = presentación
```

## Invariantes F12

```text
ONE_CANONICAL_PRODUCT_ROOT = PRESERVED
ONE_CANONICAL_XLSX_READER = PRESERVED
P8_IS_COMPUTABILITY_AUTHORITY = PRESERVED
FORMULA_ENGINE_SINGLE_MATH_AUTHORITY = PRESERVED
NO_PARALLEL_ANALYTICS_ENGINE = PASS
NO_CAFETERIA_HARDCODE = PASS
NO_RUBRO_HARDCODE = PASS
NO_UI_BUSINESS_MATH = PASS
NO_LLM_MATH = PASS
LEGACY_SERVICES_PRESERVED = PASS
F13_MEMORY_NOT_PREEMPTED = PASS
```

## Gate F12

El cierre exige:

```text
REAL_CAFETERIA_F12_DISCOVERY = PASS
CATEGORY_E2E = PASS
EMPLOYEE_E2E = PASS
CHANNEL_E2E = PASS
PAYMENT_METHOD_E2E = PASS
HOUR_E2E = PASS
OBSERVED_DEMAND_E2E = PASS
DISCOUNT_INCIDENCE_E2E = PASS
DATA_QUALITY_FACTUAL_E2E = PASS
RANKINGS_E2E = PASS
CROSS_DIMENSIONS_E2E = PASS
CATALOG_PRICE_FAIL_CLOSED_REAL_XLSX = PASS
CATALOG_PRICE_EXPLICIT_LIST_PRICE_CONTROL = PASS
GENERIC_WEB_SINGLE_ANALYSIS_EXECUTION = PASS
GENERIC_WEB_MULTI_ANALYSIS_EXECUTION = PASS
LEGACY_SERVICES_VISIBLE = PASS
GENERIC_RESULT_RENDERER_NO_MATH = PASS
```

La evidencia numérica de regresión se agrega al freeze final después de correr los gates F0–F12.