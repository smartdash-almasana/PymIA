# SERVICE_1_SUPPLIER_PURCHASE_REVIEW_CONTRACT_V1

VEREDICT:

```text
IMPLEMENTED_MINIMAL_SPECIFIC_CONTRACT
```

FILES_CREATED:

```text
pymia/smartpyme/supplier_purchase_review_contract_v1.py
tests/smartpyme/test_supplier_purchase_review_contract_v1.py
docs/producto/SERVICE_1_SUPPLIER_PURCHASE_REVIEW_CONTRACT_V1.md
```

FILES_MODIFIED:

```text
None
```

ALCANCE EXACTO:

```text
Contrato específico para revisión manual compras-proveedores dentro de Servicio 1.
Especializa service_1_accounting_contracts_v1.py.
No ejecuta revisión real de compras.
No valida precios.
No valida impuestos.
No lee registros de proveedores.
No lee registros de compras.
No produce asientos.
No confirma comprobantes correctos ni deuda exigible.
Produce delivery_input compatible con Service1XlsxDeliveryInputV1.
```

ESTADOS:

```text
READY_FOR_REVIEW
MISSING_SUPPLIER_REGISTER
MISSING_PURCHASE_REGISTER
MISSING_FIELDS
INVALID_INPUT
```

FUENTES REQUERIDAS:

```text
registro_proveedores
registro_compras
```

CAMPOS REQUERIDOS:

```text
fecha
proveedor
numero_comprobante
importe
```

LIMITS PRESERVED:

```text
No IO.
No openpyxl en el contrato.
No First Aid.
No Exceland runtime.
No FSM.
No LLM.
No chatbot.
No OCR.
No parser PDF.
No integración externa.
No bancos reales.
No Mercado Pago.
No vertical_slice.py.
No auditoría contable certificada.
No exactitud fiscal.
No validación impositiva.
No asientos automáticos.
```

TESTS:

```text
python -m pytest tests/smartpyme/test_supplier_purchase_review_contract_v1.py tests/smartpyme/test_service_1_accounting_contracts_v1.py tests/smartpyme/test_service_1_xlsx_delivery_v1.py -q
29 passed in 3.51s
```

GIT_STATUS:

```text
PENDING_VALIDATION
```

NEXT_BLOCK:

```text
SERVICE_1_ACCOUNTING_WORKPAPER_CONTRACT_V1
```

COMMIT_READY:

```text
YES
```
