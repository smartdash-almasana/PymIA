# FIRST_AID_ACTIVATION_SCENARIOS_V1

## Estado

```text
Tipo: PRODUCT_SCENARIOS
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Documentar escenarios conceptuales de activación para las 5 herramientas First Aid ya cubiertas por el contrato y el evaluator puro.

Este documento no autoriza runtime, pipeline, XLSX delivery ni ejecución de herramientas.

---

# 1. Cadena previa

```text
PYMIA_SERVICE_1_FULL_CATALOG_V1
→ FIRST_AID_TOOLBOX_PACK_SEED_V1
→ FIRST_AID_TRIAGE_COMPONENTS_DECISION_V1
→ FIRST_AID_TOOL_ACTIVATION_V1
→ FIRST_AID_TOOL_ACTIVATION_EVALUATOR_V1
→ SERVICE_1_TOOLBOX_AND_COMMERCIAL_MODULES_BOUNDARY_V1
```

---

# 2. Herramientas cubiertas

```text
caja_diaria_triage
precio_margen_basico
stock_alertas_basicas
gastos_triage
proveedores_precio_variacion_triage
```

---

# 3. Estados usados

```text
ELIGIBLE
BLOCKED_MISSING_EVIDENCE
BLOCKED_COLUMN_CONFIRMATION
BLOCKED_RESTRICTED_FORMULA
BLOCKED_FORBIDDEN_CLAIM
BLOCKED_SCOPE_MISMATCH
BLOCKED_COMPONENT_NOT_ALIGNED
BLOCKED_RUNTIME_NOT_AUTHORIZED
```

Nota:

```text
ELIGIBLE sólo representa elegibilidad conceptual.
runtime_authorized=false sigue bloqueando ejecución productiva.
```

---

# 4. Escenario A — precio_margen_basico elegible conceptualmente

## Pedido dueño

```text
Quiero revisar si el precio y el costo me dan margen.
```

## Evidencia disponible

```text
precio_venta
costo_unitario
```

## Columnas

```text
precio_venta: confirmed
costo_unitario: confirmed
```

## Resultado esperado

```text
BLOCKED_RUNTIME_NOT_AUTHORIZED
```

## Lectura

La herramienta está conceptualmente habilitada, pero no se ejecuta porque runtime sigue no autorizado.

---

# 5. Escenario B — precio_margen_basico bloqueado por evidencia faltante

## Pedido dueño

```text
Quiero saber el margen.
```

## Evidencia disponible

```text
precio_venta
```

## Faltante

```text
costo_unitario
```

## Resultado esperado

```text
BLOCKED_MISSING_EVIDENCE
```

## Pregunta al dueño

```text
¿Cuál es el costo unitario de este producto?
```

---

# 6. Escenario C — caja_diaria_triage bloqueado por columna dudosa

## Pedido dueño

```text
No me cierra la caja del día.
```

## Evidencia disponible

```text
saldo_inicial
ingresos
egresos
```

## Columna dudosa

```text
ingresos: ambiguous
```

## Resultado esperado

```text
BLOCKED_COLUMN_CONFIRMATION
```

## Pregunta al dueño

```text
Confirmá qué significa la columna de ingresos antes de calcular.
```

---

# 7. Escenario D — stock_alertas_basicas bloqueado por fórmula restringida

## Pedido dueño

```text
Quiero calcular rotación de inventario.
```

## Fórmula pedida

```text
rotacion_inventario
```

## Resultado esperado

```text
BLOCKED_RESTRICTED_FORMULA
```

## Escalamiento sugerido

```text
DETERMINISTIC_DIAGNOSIS
```

## Lectura

First Aid puede marcar stock bajo, pero rotación requiere evidencia más fuerte.

---

# 8. Escenario E — gastos_triage bloqueado por claim prohibido

## Pedido dueño

```text
Clasificame estos gastos de forma contable definitiva.
```

## Claim prohibido

```text
clasificación contable definitiva
```

## Resultado esperado

```text
BLOCKED_FORBIDDEN_CLAIM
```

## Lectura

First Aid puede ordenar gastos y pedir categorías, pero no clasifica contable o fiscalmente de forma definitiva.

---

# 9. Escenario F — proveedores_precio_variacion_triage elegible conceptualmente

## Pedido dueño

```text
Quiero revisar si el proveedor me aumentó este insumo.
```

## Evidencia disponible

```text
proveedor
producto_o_insumo
precio_o_costo
```

## Columnas

```text
proveedor: confirmed
producto_o_insumo: confirmed
precio_o_costo: confirmed
```

## Resultado esperado

```text
BLOCKED_RUNTIME_NOT_AUTHORIZED
```

## Lectura

La herramienta puede ser candidata a activación futura, pero no se ejecuta todavía.

---

# 10. Escenario G — scope mismatch

## Pedido dueño

```text
Quiero diagnóstico completo de rentabilidad.
```

## service_depth

```text
DETERMINISTIC_DIAGNOSIS
```

## Resultado esperado

```text
BLOCKED_SCOPE_MISMATCH
```

## Lectura

No corresponde a First Aid. Debe ir a Servicio 2.

---

# 11. Escenario H — herramienta inexistente o no alineada

## tool_ref

```text
unknown_tool
```

## Resultado esperado

```text
BLOCKED_COMPONENT_NOT_ALIGNED
```

## Lectura

No se puede activar una herramienta que no está declarada o alineada en el seed.

---

# 12. Tabla de escenarios

| Escenario | Tool | Condición | Estado esperado | Runtime |
|---|---|---|---|---|
| A | precio_margen_basico | evidencia mínima completa | BLOCKED_RUNTIME_NOT_AUTHORIZED | NO |
| B | precio_margen_basico | falta costo_unitario | BLOCKED_MISSING_EVIDENCE | NO |
| C | caja_diaria_triage | columna ambigua | BLOCKED_COLUMN_CONFIRMATION | NO |
| D | stock_alertas_basicas | pide rotacion_inventario | BLOCKED_RESTRICTED_FORMULA | NO |
| E | gastos_triage | pide clasificación contable definitiva | BLOCKED_FORBIDDEN_CLAIM | NO |
| F | proveedores_precio_variacion_triage | evidencia mínima completa | BLOCKED_RUNTIME_NOT_AUTHORIZED | NO |
| G | cualquier First Aid | service_depth no FIRST_AID | BLOCKED_SCOPE_MISMATCH | NO |
| H | unknown_tool | no existe mapping | BLOCKED_COMPONENT_NOT_ALIGNED | NO |

---

# 13. Límites

```text
Estos escenarios no ejecutan herramientas.
No calculan fórmulas.
No generan archivos.
No conectan con pipeline.
No llaman IA.
No producen reportes owner-facing finales.
```

---

# 14. Próximo paso posible

```text
FIRST_AID_ACTIVATION_SCENARIOS_TEST_V1
```

Objetivo:

```text
Convertir estos escenarios documentales en tests focales contra el evaluator puro.
```

Condición:

```text
No abrir pipeline, loader, XLSX delivery ni runtime productivo.
```

---

# 15. Veredicto

```text
FIRST_AID_ACTIVATION_SCENARIOS_V1 = DOCUMENTED
```

El flujo First Aid ya puede describirse como escenarios conceptuales antes de cualquier ejecución real.
