# Catálogo conversacional de hipótesis y evidencia — v1

## Estado

Documento canónico inicial derivado de `SmartPyme/app/laboratorio_pyme/conversation/hypotheses.py` y `questions.py`.

## Regla rectora

Cada hipótesis es una posibilidad investigativa, nunca un diagnóstico.

```text
síntomas → hipótesis → evidencia → preguntas
```

## Hipótesis: margen_erosionado

### Descripción

Ventas sostenidas pero rentabilidad caída por costos, inflación, descuentos o precios atrasados.

### Síntomas típicos

- RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
- vendo y no gano;
- los costos subieron;
- el margen bajó;
- vendo más y gano menos.

### Evidencia requerida

- ventas_periodo;
- compras_periodo;
- lista_precios_vigente;
- costo_mercaderia_vendida.

### Preguntas

- Tenés registros de ventas del último trimestre aunque sea en Excel?
- Actualizaste precios cuando subieron los costos?
- Cuándo fue la última vez que calculaste margen por producto?

## Hipótesis: caja_inconsistente

### Descripción

El dinero disponible no coincide con las ventas o movimientos esperados.

### Síntomas típicos

- la plata no cierra;
- falta dinero en caja;
- vendí pero no tengo la plata;
- no me cuadra;
- los números no cierran.

### Evidencia requerida

- resumen_caja_diaria;
- ventas_registradas;
- egresos_registrados.

### Preguntas

- Llevás algún cierre de caja diario?
- Los gastos personales y del negocio están mezclados?
- Más de una persona maneja la caja?

## Hipótesis: stock_inmovilizado

### Descripción

Capital atrapado en mercadería con baja rotación o sin salida.

### Síntomas típicos

- tengo mucho stock parado;
- mercadería que no sale;
- el depósito está lleno;
- compré de más;
- stock que no rota.

### Evidencia requerida

- inventario_actual;
- ultimas_ventas_por_producto;
- fecha_ultima_compra_por_item.

### Preguntas

- Tenés un inventario actualizado aunque sea básico?
- Qué productos no tuvieron movimiento recientemente?
- Comprás por volumen aunque no lo necesites todavía?

## Hipótesis: precios_atrasados

### Descripción

Los precios de venta quedaron detrás de los costos de reposición.

### Síntomas típicos

- no actualicé los precios;
- los precios están viejos;
- no sé cómo poner precio;
- hace meses que no retoco la lista;
- los precios están desactualizados.

### Evidencia requerida

- lista_precios_actual;
- fecha_ultima_actualizacion_precios;
- facturas_proveedores_recientes.

### Preguntas

- Cuándo actualizaste precios por última vez?
- Calculás precios usando costos actuales?
- Tenés una lista de precios formal?

## Hipótesis: tiempo_perdido

### Descripción

El dueño o equipo pierde horas en procesos manuales repetitivos.

### Síntomas típicos

- pierdo mucho tiempo en tareas repetidas;
- hago lo mismo todos los días;
- cargo datos a mano;
- paso horas en Excel;
- todo es manual;
- no me alcanza el tiempo.

### Evidencia requerida

- descripcion_procesos_repetitivos;
- tiempo_estimado_por_tarea;
- herramientas_actuales_usadas.

### Preguntas

- Qué tarea repetitiva consume más tiempo?
- Cuántas horas por semana se van ahí?
- Usás Excel, sistema o papel para esa tarea?

## Uso esperado

Este catálogo debe alimentar:

- anamnesis conversacional;
- selección de próxima pregunta;
- pedido documental contextual;
- bloqueo por evidencia insuficiente;
- preparación del primer informe.

No debe usarse para afirmar diagnóstico por simple coincidencia de palabras.
