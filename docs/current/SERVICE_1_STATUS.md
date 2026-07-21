# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-21

**Última regresión completa observada:** `821 passed, 0 failed`, ejecutada en local después del cierre de `CYCLE_053`.

## Estado

```text
SERVICE_1_PRODUCT_COMPLETION_GATE: PASS
SERVICIO 1 MVP DETERMINÍSTICO ASISTIDO: COMPLETO
12/12 PATOLOGÍAS PRODUCTIVAS CONECTADAS
RAÍZ PRODUCTIVA CANÓNICA ÚNICA: ACTIVA
CLI CANÓNICO: ACTIVO
DPO: PRERREQUISITO TÉCNICO DE PYME_013
KERNEL GENÉRICO PRODUCTIVO: ACTIVO
SELECCIÓN EXPLÍCITA DE CAPACIDAD: OBLIGATORIA
SIN LLM RUNTIME
SIN DIAGNÓSTICO CAUSAL
DELIVERY BLOQUEADO SALVO AUTORIZACIÓN EXPLÍCITA
CYCLE_053_GLOBAL_12_PATHOLOGY_CLOSURE: CLOSED_PASS
```

## Alcance certificado

Servicio 1 está certificado para:

- leer XLSX real por la CLI oficial;
- preguntar al dueño por columnas cuando falta confirmación;
- construir salida canónica de ingesta;
- pasar por comprensión semántica determinística;
- rechazar reentrada semántica de texto libre;
- construir planes gobernados por solicitud explícita;
- ejecutar las 12 patologías productivas con evidencia normalizada y bindings confirmados;
- producir clasificaciones y outcomes acotados sin atribución causal;
- mantener en falso `runtime_authorized`, `tool_execution_authorized`, `product_ready`, `delivery_authorized` y `diagnosis_generated`;
- producir salida trazable.

## Capacidades productivas actuales (12/12)

| Patología | Capacidad | Entrega |
|---|---|---|
| `LIQ_001` | `sold_vs_collected_gap` | XLSX sólo con solicitud explícita |
| `REN_001` | `net_margin_real` | no autorizada |
| `LIQ_002` | `projected_closing_cash_balance` | no autorizada |
| `PYME_011` | `dso` | no autorizada |
| `PYME_013` | `payment_collection_gap` | no autorizada |
| `INV_001` | `reorder_point` | no autorizada |
| `INV_002` | `inventory_turnover` | no autorizada |
| `PYME_024` | `current_ratio` | no autorizada |
| `PYME_033` | `sales_concentration` | no autorizada |
| `REN_002` | `index_update_ratio` | no autorizada |
| `PYME_027` | `interest_burden_ratio` | no autorizada |
| `PYME_026` | `adjusted_operating_cash_flow` | no autorizada |

**DPO** (`dpo`) permanece como prerrequisito técnico de `PYME_013`, no como una decimotercera patología productiva.

## Raíz técnica

```text
pymia/cli/service_1_product.py
pymia/smartpyme/service_1_product_pipeline_v1.py
```

No existe una segunda raíz productiva.

## Kernel genérico productivo

Las 10 capacidades genéricas (todas excepto LIQ_001 y REN_001) se ejecutan a través de `execute_generic_capability_v1` en `service_1_generic_capability_engine_v1.py`. Cada capacidad queda definida por un `CapabilityDefinitionV1` en `service_1_capability_registry_v1.py` y es seleccionada explícitamente por `requested_capability`.

## Límites honestos

- Completo no significa CRM, SaaS, Servicio 2/3 ni automatización LLM.
- Completo no significa que todas las entregas estén autorizadas — el delivery permanece bloqueado salvo `--deliver-result`.
- No existe selección automática de tool o capacidad desde el contenido del Excel.
- La confirmación del dueño sigue siendo parte del producto.
- Scrap y OEE no son capacidades soportadas actualmente.
- Las fórmulas con supuestos exigen evidencia y convenciones explícitas.

## Próximo ciclo autorizado

```text
PENDIENTE DE ASIGNACIÓN
```
