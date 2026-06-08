# M34-S16 — REN_002 Coeficiente Reposicion TaskSpec

Fecha: 2026-06-08
Frente activo: `DIAGNOSTIC_CORE_V1`
Slice: `M34-S16_REN_002_COEFICIENTE_REPOSICION`

## Objetivo

Implementar soporte determinístico para:

```text
REN_002_coeficiente_reposicion
```

## Fórmula fuente

Tomada de `docs/formula_catalog.v1.json`:

```text
formula_id: REN_002_coeficiente_reposicion
pathology_code: REN_002
expression: closing_index / origin_index
required_variables:
  - closing_index
  - origin_index
output_unit: ratio
```
