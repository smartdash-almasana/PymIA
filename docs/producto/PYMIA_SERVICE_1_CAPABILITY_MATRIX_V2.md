# PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2

## Estado

```text
Tipo: CAPABILITY_MATRIX_UPDATE
Estado: DRAFT_APPLIED
Metodología: Gentle AI Development
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Actualizar la matriz Servicio 1 contra el estado real del repo después de los ciclos:

- completion roadmap;
- owner output closeout.

La corrección central de esta V2 es que `Service 1 TaskSpec` ya no queda como `MISSING`.

## Loop Gentle AI aplicado

| Etapa | Aplicación en este ciclo |
|---|---|
| DESIGN | Lectura de Matrix V1, Full Catalog V1, Roadmap V1, Owner Output Closeout V1 y piezas reales del repo |
| BUILD | Creación exclusiva de esta matriz V2 documental |
| TEST | No aplica en este ciclo DOC/UPDATE ONLY |
| AUDIT | Contraste entre V2, repo real y catálogo full |
| HUMAN STOP | Obligatorio después de crear este documento |
| COMMIT/PUSH | No autorizado en este ciclo |
| NEXT CYCLE | Sólo sugerido documentalmente; no implementado aquí |

## Cambio principal contra V1

En `PYMIA_SERVICE_1_CAPABILITY_MATRIX_V1.md`, `Service 1 TaskSpec` figuraba como `MISSING`.

En V2 pasa a:

```text
IMPLEMENTED_PARTIAL
```

Motivo:

- existe vocabulario canónico (`service_1_taskspec_vocabulary_v1.py`);
- existe contrato mínimo (`service_1_taskspec_contract_v1.py`);
- existe frontera pura `FileIntakeResult -> TaskSpecPatch` (`file_intake_taskspec_boundary_v1.py`);
- ya existen outputs aguas abajo que consumen esa frontera (`owner_response_renderer_v1.py`, `owner_message_formatter_v1.py`, `service_1_excel_triage_report_v1.py`);
- todavía falta un assembler completo de `Service1TaskSpec` y sigue sin haber runtime, pipeline ni delivery.

## Estados usados

```text
MISSING
DEFINED
DOCUMENTED_ONLY
IMPLEMENTED_PARTIAL
IMPLEMENTED_FOCAL
IMPLEMENTED_VALIDATED
NEEDS_WIRING
EXPERIMENTAL_FROZEN
BLOCKED
SELLABLE
```

## Matriz principal actualizada

| CAPACIDAD | CLIENTE | INPUT | OUTPUT | ESTADO_V2 | EVIDENCIA | DEPENDENCIAS | RIESGO | NEXT_CYCLE |
|---|---|---|---|---|---|---|---|---|
| Catálogo Servicio 1 | Interno / producto | docs producto | catálogo full | DOCUMENTED_ONLY | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | Ninguna | Bajo | Mantener como fuente maestra |
| Capability Matrix V2 | Interno / producto | catálogo + roadmap + repo | matriz actualizada | DOCUMENTED_ONLY | este documento | catálogo + roadmap + closeout | Bajo | Reauditar por ciclos |
| File Intake V1 | Dueño PyME | archivo | clasificación inicial + límites | IMPLEMENTED_VALIDATED | `file_intake_v1.py` + roadmap V1 | ninguna | Medio: sólo XLSX-first | Mantener frontera sin runtime |
| File Intake → TaskSpecPatch | Interno | `FileIntakeResult` | `TaskSpecPatch` puro | IMPLEMENTED_VALIDATED | `file_intake_taskspec_boundary_v1.py` + roadmap V1 | File Intake V1 | Bajo | Reusar como frontera estable |
| Service 1 TaskSpec Contract | Interno | owner problem + metadata | `Service1TaskSpec` mínimo | IMPLEMENTED_PARTIAL | `service_1_taskspec_contract_v1.py` | vocabulario canónico | Medio: falta assembler completo | `SERVICE_1_TASKSPEC_ASSEMBLER_V1` |
| Service 1 TaskSpec Assembler | Interno | intake + patch + contexto permitido | `Service1TaskSpec` ensamblado | DEFINED | roadmap V1 lo define como próximo build | TaskSpec contract + boundary | Medio | `SERVICE_1_TASKSPEC_ASSEMBLER_V1` |
| OwnerResponseV1 | Dueño PyME | `FileIntakeResult` + `TaskSpecPatch` | respuesta owner-facing mínima | IMPLEMENTED_VALIDATED | `owner_response_renderer_v1.py` + owner output closeout | File Intake + boundary | Bajo | Mantener sin claims extra |
| OwnerMessageFormatterV1 | Dueño PyME / operador | `OwnerResponseV1` | texto plano para canal manual | IMPLEMENTED_VALIDATED | `owner_message_formatter_v1.py` + owner output closeout | OwnerResponseV1 | Bajo | Mantener presentation-only |
| ExcelTriageReportV1 | Interno / soporte | `FileIntakeResult` + `TaskSpecPatch` | anexo estructurado | IMPLEMENTED_PARTIAL | `service_1_excel_triage_report_v1.py` + closeout | File Intake + boundary | Bajo: no confundir con salida principal | Mantener como anexo técnico |
| First Aid ToolResult V1 | Interno | resultado tool + limitaciones | contrato común de output ejecutable | DEFINED | roadmap V1 | TaskSpec assembler | Medio | `FIRST_AID_TOOL_RESULT_V1` |
| precio_margen_basico | Dueño PyME | precio + costo | cálculo simple + faltantes | DOCUMENTED_ONLY | matrix V1 + catálogo full | ToolResult V1 | Medio | tool determinística focal |
| caja_diaria_triage | Dueño PyME | saldo + ingresos + egresos | flujo simple + faltantes | DOCUMENTED_ONLY | matrix V1 + catálogo full | ToolResult V1 | Medio | tool determinística focal |
| stock_alertas_basicas | Dueño PyME | producto + stock actual + mínimo | alerta básica + faltantes | DOCUMENTED_ONLY | matrix V1 + catálogo full | ToolResult V1 | Medio | tool determinística focal |
| XLSX Delivery | Dueño PyME | resultado validado | archivo descargable | DOCUMENTED_ONLY | matrix V1 + roadmap V1 | ToolResult V1 + delivery module | Alto | `FIRST_AID_XLSX_DELIVERY_V1` |
| Service 1 Pipeline | Interno | task + evidencia + tool result | entrega gobernada | DOCUMENTED_ONLY | matrix V1 + roadmap V1 | TaskSpec + FSM + tools | Alto | No abrir antes de tool ejecutable |
| FSM Servicio 1 | Interno | TaskSpec + evidencia + confirmaciones | estado gobernado | DOCUMENTED_ONLY | matrix V1 + roadmap V1 | TaskSpec | Alto | No abrir en este ciclo |
| Exceland Bridge | Interno / producto | specs + templates + tool outputs | puente controlado hacia XLSX | NEEDS_WIRING | catálogo full + matrix V1 | Exceland / SmartExcel | Alto | Bridge controlado posterior |
| Bank Reconciliation Contract | Contador / interno | extracto + planilla + reglas | contrato conciliación | DEFINED | roadmap V1 identifica contrato faltante | conciliación base | Alto | `BANK_RECONCILIATION_CONTRACT_V1` |
| Workpaper XLSX | Contador | conciliaciones + resultados validados | papeles de trabajo | MISSING | matrix V1 | conciliación + XLSX delivery | Alto | Posterior a conciliación base |
| LLM Adapter | Interno | contexto + estado + límites | preguntas/specs/explicaciones | DOCUMENTED_ONLY | matrix V1 + catálogo full | FSM + contratos | Alto | No abrir ahora |
| Chatbot operativo | Dueño PyME | texto + archivos | interacción + entregables | DOCUMENTED_ONLY | matrix V1 + catálogo full | FSM + LLM adapter + pipeline | Alto | No abrir ahora |
| PDF Intake | Dueño PyME / contador | PDF tabular | evidencia tabular usable | MISSING | `file_intake_v1.py` rechaza PDF en V1 | contrato PDF intake | Alto | Contrato y evidencia futura |
| CSV/Excel normalizado | Dueño PyME / contador | CSV/XLSX/PDF caótico | archivo curado/normalizado | IMPLEMENTED_PARTIAL | catálogo full + roadmap V1 describen capacidad parcial | document_ingestion + packaging | Alto | Definir frontera productiva |
| Servicios para contadores | Contador | archivos contables + extractos | entregables operativos | DOCUMENTED_ONLY | catálogo full | conciliaciones + workpapers | Alto | Contrato operativo inicial |
| Mercado Pago / tarjetas | Contador / dueño | MP + banco + ventas | conciliación de cobros/comisiones | MISSING | matrix V1 | conciliación base | Alto | Posterior a contrato base |
| Facturas vs cobros | Contador / dueño | facturas + cobros | cobradas / impagas / parciales | MISSING | matrix V1 | modelo factura-cobro | Alto | Posterior a conciliación base |
| IVA / IIBB | Contador | ventas + compras + alícuotas | cálculo fiscal / alertas | MISSING | matrix V1 | normativa vigente + Servicio 2 | Alto | No abrir en Servicio 1 temprano |
| Asientos automáticos | Contador | operaciones + plan de cuentas | asientos | MISSING | matrix V1 | modelo contable completo | Alto | Muy posterior |

## Correcciones contra V1

### 1. Service 1 TaskSpec ya no está en `MISSING`

Pasa a `IMPLEMENTED_PARTIAL` porque el repo ya contiene:

- `service_1_taskspec_vocabulary_v1.py`;
- `service_1_taskspec_contract_v1.py`;
- `file_intake_taskspec_boundary_v1.py`.

Además, ya hay piezas downstream que dependen de esa frontera:

- `owner_response_renderer_v1.py`;
- `owner_message_formatter_v1.py`;
- `service_1_excel_triage_report_v1.py`.

### 2. Owner output foundation ya quedó cerrada

`OwnerResponseV1 + OwnerMessageFormatterV1` ya quedan reconocidos como foundation owner-facing mínima, asistida y manual.

### 3. ExcelTriageReportV1 queda como anexo

No se promueve a output principal.

Se mantiene como:

```text
anexo estructurado / interno
```

### 4. FSM y boundary experimental siguen congelados

Siguen bajo criterio:

```text
EXPERIMENTAL_FROZEN
```

No se usan para abrir runtime, pipeline ni expansión arquitectónica en este ciclo.

### 5. XLSX Delivery sigue sin implementación

Permanece como `DOCUMENTED_ONLY`.

### 6. Pipeline sigue no implementado

Permanece como `DOCUMENTED_ONLY`.

No hay evidencia de wiring, ejecución gobernada ni delivery productivo.

## Estado actual de producto

```text
Servicio 1 tiene foundation owner-facing.
Servicio 1 no está completo como sistema full.
Falta archivo entregable.
Falta tool ejecutable.
Falta pipeline.
Falta delivery XLSX.
```

Interpretación:

- existe una primera salida honesta y usable para canal manual;
- no existe todavía un producto Servicio 1 full listo para vender como sistema completo;
- no corresponde afirmar diagnóstico, conciliación, automatización productiva ni chatbot operativo.

## Próximo ciclo recomendado

```text
SERVICE_1_TASKSPEC_ASSEMBLER_V1
```

Sólo como siguiente ciclo recomendado.

No queda implementado en este documento.

## Veredicto

```text
SERVICE_1_CAPABILITY_MATRIX_V2_READY
```
