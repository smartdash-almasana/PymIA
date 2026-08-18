# Servicio 1 — F8 Mathematical Aggregation Runtime Spec v1

**Estado:** FROZEN  
**Alcance:** runtime matemático gobernado sobre evidencia preparada F7  
**Fuera de alcance:** findings/resultados narrativos F9, discovery F10, UI, persistencia, delivery y product root

## Decisión congelada

```text
FORMULA_ENGINE_SERVICE_IS_SINGLE_MATH_AUTHORITY
F8_IS_THE_SINGLE_ANALYTICAL_AGGREGATION_RUNTIME
F7_REMAINS_EVIDENCE_PREPARATION_AUTHORITY
P8_REMAINS_COMPUTABILITY_AUTHORITY
NO_SECOND_MATH_ENGINE
NO_CAPABILITY_SPECIFIC_DIMENSIONAL_ENGINE
```

F8 no introduce `CommercialEngine`, `CafeteriaEngine`, `AnalyticsEngine` paralelo ni un `calculate_dimensional()` con ramas por capability/rubro.

## Flujo

```text
AnalysisPlan
+
P8 Service1GovernedAnalysisInputV1
+
F7 Service1PreparedAnalysisEvidenceV1
↓
F8 execute_service_1_analysis_math_v1
↓
Service1AnalysisMathResultV1
↓
F9 futuro: ResultSet / findings / outcomes
```

F8 valida drift de `case_id`, `analysis_id`, `AnalysisPlan`, `resolved grain` y `formula_refs` antes de ejecutar matemática.

## Autoridad matemática

Toda aritmética productiva utilizada por el runtime analítico se ejecuta en:

```text
pymia/services/formula_engine_service.py
FormulaEngineService
```

La autoridad expone dos familias de ejecución:

1. `calculate(formula_id, FormulaInput[])` — fórmulas empresariales canónicas F2;
2. `calculate_math_primitive(MathPrimitiveInput)` — primitivas matemáticas genéricas.

Las primitivas F8 son:

```text
SINGLE_VALUE
SUM
COUNT
AVG
MIN
MAX
SUM_PRODUCT
MULTIPLY
SUBTRACT
PERCENT_OF
```

No contienen semántica de cafetería, rubro, capability ni UI.

## Declaración de medida

F8 mantiene una tabla declarativa mínima de cómo convertir roles gobernados en inputs matemáticos. La tabla no contiene expresiones aritméticas ni implementaciones de fórmula.

Ejemplos:

```text
sales
  direct: sales = SUM(sales_amount)
  atomic fallback: sales = SUM_PRODUCT(quantity, unit_sale_price)
  formula_ref = NONE

gross_margin
  direct ventas: SUM(sales_amount)
  atomic ventas fallback: SUM_PRODUCT(quantity, unit_sale_price)
  costos = SUM_PRODUCT(quantity, unit_cost_candidate)
  formula_ref = margen_bruto

sales_concentration
  group sales = direct-or-atomic sales evidence
  total_sales = SUM(group sales)
  per-group formula_ref = PYME_033_concentracion_sku
  output = percentage

dso
  accounts_receivable = SUM(accounts_receivable_amount)
  sales = direct-or-atomic sales evidence
  days = SINGLE_VALUE(period_days | days)
  formula_ref = PYME_011_dso

projected_cash_balance
  initial_balance = SINGLE_VALUE(initial_balance)
  expected_collections = SUM(expected_collections)
  expected_payments = SUM(expected_payments)
  formula_ref = LIQ_002_saldo_final_proyectado
```

La fórmula empresarial nunca se reescribe dentro de F8. El `formula_ref` debe coincidir con el P8 y se ejecuta mediante `FormulaEngineService.calculate()` contra la fuente canónica F2.

## Grain, groups y ranking

F8 no descubre grupos. Consume exactamente los `member_row_refs` preparados por F7.

Para cada grupo:

```text
F7 member rows
↓
math primitives
↓
optional canonical formula
↓
group mathematical measure
```

`order_by` y `limit` se aplican sólo después de obtener valores matemáticos. Para `RANKED`, F8 asigna `rank` determinístico y luego aplica `limit`.

F8 no genera findings, recomendaciones ni claims de negocio.

## Trazabilidad

Cada medida ejecutada conserva:

```text
measure_ref
value
unit
formula_ref
formula_inputs
source_refs con row lineage
math_trace
```

`math_trace` registra qué primitivas y fórmula canónica participaron sin introducir autoridad narrativa.

## Convergencia de deuda F1/H-02

F8 cierra las dos deudas matemáticas identificadas antes de esta fase:

### GenericCapabilityEngine

Antes:

```text
sum(values, Decimal("0"))
```

Ahora:

```text
MathPrimitiveOperation.SUM
→ FormulaEngineService.calculate_math_primitive()
```

`SINGLE_VALUE` también se valida por la autoridad matemática común.

### Derived Evidence legacy

`service_1_derived_evidence_v1.py` conserva responsabilidades de evidencia legacy:

```text
selección de columnas confirmadas
validación de relación owner-confirmada
lookup de evidencia
validación de unidad de descuento
lineage / coverage
```

pero ya no ejecuta directamente:

```text
qty * unit_price
qty * unit_cost
sales_total += ...
costs_total += ...
discount arithmetic
```

Estas operaciones delegan a `FormulaEngineService` mediante `MULTIPLY`, `SUBTRACT`, `PERCENT_OF` y `SUM`.

Los joins no son clasificados como matemática: la preparación y materialización de relaciones pertenece a F7. El camino legacy puede conservar temporalmente su lookup gobernado mientras no se convierta en autoridad aritmética.

## Diferencia respecto de la auditoría externa

Se acepta el hallazgo H-02 sobre matemática fuera del Kernel. No se adopta el diseño sugerido de `calculate_dimensional()` con ramas por `formula_id`/capability para agregación dimensional.

La solución F8 es:

```text
semantic measure specification
→ generic math primitives
→ canonical FormulaEngineService formula execution
```

sin engine por rubro ni capability.

## Contrato de salida

`Service1AnalysisMathResultV1` es un resultado matemático intermedio, no el ResultSet productivo F9.

Mantiene:

```text
runtime_authorized = False
tool_execution_authorized = False
product_ready = False
delivery_authorized = False
diagnosis_generated = False
analysis_execution_authorized = False
```

Y registra únicamente como evidencia factual de ejecución:

```text
mathematical_execution_performed = True
aggregation_execution_performed = True|False según resultado
formula_execution_performed = True|False
ranking_execution_performed = True|False
```

## Gate F8

```text
MATH_PRIMITIVES_OWNED_BY_FORMULA_ENGINE = PASS
SINGLE_VALUE = PASS
SUM = PASS
COUNT = PASS
AVG = PASS
MIN = PASS
MAX = PASS
SUM_PRODUCT = PASS
MULTIPLY = PASS
SUBTRACT = PASS
PERCENT_OF = PASS

SALES_TOTAL = PASS
SALES_GROUPED = PASS
GROSS_MARGIN_GROUPED = PASS
DSO = PASS
PROJECTED_CASH_BALANCE = PASS
RANK_AND_LIMIT = PASS

P8_FORMULA_REF_DRIFT_FAIL_CLOSED = PASS
INVALID_NUMERIC_EVIDENCE_FAIL_CLOSED = PASS

GENERIC_CAPABILITY_SUM_DEBT_CONVERGED = PASS
DERIVED_EVIDENCE_RAW_BUSINESS_MATH_REMOVED = PASS

NO_PRODUCT_ROOT_CHANGE = REQUIRED
NO_P7_CHANGE = REQUIRED
NO_P8_CHANGE = REQUIRED
NO_UI_CHANGE = REQUIRED
NO_FINDING_GENERATION = PASS
NO_SECOND_MATH_ENGINE = PASS
```

F8 queda cerrado sólo si las regresiones F0–F7 y los gates de autoridad matemática permanecen verdes.
