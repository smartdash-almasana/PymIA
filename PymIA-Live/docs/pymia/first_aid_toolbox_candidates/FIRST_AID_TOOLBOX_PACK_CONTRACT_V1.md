# First Aid Toolbox Pack Contract V1

## Estado

CANDIDATE_CONTRACT

## Propósito

Definir el contrato documental candidato del botiquín de Primeros Auxilios PyME / Fase 1 a partir del inventario maestro consolidado.

Fuente base:

```text
PymIA-Live/docs/pymia/first_aid_toolbox_candidates/FIRST_AID_MASTER_CANDIDATE_INVENTORY_V1.md
```

Este contrato no implementa runtime.
Este contrato no crea loader.
Este contrato no toca kernel.
Este contrato no activa herramientas.

---

# 1. Servicio cubierto

```text
Primeros Auxilios PyME / Fase 1
```

Definición:

```text
Pedido puntual para ordenar, calcular, validar, alertar o pedir evidencia mínima.
```

No cubre:

```text
diagnóstico integral
causa raíz confirmada
estrategia completa
tratamiento operacional completo
auditoría contable o financiera certificada
```

---

# 2. Secuencia obligatoria

Toda ejecución futura del botiquín debe respetar esta secuencia:

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

Opción habilitante:

```text
Primeros Auxilios
Tengo algo puntual para ordenar o revisar ahora.
```

---

# 3. Principios rectores

```text
PymIA no es un oráculo.
PymIA pregunta primero.
PymIA no diagnostica sin suficiencia.
El conocimiento de dominio es enchufable.
Nada entra directo al kernel.
Fase 1 calcula y ordena.
Fase 2 interpreta y diagnostica.
```

---

# 4. Naturaleza del pack

El First Aid Toolbox Pack es un contenedor documental candidato de componentes heterogéneos:

```text
CalculationTool
ValidationPack
ChecklistPack
HeuristicPack
AlertRulePack
OwnerCopyPack
WorkflowPack
ReportPack
SimulationTool
```

Regla:

```text
Un componente candidato no es una herramienta ejecutable hasta que exista contrato runtime aprobado.
```

---

# 5. Estados permitidos

```text
USE_IN_PHASE_1
USE_IN_PHASE_1_WITH_GUARDRAILS
NOT_FOR_PHASE_1_PHASE_2
REVIEW_REQUIRED
DO_NOT_MIGRATE
```

## USE_IN_PHASE_1

Puede formar parte de Primeros Auxilios si la evidencia mínima está completa.

## USE_IN_PHASE_1_WITH_GUARDRAILS

Puede formar parte de Primeros Auxilios sólo con límites explícitos, confirmación y salida restringida.

## NOT_FOR_PHASE_1_PHASE_2

No entra en Primeros Auxilios. Pertenece a problema específico / diagnóstico sectorial.

## REVIEW_REQUIRED

No tiene decisión suficiente.

## DO_NOT_MIGRATE

No debe migrarse. Sólo pueden rescatarse patrones conceptuales con decisión HITL posterior.

---

# 6. Componentes candidatos Fase 1

## 6.1 USE_IN_PHASE_1

```text
flujo_de_fondos
proyeccion_ventas
ExcelStructureValidationPack
SimpleCashArqueoChecklist
OwnerSignalTemplate
owner_facing_copy_templates
partial_data_copy
not_calculable_na_copy
alert_severity_notification_mapping
immediate_action_short_copy
sla_breach_thresholds
backlog_risk_thresholds
weekly_brief_structure
```

## 6.2 USE_IN_PHASE_1_WITH_GUARDRAILS

```text
auto_ganancia
caja_diaria
costos_por_producto
cuentas_corrientes_clientes
precio_margen
rentabilidad_por_producto
simulador_inflacion
StockDesvioAlertRule
CostPriceReviewHeuristic
```

## 6.3 NOT_FOR_PHASE_1_PHASE_2

```text
auto_stock
compras_y_proveedores
control_de_gastos
punto_equilibrio
stock_control
```

---

# 7. Evidencia mínima por familia

## Intake / archivo

Evidencia mínima:

```text
archivo Excel o fuente tabular cargada
contexto mínimo de qué representa el archivo
período si aplica
```

Salida permitida:

```text
estructura detectada
faltantes visibles
columnas problemáticas
cobertura parcial
no calculable / no disponible
```

## Caja / flujo / saldos

Evidencia mínima:

```text
ingresos declarados
egresos declarados
saldo anterior si aplica
período
```

Salida permitida:

```text
ordenamiento de caja declarada
flujo neto simple
saldo acumulado
alerta limitada
```

Salida prohibida:

```text
caja real confirmada
conciliación bancaria
ganancia confirmada
fraude
```

## Precio / costo / margen básico

Evidencia mínima:

```text
precio de venta
costo unitario o lista de costos
unidades vendidas si aplica
margen objetivo si aplica
```

Salida permitida:

```text
margen bruto
markup
precio calculado con margen objetivo
alerta costo/precio
simulación limitada
```

Salida prohibida:

```text
precio óptimo definitivo
rentabilidad neta confirmada
estrategia comercial completa
```

## Alertas operativas

Evidencia mínima:

```text
señal o métrica normalizada
umbral aplicado
contexto mínimo de negocio
```

Salida permitida:

```text
alerta breve
canal sugerido
acción inmediata limitada
mini brief
```

Salida prohibida:

```text
causa raíz confirmada
tratamiento completo
diagnóstico integral
```

## Stock First Aid limitado

Evidencia mínima:

```text
ventas diarias o movimientos
conteo físico si existe
stock declarado
período
```

Salida permitida:

```text
desvío visible
faltante visible
alerta limitada
necesidad de más evidencia
```

Salida prohibida:

```text
rotación inventario diagnóstica
costo de reposición promedio
causa de merma
stock físico confirmado sin conteo
```

---

# 8. Composiciones candidatas

## 8.1 excel_triage_basic

Componentes:

```text
ExcelStructureValidationPack
flujo_de_fondos
proyeccion_ventas
partial_data_copy
not_calculable_na_copy
```

Salida:

```text
validación estructural + cálculos básicos + declaración de cobertura
```

## 8.2 cash_ordering_basic

Componentes:

```text
SimpleCashArqueoChecklist
caja_diaria
flujo_de_fondos
OwnerSignalTemplate
```

Salida:

```text
ordenamiento de caja declarada + alerta owner-facing
```

## 8.3 price_margin_basic

Componentes:

```text
CostPriceReviewHeuristic
precio_margen
rentabilidad_por_producto
simulador_inflacion
```

Salida:

```text
margen bruto, markup, señales costo/precio y simulación limitada
```

## 8.4 operational_alert_basic

Componentes:

```text
OwnerSignalTemplate
alert_severity_notification_mapping
immediate_action_short_copy
sla_breach_thresholds
backlog_risk_thresholds
weekly_brief_structure
```

Salida:

```text
alerta breve, canal sugerido, acción inmediata y mini brief
```

## 8.5 stock_minimal_alert

Componentes:

```text
StockDesvioAlertRule
OwnerSignalTemplate
partial_data_copy
```

Salida:

```text
alerta de desvío o faltante visible
```

---

# 9. Lenguaje owner-facing

## Permitido

```text
ordena
calcula
muestra
marca faltantes
marca inconsistencias
alerta
requiere más evidencia
no se puede determinar con la evidencia actual
```

## Prohibido

```text
diagnostica
confirma
certifica
revela
demuestra
garantiza
```

## Claims prohibidos

```text
diagnóstico integral de la empresa
auditoría contable certificada
rentabilidad real confirmada
precio óptimo definitivo
caja final confirmada
stock físico confirmado sin conteo
causa raíz confirmada
fraude detectado
estrategia comercial completa
```

---

# 10. Criterio de escalamiento

Escalar a Fase 2 cuando aparezca cualquiera de estas condiciones:

```text
uso de fórmula PHASE_2_DIAGNOSTIC
pedido de causa raíz
pedido de diagnóstico sectorial
pedido de rentabilidad real
pedido de punto de equilibrio
pedido de rotación de inventario
pedido de costo de reposición promedio
pedido de estrategia comercial
pedido de estructura completa
insuficiencia de evidencia para afirmar algo útil en Fase 1
```

---

# 11. Cuarentena / no migrar

No migrar desde fuentes externas:

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

Sólo se permite rescatar patrones conceptuales con decisión HITL posterior.

---

# 12. Resumen numérico

```text
USE_IN_PHASE_1: 13
USE_IN_PHASE_1_WITH_GUARDRAILS: 9
NOT_FOR_PHASE_1_PHASE_2: 5
Composiciones candidatas: 5
```

Nota:

```text
Los conteos mezclan herramientas, packs, reglas, templates, workflows y report patterns.
No equivalen a herramientas ejecutables.
```

---

# 13. Estado del contrato

```text
FIRST_AID_TOOLBOX_PACK_CONTRACT_V1 = CREATED
status: CANDIDATE_CONTRACT
runtime_impact: NONE
code_impact: NONE
tests_run: NO
```

---

# 14. Regla final

```text
Este contrato puede guiar futuras TaskSpecs, pero no autoriza implementación.
```
