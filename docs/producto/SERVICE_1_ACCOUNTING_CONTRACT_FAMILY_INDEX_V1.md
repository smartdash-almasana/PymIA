# SERVICE_1_ACCOUNTING_CONTRACT_FAMILY_INDEX_V1

VEREDICT:

```text
SERVICE_1_ACCOUNTING_CONTRACT_FAMILY_INDEX_V1: IMPLEMENTED_DOC_INDEX
```

PURPOSE:

```text
Índice operativo de la familia contractual contable mínima de Servicio 1.
Agrupa contrato base, contratos específicos, documentación de cierre, tests y próximo frente autorizado.
```

BASE CONTRACT:

```text
Doc:
docs/producto/SERVICE_1_ACCOUNTING_CONTRACTS_V1.md

Runtime contract:
PymIA-Live/pymia/smartpyme/service_1_accounting_contracts_v1.py

Tests:
PymIA-Live/tests/smartpyme/test_service_1_accounting_contracts_v1.py

Commit:
92509d2 feat(pymia-live): add service 1 accounting contracts
```

SPECIFIC CONTRACTS:

```text
1. Bank reconciliation
   Doc: docs/producto/SERVICE_1_BANK_RECONCILIATION_CONTRACT_V1.md
   Runtime contract: PymIA-Live/pymia/smartpyme/bank_reconciliation_contract_v1.py
   Tests: PymIA-Live/tests/smartpyme/test_bank_reconciliation_contract_v1.py
   Commit: a3be116 feat(pymia-live): add service 1 bank reconciliation contract

2. Payment platform reconciliation
   Doc: docs/producto/SERVICE_1_MERCADO_PAGO_RECONCILIATION_CONTRACT_V1.md
   Runtime contract: PymIA-Live/pymia/smartpyme/mercado_pago_reconciliation_contract_v1.py
   Tests: PymIA-Live/tests/smartpyme/test_mercado_pago_reconciliation_contract_v1.py
   Commit: 4fb1f16 feat(pymia-live): add service 1 mercado pago reconciliation contract

3. Invoice collection matching
   Doc: docs/producto/SERVICE_1_INVOICE_COLLECTION_MATCHING_CONTRACT_V1.md
   Runtime contract: PymIA-Live/pymia/smartpyme/invoice_collection_matching_contract_v1.py
   Tests: PymIA-Live/tests/smartpyme/test_invoice_collection_matching_contract_v1.py
   Commit: f2cf519 feat(pymia-live): add service 1 invoice collection matching contract

4. Supplier purchase review
   Doc: docs/producto/SERVICE_1_SUPPLIER_PURCHASE_REVIEW_CONTRACT_V1.md
   Runtime contract: PymIA-Live/pymia/smartpyme/supplier_purchase_review_contract_v1.py
   Tests: PymIA-Live/tests/smartpyme/test_supplier_purchase_review_contract_v1.py
   Commit: 9ba3386 feat(pymia-live): add service 1 supplier purchase review contract

5. Accounting workpaper
   Doc: docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_CONTRACT_V1.md
   Runtime contract: PymIA-Live/pymia/smartpyme/accounting_workpaper_contract_v1.py
   Tests: PymIA-Live/tests/smartpyme/test_accounting_workpaper_contract_v1.py
   Commit: 8016073 feat(pymia-live): add service 1 accounting workpaper contract
```

FAMILY CLOSURE:

```text
Doc:
docs/producto/SERVICE_1_ACCOUNTING_CONTRACT_FAMILY_CLOSURE_V1.md

Scope:
Cierra la familia contable mínima como capa contractual pura.
No autoriza runtime contable real.
No autoriza conciliación real.
No autoriza matching real.
No autoriza generación final de papeles de trabajo.
```

COMMON DESIGN:

```text
Todos los contratos específicos:
- especializan service_1_accounting_contracts_v1.py;
- declaran fuentes requeridas;
- declaran campos requeridos;
- calculan faltantes;
- devuelven estado;
- devuelven next_allowed_action;
- mantienen runtime_authorized=False;
- producen delivery_input compatible con Service1XlsxDeliveryInputV1.
```

FAMILY CAPABILITIES:

```text
bank_reconciliation_basic
mercado_pago_reconciliation_basic
invoice_collection_matching_basic
supplier_purchase_review_basic
accounting_workpaper_basic
```

FAMILY LIMITS:

```text
No IO.
No openpyxl en contratos.
No First Aid.
No Exceland runtime.
No FSM.
No LLM.
No chatbot.
No OCR.
No parser PDF.
No bancos reales.
No integraciones externas.
No vertical_slice.py.
No asientos automáticos.
No exactitud fiscal.
No auditoría contable certificada.
No conciliación cerrada.
```

VALIDATION COMMAND:

```text
python -m pytest tests/smartpyme/test_service_1_accounting_contracts_v1.py tests/smartpyme/test_bank_reconciliation_contract_v1.py tests/smartpyme/test_mercado_pago_reconciliation_contract_v1.py tests/smartpyme/test_invoice_collection_matching_contract_v1.py tests/smartpyme/test_supplier_purchase_review_contract_v1.py tests/smartpyme/test_accounting_workpaper_contract_v1.py tests/smartpyme/test_service_1_xlsx_delivery_v1.py -q
```

LAST_VALIDATED_RESULT:

```text
69 passed in 2.17s
```

PRODUCT MEANING:

```text
Servicio 1 puede representar cinco demandas contables frecuentes como contratos seguros, trazables y exportables.
La familia está lista para futuros runtimes específicos, pero todavía permanece en modo contractual.
```

NEXT_AUTHORIZED_FRONT:

```text
SERVICE_1_ACCOUNTING_RUNTIME_AUTHORIZATION_MATRIX_V1
```

DO_NOT_START_WITHOUT_NEW_BLOCK:

```text
No implementar runtime de conciliación.
No implementar matching real.
No leer archivos contables reales.
No generar workpapers finales.
No integrar bancos, plataformas de pago ni APIs externas.
```
