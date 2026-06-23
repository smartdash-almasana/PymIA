# SERVICE_1_FULL_LAYERED_IMPLEMENTATION_TRACE_V1

## Estado

```text
Tipo: PRODUCT_TRACE / MASTER_IMPLEMENTATION_AUDIT
Estado: MASTER_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
Commit autorizado: NO
Push autorizado: NO
```

## Propósito

Este documento fija de forma rigurosa la traza maestra de implementación por capas de **Servicio 1 Full** a partir de la verdad fáctica del repositorio y la evidencia documental, eliminando cualquier tipo de desactualización, supuestos de valor o derivas hacia MVPs o pilotos comerciales.

Servicio 1 no se reduce a First Aid: es un sistema completo determinístico e integrado de datos, Excel y contabilidad para la PyME, con chatbot conversacional arneado.

---

## Fuentes leídas / autoridad usada

*   [Pymia-memoria/_estado_actual.md](file:///e:/BuenosPasos/smartbridge/PymIA/Pymia-memoria/_estado_actual.md)
*   [Pymia-memoria/_task_actual.md](file:///e:/BuenosPasos/smartbridge/PymIA/Pymia-memoria/_task_actual.md)
*   [Pymia-memoria/_decisiones_vigentes.md](file:///e:/BuenosPasos/smartbridge/PymIA/Pymia-memoria/_decisiones_vigentes.md)
*   [Pymia-memoria/_no_volver_a_hacer.md](file:///e:/BuenosPasos/smartbridge/PymIA/Pymia-memoria/_no_volver_a_hacer.md)
*   [docs/producto/PYMIA_SERVICE_1_FULL_CATALOG_V1.md](file:///e:/BuenosPasos/smartbridge/PymIA/docs/producto/PYMIA_SERVICE_1_FULL_CATALOG_V1.md)
*   [docs/producto/PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md](file:///e:/BuenosPasos/smartbridge/PymIA/docs/producto/PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md)
*   [docs/producto/SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1.md](file:///e:/BuenosPasos/smartbridge/PymIA/docs/producto/SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1.md)

---

## 1. VEREDICT (Veredicto de Auditoría)

```text
SERVICE_1_FULL_STATUS: PARTIAL_SYSTEM_IMPLEMENTED / DOCUMENTATION_REALIGNED
```

### Diagnóstico de la Traza Maestra
1.  **Estado Implementado:** Se encuentra completamente cerrada y validada la cadena de **Primeros Auxilios (First Aid) asistido y manual**, incluyendo su delivery XLSX genérico reutilizable. La capa de contratos base (Capa 0), ingesta y normalización de valores (Capa 1), lógica de herramientas core autorizadas (Capa 2), renderizado y formateo de respuesta (Capa 3), exportación física openpyxl First Aid, y orquestación del arnés del operador (`service_1_pipeline_v1`, `service_1_operator_harness_v1`, `service_1_operator_delivery_package_v1`) están **operacionales y validadas dentro del alcance First Aid**.
2.  **Estado Parcial:**
    *   **Laboratorio Excel / Ingesta Semántica:** `document_ingestion.py` sigue residiendo como script aislado bajo `tools/`, pero ya existe una capa lógica productizada en `pymia/smartpyme/excel_treatment_lab_v1.py` que modela entradas, confirmaciones y límites sin hacer IO ni abrir runtime profundo.
    *   **Factoría Excel (Exceland):** El compilador de specs YAML y warehouse de templates en `exeland2` funciona de manera autónoma, y ahora existe un bridge lógico mínimo en `pymia/smartpyme/exceland_bridge_v1.py`; todavía falta la frontera controlada para invocar la generación física real.
    *   **Servicios Contables:** Ya existe una base contractual pura en `service_1_accounting_contracts_v1.py` y una compuerta humana explícita en `accounting_human_review_gate_v1.py`, pero todavía no existe runtime contable confiable ni conciliación operativa productiva.
3.  **Estado Faltante (Missing):** Ingesta de PDF funcional en runtime, conciliación real de Mercado Pago / tarjetas, matching real de facturas contra cobros, generación operativa de papeles de trabajo (`workpapers`), liquidación IVA/IIBB, generación de asientos para ERP, máquina de estados FSM productiva, adaptador LLM (IA arneada) y cableado del chatbot Telegram al pipeline.
4.  **Desbalance Documental Corregido en Esta Traza:** Los documentos maestros venían subestimando capas ya cerradas o productizadas de forma contractual (`xlsx_delivery`, `excel_treatment_lab_v1`, `exceland_bridge_v1`, `service_1_accounting_contracts_v1`, `accounting_human_review_gate_v1`). Esta versión realinea la traza con el código real, sin convertir contratos lógicos en claims de runtime.
5.  **Evidencia Empírica de Test y Aislamiento:** La cadena determinista de Servicio 1 mantiene suites focales verdes para delivery XLSX, Excel Treatment Lab, Exceland Bridge, accounting contracts y human review gate. Por contraste, el runtime profundo heredado de diagnóstico sigue siendo una frontera distinta y no debe confundirse con el estado de cierre de Servicio 1.

---

## 2. FULL INVENTORY (Inventario Técnico por Capas)

| Componente | Capa | Estado Real | Evidencia Documental | Evidencia de Código | Dependencia Anterior | Dependencia Posterior | Bloqueante Principal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `file_intake` | Capa 0 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_FILE_INTAKE_V1.md` | `file_intake_v1.py` | Ninguna | `boundary` | Ninguno |
| `first_aid_tool_result_v1` | Capa 0 | `IMPLEMENTED_VALIDATED` | `FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md` | `first_aid_tool_result_v1.py` | Ninguna | `precio_margen`, `caja_diaria`, `xlsx_delivery` | Ninguno |
| `service_1_taskspec_vocabulary` | Capa 0 | `IMPLEMENTED` | `PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md` | `service_1_taskspec_vocabulary_v1.py` | Ninguna | `taskspec_contract` | Ninguno |
| `service_1_taskspec_contract` | Capa 0 | `IMPLEMENTED` | `PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md` | `service_1_taskspec_contract_v1.py` | `taskspec_vocab` | `assembler` | Ninguno |
| `first_aid_toolbox_v1.json` | Capa 0 | `IMPLEMENTED` | `FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md` | `first_aid_toolbox_v1.json` | Ninguna | `toolbox_selector` | Ninguno |
| `first_aid_toolbox_pack_seed_v1.json` | Capa 0 | `IMPLEMENTED` | `FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md` | `first_aid_toolbox_pack_seed_v1.json` | Ninguna | `activation_evaluator` | Ninguno |
| `first_aid_tool_activation_v1.json` | Capa 0 | `IMPLEMENTED` | `FIRST_AID_TOOL_ACTIVATION_V1.md` | `first_aid_tool_activation_v1.json` | Ninguna | `activation_evaluator` | Ninguno |
| `file_intake_taskspec_boundary` | Capa 1 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md` | `file_intake_taskspec_boundary_v1.py` | `file_intake` | `assembler` | Ninguno |
| `service_1_taskspec_assembler` | Capa 1 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md` | `service_1_taskspec_assembler_v1.py` | `taskspec_contract`, `boundary` | `pipeline` | Ninguno |
| `evidence_value_normalizer` | Capa 1 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | `evidence_value_normalizer.py` | Ninguna | `activation_evaluator` | Ninguno |
| `first_aid_tool_activation_evaluator` | Capa 1 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` | `first_aid_tool_activation_evaluator_v1.py` | `activation_json`, `normalizer` | `pipeline` | Ninguno |
| `precio_margen_basico` | Capa 2 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | `first_aid_precio_margen_basico_v1.py` | `first_aid_tool_result` | `pipeline` | Ninguno |
| `caja_diaria_triage` | Capa 2 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | `first_aid_caja_diaria_triage_v1.py` | `first_aid_tool_result` | `pipeline` | Ninguno |
| `stock_alertas_basicas` | Capa 2 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | `first_aid_stock_alertas_basicas_v1.py` | `first_aid_tool_result` | `pipeline` | Ninguno |
| `gastos_triage` | Capa 2 | `MISSING` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | Ninguna | `first_aid_tool_result` | `pipeline` | Falta lógica runtime |
| `proveedores_triage` | Capa 2 | `DOCUMENTED_ONLY` | `FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md` | `exeland2/specs/compras_y_proveedores.yaml` | `first_aid_tool_result` | `pipeline` | Falta lógica runtime + diferido |
| `first_aid_xlsx_delivery` | Capa 3 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | `first_aid_xlsx_delivery_v1.py` | `first_aid_tool_result` | `delivery_flow` | Ninguno |
| `service_1_manual_first_aid_delivery_flow` | Capa 3 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | `service_1_manual_first_aid_delivery_flow_v1.py` | `first_aid_xlsx_delivery` | `pipeline` | Ninguno |
| `owner_response_renderer` | Capa 3 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md` | `owner_response_renderer_v1.py` | `file_intake`, `boundary` | `owner_message_formatter` | Ninguno |
| `owner_message_formatter` | Capa 3 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md` | `owner_message_formatter_v1.py` | `owner_response_renderer` | Ninguna | Ninguno |
| `service_1_excel_triage_report` | Capa 3 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md` | `service_1_excel_triage_report_v1.py` | `file_intake`, `boundary` | Ninguna | Ninguno |
| `document_ingestion` | Capa 4 | `IMPLEMENTED_PARTIAL` | `EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md` | `tools/document_ingestion.py` | Ninguna | `pipeline_full` | Falta empaquetado y wiring en runtime |
| `pdf_intake` | Capa 4 | `MISSING` | `PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md` | Ninguna | Ninguna | `document_ingestion` | Falta diseño y parser extractor |
| `exceland_factory` | Capa 5 | `IMPLEMENTED_PARTIAL` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | `exeland2/src/exceland_factory/` | Ninguna | `excel_factory_bridge` | Cantera aislada; puente lógico ya existe pero falta ejecución física controlada |
| `excel_factory_bridge` | Capa 5 | `IMPLEMENTED_MINIMAL_CONTRACT` | `SERVICE_1_EXCELAND_BRIDGE_V1.md` | `exceland_bridge_v1.py` | `exceland_factory` | `pipeline_full` | Falta frontera runtime para compilar/generar XLSX real |
| `bank_reconciliation_contract` | Capa 6 | `IMPLEMENTED_MINIMAL_CONTRACT` | `SERVICE_1_ACCOUNTING_CONTRACTS_V1.md` | `service_1_accounting_contracts_v1.py` | Ninguna | `bank_reconciliation` | Falta runtime de conciliación y entity resolution |
| `bank_reconciliation` | Capa 6 | `IMPLEMENTED_PARTIAL` | `PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` | `exeland2` template conciliador + kernel histórico | `bank_reconciliation_contract` | `workpaper_xlsx` | Falta motor PymIA-Live y entity resolution |
| `mercado_pago_reconciliation` | Capa 6 | `IMPLEMENTED_MINIMAL_CONTRACT` | `SERVICE_1_ACCOUNTING_CONTRACTS_V1.md` | `service_1_accounting_contracts_v1.py` | `bank_reconciliation_contract` | `workpaper_xlsx` | Falta runtime, parser y lógica de conciliación MP |
| `facturas_vs_cobros` | Capa 6 | `IMPLEMENTED_MINIMAL_CONTRACT` | `SERVICE_1_ACCOUNTING_CONTRACTS_V1.md` | `service_1_accounting_contracts_v1.py` | `bank_reconciliation_contract` | `workpaper_xlsx` | Falta matching real factura-cobro |
| `workpaper_xlsx` | Capa 6 | `IMPLEMENTED_MINIMAL_CONTRACT` | `SERVICE_1_ACCOUNTING_CONTRACTS_V1.md` | `service_1_accounting_contracts_v1.py` | `bank_reconciliation_contract` | `pipeline_full` | Falta generador operativo de workpapers |
| `accounting_human_review_gate` | Capa 6 | `IMPLEMENTED_MINIMAL_GATE` | `SERVICE_1_ACCOUNTING_HUMAN_REVIEW_GATE_V1.md` | `accounting_human_review_gate_v1.py` | `bank_reconciliation_contract` | `bank_reconciliation` | Bloquea claims y runtime hasta revisión humana explícita |
| `iva_iibb` | Capa 6 | `MISSING` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | Ninguna | Ninguna | Ninguna | Excluido por normativa/complejidad |
| `asientos_contables` | Capa 6 | `MISSING` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | Ninguna | Ninguna | Ninguna | Excluido por complejidad AFIP/ERP |
| `alertas_vencimientos` | Capa 6 | `IMPLEMENTED_PARTIAL` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | `first_aid_toolbox_v1.json` thresholds | Ninguna | Ninguna | Falta motor ejecutable |
| `gestor_tareas` | Capa 6 | `MISSING` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | Ninguna | Ninguna | Ninguna | Fuera de núcleo |
| `service_1_pipeline_v1` | Capa 7 | `IMPLEMENTED_VALIDATED` | `PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` | `service_1_pipeline_v1.py` | Capa 2 Tools, Capa 3 Delivery | `operator_harness` | Limitado a First Aid |
| `pipeline_full` | Capa 7 | `MISSING` | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | Ninguna | Capa 4 Lab, Capa 5 Bridge, Capa 6 Conciliación | `service_1_fsm` | Depende de la compleción de capas inferiores |
| `service_1_fsm` | Capa 8 | `EXPERIMENTAL_FROZEN` | `SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1.md` | `service_1_fsm_decision_patch_v1.py` | `pipeline_full` | `llm_adapter` | Congelamiento intencional por derivas |
| `llm_adapter` | Capa 9 | `MISSING` | `PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` | Ninguna | `service_1_fsm` | `chatbot_operativo` | Falta lógica y contratos de arnés de IA |
| `chatbot_operativo` | Capa 10| `NEEDS_WIRING` | `PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` | Telegram engine en `conversa-engine` | `llm_adapter` | Ninguna | Falta cablear canal a pipeline/FSM |

---

## 3. DEPENDENCY GRAPH (Grafo de Dependencias)

```mermaid
graph TD
    subgraph Capa 0: Contratos Fundacionales
        file_intake[file_intake_v1.py]
        tool_result[first_aid_tool_result_v1.py]
        taskspec_contract[service_1_taskspec_contract_v1.py]
        activation_contract[first_aid_tool_activation_v1.json]
    end

    subgraph Capa 1: Intake / TaskSpec / Evidence
        boundary[file_intake_taskspec_boundary_v1.py]
        assembler[service_1_taskspec_assembler_v1.py]
        activation_eval[first_aid_tool_activation_evaluator_v1.py]
    end

    subgraph Capa 2: Tools First Aid
        precio_margen[first_aid_precio_margen_basico_v1.py]
        caja_diaria[first_aid_caja_diaria_triage_v1.py]
        stock_alertas[first_aid_stock_alertas_basicas_v1.py]
        gastos_triage[gastos_triage_v1.py - MISSING]
    end

    subgraph Capa 3: Delivery de Archivos
        xlsx_delivery[first_aid_xlsx_delivery_v1.py]
        delivery_flow[service_1_manual_first_aid_delivery_flow_v1.py]
        renderer[owner_response_renderer_v1.py]
        formatter[owner_message_formatter_v1.py]
    end

    subgraph Capa 4: Excel Lab / Normalización
        doc_ingestion[tools/document_ingestion.py - PARTIAL]
        pdf_intake[pdf_intake_v1.py - MISSING]
    end

    subgraph Capa 5: Exceland Bridge / Factoría
        exceland[exeland2/ - PARTIAL]
        exceland_bridge[exceland_bridge_v1.py - IMPLEMENTED_MINIMAL_CONTRACT]
    end

    subgraph Capa 6: Contadores / Conciliaciones / Workpapers
        recon_contract[service_1_accounting_contracts_v1.py - IMPLEMENTED_MINIMAL_CONTRACT]
        review_gate[accounting_human_review_gate_v1.py - IMPLEMENTED_MINIMAL_GATE]
        bank_recon[bank_reconciliation_v1.py - PARTIAL_RUNTIME_MISSING]
        mp_recon[mercado_pago_reconciliation_v1.py - CONTRACT_ONLY]
        facturas_cobros[facturas_vs_cobros_v1.py - CONTRACT_ONLY]
        workpapers[workpaper_xlsx_v1.py - CONTRACT_ONLY]
    end

    subgraph Capa 7: Pipeline Servicio 1 Full
        pipeline_fa[service_1_pipeline_v1.py - PARTIAL]
        pipeline_full[service_1_pipeline_full_v1.py - MISSING]
    end

    subgraph Capa 8: FSM Servicio 1
        fsm[service_1_fsm_decision_patch_v1.py - FROZEN]
    end

    subgraph Capa 9: IA con Arnés / LLM Adapter
        llm_adapter[llm_adapter_v1.py - MISSING]
    end

    subgraph Capa 10: Chatbot Operativo
        chatbot[Telegram / WhatsApp - NEEDS_WIRING]
    end

    %% Conexiones
    boundary --> file_intake
    assembler --> boundary
    assembler --> taskspec_contract
    activation_eval --> activation_contract

    precio_margen --> tool_result
    caja_diaria --> tool_result
    stock_alertas --> tool_result
    gastos_triage --> tool_result

    xlsx_delivery --> tool_result
    delivery_flow --> xlsx_delivery

    renderer --> file_intake
    renderer --> boundary
    formatter --> renderer

    doc_ingestion --> file_intake
    pdf_intake --> doc_ingestion

    exceland_bridge --> exceland
    
    bank_recon --> recon_contract
    mp_recon --> recon_contract
    facturas_cobros --> recon_contract
    workpapers --> recon_contract
    review_gate --> recon_contract

    pipeline_fa --> precio_margen
    pipeline_fa --> caja_diaria
    pipeline_fa --> stock_alertas
    pipeline_fa --> delivery_flow

    pipeline_full --> pipeline_fa
    pipeline_full --> doc_ingestion
    pipeline_full --> exceland_bridge
    pipeline_full --> workpapers

    fsm --> pipeline_full
    llm_adapter --> fsm
    chatbot --> llm_adapter
```

---

## 4. LAYERED IMPLEMENTATION PLAN (Plan por Capas Estructurales)

### CAPA 0 — Contratos y Fronteras
*   **Componentes:** `file_intake_v1`, `first_aid_tool_result_v1`, `service_1_taskspec_vocabulary_v1`, `service_1_taskspec_contract_v1`, `first_aid_toolbox_v1.json`, `first_aid_toolbox_pack_seed_v1.json`, `first_aid_tool_activation_v1.json`.
*   **Dependencias satisfechas:** Ninguna.
*   **Dependencias pendientes:** Ninguna.
*   **Estado real:** `100% COMPLETO` (todos los archivos están implementados y validados con pruebas).
*   **Condición de cierre:** Los contratos declarativos y de tipado compilan y están congelados.

### CAPA 1 — Intake / TaskSpec / Evidence
*   **Componentes:** `file_intake_taskspec_boundary_v1`, `service_1_taskspec_assembler_v1`, `evidence_value_normalizer`, `first_aid_tool_activation_evaluator_v1`.
*   **Dependencias satisfechas:** Capa 0 (`file_intake`, `taskspec_contract`, contratos JSON).
*   **Dependencias pendientes:** Ninguna.
*   **Estado real:** `100% COMPLETO` (el assembler y el evaluator de activación se encuentran completamente implementados y validados con sus tests correspondientes).
*   **Condición de cierre:** Se genera un `Service1TaskSpec` coherente a partir de un archivo ingerido y se evalúa de manera determinista la activación de tools.

### CAPA 2 — Tools First Aid
*   **Componentes:** `precio_margen_basico`, `caja_diaria_triage`, `stock_alertas_basicas`, `gastos_triage` (Missing), `proveedores_triage` (Diferido).
*   **Dependencias satisfechas:** Capa 0 (`first_aid_tool_result_v1`).
*   **Dependencias pendientes:** Implementación en código de `gastos_triage`.
*   **Estado real:** `75% PARCIAL` (las 3 herramientas núcleo están completadas y testeadas; falta gastos).
*   **Condición de cierre:** Las 4 herramientas core están implementadas y devuelven un `FirstAidToolResultV1` válido.

### CAPA 3 — Delivery de Archivos
*   **Componentes:** `first_aid_xlsx_delivery_v1`, `service_1_manual_first_aid_delivery_flow_v1`, renderizadores owner-facing (`owner_response_renderer_v1`, `owner_message_formatter_v1`, `service_1_excel_triage_report_v1`).
*   **Dependencias satisfechas:** Capa 0 y Capa 1 (`file_intake`, `boundary`, `first_aid_tool_result_v1`).
*   **Dependencias pendientes:** Ninguna.
*   **Estado real:** `100% COMPLETO` (tanto los renderizadores como el motor de entrega física openpyxl y flujo de entrega manual están implementados y pasando tests).
*   **Condición de cierre:** Se escriben físicamente archivos XLSX estructurados y formateados con disclaimers, y se formatea el mensaje de chat de salida.

### CAPA 4 — Excel Lab / Normalización
*   **Componentes:** `tools/document_ingestion.py` (Parcial), `pdf_intake` (Missing).
*   **Dependencias satisfechas:** Capa 0 (`file_intake`).
*   **Dependencias pendientes:** Empaquetar y cablear `document_ingestion.py` en runtime; diseñar extractor PDF.
*   **Estado real:** `40% PARCIAL` (código de curación XLSX y CSV en tools es robusto; falta PDF y estructuración formal como módulo de PymIA-Live).
*   **Condición de cierre:** Ingesta y normalización de Excel, CSV y PDF producen un `StructuredEvidence` validado en el pipeline del producto.

### CAPA 5 — Exceland Bridge / Factoría
*   **Componentes:** Cantera en `exeland2` y bridge lógico mínimo en PymIA-Live (`exceland_bridge_v1.py`).
*   **Dependencias satisfechas:** `Service1XlsxDeliveryInputV1` y delivery XLSX genérico reutilizable.
*   **Dependencias pendientes:** Frontera runtime controlada para invocar compilación/generación física real sin meter YAML ni openpyxl de Exceland dentro del kernel.
*   **Estado real:** `60% PARCIAL` (la factoría funciona de forma autónoma en su subcarpeta; el bridge lógico ya existe y está testeado, pero falta ejecución física controlada).
*   **Condición de cierre:** PymIA-Live puede invocar el compilador y generador de openpyxl de `exeland2` bajo contrato sin mezclar código del kernel.

### CAPA 6 — Contadores / Conciliaciones / Workpapers
*   **Componentes:** `service_1_accounting_contracts_v1` (Implementado como contrato mínimo), `accounting_human_review_gate_v1` (Implementado como gate mínimo), `bank_reconciliation` (runtime parcial en cantera/histórico), `mercado_pago_reconciliation` (contract-only), `facturas_vs_cobros` (contract-only), `workpaper_xlsx` (contract-only), `alertas_vencimientos` (Parcial/Declarativo).
*   **Dependencias satisfechas:** Capa 0 (`first_aid_tool_result_v1`) y delivery XLSX genérico para reporte contractual.
*   **Dependencias pendientes:** Runtime de conciliación bancaria (con resolver de entidades), runtime MP, matching real factura-cobro y generador operativo de workpapers.
*   **Estado real:** `35% PARCIAL` (la base contractual y la compuerta humana ya existen y están testeadas; la ejecución contable real todavía no existe en PymIA-Live).
*   **Condición de cierre:** Se cruzan extractos de banco y cobros MP contra planillas de ventas emitiendo un workpaper XLSX de auditoría de diferencias de saldo.

### CAPA 7 — Pipeline Servicio 1 Full
*   **Componentes:** `service_1_pipeline_v1` (Parcial, First Aid), `service_1_pipeline_full` (Missing).
*   **Dependencias satisfechas:** Capa 2 (Tools), Capa 3 (Delivery).
*   **Dependencias pendientes:** Completar Capas 4, 5 y 6 para integrarlas en el pipeline unificado.
*   **Estado real:** `35% PARCIAL` (orquestación para First Aid completada; pipeline full multi-familia pendiente).
*   **Condición de cierre:** Un único endpoint orquesta la ingesta de cualquier archivo, clasificación de tarea, normalización, conciliación contable o triage, y genera la carpeta de entrega.

### CAPA 8 — FSM Servicio 1
*   **Componentes:** Máquina de estados finitos (`service_1_fsm_decision_patch_v1.py` congelada).
*   **Dependencias satisfechas:** Capa 7 (`pipeline_full`).
*   **Dependencias pendientes:** Descongelamiento e implementación de la máquina de estados.
*   **Estado real:** `10% INCOMPLETO` (archivado conceptualmente por riesgo de derivas técnicas).
*   **Condición de cierre:** FSM gestiona los estados de la tarea determinísticamente sin bucles infinitos.

### CAPA 9 — IA con Arnés / LLM Adapter
*   **Componentes:** Adaptador LLM de Servicio 1 (`llm_adapter_v1`).
*   **Dependencias satisfechas:** Capa 8 (FSM).
*   **Dependencias pendientes:** Contratos de arnés y tests de restricción de outputs.
*   **Estado real:** `5% MISSING` (solo documentado conceptualmente).
*   **Condición de cierre:** El LLM produce únicamente TaskSpec, EvidenceRequest, ExcelSpec u OwnerQuestion validados por el runtime.

### CAPA 10 — Chatbot Operativo
*   **Componentes:** Canal Telegram/WhatsApp cableado al LLM Adapter y FSM.
*   **Dependencias satisfechas:** Capa 9 (`llm_adapter`).
*   **Dependencias pendientes:** Integración y cableado de canal al flujo.
*   **Estado real:** `5% NEEDS_WIRING` (la infraestructura básica del canal existe en el repo principal de SmartDash, pero desconectada de Servicio 1).
*   **Condición de cierre:** El dueño PyME carga un archivo en Telegram y el chatbot devuelve de forma autónoma el paquete de entrega o pide aclaraciones controladas.

---

## 5. CRITICAL PATH (Camino Técnico Crítico hacia Servicio 1 Full)

El camino crítico estructurado e incremental, basado estrictamente en dependencias topológicas de código, es el siguiente:

1.  **Bloques ya cerrados y reusables:** `SERVICE_1_FIRST_AID_FAMILY_CLOSURE_V1`, `SERVICE_1_XLSX_DELIVERY_GENERALIZATION_V1`, `SERVICE_1_EXCEL_TREATMENT_LAB_PRODUCTIZATION_V1`, `SERVICE_1_EXCELAND_BRIDGE_V1`, `SERVICE_1_ACCOUNTING_CONTRACTS_V1` y `SERVICE_1_ACCOUNTING_HUMAN_REVIEW_GATE_V1` ya aportan bases tipadas y testeadas para las capas 2 a 6.
2.  **Conciliación Bancaria Base (`SERVICE_1_BANK_RECONCILIATION_CONTRACT_V1` o sandbox runtime contract equivalente):** Definir el runtime mínimo que consume los contratos contables ya creados, mantiene `runtime_authorized=False` por defecto y deja explícito el límite de entity resolution.
3.  **Conciliación de Mercado Pago (`SERVICE_1_MERCADO_PAGO_RECONCILIATION_V1`):** Extender la familia contractual a un runtime mínimo de conciliación MP sin abrir APIs ni automatizaciones fuera de alcance.
4.  **Facturas vs Cobros / Workpapers Runtime:** Crear la ejecución mínima para `invoice_collection_matching` y `accounting_workpaper` sobre la base contractual ya existente, sin sobreclaimear exactitud fiscal.
5.  **Pipeline Servicio 1 Full (`SERVICE_1_FULL_PIPELINE_V1`):** Unificar el pipeline para integrar laboratorio Excel, bridge de factoría y runtimes contables autorizados en un único motor central.
6.  **Máquina de Estados (`SERVICE_1_FSM_V1`):** Diseñar e implementar la máquina de estados finitos que controle transiciones y bloqueos de tareas en la Capa 8.
7.  **Adaptador IA y Arnés (`SERVICE_1_LLM_ADAPTER_V1`):** Implementar el arnés del adaptador LLM para restringir las salidas conversacionales a formatos tipados del sistema en la Capa 9.
8.  **Wiring de Chatbot (`SERVICE_1_CHATBOT_OPERATIVE_V1`):** Conectar el canal de mensajería (Telegram) a la FSM y al pipeline en la Capa 10.

---

## 6. COMPLETENESS ESTIMATE (Estimación de Completitud)

### 1. Estimación por Familia Funcional
*   **First Aid (Primeros Auxilios):** **100%** (Familia runtime cerrada dentro del alcance autorizado).
*   **Laboratorio Excel (Excel Lab):** **75%** (La capa lógica está productizada y testeada; falta runtime integrado de `document_ingestion` y falta PDF).
*   **Factoría Excel (Exceland):** **70%** (Cantera y bridge lógico mínimo listos; falta frontera controlada de generación física).
*   **XLSX Delivery:** **100%** (Totalmente implementado y pasando pruebas unitarias).
*   **Servicios Contables y Conciliación:** **25%** (La familia contractual y el gate humano existen; faltan runtimes bancarios/MP/facturas/workpapers).
*   **Alertas y Vencimientos:** **20%** (Estructura declarativa y umbrales en JSON; falta motor ejecutable).
*   **Orquestación y Arnés (Operator Engine):** **100%** (Pipeline First Aid, arnés y empaquetador manual listos y validados).
*   **FSM, LLM y Chatbot:** **15%** (Telegram base existe; FSM y adapter en estado conceptual o experimental congelado).

### 2. Estimación por Capa Técnica
*   **Capa 0 (Contratos y fronteras):** **100%**
*   **Capa 1 (Intake / TaskSpec / Evidence):** **100%**
*   **Capa 2 (Tools First Aid):** **100%**
*   **Capa 3 (Delivery de archivos):** **100%**
*   **Capa 4 (Excel Lab / normalización):** **55%**
*   **Capa 5 (Exceland Bridge / factoría):** **60%**
*   **Capa 6 (Contadores / conciliaciones / workpapers):** **35%**
*   **Capa 7 (Pipeline Servicio 1 full):** **35%**
*   **Capa 8 (FSM Servicio 1):** **10%**
*   **Capa 9 (IA con arnés / LLM Adapter):** **5%**
*   **Capa 10 (Chatbot operativo):** **5%**

### 3. Estimación del Porcentaje de Completitud Total
```text
SERVICE_1_FULL_COMPLETENESS: 60%
```
*   *Justificación:* La base del sistema asistido/manual de First Aid, el delivery XLSX genérico, la productización lógica del Excel Lab, el bridge lógico de Exceland y la familia contractual contable ya están cerrados o realineados. Sin embargo, Servicio 1 Full sigue condicionado por la falta de runtimes contables reales, `pipeline_full`, FSM y gobierno conversacional controlado.

---

## 7. NEXT BLOCK (Próximo Bloque de Avance hacia Servicio 1 Full)

El próximo bloque técnico coherente y dependencialmente correcto es:

```text
SERVICE_1_BANK_RECONCILIATION_CONTRACT_V1
```

*   **Tipo:** `CONTRACT_AND_SANDBOX_RUNTIME_BOUNDARY` (abre runtime mínimo controlado, pero no habilita ejecución contable productiva ni claims de exactitud fiscal).
*   **Motivo de dependencia:** First Aid, XLSX Delivery, Excel Treatment Lab, Exceland Bridge, accounting contracts y accounting human review gate ya están cerrados en su capa mínima. La siguiente dependencia real es transformar el contrato contable bancario en una frontera de runtime autorizable y verificable.
*   **Entregables específicos:**
    1.  *Contrato de runtime mínimo:* Entrada/salida/límites explícitos para conciliación bancaria básica.
    2.  *Integración con gate humano:* Asegurar que toda ejecución potencial siga bloqueada por `accounting_human_review_gate_v1` hasta revisión explícita.
    3.  *Prueba de humo contractual:* Validar que el runtime candidato consuma `service_1_accounting_contracts_v1` sin saltarse límites ni claims prohibidos.

---

## 8. FORBIDDEN NEXT BLOCKS (Fronteras Prohibidas Activas)

Queda estrictamente prohibido iniciar trabajos o abrir ramas de código en runtime sobre los siguientes frentes:

*   **Chatbot operativo / Telegram:** No implementar wiring del canal de mensajería (riesgo de deriva conversacional sin FSM).
*   **LLM SDKs / OpenAI / OpenRouter:** No implementar integraciones de IA (riesgo de alucinaciones matemáticas sin arnés).
*   **FSM productiva:** No descongelar ni refactorizar `service_1_fsm_decision_patch_v1.py` sin una auditoría de flujo previa.
*   **Conciliación Bancaria y Mercado Pago:** No escribir lógica de cruce de banco sin contratos formales de conciliación tipados.
*   **IVA / IIBB / Liquidaciones impositivas:** Fuera del alcance determinístico de Servicio 1.
*   **Asientos Contables Automáticos:** Fuera del alcance.
*   **Integración con ERPs (Odoo, SAP, etc.):** Fuera de alcance.
*   **Modificación de `vertical_slice.py`:** Debe permanecer congelado como adaptador CLI histórico.
*   **Frameworks externos:** No incorporar dependencias de FastAPI, LangGraph o arquitecturas de multiagentes.
*   **Git hygiene:** No ejecutar comandos del tipo `git add .` para evitar commitear archivos temporales o quarantine.

---

## Cierre

```text
SERVICE_1_FULL_LAYERED_IMPLEMENTATION_TRACE_V1_MASTER_READY
```
