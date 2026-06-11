# PYMIA CASE — Cafetería ABC owner session

Estado: `LISTO_PARA_OPERACION_ASISTIDA`

Caso: Cafetería ABC

Entrada inicial del dueño:

```text
Vendo más pero no me queda plata.
```

Evidencia base:

```text
prueba_excels/Cafetería ABC.xlsx
```

## Objetivo de la sesión

Convertir la salida trazable del `Faithful Operator` en una conversación operativa concreta con el dueño PyME.

La sesión no busca declarar diagnóstico final automático. Busca confirmar sentido de negocio, elegir foco y definir el próximo movimiento operativo.

## Estado del sistema antes de hablar con el dueño

```text
EVIDENCE_REQUESTED
→ OWNER_CONFIRMATION_PENDING
→ CLOSED
```

Cierre alcanzado:

```text
candidate_confirmed
```

## Trazabilidad del caso

```text
tenant_id: demo_cafeteria_abc
intake_id: intake_93546f538f5da1a7
evidence_id: evidence_fb309447997d4ef684c23bd417f645bf
run_id: run_c1c805258c8f4262bc309376f81cd662
output_hash: bea6fc31cb1fbf33cb2be7ea3771ba9c39dbedf8f346c73011786e7762f012ba
```

## Apertura sugerida

```text
Revisé el Excel que compartiste y lo traté como evidencia inicial. No voy a afirmar una causa definitiva todavía. Lo que sí podemos hacer ahora es ordenar la lectura y decidir por dónde conviene empezar: margen por producto, caja por período o costos directos.
```

## Confirmaciones obligatorias

### 1. Período

Pregunta:

```text
¿Este Excel cubre todo el período que querés revisar o falta algún tramo?
```

Registrar respuesta:

```text
[pendiente]
```

Decisión:

- Si cubre el período completo: continuar.
- Si falta período: pedir archivo corregido o aclaración.
- Si no sabe: bloquear honestamente.

### 2. Ventas

Pregunta:

```text
¿Las ventas que aparecen en el Excel son ventas reales cobradas, facturadas o una mezcla?
```

Registrar respuesta:

```text
[pendiente]
```

Decisión:

- Si son cobradas: lectura más cercana a caja.
- Si son facturadas: puede haber desfase con caja.
- Si son mezcla: pedir separación o aclaración.

### 3. Costos

Pregunta:

```text
¿Los costos del Excel son costos directos de producto o incluyen gastos fijos como alquiler, sueldos, servicios o retiros?
```

Registrar respuesta:

```text
[pendiente]
```

Decisión:

- Si son directos: avanzar a margen por producto.
- Si incluyen gastos fijos: separar costo directo de estructura.
- Si no sabe: pedir fuente o responsable del archivo.

### 4. Productos

Pregunta:

```text
¿Querés revisar todos los productos o primero los más vendidos / más dudosos?
```

Registrar respuesta:

```text
[pendiente]
```

Decisión:

- Si elige todos: lectura amplia.
- Si elige productos críticos: lectura focalizada.
- Si no sabe: empezar por mayor volumen de ventas.

## Elección de foco operativo

El dueño debe elegir uno:

```text
A. Margen por producto
B. Caja por período
C. Costos directos
```

Respuesta del dueño:

```text
[pendiente]
```

## Próximo movimiento según foco

### A. Margen por producto

Acción:

```text
Separar productos principales y revisar cuáles tienen margen bajo, dudoso o inconsistente.
```

Evidencia adicional posible:

```text
lista de precios, costo unitario, promociones, descuentos, desperdicio
```

### B. Caja por período

Acción:

```text
Comparar ventas del período contra pagos reales, gastos, retiros y deudas.
```

Evidencia adicional posible:

```text
movimientos de caja, banco, pagos a proveedores, sueldos, alquiler, retiros
```

### C. Costos directos

Acción:

```text
Separar insumos directos por producto y revisar variaciones de costo.
```

Evidencia adicional posible:

```text
facturas de proveedores, recetas/fichas técnicas, cantidades compradas, stock inicial/final
```

## Cierre de sesión esperado

La sesión debe terminar con una decisión concreta:

```text
El próximo análisis será: [margen por producto | caja por período | costos directos]
```

Y una evidencia requerida:

```text
Para avanzar necesito: [archivo o aclaración concreta]
```

## Prohibiciones durante la sesión

No decir:

```text
La causa definitiva es...
```

No prometer:

```text
Esto va a resolver la rentabilidad automáticamente.
```

No vender:

```text
Esto ya es una plataforma/producto terminado.
```

## Resultado operativo buscado

```text
Dueño confirma sentido de los datos
→ elige foco
→ se pide evidencia adicional concreta
→ PymIA queda listo para reprocesar o profundizar sin perder trazabilidad
```
