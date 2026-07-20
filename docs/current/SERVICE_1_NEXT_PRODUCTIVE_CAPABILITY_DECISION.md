# Servicio 1 — decisión de próxima capacidad productiva

**Ciclo:** `CYCLE_039_SERVICE_1_NEXT_PRODUCTIVE_CAPABILITY_DECISION`  
**Fecha:** 2026-07-20  
**Estado:** `DECIDED`

## Propósito

Definir una única secuencia autorizada después del cierre de la serie controlada de pilotos, sin ampliar capacidades por inferencia ni mezclar tres frentes con distinto grado de madurez.

## Opciones evaluadas

1. Conectar formalmente `REN_001` a la raíz productiva.
2. Ampliar Servicio 1 hasta 12 patologías productivas completas.
3. Diseñar capacidades industriales reales para scrap/OEE.

## Decisión

```text
PRIORIDAD 1: cerrar REN_001 como segunda vertical productiva completa.
PRIORIDAD 2: usar LIQ_001 y REN_001 como patrón de cierre para completar 12 patologías.
PRIORIDAD 3: diseñar scrap/OEE como vertical industrial posterior, con contratos y evidencia propios.
```

## Fundamento técnico

### REN_001

`REN_001` es el único candidato que ya reúne simultáneamente:

- patología presente en `docs/pathology_catalog.v1.json`;
- fórmula `REN_001_margen_neto_real` presente en `docs/formula_catalog.v1.json`;
- variables requeridas `sale_price`, `costs`, `taxes`;
- evaluador determinístico aislado;
- clasificación positiva, equilibrio y negativa;
- límites matemáticos explícitos;
- validación de plan gobernado;
- flags de autoridad mantenidos en falso;
- tests existentes.

La brecha pendiente es de integración gobernada, no de descubrimiento matemático.

### Doce patologías

El catálogo contiene decenas de patologías, pero presencia en catálogo no equivale a capacidad productiva. Una patología sólo contará dentro de las 12 cuando tenga como mínimo:

1. código y definición estable;
2. fórmula determinística y unidad de salida;
3. variables y evidencia requeridas;
4. límites matemáticos positivos, nulos, negativos e inválidos cuando correspondan;
5. plan de cálculo gobernado;
6. evaluación determinística;
7. hallazgo acotado sin atribución causal indebida;
8. tratamiento determinístico;
9. entrega explícita cuando aplique;
10. integración a la raíz oficial;
11. tests focales, vecinos y de no-deriva;
12. documentación rectora y evidencia de ejecución.

`LIQ_001` ya satisface el patrón completo. `REN_001` será el segundo patrón. Las diez restantes se seleccionarán después mediante una matriz de prioridad, evidencia disponible, diversidad operativa y costo de cierre.

### Scrap/OEE

Las columnas `scrap` y `oee` observadas en el Piloto 005 no autorizan una capacidad industrial. Antes de cualquier implementación se exige:

- definición canónica de numerador, denominador, período y unidad;
- distinción entre scrap físico, monetario y porcentual;
- definición de disponibilidad, rendimiento y calidad para OEE;
- reglas para datos faltantes, paradas planificadas, reproceso y producción buena;
- límites matemáticos y estados inválidos;
- evidencia mínima por máquina, orden y período;
- prohibición de inferir causa raíz desde un indicador aislado.

## Próximo ciclo funcional autorizado

```text
CYCLE_040_CONNECT_REN_001_TO_PRODUCTIVE_ROOT
```

### Alcance permitido

- integrar el evaluador existente de `REN_001` dentro de `service_1_product_pipeline_v1.py`;
- usar únicamente un request explícito de capacidad;
- consumir valores confirmados por el dueño;
- producir evaluación determinística y hallazgo acotado;
- mantener selección automática, diagnóstico causal y entrega automática prohibidos;
- agregar tratamiento y entrega sólo si siguen el mismo gobierno explícito de `LIQ_001`;
- actualizar locks, gates, disposición modular y tests.

### Fuera de alcance

- implementar simultáneamente otras patologías;
- diseñar scrap/OEE dentro del ciclo de integración de `REN_001`;
- modificar fórmulas de catálogo sin evidencia documental;
- seleccionar capacidades automáticamente desde headers o contenido del XLSX;
- promover `REN_001` sin recorrido real y regresión completa verde.

## Secuencia posterior

```text
CYCLE_040: integración productiva de REN_001
CYCLE_041: matriz y selección gobernada de las 10 patologías restantes
CYCLE_042+: cierre vertical de patologías por lotes pequeños
CICLO INDUSTRIAL: sólo después de contrato matemático y evidencia scrap/OEE
```
