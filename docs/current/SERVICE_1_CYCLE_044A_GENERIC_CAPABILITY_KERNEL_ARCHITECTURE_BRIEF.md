# Servicio 1 — CYCLE_044A Generic Productive Capability Kernel Architecture Brief

**Estado:** `ARCHITECTURE_DECIDED_NO_PRODUCTIVE_CODE`  
**Ciclo:** `CYCLE_044A_DEFINE_GENERIC_PRODUCTIVE_CAPABILITY_KERNEL_ARCHITECTURE`

## Problema

El patrón productivo actual repite por patología:

```text
evaluador
+ adaptador de evidencia normalizada
+ outcome
+ branch en la raíz
+ familia semántica
+ matriz
+ catálogos
+ guards
+ ripple documental y contractual
```

Este patrón permitió certificar cuatro capacidades, pero no debe repetirse sin límite. El objetivo es reducir duplicación sin reescritura total y sin alterar la raíz productiva durante este ciclo.

## Alcance exacto del kernel

El kernel comienza después de un `computation plan` gobernado y termina antes de la entrega física.

Incluye:

1. resolución de evidencia;
2. agregación gobernada;
3. validación del dominio matemático;
4. ejecución de fórmula segura;
5. clasificación;
6. outcome acotado.

Excluye:

- ingesta;
- diálogo con el dueño;
- FSM de casos;
- CLI;
- selección de capacidad;
- entrega XLSX o PDF;
- conectores externos;
- LLM runtime.

## Principios

- solicitud explícita de capacidad;
- ejecución `fail closed`;
- sin `eval`;
- conjunto cerrado de operaciones matemáticas;
- uso de `Decimal`;
- trazabilidad completa;
- resultados tipados con valor, unidad, período y procedencia;
- definición declarativa donde el comportamiento sea estable;
- Python donde exista comportamiento real, validación o control.

## Tipos de capacidad

### ATOMIC

Consume evidencia gobernada y produce un resultado tipado propio.

Casos piloto:

- `LIQ_002 / projected_closing_cash_balance`;
- `PYME_011 / dso`.

### COMPOSITE

Consume resultados gobernados de capacidades previas y verifica compatibilidad de unidad, período y procedencia.

`PYME_013` deberá consumir resultados gobernados de `dso` y `dpo`. No debe releer el Excel ni reconstruir implícitamente DSO o DPO durante su ejecución.

`dso - dpo` no representa el ciclo completo de conversión de efectivo clásico sin el componente de días de inventario (`DIO`). Su outcome debe usar una denominación acotada de brecha DSO-DPO.

## Estados de migración

```text
LEGACY_ACTIVE
GENERIC_SHADOW
GENERIC_PRIMARY
RETIRED
```

- `LEGACY_ACTIVE`: comportamiento productivo actual.
- `GENERIC_SHADOW`: ejecución genérica en tests y comparación de equivalencia.
- `GENERIC_PRIMARY`: el kernel gobierna y el módulo previo puede mantenerse como wrapper compatible.
- `RETIRED`: retiro permitido únicamente después de equivalencia, regresión completa y decisión explícita.

## Expresión matemática segura

El kernel no ejecutará expresiones Python libres. No se permite `eval`, callbacks arbitrarios ni plugins cargados desde texto.

Operaciones iniciales propuestas:

```text
ADD
SUBTRACT
MULTIPLY
DIVIDE
```

Las expresiones deberán representarse como estructura validada y sólo podrán referenciar variables declaradas.

## Agregaciones iniciales

```text
SUM
SINGLE_VALUE
```

`SINGLE_VALUE` debe rechazar cardinalidad distinta de uno.

## Resultado tipado mínimo

Cada resultado debe declarar:

- valor;
- unidad;
- período;
- precisión;
- procedencia;
- capacidad y patología de origen;
- flags de seguridad cerrados.

## Casos piloto exactos

```text
LIQ_002
PYME_011
```

No se autoriza incorporar otra capacidad durante la etapa de equivalencia.

## Criterios de aceptación

1. equivalencia exacta de resultados;
2. equivalencia de clasificaciones;
3. equivalencia de bloqueos;
4. flags de seguridad en falso;
5. cero selección automática;
6. cero `eval`;
7. `SINGLE_VALUE` rechaza cardinalidad distinta de uno;
8. denominadores protegidos;
9. regresión completa verde;
10. ninguna segunda raíz productiva;
11. no se elimina código previo durante la primera extracción;
12. las diferencias deben fallar cerradas y ser trazables.

## Plan posterior propuesto

```text
CYCLE_044B_IMPLEMENT_MINIMAL_GENERIC_CAPABILITY_KERNEL
CYCLE_044C_RUN_GENERIC_SHADOW_EQUIVALENCE
CYCLE_044D_PROMOTE_GENERIC_KERNEL
CYCLE_045_CONNECT_PYME_013_USING_GENERIC_KERNEL
```

Este plan no autoriza por sí mismo código productivo. Cada ciclo requiere autorización y cierre propios.

## Prohibiciones de CYCLE_044A

- no implementar código productivo;
- no modificar la raíz;
- no conectar `PYME_013`;
- no eliminar módulos existentes;
- no autorizar entrega adicional;
- no introducir selección automática;
- no incorporar LLM runtime;
- no generar diagnóstico causal.