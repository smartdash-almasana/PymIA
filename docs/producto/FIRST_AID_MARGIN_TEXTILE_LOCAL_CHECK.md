# FIRST_AID_MARGIN_TEXTILE_LOCAL_CHECK

## Estado

```text
Tipo: LOCAL_PRODUCT_LEARNING_CHECK
Estado: REPEATED_FIRST_AID_FAMILY_SIGNAL
Runtime impact: NONE
Code impact: NONE
```

Este documento registra una verificación local de aprendizaje de producto sobre un Excel textil de ventas/costos/margen.

No implementa runtime, no crea feature nueva, no diagnostica, no recomienda precios definitivos y no afirma rentabilidad real.

---

# 1. Veredicto

```text
LOCAL_CHECK_RESULT: PASS
FIRST_AID_VALUE: VALID
REPEATED_FAMILY: PRICE_OR_COST_LIST / MARGIN_FIRST_AID
READY_FOR_RUNTIME_IMPLEMENTATION: NO
READY_FOR_LEVEL_2: NO_WITHOUT_ADDITIONAL_EVIDENCE
```

El caso refuerza una familia ya observada: revisión inicial de precios, costos y margen declarado/estimado. Sirve para aprendizaje de producto, no para implementación.

---

# 2. Archivo inspeccionado

```text
FILE_INSPECTED: prueba_excels/pyme_textil_compleja.xlsx
SHEET: VENTAS
ROWS: 2500
COLUMNS: fecha, factura, canal, sku, cantidad, venta, descuento, costo, margen
```

---

# 3. Estructura detectada

La hoja `VENTAS` contiene una tabla de ventas textiles con:

```text
fecha
factura
canal
sku
cantidad
venta
descuento
costo
margen
```

Estructura visible:

```text
SKUs únicos: 399
Canales: 4
Descuentos observados: 0, 5, 10, 15, 20
Filas con margen negativo declarado/calculado: 589
```

La estructura es compatible con revisión inicial de lista de precios, costos, descuentos y margen.

---

# 4. Calidad mínima de datos

```text
Nulos en columnas principales: NO
Facturas duplicadas: NO
```

Esta calidad mínima permite ordenar señales iniciales. No valida por sí sola que el margen esté correctamente calculado ni que los costos estén completos.

---

# 5. Señales visibles

```text
Archivo de ventas textiles con factura, canal, SKU, cantidad, venta, descuento, costo y margen.
No hay nulos en columnas principales.
No hay facturas duplicadas.
Hay 399 SKUs.
Hay 4 canales.
Hay descuentos de 0, 5, 10, 15 y 20.
Hay 589 filas con margen negativo declarado/calculado.
```

Estas señales permiten priorizar preguntas sobre costos, descuentos y fórmula de margen. No permiten concluir rentabilidad real.

---

# 6. Qué puede afirmar Primeros Auxilios

```text
Puede ordenar ventas por canal, SKU, descuento, costo y margen declarado.
Puede marcar filas con margen negativo como señales para revisar.
Puede detectar que el archivo sirve para revisión inicial de precios/costos/margen.
Puede pedir aclaración de costos y fórmula de margen.
```

Primeros Auxilios puede entregar valor ordenando la evidencia y explicitando límites.

---

# 7. Qué NO puede afirmar

```text
No puede afirmar rentabilidad real.
No puede recomendar precios definitivos.
No puede concluir que un canal conviene o no.
No puede diagnosticar pérdida.
No puede afirmar que el margen esté correctamente calculado.
No puede convertir margen negativo en causa confirmada.
```

Tampoco puede afirmar que un SKU, canal o descuento sea “el problema” sin evidencia adicional.

---

# 8. Evidencia faltante para Nivel 2

```text
Fórmula validada de margen.
Costos completos.
IVA/impuestos.
Comisiones por canal.
Descuentos reales aplicados.
Costos indirectos.
Flete/envío/packaging.
Contexto de promociones.
Confirmación de precio bruto/neto.
Objetivo comercial por canal o producto.
```

Sin esta evidencia, el caso debe mantenerse como revisión inicial de Primeros Auxilios.

---

# 9. Relación con pilotos sintéticos previos

```text
Este caso local refuerza lo validado en PILOT_002 sobre precios/costos/margen estimado, pero con un Excel local más grande y específico del rubro textil.
```

También confirma una repetición de patrón:

```text
No crea una familia nueva; confirma repetición fuerte de PRICE_OR_COST_LIST / MARGIN_FIRST_AID.
```

La diferencia principal frente al piloto sintético es que este archivo tiene 2500 filas, 399 SKUs y señales repetidas de margen negativo declarado/calculado.

---

# 10. Familia candidata / repetida

```text
REPEATED_FAMILY: PRICE_OR_COST_LIST / MARGIN_FIRST_AID
```

La familia ya estaba representada por el piloto sintético de precios/costos. Este caso local la refuerza como patrón relevante para Primeros Auxilios PyME.

---

# 11. Recomendación

```text
Registrar como señal repetida de producto.
No implementar runtime todavía.
No abrir Nivel 2 todavía.
Usar este caso para diseñar, más adelante, un checklist mínimo de margen textil si aparece un tercer caso similar.
```

Recomendación prudente:

```text
Mantener como aprendizaje documental de producto.
No convertir en feature.
No prometer rentabilidad real.
No recomendar precios definitivos.
```

---

# 12. Regla de cierre

```text
NO_RUNTIME
NO_CODE
NO_TESTS
NO_PIPELINE
NO_DIAGNOSTIC_CORE
NO_OCF_PRODUCTIVE_WRITE
NO_REPLAY
NO_STORAGE
NO_NEW_FEATURE
NO_DIAGNOSTIC
NO_DEFINITIVE_PRICE_RECOMMENDATION
NO_REAL_PROFITABILITY_CLAIM
```

Este documento registra aprendizaje de producto. No autoriza implementación.
