# M29 — Reporte mínimo entregable Checkpoint

## Estado

CLOSED / PASS

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

M29 cubre:

1. reporte completo legible;
2. trace oculto en modo cliente;
3. trace visible en modo auditoría;
4. fail-closed sin hallazgos;
5. validación de inputs mínimos;
6. AST sin imports prohibidos.

## Validación ejecutada localmente

Comando focal:

```text
python -m pytest tests/test_minimal_delivery_report.py -q
```

Resultado focal exacto:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0
rootdir: E:\BuenosPasos\smartbridge\PymIA
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: cov-7.1.0, anyio-4.12.1
collected 5 items

tests\test_minimal_delivery_report.py .....                              [100%]

============================== 5 passed in 1.46s ==============================
```

Comando de integración con M28:

```text
python -m pytest tests/test_narrative_actionable_findings_adapter.py tests/test_minimal_delivery_report.py -q
```

Resultado integración exacto:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0
rootdir: E:\BuenosPasos\smartbridge\PymIA
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: cov-7.1.0, anyio-4.12.1
collected 9 items

tests\test_narrative_actionable_findings_adapter.py ....                 [ 44%]
tests\test_minimal_delivery_report.py .....                              [100%]

============================== 9 passed in 2.24s ==============================
```

Fecha de validación:

```text
2026-06-06 15:37:42 -03:00
```

Nota de cierre:

```text
M29 certifica owner_message + tenant_id + case_id + evidence_refs + ActionableFinding[] → Markdown mínimo entregable.
```

## Riesgos detectados

1. El reporte depende de que M28 mantenga una estructura narrativa compatible.
2. evidence_refs se normaliza de forma simple; si llegan valores extraños puede requerir endurecimiento posterior.

## Veredicto

M29 CLOSED / PASS.

Certificado por evidencia ejecutada localmente:

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
