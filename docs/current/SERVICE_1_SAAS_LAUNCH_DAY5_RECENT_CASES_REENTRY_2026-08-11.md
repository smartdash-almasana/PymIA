# SERVICE_1_SAAS_LAUNCH — DAY 5 CASES + REENTRY

**Fecha:** 2026-08-11
**Checkout:** `E:\BuenosPasos\smartbridge\PymIA`
**Rama:** `main`
**Objetivo:** dar a Servicio 1 una noción SaaS mínima de casos recientes y reentrada sin abrir una nueva arquitectura de negocio.

---

## 1. Implementado

### Navegación

La shell común ahora expone:

- `Controles`
- `Casos`
- `RADAR`

### Casos recientes

Nueva ruta:

`GET /cases`

Muestra controles ya ejecutados dentro del scope actual con:

- servicio;
- estado;
- última actualización;
- acción `Abrir caso`.

### Reentrada

Nueva ruta:

`GET /case?case_ref=...`

Permite volver a abrir un resultado ya ejecutado sin repetir el cálculo.

Los snapshots de controles se guardan aislados por:

- tenant cuando existe identidad tenant;
- sesión cuando todavía no existe identidad tenant.

El `case_ref` combina identidad del caso + servicio para evitar que dos controles distintos sobre el mismo archivo se pisen.

---

## 2. Cobertura actual

### Controles productivos

Los resultados de revisiones como:

- Control de Cobros y Conciliación;
- Margen Real;

se registran como caso reciente después de una ejecución exitosa.

### Conciliación bancaria

La conciliación en estado `REVIEW_READY` también se registra como caso reciente, conservando el packet de resultado para reentrada.

---

## 3. Aislamiento probado

Se agregó una prueba que:

1. ejecuta `Control de Cobros y Conciliación`;
2. abre `/cases` con la cookie de esa sesión;
3. verifica que el caso aparece;
4. abre el caso nuevamente;
5. verifica que el resultado original vuelve a mostrarse;
6. abre `/cases` sin esa cookie;
7. verifica que el caso no aparece en otra sesión.

Resultado focal ampliado:

`27 passed`

Regresión web/tenant/RADAR/reconciliation/Consorcios/Margen:

`50 passed, 2 skipped, 0 failed`

Los dos skips dependen del entorno de integración existente y no fueron introducidos por Day 5.

---

## 4. Límite explícito

La persistencia de `Casos recientes` implementada en Day 5 es **in-memory por instancia web**.

Por lo tanto:

- permite reentrada durante la vida de la instancia;
- mantiene aislamiento tenant/session dentro de esa instancia;
- NO sobrevive un restart;
- NO es todavía persistencia enterprise multi-instancia.

La propia UI lo declara para no presentar una capacidad mayor a la existente.

Esto no afecta la persistencia durable ya existente de identidad/semántica del tenant, que es otro contrato.

---

## 5. Estado Day 5

| Frente | Estado |
|---|---|
| Navegación `Casos` | PASS |
| Listado de casos recientes | PASS |
| Reentrada sin recomputar | PASS |
| Aislamiento entre sesiones | PASS |
| Scope tenant cuando identidad existe | IMPLEMENTED |
| Persistencia tras restart | NOT_IMPLEMENTED |
| Persistencia enterprise multi-instancia | NOT_IMPLEMENTED |

---

## 6. Decisión

`DAY_5_MINIMAL_CASE_REENTRY: PASS`

`DURABLE_CASE_PERSISTENCE: GAP`

`NEW_BUSINESS_ARCHITECTURE: NO`

El próximo corte no debe confundirse: Day 5 cerró la experiencia mínima de caso/reentrada, pero no autoriza presentar persistencia durable de casos como terminada.

Para el plan de lanzamiento, el próximo trabajo de mayor valor es componer `Caja y Capital de Trabajo` sobre capacidades existentes y someterlo al mismo gate sintético E2E antes de declararlo disponible.
