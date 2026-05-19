# Ensamble documental fase 1 — SmartPyme → PymIA

## Estado

Documento de trabajo para conectar el staging documental migrado desde SmartPyme con la normativa viva de PymIA.

## Alcance

Esta fase no toca runtime.

Solo ordena:

- documentación migrada;
- ingeniería conversacional;
- catálogos;
- fórmulas;
- drift pendiente.

## Staging recibido

Índice:

```text
docs/migrado_desde_smartpyme_MIGRATION_INDEX.md
```

Drift:

```text
docs/migrado_desde_smartpyme_DRIFT_REPORT.md
```

Documentos migrados principales:

```text
docs/migrado_desde_smartpyme_conversacional_CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md
docs/migrado_desde_smartpyme_epistemologia_NOCION_001_ORGANISMO_PYME.md
docs/migrado_desde_smartpyme_catalogos_SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
docs/migrado_desde_smartpyme_formulas_CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md
```

## Decisión de ensamble

### Conversacional

Fuente migrada:

```text
CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md
```

Se integra como memoria de soporte para:

```text
docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md
docs/ingenieria_conversacional.NORMATIVA_v1.md
```

No gobierna runtime directamente hasta depuración.

### Epistemología

Fuente migrada:

```text
NOCION_001_ORGANISMO_PYME.md
```

Se integra como fundamento conceptual de:

```text
docs/fundamentos/organismo-pyme.md
docs/epistemologia/modelo-verdad-soberania.md
```

### Catálogos

Fuente migrada:

```text
SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
```

Se integra como fundamento de:

```text
docs/ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md
docs/pathology_catalog.v1.json
```

### Fórmulas

Fuente migrada:

```text
CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md
```

Se integra como fundamento de:

```text
docs/ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md
```

## Drift pendiente

Tomado de:

```text
docs/migrado_desde_smartpyme_DRIFT_REPORT.md
```

Pendientes:

1. normalizar `findings` vs `hallazgos`;
2. definir política inglés/castellano para términos técnicos;
3. decidir serialización final de catálogos: YAML conceptual, JSON, Pydantic o combinación.

## Jerarquía de uso

La documentación migrada funciona como memoria histórica y soporte.

La normativa viva sigue siendo:

```text
docs/ingenieria_conversacional.NORMATIVA_v1.md
docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md
docs/ingenieria_conversacional.MAPA_INTEGRACION_v1.md
docs/ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md
docs/ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md
docs/pathology_catalog.v1.json
```

## Cierre parcial agente Qwen

La migración documental fase 1 quedó completada parcialmente con 4 documentos migrados:

```text
CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md
NOCION_001_ORGANISMO_PYME.md
SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md
```

Reglas respetadas:

```text
no runtime
no código
no services
no tests
no Telegram
no canonización prematura
```

Pendientes detectados para fase 2:

```text
CONVERSATIONAL_METHODS.md
PROTOCOLO_ANAMNESIS_MVP.md
HYPOTHETICO_DEDUCTIVE_METHOD.md
KNOWLEDGE_RESEARCH_AND_CASE_LAYER.md
PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md
SMARTPYME_TANQUES_CONOCIMIENTO_FISIOLOGIA_PATOLOGIAS.md
PYME_SYMPTOM_PATHOLOGY_ATLAS.md
DOMAIN_CLASSIFICATION_2026-05-12.md
DOMAIN_PACK_ARCHITECTURE.md
ARCHIVO_LEGACY.md
archive/smarttimes_full_architecture.md
```

## Próximo paso

1. migrar documentos pendientes de fase 2;
2. completar `formula_catalog.v1.json`;
3. crear schema para `pathology_catalog.v1.json`;
4. decidir loader Python futuro;
5. no tocar Telegram hasta cerrar catálogos y normativa.
