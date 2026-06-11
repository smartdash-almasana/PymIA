# PYMIA CASE — Cafetería ABC margin focus

Estado: `FOCO_OPERATIVO_PROPUESTO`

Caso: Cafetería ABC

Relato inicial:

```text
Vendo más pero no me queda plata.
```

Evidencia base:

```text
prueba_excels/Cafetería ABC.xlsx
```

## Objetivo

Preparar el primer foco operativo sugerido para Cafetería ABC: `MARGEN_PRODUCTO`.

Este documento no declara causa definitiva. Organiza la siguiente conversación y la evidencia necesaria para revisar si el problema puede estar en margen por producto.

## Por qué este foco es razonable

Ante el relato:

```text
Vendo más pero no me queda plata.
```

una primera hipótesis operativa frecuente es que el aumento de ventas no se traduzca en caja o ganancia por alguna de estas razones:

- productos con margen bajo;
- costos directos mal cargados;
- descuentos o promociones no reflejados;
- desperdicio, merma o consumo interno;
- mezcla entre costo de producto y gasto fijo;
- diferencias entre venta facturada y venta cobrada.

PymIA no afirma que esta sea la causa. Sólo propone empezar por margen por producto porque permite ordenar evidencia concreta.

## Pregunta principal al dueño

```text
¿Querés que empecemos revisando margen por producto para ver si lo que más vendés realmente deja contribución?
```

## Si el dueño acepta

Clasificación:

```text
FOCO_ELEGIDO: MARGEN_PRODUCTO
```

Evidencia requerida:

```text
1. lista de productos vendidos;
2. precio de venta por producto;
3. costo unitario directo por producto;
4. descuentos o promociones aplicadas;
5. merma, desperdicio o consumo interno si existe;
6. período exacto del análisis.
```

Siguiente acción:

```text
Preparar reproceso focalizado sobre margen por producto.
```

## Si el dueño prefiere caja

Clasificación:

```text
FOCO_ELEGIDO: CAJA_PERIODO
```

Evidencia requerida:

```text
1. movimientos de caja;
2. movimientos bancarios;
3. pagos a proveedores;
4. sueldos;
5. alquiler;
6. servicios;
7. retiros;
8. deudas o pagos pendientes.
```

Siguiente acción:

```text
Cambiar foco a caja por período y no insistir en margen.
```

## Si el dueño prefiere costos directos

Clasificación:

```text
FOCO_ELEGIDO: COSTOS_DIRECTOS
```

Evidencia requerida:

```text
1. facturas de proveedores;
2. fichas técnicas o recetas;
3. cantidades compradas;
4. stock inicial y final;
5. cambios de precio de insumos.
```

Siguiente acción:

```text
Cambiar foco a costos directos y separar insumos de gastos fijos.
```

## Si el dueño no sabe elegir

Clasificación:

```text
BLOQUEO: OWNER_UNCERTAIN_ABOUT_FOCUS
```

Respuesta sugerida:

```text
Podemos empezar por los productos de mayor venta. Si ahí no aparece el problema, pasamos a caja por período.
```

Siguiente acción:

```text
Pedir lista de productos más vendidos o usar el Excel para ordenar por volumen si la evidencia lo permite.
```

## Guion corto para operador

```text
Ya tenemos una lectura trazable inicial. No voy a decir que la causa está confirmada. Para avanzar necesitamos elegir foco. Mi sugerencia es empezar por margen por producto: revisar si los productos que más vendés realmente dejan contribución después del costo directo, descuentos y merma. Si preferís, también podemos ir por caja del período o por costos directos.
```

## Resultado esperado de la conversación

La conversación debe terminar con uno de estos resultados:

```text
FOCO_ELEGIDO: MARGEN_PRODUCTO
FOCO_ELEGIDO: CAJA_PERIODO
FOCO_ELEGIDO: COSTOS_DIRECTOS
BLOQUEO: OWNER_UNCERTAIN_ABOUT_FOCUS
```

## Condición de avance

Sólo avanzar si queda registrado:

```text
1. foco elegido;
2. evidencia concreta requerida;
3. pregunta siguiente al dueño;
4. límite de no diagnóstico final automático.
```

## Límite

Este foco no es una conclusión. Es una ruta de trabajo asistida para decidir qué evidencia pedir y cómo profundizar sin perder trazabilidad.
