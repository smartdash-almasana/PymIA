# OWNER_SEMANTIC_CONFIRMATION_REENTRY_PROJECTION_CHECKPOINT

Fecha: 2026-06-10
Estado: READY_FOR_VALIDATION
Frente: OWNER_SEMANTIC_CONFIRMATION_REENTRY_PROJECTION

## 1. Veredicto

```text
READY_FOR_VALIDATION
```

Se creó un módulo puro para proyectar una confirmación semántica explícita desde una reentrada de respuesta del dueño hacia el `owner_facing_report`.

## 2. Archivo creado

```text
pymia/smartpyme/owner_semantic_confirmation_reentry_projection.py
```

## 3. Función principal

```python
project_semantic_confirmation_reentry_to_owner_facing(
    *,
    owner_answer,
    owner_facing_report,
    missing_keys,
    source_ref,
) -> dict
```

## 4. Regla de seguridad principal

La función sólo actúa si `owner_answer.metadata` trae explícitamente:

```text
semantic_confirmation_status = CONFIRMED_BY_OWNER | CORRECTED_BY_OWNER | REJECTED_BY_OWNER
```

Si esa metadata no existe, no infiere confirmación desde texto libre y devuelve el reporte con:

```text
semantic_confirmation_reentry_projection.applied = false
reason = missing_explicit_semantic_confirmation_status
```

## 5. Flujo aplicado cuando hay confirmación explícita

```text
owner_answer metadata explícita
→ OwnerSemanticConfirmationGate
→ build_owner_confirmed_semantic_request_flow(...)
→ project_confirmed_semantic_requests_to_owner_facing(...)
→ owner_facing_report enriquecido
```

## 6. Frontera preservada

No modifica ni toca:

```text
DiagnosticCore
graph
core_delivery_bridge.py
Telegram
Hermes runtime
PDF
ERP
fórmulas
findings
```

No promueve narrativa del dueño a evidencia estructural.
No inventa consentimiento.
No infiere confirmación por texto libre.

## 7. Tests esperados

Crear:

```text
tests/smartpyme/test_owner_semantic_confirmation_reentry_projection.py
```

Casos mínimos:

1. Sin `semantic_confirmation_status` explícito:
   - no aplica proyección;
   - no agrega next questions semánticas;
   - `semantic_confirmation_reentry_projection.applied is False`.

2. Con `CONFIRMED_BY_OWNER` explícito:
   - construye flujo `BLOCKED_ACTIONABLE`;
   - agrega pedidos concretos a `next_questions`;
   - conserva status/evidence_used/missing_evidence;
   - no agrega findings.

3. Con `REJECTED_BY_OWNER` explícito:
   - flow_status `NEEDS_REINTERPRETATION`;
   - no agrega pedidos finales de evidencia;
   - agrega next step de reinterpretación.

4. Con `CORRECTED_BY_OWNER` explícito:
   - requiere `corrected_interpretation`;
   - usa corrección para construir pedidos accionables.

5. `source_ref` vacío:
   - levanta ValueError si la proyección intenta aplicarse.

## 8. Comando sugerido

```text
python -m pytest tests/smartpyme/test_owner_semantic_confirmation_reentry_projection.py tests/smartpyme/test_owner_confirmed_semantic_request_flow.py tests/smartpyme/test_owner_confirmed_semantic_request_projection.py tests/architecture -q --basetemp .tmp_pytest_owner_semantic_confirmation_reentry_projection
```

## 9. Próximo paso después de PASS

Sólo después de PASS, evaluar inserción controlada en:

```text
pymia/audit_result/core_delivery_bridge.py::project_owner_answers_into_delivery_bundle(...)
```

No insertar directamente en `graph.py`.
