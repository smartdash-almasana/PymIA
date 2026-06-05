# M29 — Reporte mínimo entregable Checkpoint

## Estado

PASS

## Contexto

M29 continúa el roadmap de servicio asistido Excel + semántica PyME.

M27 cerró: mensaje del dueño + Excel controlado -> IntakeRecord -> evidence gate -> READY_FOR_ANALYSIS.

M28 cerró: ActionableFinding[] -> EvidenceItem[] -> NarrativeReport grounded -> markdown legible/auditable.

M29 crea una salida única mínima entregable en Markdown para un caso asistido.

No declara producto final, autonomía end-to-end ni servicio comercial validado.

## Archivos creados por agente local

- pymia/narrative/minimal_delivery_report.py
- tests/test_minimal_delivery_report.py

## Artefactos de planificación

- docs/roadmap/M29_REPORTE_MINIMO_ENTREGABLE_PLAN.md
- docs/prompts/M29_REPORTE_MINIMO_ENTREGABLE_AGENT_PROMPT.md

## Objetivo del slice

Crear una función pura y determinística para producir un reporte Markdown mínimo a partir de:

- owner_message
- tenant_id
- case_id
- evidence_refs
- ActionableFinding[]

El reporte contiene:

- Problema declarado
- Evidencia usada
- Hallazgos principales
- Acciones sugeridas
- Límites del análisis

## Comportamiento cubierto

Según evidencia reportada, M29 cubre:

1. reporte completo legible;
2. trace oculto en modo cliente;
3. trace visible en modo auditoría;
4. fail-closed sin hallazgos;
5. validación de inputs mínimos;
6. AST sin imports prohibidos.

## Validación reportada por agente local

El asistente de chat no ejecutó pytest directamente.
La evidencia fue reportada por el usuario desde agente local.

Comando focal:

python -m pytest tests/test_minimal_delivery_report.py -q

Resultado reportado:

5 passed in 0.62s

Comando de integración con M28:

python -m pytest tests/test_narrative_actionable_findings_adapter.py tests/test_minimal_delivery_report.py -q

Resultado reportado:

9 passed in 0.66s

## Riesgos detectados

1. El reporte depende de que M28 mantenga una estructura narrativa compatible.
2. evidence_refs se normaliza de forma simple; si llegan valores extraños puede requerir endurecimiento posterior.

## Veredicto

M29 PASS.

Certificado por evidencia reportada:

owner_message + tenant_id + case_id + evidence_refs + ActionableFinding[] -> Markdown mínimo entregable.

No certificado:

- producto final;
- servicio comercial validado;
- diagnóstico integral;
- PDF profesional;
- UI;
- flujo end-to-end con dispatcher;
- casos reales de cliente.

## Próximo hito sugerido

M30 — Continuidad del caso.

Antes de abrir M30, cerrar M29 con commit/push y dejar repo limpio.
