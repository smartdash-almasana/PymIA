# FIRST_AID_PRODUCTION_PERFORMANCE_LOCAL_CHECK

## Estado

```text
Tipo: LOCAL_PRODUCT_LEARNING_CHECK
Estado: CANDIDATE_FIRST_AID_FAMILY
Runtime impact: NONE
Code impact: NONE
```

Este documento registra una verificación local reproducible sobre un Excel industrial de producción para evaluar si el caso puede quedar como aprendizaje/candidato de producto para Primeros Auxilios PyME.

No implementa runtime, no abre pipeline, no modifica diagnóstico, no escribe OCF productivo, no usa replay y no usa storage.

---

# 1. Veredicto

```text
LOCAL_CHECK_RESULT: PASS
FIRST_AID_VALUE: VALID
CANDIDATE_FAMILY: PRODUCTION_PERFORMANCE_FIRST_AID
READY_FOR_RUNTIME_IMPLEMENTATION: NO
READY_FOR_LEVEL_2: NO_WITHOUT_ADDITIONAL_EVIDENCE
```

El archivo permite una revisión inicial de señales visibles de producción: órdenes con OEE bajo y scrap alto. Eso alcanza para priorizar revisión en Primeros Auxilios, pero no alcanza para diagnosticar causa ni afirmar eficiencia real.

---

# 2. Archivo inspeccionado

```text
E:\BuenosPasos\smartbridge\PymIA\prueba_excels\fabrica_industrial_compleja.xlsx
```

Inspección local realizada con Python/pandas en modo lectura.

---

# 3. Estructura detectada

```text
Hoja: PRODUCCION
Registros: 3000
Columnas: fecha, orden, maquina, operario, horas, unidades, scrap, oee
Rango fechas: 2025-01-01 a 2025-12-31
Máquinas únicas: 20
Operarios únicos: 60
OEE: 45.02 a 94.99
Scrap: 0 a 250
```

La estructura parece compatible con un archivo de producción industrial.

---

# 4. Calidad mínima de datos

```text
Nulos en fecha: 0
Nulos en orden: 0
Nulos en maquina: 0
Nulos en operario: 0
Nulos en horas: 0
Nulos en unidades: 0
Nulos en scrap: 0
Nulos en oee: 0
Órdenes duplicadas: 0
```

La calidad mínima es suficiente para una priorización inicial. No valida por sí sola la calidad conceptual de OEE ni la unidad real de scrap.

---

# 5. Regla de priorización usada

Se usó una regla simple y reproducible:

```text
low_oee_rank = ranking de OEE ascendente
high_scrap_rank = ranking de scrap descendente
priority_rank_score = low_oee_rank + high_scrap_rank
```

Criterio:

```text
menor priority_rank_score = revisar antes
```

Esta regla prioriza órdenes que combinan OEE bajo y scrap alto. No atribuye causa.

---

# 6. Top 10 recalculado

| # | Orden | Fecha | Máquina | Operario | Horas | Unidades | Scrap | OEE | Score |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | OT-11695 | 2025-07-19 | MAQ_16 | OPER_030 | 10.55 | 1612 | 250 | 45.33 | 20 |
| 2 | OT-10884 | 2025-01-21 | MAQ_12 | OPER_051 | 4.72 | 2224 | 244 | 45.40 | 103 |
| 3 | OT-10846 | 2025-04-10 | MAQ_09 | OPER_028 | 13.16 | 2135 | 243 | 45.51 | 126 |
| 4 | OT-11487 | 2025-07-06 | MAQ_19 | OPER_050 | 13.54 | 557 | 250 | 47.28 | 126 |
| 5 | OT-11465 | 2025-05-17 | MAQ_04 | OPER_049 | 11.15 | 2130 | 246 | 46.95 | 157 |
| 6 | OT-12812 | 2025-12-25 | MAQ_16 | OPER_008 | 8.72 | 1986 | 247 | 47.33 | 165 |
| 7 | OT-11184 | 2025-12-05 | MAQ_18 | OPER_016 | 7.83 | 82 | 244 | 46.78 | 176 |
| 8 | OT-10285 | 2025-03-19 | MAQ_10 | OPER_008 | 1.63 | 596 | 239 | 46.65 | 223 |
| 9 | OT-12190 | 2025-05-04 | MAQ_08 | OPER_002 | 3.05 | 818 | 237 | 46.59 | 240 |
| 10 | OT-10504 | 2025-07-21 | MAQ_16 | OPER_025 | 10.67 | 1479 | 238 | 46.94 | 246 |

Comparación con el Top 10 previo:

```text
Coinciden 9 de 10 órdenes.
La diferencia aparece por usar una regla explícita de ranking combinado.
El listado previo sigue siendo razonablemente consistente como priorización de Primeros Auxilios.
```

Nota de gobernanza:

```text
La diferencia 1/10 es aceptable para este chequeo local porque la priorización
usa ranking combinado low_oee_rank + high_scrap_rank, no simple orden absoluto
por OEE ni simple orden absoluto por scrap.
```

Orden previa que no queda en el Top 10 por esta regla:

```text
OT-11775
```

Orden que ingresa por esta regla:

```text
OT-10504
```

---

# 7. Qué puede afirmar Primeros Auxilios

Primeros Auxilios puede afirmar sólo señales visibles:

```text
el archivo parece ser de producción industrial
hay 3000 registros revisables
no hay nulos en columnas principales
no hay órdenes duplicadas
existen órdenes con combinación de OEE bajo y scrap alto
se puede priorizar una primera revisión de órdenes
```

También puede proponer una pregunta siguiente al dueño:

```text
De estas órdenes, ¿tenés registrado el motivo de scrap o alguna novedad de producción, mantenimiento, materia prima, turno o cambio de producto en esas fechas?
```

---

# 8. Qué NO puede afirmar

```text
No se diagnostica causa.
No se culpa máquina.
No se culpa operario.
No se afirma pérdida económica.
No se afirma eficiencia real.
No se afirma que el OEE esté correctamente calculado.
No se deriva automáticamente a Nivel 2.
```

Tampoco puede afirmar:

```text
fallas de mantenimiento
problemas de materia prima
bajo desempeño humano
ineficiencia real por máquina
impacto económico
causa del scrap
validez técnica del OEE
```

---

# 9. Evidencia faltante para Nivel 2

Para pasar a diagnóstico determinístico acotado haría falta:

```text
fórmula usada para calcular OEE
unidad exacta de scrap
producto fabricado por orden
estándar esperado por producto/máquina
turno
motivo de scrap
registro de paradas
mantenimiento o incidentes
materia prima o lote utilizado
cambio de producto o set-up
capacidad teórica
costo unitario si se quiere estimar impacto económico
```

Sin esa evidencia, el caso debe mantenerse como priorización inicial.

---

# 10. Familia candidata

```text
CANDIDATE_FAMILY: PRODUCTION_PERFORMANCE_FIRST_AID
```

Descripción candidata:

```text
Revisión inicial de archivos industriales de producción para ordenar señales visibles como OEE bajo, scrap alto, registros faltantes, órdenes prioritarias y evidencia necesaria para un análisis posterior.
```

Esta familia queda como aprendizaje de producto, no como feature implementada.

---

# 11. Recomendación

Registrar este caso como candidato de aprendizaje para Primeros Auxilios PyME.

Recomendación prudente:

```text
usar este patrón para conversaciones asistidas con dueños industriales
no automatizar todavía
no implementar runtime
no derivar a Nivel 2 sin evidencia adicional
crear en el futuro una plantilla owner-safe de producción industrial si aparecen más casos similares
```

---

# 12. Regla de cierre

```text
NO_RUNTIME
NO_CODE
NO_PIPELINE
NO_DIAGNOSTIC_CORE
NO_OCF_PRODUCTIVE_WRITE
NO_REPLAY
NO_STORAGE
NO_AUTOMATION
NO_NEW_FEATURES
NO_REAL_DIAGNOSTIC_CLAIM
```

Este documento es verificación local y aprendizaje de producto. No autoriza implementación.
