# PYMIA CASE — Cafetería ABC session record

Estado: `SESSION_RECORD_READY`

Este registro convierte el caso Cafetería ABC en una ficha operativa completa para ejecutar una sesión asistida con el dueño.

No es diagnóstico final automático. Es soporte trazable para conversación y decisión operativa.

## Identificación

```text
case_id: cafeteria_abc_assisted_001
tenant_id: demo_cafeteria_abc
intake_id: intake_93546f538f5da1a7
evidence_id: evidence_fb309447997d4ef684c23bd417f645bf
run_id: run_c1c805258c8f4262bc309376f81cd662
output_hash: bea6fc31cb1fbf33cb2be7ea3771ba9c39dbedf8f346c73011786e7762f012ba
```

## Relato inicial

```text
Vendo más pero no me queda plata.
```

## Evidencia base

```text
prueba_excels/Cafetería ABC.xlsx
```

## Estado previo de PymIA

```text
candidate_confirmed
```

## Apertura de sesión

```text
Revisé el Excel como evidencia inicial. No voy a afirmar una causa definitiva. Vamos a validar qué representan los datos y elegir un foco operativo: margen por producto, caja por período o costos directos.
```

## Bloque 1 — Confirmación de período

Pregunta:

```text
¿Este Excel cubre todo el período que querés revisar o falta algún tramo?
```

Respuesta del dueño:

```text
[pendiente]
```

Clasificación:

```text
[CONFIRMA_PERIODO | CORRIGE_PERIODO | NO_SABE]
```

Acción según respuesta:

```text
[continuar | pedir archivo corregido | bloquear honestamente]
```

## Bloque 2 — Naturaleza de ventas

Pregunta:

```text
¿Las ventas son cobradas, facturadas o una mezcla?
```

Respuesta del dueño:

```text
[pendiente]
```

Clasificación:

```text
[VENTAS_COBRADAS | VENTAS_FACTURADAS | MEZCLA | NO_SABE]
```

Acción según respuesta:

```text
[orientar a caja | advertir desfase caja/facturación | pedir separación | bloquear honestamente]
```

## Bloque 3 — Naturaleza de costos

Pregunta:

```text
¿Los costos son costos directos de producto o incluyen gastos fijos, sueldos, alquiler, servicios o retiros?
```

Respuesta del dueño:

```text
[pendiente]
```

Clasificación:

```text
[COSTO_DIRECTO | COSTO_MIXTO | GASTO_FIJO_INCLUIDO | NO_SABE]
```

Acción según respuesta:

```text
[avanzar margen | separar estructura | pedir aclaración | bloquear honestamente]
```

## Bloque 4 — Productos

Pregunta:

```text
¿Querés revisar todos los productos o primero los más vendidos / más dudosos?
```

Respuesta del dueño:

```text
[pendiente]
```

Clasificación:

```text
[TODOS | MAYOR_VOLUMEN | PRODUCTOS_DUDOSOS | NO_SABE]
```

Acción según respuesta:

```text
[lectura amplia | foco mayor volumen | foco productos críticos | sugerir mayor volumen]
```

## Elección de foco operativo

Pregunta:

```text
¿Elegimos como próximo análisis margen por producto, caja por período o costos directos?
```

Respuesta del dueño:

```text
[pendiente]
```

Foco elegido:

```text
[MARGEN_PRODUCTO | CAJA_PERIODO | COSTOS_DIRECTOS]
```

## Evidencia adicional requerida

Completar según foco:

```text
MARGEN_PRODUCTO:
- lista de precios
- costo unitario
- descuentos/promociones
- desperdicio/merma

CAJA_PERIODO:
- movimientos de caja
- pagos a proveedores
- sueldos
- alquiler
- retiros
- deudas/pagos pendientes

COSTOS_DIRECTOS:
- facturas de proveedores
- receta/ficha técnica
- cantidades compradas
- stock inicial/final
```

Evidencia concreta pedida al dueño:

```text
[pendiente]
```

## Cierre de sesión

Decisión alcanzada:

```text
[pendiente]
```

Próximo paso acordado:

```text
[pendiente]
```

Nueva evidencia esperada:

```text
[pendiente]
```

## Condición de avance

PymIA sólo puede profundizar si queda una de estas condiciones:

```text
1. foco operativo elegido;
2. evidencia adicional concreta solicitada;
3. corrección semántica registrada;
4. bloqueo honesto por falta de claridad del dueño.
```

## Prohibiciones

Durante esta sesión no debe afirmarse:

```text
causa definitiva
solución garantizada
diagnóstico final automático
producto terminado
automatización completa
```

## Resultado esperado

```text
Cafetería ABC queda lista para reproceso focalizado o conversación operativa posterior sin perder trazabilidad.
```
