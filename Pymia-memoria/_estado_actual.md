# Estado Actual — PymIA / SmartPyme

## Estado

DOCUMENTACION_NORMATIVA_CERRADA__FASE_1_DOCUMENT_INTELLIGENCE_PENDIENTE

## Situación actual

La gobernanza documental quedó formalizada en el repo.

Se crearon y registraron documentos estratégicos, ADRs y prompts para avanzar sin pérdida de información.

## Trabajo ya realizado

- BEM fue degradado a fallback pasivo.
- Hermes quedó definido como runtime/orquestador, no como intérprete de columnas.
- TenantClinicalContext quedó fijado como contrato obligatorio del motor documental.
- Clinical Conversation Runtime quedó documentado como dirección estratégica.
- El prompt maestro Document Intelligence Enterprise quedó guardado como blueprint.
- El prompt Fase 1 quedó derivado como instrucción ejecutable.
- `DOCUMENTATION_INDEX.md` fue actualizado para registrar prompts y diseños transitorios.

## Próxima tarea activa

Ejecutar Fase 1:

```text
contratos + pymia/document_intelligence aislado + tests unitarios
```

Prompt fuente:

```text
docs/prompts/PROMPT_PHASE1_DOCUMENT_INTELLIGENCE_ISOLATED.md
```

## Restricción inmediata

No integrar runtime todavía.

No tocar:

- Hermes.
- Telegram.
- `conversa-engine/document_intake.py`.
- `conversa-engine/operational_audit_runner.py`.
- `tools/excel_evidence.py`.
- `tools/document_ingestion.py`.
- `pymia/contracts/evidence_v1.py`.
- `pymia/contracts/attachment_lifecycle_v1.py`.

## Estado de GitHub

Los documentos nuevos fueron creados directamente en `main` mediante conector GitHub.

La PC local debe hacer:

```bash
git pull origin main
```

antes de ejecutar cualquier fase de implementación.
