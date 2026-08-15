# Servicio 1 — Excel Reality Lab A4 Adversarial Matrix V1

**Fecha:** 2026-08-15
**Estado:** PASS_ADVERSARIAL_MATRIX_V1

## Objetivo

Someter el intake/semántica/computabilidad de Servicio 1 a XLSX adversariales mínimos y verificar que entradas engañosas no produzcan interpretación o ejecución insegura.

Fixtures:

`excel-prueba/S1_A4_ADV_001..011_*.xlsx`

Evaluador:

`tools/service_1_excel_reality_lab_a4_adversarial_matrix_v1.py`

## Resultado

```text
CASES: 11
PASS_COMPUTABLE: 1
PASS_NEEDS_OWNER: 8
PASS_NEEDS_EVIDENCE: 2
PASS_BLOCKED_FAIL_CLOSED: 0
FAIL_DEFECT: 0
UNSAFE_EXECUTIONS: 0
UNCONTROLLED_CRASHES: 0
VERDICT: PASS_ADVERSARIAL_MATRIX_V1
```

A4 no autoriza cambios productivos por sí mismo. Cada defecto requiere corte causal independiente.

## Casos seguros

```text
S1-A4-003 ZERO_VS_BLANK
  PASS_NEEDS_EVIDENCE
  cero preservado como 0; vacío preservado como ausencia.

S1-A4-004 INVERTED_SIGNS
  PASS_NEEDS_OWNER
  concepto/importe quedan sin interpretación material silenciosa.

S1-A4-007 MIXED_GRANULARITY
  PASS_NEEDS_OWNER
  importe_factura queda fuera de resolución silenciosa.

S1-A4-008 MISSING_MATERIAL_INPUT
  PASS_NEEDS_EVIDENCE
  P8=NEEDS_EVIDENCE; governed_input=false.

S1-A4-009 EXTREME_VALUES
  PASS_COMPUTABLE
  valor extremo finito preservado; no autocorrección por plausibilidad.

S1-A4-010 SEMANTIC_DECOYS
  PASS_NEEDS_OWNER
  importes semánticamente similares quedan sin falsa confianza.

S1-A4-011 INCOMPLETE_RELATIONSHIPS
  PASS_NEEDS_OWNER
  referencias/ids incompletos no se enlazan silenciosamente.
```

## Defectos confirmados

### A4-D01 — MIXED_CURRENCY_WITHOUT_SAFE_SIGNAL — RESUELTO

```text
case_id: S1-A4-001
fixture: S1_A4_ADV_001_mixed_currency.xlsx
observed (pre-fix): curation_status=CURATED; ARS y USD convivían sin señal gobernada
pathology: una misma evidencia monetaria contiene más de una moneda explícita sin contrato FX
risk: montos de distinta moneda podrían atravesar curación y agregarse como si fueran compatibles
root_cause: DocumentCurator no gobernaba consistencia de moneda a nivel de valores dentro de una tabla
fix: FIX_A4_MIXED_CURRENCY_SAFE_SIGNAL_V1 — DocumentCurator detecta múltiples códigos de moneda explícitos dentro de la misma tabla y emite
     ambigüedad gobernada (__mixed_currency__ en ambiguous_fields) → curation PARTIAL → requiere owner review.
     Sin conversión automática, sin tipo de cambio inferido y sin modificar los importes originales.
resultado: A4-001 = PASS_NEEDS_OWNER (MIXED_CURRENCY_WITH_SAFE_SIGNAL)
```

### A4-D02 — TOTAL_ROWS_CAN_FLOW_AS_OPERATIONS_WITHOUT_SAFE_SIGNAL — RESUELTO

```text
case_id: S1-A4-002
fixture: S1_A4_ADV_002_subtotal_as_operation.xlsx
observed (pre-fix): curation_status=CURATED; filas SUBTOTAL/TOTAL permanecían dentro de la tabla sin señal gobernada
risk: doble conteo si detalle y agregados se consumen como la misma granularidad
root_cause: DocumentCurator no señalizaba la coexistencia de filas detalle con etiquetas exactas SUBTOTAL/TOTAL en comprobante
fix: FIX_A4_TOTAL_ROWS_SAFE_SIGNAL_V1 — DocumentCurator detecta SUBTOTAL/TOTAL exactos mezclados con comprobantes de detalle y emite
     ambigüedad gobernada (__embedded_total_rows__ en ambiguous_fields) → curation PARTIAL → requiere owner review.
     Sin eliminar filas, sin recalcular totales, sin reclasificar silenciosamente ni inferir granularidad por texto débil.
resultado: A4-002 = PASS_NEEDS_OWNER (TOTAL_ROWS_PRESENT_WITH_SAFE_SIGNAL)
```

### A4-D03 — OUT_OF_PERIOD_DATES_WITHOUT_SAFE_SIGNAL — RESUELTO

```text
case_id: S1-A4-005
fixture: S1_A4_ADV_005_out_of_period_dates.xlsx
observed (pre-fix): curation_status=CURATED; fechas 2025-12-31, julio 2026 y 2026-08-01 convivían sin señal
risk: un cálculo con período gobernado podía consumir filas fuera de alcance temporal
root_cause: la curación no recibía un período explícito contra el cual validar membership temporal
fix: FIX_A4_OUT_OF_PERIOD_DATES_SAFE_SIGNAL_V1 — la curación acepta period_ref explícito en formato YYYY-MM y valida fecha normalizada contra ese período.
     Si existen fechas fuera del período gobernado, emite __out_of_period_dates__ en ambiguous_fields → curation PARTIAL → requiere owner review.
     Sin period_ref, no se infiere período desde las fechas del archivo; no se borran filas ni se altera ninguna fecha.
resultado: A4-005 = PASS_NEEDS_OWNER con period_ref=2026-07
```

### A4-D04 — DUPLICATE_ROWS_WITHOUT_SAFE_SIGNAL — RESUELTO

```text
case_id: S1-A4-006
fixture: S1_A4_ADV_006_duplicate_rows.xlsx
observed (pre-fix): curation_status=CURATED; filas de negocio exactamente repetidas sin señal owner/block
risk: doble conteo; también existe posibilidad de duplicados legítimos, por lo que auto-deduplicar sería incorrecto
root_cause_candidate: no existe señal gobernada de duplicidad de registros dentro de una tabla
fix: FIX_A4_DUPLICATE_ROWS_SAFE_SIGNAL_V1 — DocumentCurator.build_report detecta filas exactamente duplicadas y emite
     ambigüedad gobernada (__duplicate_rows__ en ambiguous_fields) → curation PARTIAL → requiere owner review.
     Sin auto-dedup, sin selección de fila, sin asumir error: los duplicados legítimos quedan representados.
resultado: A4-006 = PASS_NEEDS_OWNER (DUPLICATE_ROWS_PRESENT_WITH_SAFE_SIGNAL)
```

## Invariantes preservadas en A4

```text
NO_SECOND_XLSX_PARSER
NO_PRODUCT_ROOT_CHANGE
NO_P6_P7_P8_KERNEL_CHANGE
NO_AUTOMATIC_FIX_OF_PRODUCT_DEFECTS
NO_UNSAFE_EXECUTION
```

## Decisión

```text
A4_STATUS: PASS_ADVERSARIAL_MATRIX_V1
A5_REAL_CLIENT_SHADOW_RUNS: NOT_AUTHORIZED_YET
A4-D01 MIXED_CURRENCY_WITHOUT_SAFE_SIGNAL: RESOLVED (FIX_A4_MIXED_CURRENCY_SAFE_SIGNAL_V1)
A4-D02 TOTAL_ROWS_CAN_FLOW_AS_OPERATIONS_WITHOUT_SAFE_SIGNAL: RESOLVED (FIX_A4_TOTAL_ROWS_SAFE_SIGNAL_V1)
A4-D03 OUT_OF_PERIOD_DATES_WITHOUT_SAFE_SIGNAL: RESOLVED (FIX_A4_OUT_OF_PERIOD_DATES_SAFE_SIGNAL_V1)
A4-D04 DUPLICATE_ROWS_WITHOUT_SAFE_SIGNAL: RESOLVED (FIX_A4_DUPLICATE_ROWS_SAFE_SIGNAL_V1)
```

Orden de resolución restante:

```text
NONE
```

A4 queda cerrado con los cuatro defectos resueltos en cortes independientes, fixtures de regresión, focal tests y architecture baseline.
