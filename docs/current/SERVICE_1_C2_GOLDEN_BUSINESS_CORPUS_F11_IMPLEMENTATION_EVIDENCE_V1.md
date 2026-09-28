# SERVICE_1_C2_GOLDEN_BUSINESS_CORPUS_F11_IMPLEMENTATION_EVIDENCE_V1

## Estado

IMPLEMENTED / VERIFIED / PASS

## Propósito

F11 consolida un Golden Business Corpus multi-negocio para C2 V2 usando XLSX físicos ya existentes del repo. El corpus es EVIDENCE_ONLY / NON_NORMATIVE: fija expectativas y safe-unknowns para auditoría; no se convierte en autoridad runtime ni semántica.

## Casos físicos

7 contextos:

1. ventas/margen
2. textil ventas
3. textil compras
4. textil stock
5. cobranzas
6. taller mecánico
7. caja/banco como safe-unknown control

Fuentes físicas bajo `prueba_excels/`.

## Artefactos

- `docs/current/SERVICE_1_C2_GOLDEN_BUSINESS_CORPUS_F11_V1.json`
- `pymia/smartpyme/service_1_c2_golden_business_corpus_v1.py`
- `tests/smartpyme/test_service_1_c2_golden_business_corpus_v1.py`

## Qué verifica el evaluator

- cada workbook físico existe;
- pasa por canonical XLSX intake;
- reutiliza canonical ingestion y workbook profile;
- construye `workbook_semantic_context` sin segundo parser;
- cada sheet/columna Golden existe físicamente;
- cada expectativa V2 usa únicamente valores de la taxonomía gobernada;
- safe-unknown columns siguen explícitas y no se convierten en una verdad arbitraria;
- authority flags permanecen false;
- los nuevos componentes C2 no contienen switches por caso/sector.

## Alcance exacto

Este gate NO afirma calidad del LLM en vivo. F11 fija el corpus contractual para que la auditoría F12 pueda verificar conjuntamente F0-F11 y, cuando corresponda, ejecutar pruebas del provider configurado.

El corpus previo `SERVICE_1_PHYSICAL_XLSX_MULTI_SECTOR_PRODUCT_READINESS_CORPUS_V1` se usa como base de evidencia física y terminología de casos; no se promueven sus semantic roles legacy como nueva autoridad.

## Test gate

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_c2_golden_business_corpus_v1.py \
  tests/smartpyme/test_service_1_c2_v2_taller_real_flow.py \
  tests/smartpyme/test_service_1_c2_v2_retirement_f10.py \
  tests/smartpyme/test_service_1_semantic_coordinate_model_v2.py
```

Resultado:

```text
15 passed / 0 failed
```

## Seguridad

```text
runtime_authorized = false
tool_execution_authorized = false
product_ready = false
delivery_authorized = false
automatic_reuse_authorized = false
```

## Veredicto F11

PASS.

STOP_AFTER: F11.
F12 no iniciado en esta microtarea.
