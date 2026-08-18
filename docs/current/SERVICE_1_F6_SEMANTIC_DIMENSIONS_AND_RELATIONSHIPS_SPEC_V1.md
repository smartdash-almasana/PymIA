# Servicio 1 — F6 Semantic Dimensions and Relationships Spec v1

**Estado:** FROZEN  
**Alcance:** semántica dimensional explícita y relaciones owner-confirmables generales  
**Fuera de alcance:** joins/materialización F7, agregación F8, ResultSet, discovery, UI y product-root wiring nuevo

## Decisión congelada

```text
DIMENSIONAL_SEMANTICS_AUTHORITY = existing semantic chain / ColumnUnderstanding + P6
STRUCTURAL_RELATIONSHIP_EVIDENCE = WorkbookProfiler
OWNER_RELATIONSHIP_EVIDENCE = Service1OwnerRelationshipConfirmationEventV1
RELATIONSHIP_BINDING_PROJECTION = build_service_1_confirmed_relationship_bindings_v1
RELATIONSHIP_JOIN_EXECUTION = NONE
P7_REMAINS_REQUIREMENT_AND_GRAIN_AUTHORITY
P8_REMAINS_COMPUTABILITY_AUTHORITY
```

F6 no crea un segundo sistema semántico ni un segundo relationship engine. Extiende las superficies existentes para que sucursal, ubicación, hora y transacción sean conceptos first-class y para que las relaciones confirmadas por el dueño puedan proyectarse de forma uniforme hacia P8.

## Roles dimensionales explícitos

La capa determinística de comprensión de columnas reconoce ahora, además de los roles existentes:

```text
branch_identifier
branch_name
city
operation_time
transaction_identifier
```

Variables canónicas asociadas:

```text
branch_identifier      → branch_id
branch_name            → branch_name
city                   → city
operation_time         → operation_time
transaction_identifier → transaction_id
```

Estos roles son hipótesis semánticas gobernadas. La propuesta semántica no autoriza runtime, computabilidad, joins ni cálculo.

## Regla estricta de sucursal vs canal

```text
sales_channel != branch_identifier
sales_channel != branch_name
sales_channel != city
```

Los headers de sucursal/local/tienda se excluyen explícitamente de `sales_channel`.

Ejemplos:

```text
SucursalID → branch_identifier
Sucursal   → branch_name
CanalVenta → sales_channel
Ciudad     → city
```

Una sucursal es una dimensión física/organizacional. Un canal es el medio comercial por el que se realiza la venta. No son aliases.

## Hora y transacción

```text
Hora / HoraVenta / HoraOperacion → operation_time
VentaID / TransactionID / OperacionID → transaction_identifier
```

`operation_time` habilita el requisito temporal de `HOUR` ya definido por P7. `transaction_identifier` identifica una operación y no sustituye `document_reference` ni `product_identifier`.

## Relaciones estructurales generales

`WorkbookProfiler` ya detectaba relaciones por evidencia física de valores, cardinalidad y cobertura, sin semántica de rubro. F6 congela esa característica como comportamiento general.

Ejemplos equivalentes:

```text
Ventas.ProductoID  -> Productos.ProductoID
Ventas.SucursalID  -> Sucursales.SucursalID
```

Ambas pueden ser `MANY_TO_ONE` si la evidencia estructural lo demuestra.

No existe lógica especial para producto, cafetería o sucursal.

## Confirmación del dueño

`Service1OwnerRelationshipConfirmationEventV1` continúa siendo la evidencia canónica de que el dueño confirmó una relación material.

F6 agrega una referencia relacional determinística:

```text
<LeftSheet>.<LeftColumn>-><RightSheet>.<RightColumn>
```

y una proyección canónica:

```text
build_service_1_confirmed_relationship_bindings_v1(...)
```

que produce bindings consumibles por P8.

La proyección mantiene siempre:

```text
confirmed_by_owner = True
relationship_resolution_authorized = False
join_execution_authorized = False
runtime_authorized = False
tool_execution_authorized = False
product_ready = False
delivery_authorized = False
diagnosis_generated = False
```

La confirmación es evidencia, no permiso.

## Flujo F6

```text
WorkbookProfiler
→ structural relationship candidate

ColumnUnderstanding / semantic provider
→ dimensional semantic hypothesis
→ owner confirmation when required
→ P6 approved role

owner relationship question
→ Service1OwnerRelationshipConfirmationEventV1
→ canonical relationship binding

AnalysisPlan + P6
→ P7 requirement/grain
→ P8 computability with confirmed relationship evidence
```

P8 puede declarar el análisis computable con relación confirmada, pero F6 no hace el join ni prepara filas.

F11 corrigió el fallback semántico determinístico para mantener este contrato: una relación estructural se proyecta a confirmación cuando ambos extremos comparten el mismo rol `*_identifier`; ya no existe un whitelist exclusivo de producto. Así `ProductoID` y `SucursalID` usan exactamente el mismo mecanismo general.

## Frontera con F7

F7 será responsable de materializar evidencia gobernada:

```text
row selection
join resolution
group membership
filtering
coverage validation
provenance
```

F6 termina antes de ese punto.

## Gates F6

```text
DIMENSIONAL_ROLES_FIRST_CLASS = PASS
BRANCH_NOT_CHANNEL = PASS
OPERATION_TIME_ROLE = PASS
TRANSACTION_IDENTIFIER_ROLE = PASS
CITY_ROLE = PASS
STRUCTURAL_RELATIONSHIPS_GENERAL = PASS
PRODUCT_RELATIONSHIP_SPECIAL_CASE = 0
BRANCH_RELATIONSHIP_SPECIAL_CASE = 0
OWNER_RELATIONSHIP_EVIDENCE_GENERIC = PASS
RELATIONSHIP_BINDING_TO_P8 = PASS
JOIN_EXECUTION = 0
NO_PRODUCT_ROOT_CHANGE = REQUIRED
NO_MATH_CHANGE = REQUIRED
NO_SECOND_SEMANTIC_AUTHORITY = PASS
NO_SECOND_RELATIONSHIP_ENGINE = PASS
```
