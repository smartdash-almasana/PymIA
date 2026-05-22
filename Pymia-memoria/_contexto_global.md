# Contexto Global — PymIA / SmartPyme

## Estado

VIGENTE

## Propósito

Esta memoria preserva el contexto operativo mínimo para continuar el desarrollo de PymIA / SmartPyme sin pérdida de información entre agentes, sesiones o entornos.

## Identidad del producto

PymIA / SmartPyme no es un simple chatbot ni un parser de Excel.

El producto evoluciona hacia un sistema operativo de diagnóstico PyME basado en evidencia, conversación clínica-operacional, contratos explícitos y validación matemática.

## Dirección arquitectónica

La dirección vigente combina tres planos:

1. Clinical Conversation Runtime.
2. TenantClinicalContext como contrato obligatorio.
3. Document Intelligence local, auditable y gobernado.

## Pipeline conceptual objetivo

```text
síntoma
→ contexto
→ evidencia
→ interpretación documental
→ opacidad / FIO
→ diagnóstico
→ plan de acción
```

## Pipeline documental objetivo

```text
Adjunto Excel/CSV
→ AttachmentLifecycle
→ PreAudit local
→ lectura tabular
→ TenantClinicalContext
→ PymeColumnOntology
→ BusinessSchemaInferenceEngine
→ validación matemática relacional
→ SemanticSchema
→ FieldBinding
→ FIO si hay opacidad real
→ SchemaInferenceResult
→ EvidenceBundle enriquecido
→ Kernel PymIA
```

## Documentos normativos centrales

- `docs/DOCUMENTATION_INDEX.md`
- `docs/DEPRECATED_DOCS.md`
- `docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md`
- `docs/transient-design/TENANT_CLINICAL_CONTEXT_AND_DOCUMENT_INTELLIGENCE_DESIGN.md`
- `docs/transient-design/CONVERSATION_CLINICAL_RUNTIME_STRATEGIC_DIRECTION.md`
- `docs/prompts/PROMPT_MASTER_DOCUMENT_INTELLIGENCE_ENTERPRISE.md`
- `docs/prompts/PROMPT_PHASE1_DOCUMENT_INTELLIGENCE_ISOLATED.md`
- `docs/adr/ADR-004-bem-como-fallback-pasivo.md`
- `docs/adr/ADR-005-document-intelligence-engine.md`
- `docs/adr/ADR-006-tenant-clinical-context-as-input.md`
- `docs/adr/ADR-007-documentation-governance.md`

## Caso real obligatorio

Archivo de referencia:

```text
distribuidora_mayorista_compleja.xlsx
```

Columnas:

```text
fecha, cliente, ruta, sku, cantidad, venta, costo, margen
```

Resultado esperado:

- `fecha` → dimensión temporal.
- `cliente` → dimensión comercial.
- `ruta` → dimensión logística/comercial.
- `sku` → identificador producto.
- `cantidad` → cantidad canónica.
- `venta` → venta_total.
- `margen` → margen_bruto.
- `costo` → costo_total o costo_unitario según matemática.

## Regla crítica

El Excel no se interpreta aislado. Se interpreta contra contexto clínico-operacional del tenant.
