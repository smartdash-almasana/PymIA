# SERVICE_1_INVOICE_COLLECTION_MATCHING_CONTRACT_V1

VEREDICT:

```text
IMPLEMENTED_MINIMAL_SPECIFIC_CONTRACT
```

FILES_CREATED:

```text
PymIA-Live/pymia/smartpyme/invoice_collection_matching_contract_v1.py
PymIA-Live/tests/smartpyme/test_invoice_collection_matching_contract_v1.py
docs/producto/SERVICE_1_INVOICE_COLLECTION_MATCHING_CONTRACT_V1.md
```

FILES_MODIFIED:

```text
None
```

ALCANCE EXACTO:

```text
Contrato específico para revisión manual facturas-cobros dentro de Servicio 1.
Especializa service_1_accounting_contracts_v1.py.
No ejecuta matching real.
No calcula diferencias reales.
No lee registros de facturas.
No lee registros de cobros.
No produce asientos.
No confirma cobranzas aplicadas.
Produce delivery_input compatible con Service1XlsxDeliveryInputV1.
```

ESTADOS:

```text
READY_FOR_REVIEW
MISSING_INVOICE_REGISTER
MISSING_COLLECTION_REGISTER
MISSING_FIELDS
INVALID_INPUT
```

FUENTES REQUERIDAS:

```text
registro_facturas
registro_cobros
```

CAMPOS REQUERIDOS:

```text
fecha
cliente
numero_factura
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
No matching cerrado.
No auditoría contable certificada.
No exactitud fiscal.
No asientos automáticos.
```

TESTS:

```text
python -m pytest tests/smartpyme/test_invoice_collection_matching_contract_v1.py tests/smartpyme/test_service_1_accounting_contracts_v1.py tests/smartpyme/test_service_1_xlsx_delivery_v1.py -q
29 passed in 2.35s
```

GIT_STATUS:

```text
PENDING_VALIDATION
```

NEXT_BLOCK:

```text
SERVICE_1_SUPPLIER_PURCHASE_REVIEW_CONTRACT_V1
```

COMMIT_READY:

```text
YES
```
