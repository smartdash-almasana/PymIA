# ADR-020 — Owner Response Capture Authority

## Status

ACCEPTED

## Fecha

2026-06-09

## Dueño conceptual

Kernel PymIA / Owner Interaction Boundary / Contract Governance

## Context

Después de M45, M46, M47, M48, M49 y M50, el repositorio ya puede:

```text
detectar faltantes
→ construir preguntas explícitas al dueño
→ escribir owner_questions_bundle.json
→ proyectar preguntas visibles en render_contract
→ mostrar una pregunta owner-facing en la respuesta
```

Sin embargo, el sistema todavía no tenía autoridad documental para representar una respuesta del dueño como artefacto separado, trazable y fail-closed.

`AGENTS.md` exige mantener separadas las capas:

```text
pregunta visible
≠ respuesta capturada
≠ evidencia registrada
≠ diagnóstico recalculado
```

Antes de esta ADR, esa frontera no estaba definida mediante contrato explícito.

## Decision

Se autoriza `Owner Response Capture` únicamente como futura capacidad contractual para representar respuestas explícitas del dueño PyME a preguntas previamente emitidas por el sistema.

La capacidad autorizada es estructural.

No autoriza runtime conversacional ni consumo automático de la respuesta.

Su función permitida es:

```text
pregunta emitida
→ respuesta capturada como artefacto soberano
→ respuesta disponible para una futura evaluación gobernada
```

## Allowed sources

Toda versión futura de `Owner Response Capture` debe derivarse únicamente de artefactos existentes y trazables, por ejemplo:

- `OwnerQuestion`
- `OwnerQuestionsBundle`
- `owner_questions_bundle.json`
- `RenderContract.next_questions`
- `RenderContract.blocked_message`
- referencias explícitas de canal o adjunto, si en un futuro se autorizan por contrato propio

No puede inventar preguntas, respuestas ni evidencia.

## Mandatory rules

`Owner Response Capture` debe:

- preservar referencia explícita a la pregunta origen;
- mantener trazabilidad al artefacto fuente;
- representar la respuesta sin interpretarla como verdad operativa;
- distinguir captura de respuesta de registro de evidencia;
- fallar en cerrado si no existe pregunta origen o referencia trazable suficiente;
- operar como contrato de frontera y no como diagnóstico.

## Prohibited behaviors

Queda prohibido:

- convertir la respuesta capturada en evidencia validada automáticamente;
- recalcular diagnóstico;
- crear findings nuevos;
- confirmar estados candidatos o bloqueados;
- inferir significado adicional por heurística libre;
- abrir Telegram, Hermes, FastAPI o runtime productivo por esta ADR;
- mezclar captura de respuesta con parsing, scoring o intake productivo.

## Consequences

Desde esta ADR:

- M51 puede abrirse como frente de contrato y esquema puro para respuestas del dueño;
- la respuesta capturada queda definida como artefacto separado de evidencia y diagnóstico;
- cualquier consumo futuro de esa respuesta requerirá CapabilitySpec, ModuleContract, TaskSpec, tests y evidencia propios antes de declararse PASS.
