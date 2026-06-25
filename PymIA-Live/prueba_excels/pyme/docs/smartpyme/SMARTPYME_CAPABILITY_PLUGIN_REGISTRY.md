# SmartPyme — Capability Plugin Registry

Fecha: 2026-06-01  
Estado: registry documental inicial  
Alcance: fichas, plugins y caminos de ejecución SmartPyme observados en `main` remoto.

---

## 1. Propósito

Este documento fija una fuente de verdad inicial para responder:

```text
qué ficha existe,
qué plugin la implementa,
por qué camino se ejecuta,
qué está disponible,
qué está incompleto,
y qué no debe prometerse.
```

Nota M20:
`pymia/smartpyme/capabilities.yaml` es la fuente machine-readable inicial.
Este Markdown sigue como explicación humana y M20 no conecta `supplier_duplicate_check` al dispatcher formal.

Regla madre:

```text
Una ficha no está disponible en abstracto.
Está disponible por camino de ejecución.
```

---

## 2. Estados

```text
CONCEPTUAL
PLUG_READY
IMPLEMENTED
AVAILABLE_BY_CLI
AVAILABLE_BY_DISPATCHER
PARTIALLY_AVAILABLE_BY_PATH
AVAILABLE
pipeline_certified
UNSUPPORTED_IN_PATH
MISSING_IN_REMOTE
NEEDS_PATH_CONFIRMATION
```

---

## 3. Caminos de ejecución

### 3.1 Camino formal

```text
interrogation
→ tank_selection
→ intake
→ evidence_requirement
→ evidence
→ evidence_gate
→ readiness
→ runtime_bridge
→ microservice_dispatcher
→ delivery_package
```

### 3.2 Camino CLI local

```text
e2e_cli
→ classification
→ plugin diagnóstico
→ markdown report
→ diagnostic_result.json
→ reception_record.json
→ storage
```

---

## 4. Registry inicial

| capability_id | Ficha | Classification | Plugin / módulo | Camino formal | Camino CLI | Estado real |
|---|---|---|---|---:|---:|---|
| `excel_diagnostic` | Diagnóstico Excel | `excel_diagnostic` | `pymia.smartpyme.excel_diagnostic.diagnose_excel` | Sí | Sí | `pipeline_certified` |
| `supplier_duplicate_check` | Proveedores duplicados | `supplier_duplicate_check` | `pymia.smartpyme.classifications.supplier_duplicate_check.diagnose_supplier_duplicates` | No en dispatcher | Sí | `PARTIALLY_AVAILABLE_BY_PATH` |
| `evidence_record` | Registro de evidencia | N/A | `pymia.smartpyme.evidence` | Sí como contrato | Indirecto | `IMPLEMENTED` |
| `evidence_gate` | Suficiencia de evidencia | N/A | `pymia.smartpyme.evidence_gate.evaluate_evidence_sufficiency` | Sí | No directo | `IMPLEMENTED` |
| `readiness_gate` | Readiness de análisis | N/A | `pymia.smartpyme.readiness` | Sí | No directo | `IMPLEMENTED` |
| `runtime_bridge` | Candidato de ejecución | N/A | `pymia.smartpyme.runtime_bridge` | Sí | No directo | `IMPLEMENTED` |
| `microservice_dispatcher` | Dispatcher formal | N/A | `pymia.smartpyme.microservice_dispatcher` | Sí | No | `IMPLEMENTED_LIMITED` |
| `delivery_package` | Paquete entregable metadata | N/A | `pymia.smartpyme.delivery_package` | Sí post-gate | No claro | `IMPLEMENTED` |
| `anamnesis_fsm` | Ficha/anamnesis conversacional | N/A | `pymia.smartpyme.anamnesis_fsm` | Pre-intake | No | `IMPLEMENTED` |
| `anamnesis_fsm_integration` | Wrapper progressive_context | N/A | `pymia.smartpyme.anamnesis_fsm_integration` | Pre-intake | No | `IMPLEMENTED` |
| `report_html` | Reporte HTML | N/A | `pymia.smartpyme.report_html` | No localizado | No localizado | `MISSING_IN_REMOTE` |
| `document_parser_front` | Parser documental PDF/DOCX/PPTX | N/A | `pymia.smartpyme.document_parser_front` | No localizado | No localizado | `MISSING_IN_REMOTE` |
| `telegram_adapter_smartpyme` | Adapter Telegram SmartPyme | N/A | `pymia.smartpyme.telegram_adapter` | No localizado | No localizado | `NEEDS_PATH_CONFIRMATION` |

---

## 5. Fichas ejecutables

### 5.1 `excel_diagnostic`

```yaml
capability_id: excel_diagnostic
human_name: Diagnóstico Excel
classification: excel_diagnostic
domain:
  - comercial
  - financiero
  - stock
  - compras
plugin_module: pymia.smartpyme.excel_diagnostic
plugin_function: diagnose_excel
input_evidence:
  - excel_file
  - excel_ventas_costos
  - excel_caja_banco
  - excel_stock
outputs:
  - findings
  - markdown_report
readiness_allowed: true
runtime_mapped: true
dispatcher_available: true
cli_available: true
commercially_available: true
status: pipeline_certified
certification:
  milestone: M18.4
  evidence_commit: 3501505
  test: tests/smartpyme/test_deterministic_pipeline_e2e.py
  result: 6/6 passed
  certified_scope: excel_diagnostic deterministic canonical pipeline end-to-end
  contract_reference: SMARTPYME_DETERMINISTIC_PIPELINE_CONTRACT.md §11 / M18.4
limits:
  - Diagnóstico inicial sobre evidencia tabular.
  - No equivale a diagnóstico total de empresa.
  - No reemplaza conciliación bancaria específica ni análisis profundo de stock.
```

---

### 5.2 `supplier_duplicate_check`

```yaml
capability_id: supplier_duplicate_check
human_name: Revisión de proveedores duplicados
classification: supplier_duplicate_check
domain:
  - proveedores
  - datos_maestros
plugin_module: pymia.smartpyme.classifications.supplier_duplicate_check
plugin_function: diagnose_supplier_duplicates
input_evidence:
  - excel_proveedores
required_fields:
  - proveedor
  - cuit
  - razon_social
outputs:
  - findings
  - markdown_report
readiness_allowed: true
runtime_mapped: true
dispatcher_available: false
cli_available: true
commercially_available: false
status: PARTIALLY_AVAILABLE_BY_PATH
limits:
  - Funciona por camino CLI.
  - No está conectado al dispatcher formal.
  - No debe prometerse como disponible por todos los canales.
missing_to_available:
  - Conectar al microservice_dispatcher.
  - Agregar smoke dispatcher específico.
  - Alinear worker nominal del runtime_bridge con módulo real.
  - Documentar límites operativos.
```

---

## 6. Módulos contractuales

### 6.1 `evidence_record`

```yaml
capability_id: evidence_record
human_name: Registro de evidencia
module: pymia.smartpyme.evidence
status: IMPLEMENTED
role: metadata_contract
executes_plugin: false
limits:
  - Registra evidencia.
  - No lee archivos.
  - No valida contenido.
  - No decide suficiencia.
```

### 6.2 `evidence_gate`

```yaml
capability_id: evidence_gate
human_name: Gate de suficiencia de evidencia
module: pymia.smartpyme.evidence_gate
status: IMPLEMENTED
role: sufficiency_gate
executes_plugin: false
limits:
  - Compara pedidos contra evidencia registrada.
  - Trabaja por metadata.
  - READY no significa diagnóstico válido.
```

### 6.3 `readiness_gate`

```yaml
capability_id: readiness_gate
human_name: Gate ready-for-analysis
module: pymia.smartpyme.readiness
status: IMPLEMENTED
role: analysis_readiness_gate
executes_plugin: false
limits:
  - Decide preparación analítica.
  - No garantiza disponibilidad del plugin.
```

### 6.4 `runtime_bridge`

```yaml
capability_id: runtime_bridge
human_name: Puente a candidato de ejecución
module: pymia.smartpyme.runtime_bridge
status: IMPLEMENTED
role: execution_candidate_builder
executes_plugin: false
limits:
  - Prepara candidato.
  - No ejecuta.
  - Worker nominal no equivale a worker conectado.
```

### 6.5 `microservice_dispatcher`

```yaml
capability_id: microservice_dispatcher
human_name: Dispatcher formal
module: pymia.smartpyme.microservice_dispatcher
status: IMPLEMENTED_LIMITED
role: dispatcher
supported_classifications:
  - excel_diagnostic
unsupported_currently:
  - supplier_duplicate_check
limits:
  - Fuente real de disponibilidad formal.
  - Hoy sólo ejecuta Excel diagnostic.
```

---

## 7. Módulos conversacionales

### 7.1 `anamnesis_fsm`

```yaml
capability_id: anamnesis_fsm
human_name: FSM de anamnesis inicial
module: pymia.smartpyme.anamnesis_fsm
status: IMPLEMENTED
role: conversational_profile_builder
executes_plugin: false
limits:
  - Arma ficha.
  - Formula hipótesis.
  - Pide evidencia.
  - No diagnostica.
  - No ejecuta microservicios.
```

### 7.2 `anamnesis_fsm_integration`

```yaml
capability_id: anamnesis_fsm_integration
human_name: Integración FSM con progressive_context
module: pymia.smartpyme.anamnesis_fsm_integration
status: IMPLEMENTED
role: integration_wrapper
executes_plugin: false
limits:
  - Conecta conversación con intake projection.
  - post_ficha_routing no equivale a dispatch.
```

---

## 8. No localizados / no prometer

### 8.1 `report_html`

```yaml
capability_id: report_html
human_name: Reporte HTML
expected_module: pymia.smartpyme.report_html
status: MISSING_IN_REMOTE
commercially_available: false
note: No localizado en main remoto observado.
```

### 8.2 `document_parser_front`

```yaml
capability_id: document_parser_front
human_name: Parser documental PDF/DOCX/PPTX
expected_module: pymia.smartpyme.document_parser_front
status: MISSING_IN_REMOTE
commercially_available: false
note: PDF no debe marcarse como validado operacionalmente.
```

### 8.3 `telegram_adapter_smartpyme`

```yaml
capability_id: telegram_adapter_smartpyme
human_name: Adapter Telegram SmartPyme
expected_module: pymia.smartpyme.telegram_adapter
status: NEEDS_PATH_CONFIRMATION
commercially_available: false
note: Telegram parece vivir en conversa-engine, pendiente de auditoría específica.
```

---

## 9. Semáforo actual

### OK

```text
excel_diagnostic en dispatcher formal
excel_diagnostic en CLI
evidence.py
evidence_requirement.py
evidence_gate.py
readiness.py
runtime_bridge.py
anamnesis_fsm.py
anamnesis_fsm_integration.py
delivery_package.py
```

### Parcial

```text
supplier_duplicate_check: disponible por CLI, no por dispatcher formal
microservice_dispatcher: implementado pero limitado a Excel
```

### No localizado / no prometer

```text
report_html.py
document_parser_front.py
docling_document_metadata_adapter
pymia/smartpyme/telegram_adapter.py
```

---

## 10. Próximo frente recomendado

```text
M17 — Align supplier_duplicate_check with formal dispatcher
```

Objetivo:

```text
conectar supplier_duplicate_check al microservice_dispatcher
sin cambiar su lógica de negocio,
y agregar test smoke de dispatch.
```

Criterio de éxito:

```text
supplier_duplicate_check debe pasar de:
PARTIALLY_AVAILABLE_BY_PATH

a:
AVAILABLE_BY_CLI_AND_DISPATCHER
```

---

## 11. Frase rectora

```text
El registry evita que una ficha parezca más disponible de lo que realmente está.
```
