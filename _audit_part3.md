## 16. Capability Model Audit

### 16.1 ¿Qué es una capability hoy?

Hay **mezcla de niveles conceptuales** (documentado como inconsistencia):

| Capability | Nivel conceptual |
|---|---|
| `sold_vs_collected_gap` | Pregunta de negocio + fórmula + patología |
| `net_margin_real` | Pregunta de negocio + fórmula + patología |
| `projected_closing_cash_balance` | Fórmula/indicador |
| `dso`, `current_ratio`, `inventory_turnover` | Fórmula/indicador |
| `sales_concentration`, `interest_burden_ratio`, `index_update_ratio` | Fórmula/indicador |
| `adjusted_operating_cash_flow`, `reorder_point` | Fórmula/indicador |
| `payment_collection_gap` | Composición de 2 resultados (COMPOSITE) |
| `working_capital` (launch ref) | Agregado de 3 capabilities (service-level, no capability real) |

Una misma entrada de menú (`working_capital`) NO es una capability del registry; la web lo alinea a `_WORKING_CAPITAL_COMPONENT_CAPABILITIES` en 3 capabilities. Esto confirma que capability mezcla: pregunta de negocio, fórmula, patología y unidad de delivery.

### 16.2 Escalabilidad

El registry (11) + engine genérico (árbol binario + classify + outcome policy) puede crecer a decenas de *fórmulas escalares*, pero NO a análisis por múltiples grains. Añadir una capability grupal (ventas por producto) hoy requiere:

```text
1. nuevo rol semántico en _ROLE_RULES (o reuso: product_identifier, quantity, unit_sale_price, ...)
2. nueva family en VARIABLE_FAMILY_DEFINITIONS (con grain PRODUCT×PERIOD)
3. nueva capability en registry (o macrocapability)
4. nueva fórmula (posiblemente fuera de Kernel)
5. nuevo evaluador (agregación con GROUP BY, ranking, participaciones)
6. nuevo outcome policy
7. nuevo wiring en product root (elif / capability_definition)
8. nueva UI entry en _REVIEW_OPTIONS/_LAUNCH_REVIEW_OPTIONS + preflight roles
```

Ese es el blast radius de cada análisis nuevo: 5-8 toques. La pregunta 10 del prompt (¿escala a cientos?): NO con el modelo actual para análisis grupales.

---

## 17. P7 / Grain Audit

### 17.1 Grain soportado (físicamente)

Grain existe en 3 lugares:

1. `Service1GrainV1` (structural_scope, business_entity_grain, temporal_grain, aggregation_grain)
2. `Service1RequirementMatchV1.grain` (P7)
3. `Service1GovernedComputationInputV1.grain` (P8 → entregado a ejecución)

PERO el grain NO se traduce en plan de ejecución:

- `_resolve_atomic_inputs` (generic) agrega toda la columna → aborrada grain.
- `evaluate_liq_001_from_normalized_tables_v1` agrega toda la columna → aborrada grain.
- `evaluate_ren_001` usa Derived Evidence (que agrega todo el período) → aborrada grain.
- No existe `group_by` en ningún `GovernedComputationInputV1` ni en ningún plan.

### 17.2 Capacidad de modelar análisis del café

| Análisis | ¿P7 lo modela? | ¿P8/evaluador lo ejecuta? |
|---|---|---|
| ventas por producto | no hay family PRODUCT_* | NO |
| ventas por sucursal | CASH_COLLECTIONS es ATOMIC/REGION | ATOMIC (hosteado) |
| margen por categoría | SALES_MARGIN es ATOMIC | ATOMIC, sin join de Productos |
| ventas por hora | family temporal NONE | NO |
| producto × sucursal | grain NINGUNO | NO |
| ticket promedio por día | family temporal NONE | NO |

**Respuesta clave**: P7 está diseñado alrededor de capabilities escalares por variable/family; el grain es declarativo, no computable. Para modelar los análisis multidimensionales del café, P7 necesita: (a) families con grain no-trivial (business_entity_grain=PRODUCT, temporal_grain=DAY/HOUR), y (b) un consumidor que genere planes de agregación según grain.

---

## 18. P8 / Computability Audit

### 18.1 Qué considera computable P8

P8 declara COMPUTABLE cuando:

- P6 APPROVED para todos los roles requeridos de la family;
- la family está matched (P7);
- la matrix tiene exactamente 1 fórmula mapeada;
- la fórmula es CALCULABLE;
- `required_variables ⊆ source_bindings` (directas o Derived);
- existe `GovernedComputationInputV1`.

### 18.2 Lo que NO soporta

- N conjuntos de inputs para la misma capability (sólo un conjunto de bindings).
- Inputs multidimensionales (arrays, series, listas de grupos).
- Resultados multidimensionales (un `computed` plano por capability).
- Join products por grupo (sólo existe join en Derived Evidence para 2 sheets).
- Derived por grain: `_validated_derived_source_bindings` acepta un único packet para REN_001, no packets por grupo.
- Bypasses: composite (`working_capital`) y legacy pre-confirmed (owner_answers) — documentados, no "sombra".

---

## 19. Product Root Audit

`service_1_product_pipeline_v1.py` es el único root productivo real. Cumple:

- `ONE_CANONICAL_PRODUCT_ROOT` (web/CLI son entradas que llaman este root).
- `NO_SECOND_XLSX_PARSER` (aunque el intake de web usa `read_xlsx_*` canónico; el `landing/build_service1_excel_ingestion_chat_web.py` usa openpyxl para *contexto de chat demostrativo*, NO es ruta productiva).
- **Limitación**: el root tiene branches específicos por capability (LIQ_001, REN_001) ANTES del generic. Una capability nueva ATOMIC no-LIQ/REN pasa por el generic; una capacidad grupal no tiene casa. Ese dual-path (especializado vs genérico) es la causa de que cada análisis nuevo requiera wiring manual en el root si necesita delivery u outcome especial (ver `_delivery_block_reason`).

---

## 20. Duplicate Authorities / Architecture Drift

### 20.1 Duplicaciones detectadas (físicas)

| Duplicación | Ubicación | Severidad |
|---|---|---|
| Fórmulas escalares en dos lugares | `SUPPORTED_FORMULAS` (kernel) vs `FormulaNodeV1` (registry) | MEDIA: riesgo de drift (PYME_026/PYME_013 ya drifted) |
| DSO/PYME_013 en registry y matrix incompleto | `dpo`/`payment_collection_gap` no en evidence matrix | MEDIA: P8 no puede gobernarlas |
| Dos rutas semánticas | legacy determinístico vs asistido F2 | MEDIA: mantenimiento doble, misma firma |
| `run_owner_reentry` fuera del root | adapter SUPPORT_NECESSARY (compat CLI/harness) | BAJA (documentado como deuda) |
| Menú duplicado | `_REVIEW_OPTIONS` (12) vs `_LAUNCH_REVIEW_OPTIONS` (3) vs discovery | ALTA: 3 fuentes de verdad para lo que se ofrece |
| `_available_launch_review_options_v1` preflight | web usa preflight de roles; discovery usa P8 | DUPLICADA: dos mecanismos de disponibilidad |
| Patologías documento vs matrix | docs/current claims 12 patologías productivas; matrix tiene 10 | DRIFT documentado |

### 20.2 Derivación de la respuesta a "¿matemática fuera del Kernel?"

Existe matemática de agregación fuera del Kernel: suma de columnas en evaluadores y multiplicación/join en Derived Evidence. **No viola materialmente la arquitectura** (la fórmula final del negocio queda en el Kernel), pero es matemática de *derivación* y debería quedar normalizada como "aggregation layer" para no depender de que cada evaluador la reimplemente.

---

## 21. cafeteria_abc.xlsx Evidence Profile

```text
Sheets (físico): Ventas (5001 filas), Sucursales (6), Productos (16)

Ventas columnas: VentaID, Fecha, Hora, SucursalID, ProductoID, Cantidad,
                 PrecioUnitario, MetodoPago, CanalVenta, Descuento, Empleado
Sucursales: SucursalID, Sucursal, Ciudad
Productos:  ProductoID, Producto, Categoria, Costo, Precio

Relaciones candidatas (profiler): Ventas.ProductoID -> Productos.ProductoID (FK)
                                  Ventas.SucursalID -> Sucursales.SucursalID (FK)

Semántica confirmada por determinismo (roles disponibles):
  operation_date (Fecha), quantity (Cantidad), unit_sale_price (PrecioUnitario),
  discount_candidate (Descuento), product_identifier (ProductoID/Productos),
  unit_cost_candidate (Productos.Costo), list_price (Productos.Precio),
  sales_channel (CanalVenta), payment_method (MetodoPago),
  employee (Empleado - rol añadido en main por 8a04c5d), customer? no

Lo que NO hay: initial_balance, expected_collections/payments, collected_amount,
  period_sales_total/costs_total/taxes_total, accounts_receivable_amount, days,
  current_assets/liabilities, ...

DISCOVERY REAL (sonda): available=[] / blocked=[
  sold_vs_collected_gap (NEEDS_EVIDENCE: falta collected_amount),
  net_margin_real (NEEDS_EVIDENCE: falta costs_total/taxes_total del período),
  working_capital (NEEDS_EVIDENCE: falta initial_balance...)
]
```

Conclusiones sobre el fixture:

1. El café es un workbook **de operación** (transaccional), no de *estados financieros* (no tiene cobranzas, cuentas por cobrar, caja, inventario, impuestos).
2. Por tanto, la arquitectura correcta NO dice "cafetería no se puede analizar": el menú de análisis disponibles DEBE depender de la evidencia (y el discovery lo hace correctamente: 0 disponibles, 3 bloqueados con causa).
3. Los análisis legítimamente computables de un workbook de ventas (ventas netas, descuentos, unidades, operaciones, ticket promedio, ranking, mix por producto/sucursal/hora, participación, calidad de datos, demanda observada) **NO tienen representación** en capabilities/registry/formulas/evaluators ACTUALES.

---

## 22. Cafeteria Analytical Fit Matrix

Para cada análisis materialmente posible del café, usando los soportes reales:

```text
ANALYSIS: Ventas brutas (suma PrecioUnitario×Cantidad)
BUSINESS_QUESTION: ¿Cuánto vendió la operación en el período?
XLSX_EVIDENCE: Ventas[PrecioUnitario, Cantidad]
SEMANTIC_ROLES_REQUIRED: unit_sale_price, quantity
RELATIONSHIPS_REQUIRED: none
GRAIN: período
SEMANTIC_SUPPORT: FULL
P6_SUPPORT: YES
P7_SUPPORT: PARTIAL (family SALES_MARGIN exige product/quantity/price/cost -> no hay cost)
P8_SUPPORT: NO (no formula for ventas; matrix no tiene)
DERIVED_EVIDENCE_SUPPORT: NONE (sólo REN_001)
KERNEL_FORMULA_SUPPORT: NONE
EVALUATOR_SUPPORT: NONE
OUTCOME_SUPPORT: NONE
DELIVERY_SUPPORT: NONE
CURRENT_PRODUCT_PATH: NO
FINAL_STATUS: MISSING_MATH
EXACT_GAP: no existe fórmula de ventas netas/brutas; la agregación de una columna
           (generic) sólo soporta SUM de una variable, no multiplicación de 2 columnas.

ANALYSIS: Ventas netas (descuento aplicado)
BUSINESS_QUESTION: ¿Cuánto vendió neto de descuentos?
XLSX_EVIDENCE: Ventas[PrecioUnitario, Cantidad, Descuento]
SEMANTIC_ROLES_REQUIRED: unit_sale_price, quantity, discount_candidate
GRAIN: PERIOD
SEMANTIC_SUPPORT: PARTIAL (discount unit requiere owner)
P6_SUPPORT: YES
P7_SUPPORT: PARTIAL
P8_SUPPORT: NO
DERIVED_EVIDENCE_SUPPORT: PARTIAL (tiene _apply_discount pero hardcodeada a REN_001)
KERNEL_FORMULA_SUPPORT: NONE
EVALUATOR_SUPPORT: NONE
OUTCOME_SUPPORT: NONE
DELIVERY_SUPPORT: NONE
CURRENT_PRODUCT_PATH: NO
FINAL_STATUS: MISSING_MATH
EXACT_GAP: no hay fórmula de venta neta con descuento.

ANALYSIS: Ticket promedio
BUSINESS_QUESTION: ¿Cuál es el ticket promedio por operación?
XLSX_EVIDENCE: VentaID, PrecioUnitario, Cantidad
SEMANTIC_ROLES_REQUIRED: operation_id, sales_amount, quantity
GRAIN: TRANSACTION/PERIOD
SEMANTIC_SUPPORT: PARTIAL
P6/P7/P8: PARTIAL/NO
KERNEL_FORMULA_SUPPORT: NONE
FINAL_STATUS: MISSING_MATH
EXACT_GAP: no hay fórmula de promedio/divididos; un "SUM(col)/COUNT(rows)" no existe.

ANALYSIS: Unidades vendidas por producto
BUSINESS_QUESTION: ¿Qué productos se venden más en unidades?
XLSX_EVIDENCE: Ventas[ProductoID, Cantidad]
SEMANTIC_ROLES_REQUIRED: product_identifier, quantity
GRAIN: PRODUCT×PERIOD
SEMANTIC_SUPPORT: FULL
P6_SUPPORT: YES
P7_SUPPORT: PARTIAL (no hay family "sales by product")
P8_SUPPORT: NO (matrix sin mapping)
KERNEL: NONE
EVALUATOR: NONE
OUTCOME: NONE
DELIVERY: NONE
CURRENT_PRODUCT_PATH: NO
FINAL_STATUS: MISSING_MATH
EXACT_GAP: no existe GROUP BY product; "SUM(cantidad) group by product" no existe.

ANALYSIS: Ventas por sucursal
BUSINESS_QUESTION: ¿Cuáles sucursales concentran la venta?
XLSX_EVIDENCE: Ventas[SucursalID, PrecioUnitario, Cantidad]
SEMANTIC_ROLES_REQUIRED: branch_identifier, sales_amount
GRAIN: SUCURSAL×PERIOD
SEMANTIC_SUPPORT: PARTIAL (branch rol existe, sales_amount no directo)
P6: YES
P7/P8: NO
KERNEL: NONE
FINAL_STATUS: MISSING_MATH
EXACT_GAP: GROUP BY branch no existe.

ANALYSIS: Mix por categoría (ventas por Categoria)
BUSINESS_QUESTION: ¿Qué categorías aportan más?
XLSX_EVIDENCE: Ventas[ProductoID] × Productos[Categoria]
RELATIONSHIPS_REQUIRED: Ventas.ProductoID->Productos.ProductoID (confirmada)
GRAIN: CATEGORY×PERIOD
SEMANTIC_SUPPORT: FULL
P6: YES (join relation confirmed)
P7/P8: NO
KERNEL: NONE
EVALUATOR: NONE
FINAL_STATUS: MISSING_MATH
EXACT_GAP: join por grupo con categoría no existe.

ANALYSIS: Margen bruto por producto/categoría
BUSINESS_QUESTION: ¿Cuál es la ganancia bruta por producto?
XLSX_EVIDENCE: Ventas[Cantidad, PrecioUnitario] × Productos[Costo]
SEMANTIC_ROLES_REQUIRED: quantity, unit_sale_price, unit_cost_candidate, product_identifier
RELATIONSHIPS_REQUIRED: Ventas.ProductoID->Productos.ProductoID
GRAIN: PRODUCT×PERIOD
SEMANTIC_SUPPORT: FULL
P6: YES
P7: PARTIAL (no agrupa por producto)
P8: NO
DERIVED_EVIDENCE: PARTIAL (puede sumar todo el período, no por producto)
KERNEL: margen_bruto existe pero escalar sobre totales; no por producto
EVALUATOR: NONE
OUTCOME: NONE
FINAL_STATUS: MISSING_MATH + MISSING_DERIVATION
EXACT_GAP: Derived Evidence no puede emitir margen por producto porque no puede
           generar arrays por grupo; kernel no agrupa.
```

Resumen de la matriz (17 análisis lista del prompt §9):

```text
END_TO_END_SUPPORTED:  0/17
PARTIAL (sin producto): ~5/17  (ventas brutas, unidades, ticket, mix sucursal, calidad de datos)
MISSING_MATH:          ~7/17  (ventas netas, ranking, concentración, margen por producto/cat/sucursal)
MISSING_DERIVATION:    ~3/17  (margen por producto/cat/sucursal, join)
NOT_COMPUTABLE_FROM_WORKBOOK: ~2/17 (margen neto real sin impuestos, working capital)
```

Ninguno de los 17 análisis legítimos del café tiene `CURRENT_PRODUCT_PATH: YES` con el estado HEAD+worktree actual.

---

## 23. Service 1 Complete Product Gap

Journey general (del prompt §1: subir → inspeccionar → comprender → LLM semántico → preguntar ambigüedad → evidencia gobernada → computabilidad → exponer sólo lo computable → explicar lo no computable → selección → reutilizar misma verdad → cálculo determinístico → trazabilidad → no exceder evidencia → agregar análisis sin miniaplicación):

```text
SUPPORTED (físico, hoy):
  subir Excel (intake canónico)                          OK
  inspeccionar workbook (profiler)                        OK
  comprender columnas (roles determinísticos)             OK
  asistencia semántica LLM (frontera)                     OK (código; no activo en prod)
  preguntar ambigüedad (dialogue)                         OK
  evidencia gobernada (P6/P7/P8)                          OK
  computabilidad por capability                           OK (para las 10 de matrix)
  exponer sólo lo computable (bajo disponibilidad web)    OK (preflight / discovery F3)
  explicar lo no computable (blocked options UI)          OK (F3 worktree)
  reutilizar misma verdad semántica                       OK (semantic_run_override)
  cálculo determinístico                                  OK (kernel/generic/LIQ/REN)
  trazabilidad (source refs, provenance, delivery hash)    OK
  no exceder evidencia (fail-closed, forbidden claims)     OK

PARTIAL:
  agregar análisis sin miniaplicación                   KO (por capability escalar sí;
                                                          por grain grupal NO)
  memoria de ejecución durable completa                 PARCIAL (sólo owner evidence durable)
  series longitudinales                                 KO

ARCHITECTURALLY_BLOCKED:
  análisis multidimensionales (grupo/temporal/join)     KO (grain declarativo, no computable)
```

% aproximado del journey del prompt: ~9-10 de 15 apoyos SUPPORTED; 2 archit.-blocked. La falta es casi toda de escala/matemática de agregación, no de semántica/gobierno.
