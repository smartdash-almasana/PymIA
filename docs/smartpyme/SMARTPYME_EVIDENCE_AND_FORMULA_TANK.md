# SMARTPYME_EVIDENCE_AND_FORMULA_TANK

Estado: **DOCUMENTADO (v0.1.0-doc) — Sin implementación runtime**

---

## 1. Estado y propósito

Este documento define el **segundo KnowledgeTank canónico** de SmartPyme:

```text
SMARTPYME_EVIDENCE_AND_FORMULA_TANK
```

Su función es **mapear evidencia disponible a tipos documentales, campos
esperados, fórmulas ejecutables, hipótesis contrastables y criterios de
suficiencia**, sin ejecutar análisis y sin emitir diagnóstico.

El tanque responde la pregunta operativa:

> "Dada la hipótesis abierta por el Operational Pathology Tank,
> ¿qué evidencia y qué fórmulas permiten contrastarla, con qué
> campos mínimos, qué bloqueos y qué outputs están habilitados
> por el runtime real?"

Este documento:

- Documenta conocimiento cuantitativo y documental de dominio.
- No implementa código.
- No calcula fórmulas (solo las referencia y las declara contrastables).
- No procesa archivos.
- No diagnostica.
- Se alimenta del `InterrogationResult` y de los outputs conceptuales
  del `SMARTPYME_OPERATIONAL_PATHOLOGY_TANK`.
- Produce `EvidenceRequest` conceptual y criterios de suficiencia.
- Complementa (no reemplaza) `SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md` y
  `SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md`.

---

## 2. Relación con la arquitectura de tanques

Este tanque sigue el contrato definido en:

- `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md`
- `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md`

Y consume referencia de:

- `SMARTPYME_OPERATIONAL_PATHOLOGY_TANK.md` (síntomas + patologías candidatas);
- `SMARTPYME_INTERROGATION_SLICE.md` (síntomas detectados);
- `SMARTPYME_SEMANTIC_DIALECTIC_PHASE.md` (fase previa);
- `docs/formula_catalog.v1.json` (catálogo de fórmulas);
- `docs/formula_catalog.schema.v1.json` (schema de fórmulas);
- `docs/pathology_catalog.v1.json` (catálogo de patologías);
- `docs/contracts/scn/evidence_candidate.schema.json` (contrato SCN draft);
- `docs/ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md`;
- `docs/ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md`.

El tanque transita los 8 estados del ciclo de vida definidos en la
arquitectura:

```text
DEFINED → AVAILABLE → CANDIDATE → ACTIVE
                              ↓
                    SUSPENDED / DEACTIVATED
                              ↓
                    UNSUPPORTED / RETIRED
```

En la versión actual (0.1.0-doc) el tanque está **DEFINED y AVAILABLE
solo a nivel documental**. No existe loader, selector runtime,
`TankSelectionResult` ni `EvidenceRequest` formal implementado.

---

## 3. Definición del tanque

```yaml
tank_id: SMARTPYME_EVIDENCE_AND_FORMULA_TANK
version: "0.1.0-doc"
name: "Evidence & Formula Tank — SmartPyme Core"
domain: evidence_and_formulas
scope: transversal_pyme
description: |
  Mapea evidencia disponible a tipos documentales, campos esperados,
  fórmulas candidatas, hipótesis contrastables y criterios de
  suficiencia, sin ejecutar análisis ni emitir diagnóstico.

outputs_allowed:
  - document_type_suggestions
  - expected_fields
  - candidate_formulas
  - testable_hypotheses
  - sufficiency_criteria
  - evidence_requests
  - blocking_conditions
  - runtime_compatibility_map
  - safety_warnings
  - next_interrogation_state

outputs_forbidden:
  - confirmed_diagnosis
  - computed_results
  - causal_assertion
  - final_report
  - financial_advice
  - automated_decision
  - unsupported_classification
  - benchmark_without_sector
  - price_recommendation
  - executed_formulas
```

---

## 4. Inputs esperados

### Desde `InterrogationResult`

- `raw_input` — relato literal preservado.
- `normalized_terms` — señales léxicas.
- `business_context` — selectores estructurales normalizados.
- `semantic_signals` — señales semánticas.
- `candidate_symptoms` — síntomas detectados.
- `candidate_domains` — dominios candidatos.
- `evidence_needs` — necesidades de evidencia preliminares.
- `status` — estado del interrogatorio.
- `suggested_classification` — clasificación sugerida por slice.

### Desde `Operational Pathology Tank` (conceptual)

- `pathology_candidates` — patologías candidatas a contrastar.
- `hypothesis_candidates` — hipótesis abiertas emitidas.
- `evidence_suggestions` — evidencia sugerida por el primer tanque.
- `safety_warnings` — warnings ya emitidos.

### Desde selectores estructurales

- `sales_channel`: Local / Mayorista / Mercado Libre / Ecommerce / Instagram / Mixto
- `operation_type`: Revendo / Produzco / Servicios / Distribuyo / Mixto
- `stock_mode`: Sí / No / Informal
- `tools_used`: Excel / Sistema / Cuaderno / Varios
- `evidence_available`: Excel / PDF / Capturas / AudioTexto / NoSe
- `employee_range`
- `marketplace_presence`

**Regla:** los selectores **nunca** activan el tanque por sí solos. Solo
refuerzan dominio y tipo documental cuando el `raw_input` ya aporta señal
compatible.

---

## 5. Estados del tanque

| Estado | Significado | Condición de entrada | Condición de salida |
|---|---|---|---|
| `DEFINED` | El tanque existe en documentación. | Creación del documento. | Pase a AVAILABLE. |
| `AVAILABLE` | Cargable por futuro loader. | Loader implementado. | Pase a CANDIDATE cuando haya caso. |
| `CANDIDATE` | Hay hipótesis abiertas que requieren contraste con evidencia. | `Operational Pathology Tank` activo con hipótesis emitidas. | Confirmación → ACTIVE, o refutación → SUSPENDED. |
| `ACTIVE` | Tanque emitiendo `EvidenceRequest` y criterios de suficiencia. | Usuario confirma reformulación y hay al menos un tipo documental plausible. | Resolución → DEACTIVATED o bloqueo → UNSUPPORTED. |
| `SUSPENDED` | Evidencia insuficiente para cualquier fórmula. | `evidence_available == NoSe` o falta contexto mínimo. | Puede volver a ACTIVE si aparece evidencia. |
| `DEACTIVATED` | No aplica al caso. | Problema fuera del dominio cuantitativo/documental. | Terminal para este caso. |
| `UNSUPPORTED` | Aplica conceptualmente pero runtime no soporta análisis requerido. | Runtime sin capacidad de procesar el tipo documental. | Terminal para este caso. |
| `RETIRED` | Reemplazado por nueva versión. | Cambio MAJOR en contrato. | Terminal global. |

---

## 6. Activadores

El tanque puede pasar a `CANDIDATE` cuando:

- el `Operational Pathology Tank` emitió al menos una hipótesis abierta;
- el usuario mencionó documentos, archivos, Excel, facturas, extractos;
- los selectores indican `evidence_available` distinta de `NoSe`;
- la patología candidata tiene al menos una fórmula asociada en
  `formula_catalog.v1.json`;
- el síntoma detectado pertenece a dominios cuantificables
  (finanzas, comercial, stock, producción).

El tanque **no puede pasar a ACTIVE** si:

- no hay hipótesis abierta previa;
- no hay evidencia posible (`evidence_available == NoSe` y sin mención documental);
- el problema es puramente cualitativo sin contraste documental posible;
- el runtime no soporta el tipo de análisis asociado;
- se viola cualquier safety gate.

---

## 7. Desactivadores

El tanque debe suspenderse o desactivarse si:

- el usuario corrige la reformulación y el nuevo relato no tiene hipótesis
  contrastable;
- la evidencia aportada no contiene los campos mínimos requeridos;
- la evidencia es contradictoria sin posibilidad de resolución;
- el tipo documental recibido no corresponde a la hipótesis;
- el runtime no soporta la fórmula requerida;
- se pide evidencia excesiva (más de 3 tipos simultáneos);
- otro tanque más específico debe tomar el análisis;
- se detecta riesgo de cálculo sin validación de supuestos.

Distinguir:

- `SUSPENDED`: puede reactivarse si aparece evidencia adicional.
- `DEACTIVATED`: no aplica al caso.
- `UNSUPPORTED`: conceptualmente aplicable pero runtime no soporta.

---

## 8. Tipos documentales soportados

El tanque define tipos documentales canónicos con sus campos mínimos,
deseables y bloqueantes.

### 8.1 `excel_ventas_costos`

- **Descripción:** archivo tabular con ventas y costos por producto o
  servicio en un período.
- **Campos requeridos:** `producto`, `precio_venta`, `costo`.
- **Campos opcionales:** `cantidad`, `comision`, `logistica`, `impuestos`,
  `fecha`, `cliente`, `canal`.
- **Fórmulas habilitadas:**
  - `REN_001_margen_neto_real`
  - `A02` (margen bruto)
  - `PYME_044_margen_cliente` (si hay cliente)
  - `PYME_033_concentracion_sku` (si hay SKU)
- **Patologías contrastables:** `REN_001`, `PYME_014`, `PYME_017`,
  `PYME_044`, `PYME_049`.
- **Clasificación runtime:** `excel_diagnostic` si el archivo es tabular.
- **Bloqueante:** falta de `costo` si se pretende calcular margen.

### 8.2 `excel_proveedores`

- **Descripción:** maestro de proveedores.
- **Campos requeridos:** `proveedor`.
- **Campos condicionales requeridos:** al menos uno de `cuit` o
  `razon_social`.
- **Campos opcionales:** domicilio, email, categoría, fecha_alta, estado.
- **Fórmulas habilitadas:** ninguna matemática; solo validación de
  duplicados y variaciones legales.
- **Patologías contrastables:** `PYME_018`, `PYME_022`.
- **Clasificación runtime:** `supplier_duplicate_check` (existe en runtime
  real).
- **Bloqueante:** falta de `proveedor` o ausencia total de `cuit` y
  `razon_social`.

### 8.3 `excel_stock`

- **Descripción:** archivo con stock sistema y/o stock físico.
- **Campos requeridos:** `producto`, `stock_sistema`, `stock_real`,
  `fecha`.
- **Campos opcionales:** `movimientos`, `ventas`, `ubicacion`, `lote`.
- **Fórmulas habilitadas:**
  - `INV_002_rotacion_stock` (si hay CMV + stock promedio)
  - `INV_001_punto_reposicion` (si hay historial de ventas SKU)
- **Patologías contrastables:** `INV_001`, `INV_002`, `PYME_008`,
  `PYME_042`.
- **Clasificación runtime:** ninguna específica en runtime real actual.
- **Bloqueante:** falta de ambos stocks (sistema y real).

### 8.4 `extracto_bancario`

- **Descripción:** movimientos bancarios de una cuenta del negocio.
- **Campos requeridos:** `fecha`, `concepto`, `monto`.
- **Campos opcionales:** `origen`, `destino`, `canal`, `referencia`.
- **Fórmulas habilitadas:**
  - `LIQ_001_vendido_cobrado` (si se combina con ventas)
  - `LIQ_002_saldo_final_proyectado`
  - `PYME_026_flujo_operativo` (si hay estado de resultados)
- **Patologías contrastables:** `LIQ_001`, `LIQ_002`, `PYME_013`,
  `PYME_026`, `PYME_046`.
- **Clasificación runtime:** ninguna específica en runtime real actual.
- **Bloqueante:** extracto sin `monto` o sin `fecha`.

### 8.5 `reporte_cobros_ventas`

- **Descripción:** ventas del período discriminadas por cliente o canal.
- **Campos requeridos:** `fecha`, `cliente_o_canal`, `monto_vendido`.
- **Campos opcionales:** `monto_cobrado`, `saldo_pendiente`,
  `fecha_cobro`.
- **Fórmulas habilitadas:**
  - `PYME_011_dso`
  - `PYME_013_dso_dpo_gap` (si hay DPO)
  - `LIQ_001_vendido_cobrado`
- **Patologías contrastables:** `PYME_011`, `PYME_013`, `PYME_046`.
- **Clasificación runtime:** `excel_diagnostic` si es archivo tabular.
- **Bloqueante:** ausencia de `monto_vendido` y `monto_cobrado`.

### 8.6 `lista_precios`

- **Descripción:** lista de precios vigente y/o histórica.
- **Campos requeridos:** `producto`, `precio_venta`, `fecha_vigencia`.
- **Campos opcionales:** `canal`, `cliente_tipo`, `costo_asociado`.
- **Fórmulas habilitadas:**
  - `PYME_017_pricing_drift` (si hay benchmark de mercado)
  - `C08` (desviación vs mercado)
- **Patologías contrastables:** `PYME_017`, `PYME_048`.
- **Clasificación runtime:** `excel_diagnostic` si es tabular.
- **Bloqueante:** lista sin `precio_venta`.

### 8.7 `estructura_costos`

- **Descripción:** composición de costos fijos y variables del negocio o
  de un producto/servicio.
- **Campos requeridos:** `concepto`, `tipo` (fijo/variable), `monto`.
- **Campos opcionales:** `periodo`, `producto`, `proveedor`,
  `fecha_actualizacion`.
- **Fórmulas habilitadas:**
  - `REN_002_coeficiente_reposicion` (si hay índices)
  - `B05` (punto de equilibrio, si hay ingresos)
- **Patologías contrastables:** `REN_002`, `PYME_014`, `PYME_048`,
  `PYME_049`.
- **Clasificación runtime:** `excel_diagnostic` si es tabular.
- **Bloqueante:** ausencia de `monto` o de `tipo`.

### 8.8 `descripcion_flujo_manual`

- **Descripción:** descripción cualitativa de un flujo manual repetitivo.
- **Campos requeridos:** `tarea`, `frecuencia`, `archivos_sistemas`.
- **Campos opcionales:** `tiempo_estimado`, `personas_involucradas`,
  `errores_reportados`.
- **Fórmulas habilitadas:**
  - `PYME_047_tiempo_manual_automatizado` (si hay medición)
  - `M05_roi_automatizacion` (si hay estimación de ahorro)
- **Patologías contrastables:** `PYME_015`, `PYME_020`, `PYME_040`,
  `PYME_047`.
- **Clasificación runtime:** ninguna específica.
- **Bloqueante:** falta de `tarea` o `frecuencia`.

### 8.9 `export_mercado_libre`

- **Descripción:** export de ventas/comisiones de Mercado Libre.
- **Campos requeridos:** `fecha`, `venta_neta`, `comisiones`,
  `logistica`.
- **Campos opcionales:** `publicidad`, `impuestos`, `sku`, `cliente`.
- **Fórmulas habilitadas:**
  - `REN_001_margen_neto_real` (específico ML)
  - `PYME_044_margen_cliente` (si corresponde)
- **Patologías contrastables:** `REN_001`, `PYME_014`, `PYME_049`.
- **Clasificación runtime:** `excel_diagnostic` si es tabular.
- **Bloqueante:** ausencia de `venta_neta` o `comisiones`.

### 8.10 `balance_estado_resultados`

- **Descripción:** estados contables del negocio.
- **Campos requeridos:** estructura contable mínima (activo, pasivo,
  patrimonio, ingresos, egresos).
- **Fórmulas habilitadas:**
  - `PYME_024_liquidez_corriente`
  - `PYME_026_flujo_operativo`
  - `PYME_027_intereses_ebitda`
- **Patologías contrastables:** `PYME_024`, `PYME_026`, `PYME_027`.
- **Clasificación runtime:** ninguna específica en runtime actual.
- **Bloqueante:** ausencia de estructura contable mínima.

---

## 9. Fórmulas soportadas

El tanque **no ejecuta** fórmulas; las declara como **contrastables** y
mapea a evidencia requerida. Las fórmulas provienen de
`docs/formula_catalog.v1.json`.

### 9.1 Familias prioritarias MVP

| family_id | Familia | Scope |
|---|---|---|
| A | Rentabilidad y Margen | margen, contribución, rentabilidad |
| B | Costos | fijos, variables, unitarios, reposición |
| C | Precios / Pricing | markup, drift, elasticidad |
| E | Caja y Liquidez | flujo de caja, DSO, DPO, CCC |
| G | Inventario / Stock | rotación, stock seguridad, merma |
| M | Automatización / ROI | horas manuales, payback |
| N | Riesgo y Control | concentración, aging, sensibilidad |

### 9.2 Fórmulas contrastables prioritarias

```yaml
- formula_id: REN_001_margen_neto_real
  canonical_id: A02
  display: "((PV - Costos - Impuestos) / PV) × 100"
  required_evidence:
    - ventas_del_periodo
    - costos_directos
    - impuestos_y_comisiones
  testable_hypotheses:
    - margen_erosionado_por_comisiones
    - falsa_rentabilidad
  priority: alta

- formula_id: LIQ_001_vendido_cobrado
  canonical_id: E13
  display: "Vendido - Cobrado"
  required_evidence:
    - ventas_del_periodo
    - cobranzas_del_periodo
    - cuentas_corrientes_clientes
  testable_hypotheses:
    - descalce_cobranza
    - tension_caja_por_plazos
  priority: alta

- formula_id: LIQ_002_saldo_final_proyectado
  canonical_id: E03
  display: "Saldo Inicial + Cobros - Pagos"
  required_evidence:
    - saldo_inicial_caja_banco
    - cobranzas_esperadas
    - pagos_esperados
  testable_hypotheses:
    - riesgo_flujo_caja
    - descubierto_proyectado
  priority: alta

- formula_id: PYME_011_dso
  canonical_id: E09
  display: "(Cuentas por Cobrar / Ventas) × Días"
  required_evidence:
    - cuentas_por_cobrar
    - ventas_periodo
    - periodo_dias
  testable_hypotheses:
    - plazo_cobro_extendido
    - tension_caja_silenciosa
  priority: alta

- formula_id: PYME_013_dso_dpo_gap
  canonical_id: E08
  display: "DSO - DPO"
  required_evidence:
    - dso_calculado
    - dpo_calculado
  testable_hypotheses:
    - descalce_financiamiento
  priority: alta

- formula_id: INV_001_punto_reposicion
  canonical_id: G05
  display: "(Venta Promedio × Lead Time) + Stock Seguridad"
  required_evidence:
    - historial_ventas_sku
    - lead_time_proveedor
    - politica_stock_seguridad
  testable_hypotheses:
    - quiebre_stock_probable
    - stock_seguridad_insuficiente
  priority: alta

- formula_id: INV_002_rotacion_stock
  canonical_id: G01
  display: "CMV / Stock Promedio"
  required_evidence:
    - cmv_periodo
    - inventario_inicial
    - inventario_final
  testable_hypotheses:
    - capital_inmovilizado
    - rotacion_lenta
  priority: alta

- formula_id: PYME_017_pricing_drift
  canonical_id: C08
  display: "(Precio Propio - Mercado) / Mercado"
  required_evidence:
    - lista_precios_propia
    - benchmark_precios_mercado
  testable_hypotheses:
    - atraso_precio
    - sobreprecio_relativo
  priority: media

- formula_id: PYME_024_liquidez_corriente
  canonical_id: E05
  display: "Activo Corriente / Pasivo Corriente"
  required_evidence:
    - balance_general
    - saldos_activo_corriente
    - saldos_pasivo_corriente
  testable_hypotheses:
    - agotamiento_capital_trabajo
  priority: alta

- formula_id: PYME_033_concentracion_sku
  canonical_id: N03
  display: "SKU Principal / Ventas × 100"
  required_evidence:
    - ventas_por_sku
    - ventas_totales
  testable_hypotheses:
    - riesgo_concentracion
  priority: alta

- formula_id: PYME_047_tiempo_manual_automatizado
  canonical_id: M01
  display: "Tiempo Manual / Automatizado"
  required_evidence:
    - medicion_tiempos_proceso
    - flujo_actual
    - flujo_automatizado_estimado
  testable_hypotheses:
    - rigidez_artesanal
    - oportunidad_automatizacion
  priority: alta

- formula_id: M05_roi_automatizacion
  canonical_id: M05
  display: "((Ahorro Mensual × 12) - Costo Operación) / Inversión × 100"
  required_evidence:
    - horas_manual_actuales
    - costo_hora
    - cotizacion_automatizacion
    - costo_operacion_anual
  testable_hypotheses:
    - viabilidad_automatizacion
  priority: alta
```

### 9.3 Reglas de uso de fórmulas

- El tanque **no ejecuta** la fórmula.
- El tanque **declara** la fórmula como contrastable cuando la evidencia
  disponible cubre las `required_variables`.
- Si falta alguna variable requerida, la fórmula queda en estado
  `NO_CONTRASTABLE` y el tanque emite `EvidenceRequest` específico.
- Si la fórmula tiene `calculation_state = CALCULABLE_CON_SUPUESTOS`, el
  tanque debe emitir un `safety_warning` explícito sobre los supuestos.

---

## 10. Hipótesis contrastables

Una `TestableHypothesis` es una evolución de la `HypothesisCandidate` del
Operational Pathology Tank, ya vinculada a evidencia y fórmula concretas.

Contrato conceptual:

```yaml
testable_hypothesis:
  hypothesis_id: str
  related_pathology: str
  related_formulas: list[str]
  required_evidence: list[EvidenceRequest]
  sufficiency_criteria: SufficiencyCriteria
  falsification_conditions: list[str]
  confirmation_conditions: list[str]
  safety_warning: str
  runtime_compatible: bool
  enabled_classification: str | null
```

Reglas:

- Una hipótesis contrastable sigue sin ser diagnóstico.
- Debe declarar cómo se **falsifica** y cómo se **confirma**.
- Si el runtime no soporta la fórmula o el tipo documental, queda
  `runtime_compatible: false`.
- Si la evidencia es insuficiente, la hipótesis no pasa de
  `CANDIDATE_HYPOTHESIS`.

Ejemplo:

```yaml
testable_hypothesis:
  hypothesis_id: margen_erosionado_por_comisiones
  related_pathology: MARGIN_LEAKAGE_SUSPECTED
  related_formulas:
    - REN_001_margen_neto_real
  required_evidence:
    - evidence_type: excel_ventas_costos
      required_fields: [producto, precio_venta, costo, comision]
  sufficiency_criteria:
    min_rows: 20
    min_period_months: 1
    coverage: ">70% productos con costo cargado"
  falsification_conditions:
    - "margen_neto_real >= 20% en >70% productos"
  confirmation_conditions:
    - "margen_neto_real < 10% en >50% productos"
  safety_warning: "No afirmar erosión sin considerar comisiones y logística."
  runtime_compatible: true
  enabled_classification: excel_diagnostic
```

---

## 11. Criterios de suficiencia de evidencia

El tanque declara cuándo la evidencia es **suficiente**, **insuficiente
pero orientadora**, o **bloqueante**.

### 11.1 Niveles de suficiencia

| Nivel | Significado | Acción |
|---|---|---|
| `SUFFICIENT` | La evidencia cubre las variables de la fórmula y el criterio mínimo. | Habilita contraste de hipótesis. |
| `PARTIAL_ORIENTATIVE` | Hay evidencia parcial; orienta pero no confirma. | Emite `EvidenceRequest` adicional + warning. |
| `INSUFFICIENT_BLOCKING` | Falta evidencia crítica. | Bloquea fórmula; emite `EvidenceRequest` bloqueante. |
| `CONTRADICTORY` | La evidencia contradice la hipótesis o es internamente inconsistente. | Suspende hipótesis o deriva a desambiguación. |
| `NO_EVIDENCE` | No hay evidencia declarada. | Tanque en `SUSPENDED`. |

### 11.2 Criterios por tipo documental

- **`excel_ventas_costos`**: mínimo 20 filas + al menos 1 mes + 70% de
  productos con costo cargado → `SUFFICIENT` para `REN_001`.
- **`excel_proveedores`**: mínimo 10 filas + al menos `proveedor` + uno
  de (`cuit` o `razon_social`) → `SUFFICIENT` para
  `supplier_duplicate_check`.
- **`extracto_bancario`**: mínimo 30 días de movimientos + `monto` y
  `fecha` completos → `SUFFICIENT` para `LIQ_001`.
- **`excel_stock`**: stock sistema + stock físico de la misma fecha →
  `SUFFICIENT` para trazabilidad.
- **`descripcion_flujo_manual`**: tarea + frecuencia + archivos →
  `PARTIAL_ORIENTATIVE` (requiere medición para ROI).

---

## 12. Evidencia por patología operacional

Cruce entre patologías del Operational Pathology Tank y evidencia requerida.

| Patología | Evidencia mínima | Evidencia deseable | Fórmulas candidatas | Clasificación runtime |
|---|---|---|---|---|
| CASH_RECONCILIATION_DRIFT | `extracto_bancario` + `reporte_cobros_ventas` | + gastos + retiros | LIQ_001, LIQ_002, PYME_013, PYME_026 | ninguna específica |
| MARGIN_LEAKAGE_SUSPECTED | `excel_ventas_costos` | + comisiones + logística | REN_001, A02, PYME_044 | `excel_diagnostic` |
| COST_UPDATE_LAG | `estructura_costos` con fechas | + lista_precios + stock valuado | REN_002 | `excel_diagnostic` |
| SUPPLIER_MASTER_DUPLICATION | `excel_proveedores` | + domicilio, email | validación duplicados | `supplier_duplicate_check` |
| STOCK_TRACEABILITY_GAP | `excel_stock` (sistema + real) | + movimientos | INV_001, INV_002 | ninguna específica |
| MANUAL_WORK_OVERLOAD | `descripcion_flujo_manual` | + medición tiempos | PYME_047, M05 | ninguna específica |
| DOCUMENTARY_FRAGMENTATION | muestra representativa | + inventario soportes | — | ninguna |
| PRICING_CONTROL_WEAKNESS | `lista_precios` | + benchmark mercado | PYME_017 | `excel_diagnostic` |
| EVIDENCE_INSUFFICIENCY | al menos un tipo compatible | — | — | — |
| OPERATIONAL_VISIBILITY_GAP | descripción de qué ver y cada cuánto | + logs disponibles | — | ninguna |

---

## 13. `EvidenceRequest` conceptual

El tanque produce un `EvidenceRequest` por cada hipótesis contrastable.

Contrato conceptual:

```yaml
evidence_request:
  request_id: str
  hypothesis_id: str
  tenant_id: str
  case_id: str
  evidence_items:
    - evidence_type: str
      description: str
      required_fields: list[str]
      optional_fields: list[str]
      why_needed: str
      blocks_analysis: bool
      enables_formula: str | null
      enables_classification: str | null
      sufficiency_criteria: SufficiencyCriteria
  max_items: int  # nunca > 3
  priority_order: list[str]
  safety_warnings: list[str]
  issued_at: datetime
  valid_until: datetime | null
```

Reglas:

- Máximo **3 tipos de evidencia** simultáneos por caso
  (`NO_EXCESSIVE_EVIDENCE_REQUEST`).
- Cada `EvidenceRequest` debe explicar **por qué** se pide.
- Si la evidencia habilita una clasificación runtime real, se declara en
  `enables_classification`.
- Si la evidencia no habilita ninguna clasificación runtime, se declara
  explícitamente `enables_classification: null`.
- El `EvidenceRequest` **no ejecuta** validación; solo la define para que
  capas posteriores (Boundary Layer futura) la apliquen.

---

## 14. Relación con clasificaciones reales

En Git real actual (HEAD `52aab00`) existen:

- `excel_diagnostic`
- `supplier_duplicate_check`

El tanque **mapea** evidencia a clasificación solo cuando:

- `excel_proveedores` + campos requeridos → `supplier_duplicate_check`.
- `excel_ventas_costos`, `estructura_costos`, `lista_precios`,
  `reporte_cobros_ventas`, `export_mercado_libre` → `excel_diagnostic`
  (genérico, si es archivo tabular).

El tanque **NO asume**:

- `--classification auto` (no implementado).
- routing automático (no implementado).
- HTML output (no implementado en HEAD real actual).
- nuevas clasificaciones no implementadas.
- cálculo real de fórmulas.

---

## 15. Safety gates aplicados

Los 8 gates definidos en `SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md`:

### 15.1 NO_DIAGNOSIS_WITHOUT_EVIDENCE
- **Aplicación:** ninguna fórmula se considera contrastada sin evidencia
  `SUFFICIENT`.
- **Ejemplo:** si llega `excel_ventas_costos` sin `costo`, la fórmula
  `REN_001` queda `NO_CONTRASTABLE`.
- **Consecuencia:** status no pasa a `READY_TO_ANALYZE`.

### 15.2 NO_SELECTOR_ONLY_ACTIVATION
- **Aplicación:** selector `sales_channel = Mercado Libre` no activa solo
  el tanque.
- **Ejemplo:** selector ML + "quiero revisar mi negocio" → tanque
  `CANDIDATE` o `SUSPENDED`, no `ACTIVE`.
- **Consecuencia:** se requiere relato compatible + evidencia.

### 15.3 NO_UNSUPPORTED_OUTPUT_PROMISE
- **Aplicación:** no prometer cálculo de flujo de caja si el runtime no
  soporta esa clasificación.
- **Ejemplo:** no decir "te calculamos el FCO" si no hay capacidad.
- **Consecuencia:** `runtime_compatible: false` se declara.

### 15.4 NO_DOMAIN_CONTAMINATION
- **Aplicación:** el tanque no emite fórmulas de dominios que no cubre.
- **Ejemplo:** no mezclar marketing metrics si el caso es financiero puro.
- **Consecuencia:** `supported_domains` es cerrado.

### 15.5 NO_EXCESSIVE_EVIDENCE_REQUEST
- **Aplicación:** máximo 3 tipos de evidencia simultáneos.
- **Ejemplo:** para MARGIN_LEAKAGE_SUSPECTED: ventas + costos +
  comisiones (no 6 archivos).
- **Consecuencia:** `max_items: 3` en `EvidenceRequest`.

### 15.6 USER_CONFIRMATION_REQUIRED_FOR_AMBIGUOUS_CASES
- **Aplicación:** si la reformulación es ambigua, el usuario debe
  confirmar antes de pedir evidencia.
- **Ejemplo:** "no me queda" puede ser margen o caja.
- **Consecuencia:** status `WAITING_OWNER_CONFIRMATION`.

### 15.7 RUNTIME_COMPATIBILITY_REQUIRED
- **Aplicación:** solo sugerir clasificación si el runtime la soporta.
- **Ejemplo:** no sugerir `cash_flow_analysis` porque no existe.
- **Consecuencia:** `enabled_classification: null` si no hay match.

### 15.8 FAIL_CLOSED_ON_CONFLICT
- **Aplicación:** si dos hipótesis requieren evidencia contradictoria, no
  cerrar.
- **Ejemplo:** si evidencia dice margen alto pero el dueño dice "no me
  queda", no resolver sin desambiguación.
- **Consecuencia:** status `NEEDS_DISAMBIGUATION`.

---

## 16. Ejemplos end-to-end

### 16.1 Ejemplo 1 — "No me cierra la plata"

- **raw_input:** "No me cierra la plata."
- **síntoma:** `DESCUADRE_DINERO`.
- **patología previa:** `CASH_RECONCILIATION_DRIFT`.
- **hipótesis contrastable:** `descalce_cobranza`.
- **EvidenceRequest:**
  - `extracto_bancario` (fecha, concepto, monto)
  - `reporte_cobros_ventas` (fecha, cliente, monto_vendido, monto_cobrado)
- **Fórmulas candidatas:** LIQ_001, LIQ_002, PYME_013.
- **runtime_compatible:** `false` (no hay clasificación específica).
- **enabled_classification:** `null`.
- **safety_warning:** "No afirmar desfalco sin evidencia validada."

### 16.2 Ejemplo 2 — "Vendo mucho pero no me queda nada"

- **raw_input:** "Vendo mucho pero no me queda nada."
- **síntoma:** `MARGEN_DUDOSO`.
- **patología previa:** `MARGIN_LEAKAGE_SUSPECTED`.
- **hipótesis contrastable:** `margen_erosionado_por_comisiones`.
- **EvidenceRequest:**
  - `excel_ventas_costos` (producto, precio_venta, costo, comision)
- **Fórmula candidata:** REN_001.
- **runtime_compatible:** `true`.
- **enabled_classification:** `excel_diagnostic`.
- **safety_warning:** "No afirmar erosión sin considerar logística e
  impuestos."

### 16.3 Ejemplo 3 — "Tengo proveedores repetidos y CUIT mezclados"

- **raw_input:** "Tengo proveedores repetidos y CUIT mezclados."
- **síntoma:** `DATOS_DUPLICADOS` + `MAESTRO_DESORDENADO`.
- **patología previa:** `SUPPLIER_MASTER_DUPLICATION`.
- **hipótesis contrastable:** `duplicados_por_cuit_y_variacion_legal`.
- **EvidenceRequest:**
  - `excel_proveedores` (proveedor, cuit, razon_social)
- **Fórmula candidata:** ninguna matemática; validación de duplicados.
- **runtime_compatible:** `true`.
- **enabled_classification:** `supplier_duplicate_check`.
- **safety_warning:** "No afirmar cantidad de duplicados sin validar."

### 16.4 Ejemplo 4 — "El sistema dice un stock y el depósito otro"

- **raw_input:** "El sistema dice un stock y el depósito otro."
- **síntoma:** `STOCK_INCONSISTENTE`.
- **patología previa:** `STOCK_TRACEABILITY_GAP`.
- **hipótesis contrastable:** `stock_fantasma`.
- **EvidenceRequest:**
  - `excel_stock` (producto, stock_sistema, stock_real, fecha)
  - `movimientos` (opcional)
- **Fórmulas candidatas:** INV_001, INV_002 (si hay datos históricos).
- **runtime_compatible:** `false`.
- **enabled_classification:** `null`.
- **safety_warning:** "No atribuir a robo sin evidencia de movimientos."

### 16.5 Ejemplo 5 — "Copio todos los días de un Excel a otro"

- **raw_input:** "Copio todos los días de un Excel a otro."
- **síntoma:** `SOBRECARGA_MANUAL`.
- **patología previa:** `MANUAL_WORK_OVERLOAD`.
- **hipótesis contrastable:** `rigidez_artesanal`.
- **EvidenceRequest:**
  - `descripcion_flujo_manual` (tarea, frecuencia, archivos)
- **Fórmulas candidatas:** PYME_047, M05 (si hay medición).
- **runtime_compatible:** `false` (no hay clasificación runtime).
- **enabled_classification:** `null`.
- **safety_warning:** "No recomendar stack sin contexto de madurez."

### 16.6 Ejemplo 6 — Selector Mercado Libre + "vendo pero no me queda"

- **raw_input:** "Vendo pero no me queda."
- **selector:** `sales_channel = Mercado Libre`.
- **síntoma:** `MARGEN_DUDOSO`.
- **patología previa:** `MARGIN_LEAKAGE_SUSPECTED`.
- **hipótesis contrastable:** `margen erosionado por comisiones ML`.
- **EvidenceRequest:**
  - `export_mercado_libre` (fecha, venta_neta, comisiones, logistica)
  - `estructura_costos` (opcional)
- **Fórmula candidata:** REN_001_margen_neto_real.
- **runtime_compatible:** `true`.
- **enabled_classification:** `excel_diagnostic`.
- **safety_warning:** "No concluir viabilidad del canal sin benchmark."
- **gate activado:** `NO_SELECTOR_ONLY_ACTIVATION`.

### 16.7 Ejemplo 7 — "No sé si gano con lo que produzco"

- **raw_input:** "No sé si gano con lo que produzco."
- **síntoma:** `COSTO_INCIERTO` + `MARGEN_DUDOSO`.
- **patología previa:** `COST_UPDATE_LAG` / `MARGIN_LEAKAGE_SUSPECTED`.
- **hipótesis contrastable:** `costo_reposicion_no_trasladado`.
- **EvidenceRequest:**
  - `estructura_costos` (concepto, tipo, monto, fecha_actualizacion)
  - `lista_precios` (producto, precio_venta, fecha_vigencia)
- **Fórmulas candidatas:** REN_002, REN_001.
- **runtime_compatible:** `true`.
- **enabled_classification:** `excel_diagnostic`.
- **safety_warning:** "No recomendar suba de precio sin evidencia de
  mercado."

---

## 17. Límites explícitos

Este tanque **NO**:

- ejecuta fórmulas;
- procesa archivos;
- valida evidencia (lo hace la futura Boundary Layer);
- ejecuta clasificación;
- genera reporte final;
- toma decisiones;
- reemplaza criterio humano;
- hace benchmark sin sector declarado;
- recomienda precios;
- promete automatización;
- afirma causa raíz;
- diagnostica sin evidencia `SUFFICIENT`.

---

## 18. Relación con Operational Pathology Tank

División de responsabilidades:

- **Operational Pathology Tank:** responde "qué parece estar pasando" →
  síntomas + patologías candidatas + preguntas + hipótesis abiertas.
- **Evidence and Formula Tank (este documento):** responde "qué evidencia
  y fórmulas permiten contrastarlo" → tipos documentales, campos
  esperados, fórmulas, hipótesis contrastables, criterios de suficiencia.

Flujo:

```text
Operational Pathology Tank (ACTIVE)
    ↓ (emite hypothesis_candidates)
Evidence and Formula Tank (CANDIDATE)
    ↓ (mapea a testable_hypotheses)
Evidence and Formula Tank (ACTIVE)
    ↓ (emite EvidenceRequest)
[futuro: Boundary Layer valida evidencia]
    ↓
[futuro: runtime ejecuta fórmula si es compatible]
```

---

## 19. Relación con futuro `TankSelectionResult`

Cuando exista el slice de selección, este tanque debería aparecer así:

```yaml
tank_selection_result:
  case_id: "case-002"
  tenant_id: "tenant_demo"
  selected_tanks:
    - tank_id: SMARTPYME_OPERATIONAL_PATHOLOGY_TANK
      version: "0.1.0-doc"
      lifecycle_state: ACTIVE
    - tank_id: SMARTPYME_EVIDENCE_AND_FORMULA_TANK
      version: "0.1.0-doc"
      lifecycle_state: ACTIVE
      activation_score: 0.85
      activation_reasons:
        - "hypothesis_from: OPERATIONAL_PATHOLOGY_TANK"
        - "evidence_available: Excel"
        - "runtime_compatible: excel_diagnostic"
      evidence_requests:
        - evidence_type: excel_ventas_costos
          required_fields: [producto, precio_venta, costo, comision]
          enables_formula: REN_001_margen_neto_real
          enables_classification: excel_diagnostic
      safety_warnings:
        - "NO_DIAGNOSIS_WITHOUT_EVIDENCE"
        - "CALCULABLE_CON_SUPUESTOS: comisiones pueden faltar"
      next_action: "emit_evidence_request"
  candidate_tanks: []
  suspended_tanks: []
  rejected_tanks: []
  unsupported_tanks: []
  conflicts: []
```

---

## 20. Criterios de aceptación para futura implementación

### Funcionales
- consumir `InterrogationResult` + outputs conceptuales del Operational
  Pathology Tank;
- no ejecutar fórmulas;
- producir `EvidenceRequest` serializable;
- declarar `sufficiency_criteria` por tipo documental;
- aplicar los 8 safety gates;
- mapear a clasificación runtime solo si existe.

### Testing
- tests por cada tipo documental (SUFFICIENT, PARTIAL, BLOCKING);
- tests de fórmulas `NO_CONTRASTABLES` por falta de variables;
- tests de selector aislado (no debe activar);
- tests de evidencia contradictoria;
- tests de conflicto entre hipótesis;
- tests de `max_items: 3` (NO_EXCESSIVE_EVIDENCE_REQUEST).

### Integración
- no tocar runtime de diagnóstico;
- no asumir `--classification auto`;
- no asumir `--html-out`;
- integrarse con futuro `TankSelectionResult`;
- integrarse con futuro `IntakeRecord`.

### Documentación
- versión MAJOR alineada con contrato de KnowledgeTank;
- ejemplos end-to-end actualizados;
- matriz evidencia ↔ fórmulas ↔ clasificación actualizada.

---

## 21. Gaps conocidos

- no hay loader de tanques;
- no hay YAML ejecutable;
- no hay validador de evidencia;
- no hay selector runtime;
- no hay `TankSelectionResult` implementado;
- no hay `EvidenceRequest` formal implementado;
- no hay Boundary Layer que aplique `sufficiency_criteria`;
- no hay integración con `e2e_cli`;
- no hay `IntakeRecord` que persista pedidos de evidencia.

---

## 22. Roadmap posterior

Siguiente frente recomendado:

```text
SMARTPYME_TANK_SELECTION_SLICE
```

Luego, en orden:

1. `SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST` — persistir
   interrogatorio, tanques seleccionados y pedidos de evidencia.
2. `SMARTPYME_EVIDENCE_VALIDATION_LAYER` — validar evidencia recibida
   contra `sufficiency_criteria` (sin ejecutar fórmulas todavía).
3. `SMARTPYME_DEMO_WITH_INTAKE_BEFORE_REPORT` — demo end-to-end con
   interrogatorio → tanques → evidencia → análisis → reporte.

---

## 23. Cierre

Regla rectora de este tanque:

> **"La evidencia no confirma ni niega por sí sola; habilita contraste.
> La fórmula no diagnostica; cuantifica hipótesis. El tanque no decide;
> prepara la condición para que el análisis sea trazable, suficiente y
> compatible con el runtime real."**

---

*Este documento es normativo a nivel de diseño. No implica implementación
runtime en el HEAD actual.*
