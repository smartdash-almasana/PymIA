# OWNER_SEMANTIC_EVIDENCE_REQUESTS_CONTRACT_CHECKPOINT

Fecha: 2026-06-10
Estado: PASS
Tipo: contrato puro

## VEREDICTO

```text
PASS
```

## Alcance

Se validó el contrato `OwnerSemanticEvidenceRequest` como representación mínima de pedidos semánticos de evidencia estructural.

Este frente no implementa builder, runtime conversacional, integración con graph, DiagnosticCore, Telegram, Hermes, ERP, PDF productivo ni fórmulas.

## Decisiones contractuales

- La narrativa del dueño puede refinar el pedido owner-facing de evidencia.
- La narrativa del dueño no destraba evidencia estructural.
- `does_resolve_structural_input` debe permanecer `False`.
- `missing_key` preserva la trazabilidad técnica.
- `missing_input_type` queda restringido a `STRUCTURAL_INPUT` en este frente.
- `required_fields` no puede estar vacío.
- `accepted_formats` no puede estar vacío.
- `confidence`, si existe, debe estar entre `0` y `1`.

## Caso certificado

Caso conceptual:

```text
missing_key = own_price
owner_answer_text = "Los precios los fui cambiando porque subió la tela."
```

Salida contractual esperada:

- preserva `missing_key = own_price`;
- preserva `semantic_signal = PRICE_VARIABILITY_DUE_TO_INPUT_COST`;
- produce `refined_request_text` owner-facing y accionable;
- conserva `does_resolve_structural_input = false`.

## Archivos modificados

```text
pymia/contracts/owner_semantic_evidence_requests.py
tests/smartpyme/test_owner_semantic_evidence_requests.py
docs/pymia/OWNER_SEMANTIC_EVIDENCE_REQUESTS_CONTRACT_TASKSPEC.md
docs/pymia/OWNER_SEMANTIC_EVIDENCE_REQUESTS_CONTRACT_CHECKPOINT.md
docs/pymia/ASSISTED_SIMULATED_PILOT_002_VALUE_CHECK.md
docs/pymia/ASSISTED_SIMULATED_PILOT_002_VALUE_CHECKPOINT.md
```

## Tests

Validación requerida:

```powershell
python -m pytest tests/smartpyme/test_owner_semantic_evidence_requests.py tests/architecture -q --basetemp .tmp_pytest_owner_semantic_evidence_requests
```

Resultado observado:

```text
9 passed, 1 warning
```

La advertencia corresponde a cache de pytest y no afecta el resultado funcional.

## Bloqueantes

```text
Ninguno al momento de crear el checkpoint.
```

## NO PUSH

No se autoriza push en este frente.
