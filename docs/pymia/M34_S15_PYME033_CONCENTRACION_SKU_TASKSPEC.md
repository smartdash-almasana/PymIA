# M34-S15 — PYME_033 Concentracion SKU TaskSpec

Fecha: 2026-06-08
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S15_PYME_033_CONCENTRACION_SKU`

## Objetivo

Implementar soporte determinístico para:

```text
PYME_033_concentracion_sku
```

## Fórmula fuente

Tomada de `docs/formula_catalog.v1.json`:

```text
formula_id: PYME_033_concentracion_sku
pathology_code: PYME_033
expression: main_sku_sales / total_sales * 100
required_variables:
  - main_sku_sales
  - total_sales
output_unit: percentage
```
