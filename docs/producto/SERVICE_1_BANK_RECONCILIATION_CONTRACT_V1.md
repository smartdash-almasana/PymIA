# SERVICE_1_BANK_RECONCILIATION_CONTRACT_V1

VEREDICT:

```text
SERVICE_1_BANK_RECONCILIATION_CONTRACT_V1: IMPLEMENTED_MINIMAL_SPECIFIC_CONTRACT
```

FILES_CREATED:

```text
PymIA-Live/pymia/smartpyme/bank_reconciliation_contract_v1.py
PymIA-Live/tests/smartpyme/test_bank_reconciliation_contract_v1.py
docs/producto/SERVICE_1_BANK_RECONCILIATION_CONTRACT_V1.md
```

FILES_MODIFIED:

```text
None
```

ALCANCE EXACTO:

```text
Se crea un contrato específico de conciliación bancaria para Servicio 1.
Especializa la capa service_1_accounting_contracts_v1.py.
No ejecuta conciliación bancaria real.
No hace matching de movimientos.
No calcula diferencias reales.
No lee extractos.
No lee archivos contables.
No produce asientos.
No confirma saldos conciliados.
Solo define fuentes requeridas, campos requeridos, faltantes, estado y next_allowed_action.
Produce delivery_input compatible con Service1XlsxDeliveryInputV1.
```

ESTADOS:

```text
READY_FOR_REVIEW
MISSING_BANK_STATEMENT
MISSING_INTERNAL_LEDGER
MISSING_FIELDS
INVALID_INPUT
```

FUENTES REQUERIDAS:

```text
extracto_banco
archivo_contable
```

CAMPOS REQUERIDOS:

```text
fecha
importe
referencia
```

LIMITS PRESERVED:

```text
No IO.
No openpyxl en el contrato.
No First Aid.
No Exceland runtime.
No Mercado Pago.
No FSM.
No LLM.
No chatbot.
No OCR.
No parser PDF.
No bancos reales.
No vertical_slice.py.
No conciliación cerrada.
No auditoría contable certificada.
No exactitud fiscal.
No asientos automáticos.
```

TESTS:

```text
python -m pytest tests/smartpyme/test_bank_reconciliation_contract_v1.py tests/smartpyme/test_service_1_accounting_contracts_v1.py tests/smartpyme/test_service_1_xlsx_delivery_v1.py -q
29 passed in 3.56s
```

GIT_STATUS:

```text
PENDING_VALIDATION
```

NEXT_BLOCK:

```text
SERVICE_1_MERCADO_PAGO_RECONCILIATION_CONTRACT_V1
```

COMMIT_READY:

```text
YES
```
