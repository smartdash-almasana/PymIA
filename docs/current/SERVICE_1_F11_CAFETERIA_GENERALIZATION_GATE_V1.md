# Servicio 1 — F11 Cafeteria Generalization Gate V1

**Estado:** FROZEN + COMMITTED  
**Fixture físico:** `prueba_excels/cafeteria_abc.xlsx`  
**Objetivo:** demostrar que un Excel PyME real con detalle transaccional, dimensiones y tablas maestras atraviesa la misma arquitectura general F3→F10→F7→F8→F9 sin ramas especiales por cafetería ni por análisis.

## Evidencia física del workbook

El fixture se abre exclusivamente mediante el intake XLSX canónico de Servicio 1.

```text
Ventas       5000 filas
Sucursales      5 filas
Productos      15 filas
```

`Ventas` contiene:

```text
VentaID
Fecha
Hora
SucursalID
ProductoID
Cantidad
PrecioUnitario
MetodoPago
CanalVenta
Descuento
Empleado
```

No existe una columna `VentaTotal` / `sales_amount` precalculada.

`Sucursales` contiene:

```text
SucursalID
Sucursal
Ciudad
```

`Productos` contiene:

```text
ProductoID
Producto
Categoria
Costo
Precio
```

El WorkbookProfiler detecta físicamente:

```text
Ventas.ProductoID -> Productos.ProductoID
MANY_TO_ONE
coverage = 1.0
candidate_foreign_key = True

Ventas.SucursalID -> Sucursales.SucursalID
MANY_TO_ONE
coverage = 1.0
candidate_foreign_key = True
```

## Cadena F11 probada

```text
canonical XLSX intake
↓
WorkbookProfiler
↓
deterministic semantic provider boundary
↓
explicit owner confirmations
↓
P6 APPROVED
↓
F10 dynamic discovery / AnalysisPlan
↓
P7 requirement + resolved grain
↓
P8 computability + exact governed input
↓
F7 evidence preparation / relationship materialization
↓
F8 Math Brain
↓
F9 ResultSet / Finding / bounded outcome
```

El test F11 no usa UI como autoridad, no calcula resultados auxiliares y no reparsea el XLSX.

## Correcciones generalizables descubiertas por F11

### 1. Ventas no pueden depender de una columna total precalculada

El contrato anterior asumía:

```text
sales -> sales_amount
```

El workbook real aporta evidencia atómica:

```text
quantity + unit_sale_price
```

P7 admite ahora dos modos de evidencia:

```text
DIRECT
sales_amount

ATOMIC
quantity + unit_sale_price
```

P7 sólo decide si existe evidencia suficiente. No multiplica.

F8 ejecuta el modo atómico mediante:

```text
SUM_PRODUCT(quantity, unit_sale_price)
```

exclusivamente a través de `FormulaEngineService.calculate_math_primitive()`.

La misma alternativa se aplica a `sales`, al input ventas de `gross_margin` y al input sales de `dso`.

### 2. El fallback de relaciones no puede ser exclusivo de producto

El fallback semántico determinístico proyectaba sólo relaciones asociadas a roles de producto.

F11 lo generaliza a:

```text
left_role == right_role
AND role endswith *_identifier
AND WorkbookProfiler relation exists
```

Por tanto ProductoID y SucursalID atraviesan el mismo mecanismo.

No se agregó un branch `branch_relationship` ni un whitelist de cafetería.

### 3. Múltiples columnas P6 aprobadas requieren selección de fuente coherente

El workbook posee, por ejemplo:

```text
Ventas.ProductoID
Productos.ProductoID

Ventas.SucursalID
Sucursales.SucursalID

Ventas.PrecioUnitario
Productos.Precio
```

F10 no puede entregar todas esas columnas simultáneamente a P8 como si fueran equivalentes.

F10 proyecta ahora un subconjunto P6 específico del AnalysisPlan, manteniendo intactos los significados aprobados.

Criterios:

```text
1. preferred_roles declarados por el template
2. a igualdad semántica, preferencia por el lado fact de relaciones confirmadas
3. menor span de hojas
4. menor cantidad de fuentes
5. empate material restante -> BLOCKED
```

Esto es selección de evidencia aprobada, no inferencia semántica.

Para `sales_by_branch`, el template prefiere `branch_name`, obligando a usar la relación gobernada con `Sucursales` en vez de degradar silenciosamente a un ID.

### 4. Concentración requiere matemática cross-group, no un engine nuevo

F11 introduce el measure genérico:

```text
sales_concentration
```

Ejecución:

```text
sales por grupo
↓
SUM(all group sales)
↓
PYME_033_concentracion_sku
(main_sku_sales / total_sales * 100)
↓
percentage por producto
↓
RANKED
```

La fórmula proviene de `pymia/contracts/formula_rules_v1.json` y se ejecuta por `FormulaEngineService`.

No existe:

```text
ProductConcentrationEngine
CafeteriaConcentrationEngine
if analysis_id == product_sales_concentration
```

La estrategia está declarada por measure y opera sobre cualquier grupo compatible.

## Los seis análisis del gate

### 1. Resumen de ventas

```text
AnalysisKind = SINGLE_VALUE
sales evidence = quantity + unit_sale_price
F8 = SUM_PRODUCT
F9 = ResultSet
```

5000 filas transaccionales atraviesan la cadena.

### 2. Ventas por producto

```text
AnalysisKind = GROUPED
Dimension = PRODUCT
Groups físicos esperados = 15
Relationship materialization = no requerida
Math = mismo sales evidence mode
```

### 3. Margen bruto por producto

```text
AnalysisKind = GROUPED
Dimension = PRODUCT
Relationship = Ventas.ProductoID -> Productos.ProductoID
Ventas = SUM_PRODUCT(quantity, unit_sale_price)
Costos = SUM_PRODUCT(quantity, unit_cost_candidate)
Formula = margen_bruto
Groups = 15
```

### 4. Ventas por sucursal

```text
AnalysisKind = GROUPED
Dimension = BRANCH
preferred role = branch_name
Relationship = Ventas.SucursalID -> Sucursales.SucursalID
Groups físicos = 5
```

Los nombres de grupo se validan contra la tabla `Sucursales` del intake canónico; no están hardcodeados en el test.

### 5. Concentración de producto

F11 usa un template adicional suministrado por la extensión genérica `templates=` de F10. No se agrega todavía al catálogo comercial F10; esa expansión corresponde a F12.

```text
AnalysisKind = RANKED
Dimension = PRODUCT
Measure = sales_concentration
Formula = PYME_033_concentracion_sku
Groups = 15
Ranks = 1..15
SUM(percentages) ~= 100
```

Esto prueba además que agregar un nuevo AnalysisPlan no requiere tocar UI ni crear un runtime particular.

### 6. Evolución mensual de ventas

```text
AnalysisKind = SERIES
Dimension = time
Temporal grain = MONTH
Months físicos = 2026-01 .. 2026-05
Math = mismo atomic sales basis
```

## Reconciliación entre shapes

El gate no se limita a comprobar `READY`. Los distintos shapes deben reconciliar contra un único total transaccional:

```text
sales_total
≈ SUM(sales_by_product)
≈ SUM(sales_by_branch)
≈ SUM(sales_series_month)
```

Además, cada resultado de `sales_concentration` debe transportar ese mismo `sales_total` como denominador gobernado de `PYME_033_concentracion_sku`.

Esto detecta divergencias de evidencia o matemática entre análisis que deberían representar el mismo universo de ventas.

## Alcance honesto de ventas/descuentos

`cafeteria_abc.xlsx` contiene `Descuento` con valores observados:

```text
0
0.05
0.10
0.15
```

F11 no incorpora `discount_candidate` a estos seis AnalysisPlans. Por tanto las ventas derivadas en este gate son **ventas brutas transaccionales según cantidad × precio unitario**, antes de aplicar descuentos.

Esto es deliberado y evita inferir la unidad del descuento sin confirmación específica.

Por tanto F11 **NO certifica**:

```text
net sales after discount
margin after discount
impact of discounts
```

Esos análisis deben usar evidencia de unidad gobernada y pertenecen a expansión F12.

## Relación con F10

F10 continúa siendo discovery-only.

Cuando P8 devuelve `COMPUTABLE`, el item descubierto conserva el `Service1GovernedAnalysisInputV1` exacto como pass-through no ejecutable. F11 consume ese mismo objeto en F7.

```text
F10 does not execute
F10 does not calculate
F10 does not join
```

## Invariantes

```text
ONE_CANONICAL_XLSX_READER = PASS
P6_SEMANTIC_AUTHORITY = PRESERVED
P7_REQUIREMENT_GRAIN_AUTHORITY = PRESERVED
P8_COMPUTABILITY_AUTHORITY = PRESERVED
F7_EVIDENCE_PREPARATION_AUTHORITY = PRESERVED
FORMULA_ENGINE_SINGLE_MATH_AUTHORITY = PRESERVED
F9_RESULT_PROJECTION_AUTHORITY = PRESERVED
F10_DISCOVERY_ONLY = PRESERVED

SPECIAL_BRANCH_PER_ANALYSIS = 0
CAFETERIA_HARDCODE = 0
RUBRO_HARDCODE = 0
SECOND_PARSER = 0
SECOND_MATH_ENGINE = 0
UI_BUSINESS_MATH = 0
LLM_MATH = 0
```

## Archivos de autoridad modificados por F11

F11 hace evolución dirigida, no creación paralela:

```text
service_1_variable_family_bindings_v1.py
  -> evidencia de sales directa o atómica

service_1_computability_v1.py
  -> formula_ref canónico de sales_concentration

service_1_analysis_math_execution_v1.py
  -> atomic sales fallback + estrategia cross-group declarativa

service_1_dynamic_analysis_discovery_v1.py
  -> selección coherente de P6 + pass-through exacto de P8

service_1_deterministic_semantic_proposal_provider_v1.py
  -> relaciones genéricas por matching *_identifier
```

No se modifica:

```text
service_1_product_pipeline_v1.py
service_1_analysis_plan_v1.py
service_1_analysis_evidence_preparation_v1.py
service_1_analysis_result_projection_v1.py
FormulaEngineService
service_1_ui_v1.py
service_1_assisted_web_v1.py
```

## Gate F11

```text
REAL_CAFETERIA_XLSX = PASS
REAL_CANONICAL_INTAKE = PASS
OWNER_CONFIRMED_P6 = PASS
PRODUCT_RELATIONSHIP_CONFIRMED = PASS
BRANCH_RELATIONSHIP_CONFIRMED = PASS

SALES_TOTAL_E2E = PASS
SALES_BY_PRODUCT_E2E = PASS
GROSS_MARGIN_BY_PRODUCT_E2E = PASS
SALES_BY_BRANCH_E2E = PASS
PRODUCT_CONCENTRATION_E2E = PASS
SALES_SERIES_MONTH_E2E = PASS
SHAPE_SALES_TOTAL_RECONCILIATION = PASS

SAME_P7 = PASS
SAME_P8 = PASS
SAME_F7 = PASS
SAME_MATH_AUTHORITY = PASS
SAME_F9 = PASS

CAFE_GENERALIZATION_GATE = PASS
SPECIAL_BRANCH_PER_ANALYSIS = 0
CAFETERIA_HARDCODE = 0
```

## Evidencia de cierre

```text
F11_PHYSICAL_CAFETERIA_GATE = 9 PASS / 0 FAIL
F7_F11_REGRESSION = 64 PASS / 0 FAIL
F1_F6_KERNEL_REGRESSION = 88 PASS / 0 FAIL
SEMANTIC_LEGACY_ARCHITECTURE_REGRESSION = 60 PASS / 0 FAIL
F0_PHYSICAL_GATE = 41 PASS / 0 FAIL
```

Los tres bloques de regresión F1–F11 anteriores son disjuntos y suman `212 PASS / 0 FAIL`. El gate F0 se reporta aparte porque comparte cobertura con el bloque semántico.

La suite completa `pytest -q` fue intentada después de estos gates; el conector MCP devolvió HTTP 502 antes de ejecutar/devolver resultados. Ese evento no se clasifica como fallo de código.

F11 queda congelado porque sus tests físicos y la regresión F0–F10 están verdes y el diff no introduce una autoridad paralela.
