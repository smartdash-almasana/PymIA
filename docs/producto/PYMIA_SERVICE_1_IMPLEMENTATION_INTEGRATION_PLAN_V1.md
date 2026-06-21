# PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1

## Estado

```text
Tipo: PRODUCT_IMPLEMENTATION_PLAN
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Documentar el plan de implementación e integración de PymIA Servicio 1 a partir de la arqueología existente de Exceland, First Aid, Factoría Excel y servicios contables.

Fuentes internas relacionadas:

```text
docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/
```

---

# 1. Tesis técnica

```text
Exceland / SmartExcel = cantera de herramientas.
PymIA-Live = sistema operativo que carga, valida, ejecuta y limita.
```

Regla rectora:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

Servicio 1 debe conservar catálogo completo e implementación incremental.

---

# 2. Alcance de Servicio 1

```text
PymIA Servicio 1
= Laboratorio Operacional de Datos, Excel y Contabilidad
+ Primeros Auxilios
+ Laboratorio Excel
+ Factoría Excel
+ Excel descargables con fórmulas
+ Servicios para contadores
+ Conciliaciones
+ PDF/CSV/Excel a Excel normalizado
+ Chatbot operativo con IA bajo arnés
```

Estados de madurez por capacidad:

```text
DEFINED
DESIGNED
IMPLEMENTED_PARTIAL
IMPLEMENTED_VALIDATED
NEEDS_WIRING
SELLABLE
```

---

# 3. Orden recomendado de implementación

```text
1. SERVICE_1_FULL_CATALOG_V1
2. FIRST_AID_TOOLBOX_PACK_SEED_V1
3. FIRST_AID_TOOLBOX_PACK_LOADER_V1
4. FIRST_AID_TOOL_ACTIVATION_V1
5. precio_margen_basico
6. caja_diaria_triage
7. stock_alertas_basicas
8. XLSX_DELIVERY_V1
9. SERVICE_1_PIPELINE_WIRING_V1
10. BANK_RECONCILIATION_V1
11. MERCADO_PAGO_RECONCILIATION_V1
12. WORKPAPERS_V1
13. SERVICE_1_FSM_V1
14. LLM_ADAPTER_V1
```

---

# 4. Ciclo 1 — SERVICE_1_FULL_CATALOG_V1

Crear o consolidar:

```text
PYMIA_SERVICE_1_FULL_CATALOG_V1.md
```

Debe unir:

```text
First Aid
Laboratorio Excel
Factoría Excel
Excel descargable con fórmulas
Servicios contables
Conciliación bancaria
PDF/CSV/Excel a Excel normalizado
Chatbot con arnés
```

Salida esperada:

```text
Servicio 1 queda definido como catálogo completo.
Nada queda afuera.
Cada capacidad queda con estado.
```

---

# 5. Ciclo 2 — FIRST_AID_TOOLBOX_PACK_SEED_V1

Crear:

```text
PymIA-Live/pymia/contracts/first_aid_toolbox_pack_seed_v1.json
PymIA-Live/pymia/contracts/first_aid_toolbox_pack_v1.py
PymIA-Live/tests/contracts/test_first_aid_toolbox_pack_v1.py
```

Contenido inicial:

```text
FormulaRefs
ValidationRefs
ToolRefs
TemplateRefs
EvidenceRequirements
ClaimsLimitations
EscalationRules
OwnerFacingLimitations
```

Objetivo:

```text
El pack existe como contrato validado.
No toca runtime.
No calcula.
No diagnostica.
```

---

# 6. Ciclo 3 — FIRST_AID_TOOLBOX_PACK_LOADER_V1

Crear:

```text
PymIA-Live/pymia/smartpyme/first_aid_toolbox_pack_loader.py
PymIA-Live/tests/smartpyme/test_first_aid_toolbox_pack_loader.py
```

Responsabilidad:

```text
cargar pack
validar estructura
rechazar si falta campo obligatorio
exponer tools, formulas y validations permitidas
```

Regla:

```text
El loader no calcula.
El loader no diagnostica.
El loader sólo carga y valida.
```

---

# 7. Ciclo 4 — FIRST_AID_TOOL_ACTIVATION_V1

Crear:

```text
PymIA-Live/pymia/smartpyme/first_aid_tool_activation.py
PymIA-Live/tests/smartpyme/test_first_aid_tool_activation.py
```

Entrada:

```text
owner_problem
service_depth
available_evidence
column_confirmation_status
pack
```

Salida:

```text
eligible_tools
unavailable_tools
missing_inputs
owner_questions
limitations
```

Una herramienta se activa sólo si:

```text
pertenece a FIRST_AID
tiene evidencia mínima
respeta límites declarados
no requiere fórmula restringida
no hay columnas computacionales sin confirmar
```

---

# 8. Ciclos 5 a 7 — primeras herramientas First Aid

Herramientas iniciales:

```text
precio_margen_basico
caja_diaria_triage
stock_alertas_basicas
gastos_triage
proveedores_precio_variacion_triage
```

## precio_margen_basico

Entrada mínima:

```text
precio_venta
costo_unitario
```

Salida:

```text
margen_bruto
margen_bruto_pesos
markup
limitaciones
```

## caja_diaria_triage

Entrada mínima:

```text
saldo_inicial
ingresos
egresos
```

Salida:

```text
flujo_neto
saldo_final_estimado
faltantes
limitaciones
```

## stock_alertas_basicas

Entrada mínima:

```text
producto
stock_actual
stock_minimo
```

Salida:

```text
alerta_stock_minimo
dias_stock_restante si hay ventas_diarias_promedio
limitaciones
```

---

# 9. Ciclo 8 — XLSX_DELIVERY_V1

Crear:

```text
PymIA-Live/pymia/smartpyme/first_aid_xlsx_delivery.py
PymIA-Live/tests/smartpyme/test_first_aid_xlsx_delivery.py
```

Responsabilidad:

```text
generar Excel descargable desde output validado
```

Hojas mínimas:

```text
Resumen
Datos usados
Resultados
Faltantes
Limitaciones
```

Regla:

```text
Tool output validado -> XLSX determinístico
```

---

# 10. Ciclo 9 — SERVICE_1_PIPELINE_WIRING_V1

Recomendación:

```text
Crear PymIA-Live/pymia/application/service_1_pipeline.py
```

Motivo:

```text
Evitar seguir cargando vertical_pipeline.py.
Crear frontera clara para Servicio 1.
```

Flujo:

```text
structured_evidence
-> column_confirmation_matrix
-> toolbox_pack_loader
-> tool_activation
-> selected_tool_result
-> owner_report
-> xlsx_delivery opcional
```

Reglas:

```text
si hay columnas dudosas, no calcular.
si falta evidencia, pedir.
si hay output, declarar límites.
```

---

# 11. Ciclos contables posteriores

Después de pack, loader, activación, herramientas First Aid, XLSX delivery y pipeline wiring.

## BANK_RECONCILIATION_V1

Entrada:

```text
extracto_banco
archivo_contable
```

Salida:

```text
conciliados
pendientes
diferencias
duplicados
workpaper_xlsx
```

## MERCADO_PAGO_RECONCILIATION_V1

Entrada:

```text
reporte_mp
extracto_banco
ventas
```

Salida:

```text
ventas
comisiones
retenciones
acreditaciones
diferencias
```

## WORKPAPERS_V1

Salida estándar:

```text
Resumen
Conciliados
Pendientes
Diferencias
Duplicados
Observaciones
```

---

# 12. Chatbot con arnés

No implementar antes del núcleo operativo.

## SERVICE_1_FSM_V1

Estados:

```text
LISTENING
TASK_CLASSIFIED
EVIDENCE_REQUESTED
EVIDENCE_RECEIVED
CONFIRMATION_REQUIRED
PROCESSING
DELIVERY_READY
CLOSED
BLOCKED
```

## LLM_ADAPTER_V1

La IA sólo puede producir:

```text
TaskSpec
EvidenceRequest
OwnerQuestion
ExcelSpec
ExplanationDraft
```

La IA no debe producir por sí sola:

```text
cálculo final
conciliación definitiva
XLSX opaco
claims no validados
```

---

# 13. Restricciones de integración

```text
No migrar Exceland entero.
No meter YAML directo al kernel.
No abrir multiagentes todavía.
No abrir WhatsApp/Telegram todavía.
No prometer automatización contable completa antes de runtime validado.
No mezclar Servicio 1 con diagnóstico Servicio 2.
No convertir fórmulas FIRST_AID en hallazgos económicos fuertes.
```

---

# 14. Primer frente concreto

```text
FIRST_AID_TOOLBOX_PACK_SEED_V1
```

Objetivo:

```text
Convertir el contrato documental existente en un pack JSON/YAML validable por tests.
```

Archivos probables:

```text
PymIA-Live/pymia/contracts/first_aid_toolbox_pack_v1.py
PymIA-Live/pymia/contracts/first_aid_toolbox_pack_seed_v1.json
PymIA-Live/tests/contracts/test_first_aid_toolbox_pack_v1.py
```

Salida esperada:

```text
Pack cargable.
Pack validado.
Sin runtime.
Sin loader.
Sin activación.
Sin contaminación del kernel.
```

---

# 15. Veredicto

```text
SERVICE_1_IMPLEMENTATION_PLAN = READY_FOR_REVIEW
```

Pero:

```text
NO_CODE_AUTHORIZED
NO_TESTS_AUTHORIZED
NO_COMMIT_AUTHORIZED
NO_RUNTIME_WIRING_AUTHORIZED
```
