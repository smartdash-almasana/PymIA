# PYME BASE ROUTING PACK CONTRACT V1

## Estado

```text
DRAFT_CONTRACT
NO_RUNTIME_CHANGE
NO_CODE_AUTHORIZATION
NO_IMPLEMENTATION_AUTHORIZATION
AUDIT_REQUIRED_BEFORE_IMPLEMENTATION
```

## Propósito

Definir el primer `PYME_BASE_ROUTING_PACK` para alimentar al `Rotor Diagnóstico PyME Genérico V1`.

Este documento le da cuerpo funcional PyME al rotor mediante rutas declarativas, sin convertir el rotor ni el pack en motor de cálculo, evaluador de suficiencia, intérprete patológico, sistema de tratamientos, redactor owner-facing, ERP u orquestador total.

## Relación con el rotor

El rotor sólo consume rutas declaradas por packs válidos.

El pack declara conocimiento de routing PyME genérico.

```text
Pack declara rutas.
Rotor selecciona ruta candidata.
FormulaEngine calcula fórmulas.
EvidenceSufficiency evalúa suficiencia.
QuestionAlignmentGate alinea conversación.
PathologyInterpreter interpreta patologías, si existiera contrato posterior.
OwnerFacingReport redacta salida al dueño.
```

## Principios no negociables

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
No hardcodear fórmulas, patologías, circuitos ni reglas PyME en Python.
No diagnosticar sin evidencia suficiente.
No pedir toda la evidencia posible.
No interpretar patologías.
No sugerir tratamientos.
No redactar salida final para el dueño.
No priorizar ejecución matemática.
No planificar cadenas de cálculo.
No modificar PymIA desde este contrato.
```

## Semántica contractual obligatoria

### formula_reference

`formula_reference` es sólo una referencia declarativa de ruta.

No implica ejecución, cálculo, evaluación, priorización ni despacho de fórmulas.

### adjacent_formula_refs_deferred

`adjacent_formula_refs_deferred` es sólo trazabilidad pasiva.

No implica planificación, secuencia de cálculo, agenda matemática, estrategia diagnóstica ni ejecución futura.

### minimal_evidence_required

`minimal_evidence_required` declara evidencia mínima candidata para despejar la incógnita actual.

No certifica suficiencia. No reemplaza `EvidenceSufficiency`.

### input_signal_family

`input_signal_family` agrupa señales PyME normalizadas.

No procesa texto libre. No reemplaza `QuestionAlignmentGate` ni normalizadores externos.

### PATHOLOGY_HYPOTHESIS_NORMALIZED

Si aparece como modo de entrada, es sólo señal normalizada de routing.

No autoriza interpretación, evaluación, confirmación ni generación de patologías candidatas por parte del pack o del rotor.

## Forma mínima de cada ruta

Cada ruta debe declarar exclusivamente:

```yaml
circuit_id: string
input_signal_family: string
accepted_input_modes: list[string]
formula_reference: string
current_unknown: string
minimal_evidence_required: list[string]
adjacent_formula_refs_deferred: list[string]
status_if_missing_evidence: string
reason_code: string
forbidden_interpretations: list[string]
```

## Circuitos PyME genéricos V1

### 1. CIRCUIT_LIQUIDEZ_OPERATIVA

```yaml
circuit_id: CIRCUIT_LIQUIDEZ_OPERATIVA
input_signal_family: ventas_caja_cobranzas
accepted_input_modes:
  - OWNER_SYMPTOM_NORMALIZED
  - TECHNICAL_QUERY_NORMALIZED
  - FORMULA_DIRECT
  - EVIDENCE_FIRST
formula_reference: ventas_vs_cobranzas
current_unknown: cobranzas_del_periodo
minimal_evidence_required:
  - ventas_periodo
  - cobranzas_periodo
adjacent_formula_refs_deferred:
  - ratio_cobranza
  - ciclo_conversion_caja
  - cash_gap
  - stock_cash_lock
status_if_missing_evidence: NEEDS_EVIDENCE
reason_code: SALES_CASH_GAP_REQUIRES_COLLECTIONS_FIRST
forbidden_interpretations:
  - no inferir venta_no_cobrada
  - no inferir descalce_financiero
  - no calcular ciclo_conversion_caja
  - no priorizar formulas adyacentes
  - no sugerir tratamiento de cobranza
```

### 2. CIRCUIT_RENTABILIDAD_COMERCIAL

```yaml
circuit_id: CIRCUIT_RENTABILIDAD_COMERCIAL
input_signal_family: ventas_costos_margen
accepted_input_modes:
  - OWNER_SYMPTOM_NORMALIZED
  - TECHNICAL_QUERY_NORMALIZED
  - FORMULA_DIRECT
  - EVIDENCE_FIRST
formula_reference: margen_bruto_pct
current_unknown: costo_directo_del_periodo
minimal_evidence_required:
  - ventas_periodo
  - costo_directo_periodo
adjacent_formula_refs_deferred:
  - margen_neto_pct
  - contribucion_marginal
  - punto_equilibrio
  - rentabilidad_por_producto
status_if_missing_evidence: NEEDS_EVIDENCE
reason_code: PROFITABILITY_ROUTE_REQUIRES_DIRECT_COST_FIRST
forbidden_interpretations:
  - no inferir margen_insuficiente
  - no inferir precios_mal_calculados
  - no calcular punto_equilibrio
  - no priorizar productos
  - no sugerir suba de precios
```

### 3. CIRCUIT_STOCK_CAPITAL_INMOVILIZADO

```yaml
circuit_id: CIRCUIT_STOCK_CAPITAL_INMOVILIZADO
input_signal_family: stock_ventas_capital
accepted_input_modes:
  - OWNER_SYMPTOM_NORMALIZED
  - TECHNICAL_QUERY_NORMALIZED
  - FORMULA_DIRECT
  - EVIDENCE_FIRST
  - PATHOLOGY_HYPOTHESIS_NORMALIZED
formula_reference: rotacion_stock
current_unknown: stock_promedio_del_periodo
minimal_evidence_required:
  - stock_inicial
  - stock_final
  - costo_ventas_periodo
adjacent_formula_refs_deferred:
  - dias_inventario
  - stock_cash_lock
  - capital_inmovilizado_stock
  - cobertura_stock
status_if_missing_evidence: NEEDS_EVIDENCE
reason_code: STOCK_CAPITAL_ROUTE_REQUIRES_STOCK_AND_COGS_FIRST
forbidden_interpretations:
  - no interpretar stock_inmovilizado como patologia
  - no inferir sobrestock
  - no inferir quiebre_stock
  - no ordenar liquidacion de stock
  - no calcular rotacion_stock
```

### 4. CIRCUIT_COSTOS_PRECIOS_MARGEN

```yaml
circuit_id: CIRCUIT_COSTOS_PRECIOS_MARGEN
input_signal_family: costos_precios_margen
accepted_input_modes:
  - OWNER_SYMPTOM_NORMALIZED
  - TECHNICAL_QUERY_NORMALIZED
  - FORMULA_DIRECT
  - EVIDENCE_FIRST
formula_reference: margen_unitario
current_unknown: costo_unitario_real
minimal_evidence_required:
  - precio_venta_unitario
  - costo_unitario_real
adjacent_formula_refs_deferred:
  - margen_bruto_pct
  - contribucion_marginal
  - punto_equilibrio
  - sensibilidad_precio_costo
status_if_missing_evidence: NEEDS_EVIDENCE
reason_code: PRICE_MARGIN_ROUTE_REQUIRES_UNIT_COST_FIRST
forbidden_interpretations:
  - no inferir precio_mal_definido
  - no inferir costo_desactualizado
  - no sugerir cambio de precios
  - no calcular margen_unitario
  - no priorizar politica comercial
```

### 5. CIRCUIT_PRODUCCION_CAPACIDAD_COSTO

```yaml
circuit_id: CIRCUIT_PRODUCCION_CAPACIDAD_COSTO
input_signal_family: produccion_capacidad_costos
accepted_input_modes:
  - OWNER_SYMPTOM_NORMALIZED
  - TECHNICAL_QUERY_NORMALIZED
  - FORMULA_DIRECT
  - EVIDENCE_FIRST
formula_reference: costo_produccion_unitario
current_unknown: unidades_producidas_del_periodo
minimal_evidence_required:
  - costo_produccion_periodo
  - unidades_producidas_periodo
adjacent_formula_refs_deferred:
  - capacidad_utilizada_pct
  - costo_ocioso
  - productividad_por_hora
  - margen_unitario
status_if_missing_evidence: NEEDS_EVIDENCE
reason_code: PRODUCTION_COST_ROUTE_REQUIRES_UNITS_AND_COST_FIRST
forbidden_interpretations:
  - no inferir ineficiencia_productiva
  - no inferir capacidad_ociosa
  - no recomendar contratacion
  - no calcular costo_produccion_unitario
  - no planificar produccion
```

### 6. CIRCUIT_COBRANZAS_CUENTAS_CORRIENTES

```yaml
circuit_id: CIRCUIT_COBRANZAS_CUENTAS_CORRIENTES
input_signal_family: clientes_deuda_cobranza
accepted_input_modes:
  - OWNER_SYMPTOM_NORMALIZED
  - TECHNICAL_QUERY_NORMALIZED
  - FORMULA_DIRECT
  - EVIDENCE_FIRST
formula_reference: aging_cuentas_por_cobrar
current_unknown: saldo_vencido_por_cliente
minimal_evidence_required:
  - facturas_emitidas
  - cobranzas_registradas
  - vencimientos_facturas
adjacent_formula_refs_deferred:
  - dias_calle
  - ratio_morosidad
  - concentracion_deuda_clientes
  - cash_gap
status_if_missing_evidence: NEEDS_EVIDENCE
reason_code: RECEIVABLES_ROUTE_REQUIRES_INVOICES_COLLECTIONS_DUE_DATES
forbidden_interpretations:
  - no inferir morosidad patologica
  - no clasificar clientes
  - no sugerir acciones de cobranza
  - no calcular aging
  - no priorizar reclamos
```

### 7. CIRCUIT_PROVEEDORES_PRESION_FINANCIERA

```yaml
circuit_id: CIRCUIT_PROVEEDORES_PRESION_FINANCIERA
input_signal_family: proveedores_deuda_vencimientos
accepted_input_modes:
  - OWNER_SYMPTOM_NORMALIZED
  - TECHNICAL_QUERY_NORMALIZED
  - FORMULA_DIRECT
  - EVIDENCE_FIRST
formula_reference: aging_cuentas_por_pagar
current_unknown: deuda_vencida_con_proveedores
minimal_evidence_required:
  - facturas_proveedores
  - pagos_realizados
  - vencimientos_proveedores
adjacent_formula_refs_deferred:
  - dias_pago_proveedores
  - presion_proveedores
  - cash_gap
  - capital_trabajo_requerido
status_if_missing_evidence: NEEDS_EVIDENCE
reason_code: SUPPLIER_PRESSURE_ROUTE_REQUIRES_PAYABLES_PAYMENTS_DUE_DATES
forbidden_interpretations:
  - no inferir insolvencia
  - no inferir ruptura_con_proveedores
  - no sugerir renegociacion
  - no calcular aging_cuentas_por_pagar
  - no priorizar pagos
```

### 8. CIRCUIT_AUTOMATIZACION_ROI

```yaml
circuit_id: CIRCUIT_AUTOMATIZACION_ROI
input_signal_family: procesos_manualidad_ahorro_roi
accepted_input_modes:
  - OWNER_SYMPTOM_NORMALIZED
  - TECHNICAL_QUERY_NORMALIZED
  - FORMULA_DIRECT
  - EVIDENCE_FIRST
formula_reference: roi_automatizacion
current_unknown: horas_manual_actuales
minimal_evidence_required:
  - horas_manual_actuales
  - costo_hora_operativa
  - costo_implementacion_automatizacion
adjacent_formula_refs_deferred:
  - ahorro_mensual_estimado
  - payback_period
  - costo_error_manual
  - capacidad_liberada
status_if_missing_evidence: NEEDS_EVIDENCE
reason_code: AUTOMATION_ROI_ROUTE_REQUIRES_MANUAL_HOURS_COST_AND_IMPLEMENTATION_COST
forbidden_interpretations:
  - no inferir conveniencia_de_automatizar
  - no recomendar software
  - no aprobar inversion
  - no calcular ROI
  - no planificar implementacion
```

## Estados permitidos

```text
ROUTE_CANDIDATE
NEEDS_EVIDENCE
NEEDS_NORMALIZATION
NOT_REPRESENTABLE_IN_PACK
BLOCKED_BY_CONTRACT_BOUNDARY
```

## Criterios de aceptación

Este contrato es aceptable si:

```text
- conserva kernel estable;
- todo conocimiento entra como pack declarativo;
- no invade FormulaEngine;
- no invade EvidenceSufficiency;
- no invade QuestionAlignmentGate;
- no invade PathologyInterpreter;
- no invade OwnerFacingReport;
- no habilita implementación;
- permite simular casos PyME más amplios que liquidez;
- sigue siendo auditable;
- mantiene fail-closed.
```

## Criterios de rechazo

Se rechaza si el pack:

```text
- calcula;
- diagnostica;
- prioriza ejecución;
- interpreta patologías;
- propone tratamientos;
- redacta salida owner-facing final;
- convierte al rotor en orquestador;
- duplica QAG;
- duplica EvidenceSufficiency;
- duplica FormulaEngine;
- hardcodea conocimiento PyME en Python;
- habilita runtime desde este documento.
```

## Próximo paso metodológico

```text
AUDITORIA_CONTRACTUAL_DEL_PACK
```

Este documento no habilita código, tests, schemas Pydantic, runtime, modificación de `PymIA`, creación de packs activos ni cambios en el motor diagnóstico.
