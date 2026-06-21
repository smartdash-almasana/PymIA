# First Aid Master Candidate Inventory V1

## Estado

CANDIDATE_MASTER_INVENTORY

## Propósito

Unificar candidatos documentales de Primeros Auxilios PyME / Fase 1 provenientes de:

```text
Exceland
SmartCounter
SmartD
```

Este archivo responde:

```text
¿Qué tenemos hoy para Primeros Auxilios PyME?
¿Qué entra como candidato?
¿Qué entra con guardrails?
¿Qué queda fuera de Fase 1?
¿Qué no debe migrarse?
```

## Límites

No runtime.
No código.
No loader.
No tests.
No activación real.
No modificación de kernel.

Todo lo listado queda como candidato documental hasta decisión HITL explícita.

---

# 1. Política rectora

```text
Fase 1 calcula, ordena, valida, alerta y pide evidencia.
Fase 1 no diagnostica.
Fase 2 interpreta y diagnostica con suficiencia.
```

Toda herramienta de Primeros Auxilios requiere:

```text
pregunta madre
→ opción elegida
→ primera capa formal de ficha organizacional
→ evidencia
→ herramienta proporcional
→ salida limitada
```

Pregunta madre:

```text
¿Qué necesitás resolver hoy?
```

Opción asociada:

```text
Primeros Auxilios
Tengo algo puntual para ordenar o revisar ahora.
```

---

# 2. Fuentes consolidadas

## Exceland

Fuente decisoria:

```text
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/first_aid_tool_selection_matrix_v1.yaml
```

Resultado:

```text
14 tools evaluadas
2 USE_IN_PHASE_1
7 USE_IN_PHASE_1_WITH_GUARDRAILS
5 NOT_FOR_PHASE_1_PHASE_2
0 REVIEW_REQUIRED
```

## SmartCounter

Fuente consolidada:

```text
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/first_aid_unified_toolbox_inventory_v1.yaml
```

Resultado:

```text
5 packs Fase 1
```

## SmartD

Fuente consolidada:

```text
PymIA-Live/docs/pymia/smartd_candidates/phase_1_first_aid.yaml
```

Resultado:

```text
8 items Fase 1
```

---

# 3. Inventario maestro por función

## 3.1 Intake / evidencia / validación de archivo

| ID | Origen | Tipo | Decisión | Límite |
|---|---|---|---|---|
| `ExcelStructureValidationPack` | SmartCounter | ValidationPack | USE_IN_PHASE_1 | Valida forma, headers y tipos; no valida verdad de negocio. |
| `owner_facing_copy_templates` | SmartD | OwnerCopyPack | USE_IN_PHASE_1 | Templates owner-facing; no deben prometer diagnóstico. |
| `partial_data_copy` | SmartD | OwnerCopyPack | USE_IN_PHASE_1 | Declara análisis parcial. |
| `not_calculable_na_copy` | SmartD | OwnerCopyPack | USE_IN_PHASE_1 | Diferencia NA de cero real. |

## 3.2 Caja / flujo / saldos

| ID | Origen | Tipo | Decisión | Límite |
|---|---|---|---|---|
| `flujo_de_fondos` | Exceland | CalculationTool | USE_IN_PHASE_1 | Ordena ingresos, egresos y saldo acumulado; no confirma caja real. |
| `proyeccion_ventas` | Exceland | CalculationTool | USE_IN_PHASE_1 | Calcula ingresos; no interpreta rentabilidad. |
| `auto_ganancia` | Exceland | CalculationTool | USE_IN_PHASE_1_WITH_GUARDRAILS | Ordena caja diaria; no confirma ganancia. |
| `caja_diaria` | Exceland | CalculationTool | USE_IN_PHASE_1_WITH_GUARDRAILS | Ordena caja diaria; no confirma resultado contable. |
| `cuentas_corrientes_clientes` | Exceland | CalculationTool | USE_IN_PHASE_1_WITH_GUARDRAILS | Ordena saldos declarados; no confirma deuda real. |
| `SimpleCashArqueoChecklist` | SmartCounter | ChecklistPack | USE_IN_PHASE_1 | Arqueo manual; no verifica efectivo físico automáticamente. |

## 3.3 Precio / costo / margen básico

| ID | Origen | Tipo | Decisión | Límite |
|---|---|---|---|---|
| `costos_por_producto` | Exceland | CalculationTool | USE_IN_PHASE_1_WITH_GUARDRAILS | Calcula sobre datos entregados; no certifica costo real. |
| `precio_margen` | Exceland | CalculationTool | USE_IN_PHASE_1_WITH_GUARDRAILS | Calcula precio, margen bruto y markup; no define precio óptimo. |
| `rentabilidad_por_producto` | Exceland | CalculationTool | USE_IN_PHASE_1_WITH_GUARDRAILS | Muestra margen bruto; no confirma rentabilidad neta. |
| `simulador_inflacion` | Exceland | SimulationTool | USE_IN_PHASE_1_WITH_GUARDRAILS | Simula efecto; no recomienda estrategia comercial. |
| `CostPriceReviewHeuristic` | SmartCounter | HeuristicPack | USE_IN_PHASE_1_WITH_GUARDRAILS | Alerta costo/precio; no forecast de inflación. |

## 3.4 Alertas / comunicación / severidad

| ID | Origen | Tipo | Decisión | Límite |
|---|---|---|---|---|
| `OwnerSignalTemplate` | SmartCounter | OwnerCopyPack | USE_IN_PHASE_1 | Entrega alerta; no resuelve causa raíz. |
| `alert_severity_notification_mapping` | SmartD | WorkflowPack | USE_IN_PHASE_1 | Mapea severidad a canal; no debe sobrealertar. |
| `immediate_action_short_copy` | SmartD | OwnerCopyPack | USE_IN_PHASE_1 | Una acción corta por alerta. |
| `sla_breach_thresholds` | SmartD | ValidationPack | USE_IN_PHASE_1 | Alerta por tiempo; no diagnostica causa. |
| `backlog_risk_thresholds` | SmartD | ValidationPack | USE_IN_PHASE_1 | Alerta acumulación; no diagnostica cuello de botella. |
| `weekly_brief_structure` | SmartD | ReportPack | USE_IN_PHASE_1 | Formato breve; máximo 3-7 acciones. |

## 3.5 Stock First Aid limitado

| ID | Origen | Tipo | Decisión | Límite |
|---|---|---|---|---|
| `StockDesvioAlertRule` | SmartCounter | AlertRulePack | USE_IN_PHASE_1_WITH_GUARDRAILS | Marca desvíos; no explica causa. |

---

# 4. Candidatos fuera de Fase 1

Estos quedan fuera de Primeros Auxilios porque requieren diagnóstico o fórmulas PHASE_2_DIAGNOSTIC.

| ID | Origen | Motivo |
|---|---|---|
| `auto_stock` | Exceland | Usa rotación de inventario y costo de reposición promedio. |
| `compras_y_proveedores` | Exceland | Usa costo de reposición promedio. |
| `control_de_gastos` | Exceland | Usa resultado neto. |
| `punto_equilibrio` | Exceland | Usa punto de equilibrio y resultado neto. |
| `stock_control` | Exceland | Usa rotación de inventario y costo de reposición promedio. |

---

# 5. No migrar / cuarentena

Fuente:

```text
PymIA-Live/docs/pymia/smartd_candidates/do_not_migrate.yaml
```

No migrar:

```text
MercadoLibre endpoints
Shopify integrations
Supabase DB snapshots
SQL específicos
Vercel/runtime específico
MCP configs
agent configs
copy runtime hardcodeado
```

Sólo pueden rescatarse patrones conceptuales con revisión HITL posterior.

---

# 6. Composiciones candidatas Primeros Auxilios

## 6.1 Excel triage básico

Componentes:

```text
ExcelStructureValidationPack
flujo_de_fondos
proyeccion_ventas
partial_data_copy
not_calculable_na_copy
```

Salida limitada:

```text
validación estructural + cálculos básicos + declaración de cobertura
```

No permite:

```text
diagnóstico financiero
rentabilidad real
caja confirmada
```

## 6.2 Caja ordenada básica

Componentes:

```text
SimpleCashArqueoChecklist
caja_diaria
flujo_de_fondos
OwnerSignalTemplate
```

Salida limitada:

```text
ordenamiento de caja declarada + alerta owner-facing
```

No permite:

```text
arqueo certificado
conciliación bancaria
fraude
```

## 6.3 Precio / margen básico

Componentes:

```text
CostPriceReviewHeuristic
precio_margen
rentabilidad_por_producto
simulador_inflacion
```

Salida limitada:

```text
margen bruto, markup, señales costo/precio y simulación limitada
```

No permite:

```text
precio óptimo
rentabilidad neta confirmada
estrategia comercial completa
```

## 6.4 Alerta operativa básica

Componentes:

```text
OwnerSignalTemplate
alert_severity_notification_mapping
immediate_action_short_copy
sla_breach_thresholds
backlog_risk_thresholds
weekly_brief_structure
```

Salida limitada:

```text
alerta breve, canal sugerido, acción inmediata y mini brief
```

No permite:

```text
causa raíz confirmada
tratamiento operacional completo
diagnóstico integral
```

## 6.5 Stock alerta mínima

Componentes:

```text
StockDesvioAlertRule
OwnerSignalTemplate
partial_data_copy
```

Salida limitada:

```text
alerta de desvío o faltante visible
```

No permite:

```text
rotación inventario diagnóstica
costo reposición promedio
causa de merma
stock físico confirmado sin conteo
```

---

# 7. Lenguaje prohibido en Primeros Auxilios

Verbos prohibidos:

```text
diagnostica
confirma
certifica
revela
demuestra
garantiza
```

Claims prohibidos:

```text
diagnóstico integral de la empresa
auditoría contable certificada
rentabilidad real confirmada
precio óptimo definitivo
caja final confirmada
stock físico confirmado sin conteo
causa raíz confirmada
```

Lenguaje permitido:

```text
ordena
calcula
muestra
marca faltantes
marca inconsistencias
requiere más evidencia
alerta de forma limitada
```

---

# 8. Resumen numérico

```text
Exceland componentes Fase 1: 9
SmartCounter componentes Fase 1: 5
SmartD componentes Fase 1: 8
Total bruto maestro: 22
Composiciones candidatas: 5
Fuera de Fase 1: 5
```

Nota:

```text
Total bruto maestro cuenta componentes de distinta naturaleza: herramientas, packs, reglas, copy y report patterns.
No equivale a herramientas ejecutables.
```

---

# 9. Estado de cierre

```text
FIRST_AID_MASTER_CANDIDATE_INVENTORY_V1 = CREATED
status: CANDIDATE_MASTER_INVENTORY
runtime_impact: NONE
code_impact: NONE
tests_run: NO
```

Próxima acción sana:

```text
Auditoría corta del master inventory antes de cualquier pack contract.
```
