# Frontera conceptual — Servicio 1, Servicio 2 y RADAR

**Fecha:** 12 de agosto de 2026  
**Estado:** Definición conceptual de arquitectura  
**Motivación:** Evitar que el desarrollo de Servicio 1 absorba capacidades relacionales y documentales propias de capas posteriores.

## 1. Problema detectado

Durante el modelado de la vertical Consorcios apareció la idea de representar evidencias, hechos y relaciones persistentes entre sí, por ejemplo:

```text
Factura
↕
Proveedor
↕
Presupuesto aprobado
↕
Trabajo realizado
↕
Pago bancario
↕
Gasto declarado
↕
Liquidación
↕
Comprobante
```

Ese modelo excede la frontera razonable de Servicio 1.

## 2. Servicio 1

Servicio 1 trabaja sobre **datos operativos estructurados** y ejecuta capacidades determinísticas concretas.

Puede relacionar registros cuando ese matching sea necesario para completar una capacidad específica.

Ejemplos:

```text
movimiento bancario ↔ cobranza
factura ↔ pago
deuda ↔ cobranza
venta ↔ cobro
```

La relación existe dentro del algoritmo de la capacidad. No implica una memoria relacional general ni una ontología transversal de evidencias.

Flujo conceptual:

```text
INPUT ESTRUCTURADO
↓
SEMÁNTICA CANÓNICA
↓
CAPACIDAD DETERMINÍSTICA
↓
RESULTADO
↓
EXCEPCIONES
↓
WORKPAPER / EVIDENCIA
```

Principio:

> **Servicio 1 cruza datos para resolver una tarea.**

## 3. Servicio 2

Servicio 2 comienza cuando PymIA trata evidencias, documentos, hechos, actores y antecedentes como objetos relacionados de manera persistente y transversal.

Ejemplos de preguntas propias de esta capa:

- ¿qué corresponde con qué?;
- ¿qué originó qué?;
- ¿qué respalda qué?;
- ¿qué contradice qué?;
- ¿qué quedó pendiente?;
- ¿qué ocurrió antes?;
- ¿qué documento sostiene una afirmación o decisión?;

Flujo conceptual posible:

```text
resultados S1
+ documentos
+ comprobantes
+ decisiones
+ eventos
+ actores
+ antecedentes
↓
MEMORIA / EVIDENCIA OPERACIONAL CONECTADA
```

Principio:

> **Servicio 2 conecta evidencias para reconstruir una realidad operacional.**

Esta definición es conceptual; no implica que la implementación definitiva de Servicio 2 deba adoptar una tecnología concreta de grafo, base documental u otra persistencia.

## 4. RADAR

RADAR no reemplaza a Servicio 1 ni a Servicio 2.

RADAR supervisa variables observables y resultados contra políticas definidas por el dueño.

Modelo:

```text
RadarObservable
→ Owner Policy
→ RadarEngine
→ RadarEvent
```

Ejemplo:

```text
Resultado S1:
5,7% de cobranzas pendientes de imputación

Owner Policy:
alertar si supera 2%

RADAR:
RADAR_EVENT
```

Principio:

> **RADAR supervisa desvíos sobre estados observables; no decide por el dueño qué es grave o aceptable.**

## 5. Separación resumida

| Capa | Pregunta principal | Unidad de trabajo |
|---|---|---|
| Servicio 1 | ¿Qué pasó en estos datos? | capacidad determinística, resultado, excepción, workpaper |
| Servicio 2 | ¿Cómo se relacionan las evidencias que explican la realidad? | evidencia, hecho, relación, antecedente, contexto |
| RADAR | ¿El estado observado cruzó una frontera definida por el dueño? | observable, policy, event |

Síntesis:

> **Servicio 1 cruza datos para resolver una tarea.**  
> **Servicio 2 conecta evidencias para reconstruir una realidad.**  
> **RADAR supervisa desvíos sobre esa realidad operativa.**

## 6. Consecuencia arquitectónica inmediata

Para cerrar Servicio 1 no se debe introducir como requisito:

- red general de evidencias;
- persistencia transversal de relaciones documentales;
- reconstrucción causal de procesos completos;
- razonamiento documental entre capacidades;
- memoria histórica relacional como precondición de ejecución.

Sí es compatible con Servicio 1:

- matching determinístico acotado a una capacidad;
- semántica canónica;
- trazabilidad del resultado;
- excepciones explícitas;
- workpapers;
- observables consumibles por RADAR.

## 7. Uso de la vertical Consorcios como ejemplo

Consorcios permite visualizar claramente la frontera.

Servicio 1 puede detectar:

```text
cobranza sin imputar
saldo bancario divergente
propietario con deuda
pago sin correspondencia en la tabla esperada
```

Servicio 2 podría, en una etapa posterior, reconstruir:

```text
este gasto
↔ esta decisión de asamblea
↔ este proveedor
↔ esta factura
↔ este trabajo
↔ este pago
↔ este movimiento bancario
↔ esta liquidación
```

RADAR podría supervisar sobre los resultados disponibles:

```text
morosidad > límite acordado
cobranzas pendientes > límite acordado
diferencia de conciliación > tolerancia acordada
```

## 8. Regla de gobierno

Cuando una nueva idea aparezca durante el cierre de Servicio 1, debe preguntarse:

> **¿esta relación es necesaria para ejecutar una capacidad concreta, o estamos intentando construir memoria relacional general?**

Si es lo primero, puede pertenecer a Servicio 1.

Si es lo segundo, debe evaluarse como Servicio 2 y no ampliar el alcance actual de Servicio 1.
