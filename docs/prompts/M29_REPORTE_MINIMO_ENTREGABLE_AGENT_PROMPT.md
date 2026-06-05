# Prompt — M29 Reporte mínimo entregable

Actuá como agente implementador prudente sobre el repo local:

```text
E:\BuenosPasos\smartbridge\PymIA
```

## Contexto

M27 está cerrado y pusheado:

```text
mensaje del dueño + Excel controlado
→ IntakeRecord
→ evidence gate
→ READY_FOR_ANALYSIS
```

M28 está cerrado y pusheado:

```text
ActionableFinding[]
→ EvidenceItem[]
→ NarrativeReport grounded
→ markdown legible / auditable
```

M29 debe crear una salida única mínima entregable, sin declarar producto final.

## Objetivo M29

Crear un reporte Markdown mínimo usando lo ya existente:

```text
owner_message
+ tenant_id
+ case_id
+ evidence_refs
+ ActionableFinding[]
→ Markdown entregable
```

El reporte debe contener:

```text
# Reporte operativo mínimo
## Problema declarado
## Evidencia usada
## Hallazgos principales
## Acciones sugeridas
## Límites del análisis
```

Debe poder renderizarse en dos modos:

```text
cliente: sin trace ids visibles
auditoría: con trace ids visibles
```

## Leer antes de tocar

- `docs/roadmap/ROADMAP_SERVICIO_ASISTIDO_EXCEL_SEMANTICA_PYME.md`
- `docs/roadmap/M29_REPORTE_MINIMO_ENTREGABLE_PLAN.md`
- `docs/smartpyme/M27_EXCEL_SEMANTICA_DUENO_CHECKPOINT.md`
- `docs/smartpyme/M28_EXPLICABLE_FINDING_CHECKPOINT.md`
- `pymia/narrative/actionable_findings_adapter.py`
- `pymia/narrative/markdown_exporter.py`
- `pymia/narrative/grounding_validator.py`
- `pymia/smartpyme/finding_projection.py`
- `tests/test_narrative_actionable_findings_adapter.py`

## Archivos permitidos

Sólo modificar o crear:

```text
pymia/narrative/minimal_delivery_report.py
tests/test_minimal_delivery_report.py
```

Si necesitás tocar otro archivo, detenerse y reportar `BLOCKED`.

## Prohibido

No tocar:

```text
registry/capabilities.yaml
dispatcher
plugins
Telegram
PDF
HTML
UI/dashboard
CI
ERP/Odoo/Dolibarr
LLM/red
```

No declarar:

```text
producto final
diagnóstico integral
autonomía end-to-end
servicio comercial validado
```

## Contrato esperado

Crear una función pura, nombre sugerido:

```python
render_minimal_delivery_report(
    *,
    tenant_id: str,
    case_id: str,
    owner_message: str,
    evidence_refs: list[str],
    findings: list[ActionableFinding],
    include_trace_ids: bool = False,
) -> str
```

Reglas:

1. Validar inputs mínimos.
2. Reutilizar `build_narrative_report_from_actionable_findings`.
3. Reutilizar `render_markdown`.
4. Incluir secciones estables.
5. Ocultar trace ids si `include_trace_ids=False`.
6. Mostrar trace ids si `include_trace_ids=True`.
7. Fail-closed si no hay hallazgos.
8. No usar red, LLM, filesystem, dispatcher ni registry.

## Tests mínimos

Crear:

```text
tests/test_minimal_delivery_report.py
```

Debe cubrir:

1. reporte completo legible con problema, evidencia, hallazgos, acciones y límites;
2. trace oculto en modo cliente;
3. trace visible en modo auditoría;
4. fail-closed sin hallazgos;
5. validación de inputs mínimos;
6. AST sin imports prohibidos.

## Comandos a ejecutar

```bash
python -m pytest tests/test_minimal_delivery_report.py -q
python -m pytest tests/test_narrative_actionable_findings_adapter.py tests/test_minimal_delivery_report.py -q
```

## Respuesta final requerida

Responder con:

```text
VEREDICTO: PASS / BLOCKED
causa exacta
archivos modificados
comandos ejecutados
salidas pytest
riesgos detectados
próximo paso recomendado
```

Criterio:

No declarar PASS sin tests verdes.
No commitear.
No ampliar alcance.
No hacer parches por intuición.
