# Visión de producto PymIA

## Propósito

PymIA debe ayudar al dueño de una PyME a comprender y estabilizar su operación a partir de datos reales, significado operativo confirmado y herramientas determinísticas.

## Servicio 1

Servicio 1 es un laboratorio operativo de archivos tabulares. Su flujo rector es:

```text
archivo real
→ lectura estructural
→ comprensión de columnas
→ preguntas al dueño cuando falta significado
→ confirmación semántica
→ análisis determinístico
→ archivo de entrega
```

## Roles

- El dueño PyME aporta archivos, contexto y significado operativo.
- La capa conversacional pregunta, explica y traduce.
- PymIA valida, gobierna estados y decide cuándo puede computar.
- Las tools ejecutan cálculos y generan archivos.

## Invariantes

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
El dueño confirma durante la lectura.
```

La capa conversacional no diagnostica ni calcula como fuente soberana. No existe un operador humano obligatorio en el flujo normal.

## Estado

La columna vertebral canónica de Servicio 1 está integrada y probada sobre XLSX reales. La expansión pendiente consiste en conectar más patologías, fórmulas y herramientas al mismo flujo, sin abrir cadenas paralelas.
