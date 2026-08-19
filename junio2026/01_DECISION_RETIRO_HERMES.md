# 01 — Decisión de retiro total de Hermes

## Decisión

Hermes debe desaparecer de PymIA.

No se usará Hermes como:

- agente LLM;
- runtime;
- orchestrator;
- gateway activo;
- wrapper conversacional;
- canal oficial;
- marca técnica;
- entidad arquitectónica;
- dependencia del pipeline;
- requisito para adjuntos/evidencia;
- nombre de tests nuevos;
- fuente rectora documental.

## Cambio respecto de documentos previos

Cualquier documento que trate Hermes como runtime/orchestrator activo queda obsoleto en esa parte.

En particular, una instrucción como:

```text
Hermes opera como runtime/orchestrator capaz
```

debe considerarse inválida para el estado vigente.

La intención funcional que pudiera haber detrás —por ejemplo intake conversacional, recepción de adjuntos, ciclo de evidencia o devolución segura al dueño— puede preservarse, pero debe expresarse con contratos neutrales, no bajo Hermes.

## Criterio de clasificación

Toda referencia a Hermes debe entrar en una de estas categorías:

| Categoría | Acción |
|---|---|
| Código runtime activo | eliminar o reemplazar por interfaz neutral |
| Tests de Hermes | borrar, migrar o reescribir contra contratos neutrales |
| Documentación histórica | mover/confirmar en museo |
| Documentación actual que lo activa | corregir o invalidar explícitamente |
| README/guardrails que lo mencionan como posible interfaz | reemplazar por “interfaz conversacional neutral” |
| Subcarpetas `docs/hermes`, `tests/hermes`, `pymia/hermes` | plan de retiro explícito |

## Reemplazos conceptuales permitidos

No reemplazar Hermes por otro nombre-agente. Reemplazar por límites funcionales:

```text
ConversationalInterface
AttachmentIntake
EvidenceBundle
OwnerInteractionBoundary
KernelInputContract
SafeOwnerResponse
HumanReviewGate
```

El objetivo no es crear “Hermes 2”. El objetivo es eliminar la dependencia mental y técnica de un agente soberano.

## Evidencia observada

Se detectaron:

```text
309 archivos con referencias a Hermes/hermes/HERMES
2495 referencias textuales totales
```

Archivos con mayor concentración de referencias:

```text
docs/DOCUMENTATION_INDEX.md
docs/arquitectura/HERMES_SM1_SM2_ISOLATED_VALIDATION_PLAN.md
tests/hermes/test_hermes_adapter.py
docs/arquitectura/HERMES_OPERATIONAL_VERIFICATION.md
pymia/hermes/adapter.py
docs/hermes/*
conversa-engine/HERMES_AGENT_OPERATIONS.md
ARCHITECTURE_GUARDRAILS.md
README.md
task.md
```

## Política de auditoría futura

Toda propuesta de otro LLM que use Hermes como pieza activa debe marcarse como incorrecta.

Se permiten propuestas que digan:

```text
Eliminar Hermes.
Migrar intención funcional a contratos neutrales.
Aislar documentación histórica.
Romper dependencias activas.
Corregir tests que dependan de Hermes.
```

No se permiten propuestas que digan:

```text
Reactivar Hermes.
Conservar Hermes como orchestrator.
Usar Hermes como agente LLM.
Tratar Hermes como gateway necesario.
Agregar funcionalidades a pymia/hermes.
Crear nuevos tests bajo tests/hermes.
```

## Criterio de done para esta decisión

La decisión se considera aplicada cuando:

1. `docs/current/` no menciona Hermes como activo.
2. `README.md` no presenta Hermes como interfaz futura.
3. `ARCHITECTURE_GUARDRAILS.md` no contiene un `HERMES_BOUNDARY` vigente.
4. `task.md` deja de pedir modificaciones en `pymia/hermes/*`.
5. `pymia/hermes/` está eliminado, archivado o aislado como legacy sin imports productivos.
6. `tests/hermes/` está eliminado, migrado o marcado fuera de suite viva.
7. `conversa-engine/` no es fuente rectora.
8. La suite viva no depende de símbolos Hermes.
9. Cualquier intake conversacional se expresa con contratos neutrales.
