# Servicio 1 — Excel Reality Lab A4 Adversarial Matrix V1

**Fecha:** 2026-08-15
**Estado:** BLOCKED_BY_2_CONFIRMED_DEFECTS

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
PASS_NEEDS_OWNER: 6
PASS_NEEDS_EVIDENCE: 2
PASS_BLOCKED_FAIL_CLOSED: 0
FAIL_DEFECT: 2
UNSAFE_EXECUTIONS: 0
UNCONTROLLED_CRASHES: 0
VERDICT: FAIL_ADVERSARIAL_MATRIX_V1
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

### A4-D01 — MIXED_CURRENCY_WITHOUT_SAFE_SIGNAL

```text
case_id: S1-A4-001
fixture: S1_A4_ADV_001_mixed_currency.xlsx
observed: curation_status=CURATED; unknown_fields=[]; ambiguous_fields=[]
pathology: una misma columna monetaria contiene ARS y USD sin evidencia FX
risk: montos de distinta moneda podrían atravesar curación sin señal material de conflicto
root_cause_candidate: la curación perfila semántica de columnas pero no gobierna consistencia de unidad/moneda a nivel de valores
required_resolution: detectar incompatibilidad de moneda/unidad antes de autorizar un cálculo monetario agregado; no convertir moneda ni inventar FX
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

### A4-D03 — OUT_OF_PERIOD_DATES_WITHOUT_SAFE_SIGNAL

```text
case_id: S1-A4-005
fixture: S1_A4_ADV_005_out_of_period_dates.xlsx
observed: curation_status=CURATED; fechas 2025-12-31, julio 2026 y 2026-08-01 conviven sin señal
risk: un cálculo con período implícito podría consumir filas fuera de alcance
root_cause_candidate: intake no posee authority de período; la protección debe existir donde el período del cálculo esté gobernado
required_resolution: validar membership temporal contra período explícito antes de agregación; no inferir período sólo por mayoría de fechas
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
A4_STATUS: BLOCKED_BY_2_CONFIRMED_DEFECTS
A5_REAL_CLIENT_SHADOW_RUNS: NOT_AUTHORIZED_YET
A4-D02 TOTAL_ROWS_CAN_FLOW_AS_OPERATIONS_WITHOUT_SAFE_SIGNAL: RESOLVED (FIX_A4_TOTAL_ROWS_SAFE_SIGNAL_V1)
A4-D04 DUPLICATE_ROWS_WITHOUT_SAFE_SIGNAL: RESOLVED (FIX_A4_DUPLICATE_ROWS_SAFE_SIGNAL_V1)
```

Orden de resolución restante:

```text
1. MIXED_CURRENCY unit consistency guard (A4-D01)
2. OUT_OF_PERIOD period-membership guard (A4-D03)
```

Cada defecto debe cerrarse en un corte independiente con fixture de regresión A4, cambio mínimo en la authority correcta, focal tests, architecture baseline y rerun completo de A4.
