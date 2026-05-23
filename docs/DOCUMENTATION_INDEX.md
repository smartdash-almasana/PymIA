# Índice de Gobernanza Documental de PymIA
**Índice Canónico, Gobierno Documental y Mapeo de Relaciones de Runtime**

> [!IMPORTANT]
> Este documento actúa como el índice unificado soberano de la biblioteca documental de **PymIA**. Define qué documentos rigen y guían de forma directa la implementación y cuáles pertenecen al acervo histórico o conceptual del proyecto. Todo ingeniero o agente inteligente de desarrollo debe consultar este índice antes de guiar cambios de código.

---

## 1. Tabla General de Clasificación de Documentos

El catálogo documental completo se clasifica y se mapea con respecto a su estado y relación con el código productivo:

| Ruta del Documento | Estado | Tema | Dueño Conceptual | Decisión Asociada | Reemplaza a | Reemplazado por | Relación con Código | Acción Recomendada |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md` | **VIGENTE** | Inferencia de Esquema Semántico y Contrato de Ingestión | Document Intelligence / Polars Engine | ADR-004, ADR-005, ADR-006 | `tools/document_ingestion.py` antiguos mapeos | — | `tools/excel_evidence.py`, `tools/document_ingestion.py` | **Preservar y usar como guía principal de refactor** |
| `docs/adr/ADR-004-bem-como-fallback-pasivo.md` | **VIGENTE** | Relegación de BEM a fallback de contingencia | Arquitectura Maestra / Hermes | ADR-004 | `arquitectura/SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md` | — | `conversa-engine/document_intake.py` | **Preservar. Prohíbe BEM como default.** |
| `docs/adr/ADR-005-document-intelligence-engine.md` | **VIGENTE** | Motor local Polars y validación matemática | Document Intelligence | ADR-005 | Mapeos ad-hoc del ingestor antiguo | — | `tools/document_ingestion.py` (nuevo) | **Preservar. Rige desarrollo local.** |
| `docs/adr/ADR-006-tenant-clinical-context-as-input.md` | **VIGENTE** | EvidenceBundle e integración con Kernel | Conversational Boundary / Kernel | ADR-006 | Entrada directa de metadata opaca | — | `pymia/contracts/evidence_v1.py` | **Preservar. Rige contratos del kernel.** |
| `docs/adr/ADR-007-documentation-governance.md` | **VIGENTE** | Gobierno documental y estandarización | Gobierno Técnico | ADR-007 | — | — | — | **Preservar. Rige ciclo de vida de docs.** |
| `docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md` | **PROPUESTA** | Integración MCP Hermes↔PymIA (Hermes client, PymIA server) | Hermes Orchestrator / Kernel PymIA | ADR-008 | Integraciones ad-hoc sin frontera MCP explícita | — | `pymia/hermes/adapter.py`, `conversa-engine/main.py` | **Validar y adoptar como frontera oficial antes de contrato MCP v1.** |
| `docs/README.md` | **VIGENTE** | Raíz de la Biblioteca Documental y principios | Gobierno Técnico | ADR-007 | — | — | — | **Preservar como portal inicial.** |
| `docs/INVENTARIO_CANONICO.md` | **VIGENTE** | Inventario de variables y estructuras | Gobierno Técnico | — | — | — | — | **Preservar y verificar integridad.** |
| `docs/DOCTRINA_ROBUSTEZ_INCREMENTAL_Y_MIGRACION_MVP.md` | **VIGENTE** | doctrina y robustez incremental | Gobierno Técnico | — | — | — | — | **Preservar para mantener filosofía.** |
| `docs/hermes/principio-obligatorio-hermes-runtime-orchestrator.md` | **VIGENTE** | Rol de Hermes como orquestador | Hermes Orchestrator | — | — | — | — | **Preservar. Prohíbe lógica en Hermes.** |
| `docs/hermes/boundary-integracion-conversacional.md` | **VIGENTE** | Boundary entre Hermes y Kernel PymIA | Conversational Boundary | — | — | — | — | **Preservar.** |
| `docs/hermes/autoaditoria-hermes-pipeline-minimo-accionable.md` | **VIGENTE** | Autoaditoría e integridad de adjuntos | Hermes Orchestrator | — | — | — | — | **Preservar.** |
| `docs/arquitectura/DOCUMENT_CONTEXT_CLASSIFIER_V1.md` | **VIGENTE** | Triaje semántico contextual de entrada | Triage Subsystem | — | — | — | `document_context_classifier.py` | **Preservar.** |
| `docs/arquitectura/pipeline-traceability-boundary-v1.md` | **VIGENTE** | Trazabilidad del pipeline de evidencia | Pipeline Traceability | — | — | — | `pymia/contracts/attachment_lifecycle_v1.py` | **Preservar.** |
| `docs/arquitectura/orchestration-boundary.md` | **VIGENTE** | Límites de orquestación transaccional | Hermes Orchestrator | — | — | — | — | **Preservar.** |
| `docs/arquitectura/GLOSARIO_SEMANTICO_PYMIA.md` | **VIGENTE** | Glosario de términos clínicos-operativos | Kernel PymIA | — | — | — | — | **Preservar.** |
| `docs/arquitectura/KERNEL_ANALITICA_TABULAR_SOBERANA.md` | **VIGENTE** | Arquitectura conceptual del kernel local | Kernel PymIA | — | — | — | — | **Preservar.** |
| `docs/arquitectura/arquitectura-maestra.md` | **VIGENTE** | Guía de arquitectura unificada | Arquitectura Maestra | — | — | — | — | **Preservar.** |
| `docs/arquitectura/ONTOLOGIA_AGENTES_SISTEMA.md` | **VIGENTE** | Ontología de agentes del sistema (Dueño, Hermes, PymIA, PyME) | Arquitectura Maestra / Kernel PymIA / Hermes Orchestrator | — | — | — | `pymia/`, `conversa-engine/`, `hermes/` (transversal) | **Preservar. Rige responsabilidades entre agentes del sistema.** |
| `docs/arquitectura/HERMES_CAPABILITY_AUDIT.md` | **VIGENTE** | Radiografía de capacidades reales de Hermes Agent (Nous Research) y frontera con PymIA | Hermes Orchestrator / Arquitectura Maestra | — | — | — | `pymia/hermes/adapter.py`, `conversa-engine/` | **Preservar. Rige integración PymIA↔Hermes.** |
| `docs/contratos/contratos-clinicos-operacionales.md` | **VIGENTE** | Contratos de diagnóstico contable | Kernel PymIA | — | — | — | — | **Preservar.** |
| `docs/contratos/evidence-chain-v1.md` | **VIGENTE** | Cadena física-lógica de evidencia | Pipeline Traceability | — | — | — | — | **Preservar.** |
| `docs/contratos/owner-decision-v1.md` | **VIGENTE** | Decisiones y feedback interactivo del dueño | Conversational Boundary | — | — | — | — | **Preservar.** |
| `docs/formula_catalog.v1.json` | **VIGENTE** | Catálogo JSON de identidades matemáticas | Kernel PymIA / Polars | ADR-005 | — | — | `tools/excel_evidence.py` | **Preservar. Consumido por runtime.** |
| `docs/pathology_catalog.v1.json` | **VIGENTE** | Catálogo JSON de patologías PyME | Kernel PymIA | — | — | — | `pymia/pipeline/admission/` | **Preservar. Consumido por runtime.** |
| `docs/formula_catalog.schema.v1.json` | **VIGENTE** | Esquema JSON para validación de fórmulas | Kernel PymIA | — | — | — | — | **Preservar.** |
| `docs/catalogo/primary_context_taxonomy.v1.json` | **VIGENTE** | Taxonomía de triaje en formato JSON | Triage Subsystem | — | — | — | `document_context_classifier.py` | **Preservar. Consumido por runtime.** |
| `docs/transient-design/TENANT_CLINICAL_CONTEXT_AND_DOCUMENT_INTELLIGENCE_DESIGN.md` | **CANDIDATO** | TenantClinicalContext, PymeColumnOntology, motor documental contextual | PymIA Document Intelligence | ADR-006 | — | — | `pymia/contracts/evidence_v1.py` | **Usar como insumo directo para ADR definitivo e implementación por Opus.** |
| `docs/transient-design/CONVERSATION_CLINICAL_RUNTIME_STRATEGIC_DIRECTION.md` | **CANDIDATO** | Clinical Conversation Runtime, fases conversacionales, UI guiada y adquisición progresiva de contexto | Conversational Boundary / Runtime Governance | ADR-006, ADR-007 | — | — | Futuro `ConversationClinicalStateMachine`, `TenantClinicalContext`, menús Hermes/Telegram, `EvidencePlan`, FIO | **Usar como dirección estratégica antes de diseñar cuestionario, menú del bot o runtime conversacional.** |
| `docs/prompts/README.md` | **CANDIDATO** | Índice local de prompts de ingeniería derivados de la gobernanza documental | Gobierno Técnico / Prompt Engineering | ADR-007 | — | — | — | **Mantener sincronizado con este índice canónico.** |
| `docs/prompts/PROMPT_MASTER_DOCUMENT_INTELLIGENCE_ENTERPRISE.md` | **CANDIDATO** | Blueprint enterprise para refactor Document Intelligence completo | PymIA Document Intelligence / Prompt Engineering | ADR-004, ADR-005, ADR-006, ADR-007 | — | — | Futuro `pymia/document_intelligence/`, `EvidenceBundle`, matcher, runtime documental | **Usar sólo como blueprint rector. No ejecutar monolíticamente. Derivar prompts por fase.** |
| `docs/prompts/PROMPT_PHASE1_DOCUMENT_INTELLIGENCE_ISOLATED.md` | **VIGENTE** | Prompt quirúrgico ejecutable para Fase 1: contratos + módulo aislado + tests | PymIA Document Intelligence / Prompt Engineering | ADR-005, ADR-006 | `PROMPT_MASTER_DOCUMENT_INTELLIGENCE_ENTERPRISE.md` como ejecución monolítica | — | Futuro `pymia/document_intelligence/` y `tests/document_intelligence/` | **Usar como próxima instrucción de implementación Fase 1. Prohíbe integración runtime prematura.** |
| `docs/arquitectura/CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md` | **CANDIDATO** | Diseño preliminar del triage taxonómico | Triage Subsystem | — | — | — | — | **Validar antes de recodificar triage.** |
| `docs/arquitectura/HERMES_CONTRATO_SEMANTICO.md` | **CANDIDATO** | Contrato de comunicación Hermes-Dueño | Hermes Orchestrator | — | — | — | — | **Validar antes de expandir el chatbot.** |
| `docs/hermes/soul.md` | **CANDIDATO** | Directrices de comportamiento de Hermes | Hermes Orchestrator | — | — | — | — | **Validar y consolidar en config.** |
| `docs/catalogo/atlas-sintomas-patologias.md` | **CANDIDATO** | Catálogo clínico-operativo expandido | Kernel PymIA | — | — | — | — | **Validar con expertos contables.** |
| `docs/catalogo/diseno-catalogo-clinico.md` | **CANDIDATO** | Estructuración del catálogo contable | Kernel PymIA | — | — | — | — | **Validar para fase de diagnóstico.** |
| `docs/catalogo/anamnesis-y-catalogos.md` | **CANDIDATO** | Captura interactiva de síntomas | Conversational Boundary | — | — | — | — | **Validar.** |
| `docs/producto/capa-00-canal-entrada.md` | **CANDIDATO** | Diseño funcional de la ingesta | Producto | — | — | — | — | **Validar para experiencia de usuario.** |
| `docs/producto/capa-01-admision-epistemologica.md` | **CANDIDATO** | Triage clínico operacional funcional | Producto | — | — | — | — | **Validar.** |
| `docs/producto/protocolo-anamnesis-mvp.md` | **CANDIDATO** | Flujo conversacional de recepción | Producto | — | — | — | — | **Validar.** |
| `docs/producto/asertividades-operativas.md` | **CANDIDATO** | Métricas de precisión diagnóstica | Producto | — | — | — | — | **Validar.** |
| `docs/producto/registro-ciclos-operativos.md` | **CANDIDATO** | Planificación de ciclos comerciales | Producto | — | — | — | — | **Validar.** |
| `docs/hermes/pipeline-funcional-pymia-nodos-existentes.md` | **CANDIDATO** | Conexión preliminar de nodos conversacionales | Hermes Orchestrator | — | — | — | — | **Ignorar en implementación actual.** |
| `docs/hermes/hipotesis-ensamble-nodos-smartpyme-para-kernel-pymia.md` | **CANDIDATO** | Hipótesis de asamblea de nodos | Hermes Orchestrator | — | — | — | — | **Ignorar en implementación actual.** |
| `docs/hermes/contrato-minimo-integracion-externa.md` | **CANDIDATO** | Borrador de integración con APIs externas | Hermes Orchestrator | — | — | — | — | **Ignorar en implementación actual.** |
| `docs/hermes/decision-ensamblaje-chip1-estructura-destino.md` | **CANDIDATO** | Integración del chip conversacional preliminar | Hermes Orchestrator | — | — | — | — | **Ignorar.** |
| `docs/hermes/flujo-objetivo-hermes-como-conducto-parte-1.md` | **CANDIDATO** | Flujo secuencial de Hermes como proxy | Hermes Orchestrator | — | — | — | — | **Ignorar.** |
| `docs/arquitectura/SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md` | **SUPERADO** | Semántica compartida Hermes-PymIA-BEM | Arquitectura | ADR-004 | — | `docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md` | — | **No usar. BEM ya no es primario.** |
| `docs/arquitectura/signal-admission-refactor.md` | **SUPERADO** | Refactor de admisión de señales físicas | Kernel PymIA | — | — | Contratos clínicos vigentes | — | **No usar. Obsoleto.** |
| `docs/arquitectura/palantir-principles.md` | **ARCHIVO** | Principios filosóficos de desarrollo | Gobierno Técnico | — | — | — | — | **Conservar solo como referencia.** |
| `docs/arquitectura/PDF_IMAGE_EXTRACTION_BENCHMARK.md` | **ARCHIVO** | Pruebas de extracción sobre PDFs escaneados | Document Intelligence | — | — | — | — | **Conservar solo como referencia.** |
| `docs/arquitectura/domain-classification.md` | **ARCHIVO** | Clasificación de dominios del modelo | Arquitectura | — | — | — | — | **Conservar como referencia.** |
| `docs/arquitectura/entropy-routing.md` | **ARCHIVO** | Ruteo estocástico de conversaciones | Arquitectura | — | — | — | — | **Conservar como referencia.** |
| `docs/arquitectura/capability-runtime.md` | **ARCHIVO** | Capacidades de ejecución del runtime | Arquitectura | — | — | — | — | **Conservar.** |
| `docs/arquitectura/harness-engineering.md` | **ARCHIVO** | Gobierno de arneses y simuladores | Arquitectura | — | — | — | — | **Conservar.** |
| `docs/vision/SMARTPYME_LABORATORIO_PYME_Y_ESTABILIZACION_OPERACIONAL.md` | **ARCHIVO** | Visión del laboratorio contable | Vision | — | — | — | — | **Conservar histórica.** |
| `docs/vision/SMARTPYME_MVP_REALISTA_Y_FILOSOFIA_OPERACIONAL.md` | **ARCHIVO** | Filosofía operativa inicial | Vision | — | — | — | — | **Conservar histórica.** |
| `docs/fundamentos/metodo-hipotetico-deductivo.md` | **ARCHIVO** | Base metodológica del diagnóstico contable | Epistemología | — | — | — | — | **Conservar histórica.** |
| `docs/fundamentos/organismo-pyme.md` | **ARCHIVO** | Definición biológica-operacional de PyME | Epistemología | — | — | — | — | **Conservar histórica.** |
| `docs/fundamentos/primer-tiempo-logico.md` | **ARCHIVO** | Tiempos de asimilación lógica del dueño | Epistemología | — | — | — | — | **Conservar histórica.** |
| `docs/fundamentos/cosmovision-clinico-operacional.md` | **ARCHIVO** | Cosmovisión fundacional del kernel | Epistemología | — | — | — | — | **Conservar histórica.** |
| `docs/epistemologia/protocolo-conversacional-hermes.md` | **ARCHIVO** | Protocolo conversacional estricto | Epistemología | — | — | — | — | **Conservar histórica.** |
| `docs/epistemologia/modelo-verdad-soberania.md` | **ARCHIVO** | Modelo epistémico de verdad de datos | Epistemología | — | — | — | — | **Conservar histórica.** |
| `docs/epistemologia/contrato-epistemologico-smartgraph.md` | **ARCHIVO** | Contrato de grafos del conocimiento | Epistemología | — | — | — | — | **Conservar histórica.** |
| `docs/hermes/protocolo-doble-lectura-codex-kernel.md` | **ARCHIVO** | Protocolo de sincronía conversacional | Hermes | — | — | — | — | **Conservar histórica.** |
| `docs/hermes/plano-logico-kernel-integrado-pines-estados-compuertas.md` | **ARCHIVO** | Plano físico de compuertas lógicas | Hermes | — | — | — | — | **Conservar histórica.** |
| `docs/hermes/inventario-smartpyme-nodos-colgados-para-pymia.md` | **ARCHIVO** | Inventario de código colgado legacy | Hermes | — | — | — | — | **Conservar histórica.** |
| `docs/hermes/kernel-minimo-viable-y-corpus-minimo.md` | **ARCHIVO** | Corpus mínimo viable de conversación | Hermes | — | — | — | — | **Conservar histórica.** |
| `docs/hermes/incidente-integracion-hermes-pymia-a-mitad-de-construccion.md` | **ARCHIVO** | Revisión post-mortem de incidentes | Hermes | — | — | — | — | **Conservar histórica.** |
| `docs/migrado_desde_smartpyme_MIGRATION_INDEX.md` | **ARCHIVO** | Índice del proceso de migración física | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/migrado_desde_smartpyme_DRIFT_REPORT.md` | **ARCHIVO** | Drift report de campos y base de datos | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/migrado_desde_smartpyme_MIGRACION_FISICA_FASE3.md` | **ARCHIVO** | Detalle técnico del traspaso físico | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/migrado_desde_smartpyme_REPORTE_CIERRE_FASE1.md` | **ARCHIVO** | Cierre técnico inicial | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/migrado_desde_smartpyme_ARQUEOLOGIA_FASE3.md` | **ARCHIVO** | Arqueología de lógica de negocio legacy | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/migrado_desde_smartpyme_formulas_CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md` | **ARCHIVO** | Resumen de fórmulas heredadas | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/migrado_desde_smartpyme_conversacional_CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md` | **ARCHIVO** | Estrategia de comercio conversacional | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/migrado_desde_smartpyme_catalogos_SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md` | **ARCHIVO** | Estructuración histórica de catálogos | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/migrado_desde_smartpyme_epistemologia_NOCION_001_ORGANISMO_PYME.md` | **ARCHIVO** | Noción histórica del organismo PyME | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.corpus_migrado.md` | **ARCHIVO** | Corpus bruto de diálogos históricos | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.MIGRACION_SMARTPYME_CONVERSACIONAL_v1.md` | **ARCHIVO** | Transición conversacional inicial | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.NORMATIVA_v1.md` | **ARCHIVO** | Reglas de normativas conversacionales antiguas | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md` | **ARCHIVO** | Histórico de primer contacto con cliente | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md` | **ARCHIVO** | Catálogos históricos de hipótesis | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md` | **ARCHIVO** | Fórmulas iniciales matematizadoras | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.ENSAMBLE_DOCUMENTAL_FASE1_v1.md` | **ARCHIVO** | Ensamblado de staging documental | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.MAPA_INTEGRACION_v1.md` | **ARCHIVO** | Jerarquías provisionales antiguas | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md` | **ARCHIVO** | Patologías iniciales del sistema | Arqueología | — | — | — | — | **Conservar histórica.** |
| `docs/ingenieria_conversacional.README.md` | **BORRAR_PROPUESTO** | Índice conversacional heredado redundante | Arqueología | — | — | `docs/DOCUMENTATION_INDEX.md` | — | **Proponer borrado en próximo cleanup.** |

---

## 2. Reglas del Gobierno Documental de PymIA

Para evitar que la biblioteca documental vuelva a sufrir un proceso de degradación o acumulación de ruido técnico, se fijan las siguientes normas estrictas:

1. **Soberanía del Índice**: Ningún documento nuevo puede ser creado sin ser incorporado inmediatamente a este índice (`docs/DOCUMENTATION_INDEX.md`).
2. **Ciclo de Vida Claro**: Todo documento nuevo debe nacer en estado `CANDIDATO` o `VIGENTE`. Al ser reemplazado por un diseño superador, debe transicionar de forma obligatoria a `SUPERADO` (si es contradicho) o `ARCHIVO` (si se conserva como memoria útil).
3. **No Duplicidad de Reglas**: Queda estrictamente prohibido duplicar o repartir reglas normativas de implementación del código entre documentos diferentes. La documentación normativa vigente debe ser auto-contenida e inequívoca.
4. **Vinculación con Código Productivo**: Los documentos de estado `VIGENTE` que describen contratos deben mapear 1-a-1 con archivos reales en el código del repositorio (como se muestra en la columna "Relación con Código" de la tabla general).
5. **No uso de Documentación No-Vigente**: Queda terminantemente prohibido guiar actividades de refactorización o codificación basándose en documentos clasificados como `SUPERADO`, `ARCHIVO` o `BORRAR_PROPUESTO`. Su uso para guiar código constituye un fallo técnico severo.
