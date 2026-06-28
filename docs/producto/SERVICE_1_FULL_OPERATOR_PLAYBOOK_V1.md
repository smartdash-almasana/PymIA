# SERVICE_1_FULL_OPERATOR_PLAYBOOK_V1

## Estado

```text
STATUS: OPERATIONAL_PLAYBOOK_V1
SCOPE: Servicio 1 asistido / operador humano
RUNTIME: existente
STAGE_6: no habilitado
AUTONOMIA: no
COMMIT_READY: pending review
```

---

# 1. Propósito

Este playbook define cómo operar **Servicio 1** de PymIA sobre archivos Excel/CSV de PyMEs sin improvisar, sin abrir capacidades nuevas y sin forzar diagnósticos fuera de alcance.

Servicio 1 es un **Laboratorio Operacional Asistido**:

```text
- el operador recibe archivos;
- el sistema detecta estructura;
- el operador elige familia First Aid;
- el operador arma tool_requests explícitas;
- las tools ejecutan;
- el sistema genera archivos de salida;
- el operador revisa y entrega.
```

Regla madre:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

---

# 2. Alcance operativo

Servicio 1 puede operar de forma supervisada sobre:

```text
- archivos XLSX;
- archivos CSV;
- hojas tabulares;
- columnas identificables;
- datos declarados por el cliente;
- casos acotados por período, área o problema.
```

Puede entregar:

```text
- XLSX de análisis por tool;
- owner_message.md;
- operator_packet.json;
- pipeline_result.json;
- detected_structure.json;
- column_confirmation_packet.json;
- README de entrega;
- QA artifacts;
- manifest si está disponible.
```

---

# 3. Fuera de alcance

Servicio 1 no debe prometer ni ejecutar:

```text
- auditoría contable;
- certificación fiscal;
- conciliación bancaria definitiva;
- IVA / IIBB / liquidaciones fiscales;
- asientos contables automáticos;
- lectura OCR/PDF productiva;
- APIs bancarias;
- Mercado Pago API;
- Mercado Libre API;
- diagnóstico autónomo;
- chatbot productivo;
- Stage 6;
- mapeo automático universal NormalizedTableV1 -> tool_requests.
```

Si un caso requiere esas capacidades, marcar:

```text
BLOCKED / OUT_OF_SCOPE / NEEDS_OPERATOR_MAPPING
```

---

# 4. Inputs aceptados

## Aceptados

```text
- .xlsx
- .csv
- tablas con encabezados claros
- hojas de ventas
- hojas de productos
- hojas de costos
- hojas de stock
- hojas de caja/gastos
- hojas de proveedores
```

## No aceptados en runtime actual

```text
- PDF;
- imágenes;
- capturas;
- extractos bancarios no tabulares;
- credenciales;
- tokens;
- claves fiscales;
- accesos a sistemas externos.
```

---

# 5. Familias First Aid operables

## 5.1 precio_margen_basico

### Uso

Revisar relación básica entre precio de venta y costo unitario.

### Inputs runtime

```text
precio_venta
costo_unitario
```

### Columnas orientativas

```text
producto
sku
categoria
familia
proveedor
precio
costo
```

### Acción del operador

Armar una `tool_request` por producto, SKU o fila representativa.

### Bloquear si

```text
- falta precio_venta;
- falta costo_unitario;
- precio_venta <= 0;
- costo_unitario <= 0;
- el costo no corresponde al mismo producto;
- la moneda no está clara.
```

---

## 5.2 stock_alertas_basicas

### Uso

Detectar señales básicas de stock bajo o crítico.

### Inputs runtime

```text
sku
stock_actual
stock_minimo
```

### Columnas orientativas

```text
producto
categoria
ubicacion
stock_objetivo
rotacion
```

### Acción del operador

Armar una `tool_request` por SKU o producto.

### Bloquear si

```text
- falta SKU o identificador equivalente;
- falta stock_actual;
- falta stock_minimo;
- los valores no son numéricos;
- stock_actual y stock_minimo pertenecen a períodos distintos.
```

---

## 5.3 caja_diaria_triage

### Uso

Triage básico de caja. No es conciliación definitiva.

### Inputs runtime actuales

```text
saldo_inicial
ingresos
egresos
```

### Modos operativos del operador

```text
MODO AGREGADO:
- armar una única tool_request con saldo_inicial, ingresos y egresos consolidados.

MODO POR_FECHA:
- calcular por fuera del payload runtime los totales por fecha;
- armar una tool_request por fecha usando el mismo contrato runtime: saldo_inicial, ingresos y egresos;
- documentar fecha y filas fuente en notas operativas del caso, no dentro del payload runtime si el contrato no lo soporta.
```

### Acción del operador

Antes de armar `tool_requests`, declarar:

```text
caja_mode: AGREGADO | POR_FECHA
```

### Bloquear si

```text
- no hay período;
- no hay ingresos o ventas;
- no hay caja declarada o egresos equivalentes;
- se pretende conciliación bancaria definitiva;
- se mezclan caja, banco, Mercado Pago y tarjetas sin criterio claro.
```

---

## 5.4 gastos_triage

### Uso

Clasificación o revisión básica de gastos declarados.

### Inputs orientativos

```text
concepto
importe
```

### Columnas útiles

```text
fecha
categoria
proveedor
medio_pago
observacion
```

### Acción del operador

Armar `tool_requests` sólo si el archivo permite distinguir gastos de otros movimientos.

### Bloquear si

```text
- los movimientos mezclan ventas, cobros, gastos y transferencias sin clasificación;
- no hay importe;
- no hay tipo de movimiento;
- el usuario espera imputación contable definitiva.
```

---

## 5.5 proveedores_precio_variacion_triage

### Uso

Detectar variaciones básicas de precios o costos de proveedores según el contrato disponible.

### Input runtime actual conocido

```text
precio_o_costo
```

### Columnas orientativas del archivo

```text
proveedor
producto
sku
fecha
periodo
categoria
cantidad
moneda
precio
costo
```

### Acción del operador

Verificar que la fila usada represente un precio/costo comparable. Si el análisis requiere precio anterior y actual, documentar esa comparación en notas operativas del caso y no inventar campos que el contrato runtime no soporte.

### Bloquear si

```text
- no hay proveedor cuando la comparación depende del proveedor;
- no hay producto comparable;
- se mezclan productos distintos;
- no está clara la moneda;
- no hay período de comparación cuando se reporta variación;
- el contrato runtime no admite el análisis que se intenta prometer.
```

---

# 6. Flujo operativo estándar

## Paso 1 — Recibir archivo

Guardar el archivo en carpeta local de trabajo, fuera de commits.

```text
E:\BuenosPasos\smartbridge\PymIA\prueba_excels\
```

No usar credenciales ni datos sensibles innecesarios.

## Paso 2 — Intake

Ejecutar intake/harness existente y confirmar:

```text
- archivo soportado;
- hojas detectadas;
- columnas detectadas;
- filas detectadas;
- reason_code;
- runtime_authorized=false.
```

Si intake falla:

```text
status: BLOCKED
reason: INTAKE_FAILED
```

## Paso 3 — Leer estructura

Revisar:

```text
- nombres de hojas;
- cantidad de filas;
- columnas disponibles;
- tipos aparentes de datos;
- hojas candidatas.
```

No ejecutar tools todavía.

## Paso 4 — Elegir familia First Aid

| Señal en columnas | Familia candidata |
|---|---|
| precio + costo | precio_margen_basico |
| SKU + stock actual + stock mínimo | stock_alertas_basicas |
| ingresos + egresos + saldo / caja | caja_diaria_triage |
| tipo movimiento + importe | gastos_triage |
| proveedor/producto/precio/costo comparable | proveedores_precio_variacion_triage |

Si ninguna familia calza:

```text
status: UNSUPPORTED_FOR_SERVICE_1_FIRST_AID
```

## Paso 5 — Confirmar modo operativo

Antes de armar `tool_requests`, definir fuera del payload runtime:

```text
tool_family:
input_sheet:
mapping_mode:
period:
unit:
currency:
operator_notes:
```

Para caja:

```text
caja_mode: AGREGADO | POR_FECHA
```

## Paso 6 — Armar tool_requests

Las `tool_requests` deben ser explícitas y respetar el contrato runtime actual.

No usar mapeo automático universal.

El payload runtime debe incluir sólo campos soportados por la tool.

La trazabilidad operativa debe registrarse fuera del payload runtime, por ejemplo en notas del caso:

```text
tool_ref:
source_sheet:
source_rows:
operator_mapping_notes:
```

Si el operador no puede justificar el mapeo:

```text
status: NEEDS_OPERATOR_MAPPING
```

## Paso 7 — Ejecutar runtime existente

Ejecutar sólo runtime ya disponible.

Prohibido:

```text
- modificar código;
- crear módulos;
- tocar pipeline;
- tocar harness;
- abrir Stage 6;
- inventar adaptadores.
```

Si falta comando o contrato:

```text
status: BLOCKED
reason: NO_EXECUTION_CONTRACT
```

## Paso 8 — Revisar resultados

Clasificar resultados:

```text
OK
INVALID_INPUT
MISSING_INPUTS
BLOCKED
```

`MISSING_INPUTS` no es fracaso. Es bloqueo sano.

`INVALID_INPUT` puede indicar:

```text
- dato negativo;
- cero inválido;
- columna mal mapeada;
- error real del archivo;
- input fuera de contrato.
```

## Paso 9 — Revisar outputs

Confirmar existencia de:

```text
- pipeline_result.json;
- operator_packet.json;
- detected_structure.json;
- column_confirmation_packet.json;
- owner_message.md;
- XLSX generados;
- README / manifest si aplica.
```

Si no se generan outputs:

```text
status: PARTIAL / BLOCKED
```

## Paso 10 — Preparar entrega

La entrega debe decir:

```text
- qué archivo se analizó;
- qué hojas se usaron;
- qué columnas se interpretaron;
- qué tools se ejecutaron;
- qué resultados salieron;
- qué faltantes existen;
- qué no se puede afirmar.
```

No debe decir:

```text
- diagnóstico definitivo;
- auditoría;
- certificación;
- conciliación cerrada;
- resultado fiscal;
- decisión automática.
```

---

# 7. Estados operativos

```text
SUPPORTED
UNSUPPORTED
INTAKE_ONLY
NEEDS_OPERATOR_MAPPING
EXECUTED
DELIVERED
PARTIAL
BLOCKED
```

## Definición rápida

```text
SUPPORTED: archivo legible por intake.
INTAKE_ONLY: estructura detectada sin ejecución de tools.
NEEDS_OPERATOR_MAPPING: hay columnas candidatas, pero requiere decisión humana.
EXECUTED: se ejecutó al menos una tool.
DELIVERED: se generaron outputs revisables.
PARTIAL: algo corrió, pero falta una parte.
BLOCKED: no avanzar sin nueva evidencia o contrato.
UNSUPPORTED: fuera del alcance actual de Servicio 1.
```

---

# 8. Reglas de bloqueo

Bloquear si:

```text
- falta columna obligatoria;
- hay valores no numéricos donde se exige número;
- se mezclan períodos;
- no hay moneda clara;
- se pretende diagnóstico contable;
- se pretende conciliación definitiva;
- se requieren APIs;
- se requiere PDF/OCR;
- el archivo pertenece a una familia sin tool actual;
- el operador no puede explicar el mapping;
- la salida sería engañosa.
```

Bloquear no es fallar. Bloquear evita alucinación operativa.

---

# 9. Claims prohibidos

Nunca afirmar:

```text
- “la empresa está auditada”;
- “la caja está conciliada definitivamente”;
- “el margen real contable es...”;
- “el resultado fiscal es...”;
- “esto reemplaza al contador”;
- “la IA resolvió automáticamente”;
- “los datos son correctos”;
- “no hay errores”;
- “esto es diagnóstico integral de la empresa”.
```

Usar en cambio:

```text
- “según los datos declarados”;
- “en esta hoja analizada”;
- “con estas columnas”;
- “como triage inicial”;
- “requiere revisión humana”;
- “hay faltantes”;
- “no se pudo determinar con esta evidencia”.
```

---

# 10. Checklist final del operador

```text
[ ] Archivo soportado.
[ ] Hojas detectadas.
[ ] Columnas relevantes identificadas.
[ ] Familia First Aid elegida.
[ ] Mapping documentado fuera del payload si el contrato no lo soporta.
[ ] Tool_requests explícitas y compatibles con contrato runtime.
[ ] Runtime existente usado.
[ ] Runtime no modificado.
[ ] Stage 6 no abierto.
[ ] Resultados OK / INVALID / MISSING revisados.
[ ] Outputs generados.
[ ] Owner message revisado.
[ ] Claims prohibidos ausentes.
[ ] Faltantes documentados.
[ ] Estado final asignado.
```

---

# 11. Registro mínimo por caso

```text
case_id:
archivo:
fecha:
operador:
familia_first_aid:
hojas_usadas:
columnas_usadas:
mapping_mode:
tool_requests_count:
results_ok:
results_invalid:
results_missing:
outputs_generados:
blockers:
claims_prohibidos_detectados:
estado_final:
leccion_aprendida:
```

---

# 12. Criterio de servicio vendible

Servicio 1 puede ofrecerse de forma controlada cuando el operador pueda repetir este ciclo:

```text
recibir archivo
→ intake
→ detectar estructura
→ elegir familia First Aid
→ armar tool_requests
→ ejecutar
→ generar outputs
→ revisar
→ entregar
→ registrar faltantes
```

No hace falta que todas las familias estén automatizadas.

Sí hace falta que el operador no improvise.

---

# 13. Priorización actual de familias

## Operativas / validadas en ejecución o smoke

```text
precio_margen_basico
stock_alertas_basicas
```

Notas:

```text
precio_margen_basico:
- operativo y demo-ready con cafeteria_abc.xlsx.

stock_alertas_basicas:
- operativo en smoke con datos existentes, con caveat de calidad de datos cuando aparezcan inputs inválidos.
```

## Parciales / requieren mapping operativo más cuidadoso

```text
gastos_triage
caja_diaria_triage
proveedores_precio_variacion_triage
```

## Fuera de alcance actual

```text
producción industrial KPI
conciliación definitiva
PDF/OCR
APIs
```

---

# 14. Regla antideriva

Si un archivo no calza con una familia First Aid actual:

```text
no forzar,
no inventar tool,
no abrir Stage 6,
no simular diagnóstico.
```

Registrar:

```text
UNSUPPORTED_FOR_SERVICE_1_FIRST_AID
```

o:

```text
NEEDS_OPERATOR_MAPPING
```

---

# 15. Cierre

Este playbook convierte Servicio 1 en una operación repetible.

No completa todo el producto.

Pero evita que cada Excel sea una conversación nueva.

Servicio 1 avanza cuando cada caso produce:

```text
archivo leído,
mapping explícito,
tool ejecutada,
output generado,
bloqueo sano si corresponde,
y aprendizaje registrado.
```
