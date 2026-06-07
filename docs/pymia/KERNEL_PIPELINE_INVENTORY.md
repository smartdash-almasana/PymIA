# Inventario kernel y pipeline PymIA / SmartPyme

> Documento relacionado: `docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md` define los puertos, gates, entradas y salidas que deben ordenar este inventario antes de nuevas implementaciones.

Fecha de creación: 2026-06-07 08:42 America/Argentina/Buenos_Aires
Última ampliación: 2026-06-07 08:42 America/Argentina/Buenos_Aires

## Veredicto

`CORE_PARCIAL_CON_INFRAESTRUCTURA_AVANZADA`

PymIA tiene infraestructura conversacional, evidencia, Telegram, catálogos y un núcleo mínimo real. El núcleo diagnóstico amplio todavía no está completo. SmartPyme conserva código heredado relevante que no debe perderse.

## Nivel de lectura usado en este inventario

| Indicador | Significado |
|---|---|
| `LEIDO_PROFUNDO` | Archivo abierto y leído con contenido relevante verificado. |
| `LEIDO_PARCIAL` | Archivo abierto parcialmente o por extracto suficiente para identificar función. |
| `IDENTIFICADO_POR_ESTRUCTURA` | Detectado por árbol, nombre, tests o referencias; requiere lectura posterior antes de usarlo como base de implementación. |
| `REFERENCIADO_POR_TESTS` | No necesariamente leído; aparece cubierto o mencionado por tests. |

Este inventario distingue existencia de comprensión. Los elementos `IDENTIFICADO_POR_ESTRUCTURA` no deben tratarse como auditados en profundidad.

---

## 1. Núcleo diagnóstico mínimo en PymIA

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Motor de fórmulas | `pymia/services/formula_engine_service.py` | Calcula fórmulas determinísticas o bloquea si faltan datos. | Ejecutable mínimo |
| Contrato de fórmulas | `pymia/contracts/formula_contract.py` | Define `FormulaInput`, `FormulaResult`, estados y fórmulas soportadas. | Ejecutable |
| Motor de patologías | `pymia/services/pathology_engine_service.py` | Evalúa una patología contra resultado de fórmula. | Ejecutable mínimo |
| Tanque de patologías local | `pymia/services/pathology_knowledge_tank.py` | Contiene patologías ejecutables locales. Hoy sólo se verificó `margen_bruto_negativo`. | Muy parcial |
| Reporte diagnóstico | `pymia/services/diagnostic_report_service.py` | Construye reporte diagnóstico mínimo y bloquea si falta evidencia, impacto o hallazgos. | Ejecutable parcial |
| Loader de catálogos | `pymia/services/catalog_loader_v1.py` | Carga catálogos JSON de fórmulas/patologías desde `docs`. | Ejecutable |

## 2. Catálogos PymIA

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Catálogo de patologías PymIA | `docs/pathology_catalog.v1.json` | Catálogo amplio de 50 patologías PyME. Incluye `LIQ_001`, `REN_001`, `INV_001`, `INV_002`, pricing, fiscal, datos, liquidez. | Documental/cargable |
| Catálogo de fórmulas PymIA | `docs/formula_catalog.v1.json` | Catálogo matematizador correlacionado con patologías. | Documental/cargable |
| Schema de fórmulas | `docs/formula_catalog.schema.v1.json` | Validación estructural del catálogo de fórmulas. | Documental/técnico |
| Diseño catálogo clínico | `docs/catalogo/diseno-catalogo-clinico.md` | Diseño conceptual migrado del catálogo síntoma-patología. | Documental |
| Atlas síntomas/patologías | `docs/catalogo/atlas-sintomas-patologias.md` | Marco clínico de síntomas y patologías. | Documental |
| Patologías y tanques | `docs/ingenieria_conversacional.PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md` | Define knowledge tanks, patologías, fórmulas, taxonomías. | Documental rector |
| Fórmulas matemáticas | `docs/ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md` | Define familias de fórmulas: rentabilidad, punto de equilibrio, stock, caja, precios, compras, escenarios. | Documental rector |

## 3. SmartPyme heredado relevante

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Catálogo Python SmartPyme | `../SmartPyme/app/catalog/pathologies.py` | Catálogo ejecutable de 6 patologías. | Ejecutable parcial |
| Patologías SmartPyme vistas | `../SmartPyme/app/catalog/pathologies.py` | `margen_bruto_negativo`, `trampa_producto_ads_negativo`, `venta_bajo_costo`, `falla_precision_int64`, `limbo_liquidaciones_ml`, `clasificacion_iva_lesiva`. | Parcial |
| Catálogo symptom/pathology | `../SmartPyme/app/catalogs/symptom_pathology_catalog.py` | Mapea dolor del dueño a síntoma operativo, patologías candidatas, skills, evidencia, variables, preguntas mayéuticas y bloqueos. | Muy relevante |
| Catálogos JSON SmartPyme | `../SmartPyme/app/catalogs/patologias_pyme_v0.json` | Catálogo JSON heredado de patologías PyME. | Relevante; revisar contenido |
| Fórmulas SmartPyme JSON | `../SmartPyme/app/catalogs/formulas_smartpyme_v0.json` | Catálogo heredado de fórmulas. | Relevante; revisar contenido |
| Column mapping catalog | `../SmartPyme/app/catalogs/column_mapping_catalog.json` | Mapeos de columnas. | Relevante para Excel heterogéneo |
| Taxonomía operativa argentina | `../SmartPyme/app/catalogs/taxonomia_operativa_pyme_argentina_v0.json` | Taxonomía sectorial PyME. | Relevante |
| Domain pack registry | `../SmartPyme/app/catalogs/domain_pack_registry.py` | Registro de paquetes de dominio. | Relevante |
| Skill registry | `../SmartPyme/app/catalogs/skill_registry.py` | Registro de skills. | Relevante |
| Operational conditions catalog | `../SmartPyme/app/catalogs/operational_conditions_catalog.py` | Catálogo de condiciones operativas. | Relevante |
| Diseño catálogo síntoma-patología | `../SmartPyme/docs/architecture/SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md` | Diseño histórico del catálogo síntoma-patología-skill. | Documental |

## 4. SmartPyme servicios heredados relevantes

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Formula engine | `../SmartPyme/app/services/formula_engine_service.py` | Motor de fórmulas similar al de PymIA. | Ejecutable mínimo |
| Formula catalog service | `../SmartPyme/app/services/formula_catalog_service.py` | Servicio de catálogo de fórmulas. | Relevante |
| Pathology engine | `../SmartPyme/app/services/pathology_engine_service.py` | Servicio de evaluación de patologías. | Relevante |
| Pathology evaluators | `../SmartPyme/app/services/pathology_evaluators.py` | Evaluadores ejecutables de patologías. Se verificaron `evaluate_margen_bruto_negativo`, `evaluate_venta_bajo_costo` y `EVALUATOR_REGISTRY`. | Ejecutable parcial |
| Diagnostic service | `../SmartPyme/app/services/diagnostic_service.py` | Servicio diagnóstico. | Relevante |
| Diagnostic report service | `../SmartPyme/app/services/diagnostic_report_service.py` | Reporte diagnóstico. | Relevante |
| Basic operational diagnostic | `../SmartPyme/app/services/basic_operational_diagnostic_service.py` | Diagnóstico operacional básico. | Relevante |
| Data curation service | `../SmartPyme/app/services/data_curation_service.py` | Curación de datos. | Relevante |
| Comparison service | `../SmartPyme/app/services/comparison_service.py` | Comparación de fuentes/valores. | Relevante |
| Findings service | `../SmartPyme/app/services/findings_service.py` | Gestión/construcción de hallazgos. | Relevante |
| Finding communication service | `../SmartPyme/app/services/finding_communication_service.py` | Comunicación de hallazgos. | Relevante |
| Fact extraction service | `../SmartPyme/app/services/fact_extraction_service.py` | Extracción de hechos. | Relevante |
| Normalization service | `../SmartPyme/app/services/normalization_service.py` | Normalización de datos. | Relevante |
| Canonicalization service | `../SmartPyme/app/services/canonicalization_service.py` | Canonicalización de datos. | Relevante |
| Clinical operational mapper | `../SmartPyme/app/services/clinical_operational_mapper.py` | Mapeo clínico-operacional. | Relevante |
| Operational assistant service | `../SmartPyme/app/services/operational_assistant_service.py` | Servicio asistente operacional. | Relevante |
| Operational interview engine | `../SmartPyme/app/services/operational_interview_engine.py` | Entrevista operacional. | Relevante |
| Operational taxonomy service | `../SmartPyme/app/services/operational_taxonomy_service.py` | Taxonomía operacional. | Relevante |
| Operational taxonomy matcher | `../SmartPyme/app/services/operational_taxonomy_matcher_service.py` | Matching taxonómico. | Relevante |
| Context validation service | `../SmartPyme/app/services/context_validation_service.py` | Valida contexto. | Relevante |
| Clarification service | `../SmartPyme/app/services/clarification_service.py` | Aclaraciones al dueño. | Relevante |
| Owner confirmation service | `../SmartPyme/app/services/owner_confirmation_service.py` | Confirmaciones del dueño. | Relevante |
| Owner selection service | `../SmartPyme/app/services/owner_selection_service.py` | Selecciones del dueño. | Relevante |
| Case opening service | `../SmartPyme/app/services/case_opening_service.py` | Apertura de caso. | Relevante |
| Case closure service | `../SmartPyme/app/services/case_closure_service.py` | Cierre de caso. | Relevante |
| Local XLSX diagnostic ingestion | `../SmartPyme/app/services/local_xlsx_diagnostic_ingestion_service.py` | Ingesta diagnóstica XLSX. | Relevante |
| Document ingestion orchestrator | `../SmartPyme/app/services/document_ingestion_orchestrator.py` | Orquesta ingestión documental. | Relevante |
| Document intake service | `../SmartPyme/app/services/document_intake_service.py` | Intake de documentos. | Relevante |

## 5. SmartPyme laboratorio / tabular

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Diagnóstico tabular CSV | `../SmartPyme/app/laboratorio_pyme/tabular_diagnostic.py` | Lee CSV con Polars y devuelve métricas de calidad: filas, columnas, columnas vacías, nulos, duplicados. | Ejecutable mínimo |
| Laboratorio service | `../SmartPyme/app/laboratorio_pyme/service.py` | Servicio de laboratorio PyME. | Relevante |
| Laboratorio application service | `../SmartPyme/app/laboratorio_pyme/application_service.py` | Capa de aplicación del laboratorio. | Relevante |
| Laboratorio contracts | `../SmartPyme/app/laboratorio_pyme/contracts.py` | Contratos del laboratorio. | Relevante |
| Laboratorio p0 runner | `../SmartPyme/app/laboratorio_pyme/p0_runner.py` | Runner inicial. | Relevante |

## 6. Excel, documentos y semántica PymIA

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Diagnóstico Excel directo | `pymia/smartpyme/excel_diagnostic.py` | Detecta celdas vacías, duplicados, productos sin costo, margen no calculable, margen bajo. | Ejecutable parcial |
| Parser frontal | `pymia/smartpyme/document_parser_front.py` | Frente de parsing documental. | Ejecutable |
| Metadata documento parseado | `pymia/smartpyme/parsed_document_metadata.py` | Modelo de metadata de documento. | Ejecutable |
| Adapter XLSX metadata | `pymia/smartpyme/xlsx_document_metadata_adapter.py` | Extrae/normaliza metadata desde Excel. | Ejecutable |
| Adapter Docling | `pymia/smartpyme/docling_document_metadata_adapter.py` | Adapter documental alternativo. | Ejecutable |
| Resolución semántica | `pymia/smartpyme/semantic_field_resolution.py` | Mapea columnas/campos a sentido operativo. | Ejecutable |
| Clasificación proveedores duplicados | `pymia/smartpyme/classifications/supplier_duplicate_check.py` | Clasificación específica de duplicados de proveedor. | Ejecutable puntual |

## 7. Evidencia, readiness y gates PymIA

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Evidence model | `pymia/smartpyme/evidence.py` | Modelo de evidencia. | Ejecutable |
| Evidence requirement | `pymia/smartpyme/evidence_requirement.py` | Requerimientos de evidencia. | Ejecutable |
| Evidence gate | `pymia/smartpyme/evidence_gate.py` | Decide si hay evidencia suficiente. | Ejecutable |
| Readiness | `pymia/smartpyme/readiness.py` | Estado de preparación para avanzar. | Ejecutable |
| Post-ficha evidence gate | `pymia/smartpyme/post_ficha_evidence_gate.py` | Evalúa evidencia después de completar ficha. | Ejecutable |
| Execution result gate | `pymia/smartpyme/execution_result_gate.py` | Valida resultados de ejecución antes de entrega. | Ejecutable |

## 8. Ficha, anamnesis y caso PymIA

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| FSM anamnesis | `pymia/smartpyme/anamnesis_fsm.py` | Primera entrevista / ficha PyME. | Ejecutable |
| Integración FSM | `pymia/smartpyme/anamnesis_fsm_integration.py` | Integra ficha con contexto progresivo, post-ficha y evidencia. | Ejecutable |
| Readiness anamnesis | `pymia/smartpyme/anamnesis_readiness.py` | Control de avance de anamnesis. | Ejecutable |
| Contrato conversacional | `pymia/smartpyme/conversation_contract.py` | Define reglas de conversación. | Ejecutable |
| Taxonomía | `pymia/smartpyme/taxonomy.py` | Clasifica tipo de PyME/organismo. | Ejecutable |
| Intake | `pymia/smartpyme/intake.py` | Convierte ficha/dolor en intake y evidence requests. | Ejecutable |
| Interrogation | `pymia/smartpyme/interrogation.py` | Estructura selectores/preguntas. | Ejecutable |
| Tank selection | `pymia/smartpyme/tank_selection.py` | Selección de tanque/conocimiento. | Ejecutable |
| Hipótesis operacional | `pymia/smartpyme/operational_hypothesis.py` | Modela hipótesis investigables. | Ejecutable |

## 9. Ejecución, hallazgos y reportes PymIA

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Runtime bridge | `pymia/smartpyme/runtime_bridge.py` | Puente para ejecutar capacidades. | Ejecutable |
| Microservice dispatcher | `pymia/smartpyme/microservice_dispatcher.py` | Dispatch de microservicios/capacidades. | Ejecutable |
| Finding projection | `pymia/smartpyme/finding_projection.py` | Convierte resultados en hallazgos accionables. | Ejecutable |
| Delivery package | `pymia/smartpyme/delivery_package.py` | Paquete de entrega. | Ejecutable |
| Delivery markdown | `pymia/smartpyme/delivery_markdown.py` | Render Markdown de entrega. | Ejecutable |
| Narrative | `pymia/narrative/` | Modelos, generadores y reporte mínimo narrativo. | Ejecutable parcial |

## 10. Telegram y estado PymIA

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Runtime Telegram directo | `pymia/telegram_bot_runtime.py` | Bot Telegram live/directo. | Ejecutable |
| Handler documentos Telegram | `pymia/telegram_document_handler.py` | Recibe/guarda documentos. | Ejecutable |
| Resumen Excel Telegram | `pymia/telegram_excel_summary.py` | Resume estructura de Excel. | Ejecutable |
| Diagnóstico Excel Telegram | `pymia/telegram_excel_diagnostic.py` | Diagnóstico Excel desde canal Telegram. | Ejecutable parcial |
| State | `pymia/orchestration/state.py` | Estado runtime/caso. | Ejecutable |
| State storage | `pymia/orchestration/state_storage.py` | Persistencia de estado. | Ejecutable |
| Graph | `pymia/orchestration/graph.py` | Grafo de decisión/orquestación. | Ejecutable |

## 11. Auditoría operacional y golden outputs PymIA

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Operational audit builder | `pymia/audit_result/builder.py` | Construye `OperationalAuditResult` desde evidencia estructurada, reporte narrativo, grounding, señales, patologías, acciones, preguntas y threads de auditoría. Mapea señales como `margen_bajo`, `caja_tensionada`, `sobrestock` a patologías `REN_001`, `LIQ_001`, `INV_002`, `INV_001`. | Relevante / ejecutable parcial |
| Evidence requirement matcher | `pymia/audit_result/evidence_requirement_matcher.py` | Cruza `StructuredEvidence` contra `formula_catalog.v1.json` y `pathology_catalog.v1.json`; calcula evidencia disponible/faltante, estado `calculable`, `pending_data`, `candidate`, `blocked`, `not_applicable`; genera preguntas de auditoría. | Muy relevante |
| Audit result models | `pymia/audit_result/models.py` | Modelos del resultado de auditoría operacional: métricas, patologías, riesgos, acciones, threads, narrativa permitida. | Relevante |
| Audit validators | `pymia/audit_result/validators.py` | Validaciones del resultado de auditoría. | Relevante |
| Golden findings La Textil | `tests/golden_findings/la_textil_expected.json` | Expected output amplio con fórmulas y patologías esperadas para caso textil; contiene referencias a `LIQ_001_vendido_cobrado`, `REN_001_margen_neto_real`, `INV_001_punto_reposicion`, `INV_002_rotacion_stock`, `PYME_017_pricing_drift`, entre otras. | Muy relevante |

## 12. Tests PymIA principales asociados

| Frente | Ruta |
|---|---|
| Fórmulas | `tests/services/test_formula_engine_service.py` |
| Patologías | `tests/services/test_pathology_engine_service.py` |
| Reporte diagnóstico | `tests/services/test_diagnostic_report_service.py` |
| Integración kernel chip 1 | `tests/services/test_kernel_chip1_integration.py` |
| Loader catálogo | `tests/services/test_catalog_loader_v1.py` |
| Excel diagnostic | `tests/smartpyme/test_excel_diagnostic.py` |
| Finding projection | `tests/smartpyme/test_finding_projection.py` |
| Evidence gate | `tests/smartpyme/test_evidence_gate.py` |
| Post-ficha gate | `tests/smartpyme/test_post_ficha_evidence_gate.py` |
| Semantic resolution | `tests/smartpyme/test_semantic_field_resolution.py` |
| Intake | `tests/smartpyme/test_intake.py` |
| Ficha FSM | `tests/smartpyme/test_anamnesis_fsm.py` |
| Integración FSM | `tests/smartpyme/test_anamnesis_fsm_integration.py` |
| Telegram runtime | `tests/telegram_runtime/test_telegram_bot_runtime.py` |
| Telegram FSM | `tests/telegram_runtime/test_telegram_bot_runtime_fsm_integration.py` |
| Telegram evidence bridge | `tests/telegram_runtime/test_telegram_bot_runtime_evidence_bridge.py` |
| Telegram E2E sequence | `tests/telegram_runtime/test_telegram_bot_runtime_e2e_sequence.py` |
| Narrative pipeline | `tests/test_narrative_pipeline.py` |
| Narrative report v2 | `tests/test_narrative_report_v2.py` |
| Minimal delivery report | `tests/test_minimal_delivery_report.py` |
| Orchestration state | `tests/orchestration/test_state.py` |
| State storage | `tests/orchestration/test_state_storage.py` |
| Graph | `tests/orchestration/test_graph.py` |

## 12. Tests SmartPyme relevantes encontrados

| Frente | Ruta |
|---|---|
| Fórmula API/agente/contrato/engine/resultados | `../SmartPyme/tests/test_formula_*` |
| Patologías API/engine/catalog/repository/venta bajo costo | `../SmartPyme/tests/test_pathology_*` |
| Catálogo síntoma-patología | `../SmartPyme/tests/catalogs/test_symptom_pathology_catalog.py` |
| Catálogo de fórmulas | `../SmartPyme/tests/catalogs/test_formula_catalog_service.py` |
| Domain pack registry | `../SmartPyme/tests/catalogs/test_domain_pack_registry.py` |
| Diagnóstico BEM/API | `../SmartPyme/tests/api/test_bem_to_diagnostic_e2e.py` |
| Diagnostic router | `../SmartPyme/tests/api/test_diagnostic_router.py` |
| Diagnostic report lifecycle | `../SmartPyme/tests/e2e/test_diagnostic_report_lifecycle.py` |
| Findings service | `../SmartPyme/tests/core/test_findings_service.py` |
| Finding communication | `../SmartPyme/tests/core/test_finding_communication_service.py` |
| Comparison service | `../SmartPyme/tests/core/test_comparison_service.py` |
| Fact extraction | `../SmartPyme/tests/core/test_fact_extraction_service.py` |
| Reconciliation | `../SmartPyme/tests/core/test_reconciliation*.py` |
| Telegram XLSX E2E | `../SmartPyme/tests/test_telegram_xlsx_e2e_ts_017.py` |
| Telegram XLSX router E2E | `../SmartPyme/tests/test_telegram_xlsx_router_e2e_ts_018.py` |

## 13. Omisiones detectadas en pasada adicional

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Document intelligence | `pymia/document_intelligence/` | Contratos e inferencia para entender documentos: `field_binding`, `semantic_schema`, `schema_inference_result`, `tenant_clinical_context`, `schema_inference_engine`. | Relevante para Excel heterogéneo / `IDENTIFICADO_POR_ESTRUCTURA` |
| Admission pipeline | `pymia/pipeline/admission/v1/` | Pipeline inicial de admisión, heurísticas y formateo de respuesta. | Relevante histórico/entrada / `IDENTIFICADO_POR_ESTRUCTURA` |
| Pipeline radiography | `pymia/pipeline_radiography/` | Runner, escenarios, trazas y reportes para radiografiar pipeline. | Relevante para auditoría preventiva / `IDENTIFICADO_POR_ESTRUCTURA` |
| Operational harness | `pymia/operational_harness/` | Harness operacional para consolidar fuentes/escenarios y correr checks locales. | Relevante / `IDENTIFICADO_POR_ESTRUCTURA` |
| SmartPyme repositories | `../SmartPyme/app/repositories/` | Repositorios de evidence, facts, findings, formulas, pathology, operational cases, decisions, jobs, reports, raw documents, Supabase/in-memory. | Relevante heredado / `IDENTIFICADO_POR_ESTRUCTURA` |
| SmartPyme core | `../SmartPyme/app/core/` | Core con calculators, findings, hallazgos, reconciliation, validation, clarification, pipeline y orchestrator. | Relevante heredado / `IDENTIFICADO_POR_ESTRUCTURA` |

## 14. Hallazgo de código adicional: tools y conversa-engine

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Document ingestion tool | `tools/document_ingestion.py` | Pipeline de curación XLSX: raw tables, normalized tables, curation report, export a `StructuredEvidence`, `XlsxCurationPipeline`, `build_structured_evidence_from_xlsx`. | Muy relevante / `IDENTIFICADO_POR_FIRMAS` |
| Excel evidence tool | `tools/excel_evidence.py` | Construye evidencia estructurada desde Excel y artefactos para kernel/auditoría. | Muy relevante / `IDENTIFICADO_POR_FIRMAS` |
| Document context classifier | `tools/document_context_classifier.py` | Clasifica contexto documental antes de tratarlo como evidencia. | Relevante / `IDENTIFICADO_POR_ESTRUCTURA` |
| BEM schema builder | `tools/bem_schema_builder/` | Construcción de schema/perfil Excel/preguntas para BEM. | Relevante heredado / `IDENTIFICADO_POR_ESTRUCTURA` |
| Conversa operational audit runner | `conversa-engine/operational_audit_runner.py` | Runner de auditoría operacional desde Excel. | Relevante / `IDENTIFICADO_POR_FIRMAS` |
| Conversa operational audit router | `conversa-engine/operational_audit_router.py` | Rutea mensajes contra `OperationalAuditResult`. | Relevante / `IDENTIFICADO_POR_FIRMAS` |
| Conversa document intake | `conversa-engine/document_intake.py` | Ingesta documental y disparo de auditoría operacional. | Relevante / `IDENTIFICADO_POR_FIRMAS` |
| Conversa evidence router | `conversa-engine/evidence_router.py` | Ruteo de evidencia conversacional. | Relevante / `IDENTIFICADO_POR_FIRMAS` |
| Conversa symptom pathology catalog | `conversa-engine/symptom_pathology_catalog.py` | Catálogo local de síntomas/patologías usado por conversa-engine. | Relevante / `IDENTIFICADO_POR_FIRMAS` |

## 15. Hallazgo adicional: contratos, MCP, microsaas y tests omitidos

| Componente | Ruta | Para qué sirve | Estado |
|---|---|---|---|
| Contracts PymIA | `pymia/contracts/` | Contratos de admisión, attachment lifecycle, catálogos, reporte diagnóstico, evidencia, fórmulas, patologías, primary context y SCN render/output. | Relevante / `IDENTIFICADO_POR_ESTRUCTURA` |
| MCP first clinical interview | `pymia/mcp_server/first_clinical_interview.py` | Servidor/herramienta MCP para primera entrevista clínica. | Relevante / `IDENTIFICADO_POR_ESTRUCTURA` |
| MCP server | `pymia/mcp_server/server.py` | Servidor MCP PymIA. | Relevante / `IDENTIFICADO_POR_ESTRUCTURA` |
| Microsaas registry | `pymia/microsaas/registry.py` | Registro de microsaas/capacidades. | Relevante / `IDENTIFICADO_POR_ESTRUCTURA` |
| Microsaas contracts | `pymia/microsaas/contracts.py` | Contratos de microsaas. | Relevante / `IDENTIFICADO_POR_ESTRUCTURA` |
| Tests document intelligence | `tests/document_intelligence/` | Tests de inferencia documental y contexto progresivo. | Relevante / `REFERENCIADO_POR_TESTS` |
| Tests SCN | `tests/scn/` | Tests de frontera SCN, render contract, output gateway y policy enforcement. | Relevante / `REFERENCIADO_POR_TESTS` |
| Tests contracts | `tests/contracts/` | Tests de contratos como attachment lifecycle. | Relevante / `REFERENCIADO_POR_TESTS` |
| Fixtures SmartPyme | `tests/fixtures/smartpyme/` | Excels fixture: `proveedores_duplicados.xlsx`, `ventas_costos_margen.xlsx`. | Relevante / `REFERENCIADO_POR_TESTS` |
| Tests depth E2E textil | `tests/smartpyme/test_depth_e2e_textile_owner_excel_flow.py` y `test_depth_e2e_textile_owner_excel_natural_gate.py` | Flujo profundo dueño + Excel textil. | Muy relevante / `REFERENCIADO_POR_TESTS` |

## 16. Qué tenemos

- Infraestructura conversacional avanzada.
- Telegram funcional.
- Ficha PyME funcional.
- Estado persistente.
- Gates de evidencia.
- Parser/metadata Excel.
- Semántica de campos.
- Catálogo documental de 50 patologías.
- Catálogo documental de fórmulas.
- Motor mínimo de fórmulas.
- Motor mínimo de patologías.
- Reporte diagnóstico mínimo.
- Narrativa/reporte mínimo.
- Muchos tests de flujo.
- En SmartPyme hay material heredado relevante: más contratos, repositorios, catálogos, servicios clínico-operacionales, tests de fórmula/patología, laboratorio tabular y symptom catalog.

## 14. Qué falta

- Convertir el catálogo de 50 patologías en código ejecutable.
- Ampliar fórmulas reales.
- Unir Excel heterogéneo → variables normalizadas → fórmula → patología.
- Crear tests multi-caso por patología.
- Medir impacto económico real.
- Generar reporte clínico integral desde findings reales.
- Validar robustez con varios Excel y varias PyMEs.
- Decidir qué partes heredadas de SmartPyme migrar formalmente a PymIA y cuáles dejar como arqueología.

## 15. Qué no volver a redescubrir

- Ya existe un kernel mínimo: fórmula + patología + reporte.
- Ya existe catálogo amplio documental de patologías.
- Ya existe catálogo documental de fórmulas.
- Ya existe infraestructura de evidencia y post-ficha.
- Ya existe Telegram con ficha y upload.
- SmartPyme conserva material heredado útil, especialmente `symptom_pathology_catalog.py`, servicios de diagnóstico/fórmula/patología, catálogos JSON y tests.
- La brecha central no es recepción ni conversación: es núcleo diagnóstico amplio ejecutable.

## 16. Próximo foco lógico

Construir `DiagnosticCoreV1` encima de lo existente, sin rehacer todo:

```text
ficha + Excel
→ variables normalizadas
→ patologías candidatas
→ fórmulas ejecutables
→ hallazgos cuantificados
→ reporte clínico operativo
```
