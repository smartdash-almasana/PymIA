# Prompts de Ingeniería — PymIA

## Estado

CANDIDATO

## Propósito

Índice operativo de prompts normativos y ejecutables derivados de la gobernanza documental de PymIA.

Este directorio no reemplaza `docs/DOCUMENTATION_INDEX.md`; funciona como índice local de prompts. Todo prompt que pase a guiar implementación debe quedar también registrado en el índice canónico de gobernanza documental.

## Prompts disponibles

| Documento | Estado | Uso |
|---|---|---|
| `PROMPT_MASTER_DOCUMENT_INTELLIGENCE_ENTERPRISE.md` | BLUEPRINT_ENTERPRISE | Prompt maestro de refactorización enterprise. No ejecutar de forma monolítica. Usar para derivar fases. |
| `PROMPT_PHASE1_DOCUMENT_INTELLIGENCE_ISOLATED.md` | EJECUTABLE_FASE_1 | Prompt quirúrgico para implementar contratos + módulo aislado `pymia/document_intelligence/` + tests unitarios, sin integración runtime. |

## Regla operativa

El prompt maestro conserva el diseño completo.

La implementación se ejecuta por fases pequeñas:

1. Fase 1 — contratos + módulo aislado + tests.
2. Fase 2 — ontología + validación matemática + FIO.
3. Fase 3 — integración runtime.
4. Fase 4 — E2E Telegram.

## Restricción

No usar ningún prompt de este directorio para modificar código sin leer antes:

- `docs/DOCUMENTATION_INDEX.md`
- `docs/DEPRECATED_DOCS.md`
- `docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md`
- `docs/transient-design/TENANT_CLINICAL_CONTEXT_AND_DOCUMENT_INTELLIGENCE_DESIGN.md`
- ADR-004, ADR-005, ADR-006 y ADR-007.
