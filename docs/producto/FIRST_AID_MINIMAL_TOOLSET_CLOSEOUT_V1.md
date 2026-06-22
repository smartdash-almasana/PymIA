# FIRST_AID_MINIMAL_TOOLSET_CLOSEOUT_V1

## Estado

```text
Tipo: CLOSEOUT_DOC
Estado: DRAFT_APPLIED
Metodología: Gentle AI Development
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Declarar el cierre formal del primer set mínimo de herramientas determinísticas First Aid de Servicio 1.

Este cierre no declara Servicio 1 completo.
Este cierre no autoriza pipeline.
Este cierre no autoriza FSM.
Este cierre no autoriza XLSX Delivery.
Este cierre no autoriza chatbot.
Este cierre no autoriza LLM.

Declara únicamente que existe un tridente inicial de tools puras, focales y testeadas, listo para servir como fuente futura de entregables controlados.

---

# 1. Toolset cerrado

```text
precio_margen_basico
caja_diaria_triage
stock_alertas_basicas
```

Estas tres tools comparten contrato de salida:

```text
FirstAidToolResultV1
```

Y mantienen la regla:

```text
runtime_authorized = False
```

---

# 2. Cadena actual

```text
FileIntakeResult
→ TaskSpecPatch
→ Service1TaskSpec
→ FirstAidToolResultV1
→ First Aid minimal tools
```

La cadena todavía no está cableada por pipeline.
La ejecución de tools sigue siendo focal/manual/testeada, no runtime productivo.

---

# 3. Herramientas incluidas

## 3.1 precio_margen_basico

Archivo:

```text
PymIA-Live/pymia/smartpyme/first_aid_precio_margen_basico_v1.py
```

Test:

```text
PymIA-Live/tests/smartpyme/test_first_aid_precio_margen_basico_v1.py
```

Inputs:

```text
precio_venta
costo_unitario
```

Resultados permitidos:

```text
margen_bruto_pesos
margen_bruto_porcentaje
markup_porcentaje
```

Límites:

```text
No confirma rentabilidad real.
No incluye impuestos.
No incluye comisiones.
No incluye costos fijos.
No incluye costos indirectos.
No reemplaza análisis contable.
```

## 3.2 caja_diaria_triage

Archivo:

```text
PymIA-Live/pymia/smartpyme/first_aid_caja_diaria_triage_v1.py
```

Test:

```text
PymIA-Live/tests/smartpyme/test_first_aid_caja_diaria_triage_v1.py
```

Inputs:

```text
saldo_inicial
ingresos
egresos
```

Resultados permitidos:

```text
flujo_neto
saldo_final_estimado
```

Límites:

```text
No confirma saldo bancario real.
No equivale a conciliación.
No valida efectivo físico.
No incluye movimientos no declarados.
No reemplaza revisión contable.
```

## 3.3 stock_alertas_basicas

Archivo:

```text
PymIA-Live/pymia/smartpyme/first_aid_stock_alertas_basicas_v1.py
```

Test:

```text
PymIA-Live/tests/smartpyme/test_first_aid_stock_alertas_basicas_v1.py
```

Inputs requeridos:

```text
producto
stock_actual
stock_minimo
```

Input opcional:

```text
ventas_diarias_promedio
```

Resultados permitidos:

```text
stock_bajo
diferencia_vs_minimo
dias_stock_restante
```

Límites:

```text
No confirma stock físico real.
No reemplaza conteo físico.
No valida sistema de inventario.
No confirma quiebre de stock.
No calcula rotación real.
No incluye compras pendientes ni ventas no declaradas.
```

---

# 4. Lo que este cierre habilita

Este cierre habilita el siguiente diseño controlado:

```text
FIRST_AID_XLSX_DELIVERY_V1
```

Motivo:

```text
Ya existen tres outputs determinísticos compatibles con FirstAidToolResultV1.
```

XLSX Delivery podrá tomar resultados validados y producir un archivo descargable determinístico.

---

# 5. Lo que este cierre NO habilita

```text
No habilita pipeline.
No habilita FSM.
No habilita runtime productivo.
No habilita chatbot.
No habilita LLM.
No habilita document_ingestion.
No habilita Exceland bridge.
No habilita conciliación bancaria.
No habilita Mercado Pago.
No habilita IVA/IIBB.
No habilita asientos automáticos.
```

---

# 6. Riesgos controlados

```text
diagnóstico prematuro
claims de rentabilidad real
claims de saldo bancario real
claims de stock físico real
conciliación implícita
archivo normalizado no confirmado
runtime accidental
pipeline prematuro
XLSX delivery opaco
```

---

# 7. Estado de producto después del cierre

```text
Servicio 1 tiene foundation owner-facing.
Servicio 1 tiene TaskSpec assembler parcial.
Servicio 1 tiene contrato común FirstAidToolResultV1.
Servicio 1 tiene tres tools First Aid determinísticas.
Servicio 1 todavía no tiene XLSX Delivery.
Servicio 1 todavía no tiene pipeline propio.
Servicio 1 todavía no tiene FSM real.
Servicio 1 todavía no tiene chatbot operativo.
Servicio 1 todavía no está completo como sistema full.
```

---

# 8. Próximo ciclo recomendado

```text
FIRST_AID_XLSX_DELIVERY_V1
```

Tipo esperado:

```text
CODE + TEST FOCAL ONLY
```

Condición:

```text
Debe consumir FirstAidToolResultV1.
Debe generar XLSX determinístico.
No debe ejecutar tools.
No debe abrir pipeline.
No debe abrir FSM.
No debe usar LLM.
No debe usar chatbot.
```

---

# 9. Veredicto

```text
FIRST_AID_MINIMAL_TOOLSET_CLOSED
```
