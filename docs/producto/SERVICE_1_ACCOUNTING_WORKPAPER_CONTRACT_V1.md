# SERVICE_1_ACCOUNTING_WORKPAPER_CONTRACT_V1

VEREDICT:

```text
IMPLEMENTED_MINIMAL_SPECIFIC_CONTRACT
```

FILES_CREATED:

```text
pymia/smartpyme/accounting_workpaper_contract_v1.py
tests/smartpyme/test_accounting_workpaper_contract_v1.py
docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_CONTRACT_V1.md
```

FILES_MODIFIED:

```text
None
```

ALCANCE EXACTO:

```text
Contrato específico para papel de trabajo contable dentro de Servicio 1.
Especializa service_1_accounting_contracts_v1.py.
No genera papeles de trabajo finales.
No certifica evidencia.
No valida auditoría.
No lee archivos soporte.
No lee plantillas.
No produce asientos.
Produce delivery_input compatible con Service1XlsxDeliveryInputV1.
```

ESTADOS:

```text
READY_FOR_REVIEW
MISSING_SUPPORTING_EVIDENCE
MISSING_WORKPAPER_TEMPLATE
MISSING_FIELDS
INVALID_INPUT
```

FUENTES REQUERIDAS:

```text
evidencia_soporte
plantilla_papel_trabajo
```

CAMPOS REQUERIDOS:

```text
periodo
cliente
area_revision
responsable
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
python -m pytest tests/smartpyme/test_accounting_workpaper_contract_v1.py tests/smartpyme/test_service_1_accounting_contracts_v1.py tests/smartpyme/test_service_1_xlsx_delivery_v1.py -q
29 passed in 3.08s
```

GIT_STATUS:

```text
PENDING_VALIDATION
```

NEXT_BLOCK:

```text
SERVICE_1_ACCOUNTING_CONTRACT_FAMILY_CLOSURE_V1
```

COMMIT_READY:

```text
YES
```
