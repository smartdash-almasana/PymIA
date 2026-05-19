# Catálogo de fórmulas matemáticas PyME — v1

## Estado

Documento inicial. Define la necesidad de un catálogo matemático separado del catálogo de patologías.

## Propósito

PymIA necesita una capa matematizadora capaz de:

- tomar hipótesis o patologías candidatas;
- seleccionar fórmulas pertinentes;
- identificar variables necesarias;
- pedir evidencia faltante;
- calcular desvíos;
- comparar contra umbrales de normalidad;
- proyectar escenarios pedidos por el dueño;
- explicar resultados en lenguaje operativo.

## Separación conceptual

### Catálogo de patologías

Responde:

```text
¿Qué puede estar pasando?
```

Ejemplos:

- margen erosionado;
- caja inconsistente;
- stock inmovilizado;
- precios atrasados;
- tiempo operativo perdido.

### Catálogo de fórmulas

Responde:

```text
¿Cómo se calcula, verifica o proyecta?
```

Ejemplos:

- margen bruto;
- margen neto;
- punto de equilibrio;
- rotación de stock;
- capital inmovilizado;
- contribución marginal;
- rentabilidad objetivo;
- ventas necesarias para alcanzar determinada ganancia.

### Capa matematizadora

Responde:

```text
¿Qué fórmula aplica, qué variables faltan y qué resultado se puede sostener con evidencia?
```

No diagnostica por sí sola. Calcula, compara y proyecta bajo contratos de evidencia.

## Relación patología → fórmula

Cada patología candidata puede referenciar una o varias fórmulas.

Ejemplo:

```json
{
  "pathology_code": "desalineacion_costo_precio",
  "formula_refs": [
    "margen_bruto_real",
    "brecha_margen_vs_objetivo",
    "precio_minimo_objetivo"
  ]
}
```

La patología define el patrón de desvío. La fórmula define el mecanismo de contraste.

## Formato sugerido de una fórmula

```json
{
  "formula_id": "margen_bruto_real",
  "nombre": "Margen bruto real",
  "categoria": "rentabilidad",
  "expresion": "(venta_neta - costo_variable) / venta_neta",
  "unidad_resultado": "porcentaje",
  "variables_requeridas": [
    "venta_neta",
    "costo_variable"
  ],
  "evidencia_requerida": [
    "ventas_periodo",
    "costos_variables_periodo"
  ],
  "interpretacion": "Mide qué porcentaje de la venta queda después de cubrir el costo variable directo.",
  "criterios_normalidad": [
    {
      "condicion": "margen_bruto_real >= margen_objetivo",
      "estado": "dentro_de_objetivo"
    },
    {
      "condicion": "margen_bruto_real < margen_objetivo",
      "estado": "desvio_negativo"
    }
  ],
  "preguntas_habilitadas": [
    "¿Cuánto margen real tengo?",
    "¿Cuánto debería vender para llegar al margen objetivo?",
    "¿Qué precio mínimo necesito para sostener el margen?"
  ]
}
```

## Familias iniciales de fórmulas

### Rentabilidad

- margen_bruto_real
- margen_neto
- contribucion_marginal
- margen_por_producto
- margen_vs_objetivo
- precio_minimo_objetivo
- rentabilidad_sobre_ventas

### Punto de equilibrio

- punto_equilibrio_ventas
- punto_equilibrio_unidades
- ventas_necesarias_para_ganancia_objetivo
- ventas_necesarias_para_rentabilidad_objetivo

### Stock

- rotacion_stock
- dias_stock
- capital_inmovilizado_stock
- stock_minimo
- stock_maximo
- cobertura_stock_dias
- quiebre_stock_estimado

### Caja

- flujo_caja_neto
- saldo_caja_proyectado
- burn_rate
- runway_dias
- ciclo_conversion_efectivo
- brecha_caja_operativa

### Precios y costos

- variacion_costo_reposicion
- atraso_precio_vs_costo
- precio_sugerido_por_margen
- costo_total_unitario
- costo_variable_unitario
- costo_fijo_asignado_unitario

### Productividad y tiempo

- horas_operativas_perdidas
- costo_hora_operativa
- ahorro_estimado_por_automatizacion
- productividad_por_persona
- productividad_por_proceso

### Compras y proveedores

- variacion_precio_proveedor
- concentracion_proveedor
- plazo_promedio_pago
- impacto_aumento_insumos

### Escenarios y objetivos

- brecha_hacia_objetivo
- crecimiento_necesario_mensual
- ventas_objetivo_en_periodo
- rentabilidad_objetivo_en_periodo
- sensibilidad_margen_precio_costo

## Ejemplos iniciales

### margen_bruto_real

```json
{
  "formula_id": "margen_bruto_real",
  "nombre": "Margen bruto real",
  "categoria": "rentabilidad",
  "expresion": "(venta_neta - costo_variable) / venta_neta",
  "unidad_resultado": "porcentaje",
  "variables_requeridas": ["venta_neta", "costo_variable"],
  "evidencia_requerida": ["ventas_periodo", "costos_variables_periodo"],
  "interpretacion": "Porcentaje de la venta que queda luego de cubrir costos variables directos."
}
```

### punto_equilibrio_ventas

```json
{
  "formula_id": "punto_equilibrio_ventas",
  "nombre": "Punto de equilibrio en ventas",
  "categoria": "punto_equilibrio",
  "expresion": "costos_fijos / margen_contribucion_porcentual",
  "unidad_resultado": "moneda",
  "variables_requeridas": ["costos_fijos", "margen_contribucion_porcentual"],
  "evidencia_requerida": ["costos_fijos_periodo", "ventas_periodo", "costos_variables_periodo"],
  "interpretacion": "Ventas necesarias para cubrir costos fijos sin pérdida ni ganancia."
}
```

### ventas_necesarias_para_ganancia_objetivo

```json
{
  "formula_id": "ventas_necesarias_para_ganancia_objetivo",
  "nombre": "Ventas necesarias para alcanzar ganancia objetivo",
  "categoria": "escenarios_y_objetivos",
  "expresion": "(costos_fijos + ganancia_objetivo) / margen_contribucion_porcentual",
  "unidad_resultado": "moneda",
  "variables_requeridas": ["costos_fijos", "ganancia_objetivo", "margen_contribucion_porcentual"],
  "evidencia_requerida": ["costos_fijos_periodo", "ventas_periodo", "costos_variables_periodo"],
  "interpretacion": "Ventas requeridas para cubrir la estructura y alcanzar una ganancia definida."
}
```

### precio_sugerido_por_margen

```json
{
  "formula_id": "precio_sugerido_por_margen",
  "nombre": "Precio sugerido por margen objetivo",
  "categoria": "precios_y_costos",
  "expresion": "costo_unitario / (1 - margen_objetivo)",
  "unidad_resultado": "moneda",
  "variables_requeridas": ["costo_unitario", "margen_objetivo"],
  "evidencia_requerida": ["costo_unitario_actual", "margen_objetivo"],
  "interpretacion": "Precio mínimo sugerido para sostener un margen bruto objetivo."
}
```

## Preguntas que habilita el catálogo

El dueño puede preguntar:

- ¿cuánto tengo que vender para ganar X?
- ¿qué precio necesito para llegar a tal margen?
- ¿en cuántos meses puedo alcanzar tal rentabilidad?
- ¿qué pasa si sube el costo un 10%?
- ¿qué producto me conviene empujar?
- ¿cuánto capital tengo trabado en stock?
- ¿cuánto tiempo o plata ahorro si automatizo este proceso?

La capa matematizadora debe traducir esas preguntas a fórmulas, variables y evidencia.

## Regla de evidencia

Ningún cálculo operativo debe presentarse como confirmado si faltan variables o evidencia.

Estados posibles:

```text
CALCULABLE
CALCULABLE_CON_SUPUESTOS
NO_CALCULABLE_POR_EVIDENCIA_INSUFICIENTE
```

## Regla de normalidad y desvío

Cada fórmula puede tener criterios de normalidad o comparación:

```json
{
  "formula_id": "margen_bruto_real",
  "normalidad_refs": [
    "margen_objetivo_empresa",
    "margen_objetivo_rubro",
    "margen_historico_empresa"
  ],
  "desvio": "margen_bruto_real - margen_objetivo"
}
```

La normalidad puede venir de:

- objetivo declarado por el dueño;
- histórico de la empresa;
- benchmark sectorial si existe;
- criterio experto documentado;
- umbral configurable por caso.

## Implementación futura

Este documento debe derivar en:

- `schemas/formula_catalog.schema.json`
- `catalogs/formula_catalog.v1.json`
- loader determinístico de fórmulas;
- tests de variables requeridas;
- vínculo `pathology_code -> formula_refs`;
- capa matematizadora que aplique fórmulas solo con evidencia suficiente.
