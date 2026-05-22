# Prompt Maestro — Document Intelligence Enterprise Blueprint

## Estado

BLUEPRINT_ENTERPRISE

## Propósito

Este documento conserva el prompt maestro de refactorización enterprise para el subsistema Document Intelligence de PymIA/SmartPyme.

No debe ejecutarse como una única tarea monolítica. Su función es servir como blueprint rector para derivar prompts quirúrgicos por fase.

## Decisión operativa

El refactor completo se divide en fases controladas:

```text
Fase 1: contratos + módulo document_intelligence aislado + tests unitarios
Fase 2: PymeColumnOntology + validación matemática + FIO
Fase 3: integración con document_intake / EvidenceBundle / matcher
Fase 4: E2E Telegram con distribuidora_mayorista_compleja.xlsx
```

## Veredicto sobre el prompt maestro original

El prompt maestro original tiene:

- alta cobertura conceptual;
- alta cobertura enterprise;
- buena preservación de restricciones duras;
- buena trazabilidad documental;
- buen énfasis en TenantClinicalContext;
- buena separación Hermes / Document Intelligence;
- buena protección de AttachmentLifecycle y EvidenceBundle;
- buena definición de pruebas obligatorias;
- buen control contra BEM como ruta principal.

Pero tiene un riesgo operativo alto si se ejecuta completo de una sola vez, porque combina:

- auditoría completa del repo;
- creación de contratos;
- creación de módulo nuevo;
- loader tabular;
- ontología;
- motor de inferencia;
- validación matemática;
- FIO;
- integración runtime;
- matcher;
- anamnesis;
- Telegram;
- pytest completo;
- E2E.

Por eso queda guardado como blueprint y no como instrucción de ejecución directa.

## Principios del blueprint

### 1. Documentación normativa primero

Todo agente debe leer:

- `docs/DOCUMENTATION_INDEX.md`
- `docs/DEPRECATED_DOCS.md`
- `docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md`
- `docs/transient-design/TENANT_CLINICAL_CONTEXT_AND_DOCUMENT_INTELLIGENCE_DESIGN.md`
- `docs/transient-design/CONVERSATION_CLINICAL_RUNTIME_STRATEGIC_DIRECTION.md`
- `docs/adr/ADR-004-bem-como-fallback-pasivo.md`
- `docs/adr/ADR-005-document-intelligence-engine.md`
- `docs/adr/ADR-006-tenant-clinical-context-as-input.md`
- `docs/adr/ADR-007-documentation-governance.md`

Documentos marcados como `SUPERADO`, `ARCHIVO` o `BORRAR_PROPUESTO` no pueden guiar implementación.

### 2. Restricciones duras

- Hermes no interpreta columnas.
- Telegram no se rompe.
- AttachmentLifecycle se preserva.
- EvidenceBundle se preserva.
- tenant_id no se pierde.
- Estado obligatorio no vive sólo en metadata opaca.
- Sin TenantClinicalContext mínimo no hay inferencia financiera crítica.
- BEM no es ruta principal.
- Costo total vs costo unitario se resuelve por matemática, no por nombre.
- Benchmark se bloquea si la confianza del schema no alcanza.

### 3. Arquitectura objetivo

```text
Adjunto Excel/CSV
→ AttachmentLifecycle
→ PreAudit local
→ lectura tabular
→ motor tabular local
→ TenantClinicalContext
→ PymeColumnOntology
→ BusinessSchemaInferenceEngine
→ validación matemática relacional
→ SemanticSchema
→ FieldBinding
→ FIO si hay opacidad real
→ SchemaInferenceResult
→ EvidenceBundle enriquecido
→ matcher de evidencia
→ kernel PymIA
```

### 4. Contratos objetivo

- TenantClinicalContext
- BusinessIdentity
- OperationalProfile
- ClinicalHypothesis
- ActivePathology
- FormulaContext
- EvidencePlan
- TenantVocabulary
- HistoricalColumnMapping
- ContextConfidencePolicy
- SemanticSchema
- FieldBinding
- ColumnRole
- BusinessVariable
- ConfidenceScore
- AmbiguityStatus
- EvidenceQuality
- FichaInformativaOpacidad
- MathematicalConsistencyCheck
- SchemaInferenceResult

### 5. Caso real obligatorio

Archivo:

```text
distribuidora_mayorista_compleja.xlsx
```

Columnas:

```text
fecha, cliente, ruta, sku, cantidad, venta, costo, margen
```

Contexto:

```text
rubro = distribuidora mayorista
business_model = distribución
active_pathologies = rentabilidad_incierta / margen_bajo
formula_context = ventas_total, costos_total, margen_bruto
has_routes = true
sells_products = true
manages_stock = true
```

Resultado esperado:

- `fecha` → dimensión temporal.
- `cliente` → dimensión comercial.
- `ruta` → dimensión logística/comercial.
- `sku` → identificador producto.
- `cantidad` → cantidad canónica, no ambigua si es numérica.
- `venta` → venta_total.
- `margen` → margen_bruto.
- `costo` → costo_total o costo_unitario según validación matemática.

Reglas:

```text
venta - costo ≈ margen              → costo_total
venta - cantidad * costo ≈ margen   → costo_unitario
ninguna ecuación cierra             → FIO específica y benchmark bloqueado
```

### 6. FIO

FIO es el único origen válido de preguntas al dueño ante opacidad real.

Prohibido:

```text
Indicá qué columnas son ventas/costos.
```

Correcto:

```text
La columna costo puede representar costo total o costo unitario. Las ecuaciones disponibles no cierran con suficiente confianza. Confirmá si costo está expresado por unidad o por línea.
```

## Uso correcto de este blueprint

No ejecutar este blueprint entero.

Derivar prompts por fase:

1. `PROMPT_PHASE1_DOCUMENT_INTELLIGENCE_ISOLATED.md`
2. prompt Fase 2: ontología + matemática + FIO
3. prompt Fase 3: integración runtime
4. prompt Fase 4: E2E Telegram

## Criterio de éxito global

El producto evoluciona de parser de Excel a sistema operativo de diagnóstico PyME basado en evidencia, con contratos explícitos, trazabilidad, contexto clínico-operacional, validación matemática y bloqueo seguro ante incertidumbre.
