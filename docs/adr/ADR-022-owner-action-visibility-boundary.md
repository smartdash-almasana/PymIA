# ADR-022 — Owner Action Visibility Boundary

## Status

ACCEPTED

## Fecha

2026-06-09

## Dueño conceptual

Kernel PymIA / Delivery Boundary / Owner Interaction Boundary / Contract Governance

## Context

Después de M42, M43, M44, M49, M51, M52, M53, M54 y M55, el repositorio ya puede:

```text
producir OwnerFacingReport
→ hacerlo visible mediante la respuesta existente
→ capturar respuestas del dueño como contrato
→ evaluarlas
→ decidir una siguiente acción mínima
```

Sin embargo, todavía no existe una frontera canónica para hacer visible `OwnerNextActionBundle` sin romper la soberanía owner-facing ya definida ni abrir una segunda vía de render.

El riesgo arquitectónico es claro:

```text
OwnerFacingReport
≠ renderizador paralelo de acciones
≠ markdown conversacional ad-hoc
≠ graph con lógica de decisión owner-facing
```

Si `OwnerNextActionBundle` se proyectara directamente desde un nuevo renderizador o desde `graph.py`, el sistema duplicaría autoridad owner-facing y perdería una única fuente de verdad visible.

## Problem

El sistema necesita una frontera explícita para responder estas preguntas antes de cualquier integración visible:

- dónde debe resolverse `target_questions` si hoy sólo contiene IDs;
- qué artefacto owner-facing es soberano para mostrar la siguiente acción;
- cómo evitar que `delivery_markdown.py` o `graph.py` asuman lógica conversacional;
- cómo mantener fail-closed si la resolución `ID -> texto` no está disponible.

## Decision

Se decide que:

1. `OwnerFacingReport` sigue siendo la frontera owner-facing soberana.
2. `delivery_markdown.py` queda fuera de lógica conversacional y no debe transformarse en renderizador paralelo de acciones owner-facing.
3. `graph.py` no debe conocer `OwnerNextActionBundle`.
4. `core_delivery_bridge.py` es el candidato futuro correcto para integrar `OwnerNextActionBundle`, pero no se modifica en M56.
5. `target_questions` hoy contiene IDs y la resolución `ID -> texto` debe definirse antes de cualquier render visible.
6. `OwnerAnswer` y `OwnerNextAction` no se promueven a evidencia dura por esta frontera.
7. esta frontera no autoriza diagnóstico nuevo ni findings nuevos.

## Sources of truth

Las fuentes de verdad existentes para un futuro frente visible son:

- `OwnerFacingReport`
- `RenderContract`
- `DeliveryPackage`
- `OwnerQuestionsBundle`
- `OwnerAnswerEvaluationBundle`
- `OwnerNextActionBundle`

De ellas, la frontera visible soberana sigue siendo `OwnerFacingReport` y sus proyecciones ya autorizadas hacia la respuesta existente.

## Recommended future flow

El flujo futuro recomendado es:

```text
OwnerNextActionBundle
→ resolución target_questions IDs/textos
→ RenderContract / OwnerFacingReport
→ respuesta visible existente
```

Esto implica que, antes de cualquier implementación visible, debe definirse un contrato explícito de resolución entre:

- IDs de `target_questions`
- textos owner-facing trazables
- artefacto soberano que los expone

## Prohibited behaviors

Queda prohibido:

- crear un renderizador paralelo de `OwnerNextActionBundle`;
- duplicar lógica owner-facing en `delivery_markdown.py`;
- hacer que `graph.py` conozca o interprete `OwnerNextActionBundle`;
- mostrar IDs crudos al dueño como salida visible final;
- promover `OwnerNextAction` o `OwnerAnswer` a evidencia dura;
- generar narrativa libre no trazable;
- introducir diagnóstico o findings nuevos.

## Fail-closed limits

Si no existe resolución explícita de `target_questions` a texto owner-facing trazable, el sistema debe:

- fallar en cerrado;
- no renderizar la acción visible;
- preservar el bundle interno como artefacto técnico;
- esperar un frente metodológico específico de resolución y proyección visible.

## Consequences

Desde esta ADR:

- M56 puede cerrarse como auditoría documental de frontera;
- cualquier visibilidad futura de `OwnerNextActionBundle` debe pasar por `OwnerFacingReport` o su frontera contractual equivalente, no por un canal paralelo;
- la próxima implementación visible requerirá CapabilitySpec, ModuleContract, TaskSpec, tests y evidencia propios antes de tocar `core_delivery_bridge.py`.
