# FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1

## Estado

```text
Tipo: PRODUCT_ARCHAEOLOGY
Estado: DRAFT_APPLIED
Fuente: E:\BuenosPasos\exeland2
Runtime impact: NONE
Code impact: NONE
```

## Propósito

Inventariar material existente de `exeland2` para poblar el futuro almacén enchufable de `Primeros Auxilios PyME`.

Este documento no importa código, no migra YAML, no crea contratos runtime y no autoriza wiring.

Su función es clasificar qué piezas del acervo Exceland pueden convertirse en:

```text
ToolboxPack
FormulaPack
ValidationPack
TemplatePack
FirstAidTool
```

---

# 1. Fuentes leídas

```text
E:\BuenosPasos\exeland2\catalog\formulas.yaml
E:\BuenosPasos\exeland2\catalog\validations.yaml
E:\BuenosPasos\exeland2\catalog\product_registry.yaml
E:\BuenosPasos\exeland2\specs\precio_margen.yaml
E:\BuenosPasos\exeland2\specs\caja_diaria.yaml
E:\BuenosPasos\exeland2\specs\stock_control.yaml
```

No se leyó todavía la totalidad de specs. Esta es una primera arqueología suficiente para clasificar dirección.

---

# 2. Hallazgo principal

`exeland2` contiene material valioso para Primeros Auxilios, pero no debe importarse como producto cerrado ni como runtime directo.

Lectura correcta:

```text
Exceland = cantera de herramientas.
PymIA = sistema operativo organizacional.
```

Por lo tanto:

```text
No copiar Exceland como módulo vivo.
No meter sus fórmulas directamente en kernel.
No convertir PymIA en generador de plantillas Excel.
Sí extraer fórmulas, validadores, plantillas y patrones como packs enchufables.
```

---

# 3. Fórmulas detectadas

`catalog/formulas.yaml` contiene 15 fórmulas:

| Fórmula | Categoría | Clasificación PymIA | Nivel sugerido |
|---|---|---|---|
| `margen_bruto` | pricing | señal de margen bruto | FIRST_AID / NIVEL_2 si se interpreta |
| `margen_bruto_pesos` | pricing | diferencia precio-costo | FIRST_AID |
| `precio_venta_con_margen` | pricing | cálculo de precio objetivo | FIRST_AID / herramienta |
| `markup` | pricing | markup sobre costo | FIRST_AID |
| `ingresos_totales` | financial | total simple | FIRST_AID |
| `egresos_totales` | financial | total simple | FIRST_AID |
| `resultado_neto` | financial | resultado básico | NIVEL_2 si se usa como diagnóstico |
| `punto_equilibrio_unidades` | financial | break-even | NIVEL_2 |
| `punto_equilibrio_pesos` | financial | break-even | NIVEL_2 |
| `flujo_caja_neto` | cashflow | ingreso - egreso | FIRST_AID |
| `saldo_acumulado` | cashflow | continuidad de saldo | FIRST_AID |
| `alerta_stock_minimo` | stock | alerta simple | FIRST_AID |
| `dias_stock_restante` | stock | duración estimada | FIRST_AID si hay ventas diarias |
| `rotacion_inventario` | stock | rotación | NIVEL_2 si exige CMV/inventario confiable |
| `costo_reposicion_promedio` | stock | costo ponderado | NIVEL_2 / herramienta avanzada |

---

# 4. Fórmulas aptas para Primeros Auxilios

Estas fórmulas pueden vivir en una primera caja de herramientas FIRST_AID porque son simples, explicables y de baja fricción si los datos están presentes:

```text
margen_bruto
margen_bruto_pesos
precio_venta_con_margen
markup
ingresos_totales
egresos_totales
flujo_caja_neto
saldo_acumulado
alerta_stock_minimo
dias_stock_restante
```

Condición:

```text
Deben declarar datos usados y faltantes.
No deben convertirse automáticamente en diagnóstico.
```

Ejemplo:

```text
Puedo calcular margen bruto si tengo precio y costo.
No puedo afirmar rentabilidad real si faltan comisiones, impuestos, envíos, descuentos o estructura de costos.
```

---

# 5. Fórmulas que deben escalar a Nivel 2

Estas fórmulas son útiles, pero pueden inducir diagnóstico si se usan sin suficiente evidencia:

```text
resultado_neto
punto_equilibrio_unidades
punto_equilibrio_pesos
rotacion_inventario
costo_reposicion_promedio
```

Motivo:

```text
requieren mayor precisión de costos, períodos, inventario, CMV o estructura financiera.
```

Regla:

```text
Pueden estar en el almacén, pero no activarse como hallazgo FIRST_AID salvo como simulación o cálculo explícitamente limitado.
```

---

# 6. Validaciones detectadas

`catalog/validations.yaml` contiene validaciones simples y valiosas:

```text
positive_number
non_negative_number
percentage_0_1
percentage_0_100
integer_positive
integer_non_negative
```

Clasificación:

```text
ValidationPack FIRST_AID_READY
```

Estas validaciones son más seguras que las fórmulas para Primeros Auxilios, porque ayudan a detectar errores de entrada sin diagnosticar.

Uso recomendado:

```text
marcar valores negativos inesperados
marcar porcentajes fuera de rango
marcar unidades no enteras
marcar campos obligatorios vacíos
explicar formato esperado al dueño
```

---

# 7. Productos-herramienta detectados

`product_registry.yaml` contiene 12 productos:

| Producto | Categoría | Lectura PymIA | Nivel sugerido |
|---|---|---|---|
| `caja_diaria` | cashflow | control simple de caja | FIRST_AID |
| `precio_margen` | pricing | cálculo precio/margen | FIRST_AID |
| `stock_control` | stock | alertas de stock | FIRST_AID |
| `punto_equilibrio` | financial | break-even | NIVEL_2 |
| `costos_por_producto` | financial | estructura de costo | NIVEL_2 |
| `flujo_de_fondos` | cashflow | proyección | NIVEL_2 / NIVEL_3 |
| `control_de_gastos` | cashflow | categorización de gastos | FIRST_AID / NIVEL_2 |
| `rentabilidad_por_producto` | financial | rentabilidad | NIVEL_2 |
| `compras_y_proveedores` | stock | proveedores/compras | FIRST_AID / NIVEL_2 |
| `cuentas_corrientes_clientes` | financial | saldos por cliente | NIVEL_2 |
| `simulador_inflacion` | pricing | escenario de inflación | NIVEL_2 |
| `proyeccion_ventas` | financial | forecast | NIVEL_2 / NIVEL_3 |

---

# 8. Herramientas candidatas para almacén FIRST_AID

## 8.1 Caja diaria simple

Fuente:

```text
specs/caja_diaria.yaml
```

Puede transformarse en:

```text
FirstAidTool: caja_diaria_triage
```

Dolores cubiertos:

```text
No me cierra la caja.
Quiero ordenar ingresos y egresos.
Quiero ver saldo inicial, ingresos, egresos y saldo final.
```

Límite:

```text
No es conciliación bancaria completa.
No certifica caja real.
```

## 8.2 Precio y margen

Fuente:

```text
specs/precio_margen.yaml
```

Puede transformarse en:

```text
FirstAidTool: precio_margen_basico
```

Dolores cubiertos:

```text
No sé qué precio poner.
No sé si el margen me da.
Tengo costo y quiero precio objetivo.
```

Límite:

```text
No afirma rentabilidad real si faltan comisiones, impuestos, descuentos, envíos o gastos fijos.
```

## 8.3 Stock control

Fuente:

```text
specs/stock_control.yaml
```

Puede transformarse en:

```text
FirstAidTool: stock_alertas_basicas
```

Dolores cubiertos:

```text
No sé si tengo stock mínimo.
Quiero ver días de stock restante.
Quiero detectar alerta de reposición.
```

Límite:

```text
No confirma stock físico.
No calcula rotación confiable sin ventas/CMV/inventario promedio.
```

## 8.4 Control de gastos

Fuente:

```text
product_registry.yaml -> control_de_gastos
```

Puede transformarse en:

```text
FirstAidTool: gastos_triage
```

Dolores cubiertos:

```text
Tengo gastos mezclados.
No sé en qué se va la plata.
Quiero ordenar egresos por categoría.
```

Límite:

```text
No reemplaza contabilidad.
No clasifica fiscalmente sin revisión.
```

## 8.5 Compras y proveedores

Fuente:

```text
product_registry.yaml -> compras_y_proveedores
```

Puede transformarse en:

```text
FirstAidTool: proveedores_precio_variacion_triage
```

Dolores cubiertos:

```text
Me aumentaron proveedores.
No sé si trasladé costos.
Quiero comparar compras.
```

Límite:

```text
No decide estrategia de compras.
No confirma rentabilidad sin ventas/costos cruzados.
```

---

# 9. Propuesta de packs enchufables

## FormulaPack inicial

```yaml
pack_id: first_aid_formula_pack_v1
source: exceland2/catalog/formulas.yaml
scope: FIRST_AID
status: CANDIDATE
formulas:
  - margen_bruto
  - margen_bruto_pesos
  - precio_venta_con_margen
  - markup
  - ingresos_totales
  - egresos_totales
  - flujo_caja_neto
  - saldo_acumulado
  - alerta_stock_minimo
  - dias_stock_restante
```

## ValidationPack inicial

```yaml
pack_id: first_aid_validation_pack_v1
source: exceland2/catalog/validations.yaml
scope: FIRST_AID
status: CANDIDATE
validations:
  - positive_number
  - non_negative_number
  - percentage_0_1
  - percentage_0_100
  - integer_positive
  - integer_non_negative
```

## ToolboxPack inicial

```yaml
pack_id: first_aid_toolbox_pack_v1
source: exceland2/catalog/product_registry.yaml
scope: FIRST_AID
status: CANDIDATE
tools:
  - caja_diaria_triage
  - precio_margen_basico
  - stock_alertas_basicas
  - gastos_triage
  - proveedores_precio_variacion_triage
```

---

# 10. Regla de migración

Nada de `exeland2` debe entrar directamente al runtime de PymIA.

Flujo correcto:

```text
arqueología
→ inventario
→ clasificación FIRST_AID / NIVEL_2 / NIVEL_3
→ contrato de pack
→ tests de contrato
→ loader enchufable
→ activación controlada
```

Prohibido:

```text
copiar YAML directo al kernel
hardcodear fórmulas en Python
activar diagnóstico por fórmula aislada
transformar productos Exceland en features runtime sin frontera
```

---

# 11. Valor para Primeros Auxilios

El valor no está en vender plantillas Excel.

El valor está en que PymIA pueda decir:

```text
Para este dolor puntual tengo una herramienta de primeros auxilios.
Puedo revisar la fuente, validar datos básicos, aplicar un cálculo limitado y decirte qué falta para avanzar.
```

Eso convierte Exceland en almacén enchufable, no en producto principal.

---

# 12. Veredicto

```text
EXCELAND2_ARCHAEOLOGY = USEFUL_FOR_FIRST_AID_TOOLBOX
```

Clasificación:

```text
FormulaPack candidates: YES
ValidationPack candidates: YES
ToolboxPack candidates: YES
Runtime import: NO
Kernel contamination risk: HIGH if copied directly
```

---

# 13. Siguiente paso recomendado

Crear un contrato documental mínimo:

```text
FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
```

Debe definir:

```text
pack_id
source
scope
allowed_service_depth
required_inputs
outputs
owner-facing limitations
forbidden_claims
evidence_sufficiency_rules
formula_refs
validation_refs
tool_refs
```

No implementar loader todavía.
