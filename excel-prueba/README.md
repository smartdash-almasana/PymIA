# Excel de prueba — corpus A4 adversarial

Esta carpeta contiene archivos `.xlsx` diseñados para probar fallos y ambigüedades adversariales de Servicio 1.

## 01_integridad_estructural

Casos donde la estructura del Excel puede inducir conteos, joins o agregaciones incorrectas.

- `S1_A4_ADV_002_subtotal_as_operation.xlsx` — subtotales embebidos tratados como operaciones.
- `S1_A4_ADV_006_duplicate_rows.xlsx` — filas duplicadas exactas.
- `S1_A4_ADV_007_mixed_granularity.xlsx` — granularidades mezcladas dentro del mismo archivo.

## 02_calidad_numerica_y_nulos

Casos donde el significado numérico o la ausencia de valor puede confundirse.

- `S1_A4_ADV_003_zero_vs_blank.xlsx` — cero versus celda vacía.
- `S1_A4_ADV_004_inverted_signs.xlsx` — signos invertidos.
- `S1_A4_ADV_009_extreme_values.xlsx` — valores extremos.

## 03_moneda_y_temporalidad

Casos donde moneda o período pueden invalidar una comparación o cálculo.

- `S1_A4_ADV_001_mixed_currency.xlsx` — monedas mezcladas.
- `S1_A4_ADV_005_out_of_period_dates.xlsx` — fechas fuera del período esperado.

## 04_semantica_y_relaciones

Casos donde nombres plausibles o relaciones incompletas pueden provocar una interpretación incorrecta.

- `S1_A4_ADV_010_semantic_decoy_columns.xlsx` — columnas señuelo semánticas.
- `S1_A4_ADV_011_incomplete_relationships.xlsx` — relaciones incompletas entre entidades/hojas.

## 05_evidencia_insuficiente

Casos donde falta evidencia material y Servicio 1 debe bloquear de forma segura.

- `S1_A4_ADV_008_missing_material_input.xlsx` — input material ausente.

## Regla de uso

Estos archivos no son demos comerciales ni plantillas de cliente. Son fixtures adversariales. Deben conservarse separados de corpus estructural (A1), cálculo (A2), rubros (A3) y futuros archivos reales de demostración.
