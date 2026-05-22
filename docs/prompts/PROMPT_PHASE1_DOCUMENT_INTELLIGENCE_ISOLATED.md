# Prompt Fase 1 — Document Intelligence Aislado

## Estado

EJECUTABLE_FASE_1

## Propósito

Prompt quirúrgico para implementar sólo la primera fase del refactor Document Intelligence.

Esta fase crea contratos, módulo aislado y tests unitarios. No integra runtime productivo.

---

```xml
<task>
Actuá como agente senior de refactor Python backend.

Tu tarea es implementar la Fase 1 del subsistema `pymia/document_intelligence/`: contratos tipados, módulo aislado y tests unitarios mínimos.

No integres todavía con Hermes, Telegram, document_intake, operational_audit_runner, EvidenceBundle runtime, matcher ni kernel productivo.
</task>

<contexto_obligatorio>
Antes de tocar código, leer:

1. docs/DOCUMENTATION_INDEX.md
2. docs/DEPRECATED_DOCS.md
3. docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md
4. docs/transient-design/TENANT_CLINICAL_CONTEXT_AND_DOCUMENT_INTELLIGENCE_DESIGN.md
5. docs/prompts/PROMPT_MASTER_DOCUMENT_INTELLIGENCE_ENTERPRISE.md
6. docs/adr/ADR-004-bem-como-fallback-pasivo.md
7. docs/adr/ADR-005-document-intelligence-engine.md
8. docs/adr/ADR-006-tenant-clinical-context-as-input.md
9. docs/adr/ADR-007-documentation-governance.md

No uses documentos marcados como SUPERADO, ARCHIVO o BORRAR_PROPUESTO para guiar implementación.
</contexto_obligatorio>

<alcance_estricto>
Implementar únicamente:

1. estructura `pymia/document_intelligence/`;
2. contratos tipados;
3. skeleton funcional de `SchemaInferenceResult`;
4. skeleton mínimo de FIO;
5. tests unitarios de importación, validación básica y bloqueo sin TenantClinicalContext;
6. documentación mínima en docstrings.

Prohibido en esta fase:

- modificar Hermes;
- modificar Telegram;
- modificar `conversa-engine/document_intake.py`;
- modificar `conversa-engine/operational_audit_runner.py`;
- modificar `tools/excel_evidence.py`;
- modificar `tools/document_ingestion.py`;
- modificar `pymia/contracts/evidence_v1.py`;
- modificar `pymia/contracts/attachment_lifecycle_v1.py`;
- invocar BEM;
- implementar integración runtime;
- hacer refactor masivo.
</alcance_estricto>

<estructura_a_crear>
Crear:

pymia/document_intelligence/
  __init__.py
  contracts/
    __init__.py
    tenant_clinical_context.py
    semantic_schema.py
    field_binding.py
    fio.py
    schema_inference_result.py
  inference/
    __init__.py
    schema_inference_engine.py
</estructura_a_crear>

<contratos_minimos>
Implementar con Pydantic si el repo ya usa Pydantic. Si no, usar dataclasses tipadas.

Contratos mínimos:

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

Todos deben importar sin error.
Todos deben tener typing explícito.
Todos deben tener docstring corto de semántica de negocio.
</contratos_minimos>

<reglas_fase_1>
1. `TenantClinicalContext` debe tener método o propiedad para validar contexto mínimo.
2. `SchemaInferenceEngine` debe rechazar inferencia si `TenantClinicalContext` es None o inválido.
3. El rechazo no debe romper runtime; debe devolver error contractual o excepción específica del módulo.
4. `SchemaInferenceResult.can_run_benchmark` debe ser False si falta contexto.
5. No implementar todavía matemática completa de costo.
6. No implementar todavía PymeColumnOntology completa.
7. No tocar lifecycle existente.
</reglas_fase_1>

<tests_obligatorios_fase_1>
Crear tests en:

`tests/document_intelligence/`

Tests mínimos:

1. `test_contracts_import_without_error`
2. `test_tenant_clinical_context_minimum_valid`
3. `test_tenant_clinical_context_minimum_invalid_without_business_identity`
4. `test_schema_inference_blocks_without_tenant_context`
5. `test_schema_inference_result_blocks_benchmark_when_context_missing`
6. `test_fio_contract_requires_specific_owner_question`
7. `test_field_binding_exposes_confidence_and_ambiguity_status`
8. `test_semantic_schema_exposes_global_confidence_and_evidence_quality`

Ejecutar:

```bash
pytest tests/document_intelligence --tb=short -q
```

Después ejecutar, si es viable:

```bash
pytest --tb=short -q
```
</tests_obligatorios_fase_1>

<criterios_pass>
PASS si:

- existe `pymia/document_intelligence/`;
- todos los contratos importan;
- los tests nuevos pasan;
- no se tocó Hermes;
- no se tocó Telegram;
- no se tocó document_intake;
- no se tocó operational_audit_runner;
- no se rompió AttachmentLifecycle;
- no se hizo integración runtime prematura.
</criterios_pass>

<criterios_fail>
FAIL si:

- se modifica runtime productivo;
- se usa BEM;
- se intenta resolver todo el refactor completo;
- falta TenantClinicalContext;
- no hay tests;
- los contratos no importan;
- se esconde estado obligatorio sólo en metadata opaca.
</criterios_fail>

<formato_salida>
Devolver:

# Reporte Fase 1 — Document Intelligence Aislado

## Estado
PASS / PARTIAL / FAIL

## Archivos creados

## Archivos modificados

## Contratos implementados

## Tests agregados

## Comandos ejecutados

## Resultado de pytest

## Confirmación de no integración runtime

## Riesgos residuales

## Próximo paso único
</formato_salida>

<analisis>
```
