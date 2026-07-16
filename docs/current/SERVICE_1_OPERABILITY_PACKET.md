# Servicio 1 — Operability Packet V1

**Ciclo:** `CYCLE_030_OPERABILITY_PACKET_FOR_SERVICE_1`  
**Fecha:** 2026-07-16  
**Estado:** `ACTIVE`

## Propósito

Este paquete explica cómo operar el MVP determinístico asistido de Servicio 1 sin abrir nuevas rutas técnicas.

Autoridad:

```text
CLI oficial: python -m pymia.cli.service_1_product
Raíz canónica: pymia/smartpyme/service_1_product_pipeline_v1.py
Fixture de prueba: prueba_excels/cafeteria_abc.xlsx
Sheet de prueba: Ventas
```

## Modo A — ejecución explícita de tool permitida

### 1. Crear carpeta de trabajo

```powershell
mkdir .tmp\service_1_ops -Force
mkdir .tmp\service_1_ops\output -Force
```

### 2. Crear `owner_column_answers.json`

```json
{
  "VentaID": "identificador único de la venta",
  "Fecha": "fecha en que se realizó la venta",
  "Hora": "hora en que se realizó la venta",
  "SucursalID": "identificador de la sucursal",
  "ProductoID": "identificador del producto vendido",
  "Cantidad": "cantidad de unidades vendidas",
  "PrecioUnitario": "precio de venta por unidad",
  "MetodoPago": "medio de pago utilizado",
  "CanalVenta": "canal por el que se realizó la venta",
  "Descuento": "descuento aplicado a la venta",
  "Empleado": "empleado que registró o realizó la venta"
}
```

### 3. Crear `tool_requests.json`

```json
[
  {
    "tool_ref": "precio_margen_basico",
    "inputs": {
      "precio_venta": 1200,
      "costo_unitario": 800
    }
  }
]
```

### 4. Primer pase

```powershell
python -m pymia.cli.service_1_product `
  --xlsx prueba_excels/cafeteria_abc.xlsx `
  --owner-column-answers .tmp/service_1_ops/owner_column_answers.json `
  --tool-requests .tmp/service_1_ops/tool_requests.json `
  --output-dir .tmp/service_1_ops/output `
  --sheet-name Ventas `
  --result-json .tmp/service_1_ops/first_pass.json
```

Resultado esperado:

```text
status = NEEDS_OWNER_CONFIRMATION
product_pipeline.tools_executed = false
no debe existir XLSX de salida todavía
```

### 5. Crear `semantic_owner_answers.json`

Abrir `.tmp/service_1_ops/first_pass.json` y leer:

```text
product_pipeline.owner_questions
```

Para cada pregunta, crear una entrada:

```json
{
  "<column_name>": "<one allowed option id>"
}
```

Regla estricta:

```text
El valor debe salir de allowed_option_ids.
No usar texto libre.
No inventar option_id.
```

### 6. Segundo pase

```powershell
python -m pymia.cli.service_1_product `
  --xlsx prueba_excels/cafeteria_abc.xlsx `
  --owner-column-answers .tmp/service_1_ops/owner_column_answers.json `
  --semantic-owner-answers .tmp/service_1_ops/semantic_owner_answers.json `
  --tool-requests .tmp/service_1_ops/tool_requests.json `
  --output-dir .tmp/service_1_ops/output `
  --sheet-name Ventas `
  --result-json .tmp/service_1_ops/final_pass.json
```

Resultado esperado:

```text
status = PRODUCT_PIPELINE_READY
product_pipeline.semantic_bindings_confirmed = true
product_pipeline.tools_executed = true
product_pipeline.physical_run.executed_tool_refs = ["precio_margen_basico"]
.tmp/service_1_ops/output contiene al menos un .xlsx
```

## Modo B — plan gobernado sin ejecución

Usar `--requested-capability` en lugar de `--tool-requests`.

```powershell
python -m pymia.cli.service_1_product `
  --xlsx <ventas_cobros.xlsx> `
  --owner-column-answers <owner_column_answers.json> `
  --semantic-owner-answers <semantic_owner_answers.json> `
  --requested-capability sold_vs_collected_gap `
  --output-dir <output_dir> `
  --sheet-name Ventas `
  --result-json <result.json>
```

Resultado esperado:

```text
status = COMPUTATION_PLAN_READY
product_pipeline.tools_executed = false
product_pipeline.physical_run = null
product_pipeline.computation_plan.status = READY_FOR_COMPUTATION
product_pipeline.computation_plan.formula_id = LIQ_001_vendido_cobrado
product_pipeline.computation_plan.runtime_authorized = false
product_pipeline.computation_plan.tool_execution_authorized = false
product_pipeline.computation_plan.computation_executed = false
```

## Estados operativos

### PASS

```text
PRODUCT_PIPELINE_READY
COMPUTATION_PLAN_READY
```

### BLOCKED / requiere dueño

```text
NEEDS_OWNER_CONFIRMATION
BLOCKED
```

## Bloqueos esperados

```text
XLSX inexistente.
JSON inválido.
Faltan respuestas del dueño para columnas.
Respuestas semánticas en texto libre.
Se pasan --tool-requests y --requested-capability al mismo tiempo.
No se pasa ni --tool-requests ni --requested-capability.
```

## Límites operativos

```text
No hay selección automática de tool desde el Excel.
No hay autoridad LLM en runtime.
LIQ_001 llega a plan, no a ejecución.
No hay Servicio 2/3 en este paquete.
```
