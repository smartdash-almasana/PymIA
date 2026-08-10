# SERVICE_1_REN_001_SELLABLE_VERTICAL_CLOSURE_V1_TASKSPEC

## Objetivo

Cerrar el único gap físico observado entre `REN_001 / net_margin_real` y la vertical vendible ya probada de `LIQ_001`: exponer en la web el delivery XLSX que la raíz productiva de REN_001 ya sabe generar.

## Estado previo probado

REN_001 ya dispone de:

```text
XLSX
→ confirmación semántica del dueño
→ P6
→ P7
→ P8
→ Service1GovernedComputationInputV1
→ ejecución determinística REN_001
→ bounded outcome
→ build_service_1_xlsx_delivery_v1
```

`service_1_product_pipeline_v1` ya genera `delivery_result` para `net_margin_real` cuando recibe `deliver_result=True`.

## Gap exacto

La capa `service_1_assisted_web_v1` actualmente:

1. solicita `deliver_result=True` únicamente para `sold_vs_collected_gap`;
2. solo expone `/download-sales-collections`;
3. muestra para REN_001 el mensaje genérico de descarga no habilitada.

## Corte autorizado

```text
SERVICE_1_REN_001_SELLABLE_VERTICAL_CLOSURE_V1
```

Implementar únicamente:

```text
run_review(net_margin_real)
→ deliver_result=True
→ delivery_generated=True si P10/delivery existente pasa
→ enlace /download-net-margin
→ lectura segura del delivery desde last_review_result
→ descarga XLSX
```

## Invariantes

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_NEW_DELIVERY_ENGINE
NO_NEW_P10_GATE
NO_LLM_RUNTIME_AUTHORITY
NO_AUTO_CAPABILITY_SELECTION
OWNER_CONFIRMATION_REMAINS_REQUIRED
P6_P7_P8_REMAIN_REQUIRED
FAIL_CLOSED
```

## No alcance

- No modificar evaluator, normalized evidence ni outcome REN_001 salvo fallo demostrado.
- No crear segunda raíz productiva.
- No crear nuevo formato XLSX.
- No habilitar otra capacidad.
- No refactor general de downloads.
- No UX amplia.

## Acceptance

1. La web solicita delivery para `net_margin_real`.
2. Un packet REN_001 sin delivery no ofrece descarga.
3. Un packet REN_001 con `delivery_generated=True` ofrece `/download-net-margin`.
4. El endpoint solo sirve el archivo de la sesión y dentro de `output_dir`.
5. Archivo inexistente o path inválido falla cerrado.
6. LIQ_001 conserva su comportamiento actual.
7. Tests focales PASS.
8. Luego se exige E2E físico real antes de declarar el corte cerrado.
