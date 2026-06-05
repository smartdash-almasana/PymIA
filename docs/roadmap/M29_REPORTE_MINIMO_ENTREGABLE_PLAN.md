# M29 — Reporte mínimo entregable Plan

## Estado

PLAN_DRAFT

## Contexto

M27 cerró el puente:

```text
mensaje del dueño + Excel controlado
→ IntakeRecord
→ evidence gate
→ READY_FOR_ANALYSIS
```

M28 cerró el puente:

```text
ActionableFinding[]
→ EvidenceItem[]
→ NarrativeReport grounded
→ markdown legible / auditable
```

M29 debe unir esos avances en una salida única mínima y entregable para un caso asistido.

No declarar producto final.
No declarar autonomía end-to-end.
No declarar servicio comercial validado.

---

## Objetivo

Generar un reporte Markdown mínimo con estructura estable para un caso asistido:

```text
problema declarado
+ evidencia usada
+ hallazgos principales
+ severidad
+ recomendación básica
+ límites del análisis
+ trace opcional
```

---

## Resultado esperado

Un flujo reproducible:

```text
owner_message
+ excel_fixture_ref
+ ActionableFinding[]
→ minimal delivery report markdown
```

Debe ser legible por una persona no técnica y auditable por el equipo.

---

## Alcance permitido

- crear un builder puro de reporte mínimo;
- reutilizar `ActionableFinding`;
- reutilizar `build_narrative_report_from_actionable_findings`;
- reutilizar `render_markdown`;
- incluir problema declarado;
- incluir evidencia usada;
- incluir límites del análisis;
- incluir disclaimer operativo;
- incluir modo con trace opcional;
- agregar tests focales.

---

## Fuera de alcance

- PDF;
- HTML;
- UI/dashboard;
- Telegram;
- envío automático;
- registry;
- dispatcher;
- plugins;
- CI;
- ERP/Odoo/Dolibarr;
- LLM externo;
- nueva capability de negocio;
- promesa de diagnóstico integral;
- producto final.

---

## Archivos sugeridos

```text
pymia/narrative/minimal_delivery_report.py
tests/test_minimal_delivery_report.py
docs/smartpyme/M29_REPORTE_MINIMO_ENTREGABLE_CHECKPOINT.md
```

---

## Contrato sugerido

Entrada mínima:

```text
owner_message: str
case_id: str
tenant_id: str
evidence_refs: list[str]
findings: list[ActionableFinding]
include_trace_ids: bool = False
```

Salida:

```text
str  # Markdown
```

El reporte debe contener secciones mínimas:

```text
# Reporte operativo mínimo
## Problema declarado
## Evidencia usada
## Hallazgos principales
## Acciones sugeridas
## Límites del análisis
```

Si no hay hallazgos, debe fallar cerrado con una salida explícita:

```text
No hay hallazgos suficientes para generar un reporte operativo.
```

---

## Tests esperados

1. Genera reporte con problema declarado, evidencia, hallazgos, acciones y límites.
2. Reutiliza narrativa grounded de M28.
3. Oculta trace en modo cliente.
4. Muestra trace en modo auditoría.
5. Fail-closed si `findings` está vacío.
6. No usa red, LLM, Telegram, PDF, HTML, UI ni pandas.

---

## Criterio PASS

M29 puede cerrarse si un agente local reporta tests verdes para:

```text
python -m pytest tests/test_minimal_delivery_report.py -q
python -m pytest tests/test_narrative_actionable_findings_adapter.py tests/test_minimal_delivery_report.py -q
```

Y si el reporte resultante no promete producto, diagnóstico integral ni autonomía.

---

## Criterio BLOCKED

Bloquear si el reporte requiere:

- dispatcher;
- registry;
- UI/PDF/HTML;
- LLM;
- datos no disponibles;
- nueva capability;
- promesa comercial no validada.

---

## Prompt para agente implementador/auditor

```text
Actuá como agente implementador prudente sobre el repo local:
E:\BuenosPasos\smartbridge\PymIA

Objetivo M29:
Crear un reporte Markdown mínimo entregable usando lo ya cerrado en M27 y M28.

Leer antes de tocar:
- docs/roadmap/ROADMAP_SERVICIO_ASISTIDO_EXCEL_SEMANTICA_PYME.md
- docs/smartpyme/M27_EXCEL_SEMANTICA_DUENO_CHECKPOINT.md
- docs/smartpyme/M28_EXPLICABLE_FINDING_CHECKPOINT.md
- pymia/narrative/actionable_findings_adapter.py
- pymia/narrative/markdown_exporter.py
- pymia/narrative/grounding_validator.py
- pymia/smartpyme/finding_projection.py
- tests/test_narrative_actionable_findings_adapter.py

Implementar sólo si los contratos son claros.

Archivos permitidos:
- pymia/narrative/minimal_delivery_report.py
- tests/test_minimal_delivery_report.py

No tocar:
- registry/capabilities.yaml
- dispatcher
- plugins
- Telegram/PDF/HTML/UI
- CI
- ERP/Odoo/Dolibarr
- LLM/red

Contrato esperado:
owner_message + tenant_id + case_id + evidence_refs + ActionableFinding[]
→ Markdown con problema declarado, evidencia usada, hallazgos, acciones, límites y trace opcional.

Tests mínimos:
1. reporte completo legible;
2. trace oculto en modo cliente;
3. trace visible en modo auditoría;
4. fail-closed sin hallazgos;
5. AST sin imports prohibidos.

Ejecutar:
python -m pytest tests/test_minimal_delivery_report.py -q
python -m pytest tests/test_narrative_actionable_findings_adapter.py tests/test_minimal_delivery_report.py -q

Respuesta final:
VEREDICTO PASS/BLOCKED
archivos modificados
salidas pytest
riesgos
no declarar producto.
```
