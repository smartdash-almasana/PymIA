# SERVICE_1_OWNER_FACING_ROLE_EXPLANATION_CATALOG_V1

## Estado

```text
IMPLEMENTED
```

## Objetivo

Crear una fuente real, testeada y owner-facing para explicar roles semánticos de columnas al dueño.

Este slice conecta conceptualmente:

```text
suggested_semantic_role
→ owner_facing_role_explanation
```

sin integrar todavía con ingestion, prompt builder, storage ni pipeline.

## Motivo

La investigación detectó un gap real:

```text
service_1_column_confirmation_owner_prompt_v1.py
requiere owner_facing_role_explanation como input obligatorio,
pero no existía productor upstream formal para ese texto.
```

Este catálogo cierra esa fuente básica.

## Archivo runtime

```text
PymIA-Live/pymia/smartpyme/service_1_owner_facing_role_explanation_catalog_v1.py
```

## Test

```text
PymIA-Live/tests/smartpyme/test_service_1_owner_facing_role_explanation_catalog_v1.py
```

## Funciones públicas

```python
explain_owner_facing_semantic_role_v1(role)
known_owner_facing_semantic_roles_v1()
normalize_semantic_role_v1(role)
```

## Output

```text
Service1OwnerFacingRoleExplanationV1
```

Campos:

```text
schema_version
service_name
semantic_role
owner_label
owner_facing_role_explanation
calculation_relevance
known_role
human_review_required
runtime_authorized
recalculation_authorized
```

## Cobertura

Cubre los roles reales conocidos por `column_confirmation_v1.py`:

```text
venta_total
precio_venta
costo_unitario
costo_total
margen
cantidad
stock
stock_final
pago
cobro
ingreso
egreso
saldo
gasto
impuesto
descuento
producto
sku
cliente
proveedor
fecha
moneda
factura
canal
unknown
```

## Fallback seguro

Si el rol no existe:

```text
known_role=False
owner_label="Rol no reconocido"
owner_facing_role_explanation="Esta columna necesita revision manual antes de usarla para calculos o conclusiones."
calculation_relevance="INFORMATIONAL"
```

## Seguridad

Este slice fija:

```text
human_review_required=True
runtime_authorized=False
recalculation_authorized=False
```

## Exclusiones

Este slice no hace:

```text
NO ingestion integration
NO owner_prompt modification
NO ColumnSemanticClassifier modification
NO ColumnConfirmationMatrix modification
NO classifier modification
NO applier modification
NO case_patch modification
NO persistence
NO recalculation
NO reexecution
NO vertical_pipeline
NO landing/browser
```

## Tests cubiertos

```text
- cubre todos los roles del contrato column_confirmation_v1
- explica venta_total para dueño
- explica costo_unitario para dueño
- explica cantidad para dueño
- explica roles informacionales
- explica rol de segmentación canal
- fallback seguro para rol desconocido
- normaliza None/blanco/mayúsculas
- preserva flags de seguridad
- to_dict estable
- puede alimentar owner_prompt_v1 sin integrarlo
- cada rol conocido tiene label y explicación
```

## Próximo frente permitido

```text
SERVICE_1_COLUMN_INTERPRETATION_TO_OWNER_PROMPT_BRIDGE_V1
```

Objetivo futuro:

```text
ColumnConfirmationEntry
+ catalog explanation
→ service_1_column_confirmation_owner_prompt_v1
```

Todavía sin recalculation, sin persistence y sin pipeline integration.
