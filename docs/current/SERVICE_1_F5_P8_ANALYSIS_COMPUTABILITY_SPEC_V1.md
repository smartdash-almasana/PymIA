# Servicio 1 — F5 P8 Analysis Computability Spec v1

**Estado:** FROZEN  
**Alcance:** extensión del P8 canónico para computabilidad declarativa de `AnalysisPlanV1`  
**Fuera de alcance:** ejecución analítica, joins materiales F7, agregación F8, ResultSet F9, discovery F10, UI y product root

## Decisión congelada

```text
P8_IS_ANALYSIS_COMPUTABILITY_AUTHORITY
P7_REMAINS_REQUIREMENT_AND_GRAIN_RESOLUTION_AUTHORITY
FORMULA_ENGINE_REMAINS_MATH_AUTHORITY
ANALYSIS_EXECUTION_AUTHORITY = NONE
```

F5 extiende el P8 existente en `pymia/smartpyme/service_1_computability_v1.py`. No crea un segundo P8, un `AnalysisEngine`, un dispatcher productivo ni una ruta paralela.

## Flujo F5

```text
Service1AnalysisPlanV1
+
P6 APPROVED semantic evidence
+
Service1AnalysisRequirementMatchV1 from P7
+
confirmed relationship evidence when required
↓
P8 build_service_1_analysis_computability_decision_v1
↓
COMPUTABLE | NEEDS_EVIDENCE | UNSUPPORTED | BLOCKED
↓
Service1GovernedAnalysisInputV1 only when COMPUTABLE
```

`COMPUTABLE` significa que la evidencia y los contratos son suficientes para preparar una ejecución gobernada futura. No significa que F5 ejecute el análisis ni que el runtime de agregación ya exista.

## GovernedAnalysisInputV1

El contrato contiene:

```text
case_id
analysis_plan
source_bindings
relationship_bindings
resolved grain
formula_refs
safety_flags
provenance
```

Mantiene siempre:

```text
runtime_authorized = False
tool_execution_authorized = False
product_ready = False
delivery_authorized = False
diagnosis_generated = False
analysis_execution_authorized = False
```

Los `source_bindings` son roles semánticos P6 aprobados resueltos a una única columna física por rol requerido. F5 bloquea grupos alternativos ambiguos, múltiples columnas candidatas para el mismo rol y reutilización de una misma columna para roles distintos.

## Integridad P7 → P8

P8 valida antes de declarar computabilidad:

1. `analysis_id` coincide entre plan y P7;
2. `requested_grain` no deriva entre F3 y P7;
3. `required_relationship_refs` coincide con el plan;
4. `resolved_grain` de P7 coincide con el grain solicitado en sus tres ejes;
5. las columnas/roles reportados por P7 provienen de las decisiones P6 entregadas;
6. las decisiones P6 pertenecen al mismo `case_id` y están `APPROVED`.

Cualquier drift material bloquea fail-closed.

## Relationships

F5 no resuelve joins ni endpoints. Si el plan exige `relationship_refs`, P8 exige evidencia de relación ya confirmada y la transporta como `relationship_bindings`.

Reglas:

```text
required relationship missing
→ NEEDS_EVIDENCE

relationship present but not confirmed_by_owner
→ NEEDS_EVIDENCE

undeclared relationship injected
→ BLOCKED

relationship ref mismatch
→ BLOCKED
```

La definición semántica general de relaciones pertenece a F6 y el join material pertenece a F7. F5 sólo gobierna su suficiencia como evidencia.

## Extensión declarativa de requisitos usada por F5

F5 reutiliza el mismo P7 canónico y amplía únicamente su tabla declarativa de requisitos de medida para poder producir decisiones P8 sobre los ejemplos del roadmap. No cambia la autoridad de P7, no modifica su resolución de grain y no agrega ejecución.

## Measures cubiertas por computabilidad F5

F5 no calcula ninguna medida. Sólo declara requisitos y `formula_refs` cuando corresponde.

```text
sales
required evidence mode: sales_amount OR (quantity + unit_sale_price)
formula_refs: none

 gross_margin
required evidence mode: [sales_amount OR (quantity + unit_sale_price)] + quantity + unit_cost_candidate
formula_refs: margen_bruto

 sales_concentration
required evidence mode: sales_amount OR (quantity + unit_sale_price)
formula_refs: PYME_033_concentracion_sku

 units
required roles: quantity
formula_refs: none

 row_count
required roles: transaction_identifier
formula_refs: none

 catalog_price_variance_pct
required roles: quantity + unit_sale_price + list_price
formula_refs: precio_catalogo_variacion_pct

 dso
required evidence mode: accounts_receivable_amount + [sales_amount OR (quantity + unit_sale_price)] + (period_days OR days)
formula_refs: PYME_011_dso

 projected_cash_balance
required roles: initial_balance + expected_collections + expected_payments
formula_refs: LIQ_002_saldo_final_proyectado
```

Para `sales`, la agregación futura (`SUM`, grouping, series, ranking) no se modela como fórmula de negocio en F5. Su runtime pertenece a F8.

Los `formula_refs` existentes se validan contra la fuente canónica F2 `pymia/contracts/formula_rules_v1.json`, pero F5 no llama al `FormulaEngineService`.

## Ejemplos de decisión

```text
ventas por producto
P7 MATCH + sales evidence mode + product
→ COMPUTABLE

ventas por sucursal
P7 MATCH + sales evidence mode + branch
→ COMPUTABLE

serie ventas por día
P7 MATCH + sales evidence mode + operation_date
→ COMPUTABLE

ranking ventas por producto
P7 MATCH
→ COMPUTABLE

margen bruto por producto
sales evidence mode + quantity + unit_cost_candidate + product + relación confirmada cuando el plan la exige
→ COMPUTABLE

DSO sin cuentas por cobrar/período
→ NEEDS_EVIDENCE

caja proyectada sin cobranzas/pagos esperados
→ NEEDS_EVIDENCE
```

## Separación de autoridades

```text
AnalysisPlan = intención declarativa
P6 = evidencia semántica aprobada
P7 = requisitos + resolved grain
P8 = computabilidad
F6 = semántica/relaciones generales
F7 = preparación material de evidencia/joins/groups
F8 = matemática de agregación y fórmulas
```

F5 no hace:

```text
SUM
COUNT
AVG
RANK
join
row selection
group membership
formula execution
result set
product dispatch
```

## Gate F5

```text
P8_SINGLE_AUTHORITY = PASS
GOVERNED_ANALYSIS_INPUT = PASS
P7_TO_P8_DRIFT_GATES = PASS
SINGLE_VALUE_COMPUTABILITY = PASS
GROUPED_COMPUTABILITY = PASS
SERIES_COMPUTABILITY = PASS
RANKED_COMPUTABILITY = PASS
RELATIONSHIP_EVIDENCE_GATE = PASS
MARGIN_BY_PRODUCT_COMPUTABILITY = PASS
DSO_NEEDS_EVIDENCE = PASS
PROJECTED_CASH_NEEDS_EVIDENCE = PASS
NO_ANALYSIS_EXECUTION = PASS
NO_PRODUCT_ROOT_CHANGE = REQUIRED
NO_MATH_RUNTIME_CHANGE = REQUIRED
```
