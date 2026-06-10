# OWNER_SEMANTIC_EVIDENCE_REQUEST_BUILDER_CHECKPOINT

Fecha: 2026-06-10
Estado: PASS
Frente: OWNER_SEMANTIC_EVIDENCE_REQUEST_BUILDER

## 1. Veredicto

```text
PASS
```

Se agregó un builder mínimo para convertir faltantes estructurales + narrativa del dueño en pedidos de evidencia accionables.

Este checkpoint declara cierre con tests focales y arquitectura.

## 2. Archivo agregado

```text
pymia/smartpyme/owner_semantic_evidence_request_builder.py
```

## 3. Capacidad agregada

Función pública:

```python
build_owner_semantic_evidence_request(...)
```

Responsabilidad:

```text
missing_key estructural + owner_answer_text + source_ref
→ OwnerSemanticEvidenceRequest validado
```

## 4. Casos iniciales soportados

```text
own_price
average_stock
dso
```

### own_price

Caso narrativo típico:

```text
Los precios los fui cambiando porque subió la tela.
```

Pedido refinado esperado:

```text
precios de venta por producto/SKU de la última semana y vigencia de precios si cambiaron durante el período.
```

### average_stock

Caso narrativo típico:

```text
El stock lo llevo a ojo.
```

Pedido refinado esperado:

```text
stock inicial y stock final por producto, admitiendo estimación marcada como estimada si no existe dato exacto.
```

### dso

Caso narrativo típico:

```text
Algunos clientes pagan tarde o se atrasan.
```

Pedido refinado esperado:

```text
cliente, importe, fecha de factura o venta y fecha real de cobro o plazo aproximado.
```

## 5. Regla soberana preservada

```text
La narrativa del dueño refina el pedido.
No resuelve evidencia estructural.
No produce findings.
No modifica DiagnosticCore.
```

Todo request construido mantiene:

```text
does_resolve_structural_input = False
missing_input_type = STRUCTURAL_INPUT
missing_key preservado
```

## 6. No tocado

No se modificó:

```text
DiagnosticCore
graph
runtime
Telegram
Hermes runtime
ERP
PDF
fórmulas
owner_answers_evaluator
```

## 7. Validación ejecutada

Codex creó tests focales y ejecutó:

```text
python -m pytest tests/smartpyme/test_owner_semantic_evidence_request_builder.py tests/smartpyme/test_owner_semantic_evidence_requests.py tests/architecture -q --basetemp .tmp_pytest_owner_semantic_evidence_request_builder
```

Resultado:

```text
18 passed, 1 warning
```

La advertencia corresponde a cache de pytest y no afecta el resultado funcional.

## 8. Criterios de aceptación esperados

- `own_price` + narrativa de suba de tela genera `PRICE_VARIABILITY_DUE_TO_INPUT_COST`.
- `average_stock` + narrativa informal genera pedido de stock inicial/final.
- `dso` + narrativa de atraso genera pedido de fechas/plazos de cobro.
- Caso soportado sin términos específicos baja confianza, pero mantiene pedido accionable.
- `missing_key` no soportado falla cerrado.
- `does_resolve_structural_input` permanece `False`.
- No se modifican módulos prohibidos.

## 9. Patch productivo

```text
SIN PATCH PRODUCTIVO
```

Los tests focales validaron el builder existente sin requerir cambios.
