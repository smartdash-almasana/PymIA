# SERVICE_1_EXCEL_TREATMENT_LAB_PRODUCTIZATION_V1

## Estado

```text
Tipo: IMPLEMENTATION BLOCK
Estado: IMPLEMENTED_PENDING_COMMIT
Runtime impact: EXCEL_LAB_LOGICAL_LAYER_ONLY
Code impact: YES
Tests impact: YES
Commit autorizado: NO
Push autorizado: NO
```

## Propósito

Productizar `Excel Treatment Lab` como familia estructural mínima de Servicio 1 sobre el delivery XLSX genérico ya cerrado en:

```text
PymIA-Live/pymia/smartpyme/service_1_xlsx_delivery_v1.py
```

Sin abrir chatbot, LLM, FSM, conciliación bancaria, Mercado Pago, IVA/IIBB, asientos automáticos ni `vertical_slice.py`.

## Veredicto

```text
SERVICE_1_EXCEL_TREATMENT_LAB_PRODUCTIZATION_V1: IMPLEMENTED_MINIMAL_CONTRACT
```

Se creó una capa pura y determinística:

```text
PymIA-Live/pymia/smartpyme/excel_treatment_lab_v1.py
```

que recibe hechos ya declarados del Laboratorio Excel y devuelve un resultado compatible con `Service1XlsxDeliveryInputV1`.

## Diseño aplicado

### Input mínimo

`ExcelTreatmentLabInputV1` acepta solamente contrato lógico declarado:

- `source_file`
- `detected_columns`
- `confirmed_columns`
- `rows_processed`
- `warnings`
- `missing_inputs`
- `limitations`
- `forbidden_claims`
- `owner_summary`
- `technical_notes`

### Output mínimo

`build_excel_treatment_lab_v1(...)` devuelve un payload tipado que:

- mantiene top-level propio de Excel Treatment Lab;
- incluye `service_name = SERVICE_1`;
- fija `capability_ref = excel_treatment_lab_v1`;
- fija `runtime_authorized = False`;
- es compatible directamente con `build_service_1_xlsx_delivery_v1(...)`.

### Estados soportados

```text
OK
MISSING_INPUTS
MISSING_CONFIRMATION
INVALID_INPUT
```

Reglas mínimas:

- `INVALID_INPUT` si `rows_processed < 0`
- `MISSING_INPUTS` si falta `source_file` o `detected_columns`
- `MISSING_CONFIRMATION` si hay columnas detectadas sin confirmar
- `OK` si todas las columnas detectadas quedaron confirmadas

## Límites preservados

Este bloque:

```text
no usa openpyxl
no lee archivos reales
no hace IO
no ejecuta normalización real
no infiere columnas con IA
no llama LLM
no llama pipeline
no llama FSM
no llama document_ingestion
no depende de First Aid
no duplica el delivery XLSX
```

## Archivos creados

```text
PymIA-Live/pymia/smartpyme/excel_treatment_lab_v1.py
PymIA-Live/tests/smartpyme/test_excel_treatment_lab_v1.py
docs/producto/SERVICE_1_EXCEL_TREATMENT_LAB_PRODUCTIZATION_V1.md
```

## Tests ejecutados

Suite focal ejecutada:

```text
python -m pytest tests/smartpyme/test_excel_treatment_lab_v1.py tests/smartpyme/test_service_1_xlsx_delivery_v1.py -q
15 passed in 2.23s
```

## Próximo bloque natural

```text
Conectar esta frontera lógica con una frontera estable posterior de curación/confirmación,
sin abrir todavía pipeline full, FSM, LLM ni chatbot.
```
