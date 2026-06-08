# M35-S5 — Extend Evidence Binding New Formulas TaskSpec

Fecha: 2026-06-08
Frente activo: `M35_EVIDENCE_TO_CORE_BINDING`
Slice: `M35-S5_EXTEND_EVIDENCE_BINDING_NEW_FORMULAS`

## Objetivo

Extender `StructuredEvidence.computed_variables -> DiagnosticCoreInput` para:

```text
PYME_044_margen_cliente
PYME_033_concentracion_sku
REN_002_coeficiente_reposicion
```

## Mapping mínimo

### PYME_044_margen_cliente

```text
client_revenue <- client_revenue | ingresos_cliente
client_direct_costs <- client_direct_costs | costos_directos_cliente
client_service_costs <- client_service_costs | costos_servicio_cliente
```

### PYME_033_concentracion_sku

```text
main_sku_sales <- main_sku_sales | ventas_sku_principal
total_sales <- total_sales | ventas_total
```

### REN_002_coeficiente_reposicion

```text
closing_index <- closing_index | indice_cierre
origin_index <- origin_index | indice_origen
```
