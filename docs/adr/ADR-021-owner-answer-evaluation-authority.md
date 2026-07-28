# ADR-021 — Owner Answer Evaluation Authority

## Status

ACCEPTED

## Fecha

2026-06-09

## Dueño conceptual

Kernel PymIA / Epistemic Boundary / Contract Governance

## Context

Después de M51, el repositorio ya puede representar respuestas explícitas del dueño PyME como un artefacto contractual separado:

```text
pregunta emitida
→ respuesta capturada
```

Sin embargo, todavía no existía autoridad documental para evaluar esa respuesta de forma estructurada sin mezclarla con:

```text
evidencia dura
≠ diagnóstico
≠ graph/state
≠ runtime
```

`AGENTS.md` exige mantener estas capas separadas y no declarar una respuesta como evidencia validada sin un frente metodológico explícito.

Antes de esta ADR, esa evaluación epistemológica no tenía contrato autorizado.

## Decision

Se autoriza `Owner Answer Evaluation` únicamente como futura capacidad contractual para evaluar un `OwnerAnswersBundle` y producir una salida estructurada.

La evaluación autorizada:

- no modifica diagnóstico;
- no recalcula fórmulas;
- no escribe evidencia dura;
- no consume graph/state/runtime;
- no verifica materialmente la verdad en este slice.

Su función permitida es:

```text
OwnerAnswersBundle
→ evaluación estructurada fail-closed
→ artefacto disponible para frentes futuros
```

## Allowed sources

Toda versión futura de `Owner Answer Evaluation` debe derivarse únicamente de artefactos existentes y trazables, por ejemplo:

- `OwnerAnswer`
- `OwnerAnswersBundle`
- `OwnerQuestion`
- `OwnerQuestionsBundle`
- referencias explícitas entre pregunta y respuesta

No puede derivarse de imports de runtime ni de efectos laterales externos.

## Mandatory rules

`Owner Answer Evaluation` debe:

- preservar trazabilidad hacia la respuesta origen;
- preservar vínculo con la pregunta asociada;
- modelar veredictos explícitos y fail-closed;
- permitir errores de validación y notas de revisión;
- permitir mapeo y normalización opcionales sin convertirlas en evidencia;
- representar `verified` sólo como estado contractual, no como verificación material real.

## Prohibited behaviors

Queda prohibido:

- escribir evidencia dura;
- recalcular diagnóstico;
- cambiar findings;
- tocar `graph`, `state` o runtime;
- inferir verdad operacional por heurística libre;
- abrir Telegram, Hermes, FastAPI, red o LLM;
- introducir `evidence_candidate` en este slice.

## Consequences

Desde esta ADR:

- M52 puede abrirse como frente de contrato y esquema puro;
- la evaluación de respuestas del dueño queda separada de evidencia validada;
- cualquier uso futuro de esta evaluación requerirá CapabilitySpec, ModuleContract, TaskSpec, tests y evidencia propios antes de declararse PASS.
