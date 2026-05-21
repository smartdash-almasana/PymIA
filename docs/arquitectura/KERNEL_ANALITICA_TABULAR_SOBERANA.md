# Kernel de Analítica Tabular Soberana

## Principio

PymIA no debe limitarse a patologías complejas o diagnósticos sofisticados.

El kernel también debe ser soberano sobre la analítica tabular simple.

La soberanía del kernel no consiste solamente en controlar inferencias avanzadas.
También consiste en impedir que operaciones básicas sobre evidencia económica queden delegadas a agentes autónomos externos.

---

## Problema Detectado

Hermes, utilizando execute_code sobre XLSX crudo, demostró gran eficacia para:

- agrupar,
- sumar,
- rankear,
- calcular márgenes,
- ordenar top/bottom,
- calcular porcentajes,
- producir exploraciones rápidas.

Esto expuso una debilidad arquitectónica:

el kernel actual posee mayor madurez doctrinal que capacidad oficial de exploración tabular básica.

Como consecuencia:

- Hermes se transforma de facto en analista operativo,
- execute_code se vuelve el camino de menor resistencia,
- la exploración tabular ocurre fuera del kernel,
- aparecen inferencias no controladas.

---

## Regla Arquitectónica

Toda analítica económica básica debe poder resolverse dentro del kernel.

Ejemplos:

- top productos,
- bottom productos,
- ranking por margen,
- ventas por cliente,
- participación porcentual,
- concentración,
- variación,
- crecimiento,
- margen bruto,
- comparación temporal,
- regla de tres,
- agregaciones simples.

---

## Objetivo

Eliminar la necesidad de que Hermes utilice execute_code directamente sobre evidencia económica cruda para resolver preguntas operacionales simples.

---

## Arquitectura Objetivo

```text
Hermes
  → PymIA.TabularAnalytics
      → StructuredEvidence
      → Aggregations
      → Metrics
      → ControlledInferences
  → Hermes.format()
```

Hermes:
- no abre XLSX,
- no ejecuta openpyxl,
- no usa pandas directamente,
- no decide métodos analíticos.

PymIA:
- controla la lectura,
- controla la semántica,
- controla las métricas,
- controla las inferencias permitidas.

---

## Capacidades Mínimas del Kernel

El módulo TabularAnalytics debe poder resolver:

### Agregación
- sum,
- avg,
- median,
- count,
- distinct,
- weighted calculations.

### Ranking
- top N,
- bottom N,
- percentiles,
- concentración.

### Temporal
- variación,
- tendencia,
- comparación entre períodos,
- crecimiento.

### Económico-financiero básico
- margen bruto,
- participación,
- ticket promedio,
- rotación,
- composición.

### Inferencia Controlada
El kernel puede emitir:
- observaciones,
- alertas,
- tensiones,
- anomalías simples,
- faltantes de evidencia.

El kernel NO debe:
- recomendar discontinuaciones,
- emitir juicios estratégicos libres,
- inferir causalidad sin evidencia.

---

## Principio Epistemológico

Lo simple también debe ser soberano.

Si las operaciones básicas quedan fuera del kernel:
- el agente conversacional se transforma en analista,
- el kernel pierde autoridad práctica,
- aparecen bypasses epistemológicos.

---

## Máxima Operacional

El kernel no debe ser solamente profundo.

También debe ser útil para preguntas simples del día a día operacional.
