# PYMIA_SERVICE_1_FULL_CATALOG_V1

## Estado

```text
Tipo: PRODUCT_CATALOG
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Este documento consolida el catálogo completo de PymIA Servicio 1 para evitar que la visión se achique, se fragmente o se pierda en ciclos de implementación parciales.

Servicio 1 no es un MVP mutilado. Es una línea completa de producto que debe implementarse incrementalmente, respetando el catálogo completo y sin dejar capacidades fuera por conveniencia de corto plazo.

Este documento es la fuente maestra de qué es Servicio 1, qué existe, qué falta y qué estado tiene cada pieza.

Fuentes internas relacionadas:

```text
docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md
docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
docs/producto/PYMIA_SERVICE_1_EXTERNAL_AUDIT_PROMPTS_V1.md
docs/producto/EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md
docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md
docs/pymia/PRIMEROS_AUXILIOS_GPT_V1_CHECKPOINT.md
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/
PymIA-Live/pymia/contracts/first_aid_toolbox_v1.json
PymIA-Live/pymia/contracts/first_aid_toolbox_v1.py
PymIA-Live/pymia/smartpyme/first_aid_entrypoint.py
PymIA-Live/pymia/smartpyme/first_aid_toolbox_selector.py
PymIA-Live/pymia/smartpyme/first_aid_owner_output.py
PymIA-Live/pymia/smartpyme/first_aid_toolbox_owner_output.py
PymIA-Live/pymia/smartpyme/service_depth.py
PymIA-Live/pymia/smartpyme/evidence_value_normalizer.py
PymIA-Live/pymia/contracts/evidence_availability_v1.py
PymIA-Live/pymia/contracts/evidence_warning_v1.py
PymIA-Live/tools/document_ingestion.py
```

---

## Tesis

```text
PymIA Servicio 1 no es una feature.
PymIA Servicio 1 es una línea de producto operacional basada en archivos útiles.
```

Regla rectora:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

División de responsabilidades:

```text
Exceland / SmartExcel = cantera de herramientas.
PymIA-Live = sistema operativo que carga, valida, ejecuta y limita.
```

El catálogo completo incluye:

```text
Primeros Auxilios
Laboratorio Excel
Factoría Excel
Excel descargables con fórmulas
Servicios para contadores
Conciliaciones
PDF/CSV/Excel a Excel normalizado
Chatbot operativo con IA bajo arnés
```

Nada queda afuera. Cada capacidad queda con estado.

---

## Definición de Servicio 1

PymIA Servicio 1 se define como:

```text
Laboratorio Operacional de Datos, Excel y Contabilidad

+ Primeros Auxilios
+ Laboratorio Excel
+ Factoría Excel
+ Excel descargables con fórmulas
+ Servicios para contadores
+ Conciliaciones
+ PDF/CSV/Excel a Excel normalizado
+ Chatbot operativo con IA bajo arnés
```

---

## Límites con Servicio 2 y Servicio 3

### Servicio 1 — Laboratorio Operacional

Servicio 1 se encarga de:

```text
ordenar
limpiar
convertir
validar
conciliar
estructurar
generar archivos
producir entregables operativos
```

Servicio 1 no diagnostica la empresa como sistema. Servicio 1 produce archivos útiles a partir de evidencia imperfecta.

### Servicio 2 — Diagnóstico Determinístico

Servicio 2 se encarga de:

```text
diagnóstico determinístico económico/financiero
interpretación sobre evidencia suficiente
fórmulas de mayor profundidad
cruce de fuentes
hipótesis respaldadas
```

Servicio 2 requiere suficiencia de evidencia y cruce de fuentes. No se activa desde una sola fuente sin confirmación.

### Servicio 3 — Laboratorio Organizacional

Servicio 3 se encarga de:

```text
laboratorio organizacional
estabilización operativa
patologías sistémicas
intervención longitudinal
seguimiento continuo
```

Servicio 3 requiere ficha completa, continuidad temporal y múltiples evidencias.

### Regla de frontera

```text
Servicio 1 no debe mezclarse con diagnóstico Servicio 2.
Servicio 1 no debe convertirse en laboratorio organizacional Servicio 3.
Servicio 1 produce entregables; Servicio 2 produce interpretaciones; Servicio 3 produce intervenciones.
```

---

## Estados de madurez

Cada capacidad del catálogo se clasifica en uno de estos estados:

```text
DEFINED                    = concepto definido, sin diseño técnico
DESIGNED                   = diseño técnico documentado, sin código
DOCUMENTED_ONLY            = documentado extensamente, sin código implementado
IMPLEMENTED_PARTIAL        = código existe pero incompleto o no integrado
IMPLEMENTED_VALIDATED      = código implementado y validado con tests
NEEDS_WIRING               = código existe pero no está conectado al pipeline
SELLABLE                   = vendible como producto operativo
MISSING                    = no existe ni como documento ni como código
```

---

## Catálogo completo por familias

### 1. Primeros Auxilios / First Aid

**Propósito:** Intervenir sobre una sola fuente con valor inmediato, ficha mínima y señal proporcional.

**Cliente objetivo:** Dueño PyME con un archivo o problema puntual que necesita ordenar ahora.

**Inputs esperados:** Archivo Excel/CSV/PDF o mensaje textual corto. Ficha mínima 10-20%.

**Outputs esperados:** Archivo curado, tabla limpia, alerta puntual, hallazgo provocador, declaración de faltantes.

**Artefacto entregable:** Excel curado con hoja Hallazgos_PymIA + pregunta provocadora.

**Estado actual:** IMPLEMENTED_VALIDATED

**Evidencia documental:**
- `docs/pymia/PRIMEROS_AUXILIOS_GPT_V1_CHECKPOINT.md` — cierre operativo 2026-06-20
- `docs/producto/EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md` — concepto de producto
- `docs/producto/FIRST_AID_OWNER_EXPERIENCE_V1.md` — experiencia owner-facing
- `docs/producto/FIRST_AID_PYME_PAIN_AUDIT_V1.md` — auditoría de 8 dolores
- `docs/producto/FIRST_AID_GPT_V1_PILOT_OFFER.md` — oferta piloto
- `docs/producto/FIRST_AID_GPT_V1_ASSISTED_PILOT_001..004.md` — 4 pilotos sintéticos
- `docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md` — contrato del pack

**Evidencia de código:**
- `PymIA-Live/pymia/smartpyme/first_aid_entrypoint.py` — evalúa si un intake entra a FIRST_AID
- `PymIA-Live/pymia/smartpyme/first_aid_toolbox_selector.py` — selecciona componentes post-gating
- `PymIA-Live/pymia/smartpyme/first_aid_owner_output.py` — traduce verdict a lenguaje owner
- `PymIA-Live/pymia/smartpyme/first_aid_toolbox_owner_output.py` — salida owner del toolbox
- `PymIA-Live/pymia/smartpyme/service_depth.py` — clasifica FIRST_AID / DIAGNOSTIC / ORGANIZATIONAL

**Riesgo:** Inflar FIRST_AID hasta convertirlo en diagnóstico total sin suficiencia de evidencia.

**Next action:** Activar primera herramienta concreta (precio_margen_basico) como cierre del Ciclo 5 del plan de implementación.

---

### 2. Laboratorio Excel (Excel Treatment Lab)

**Propósito:** Cámara de descompresión entre el caos administrativo del dueño y la estructura computable de PymIA.

**Cliente objetivo:** Dueño PyME con un Excel desordenado que necesita "sacar algo en limpio".

**Inputs esperados:** Archivo Excel caótico, PDF tabular, CSV con headers ambiguos.

**Outputs esperados:** Excel curado, tabla limpia, hoja Hallazgos_PymIA, mini-dashboard, pregunta provocadora.

**Artefacto entregable:** `archivo_curado_pymIA.xlsx` con hojas normalizadas + Hallazgos_PymIA + Limitaciones.

**Estado actual:** IMPLEMENTED_PARTIAL

**Evidencia documental:**
- `docs/producto/EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md` — 9 fases funcionales completas
- `docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md` — sección 10.1

**Evidencia de código:**
- `PymIA-Live/tools/document_ingestion.py` — pipeline completo: ingest, semantic mapping, curation, StructuredEvidence export
- `PymIA-Live/tools/bem_schema_builder/excel_profile_builder.py` — profiling de Excel
- `PymIA-Live/tools/bem_schema_builder/owner_questions_builder.py` — preguntas al dueño

**Riesgo:** Convertirse en Excel Reader genérico o macro disfrazada sin continuidad hacia OCF.

**Next action:** Consolidar `document_ingestion.py` como producto vendible propio, no sólo como herramienta interna.

---

### 3. Factoría Excel (Exceland)

**Propósito:** Cantera de herramientas enchufables para PymIA. Genera XLSX determinísticos bajo contrato.

**Cliente objetivo:** PymIA-Live (consumo interno) y contadores/PyMEs (producto final).

**Inputs esperados:** Specs YAML, catálogo de fórmulas, catálogo de productos, templates.

**Outputs esperados:** Archivos XLSX generados determinísticamente con fórmulas, validaciones y layouts.

**Artefacto entregable:** 14 productos XLSX en `warehouse/templates/`.

**Estado actual:** IMPLEMENTED_PARTIAL

**Evidencia documental:**
- `exeland2/catalog/formulas.yaml` — 15 fórmulas canónicas
- `exeland2/catalog/validations.yaml` — 6 validaciones base
- `exeland2/catalog/product_registry.yaml` — 12 productos registrados
- `exeland2/specs/*.yaml` — 14 specs YAML
- `exeland2/warehouse/templates/*.xlsx` — 14 XLSX generados

**Evidencia de código:**
- `exeland2/src/exceland_factory/` — factory completa: workbook_builders, postprocess, spec_compiler, nl_parser, matcher, style_system, formulas, layouts

**Riesgo:** Duplicación entre `exeland/` y `exeland2/`. Factoría funcionando como producto paralelo sin conexión a PymIA-Live.

**Next action:** Definir cuál es la cantera oficial (`exeland2/`) y crear puente de integración controlada (Ciclo 9 del plan).

---

### 4. Conversión y normalización de archivos

**Propósito:** Convertir PDF/CSV/Excel caóticos en Excel normalizado computable.

**Cliente objetivo:** Dueño PyME o contador con archivos desordenados.

**Inputs esperados:** PDF tabular, CSV con headers ambiguos, Excel con celdas combinadas y formatos inconsistentes.

**Outputs esperados:** Excel normalizado con columnas semánticas, datos tipados, validaciones y declaraciones de ambigüedad.

**Artefacto entregable:** Archivo XLSX normalizado + reporte de curation.

**Estado actual:** IMPLEMENTED_PARTIAL

**Evidencia documental:**
- `docs/producto/EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md` — fases de desinfección y normalización
- `PymIA-Live/docs/pymia/first_aid_toolbox_candidates/EVIDENCE_VALUE_NORMALIZER_V1_CHECKPOINT.md`

**Evidencia de código:**
- `PymIA-Live/tools/document_ingestion.py` — XlsxCurationPipeline completo
- `PymIA-Live/pymia/smartpyme/evidence_value_normalizer.py` — normalizador de valores (16/16 tests PASS)
- `PymIA-Live/pymia/contracts/evidence_warning_v1.py` — contrato de warnings (16/16 tests PASS)

**Riesgo:** PDF → Excel no está evidenciado funcionalmente. La auditoría de SmartPyme lo marca como "no evidenciada".

**Next action:** Definir contrato de ingesta PDF como capacidad MISSING a resolver en ciclo posterior.

---

### 5. Servicios para contadores

**Propósito:** Proveer herramientas operativas para contadores que trabajan con PyMEs.

**Cliente objetivo:** Contadores y estudios contables.

**Inputs esperados:** Archivos de clientes PyME, extractos bancarios, libros contables.

**Outputs esperados:** Papeles de trabajo, conciliaciones, reportes normalizados.

**Artefacto entregable:** XLSX con papeles de trabajo estándar.

**Estado actual:** DEFINED

**Evidencia documental:**
- `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` — sección 11 menciona ciclos contables
- `PymIA-Live/docs/pymia/smartcounter_candidates/` — candidatos de SmartCounter

**Evidencia de código:** Ninguna específica para contadores.

**Riesgo:** Mezclar con diagnóstico Servicio 2 si se intenta hacer interpretación contable sin suficiencia.

**Next action:** Definir como familia propia cuando se cierren los ciclos de conciliación y workpapers.

---

### 6. Conciliación bancaria

**Propósito:** Cruzar extracto bancario con archivo contable para identificar conciliados, pendientes, diferencias y duplicados.

**Cliente objetivo:** Dueño PyME y contador.

**Inputs esperados:** Extracto bancario (XLSX/CSV/PDF) + archivo contable (XLSX/CSV).

**Outputs esperados:** Conciliados, pendientes, diferencias, duplicados, workpaper XLSX.

**Artefacto entregable:** `conciliacion_bancaria_{tenant_id}.xlsx` con hojas Resumen, Conciliados, Pendientes, Diferencias, Duplicados, Observaciones.

**Estado actual:** IMPLEMENTED_PARTIAL

**Evidencia documental:**
- `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` — Ciclo 10 BANK_RECONCILIATION_V1
- `smartbridge/SmartPyme/factory/topology_catalog.json` — "Conciliacion deterministica"
- `smartbridge/SmartPyme/factory/reports/kernel_total_audit_001.md` — entity resolution pendiente

**Evidencia de código:**
- `exeland2/warehouse/templates/conciliador_bancario_macro.xlsx` — template existe
- SmartPyme tiene reconciliación CSV genérica en kernel pero no expuesta por MCP

**Riesgo:** Entity resolution falta y bloquea reconciliación confiable. Sin resolver esto, cualquier conciliación va a ser frágil.

**Next action:** Ciclo 10 del plan. Definir contrato BANK_RECONCILIATION_V1 con entrada/salida/límites claros.

---

### 7. Mercado Pago / tarjetas

**Propósito:** Conciliar reportes de Mercado Pago y tarjetas con extracto bancario y ventas.

**Cliente objetivo:** Dueño PyME que cobra por Mercado Pago y tarjetas.

**Inputs esperados:** Reporte MP (XLSX/CSV), extracto bancario, archivo de ventas.

**Outputs esperados:** Ventas, comisiones, retenciones, acreditaciones, diferencias.

**Artefacto entregable:** `conciliacion_mp_{tenant_id}.xlsx`.

**Estado actual:** MISSING

**Evidencia documental:** Mencionado en plan de implementación como Ciclo 11 MERCADO_PAGO_RECONCILIATION_V1.

**Evidencia de código:** Ninguna.

**Riesgo:** Complejidad de APIs externas y formatos variables de reportes MP.

**Next action:** Definir contrato MERCADO_PAGO_RECONCILIATION_V1 después de cerrar conciliación bancaria base.

---

### 8. Facturas vs cobros

**Propósito:** Cruzar facturas emitidas con cobros recibidos para detectar diferencias.

**Cliente objetivo:** Contador y dueño PyME.

**Inputs esperados:** Registro de facturas (XLSX/CSV), registro de cobros (XLSX/CSV).

**Outputs esperados:** Facturas cobradas, facturas pendientes, cobros sin factura, diferencias.

**Artefacto entregable:** `facturas_vs_cobros_{tenant_id}.xlsx`.

**Estado actual:** MISSING

**Evidencia documental:** No encontrado documento específico.

**Evidencia de código:** Ninguna.

**Riesgo:** Requiere modelo de dominio de factura y cobro bien definido.

**Next action:** Definir como capacidad MISSING a resolver después de workpapers.

---

### 9. Compras y proveedores

**Propósito:** Detectar variaciones de precios de proveedores y ordenar compras.

**Cliente objetivo:** Dueño PyME.

**Inputs esperados:** Registros de compras (XLSX/CSV) con proveedor, producto, precio, fecha.

**Outputs esperados:** Variaciones de precio por proveedor, alertas de aumento, comparativas.

**Artefacto entregable:** `compras_proveedores_triage_{tenant_id}.xlsx`.

**Estado actual:** DOCUMENTED_ONLY

**Evidencia documental:**
- `docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md` — sección 8.5 (proveedores_precio_variacion_triage)
- `docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md` — sección 9 (tool_refs)
- `exeland2/catalog/product_registry.yaml` — compras_y_proveedores clasificado como FIRST_AID/NIVEL_2

**Evidencia de código:**
- `exeland2/specs/compras_y_proveedores.yaml` — spec existe en cantera
- En contrato JSON: decision = NOT_FOR_PHASE_1_PHASE_2

**Riesgo:** Requiere diagnóstico específico de compras/proveedores. Clasificado como fuera de Fase 1.

**Next action:** Clasificar definitivamente como herramienta First Aid o escalar a Nivel 2.

---

### 10. Papeles de trabajo

**Propósito:** Generar papeles de trabajo estándar para contadores y dueños.

**Cliente objetivo:** Contadores.

**Inputs esperados:** Resultados de conciliaciones, triages, cálculos validados.

**Outputs esperados:** Papeles de trabajo con hojas Resumen, Conciliados, Pendientes, Diferencias, Duplicados, Observaciones.

**Artefacto entregable:** `workpaper_{tipo}_{tenant_id}.xlsx`.

**Estado actual:** MISSING

**Evidencia documental:** Mencionado en plan como Ciclo 12 WORKPAPERS_V1.

**Evidencia de código:** Ninguna específica.

**Riesgo:** Sin workpapers, las conciliaciones no tienen entregable profesional.

**Next action:** Definir estructura estándar de workpapers después de cerrar conciliación bancaria.

---

### 11. IVA / IIBB

**Propósito:** Calcular y validar IVA e Ingresos Brutos a partir de registros de ventas y compras.

**Cliente objetivo:** Contador.

**Inputs esperados:** Registro de ventas, registro de compras, alícuotas.

**Outputs esperados:** Débito fiscal, crédito fiscal, saldo técnico, alerta de diferencias.

**Artefacto entregable:** `iva_iibb_{tenant_id}.xlsx`.

**Estado actual:** MISSING

**Evidencia documental:** No encontrado documento específico.

**Evidencia de código:** Ninguna.

**Riesgo:** Requiere reglas AFIP y jurisdiccionales actualizadas. Fuera de First Aid por complejidad.

**Next action:** Fuera de alcance Servicio 1 en corto plazo. Posible Servicio 2.

---

### 12. Asientos automáticos

**Propósito:** Generar asientos contables automáticos a partir de evidencia validada.

**Cliente objetivo:** Contador.

**Inputs esperados:** Registro de operaciones validadas, plan de cuentas.

**Outputs esperados:** Asientos contables en formato estándar.

**Artefacto entregable:** `asientos_{tenant_id}.xlsx`.

**Estado actual:** MISSING

**Evidencia documental:** No encontrado.

**Evidencia de código:** Ninguna.

**Riesgo:** Requiere modelo contable completo y validación exhaustiva.

**Next action:** Fuera de alcance Servicio 1. Posible Servicio 2/3.

---

### 13. Alertas / vencimientos

**Propósito:** Detectar vencimientos, SLAs incumplidos y acumulación de tareas.

**Cliente objetivo:** Dueño PyME.

**Inputs esperados:** Registro de tareas con fechas, umbrales SLA.

**Outputs esperados:** Alertas de vencimiento, alertas de backlog, severidad.

**Artefacto entregable:** Notificaciones owner-facing + brief semanal.

**Estado actual:** IMPLEMENTED_PARTIAL

**Evidencia documental:**
- `PymIA-Live/docs/pymia/smartd_candidates/` — candidatos SmartD

**Evidencia de código:**
- Contrato JSON `first_aid_toolbox_v1.json` incluye:
  - `sla_breach_thresholds` (USE_IN_PHASE_1)
  - `backlog_risk_thresholds` (USE_IN_PHASE_1)
  - `alert_severity_notification_mapping` (USE_IN_PHASE_1)
  - `immediate_action_short_copy` (USE_IN_PHASE_1)
  - `weekly_brief_structure` (USE_IN_PHASE_1)

**Riesgo:** Sin cableado a pipeline, estos componentes quedan como contratos declarativos sin ejecución.

**Next action:** Cablear al pipeline en Ciclo 8 (XLSX_DELIVERY_V1) y Ciclo 9 (SERVICE_1_PIPELINE_WIRING_V1).

---

### 14. Gestor de tareas

**Propósito:** Registro y seguimiento de tareas operativas del dueño.

**Cliente objetivo:** Dueño PyME.

**Inputs esperados:** Lista de tareas, responsables, fechas.

**Outputs esperados:** Vista de tareas, alertas de vencimiento.

**Artefacto entregable:** XLSX de tareas ordenadas.

**Estado actual:** MISSING

**Evidencia documental:** No encontrado.

**Evidencia de código:** Ninguna.

**Riesgo:** No es núcleo de Servicio 1. Puede ser Servicio 3.

**Next action:** Fuera de alcance Servicio 1 por ahora.

---

### 15. XLSX Delivery

**Propósito:** Generar Excel descargable desde output validado de herramientas First Aid.

**Cliente objetivo:** Dueño PyME.

**Inputs esperados:** Tool output validado (resultado de precio_margen, caja_diaria, stock, etc.).

**Outputs esperados:** XLSX con hojas mínimas: Resumen, Datos usados, Resultados, Faltantes, Limitaciones.

**Artefacto entregable:** `{tool_name}_{tenant_id}_{timestamp}.xlsx`.

**Estado actual:** DOCUMENTED_ONLY

**Evidencia documental:**
- `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` — Ciclo 8 XLSX_DELIVERY_V1

**Evidencia de código:** Ninguna.

**Riesgo:** Sin XLSX delivery, Servicio 1 no tiene entregable tangible para el dueño.

**Next action:** Ciclo 8. Crear `PymIA-Live/pymia/smartpyme/first_aid_xlsx_delivery.py`.

---

### 16. Chatbot operativo

**Propósito:** Interfaz conversacional que gobierna la interacción del dueño con Servicio 1.

**Cliente objetivo:** Dueño PyME.

**Inputs esperados:** Mensajes de texto, archivos adjuntos.

**Outputs esperados:** Preguntas, respuestas, requests de evidencia, entregas de archivos.

**Artefacto entregable:** Conversación + archivos entregables.

**Estado actual:** NEEDS_WIRING

**Evidencia documental:**
- `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` — sección 12

**Evidencia de código:**
- Telegram runtime existe en PymIA (HERMES docs)
- Infra de canal existe pero no cableada a Servicio 1

**Riesgo:** Abrir canales externos (WhatsApp/Telegram) antes de cerrar núcleo operativo.

**Next action:** No abrir canales hasta tener SERVICE_1_FSM_V1 y LLM_ADAPTER_V1.

---

### 17. IA con arnés

**Propósito:** IA limitada a conversación, clasificación, specs y explicación. No calcula, no concilia, no genera XLSX opaco.

**Cliente objetivo:** Sistema interno (PymIA-Live).

**Inputs esperados:** Contexto del caso, evidencia disponible, estado de la FSM.

**Outputs esperados:** TaskSpec, EvidenceRequest, OwnerQuestion, ExcelSpec, ExplanationDraft.

**Artefacto entregable:** Borradores validados por el sistema.

**Estado actual:** DOCUMENTED_ONLY

**Evidencia documental:**
- `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` — sección 12 LLM_ADAPTER_V1
- `docs/producto/PYMIA_SERVICE_1_EXTERNAL_AUDIT_PROMPTS_V1.md` — Prompt 4 (auditoría de arnés)

**Evidencia de código:** Ninguna concreta.

**Riesgo:** Que la IA calcule o concilie indirectamente, rompiendo la frontera determinística.

**Next action:** Ciclo 14. Definir LLM_ADAPTER_V1 con contratos estrictos de qué puede y no puede producir.

---

### 18. Service 1 Pipeline

**Propósito:** Pipeline propio de Servicio 1, separado de vertical_pipeline.py.

**Cliente objetivo:** Sistema interno.

**Inputs esperados:** StructuredEvidence, ColumnConfirmationMatrix, toolbox pack.

**Outputs esperados:** Tool result, owner report, XLSX delivery opcional.

**Artefacto entregable:** Pipeline ejecutable con frontera clara.

**Estado actual:** DOCUMENTED_ONLY

**Evidencia documental:**
- `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` — Ciclo 9 SERVICE_1_PIPELINE_WIRING_V1

**Evidencia de código:** Ninguna. `vertical_pipeline.py` existe pero no tiene frontera de Servicio 1.

**Riesgo:** Seguir cargando `vertical_pipeline.py` sin crear frontera clara.

**Next action:** Ciclo 9. Crear `PymIA-Live/pymia/application/service_1_pipeline.py`.

---

### 19. FSM Servicio 1

**Propósito:** Máquina de estados finitos que gobierna el flujo de Servicio 1.

**Cliente objetivo:** Sistema interno.

**Estados definidos:**

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

**Estado actual:** DOCUMENTED_ONLY

**Evidencia documental:**
- `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` — sección 12

**Evidencia de código:** Ninguna.

**Riesgo:** Sin FSM, el chatbot no tiene gobierno determinístico.

**Next action:** Ciclo 13. Implementar SERVICE_1_FSM_V1.

---

### 20. LLM Adapter Servicio 1

**Propósito:** Adaptador que limita la IA a producir sólo artefactos validables por el sistema.

**Cliente objetivo:** Sistema interno.

**Artefactos que la IA puede producir:**

```text
TaskSpec
EvidenceRequest
OwnerQuestion
ExcelSpec
ExplanationDraft
```

**Artefactos que la IA NO debe producir:**

```text
cálculo final
conciliación definitiva
XLSX opaco
claims no validados
```

**Estado actual:** DOCUMENTED_ONLY

**Evidencia documental:**
- `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` — sección 12
- `docs/producto/PYMIA_SERVICE_1_EXTERNAL_AUDIT_PROMPTS_V1.md` — Prompt 4

**Evidencia de código:** Ninguna.

**Riesgo:** Que la IA produzca claims finales sin validación del sistema.

**Next action:** Ciclo 14. Implementar LLM_ADAPTER_V1.

---

## Matriz principal

| CAPACIDAD | FAMILIA | ESTADO | DOCS | CÓDIGO | OUTPUT | RIESGO | NEXT_ACTION |
|---|---|---|---|---|---|---|---|
| precio_margen_basico | First Aid | DOCUMENTED_ONLY | ARCHAEOLOGY + CONTRACT | No existe como tool ejecutable | margen, markup, limitaciones | Bajo | Ciclo 5 |
| caja_diaria_triage | First Aid | DOCUMENTED_ONLY | ARCHAEOLOGY + CONTRACT | No existe como tool ejecutable | flujo, saldo, faltantes | Bajo | Ciclo 6 |
| stock_alertas_basicas | First Aid | DOCUMENTED_ONLY | ARCHAEOLOGY + CONTRACT | No existe como tool ejecutable | alertas, días stock | Bajo | Ciclo 7 |
| gastos_triage | First Aid | DOCUMENTED_ONLY | CONTRACT | No existe como tool ejecutable | gastos ordenados | Bajo | Ciclo posterior |
| proveedores_precio_variacion_triage | First Aid | DOCUMENTED_ONLY | CONTRACT | Spec en cantera, no en runtime | variaciones, alertas | Medio | Clasificar Fase 1 o Nivel 2 |
| Excel descargable con fórmulas | Factoría Excel | IMPLEMENTED_PARTIAL | formulas.yaml | Factory genera XLSX con fórmulas | XLSX con fórmulas activas | Medio | XLSX_DELIVERY_V1 |
| plantilla caja diaria | Factoría Excel | IMPLEMENTED_PARTIAL | specs/caja_diaria.yaml | XLSX generado en warehouse | XLSX template | Bajo | Integrar a delivery |
| plantilla stock | Factoría Excel | IMPLEMENTED_PARTIAL | specs/stock_control.yaml | XLSX generado en warehouse | XLSX template | Bajo | Integrar a delivery |
| plantilla margen | Factoría Excel | IMPLEMENTED_PARTIAL | specs/precio_margen.yaml | XLSX generado en warehouse | XLSX template | Bajo | Integrar a delivery |
| plantilla costos | Factoría Excel | IMPLEMENTED_PARTIAL | specs/costos_por_producto.yaml | XLSX generado en warehouse | XLSX template | Bajo | Integrar a delivery |
| plantilla punto de equilibrio | Factoría Excel | IMPLEMENTED_PARTIAL | specs/punto_equilibrio.yaml | XLSX generado en warehouse | XLSX template | Bajo | Nivel 2, no Fase 1 |
| PDF → Excel | Conversión | MISSING | Mencionado en audit | No evidenciado | Excel normalizado | Alto | Definir contrato |
| CSV normalizado | Conversión | IMPLEMENTED_PARTIAL | document_ingestion | SemanticFieldMapper | StructuredEvidence | Bajo | Cablear a pipeline |
| Excel normalizado | Conversión | IMPLEMENTED_PARTIAL | document_ingestion | XlsxCurationPipeline completa | CuratedDocument + SE | Bajo | Cablear a pipeline |
| conciliación bancaria | Conciliación | IMPLEMENTED_PARTIAL | Plan Ciclo 10 | Template XLSX + SmartPyme genérico | Workpaper XLSX | Alto | BANK_RECONCILIATION_V1 |
| Mercado Pago / tarjetas | Conciliación MP | MISSING | Plan Ciclo 11 | No existe | Workpaper XLSX | Alto | MERCADO_PAGO_RECONCILIATION_V1 |
| facturas vs cobros | Contabilidad | MISSING | No documentado | No existe | Workpaper XLSX | Alto | Definir contrato |
| compras/proveedores | Compras | DOCUMENTED_ONLY | ARCHAEOLOGY 8.5 | Spec en cantera, NOT_FOR_PHASE_1 | Triage XLSX | Medio | Clasificar |
| papeles de trabajo | Contabilidad | MISSING | Plan Ciclo 12 | No existe | Workpaper XLSX | Alto | WORKPAPERS_V1 |
| IVA/IIBB | Contabilidad | MISSING | No documentado | No existe | XLSX fiscal | Alto | Fuera de Servicio 1 |
| asientos automáticos | Contabilidad | MISSING | No documentado | No existe | XLSX asientos | Alto | Fuera de Servicio 1 |
| vencimientos/alertas | Alertas | IMPLEMENTED_PARTIAL | SmartD candidates | En contrato JSON, no cableado | Notificaciones | Medio | Cablear Ciclo 8-9 |
| gestor de tareas | Tareas | MISSING | No documentado | No existe | XLSX tareas | Bajo | Fuera de Servicio 1 |
| XLSX delivery | Delivery | DOCUMENTED_ONLY | Plan Ciclo 8 | No existe | XLSX descargable | Alto | Crear first_aid_xlsx_delivery |
| service_1_pipeline | Pipeline | DOCUMENTED_ONLY | Plan Ciclo 9 | No existe, vertical_pipeline sin frontera | Pipeline ejecutable | Alto | Crear service_1_pipeline |
| Service 1 FSM | FSM | DOCUMENTED_ONLY | Plan sección 12 | No existe | Máquina de estados | Alto | Crear SERVICE_1_FSM_V1 |
| LLM Adapter | IA | DOCUMENTED_ONLY | Plan sección 12 | No existe | TaskSpec/EvidenceRequest/etc | Alto | Crear LLM_ADAPTER_V1 |

---

## Capacidades ya existentes

### Documentadas

Capacidades con documentación extensa pero sin código:

```text
XLSX Delivery (first_aid_xlsx_delivery)
Service 1 Pipeline (service_1_pipeline.py)
FSM Servicio 1 (SERVICE_1_FSM_V1)
LLM Adapter Servicio 1 (LLM_ADAPTER_V1)
Mercado Pago / tarjetas (MERCADO_PAGO_RECONCILIATION_V1)
Facturas vs cobros
Papeles de trabajo (WORKPAPERS_V1)
IVA/IIBB
Asientos automáticos
Gestor de tareas
```

### Implementadas parcialmente

Capacidades con código parcial:

```text
Laboratorio Excel — document_ingestion.py (pipeline completo pero no empaquetado como producto)
Factoría Excel — exceland2/ (factory completa, 14 XLSX generados, no conectada a PymIA-Live)
Excel normalizado — XlsxCurationPipeline funcional
CSV normalizado — SemanticFieldMapper funcional
Conciliación bancaria — template XLSX existe, SmartPyme tiene reconciliación genérica
Vencimientos/alertas — componentes en contrato JSON, no cableados
Compras/proveedores — spec en cantera, clasificada NOT_FOR_PHASE_1_PHASE_2
```

### Implementadas y validadas

Capacidades con código y tests passing:

```text
First Aid entrypoint — first_aid_toolbox_v1 contract (14/14 PASS)
First Aid selector — first_aid_toolbox_selector.py (9/9 PASS)
First Aid owner output — first_aid_owner_output.py (9/9 PASS)
First Aid toolbox owner output — first_aid_toolbox_owner_output.py
Service depth classifier — service_depth.py
Evidence Availability Contract — evidence_availability_v1.py (15/15 PASS)
Evidence Warning Contract — evidence_warning_v1.py (16/16 PASS)
Evidence Value Normalizer — evidence_value_normalizer.py (16/16 PASS)
```

### Needs wiring

Capacidades que existen pero no están integradas en Servicio 1:

```text
Chatbot operativo — Telegram runtime existe, no cableado a Servicio 1
document_ingestion.py — funciona como tool, no como producto
exeland2/ factory — genera XLSX, no conectada a PymIA-Live
SmartCounter módulos — excel_reader, header detector, mapper, normalizer sueltos
SmartD candidatos — componentes de alertas en contrato, no ejecutables
```

### Missing

Capacidades que todavía no existen:

```text
PDF → Excel (ingesta funcional)
Mercado Pago / tarjetas (conciliación)
Facturas vs cobros
Papeles de trabajo (estructura)
IVA/IIBB
Asientos automáticos
Gestor de tareas
XLSX delivery (first_aid_xlsx_delivery.py)
Service 1 Pipeline (service_1_pipeline.py)
FSM Servicio 1
LLM Adapter Servicio 1
Herramientas First Aid concretas (precio_margen, caja_diaria, stock_alertas, gastos_triage, proveedores_triage)
```

---

## First Aid Toolbox

### Referencia documental

```text
docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
PymIA-Live/pymia/contracts/first_aid_toolbox_v1.json
PymIA-Live/pymia/contracts/first_aid_toolbox_v1.py
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/ (26 archivos)
```

### Estado del contrato

```text
contract_id: FIRST_AID_TOOLBOX_PACK_CONTRACT_V1
schema_version: 1.0
status: CANDIDATE_CONTRACT
components_total: 27
phase_1_components: 22
compositions_total: 5
implementation_authorized: false
```

### FormulaRefs

Fórmulas aptas para Primeros Auxilios (derivadas de `exeland2/catalog/formulas.yaml`):

```text
margen_bruto              — señal de margen bruto, FIRST_AID
margen_bruto_pesos        — diferencia precio-costo, FIRST_AID
precio_venta_con_margen   — cálculo de precio objetivo, FIRST_AID
markup                    — markup sobre costo, FIRST_AID
ingresos_totales          — total simple, FIRST_AID
egresos_totales           — total simple, FIRST_AID
flujo_caja_neto           — ingreso - egreso, FIRST_AID
saldo_acumulado           — continuidad de saldo, FIRST_AID
alerta_stock_minimo       — alerta simple, FIRST_AID
dias_stock_restante       — duración estimada, FIRST_AID
```

Fórmulas restringidas (NO activables en FIRST_AID sin mayor suficiencia):

```text
resultado_neto            — DETERMINISTIC_DIAGNOSIS
punto_equilibrio_unidades — DETERMINISTIC_DIAGNOSIS
punto_equilibrio_pesos    — DETERMINISTIC_DIAGNOSIS
rotacion_inventario       — DETERMINISTIC_DIAGNOSIS
costo_reposicion_promedio — DETERMINISTIC_DIAGNOSIS
```

### ValidationRefs

Validadores candidatos (derivados de `exeland2/catalog/validations.yaml`):

```text
positive_number
non_negative_number
percentage_0_1
percentage_0_100
integer_positive
integer_non_negative
```

### ToolRefs

Herramientas candidatas:

```text
caja_diaria_triage                      — revisión inicial de caja diaria
precio_margen_basico                    — revisión básica de precio y margen
stock_alertas_basicas                   — alertas básicas de stock
gastos_triage                           — orden inicial de gastos
proveedores_precio_variacion_triage     — revisión inicial de compras y proveedores
```

### Composiciones

```text
excel_triage_basic        — ExcelStructureValidationPack + flujo_de_fondos + proyeccion_ventas + disclaimers
cash_ordering_basic       — SimpleCashArqueoChecklist + caja_diaria + flujo_de_fondos + OwnerSignalTemplate
price_margin_basic        — CostPriceReviewHeuristic + precio_margen + rentabilidad_por_producto + simulador_inflacion
operational_alert_basic   — OwnerSignalTemplate + alert_severity + sla_breach + backlog_risk + weekly_brief
stock_minimal_alert       — StockDesvioAlertRule + OwnerSignalTemplate + partial_data_copy
```

### Evidencia Requirements por herramienta

```text
caja_diaria_triage:         mínimo = saldo_inicial, ingresos, egresos
precio_margen_basico:       mínimo = precio_venta, costo_unitario
stock_alertas_basicas:      mínimo = producto, stock_actual, stock_minimo
gastos_triage:              mínimo = concepto, importe
proveedores_precio_variacion_triage: mínimo = proveedor, producto_o_insumo, precio_o_costo
```

### ForbiddenClaims globales

```text
rentabilidad real confirmada
margen neto real sin costos completos
saldo bancario conciliado con una sola fuente
stock físico confirmado sin conteo
fraude o irregularidad intencional
auditoría contable cerrada
precio óptimo definitivo
estrategia comercial completa
punto de equilibrio empresarial total sin evidencia suficiente
diagnóstico integral de la empresa
```

---

## Factoría Excel

### Tesis

```text
La IA no genera XLSX opaco.
La IA puede generar ExcelSpec.
El sistema valida.
El generador determinístico crea el archivo.
```

### Flujo

```text
pedido usuario
→ ExcelSpec (generada por IA o configurada)
→ validador (contrato de estructura)
→ generador XLSX (determinístico, openpyxl/xlsxwriter)
→ archivo descargable
```

### Plantillas candidatas

```text
caja diaria
stock
margen
costos
punto de equilibrio
cuentas corrientes
conciliador simple
proveedores
gastos
ventas
flujo de fondos
```

### Estado actual

14 specs YAML implementadas en `exeland2/specs/`. 15 fórmulas canónicas en `exeland2/catalog/formulas.yaml`. 12 productos registrados en `exeland2/catalog/product_registry.yaml`. 14 XLSX generados en `exeland2/warehouse/templates/`.

### Integración pendiente

```text
Factoría existe como producto independiente.
No hay puente que permita a PymIA-Live invocar la generación de XLSX bajo contrato.
No migrar Exceland entero al kernel.
No meter YAML directo al kernel.
No hardcodear fórmulas en kernel.
```

---

## Servicios contables

### Conciliación bancaria

**Estado:** IMPLEMENTED_PARTIAL

Template XLSX existe en cantera. SmartPyme tiene reconciliación CSV genérica en kernel pero no expuesta por MCP. Entity resolution falta y bloquea reconciliación confiable.

**Plan:** Ciclo 10 BANK_RECONCILIATION_V1.

**Entrada:** extracto_banco + archivo_contable

**Salida:** conciliados, pendientes, diferencias, duplicados, workpaper_xlsx

### Mercado Pago / tarjetas

**Estado:** MISSING

No existe documento ni código específico. Mencionado en plan como Ciclo 11.

**Plan:** MERCADO_PAGO_RECONCILIATION_V1.

**Entrada:** reporte_mp + extracto_banco + ventas

**Salida:** ventas, comisiones, retenciones, acreditaciones, diferencias

### Facturas vs cobros

**Estado:** MISSING

No documentado ni implementado.

### Compras y proveedores

**Estado:** DOCUMENTED_ONLY

Documentado en arqueología de Exceland como herramienta FIRST_AID. Spec existe en cantera. Clasificada como NOT_FOR_PHASE_1_PHASE_2 en contrato JSON.

### Papeles de trabajo

**Estado:** MISSING

Mencionado en plan como Ciclo 12 WORKPAPERS_V1.

**Salida estándar:** Resumen, Conciliados, Pendientes, Diferencias, Duplicados, Observaciones.

### IVA / IIBB

**Estado:** MISSING

Fuera de alcance Servicio 1 en corto plazo. Requiere reglas AFIP y jurisdiccionales.

### Asientos automáticos

**Estado:** MISSING

Fuera de alcance Servicio 1. Requiere modelo contable completo.

### Vencimientos / alertas

**Estado:** IMPLEMENTED_PARTIAL

Componentes existen en contrato JSON (sla_breach_thresholds, backlog_risk_thresholds, alert_severity_notification_mapping, weekly_brief_structure). No cableados al pipeline.

### Gestor de tareas

**Estado:** MISSING

Fuera de alcance Servicio 1. Posible Servicio 3.

---

## Integración recomendada

Orden de integración (basado en `PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md`):

```text
1.  SERVICE_1_FULL_CATALOG_V1 (este documento)
2.  Auditoría específica de first_aid_toolbox_v1.py/json
3.  FIRST_AID_TOOLBOX_PACK_SEED_V1 (semilla JSON/YAML validable)
4.  FIRST_AID_TOOLBOX_PACK_LOADER_V1 (loader que carga y valida)
5.  FIRST_AID_TOOL_ACTIVATION_V1 (activación controlada)
6.  precio_margen_basico (primera herramienta concreta)
7.  caja_diaria_triage (segunda herramienta)
8.  stock_alertas_basicas (tercera herramienta)
9.  gastos_triage (cuarta herramienta)
10. proveedores_precio_variacion_triage (quinta herramienta)
11. XLSX_DELIVERY_V1 (first_aid_xlsx_delivery.py)
12. SERVICE_1_PIPELINE_WIRING_V1 (service_1_pipeline.py)
13. Integración controlada con Exceland (puente cantera → PymIA-Live)
14. BANK_RECONCILIATION_V1 (conciliación bancaria)
15. MERCADO_PAGO_RECONCILIATION_V1 (conciliación MP)
16. WORKPAPERS_V1 (papeles de trabajo)
17. SERVICE_1_FSM_V1 (máquina de estados)
18. LLM_ADAPTER_V1 (adaptador IA con arnés)
```

---

## Restricciones

```text
No migrar Exceland entero.
No meter YAML directo al kernel.
No hardcodear fórmulas en kernel.
No abrir multiagentes todavía.
No abrir WhatsApp/Telegram todavía.
No prometer automatización contable completa antes de runtime validado.
No mezclar Servicio 1 con diagnóstico Servicio 2.
No convertir fórmulas FIRST_AID en hallazgos económicos fuertes.
No usar IA para cálculos críticos.
No usar IA para conciliación definitiva.
No usar IA para XLSX opaco.
No autorizar runtime sin contrato previo.
No autorizar wiring sin tests previos.
No achicar el catálogo por conveniencia de corto plazo.
```

---

## Próximo paso recomendado

```text
Auditar first_aid_toolbox_v1.py/json contra FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md
antes de crear nuevos contratos o autorizar implementación.
```

Verificar que:

- Los 27 componentes del JSON coinciden con los tool_refs, formula_refs y validation_refs del contrato documental.
- Las 5 composiciones del JSON están cerradas sobre Fase 1.
- Las decisiones (USE_IN_PHASE_1, USE_IN_PHASE_1_WITH_GUARDRAILS, NOT_FOR_PHASE_1_PHASE_2) son consistentes con la clasificación de la arqueología.
- El SmartExcel addendum queda explícitamente separado del master.
- No hay componentes phantom (en código pero no en documento, o viceversa).

Esta auditoría no toca código. No corre tests. No autoriza implementación. Sólo valida que el contrato de código y el contrato documental dicen lo mismo.
