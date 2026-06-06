# M28 — Hallazgo explicable Checkpoint

## Estado

CLOSED / PASS

## Contexto

M28 continúa el roadmap de servicio asistido Excel + semántica PyME después de M27.

M27 certificó el slice:

```text
mensaje del dueño + Excel controlado
→ IntakeRecord
→ evidence gate
→ READY_FOR_ANALYSIS
```

M28 aborda el siguiente paso del roadmap:

```text
ActionableFinding[]
→ narrativa grounded
→ markdown legible
```

Este checkpoint no declara producto final.
No declara autonomía end-to-end.
No declara servicio comercial validado.

---

## Archivos WIP aceptados

```text
pymia/narrative/actionable_findings_adapter.py
tests/test_narrative_actionable_findings_adapter.py
```

---

## Objetivo del slice

Crear un adaptador puro y determinístico entre:

```text
pymia.smartpyme.finding_projection.ActionableFinding
```

y los modelos narrativos existentes:

```text
pymia.narrative.models.EvidenceItem
pymia.narrative.models.NarrativeClaim
pymia.narrative.models.NarrativeReport
```

El objetivo es permitir que hallazgos técnicos ya generados por SmartPyme puedan transformarse en narrativa auditable y legible para un dueño PyME.

---

## Contratos respetados

Según auditoría reportada, el adapter respeta:

- `ActionableFinding` como input operativo;
- `EvidenceItem` como unidad de grounding;
- `NarrativeClaim` con `evidence_ids` obligatorios;
- `NarrativeReport` como salida narrativa;
- `validate_grounding(...)` como verificación de sustento;
- `render_markdown(...)` para salida con o sin trace.

---

## Comportamiento cubierto

El slice M28 cubre:

1. `ActionableFinding[] → EvidenceItem[]`.
2. Preservación de campos trazables:
   - entidad;
   - métrica;
   - diferencia;
   - severidad;
   - recomendación;
   - referencias de evidencia.
3. `ActionableFinding[] → NarrativeReport`.
4. Markdown legible sin trace visible.
5. Markdown auditable con trace visible.
6. Fail-closed con lista vacía.
7. AST check contra imports prohibidos.

---

## Límites preservados

M28 no debe interpretarse como:

- nueva capability de negocio;
- producto final;
- diagnóstico integral;
- entrega comercial validada;
- autonomía completa;
- integración con dispatcher;
- integración con registry;
- integración con UI;
- integración con Telegram/PDF/HTML;
- uso de LLM;
- uso de red.

---

## Validación ejecutada localmente

Comando focal:

```text
python -m pytest tests/test_narrative_actionable_findings_adapter.py -q
```

Comando de ecosistema narrativo:

```text
python -m pytest tests/test_narrative_pipeline.py tests/test_narrative_report_v2.py tests/test_narrative_actionable_findings_adapter.py -q
```

Fecha de validación:

```text
2026-06-06 15:24:52 -03:00
```

Resultado focal exacto:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0
rootdir: E:\BuenosPasos\smartbridge\PymIA
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: cov-7.1.0, anyio-4.12.1
collected 4 items

tests\test_narrative_actionable_findings_adapter.py ....                 [100%]

============================== 4 passed in 1.26s ==============================
```

Resultado ecosistema narrativo exacto:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0
rootdir: E:\BuenosPasos\smartbridge\PymIA
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: cov-7.1.0, anyio-4.12.1
collected 13 items

tests\test_narrative_pipeline.py .....                                   [ 38%]
tests\test_narrative_report_v2.py ....                                   [ 69%]
tests\test_narrative_actionable_findings_adapter.py ....                 [100%]

============================= 13 passed in 3.79s ==============================
```

Nota de cierre:

```text
M28 valida ActionableFinding[] → NarrativeReport grounded → markdown legible/auditable.
```

---

## Riesgos detectados

### 1. Acoplamiento de métricas

El adapter usa:

```text
finding.severity → EvidenceItem.value
finding.difference → EvidenceItem.context
```

Esto es aceptable bajo los contratos actuales, pero si cambia `ActionableFinding` o la semántica de `EvidenceItem`, el adapter deberá revisarse.

### 2. IDs sintéticos de evidencia

El adapter genera IDs como:

```text
actionable_finding:1:margen
```

Esto es válido para grounding y auditoría, pero cualquier capa visual futura debe decidir si los oculta o los muestra sólo en modo trace.

---

## Veredicto

M28 puede cerrarse como slice técnico mínimo si el usuario decide asimilar el WIP.

Certificado por evidencia reportada:

```text
ActionableFinding[]
→ EvidenceItem[]
→ NarrativeReport grounded
→ markdown legible / markdown auditable
```

No certificado:

```text
producto final
servicio comercial validado
narrativa óptima para mercado
PDF profesional
flujo end-to-end desde cliente real
```

---

## Próximo paso sugerido

Si M28 se commitea, el próximo hito natural es M29:

```text
Reporte mínimo entregable
```

Objetivo M29:

```text
mensaje del dueño + Excel controlado + hallazgos
→ informe mínimo con problema, evidencia, hallazgos, severidad,
  recomendación, límites y trace opcional
```

M29 no debe abrir UI, PDF, ERP, registry, dispatcher ni LLM.
