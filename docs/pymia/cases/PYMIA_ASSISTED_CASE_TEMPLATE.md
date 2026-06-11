# PYMIA ASSISTED CASE TEMPLATE

Estado: `TEMPLATE_OPERATIVO`

Esta plantilla permite abrir un caso asistido local sin crear producto, canal ni diagnóstico final automático.

## Identificación

```text
case_id: [pendiente]
tenant_id: [pendiente]
intake_id: [pendiente]
evidence_id: [pendiente]
run_id: [pendiente]
output_hash: [pendiente]
```

## Relato inicial del dueño

```text
[pegar frase inicial]
```

## Evidencia base

```text
[ruta del Excel o archivo recibido]
```

## Recorrido esperado

```text
1. EVIDENCE_REQUESTED
2. OWNER_CONFIRMATION_PENDING
3. CLOSED | EVIDENCE_REQUESTED | BLOCKED
```

## Confirmación semántica mínima

### Período

Pregunta:

```text
¿Este archivo cubre todo el período que querés revisar o falta algún tramo?
```

Respuesta:

```text
[pendiente]
```

Clasificación:

```text
[CONFIRMA_PERIODO | CORRIGE_PERIODO | NO_SABE]
```

### Ventas

Pregunta:

```text
¿Las ventas son cobradas, facturadas o una mezcla?
```

Respuesta:

```text
[pendiente]
```

Clasificación:

```text
[VENTAS_COBRADAS | VENTAS_FACTURADAS | MEZCLA | NO_SABE]
```

### Costos

Pregunta:

```text
¿Los costos son costos directos de producto o incluyen gastos fijos, sueldos, alquiler, servicios o retiros?
```

Respuesta:

```text
[pendiente]
```

Clasificación:

```text
[COSTO_DIRECTO | COSTO_MIXTO | GASTO_FIJO_INCLUIDO | NO_SABE]
```

### Productos / líneas

Pregunta:

```text
¿Querés revisar todos los productos o primero los más vendidos / más dudosos?
```

Respuesta:

```text
[pendiente]
```

Clasificación:

```text
[TODOS | MAYOR_VOLUMEN | PRODUCTOS_DUDOSOS | NO_SABE]
```

## Foco operativo elegido

```text
[MARGEN_PRODUCTO | CAJA_PERIODO | COSTOS_DIRECTOS | OTRO]
```

## Evidencia adicional requerida

```text
[archivo, columna, aclaración o fuente concreta]
```

## Próximo paso acordado

```text
[acción concreta]
```

## Estado final de la sesión

```text
[CANDIDATE_CONFIRMED | CORRECTION_REQUESTED | BLOCKED_BY_OWNER_UNCERTAINTY | NEW_EVIDENCE_REQUESTED]
```

## Prohibiciones

No afirmar:

```text
causa definitiva
solución garantizada
diagnóstico final automático
producto terminado
automatización completa
```

## Cierre operativo

El caso queda listo para:

```text
[reprocesar evidencia | profundizar foco | pedir aclaración | cerrar por bloqueo honesto]
```
