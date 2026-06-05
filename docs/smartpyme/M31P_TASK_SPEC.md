# M31-P — TaskSpec Pilotos asistidos reales

## Estado

READY_FOR_DOCUMENTAL_EXECUTION

## Task ID

```text
smartpyme.m31p.prepare_assisted_pilots
```

## Objetivo

Preparar la ejecución metodológica de M31-P sin tocar código productivo.

El objetivo es dejar definido cómo se registrarán, validarán y cerrarán 3 a 5 pilotos asistidos reales o realistas usando el protocolo M31.

## Capacidad relacionada

```text
smartpyme.m31p.assisted_pilot_validation
```

## Fuente

- `docs/adr/ADR-M31P-PILOTOS-ASISTIDOS.md`
- `docs/smartpyme/M31P_CAPABILITY_SPEC.md`
- `docs/smartpyme/M31P_PILOTOS_ASISTIDOS_PLAN.md`
- `docs/smartpyme/M31_CLOSURE_CLARIFICATION.md`
- `docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_CHECKPOINT.md`
- `docs/roadmap/ROADMAP_SERVICIO_ASISTIDO_EXCEL_SEMANTICA_PYME.md`
- `AGENTS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`

## Archivos permitidos

Sólo documentación SmartPyme/PymIA:

```text
docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md
docs/smartpyme/M31P_PILOT_VALIDATION_CHECKLIST.md
docs/smartpyme/M31P_CHECKPOINT.md
```

## Archivos de sólo lectura

```text
AGENTS.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
docs/pymia/START_HERE_FOR_AGENTS.md
docs/adr/ADR-M31P-PILOTOS-ASISTIDOS.md
docs/smartpyme/M31P_CAPABILITY_SPEC.md
docs/smartpyme/M31P_PILOTOS_ASISTIDOS_PLAN.md
docs/smartpyme/M31_CLOSURE_CLARIFICATION.md
docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_CHECKPOINT.md
docs/roadmap/ROADMAP_SERVICIO_ASISTIDO_EXCEL_SEMANTICA_PYME.md
```

## Archivos prohibidos

No tocar:

```text
pymia/**
conversa-engine/**
src/**
scripts/**
tests/**
landing/**
tools/**
pyproject.toml
pytest.ini
README.md
```

## Tareas permitidas

1. Crear plantilla de registro de piloto.
2. Crear checklist de validación de piloto.
3. Crear checkpoint M31-P inicial o de cierre, según evidencia disponible.
4. Documentar PASS / PARTIAL / BLOCKED de la fase.
5. Registrar explícitamente si todavía no hay pilotos ejecutados.

## Tareas prohibidas

- Implementar código.
- Crear tests de runtime.
- Modificar capacidades existentes.
- Abrir M32.
- Implementar Guided Evidence Recovery.
- Integrar ERP.
- Crear UI o PDF profesional.
- Declarar producto.
- Declarar autonomía.
- Convertir pilotos en LearningMemory automática.

## Plantilla mínima de piloto

Cada piloto debe registrarse con:

```yaml
pilot_id:
tenant_ref:
case_date:
business_type:
owner_problem_statement:
owner_operational_meaning:
received_evidence:
missing_evidence:
protocol_steps_applied:
output_delivered:
final_status:
execution_time_minutes:
human_intervention:
blockers:
candidate_learnings:
repeatability_assessment:
limitations:
```

## Validación documental mínima

Antes de ejecutar pilotos, validar que existen:

- ADR-M31P;
- CapabilitySpec M31-P;
- TaskSpec M31-P;
- plantilla de registro de piloto;
- checklist de validación.

## Criterio PASS de esta TaskSpec

Esta TaskSpec puede cerrar como PASS_DOCUMENTAL si:

- se crea plantilla de piloto;
- se crea checklist de validación;
- no se toca código productivo;
- no se abre M32;
- no se implementa Guided Evidence Recovery;
- se mantiene distinción entre PASS_DOCUMENTAL y PASS_OPERATIVO;
- se deja explícito que M31-P operativo sigue pendiente hasta tener pilotos reales.

## Criterio PARTIAL

Queda PARTIAL si:

- sólo se crea uno de los documentos requeridos;
- falta checklist o plantilla;
- no queda claro el criterio PASS/PARTIAL/BLOCKED;
- no queda claro que no se trata de producto.

## Criterio BLOCKED

Queda BLOCKED si:

- se requiere código para avanzar;
- no hay autorización documental suficiente;
- se intenta saltar a M32;
- se intenta declarar PASS_OPERATIVO sin pilotos;
- se intenta convertir evidencia en LearningMemory automática.

## Evidencia esperada

Para reportar cierre documental:

- archivos creados;
- commits o diffs;
- lectura de fuente;
- ausencia de cambios productivos;
- veredicto PASS_DOCUMENTAL / PARTIAL / BLOCKED.

## Resultado esperado inmediato

Después de esta TaskSpec, el siguiente paso es crear:

```text
docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md
docs/smartpyme/M31P_PILOT_VALIDATION_CHECKLIST.md
```

No ejecutar pilotos todavía si no hay casos disponibles.
