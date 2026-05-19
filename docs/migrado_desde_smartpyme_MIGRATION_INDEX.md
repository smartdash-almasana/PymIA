# MIGRATION_INDEX.md

Índice de migración documental desde SmartPyme hacia PymIA.

Fase 1: Solo documentación - Preservación y clasificación.

## Formato de entrada

* **origen**: Ruta original en SmartPyme/
* **destino**: Ruta destino en PymIA/docs/migrado_desde_smartpyme/
* **categoria**: conversacional | epistemologia | catalogos | patologias | taxonomias | formulas | memoria_historica
* **resumen_1_linea**: Descripción breve del contenido
* **prioridad**: alta | media | baja
* **riesgo_drift**: bajo | medio | alto

---

## Entradas migradas

### Fase 1

#### conversacional

* **origen**: SmartPyme/docs/architecture/CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/conversacional/CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md
* **categoria**: conversacional
* **resumen_1_linea**: Estrategia de comercio conversacional multiusuario: microservicios puntuales, bot como canal comercial, y soporte para múltiples roles dentro de un mismo tenant con trazabilidad auditable.
* **prioridad**: alta
* **riesgo_drift**: bajo

#### epistemologia

* **origen**: SmartPyme/docs/nociones_conceptuales/NOCION_001_ORGANISMO_PYME.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/epistemologia/NOCION_001_ORGANISMO_PYME.md
* **categoria**: epistemologia
* **resumen_1_linea**: Noción fundacional: la PyME como organismo incompleto donde el dueño es variable dinámica y SmartPyme acompaña la toma de decisiones con coherencia operativa, no exactitud absoluta.
* **prioridad**: alta
* **riesgo_drift**: bajo

#### catalogos

* **origen**: SmartPyme/docs/architecture/SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/catalogos/SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
* **categoria**: catalogos
* **resumen_1_linea**: Diseño conceptual del catálogo clínico-operativo PyME: traducción de dolor del dueño a síntoma, patologías posibles, hipótesis investigable, skills candidatas y evidencia requerida.
* **prioridad**: alta
* **riesgo_drift**: medio

#### formulas

* **origen**: SmartPyme/docs/architecture/CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/formulas/CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md
* **categoria**: formulas
* **resumen_1_linea**: Kernel matemático clínico: motor de reducción dirigida de incertidumbre con pipeline cognitivo (narrativa→hipótesis→fórmulas→evidencia→cálculo) y axiomas de trazabilidad, DAG fisiológico y estado INSUFFICIENT_DATA.
* **prioridad**: alta
* **riesgo_drift**: medio

---

## Fase 3 — Entradas Identificadas para Migración Física

### conversacional

* **origen**: SmartPyme/docs/architecture/CONVERSATIONAL_METHODS.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/conversacional/CONVERSATIONAL_METHODS.md
* **categoria**: conversacional
* **resumen_1_linea**: Métodos conversacionales: mayéutica externa con dueño + método hipotético-deductivo interno del sistema.
* **prioridad**: alta
* **riesgo_drift**: medio (terminología findings/hallazgos)

* **origen**: SmartPyme/docs/hermes-producto/PROTOCOLO_ANAMNESIS_MVP.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/conversacional/PROTOCOLO_ANAMNESIS_MVP.md
* **categoria**: conversacional
* **resumen_1_linea**: Protocolo operativo de anamnesis para MVP: preguntas estructuradas para formulación clara de demanda.
* **prioridad**: alta
* **riesgo_drift**: bajo

### epistemologia

* **origen**: SmartPyme/docs/architecture/HYPOTHETICO_DEDUCTIVE_METHOD.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/epistemologia/HYPOTHETICO_DEDUCTIVE_METHOD.md
* **categoria**: epistemologia
* **resumen_1_linea**: Método científico aplicado a diagnóstico PyME: hipótesis verificable → evidencia → contraste → diagnóstico.
* **prioridad**: alta
* **riesgo_drift**: bajo

* **origen**: SmartPyme/docs/architecture/KNOWLEDGE_RESEARCH_AND_CASE_LAYER.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/epistemologia/KNOWLEDGE_RESEARCH_AND_CASE_LAYER.md
* **categoria**: epistemologia
* **resumen_1_linea**: Capa de investigación y casos: vinculación de evidencia con hipótesis para construcción de OperationalCase.
* **prioridad**: alta
* **riesgo_drift**: bajo

### patologias

* **origen**: SmartPyme/docs/architecture/PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/patologias/PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md
* **categoria**: patologias
* **resumen_1_linea**: Catálogo de modelos operativos y síntomas PyME: mapeo de dolores a patologías investigables.
* **prioridad**: alta
* **riesgo_drift**: bajo

* **origen**: SmartPyme/docs/architecture/PYME_SYMPTOM_PATHOLOGY_ATLAS.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/patologias/PYME_SYMPTOM_PATHOLOGY_ATLAS.md
* **categoria**: patologias
* **resumen_1_linea**: Atlas de síntomas y patologías: flujo semántico diagnóstico desde dolor expresado hasta evidencia requerida.
* **prioridad**: alta
* **riesgo_drift**: bajo

* **origen**: SmartPyme/docs/architecture/SMARTPYME_TANQUES_CONOCIMIENTO_FISIOLOGIA_PATOLOGIAS.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/patologias/SMARTPYME_TANQUES_CONOCIMIENTO_FISIOLOGIA_PATOLOGIAS.md
* **categoria**: patologias
* **resumen_1_linea**: Documento maestro de fisiología/patologías PyME: base conceptual para Knowledge Tanks sectoriales.
* **prioridad**: alta
* **riesgo_drift**: medio (Knowledge Tank/Tanque de Conocimiento)

### taxonomias

* **origen**: SmartPyme/docs/architecture/DOMAIN_PACK_ARCHITECTURE.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/taxonomias/DOMAIN_PACK_ARCHITECTURE.md
* **categoria**: taxonomias
* **resumen_1_linea**: Arquitectura de Domain Packs: estructura modular del conocimiento por rubro y función transversal.
* **prioridad**: alta
* **riesgo_drift**: medio (Domain Pack/Paquete de Dominio)

* **origen**: SmartPyme/docs/architecture/DOMAIN_CLASSIFICATION_2026-05-12.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/taxonomias/DOMAIN_CLASSIFICATION_2026-05-12.md
* **categoria**: taxonomias
* **resumen_1_linea**: Clasificación de dominios por fecha: snapshot de taxonomía operativa para trazabilidad temporal.
* **prioridad**: alta
* **riesgo_drift**: bajo

### formulas

* **origen**: SmartPyme/app/catalogs/formulas_smartpyme_v0.json
* **destino**: PymIA/docs/migrado_desde_smartpyme/formulas/formulas_smartpyme_v0.json
* **categoria**: formulas
* **resumen_1_linea**: Catálogo operativo de 95+ fórmulas financieras: margen, cashflow, stock, DSO/DPO, pricing.
* **prioridad**: alta
* **riesgo_drift**: medio (JSON vs Markdown, inglés/castellano)

* **origen**: SmartPyme/docs/architecture/KNOWLEDGE_TANKS_ARCHITECTURE.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/formulas/KNOWLEDGE_TANKS_ARCHITECTURE.md
* **categoria**: formulas
* **resumen_1_linea**: Arquitectura de Knowledge Tanks: especificación de fórmulas por tanque sectorial y transversal.
* **prioridad**: media
* **riesgo_drift**: medio (Knowledge Tank/Tanque)

### domain_packs

* **origen**: SmartPyme/docs/architecture/SMARTPYME_ARCHITECTURE_MASTER.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/domain_packs/SMARTPYME_ARCHITECTURE_MASTER.md
* **categoria**: domain_packs
* **resumen_1_linea**: Documento maestro de arquitectura: definición de Core vs Domain Packs vs Knowledge Tanks.
* **prioridad**: alta
* **riesgo_drift**: bajo

* **origen**: SmartPyme/docs/architecture/SPECIFIC_KNOWLEDGE_TANKS_AND_SOURCE_ENGINE.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/domain_packs/SPECIFIC_KNOWLEDGE_TANKS_AND_SOURCE_ENGINE.md
* **categoria**: domain_packs
* **resumen_1_linea**: Especificación de tanques sectoriales y transversales: fuentes, ingesta y actualización de conocimiento.
* **prioridad**: media
* **riesgo_drift**: bajo

* **origen**: SmartPyme/docs/architecture/EXTERNAL_KNOWLEDGE_INTAKE_ENGINE.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/domain_packs/EXTERNAL_KNOWLEDGE_INTAKE_ENGINE.md
* **categoria**: domain_packs
* **resumen_1_linea**: Motor de ingesta de conocimiento externo: integración de fuentes sectoriales y normativas.
* **prioridad**: media
* **riesgo_drift**: bajo

### memoria_historica

* **origen**: SmartPyme/docs/ARCHIVO_LEGACY.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/memoria_historica/ARCHIVO_LEGACY.md
* **categoria**: memoria_historica
* **resumen_1_linea**: Índice de documentos legacy y deprecables: trazabilidad de evolución arquitectónica.
* **prioridad**: media
* **riesgo_drift**: bajo

* **origen**: SmartPyme/docs/archive/smarttimes_full_architecture.md
* **destino**: PymIA/docs/migrado_desde_smartpyme/memoria_historica/smarttimes_full_architecture.md
* **categoria**: memoria_historica
* **resumen_1_linea**: Arquitectura histórica completa: valor de referencia para evolución del sistema.
* **prioridad**: baja
* **riesgo_drift**: bajo

---

> **Nota Fase 3**: Estas entradas representan documentos identificados y localizados. La copia física a destino está pendiente de resolución de limitaciones técnicas de herramientas de escritura en subdirectorios anidados. Ver `MIGRACION_FISICA_FASE3.md` para detalle completo.