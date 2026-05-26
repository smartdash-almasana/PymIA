# SMARTPYME_DELIVERY_MARKDOWN_MINIMAL

Estado: DRAFT IMPLEMENTED

## Objetivo

Renderizar un `DeliveryPackage` a Markdown legible para tenant, con una función
pura y determinística.

## Archivos

- `pymia/smartpyme/delivery_markdown.py`
- `tests/smartpyme/test_delivery_markdown.py`

## API pública

- `render_delivery_markdown(package) -> str`

## Entrada

`package` puede ser:

- `dict`
- objeto con `to_dict()` que devuelva `dict` (ej. `DeliveryPackage`)

Si el input no cumple contrato, lanza `ValueError`.

## Salida

Markdown con estructura:

- encabezado general
- status/tenant/intake/classification/created
- summary
- output references
- warnings
- reasons

## Placeholders

Si listas están vacías, renderiza:

- `No output references.`
- `No warnings.`
- `No reasons.`

## Restricciones

- No escribe archivos.
- No valida filesystem.
- No ejecuta microservicios.
- No importa `excel_diagnostic`.
- No importa `supplier_duplicate_check`.
- No muta inputs.

## Validación

- `test_delivery_markdown.py` (12 tests)
- regresión con `test_delivery_package.py`
- regresión con `test_execution_result_gate.py`
