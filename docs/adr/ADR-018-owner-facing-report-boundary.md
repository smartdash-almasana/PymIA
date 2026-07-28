# ADR-018 — Owner-Facing Report Boundary

## Status

ACCEPTED

## Fecha

2026-06-08

## Dueño conceptual

Kernel PymIA / Delivery Boundary / Contract Governance

## Context

Después de M35, M36, M37, M38, M39, M40 y M41, el repositorio ya contiene una cadena operacional trazable:

```text
StructuredEvidence
→ DiagnosticCoreInput
→ DiagnosticCoreV1
→ FormulaInputGate / EvidenceGateDecision
→ OperationalAuditResult
→ RenderContract
→ ExecutionResultGate
→ DeliveryPackage
→ PymIAState
```

La salida soberana existente ya permite:

- preservar `source_refs`;
- registrar evidencia usada y faltante;
- exponer estados de bloqueo o entrega;
- producir artefactos internos verificables.

Sin embargo, el repositorio no tenía todavía una autoridad canónica que habilitara un `Owner-Facing Report` sin romper la frontera soberana definida por SCN ni la prohibición previa de narrativa owner-facing introducida por M37.

## Decision

Se autoriza `Owner-Facing Report V1` únicamente como una renderización controlada y trazable del estado operacional ya existente.

El `Owner-Facing Report V1`:

- no es un diagnóstico nuevo;
- no reemplaza `OperationalAuditResult`;
- no reemplaza `DeliveryPackage`;
- no modifica `RenderContract`;
- no recalcula fórmulas;
- no crea findings nuevos;
- no cambia el veredicto del core ni del gate;
- no agrega autoridad clínica/operacional adicional.

Su función permitida es traducir, para lectura del dueño, artefactos ya producidos por el sistema.

## Allowed sources

Toda versión `Owner-Facing Report V1` debe derivarse únicamente de artefactos existentes y trazables:

- `RenderContract`
- `DeliveryPackage`
- `OperationalAuditResult`
- `missing_evidence`
- `evidence_used`
- `next_questions`
- `next_steps`
- `blocked_message`

No puede leer fuentes extra no registradas para expandir conclusiones.

## Mandatory rules

El `Owner-Facing Report V1` debe:

- preservar el estado real del circuito (`DELIVERED`, `BLOCKED`, u otro estado contractual vigente);
- exponer explícitamente bloqueos y faltantes cuando existan;
- distinguir evidencia confirmada de evidencia faltante;
- distinguir findings o estados `CANDIDATE` de cualquier afirmación confirmada;
- mantener trazabilidad hacia artefactos operacionales ya emitidos;
- fallar en cerrado si faltan artefactos mínimos para una traducción confiable.

## Prohibited behaviors

Queda prohibido:

- inventar evidencia;
- inventar variables;
- crear findings nuevos;
- cambiar diagnóstico;
- ocultar bloqueos;
- presentar `CANDIDATE` como `CONFIRMED`;
- generar narrativa libre no trazable;
- introducir interpretación no respaldada por artefactos existentes.

## Consequences

Desde esta ADR:

- M42 puede abrirse como frente documental/técnico para `Owner-Facing Report V1`;
- cualquier implementación de owner-facing debe quedar subordinada a los artefactos soberanos existentes;
- la frontera soberana sigue siendo `OperationalAuditResult` y sus derivados contractuales, no el reporte al dueño;
- si un estado está bloqueado, el reporte al dueño debe conservar ese bloqueo y explicarlo sin maquillarlo.
