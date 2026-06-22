# SERVICE_1_MANUAL_OPERATOR_RUNBOOK_V1

## Estado

```text
Tipo: OPERATOR_RUNBOOK
Servicio: SERVICE_1
Lane: Manual First Aid Delivery
Estado: DRAFT_APPLIED
Runtime impact: NONE
Pipeline impact: NONE
FSM impact: NONE
LLM impact: NONE
Chatbot impact: NONE
```

## Propósito

Este runbook describe cómo un operador humano puede ejecutar manualmente la lane First Aid de Servicio 1 usando componentes ya implementados.

El objetivo es producir entregables operativos mínimos:

```text
FirstAidToolResultV1[]
→ aggregate
→ XLSX por resultado
→ summary_text owner-facing
→ metadata de entrega
```

Este runbook no declara Servicio 1 completo.
No habilita pipeline productivo.
No habilita FSM.
No habilita chatbot.
No habilita LLM.
No habilita document ingestion.
No habilita Exceland bridge.

---

# 1. Componentes disponibles

## 1.1 Contrato común

```text
PymIA-Live/pymia/smartpyme/first_aid_tool_result_v1.py
```

Contrato:

```text
FirstAidToolResultV1
```

Regla obligatoria:

```text
runtime_authorized = False
```

## 1.2 Tools First Aid disponibles

```text
precio_margen_basico
caja_diaria_triage
stock_alertas_basicas
```

Archivos:

```text
PymIA-Live/pymia/smartpyme/first_aid_precio_margen_basico_v1.py
PymIA-Live/pymia/smartpyme/first_aid_caja_diaria_triage_v1.py
PymIA-Live/pymia/smartpyme/first_aid_stock_alertas_basicas_v1.py
```

## 1.3 Agregación

```text
PymIA-Live/pymia/smartpyme/first_aid_delivery_aggregate_v1.py
```

Función:

```text
build_first_aid_delivery_aggregate_v1(...)
```

## 1.4 XLSX Delivery

```text
PymIA-Live/pymia/smartpyme/first_aid_xlsx_delivery_v1.py
```

Función:

```text
build_first_aid_xlsx_delivery_v1(...)
```

## 1.5 Flujo manual

```text
PymIA-Live/pymia/smartpyme/service_1_manual_first_aid_delivery_flow_v1.py
```

Función:

```text
build_service_1_manual_first_aid_delivery_flow_v1(...)
```

## 1.6 Smoke case reproducible

```text
PymIA-Live/pymia/smartpyme/service_1_manual_first_aid_smoke_case_v1.py
```

Función:

```text
run_service_1_manual_first_aid_smoke_case_v1(...)
```

---

# 2. Rol del operador

El operador humano debe:

```text
1. recibir datos declarados por el dueño o contador
2. verificar que los datos sean suficientes para una tool First Aid
3. ejecutar sólo tools autorizadas manualmente
4. revisar los FirstAidToolResultV1 generados
5. generar XLSX y summary_text mediante el flujo manual
6. revisar limitaciones y claims prohibidos antes de entregar
7. entregar archivos y resumen sin prometer diagnóstico integral
```

El operador no debe:

```text
afirmar rentabilidad real
afirmar saldo bancario real
afirmar stock físico real
afirmar conciliación cerrada
afirmar archivo normalizado
afirmar diagnóstico integral de empresa
```

---

# 3. Inputs manuales permitidos

## 3.1 Precio / margen básico

Input mínimo:

```text
precio_venta
costo_unitario
```

Output esperado:

```text
margen_bruto_pesos
margen_bruto_porcentaje
markup_porcentaje
```

Advertencia:

```text
No confirma rentabilidad real.
No incluye impuestos, comisiones, costos fijos ni costos indirectos.
```

## 3.2 Caja diaria triage

Input mínimo:

```text
saldo_inicial
ingresos
egresos
```

Output esperado:

```text
flujo_neto
saldo_final_estimado
```

Advertencia:

```text
No confirma saldo bancario real.
No equivale a conciliación.
No valida efectivo físico.
```

## 3.3 Stock alertas básicas

Input mínimo:

```text
producto
stock_actual
stock_minimo
```

Input opcional:

```text
ventas_diarias_promedio
```

Output esperado:

```text
stock_bajo
diferencia_vs_minimo
dias_stock_restante
```

Advertencia:

```text
No confirma stock físico real.
No reemplaza conteo físico.
No confirma quiebre real.
No calcula rotación real.
```

---

# 4. Procedimiento manual

## Paso 1 — Preparar carpeta de salida

Crear una carpeta local de entrega, por ejemplo:

```text
.tmp/service_1_manual_first_aid_delivery/
```

La carpeta debe existir antes de ejecutar el flujo.

## Paso 2 — Construir resultados First Aid

El operador puede ejecutar las tools disponibles con datos declarados.

Ejemplo conceptual:

```text
run_precio_margen_basico_v1(precio_venta=1000, costo_unitario=650)
run_caja_diaria_triage_v1(saldo_inicial=5000, ingresos=2400, egresos=1800)
run_stock_alertas_basicas_v1(producto="SKU-001", stock_actual=7, stock_minimo=10)
```

Cada ejecución debe devolver:

```text
FirstAidToolResultV1
```

Cada resultado debe mantener:

```text
runtime_authorized = False
```

## Paso 3 — Revisar resultados antes de entregar

El operador debe revisar:

```text
status
inputs_used
computed_results
missing_inputs
limitations
forbidden_claims
owner_summary
technical_notes
```

Si hay `MISSING_INPUTS`, el operador puede entregar el aviso de faltantes, pero no debe presentar resultado completo.

Si hay `INVALID_INPUT`, el operador debe pedir corrección de datos.

## Paso 4 — Ejecutar flujo manual de entrega

Usar:

```text
build_service_1_manual_first_aid_delivery_flow_v1(tool_results, output_dir)
```

Entrada:

```text
lista de FirstAidToolResultV1
carpeta de salida existente
```

Salida:

```text
delivery_count
aggregate_id
tool_refs
statuses
deliveries
summary_text
runtime_authorized=False
notes
```

## Paso 5 — Revisar archivos generados

El flujo genera un XLSX por resultado.

Patrón de nombre:

```text
first_aid_001_precio_margen_basico.xlsx
first_aid_002_caja_diaria_triage.xlsx
first_aid_003_stock_alertas_basicas.xlsx
```

La numeración evita colisiones cuando se repite `tool_ref`.

Cada XLSX debe incluir hojas mínimas:

```text
Resumen
Datos usados
Resultados
Faltantes
Limitaciones
Claims prohibidos
Notas técnicas
```

## Paso 6 — Revisar summary_text

El resumen debe incluir:

```text
cantidad de resultados procesados
tool_ref + status por resultado
faltantes detectados si existen
limitaciones principales
aclaraciones conservadoras
frase: Entrega preliminar basada en datos declarados.
```

## Paso 7 — Entrega al dueño o contador

El operador puede entregar:

```text
1. XLSX generados
2. summary_text
3. advertencias/limitaciones
```

No debe entregar como:

```text
diagnóstico integral
conciliación cerrada
certificación contable
validación de stock físico
validación de saldo bancario real
rentabilidad real confirmada
```

---

# 5. Smoke case reproducible

Para validar la lane manual, existe:

```text
run_service_1_manual_first_aid_smoke_case_v1(output_dir)
```

Este smoke case:

```text
ejecuta las 3 tools First Aid con inputs fijos
genera 3 XLSX reales
genera summary_text
genera operator_runbook
devuelve metadata de entrega
```

Uso esperado en test:

```text
python -m pytest tests/smartpyme/test_service_1_manual_first_aid_smoke_case_v1.py tests/smartpyme/test_service_1_manual_first_aid_delivery_flow_v1.py tests/smartpyme/test_first_aid_xlsx_delivery_v1.py tests/smartpyme/test_first_aid_delivery_aggregate_v1.py -q
```

Resultado validado:

```text
53 passed
```

---

# 6. Checklist antes de entregar

El operador debe confirmar:

```text
[ ] Cada result tiene runtime_authorized=False.
[ ] No hay status INVALID_INPUT sin resolver.
[ ] Si hay MISSING_INPUTS, el resumen lo muestra.
[ ] XLSX generados abren correctamente.
[ ] summary_text contiene limitaciones.
[ ] summary_text contiene aclaraciones conservadoras.
[ ] No se promete diagnóstico integral.
[ ] No se promete conciliación cerrada.
[ ] No se promete saldo bancario real.
[ ] No se promete stock físico real.
[ ] No se promete rentabilidad real.
```

---

# 7. Qué hacer ante errores

## 7.1 Output directory inexistente

Acción:

```text
Crear carpeta de salida y reintentar.
```

## 7.2 runtime_authorized=True

Acción:

```text
Bloquear entrega.
Revisar origen del resultado.
No modificar manualmente el payload para forzar entrega.
```

## 7.3 Missing inputs

Acción:

```text
Entregar aviso de faltantes o pedir datos adicionales.
No completar datos por inferencia.
```

## 7.4 Invalid input

Acción:

```text
Pedir corrección del dato.
No corregir por intuición.
No convertir semánticamente valores dudosos.
```

## 7.5 Archivo XLSX no abre

Acción:

```text
No entregar.
Reejecutar smoke/test focal.
Revisar path de salida.
```

---

# 8. Fronteras explícitas

Este runbook no habilita:

```text
pipeline automático
FSM de producto
chatbot
LLM
OCR
document ingestion real
Exceland bridge
conciliación bancaria
Mercado Pago
IVA/IIBB
asientos contables
normalización documental completa
```

Es únicamente una guía de operación manual para la lane First Aid ya implementada.

---

# 9. Estado de Servicio 1 después de este runbook

```text
Servicio 1 First Aid tiene:
- contrato común de resultados
- tres tools determinísticas
- aggregate
- XLSX delivery
- flujo manual de entrega
- smoke case reproducible
- runbook operador manual
```

Todavía falta para Servicio 1 full:

```text
caso semi-real
ingesta real controlada
pipeline mínimo
harness operador
integración con archivos subidos
servicios contables específicos
conciliaciones
Factoría Excel
chatbot bajo arnés
```

---

# 10. Veredicto

```text
SERVICE_1_MANUAL_OPERATOR_RUNBOOK_V1_READY
```
