# COLUMN_CONFIRMATION_REPORT_INTEGRATION_V1_CLOSEOUT

## STATUS

```text
CLOSED_PENDING_COMMIT_PUSH
```

## OBJECTIVE

Integrar la vista owner-facing de confirmación de columnas dentro del reporte owner-facing existente, de modo que las columnas pendientes de confirmación sean visibles para el dueño antes de presentar cálculos dependientes.

Este frente conecta la cadena previa de confirmación de columnas con el renderer principal de reporte, sin abrir storage, replay, OCF productivo, CLI, dashboard, chatbot ni canales externos.

## PREVIOUS FRONTS

```text
COLUMN_CONFIRMATION_LAYER_V1
OWNER_COLUMN_CONFIRMATION_FLOW_V1
COLUMN_CONFIRMATION_OWNER_VIEW_V1
OWNER_COLUMN_CONFIRMATION_E2E_TRACE_V1
```

Cadena consolidada antes de este frente:

```text
columna dudosa
→ owner_question
→ vista owner-facing
→ respuesta clasificada del dueño
→ apply_owner_answer
→ cálculo desbloqueado sólo si corresponde
```

Cadena integrada por este frente:

```text
reporte owner-facing
→ detecta column_confirmation_matrix si existe
→ renderiza sección de confirmación si hay columnas accionables
→ no agrega ruido si no hay pendientes
```

## THIS FRONT

```text
COLUMN_CONFIRMATION_REPORT_INTEGRATION_V1
```

Este frente integra `render_column_confirmation_owner_view(...)` dentro de `render_markdown_from_report(...)` mediante una sección owner-facing de confirmación de columnas.

## FILES_CHANGED

```text
PymIA-Live/pymia/rendering/owner_markdown_renderer.py
PymIA-Live/tests/rendering/test_column_confirmation_report_integration.py
```

## BEHAVIOR_ADDED

El renderer principal ahora puede leer:

```text
report["column_confirmation_matrix"]
```

Acepta:

```text
ColumnConfirmationMatrix
plain dict compatible con ColumnConfirmationMatrix
```

Si la matriz contiene columnas accionables, el reporte owner-facing agrega:

```text
## Confirmación de columnas
```

junto con la salida de:

```text
render_column_confirmation_owner_view(...)
```

Si no hay matriz, o si la matriz no contiene columnas pendientes accionables, el reporte no agrega sección de confirmación ni mensaje innecesario.

## VALIDATED_BEHAVIOR

```text
- Reporte owner-facing incluye vista de confirmación cuando hay columnas pendientes.
- Reporte no incluye sección si no hay column_confirmation_matrix.
- Reporte no incluye sección si la matriz existe pero no hay columnas pendientes.
- Reporte acepta column_confirmation_matrix como dict.
- MetodoPago se preserva como forma de pago, no como monto.
- OWNER_VIEW no incorpora IDs técnicos nuevos.
```

## TESTS

Commands reported:

```bash
python -m pytest tests/rendering/test_column_confirmation_report_integration.py -q

python -m pytest tests/contracts/test_column_confirmation_v1.py \
                 tests/rendering/test_column_confirmation_owner_view.py \
                 tests/rendering/test_column_confirmation_e2e_trace.py \
                 tests/rendering/test_column_confirmation_report_integration.py \
                 tests/rendering/test_owner_markdown_renderer_boundary.py -q
```

Results reported:

```text
tests/rendering/test_column_confirmation_report_integration.py
4 passed in 1.28s

validación ampliada
52 passed in 0.62s
```

## INVARIANTS

- El reporte owner-facing puede mostrar preguntas de confirmación de columnas.
- El reporte no debe presentar cálculos bloqueados como resultados confirmados.
- La sección de confirmación sólo aparece si hay columnas accionables.
- Columnas confirmadas no generan sección.
- Columnas ignoradas no generan sección.
- `MetodoPago` no se presenta como monto.
- La integración permanece dentro de rendering.
- No se abre storage.
- No se abre replay.
- No se abre OCF productivo.
- No se toca diagnostic_core.
- No se toca CLI.
- No se abren canales externos.

## RISK_REDUCED

Este frente reduce el riesgo de que el sistema tenga un mecanismo seguro de confirmación de columnas, pero que el reporte entregado al dueño omita esas preguntas y deje bloqueos sin vía visible de resolución.

Riesgo reducido principal:

```text
Columnas pendientes computacionalmente bloqueantes sin aparición en el reporte owner-facing.
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
persistencia de respuestas
captura real de respuestas del dueño
```

## RESIDUAL_RISKS

- Falta persistir sesiones reales de confirmación.
- Falta capturar respuestas reales del dueño desde un canal operativo.
- Falta replay real de confirmaciones persistidas.
- Falta decidir formato final de UX/copy con acentos, tono y canal.
- Falta conectar esta matriz al flujo productivo si todavía no se propaga en `report`.

## NEXT_FRONT_RECOMMENDED

```text
COLUMN_CONFIRMATION_REPORT_WIRING_AUDIT_V1
```

Recommended objective:

```text
Auditar si column_confirmation_matrix ya llega naturalmente al report real generado por el pipeline.
Si no llega, documentar la frontera exacta antes de tocar CLI o pipeline.
```

No abrir implementación runtime hasta verificar la frontera de wiring.

## FINAL_VERDICT

```text
COLUMN_CONFIRMATION_REPORT_INTEGRATION_V1: CLOSED_PENDING_COMMIT_PUSH
```
