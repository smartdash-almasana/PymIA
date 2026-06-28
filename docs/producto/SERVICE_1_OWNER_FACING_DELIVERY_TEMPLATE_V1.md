# SERVICE_1_OWNER_FACING_DELIVERY_TEMPLATE_V1

## Estado

```text
STATUS: OWNER_FACING_TEMPLATE_V1
SCOPE: Servicio 1 / entrega comprensible para dueño PyME
RUNTIME: no modificado
STAGE_6: no habilitado
AUTONOMIA: no
COMMIT_READY: pending review
```

---

# 1. Propósito

Este documento define la plantilla estándar para transformar los outputs técnicos de **Servicio 1** en una entrega clara, conservadora y comprensible para el dueño de una PyME.

No reemplaza al playbook operativo.
No reemplaza la matriz de capacidades.
No agrega runtime.
No crea nuevas tools.

Su función es convertir esto:

```text
pipeline_result.json
operator_packet.json
detected_structure.json
column_confirmation_packet.json
owner_message.md
XLSX outputs
QA artifacts
```

en una entrega owner-facing:

```text
qué analizamos,
qué encontramos,
qué archivos entregamos,
qué falta,
qué no podemos afirmar,
y cuál es la próxima acción sugerida.
```

Regla madre:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

---

# 2. Cuándo usar esta plantilla

Usar esta plantilla cuando un caso de Servicio 1 haya llegado a alguno de estos estados:

```text
EXECUTED
DELIVERED
PARTIAL
BLOCKED_WITH_EVIDENCE
```

No usarla para prometer que un caso está resuelto si sólo existe intake sin interpretación suficiente.

Si el caso queda en `INTAKE_ONLY` o `NEEDS_OPERATOR_MAPPING`, la entrega debe limitarse a informar estructura detectada y faltantes.

---

# 3. Estructura estándar de entrega al dueño

La entrega owner-facing debe tener estas secciones, en este orden:

```text
1. Título de entrega
2. Resumen ejecutivo
3. Archivo analizado
4. Alcance de la revisión
5. Hojas y columnas utilizadas
6. Herramientas aplicadas
7. Resultados principales
8. Archivos entregados
9. Faltantes, inválidos o bloqueos
10. Límites de la entrega
11. Próximas acciones sugeridas
12. Nota de revisión humana
```

---

# 4. Plantilla base

```markdown
# Entrega PymIA — Servicio 1

## 1. Resumen ejecutivo

Analizamos el archivo **{archivo_analizado}** dentro del alcance de **{alcance_de_revision}**.

La revisión se realizó sobre datos declarados por la empresa y debe leerse como un primer auxilio operativo, no como auditoría contable ni diagnóstico integral.

Resultado general:

- Estado del caso: **{estado_del_caso}**
- Herramientas aplicadas: **{herramientas_aplicadas}**
- Resultados válidos: **{resultados_ok}**
- Datos inválidos: **{resultados_invalidos}**
- Datos faltantes: **{resultados_faltantes}**

## 2. Archivo analizado

- Archivo recibido: **{archivo_analizado}**
- Tipo de archivo: **{tipo_archivo}**
- Período informado: **{periodo}**
- Área revisada: **{area_revisada}**

## 3. Qué revisamos

Usamos las siguientes hojas y columnas:

| Hoja | Columnas utilizadas | Motivo |
|---|---|---|
| {hoja_1} | {columnas_1} | {motivo_1} |
| {hoja_2} | {columnas_2} | {motivo_2} |

## 4. Herramientas aplicadas

| Herramienta | Para qué se usó | Estado |
|---|---|---|
| {tool_1} | {uso_tool_1} | {estado_tool_1} |
| {tool_2} | {uso_tool_2} | {estado_tool_2} |

## 5. Resultados principales

{resultados_principales}

## 6. Archivos entregados

Se entregan los siguientes archivos:

| Archivo | Contenido | Uso sugerido |
|---|---|---|
| {archivo_output_1} | {contenido_1} | {uso_1} |
| {archivo_output_2} | {contenido_2} | {uso_2} |

## 7. Faltantes, inválidos o bloqueos

{faltantes_invalidos_bloqueos}

## 8. Límites de esta entrega

Esta entrega:

- no es auditoría contable;
- no es certificación fiscal;
- no es conciliación bancaria definitiva;
- no valida que los datos declarados sean correctos;
- no reemplaza revisión humana;
- no reemplaza al contador;
- no ejecuta decisiones automáticas.

## 9. Próximas acciones sugeridas

{proximas_acciones}

## 10. Nota final

Los resultados surgen de los datos disponibles en el archivo recibido y de las columnas utilizadas en esta revisión. Si se corrigen, amplían o completan los datos, la revisión puede cambiar.
```

---

# 5. Campos requeridos

Toda entrega debe completar estos campos mínimos:

```text
archivo_analizado:
tipo_archivo:
estado_del_caso:
alcance_de_revision:
hojas_usadas:
columnas_usadas:
herramientas_aplicadas:
resultados_ok:
resultados_invalidos:
resultados_faltantes:
archivos_entregados:
limites:
proximas_acciones:
```

Si un campo no puede completarse, no inventar. Usar:

```text
No determinado con la evidencia disponible.
```

---

# 6. Traducción de estados técnicos a lenguaje dueño PyME

| Estado técnico | Lenguaje owner-facing |
|---|---|
| OK | Se pudo calcular con los datos disponibles. |
| INVALID_INPUT | El dato existe, pero no es válido para este cálculo. |
| MISSING_INPUTS | Falta un dato necesario para calcular. |
| BLOCKED | No conviene avanzar sin más información. |
| NEEDS_OPERATOR_MAPPING | Hace falta confirmar qué columna representa cada dato. |
| UNSUPPORTED | Este archivo o problema está fuera del alcance de esta revisión. |
| PARTIAL | Se pudo revisar una parte, pero no todo el caso. |
| DELIVERED | Se generó una entrega revisable. |

---

# 7. Bloques reutilizables por familia

## 7.1 precio_margen_basico

### Descripción owner-facing

```text
Revisamos la relación entre precio de venta y costo unitario declarado para estimar margen básico por producto o SKU.
```

### Resultados posibles

```text
- margen calculado correctamente;
- costo faltante;
- precio faltante;
- costo igual o menor a cero;
- precio igual o menor a cero;
- datos no comparables.
```

### Texto sugerido

```text
La revisión de precios y costos permite detectar productos con margen bajo, datos faltantes o valores inválidos. No confirma rentabilidad contable real, porque se basa sólo en los datos declarados en el archivo recibido.
```

---

## 7.2 stock_alertas_basicas

### Descripción owner-facing

```text
Revisamos stock actual contra stock mínimo declarado para detectar señales básicas de stock bajo o crítico.
```

### Resultados posibles

```text
- stock suficiente;
- stock bajo;
- stock crítico;
- stock actual faltante;
- stock mínimo faltante;
- SKU o producto no identificable.
```

### Texto sugerido

```text
La revisión de stock ayuda a priorizar productos que podrían requerir reposición o control. No reemplaza un sistema de inventario ni confirma rotación real.
```

---

## 7.3 caja_diaria_triage

### Descripción owner-facing

```text
Revisamos una señal básica de caja usando saldo inicial, ingresos y egresos declarados.
```

### Resultados posibles

```text
- flujo neto calculado;
- ingresos faltantes;
- egresos faltantes;
- saldo inicial faltante;
- datos mezclados o no comparables;
- caso bloqueado por requerir conciliación definitiva.
```

### Texto sugerido

```text
Esta revisión es un triage inicial de caja. No es conciliación bancaria definitiva y no valida extractos, medios de pago ni saldos contables.
```

---

## 7.4 gastos_triage

### Descripción owner-facing

```text
Revisamos conceptos e importes declarados para identificar señales básicas de gastos o movimientos que requieren clasificación.
```

### Resultados posibles

```text
- gasto o movimiento identificable;
- concepto faltante;
- importe faltante;
- importe inválido;
- mezcla de ventas, cobros, gastos o transferencias sin criterio suficiente.
```

### Texto sugerido

```text
Esta revisión ayuda a ordenar gastos declarados, pero no constituye imputación contable ni clasificación fiscal definitiva.
```

---

## 7.5 proveedores_precio_variacion_triage

### Descripción owner-facing

```text
Revisamos señales básicas de precios o costos asociados a proveedores cuando los datos disponibles permiten comparación.
```

### Resultados posibles

```text
- precio/costo revisable;
- proveedor no identificado;
- producto no comparable;
- moneda no clara;
- período no claro;
- comparación no soportada con la evidencia disponible.
```

### Texto sugerido

```text
Esta revisión puede señalar costos o precios de proveedores que conviene revisar, pero no confirma variaciones definitivas si no hay períodos, monedas y productos comparables.
```

---

# 8. Claims prohibidos en la entrega

Nunca incluir:

```text
- “la empresa está auditada”;
- “la caja está conciliada”;
- “el margen real contable es...”;
- “el resultado fiscal es...”;
- “esto reemplaza al contador”;
- “la IA resolvió automáticamente”;
- “los datos son correctos”;
- “no hay errores”;
- “diagnóstico integral de la empresa”.
```

Usar en cambio:

```text
- “según los datos declarados”;
- “en esta hoja analizada”;
- “con estas columnas”;
- “como revisión inicial”;
- “como triage operativo”;
- “requiere revisión humana”;
- “hay faltantes”;
- “no se pudo determinar con esta evidencia”.
```

---

# 9. Ejemplo aplicado: cafeteria_abc.xlsx

```markdown
# Entrega PymIA — Revisión inicial de precios y márgenes

## 1. Resumen ejecutivo

Analizamos el archivo **cafeteria_abc.xlsx** como revisión inicial de precios, costos y márgenes.

La revisión se realizó sobre datos declarados por la empresa y debe leerse como un primer auxilio operativo, no como auditoría contable ni diagnóstico integral.

Resultado general:

- Estado del caso: **DELIVERED**
- Herramienta aplicada: **precio_margen_basico**
- Resultados válidos: **15**
- Datos inválidos: **0**
- Datos faltantes: **0**

## 2. Archivo analizado

- Archivo recibido: **cafeteria_abc.xlsx**
- Tipo de archivo: **XLSX**
- Área revisada: **precios, costos y margen básico**

## 3. Qué revisamos

Usamos la hoja **Productos** y las columnas asociadas a costo y precio.

## 4. Herramienta aplicada

| Herramienta | Para qué se usó | Estado |
|---|---|---|
| precio_margen_basico | Calcular margen básico por producto usando precio y costo declarados | OK |

## 5. Resultados principales

Se procesaron 15 productos. Los 15 cálculos fueron válidos. El rango de margen observado estuvo aproximadamente entre 54.08% y 67.27%, según los datos declarados en el archivo.

## 6. Archivos entregados

Se generaron 15 archivos XLSX con resultados individuales de revisión de margen.

## 7. Faltantes, inválidos o bloqueos

No se detectaron faltantes ni inputs inválidos en esta revisión.

## 8. Límites de esta entrega

Esta entrega no es auditoría contable, no valida impuestos, no confirma que los datos declarados sean correctos y no reemplaza revisión humana.

## 9. Próxima acción sugerida

Revisar si los márgenes calculados coinciden con la política comercial esperada y priorizar productos donde el margen observado no coincida con la estrategia de precios.
```

---

# 10. Checklist de entrega owner-facing

Antes de entregar, verificar:

```text
[ ] El archivo analizado está identificado.
[ ] El alcance está escrito en lenguaje claro.
[ ] Las hojas usadas están indicadas.
[ ] Las columnas interpretadas están indicadas.
[ ] Las tools ejecutadas están nombradas.
[ ] Los resultados OK / INVALID / MISSING están traducidos.
[ ] Los archivos entregados están listados.
[ ] Los faltantes están explícitos.
[ ] Los límites están explícitos.
[ ] No hay claims prohibidos.
[ ] Hay próxima acción sugerida.
[ ] El texto no promete autonomía, auditoría ni diagnóstico integral.
```

---

# 11. Relación con otros documentos

Este template depende de:

```text
docs/producto/SERVICE_1_FULL_OPERATOR_PLAYBOOK_V1.md
docs/producto/SERVICE_1_CAPABILITY_COMPLETION_MATRIX_V1.md
```

El playbook define cómo operar.
La matriz define qué capacidades existen.
Este template define cómo entregar.

---

# 12. Veredicto

```text
OWNER_FACING_DELIVERY_TEMPLATE: CREATED
SERVICE_1_COMMERCIAL_DELIVERY_LAYER: PARTIAL_READY
NEXT_ACTION: verify markdown and scope; then decide commit
```
