# M34-S14 — PYME_044 Margen Cliente TaskSpec

Fecha: 2026-06-08
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S14_PYME_044_MARGEN_CLIENTE`

## Objetivo

Implementar soporte determinístico para:

```text
PYME_044_margen_cliente
```

## Fórmula fuente

Tomada de `docs/formula_catalog.v1.json`:

```text
formula_id: PYME_044_margen_cliente
pathology_code: PYME_044
expression: client_revenue - client_direct_costs - client_service_costs
required_variables:
  - client_revenue
  - client_direct_costs
  - client_service_costs
output_unit: currency
```
