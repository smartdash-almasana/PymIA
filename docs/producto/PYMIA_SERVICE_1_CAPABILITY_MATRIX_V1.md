# PYMIA_SERVICE_1_CAPABILITY_MATRIX_V1

## Estado

```text
Tipo: ROADMAP_CYCLE_4
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Convertir el catálogo y la arqueología inicial de Servicio 1 en una matriz operativa de capacidades.

Este documento no autoriza código, runtime, loaders, pipeline, XLSX delivery ni LLM adapter.

---

# 1. Fuente

Documento rector previo:

```text
docs/producto/PYMIA_SERVICE_1_ARCHAEOLOGY_AUDIT_V1.md
```

Catálogo fuente:

```text
docs/producto/PYMIA_SERVICE_1_FULL_CATALOG_V1.md
```

Formato requerido por roadmap:

```text
CAPACIDAD | CLIENTE | INPUT | OUTPUT | ESTADO | DEPENDENCIAS | RIESGO
```

---

# 2. Estados usados

```text
MISSING              = no existe evidencia suficiente documental ni técnica
DEFINED              = concepto definido, sin diseño técnico operativo
DOCUMENTED_ONLY      = documentado, sin ejecución productiva
IMPLEMENTED_PARTIAL  = hay código o artefactos parciales, no integrados como producto Servicio 1
IMPLEMENTED_FOCAL    = implementado y testeado focalmente, no runtime productivo
NEEDS_WIRING         = existe pieza reutilizable, falta conexión gobernada
BLOCKED              = requiere decisión previa
SELLABLE             = vendible operativo
```

Estado global actual:

```text
Servicio 1 todavía no es SELLABLE como sistema completo.
First Aid Activation sí está IMPLEMENTED_FOCAL.
```

---

# 3. Matriz principal

| CAPACIDAD | CLIENTE | INPUT | OUTPUT | ESTADO | DEPENDENCIAS | RIESGO |
|---|---|---|---|---|---|---|
| Catálogo Servicio 1 | Interno / producto | Documentos producto | Catálogo completo | DOCUMENTED_ONLY | Ninguna | Bajo |
| Arqueología Servicio 1 | Interno / producto | Docs + repo | Mapa de evidencia | DOCUMENTED_ONLY | Catálogo | Bajo |
| Capability Matrix | Interno / producto | Catálogo + arqueología | Matriz operativa | DOCUMENTED_ONLY | Arqueología | Bajo |
| First Aid Activation | Interno / owner | tool_ref + evidencia mínima + claims + service_depth | estado de activación | IMPLEMENTED_FOCAL | seed pack + contrato activación | Medio: no ejecutar runtime |
| First Aid seed pack | Interno | JSON candidato | pack validable | IMPLEMENTED_FOCAL | contrato toolbox | Medio: no usar como loader productivo |
| First Aid scenarios | Interno / QA | casos conceptuales | tests de estados | IMPLEMENTED_FOCAL | evaluator | Bajo |
| precio_margen_basico | Dueño PyME | precio_venta + costo_unitario | margen básico / faltantes / limitaciones | DOCUMENTED_ONLY | evaluator + futura tool | Medio: no afirmar rentabilidad real |
| caja_diaria_triage | Dueño PyME | saldo_inicial + ingresos + egresos | flujo simple / faltantes / limitaciones | DOCUMENTED_ONLY | evaluator + futura tool | Medio: no afirmar saldo bancario real |
| stock_alertas_basicas | Dueño PyME | producto + stock_actual + stock_minimo | alerta stock / faltantes / limitaciones | DOCUMENTED_ONLY | evaluator + futura tool | Medio: no afirmar stock físico |
| gastos_triage | Dueño PyME / contador | concepto + importe | orden inicial de gastos | DOCUMENTED_ONLY | evaluator + futura tool | Medio: no clasificación contable definitiva |
| proveedores_precio_variacion_triage | Dueño PyME | proveedor + insumo + precio/costo | variación visible / faltantes | DOCUMENTED_ONLY | evaluator + futura tool | Medio: no estrategia de compras |
| Laboratorio Excel | Dueño PyME | Excel/CSV/PDF caótico | archivo curado / señales / limitaciones | IMPLEMENTED_PARTIAL | document_ingestion + packaging producto | Alto: puede confundirse con Excel reader genérico |
| File Intake XLSX | Dueño PyME | XLSX | perfil + evidencia estructurada | IMPLEMENTED_PARTIAL | document_ingestion | Medio: falta frontera Servicio 1 |
| File Intake CSV | Dueño PyME | CSV | mapeo semántico / evidencia | IMPLEMENTED_PARTIAL | mapper/normalizer | Medio: faltan casos Servicio 1 |
| File Intake PDF | Dueño PyME / contador | PDF tabular | Excel normalizado | MISSING | contrato PDF intake | Alto |
| XLSX Delivery First Aid | Dueño PyME | resultado validado de tool | archivo Excel descargable | DOCUMENTED_ONLY | tool ejecutable + delivery module | Alto: producto sin archivo pierde valor |
| Excel Factory / Exceland | Interno / producto | specs YAML / fórmulas / templates | XLSX determinísticos | IMPLEMENTED_PARTIAL | puente controlado hacia PymIA-Live | Alto: no migrar Exceland entero |
| ExcelSpec | Interno / IA con arnés | pedido usuario | spec validable | DEFINED | LLM adapter + validador | Alto: IA no debe generar XLSX opaco |
| Plantilla caja diaria | Dueño PyME | caja diaria | XLSX template | IMPLEMENTED_PARTIAL | Exceland bridge | Medio |
| Plantilla stock | Dueño PyME | stock | XLSX template | IMPLEMENTED_PARTIAL | Exceland bridge | Medio |
| Plantilla margen | Dueño PyME | precios/costos | XLSX template | IMPLEMENTED_PARTIAL | Exceland bridge | Medio |
| Plantilla costos | Dueño PyME | costos producto | XLSX template | IMPLEMENTED_PARTIAL | Exceland bridge | Medio |
| Punto de equilibrio | Dueño PyME / diagnóstico | costos + precio + margen | cálculo punto equilibrio | BLOCKED | Servicio 2 / suficiencia | Alto: no First Aid |
| Conciliación bancaria | Contador / dueño | extracto banco + planilla contable | conciliados / pendientes / diferencias / XLSX | IMPLEMENTED_PARTIAL | entity resolution + contrato | Alto |
| Mercado Pago / tarjetas | Contador / dueño | reporte MP + banco + ventas | comisiones / retenciones / acreditaciones | MISSING | conciliación base | Alto |
| Facturas vs cobros | Contador / dueño | facturas + cobros | cobradas / impagas / parciales | MISSING | modelo factura-cobro | Alto |
| Papeles de trabajo | Contador | conciliaciones + resultados validados | workpaper XLSX | MISSING | conciliación + XLSX delivery | Alto |
| IVA / IIBB | Contador | ventas + compras + alícuotas | cálculo fiscal / alertas | MISSING | normativa vigente + Servicio 2 | Alto |
| Asientos automáticos | Contador | operaciones + plan de cuentas | asientos | MISSING | modelo contable completo | Alto |
| Alertas / vencimientos | Dueño PyME | tareas / fechas / umbrales | alertas / brief | IMPLEMENTED_PARTIAL | wiring + FSM | Medio |
| Gestor de tareas | Dueño PyME | tareas + responsables + fechas | lista ordenada / alertas | MISSING | decisión de alcance | Medio |
| Commercial Modules | Producto / interno | module registry + schema | módulos declarativos | DOCUMENTED_ONLY | boundary + futura validación | Medio |
| cobranzas_vencidas | PyME / contador | cliente + monto + vencimiento + estado | findings + acciones sugeridas | DOCUMENTED_ONLY | module loader no creado | Medio |
| stock_roto | PyME | sku + producto + stock_actual + stock_minimo | findings + acciones sugeridas | DOCUMENTED_ONLY | module loader no creado | Medio |
| conciliacion_ventas_ml | PyME / contador | orden + sku + montos + comisión | conciliación ML / findings | DOCUMENTED_ONLY | module loader no creado | Alto |
| Service 1 TaskSpec | Interno | pedido usuario | task_type + inputs + output esperado | MISSING | Capability Matrix | Alto |
| Service 1 FSM | Interno | TaskSpec + evidencia + confirmaciones | estado gobernado | DOCUMENTED_ONLY | TaskSpec | Alto |
| Service 1 Pipeline | Interno | task + evidencia + tool result | entrega gobernada | DOCUMENTED_ONLY | TaskSpec + FSM + tools | Alto |
| LLM Adapter Servicio 1 | Interno | contexto + estado + límites | preguntas/specs/explicaciones | DOCUMENTED_ONLY | FSM + contratos | Alto |
| Chatbot Servicio 1 | Dueño PyME | texto + archivos | interacción + entregables | DOCUMENTED_ONLY | FSM + LLM adapter + pipeline | Alto |

---

# 4. Capacidades priorizadas

## Prioridad A — cerrar núcleo sin runtime productivo

```text
Service 1 TaskSpec V1
```

Motivo:

```text
Antes de ejecutar tools o pipeline, el sistema debe representar formalmente qué pidió el usuario.
```

Dependencias:

```text
Capability Matrix V1
First Aid Activation Evaluator
Service depth classifier
```

---

## Prioridad B — herramientas First Aid ejecutables mínimas

Orden conservador:

```text
1. precio_margen_basico
2. caja_diaria_triage
3. stock_alertas_basicas
```

Motivo:

```text
Son las herramientas de menor riesgo si quedan limitadas a cálculo simple, faltantes y disclaimers.
```

Condición:

```text
No emitir diagnóstico.
No generar XLSX todavía.
No usar IA para cálculo.
```

---

## Prioridad C — XLSX Delivery

```text
first_aid_xlsx_delivery.py
```

Motivo:

```text
Servicio 1 no puede quedarse sólo en texto. El archivo descargable es parte central del producto.
```

Condición:

```text
Sólo después de tener al menos una tool First Aid ejecutable y testeada.
```

---

## Prioridad D — pipeline y FSM

```text
service_1_pipeline.py
SERVICE_1_FSM_V1
```

Motivo:

```text
El pipeline y la FSM deben gobernar ejecución y entrega, no reemplazar contratos.
```

Condición:

```text
No abrir antes de TaskSpec y primera tool ejecutable.
```

---

# 5. No abrir todavía

```text
Mercado Pago / tarjetas
IVA / IIBB
Asientos automáticos
Chatbot externo
Commercial Modules runtime
LLM Adapter productivo
Pipeline compartido First Aid + Commercial Modules
```

Motivo:

```text
Son capas de mayor complejidad y dependencia. Abrirlas ahora rompería la secuencia del roadmap.
```

---

# 6. Decisión de dirección

La dirección inmediata no es seguir agregando documentación genérica.

La dirección inmediata es:

```text
Capability Matrix V1
→ Service 1 TaskSpec V1
→ primera tool First Aid ejecutable limitada
→ XLSX Delivery mínimo
→ Service 1 Pipeline
```

---

# 7. Próximo documento recomendado

```text
docs/producto/PYMIA_SERVICE_1_TASKSPEC_V1.md
```

Objetivo:

```text
Definir cómo se representa un pedido Servicio 1 antes de ejecutar herramientas.
```

Debe cubrir:

```text
task_id
task_type
service_depth
owner_problem
evidence_required
evidence_received
column_confirmation_required
selected_tool_ref
expected_output
blocking_state
next_allowed_action
forbidden_claims
runtime_authorized
```

---

# 8. Veredicto

```text
PYMIA_SERVICE_1_CAPABILITY_MATRIX_V1 = DRAFT_APPLIED
```

Condición:

```text
No autoriza runtime productivo. Habilita el diseño de Service 1 TaskSpec V1.
```
