# ADR-019 — Guided Evidence Recovery Authority

## Status

ACCEPTED

## Fecha

2026-06-09

## Dueño conceptual

Kernel PymIA / Evidence Boundary / Contract Governance

## Context

Después de M35, M36, M37, M38, M39, M40, M41, M42, M43 y M44, el repositorio ya puede:

```text
registrar evidencia
→ evaluar sufficiency / readiness
→ detectar faltantes
→ producir artefactos soberanos
→ traducir owner-facing controlado
→ hacer visible un summary trazable
```

Sin embargo, cuando el circuito queda bloqueado por evidencia faltante o por ausencia de sentido operativo suficiente, el sistema todavía no tiene una autoridad canónica para abrir una recuperación guiada y gobernada frente al dueño PyME.

El `AGENTS.md` ya establece que, si falta evidencia o sentido operativo, el estado correcto no es silencio sino `GAP`, `BLOCKED`, `NEEDS_EVIDENCE` o stop metodológico. También advierte explícitamente que Guided Evidence Recovery no debía implementarse sin una futura cadena formal de:

```text
ADR
→ CapabilitySpec
→ ModuleContract
→ TaskSpec
→ tests
→ evidence
```

Antes de esta ADR, esa autoridad todavía no existía.

## Decision

Se autoriza `Guided Evidence Recovery` únicamente como futura capacidad gobernada para pedir al dueño PyME:

- evidencia faltante;
- aclaración semántica de columnas, períodos o procesos;
- sentido operativo faltante para interpretar correctamente un archivo o un bloqueo ya detectado.

La capacidad autorizada no es diagnóstica.

Su función permitida es:

```text
detectar faltantes ya trazados
→ proyectar pedido controlado de evidencia o sentido operativo
→ mantener el caso dentro de una frontera fail-closed
```

## Allowed sources

Toda versión futura de `Guided Evidence Recovery` debe derivarse únicamente de artefactos existentes y trazables, por ejemplo:

- `OperationalAuditResult`
- `RenderContract`
- `OwnerFacingReport`
- `DeliveryPackage`
- `missing_evidence`
- `next_questions`
- `blocked_message`
- `EvidenceGateDecision`
- `FormulaInputGateResult`
- intake/evidence ya registrados

No puede inferir datos ausentes desde fuentes no registradas ni expandir conclusiones fuera de esos artefactos.

## Mandatory rules

`Guided Evidence Recovery` debe:

- preservar el estado real del circuito;
- pedir evidencia faltante o sentido operativo faltante de forma explícita;
- distinguir evidencia ausente de interpretación ausente;
- mantener trazabilidad hacia el artefacto que originó el bloqueo o gap;
- fallar en cerrado si no existe base trazable suficiente para pedir algo al dueño;
- operar como capacidad asistida y gobernada, no como diagnóstico autónomo.

## Prohibited behaviors

Queda prohibido:

- inventar evidencia;
- inventar valores, variables o columnas;
- completar datos faltantes por heurística no autorizada;
- crear findings nuevos;
- cambiar diagnóstico;
- confirmar estados candidatos;
- abrir Telegram, Hermes, FastAPI o canal productivo por esta ADR;
- generar narrativa libre no trazable;
- convertir una pregunta operativa en una conclusión clínica/operacional.

## Consequences

Desde esta ADR:

- M45 puede abrirse como frente documental de autorización para `Guided Evidence Recovery`;
- la recuperación guiada queda subordinada a artefactos soberanos ya emitidos;
- la capacidad puede pedir evidencia o sentido operativo faltante, pero no producir diagnóstico nuevo;
- cualquier implementación futura requerirá CapabilitySpec, ModuleContract, TaskSpec, tests y evidencia propios antes de declararse cerrada.
