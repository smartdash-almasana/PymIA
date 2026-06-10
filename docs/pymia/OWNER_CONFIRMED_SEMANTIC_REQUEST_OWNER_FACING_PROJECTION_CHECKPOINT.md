# OWNER_CONFIRMED_SEMANTIC_REQUEST_OWNER_FACING_PROJECTION_CHECKPOINT

Fecha: 2026-06-10
Estado: PASS
Frente: OWNER_CONFIRMED_SEMANTIC_REQUEST_OWNER_FACING_PROJECTION

## 1. Veredicto

```text
PASS
```

Se implementó un módulo puro de proyección owner-facing para resultados `BLOCKED_ACTIONABLE` del flujo semántico confirmado por el dueño.

## 2. Archivo creado

```text
pymia/smartpyme/owner_confirmed_semantic_request_projection.py
```

## 3. Función principal

```python
project_confirmed_semantic_requests_to_owner_facing(
    *,
    owner_facing_report,
    flow_result,
) -> dict
```

## 4. Responsabilidad

Enriquecer una copia del reporte visible con:

```text
next_steps
next_questions
limit_warnings
semantic_request_projection
```

sin alterar estado soberano, evidencia ni findings.

## 5. Reglas implementadas

Si `flow_status == BLOCKED_ACTIONABLE`:

- agrega un paso visible indicando que el eje confirmado permite pedir evidencia concreta pero no habilita diagnóstico;
- agrega los `refined_request_text` de cada `OwnerSemanticEvidenceRequest` a `next_questions`;
- agrega warning visible indicando que la confirmación del dueño no reemplaza evidencia estructural;
- agrega `semantic_request_projection` con flags fail-closed.

Si `flow_status == PENDING_OWNER_CONFIRMATION`:

- agrega paso visible indicando que falta confirmación/corrección del dueño.

Si `flow_status == NEEDS_REINTERPRETATION`:

- agrega paso visible indicando que corresponde reformular interpretación antes de pedir evidencia final.

## 6. Frontera preservada

La función no debe modificar:

```text
status
delivery_status
operational_status
findings
evidence_used
missing_evidence
```

Tampoco:

```text
DiagnosticCore
graph
Telegram
Hermes runtime
PDF
ERP
fórmulas
findings
```

## 7. Validación ejecutada por Codex

Tests creados en:

```text
tests/smartpyme/test_owner_confirmed_semantic_request_projection.py
```

Casos validados:

1. `BLOCKED_ACTIONABLE` agrega refined request a `next_questions`.
2. `BLOCKED_ACTIONABLE` agrega warning y next step fail-closed.
3. No altera `status`, `evidence_used` ni `missing_evidence`.
4. Deduplica preguntas existentes.
5. `PENDING_OWNER_CONFIRMATION` no agrega requests finales, sólo step de confirmación.
6. `NEEDS_REINTERPRETATION` no agrega requests finales, sólo step de reinterpretación.
7. Acepta `OwnerFacingReport` con `to_dict()` además de dict.
8. `semantic_request_projection` conserva `does_resolve_structural_input=False` y `produces_findings=False`.

Comando sugerido:

```text
python -m pytest tests/smartpyme/test_owner_confirmed_semantic_request_projection.py tests/smartpyme/test_owner_confirmed_semantic_request_flow.py tests/smartpyme/test_owner_facing_report.py tests/architecture -q --basetemp .tmp_pytest_owner_confirmed_semantic_request_projection
```

Resultado:

```text
23 passed, 1 warning
```

La advertencia corresponde a cache de pytest y no afecta el resultado funcional.

## 8. Patch productivo

```text
SIN PATCH PRODUCTIVO
```

Los tests focales validaron el proyector existente sin requerir cambios en código productivo.
