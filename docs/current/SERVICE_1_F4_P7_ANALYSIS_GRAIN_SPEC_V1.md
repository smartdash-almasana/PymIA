# Servicio 1 — F4 P7 Analysis Grain Spec v1

**Estado:** FROZEN  
**Alcance:** extensión del P7 canónico para requisitos analíticos y grain resuelto  
**Fuera de alcance:** P8/F5, semántica relacional F6, joins F7, agregación F8, product root, UI y discovery

## Decisión congelada

```text
P7_IS_REQUIREMENT_AND_GRAIN_RESOLUTION_AUTHORITY
REQUESTED_GRAIN = AnalysisPlan intent
RESOLVED_GRAIN = Service1GrainV1 emitted by P7
REQUIRED_RELATIONSHIPS = requirements only
RELATIONSHIP_RESOLUTION = NOT_F4
P8_COMPUTABILITY = NOT_F4
ANALYSIS_EXECUTION = NONE
```

F4 extiende el P7 existente en `service_1_variable_family_bindings_v1.py`; no crea un segundo P7 ni un engine analítico paralelo.

## Flujo F4

```text
Service1AnalysisPlanV1
+
P6 APPROVED decisions
↓
P7 build_service_1_analysis_requirement_match_v1
↓
Service1AnalysisRequirementMatchV1
  required_role_groups
  satisfied_role_groups
  missing_role_groups
  requested_grain
  resolved_grain
  required_relationship_refs
```

`resolved_grain` sólo existe con `REQUIREMENT_MATCHED`. Cualquier estado incompleto o bloqueado sale sin grain resuelto.

## Grain canónico resuelto

`Service1GrainV1` sigue siendo el contrato de grain resuelto y soporta:

```text
business entity:
TRANSACTION
LINE_ITEM
INVOICE
CUSTOMER
SUPPLIER
PRODUCT
CATEGORY
BRANCH
EMPLOYEE
CHANNEL
PAYMENT_METHOD
ACCOUNT
NONE

temporal:
EVENT
DAY
WEEK
MONTH
QUARTER
YEAR
HOUR
PERIOD
NONE

aggregation:
ATOMIC
GROUPED
AGGREGATED
```

Los grains empresariales compuestos son genéricos mediante `+`, por ejemplo `PRODUCT+BRANCH`. Cada componente debe ser un grain base válido y no puede repetirse. `NONE` no puede combinarse con otro componente.

## Requisitos analíticos mínimos F4

```text
measure sales
→ sales_amount
OR
→ quantity + unit_sale_price

F11 refinement: P7 selects the direct mode when `sales_amount` exists; otherwise it accepts atomic line evidence `quantity + unit_sale_price`. P7 still does not calculate the derived amount.

dimension product
→ product_identifier OR product_name

dimension branch
→ branch_identifier OR branch_name

dimension category
→ commercial_category

dimension employee
→ employee_identifier OR employee_name

dimension channel
→ sales_channel

dimension payment_method
→ payment_method

dimension transaction
→ transaction_identifier

dimension time + DAY/WEEK/MONTH
→ operation_date

dimension time + HOUR
→ operation_time
```

Regla estricta:

```text
sales_channel != branch_identifier
sales_channel != branch_name
```

Por lo tanto `sales_channel` nunca satisface la dimensión `branch`.

Los roles `branch_identifier`, `branch_name` y `operation_time` pueden todavía no ser producidos por la semántica vigente. F4 sólo define su contrato P7; su incorporación semántica productiva pertenece a F6.

## Requested grain vs resolved grain

`Service1RequestedAnalysisGrainV1` permanece inalterado y expresa intención analítica. P7 valida que las decisiones P6 aprobadas satisfagan los roles requeridos y, sólo entonces, proyecta el mismo grain solicitado como `Service1GrainV1` resuelto con `structural_scope=REGION`.

F4 no inventa un grain alternativo ni modifica el AnalysisPlan.

## Relationships

`AnalysisPlan.relationship_refs` se proyecta sin transformación a `required_relationship_refs`.

P7 no confirma relaciones, no resuelve joins y no ejecuta relaciones. La resolución semántica relacional corresponde a F6 y la preparación material de joins a F7.

## Autoridad

`Service1AnalysisRequirementMatchV1` es inmutable y mantiene siempre:

```text
runtime_authorized = False
tool_execution_authorized = False
delivery_authorized = False
diagnosis_generated = False
```

P7 no calcula, no ejecuta fórmulas y no decide computabilidad. P8 conserva íntegramente la autoridad de computabilidad y `FormulaEngineService` conserva la autoridad matemática.

## Gate F4

```text
P7_SINGLE_AUTHORITY = PASS
ANALYSIS_REQUIREMENT_MATCH = PASS
RESOLVED_GRAIN = PASS
COMPOSITE_GRAIN = PASS
BRANCH_NOT_CHANNEL = PASS
REQUIRED_RELATIONSHIPS_ARE_REQUIREMENTS_ONLY = PASS
P8_UNCHANGED = REQUIRED
PRODUCT_ROOT_UNCHANGED = REQUIRED
MATH_AUTHORITY_UNCHANGED = REQUIRED
NO_ANALYSIS_EXECUTION = PASS
```
