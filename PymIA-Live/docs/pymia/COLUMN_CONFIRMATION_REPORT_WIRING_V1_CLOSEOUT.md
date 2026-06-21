# COLUMN_CONFIRMATION_REPORT_WIRING_V1_CLOSEOUT

## STATUS

```text
CLOSED
```

## OBJECTIVE

Cerrar el cableado real de la matriz de confirmación de columnas desde la evidencia estructurada hasta el reporte owner-facing.

Este frente conecta la matriz que ya nacía en la ingesta con el `report` consumido por el renderer principal, permitiendo que la sección de confirmación de columnas aparezca en el informe real cuando existan columnas pendientes accionables.

## PREVIOUS FRONTS

```text
COLUMN_CONFIRMATION_LAYER_V1
OWNER_COLUMN_CONFIRMATION_FLOW_V1
COLUMN_CONFIRMATION_OWNER_VIEW_V1
OWNER_COLUMN_CONFIRMATION_E2E_TRACE_V1
COLUMN_CONFIRMATION_REPORT_INTEGRATION_V1
COLUMN_CONFIRMATION_REPORT_WIRING_AUDIT_V1
```

## THIS FRONT

```text
COLUMN_CONFIRMATION_REPORT_WIRING_V1
```

## PROBLEM

La auditoría previa determinó:

```text
VEREDICTO: NOT_WIRED
```

La matriz existía en la metadata de `StructuredEvidence`, y el renderer ya sabía usar `report["column_confirmation_matrix"]`, pero el pipeline real no transportaba esa matriz al reporte.

Ruta rota antes del frente:

```text
StructuredEvidence.metadata["column_confirmation_matrix"]
→ build_structured_summary(...)
→ metadata recortada
→ report sin column_confirmation_matrix
→ renderer sin sección de confirmación
```

## CHANGE

Se modificó:

```text
PymIA-Live/pymia/application/vertical_pipeline.py
```

Cambio principal:

```text
StructuredEvidence.metadata["column_confirmation_matrix"]
→ build_structured_summary(...)
→ structured_summary["column_confirmation_matrix"]
→ _build_owner_report_base(...)
→ report["column_confirmation_matrix"]
```

## IMPLEMENTATION_DETAIL

En `build_structured_summary(...)` se extrae defensivamente la metadata:

```python
metadata = evidence.get("metadata") or payload.get("metadata") or {}
column_confirmation_matrix = metadata.get("column_confirmation_matrix")
if column_confirmation_matrix is not None:
    summary["column_confirmation_matrix"] = column_confirmation_matrix
```

En `_build_owner_report_base(...)` la matriz se mueve desde `structured_summary` hacia la raíz del `report`:

```python
column_confirmation_matrix = structured_summary.pop("column_confirmation_matrix", None)
report["structured_evidence_summary"] = structured_summary
if column_confirmation_matrix is not None:
    report["column_confirmation_matrix"] = column_confirmation_matrix
```

## VALIDATED_PATH

Ruta final cerrada:

```text
StructuredEvidence.metadata["column_confirmation_matrix"]
→ build_structured_summary(...)
→ report["column_confirmation_matrix"]
→ owner_markdown_renderer.py
→ render_column_confirmation_owner_view(...)
→ sección owner-facing de confirmación de columnas
```

## TESTS

Commands reported:

```bash
python -m pytest tests/application/test_vertical_pipeline_boundary.py -q

python -m pytest tests/contracts/test_column_confirmation_v1.py \
                 tests/rendering/test_column_confirmation_owner_view.py \
                 tests/rendering/test_column_confirmation_e2e_trace.py \
                 tests/rendering/test_column_confirmation_report_integration.py \
                 tests/rendering/test_owner_markdown_renderer_boundary.py \
                 tests/application/test_vertical_pipeline_boundary.py -q
```

Results reported:

```text
Focal:
tests/application/test_vertical_pipeline_boundary.py
15 passed en 43.40s

Validación cruzada:
67 passed en 41.68s
```

## COMMIT

```text
feat(pymia-live): wire column confirmation matrix into owner report
```

## INVARIANTS

- El pipeline transporta la matriz sólo si existe.
- Si no existe `column_confirmation_matrix`, no agrega clave artificial al reporte.
- La matriz sale de `structured_evidence_summary` y queda en la raíz de `report`, donde la espera el renderer.
- No se duplican preguntas owner-facing.
- No se modifica `owner_question` ni `next_questions`.
- No se toca `diagnostic_core`.
- No se toca storage.
- No se toca replay.
- No se toca OCF productivo.
- No se toca CLI.
- No se abren canales externos.

## RISK_REDUCED

Este frente reduce el riesgo de tener una matriz de confirmación correctamente generada pero invisible en el reporte real del dueño.

Riesgo reducido principal:

```text
Confirmación de columnas implementada pero desconectada del pipeline owner-facing real.
```

## NON_GOALS

Este frente no abrió:

```text
storage
replay real
OCF productivo
diagnostic_core
CLI
dashboard
chatbot
external channels
new Excel pilots
Nivel 2
captura real de respuestas del dueño
persistencia de sesiones de confirmación
```

## RESIDUAL_RISKS

- Falta validar con fixture Excel real que el reporte final efectivamente muestre la sección cuando la matriz contiene columnas pendientes.
- Falta persistir respuestas reales del dueño.
- Falta replay real de confirmaciones persistidas.
- Falta UX/copy final por canal.
- Falta decidir si la confirmación de columnas debe priorizarse visualmente por encima de otras preguntas owner-facing.

## NEXT_FRONT_RECOMMENDED

```text
COLUMN_CONFIRMATION_REAL_REPORT_SMOKE_V1
```

Recommended objective:

```text
Ejecutar un smoke real con un Excel que genere ColumnConfirmationMatrix accionable y verificar que el markdown owner-facing incluya la sección "Confirmación de columnas".
```

Suggested scope:

```text
- No cambiar código.
- Usar fixture existente si alcanza.
- Validar output markdown.
- Confirmar que MetodoPago no aparece como monto.
- Confirmar que cálculos bloqueados no se presentan como resultados.
```

## FINAL_VERDICT

```text
COLUMN_CONFIRMATION_REPORT_WIRING_V1: CLOSED
```
