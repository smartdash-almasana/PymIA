# CASH LIQUIDITY GRAPH SIMULATION SPEC V1

## Estado

```text
DRAFT_SIMULATION_SPEC
NO_RUNTIME_CHANGE
NO_CODE_AUTHORIZATION
NO_IMPLEMENTATION_AUTHORIZATION
AUDIT_REQUIRED_BEFORE_IMPLEMENTATION
```

## Propósito

Definir una simulación contractual del micrografo `CASH_LIQUIDITY_GRAPH_V1` declarado en `ORGANIZATIONAL_FUNCTION_GRAPH_CONTRACT_V1.md`.

La simulación debe validar si el grafo funcional puede reducir señales amplias de caja, ventas, cobranzas, margen, stock y proveedores a una incógnita dominante y a evidencia mínima candidata, sin diagnosticar, sin calcular fórmulas y sin prescribir tratamientos.

## Fuentes rectoras

```text
AGENTS.md
docs/contracts/ROTOR_DIAGNOSTICO_PYME_GENERICO_V1.md
docs/contracts/PYME_BASE_ROUTING_PACK_CONTRACT_V1.md
docs/contracts/ORGANIZATIONAL_FUNCTION_GRAPH_CONTRACT_V1.md
docs/adr/ADR-024-pack-system-foundation.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
```

## Alcance

Esta especificación sólo cubre simulación manual/documental.

No habilita:

```text
- código;
- tests automatizados;
- schemas Pydantic;
- parser de packs;
- runtime;
- cambios en PymIA-Live;
- cambios en FormulaEngine;
- cambios en EvidenceSufficiency;
- cambios en QuestionAlignmentGate;
- diagnóstico patológico;
- tratamientos;
- redacción owner-facing final.
```

## Micrografo bajo simulación

```text
CASH_LIQUIDITY_GRAPH_V1
```

Nodos permitidos:

```text
sales
collections
cash
accounts_receivable
gross_margin
inventory_cash_lock
supplier_payments
```

Fórmulas de referencia permitidas:

```text
ratio_cobranza
brecha_caja_ventas
margen_bruto_pct
stock_cash_lock
supplier_payment_pressure
```

Estas fórmulas son referencias declarativas. No se ejecutan, no se calculan y no priorizan cálculo.

## Regla central

```text
Una simulación válida debe elegir una sola current_unknown dominante por ciclo.
```

La selección de `current_unknown` es navegación contractual. No implica diagnóstico, ejecución matemática, priorización global ni orquestación total.

## Estados permitidos

```text
GRAPH_ROUTE_CANDIDATE
NEEDS_EVIDENCE
NEEDS_NORMALIZATION
NEEDS_PACK
BLOCKED_BY_DISTANCE
BLOCKED_BY_MISSING_FORMULA_REFERENCE
BLOCKED_BY_MISSING_VARIABLE_DEFINITION
BLOCKED_BY_CONTRACT_BOUNDARY
```

## Estados prohibidos

```text
PATHOLOGY_CONFIRMED
TREATMENT_SELECTED
FORMULA_EXECUTED
EVIDENCE_SUFFICIENT_CERTIFIED
OWNER_MESSAGE_RENDERED
AUTOMATION_APPROVED
```

## Forma obligatoria de cada caso simulado

Cada caso debe completarse con esta estructura:

```yaml
case_id: string
input_signal: string
input_mode: string
initial_route_source: string
dominant_node: string
active_subgraph: list[string]
current_formula_reference: string
current_unknown: string
known_variables: list[string]
missing_variables: list[string]
minimal_evidence_candidate: list[string]
deferred_evidence: list[string]
status: string
reason_code: string
stop_condition: string
boundary_check:
  calculated_formula: false
  diagnosed_pathology: false
  interpreted_pathology: false
  certified_evidence_sufficiency: false
  selected_treatment: false
  rendered_owner_message: false
  replaced_qag: false
  became_orchestrator: false
```

## Casos obligatorios

### Caso 1 — ventas altas, caja baja

```yaml
case_id: CASH_GRAPH_001
input_signal: vendo mucho pero no me queda plata
input_mode: OWNER_SYMPTOM_NORMALIZED
initial_route_source: CIRCUIT_LIQUIDEZ_OPERATIVA
dominant_node: cash
active_subgraph:
  - sales
  - collections
  - cash
  - accounts_receivable
current_formula_reference: ratio_cobranza
current_unknown: cobranzas_del_periodo
known_variables:
  - ventas_periodo
missing_variables:
  - cobranzas_del_periodo
  - cuentas_corrientes_clientes
minimal_evidence_candidate:
  - cobranzas_del_periodo
deferred_evidence:
  - stock_final
  - margen_bruto_pct
  - vencimientos_proveedores
status: NEEDS_EVIDENCE
reason_code: SALES_CASH_SYMPTOM_REQUIRES_COLLECTIONS_UNKNOWN_FIRST
stop_condition: NO_DIAGNOSIS_UNTIL_COLLECTIONS_UNKNOWN_RESOLVED
boundary_check:
  calculated_formula: false
  diagnosed_pathology: false
  interpreted_pathology: false
  certified_evidence_sufficiency: false
  selected_treatment: false
  rendered_owner_message: false
  replaced_qag: false
  became_orchestrator: false
```

### Caso 2 — ventas y cobranzas presentes, margen ausente

```yaml
case_id: CASH_GRAPH_002
input_signal: ventas y cobranzas del periodo disponibles
input_mode: EVIDENCE_FIRST
initial_route_source: CIRCUIT_LIQUIDEZ_OPERATIVA
dominant_node: collections
active_subgraph:
  - sales
  - collections
  - cash
  - gross_margin
current_formula_reference: margen_bruto_pct
current_unknown: costo_directo_periodo
known_variables:
  - ventas_periodo
  - cobranzas_del_periodo
missing_variables:
  - costo_directo_periodo
minimal_evidence_candidate:
  - costo_directo_periodo
deferred_evidence:
  - stock_final
  - vencimientos_proveedores
status: NEEDS_EVIDENCE
reason_code: COLLECTIONS_KNOWN_MARGIN_UNKNOWN_BEFORE_DIAGNOSTIC_INTERPRETATION
stop_condition: NO_DIAGNOSIS_UNTIL_MARGIN_UNKNOWN_RESOLVED
boundary_check:
  calculated_formula: false
  diagnosed_pathology: false
  interpreted_pathology: false
  certified_evidence_sufficiency: false
  selected_treatment: false
  rendered_owner_message: false
  replaced_qag: false
  became_orchestrator: false
```

### Caso 3 — caja baja con stock alto declarado

```yaml
case_id: CASH_GRAPH_003
input_signal: tengo mucha mercaderia parada y falta caja
input_mode: OWNER_SYMPTOM_NORMALIZED
initial_route_source: CIRCUIT_STOCK_CAPITAL_INMOVILIZADO
dominant_node: inventory_cash_lock
active_subgraph:
  - inventory_cash_lock
  - cash
  - sales
current_formula_reference: stock_cash_lock
current_unknown: stock_final_valorizado
known_variables:
  - ventas_periodo
missing_variables:
  - stock_final_valorizado
  - costo_ventas_periodo
minimal_evidence_candidate:
  - stock_final_valorizado
  - costo_ventas_periodo
deferred_evidence:
  - cobranzas_del_periodo
  - margen_bruto_pct
status: NEEDS_EVIDENCE
reason_code: INVENTORY_CASH_SIGNAL_REQUIRES_STOCK_VALUE_FIRST
stop_condition: NO_PATHOLOGY_INTERPRETATION_UNTIL_STOCK_UNKNOWN_RESOLVED
boundary_check:
  calculated_formula: false
  diagnosed_pathology: false
  interpreted_pathology: false
  certified_evidence_sufficiency: false
  selected_treatment: false
  rendered_owner_message: false
  replaced_qag: false
  became_orchestrator: false
```

### Caso 4 — presión de proveedores y caja insuficiente

```yaml
case_id: CASH_GRAPH_004
input_signal: proveedores presionan y la caja no alcanza
input_mode: OWNER_SYMPTOM_NORMALIZED
initial_route_source: CIRCUIT_PROVEEDORES_PRESION_FINANCIERA
dominant_node: supplier_payments
active_subgraph:
  - supplier_payments
  - cash
  - collections
  - accounts_receivable
current_formula_reference: supplier_payment_pressure
current_unknown: deuda_vencida_con_proveedores
known_variables:
  - caja_disponible
missing_variables:
  - deuda_vencida_con_proveedores
  - vencimientos_proveedores
minimal_evidence_candidate:
  - deuda_vencida_con_proveedores
  - vencimientos_proveedores
deferred_evidence:
  - stock_final
  - margen_bruto_pct
status: NEEDS_EVIDENCE
reason_code: SUPPLIER_PRESSURE_REQUIRES_PAYABLES_DUE_DATES_FIRST
stop_condition: NO_INSOLVENCY_INFERENCE_UNTIL_PAYABLES_UNKNOWN_RESOLVED
boundary_check:
  calculated_formula: false
  diagnosed_pathology: false
  interpreted_pathology: false
  certified_evidence_sufficiency: false
  selected_treatment: false
  rendered_owner_message: false
  replaced_qag: false
  became_orchestrator: false
```

### Caso 5 — síntoma abierto sin eje claro

```yaml
case_id: CASH_GRAPH_005
input_signal: quiero entender que pasa en mi empresa
input_mode: OPEN_EXPLORATION_NORMALIZED
initial_route_source: none
dominant_node: none
active_subgraph: []
current_formula_reference: none
current_unknown: none
known_variables: []
missing_variables: []
minimal_evidence_candidate: []
deferred_evidence: []
status: NEEDS_NORMALIZATION
reason_code: OPEN_EXPLORATION_REQUIRES_INITIAL_AXIS_BEFORE_GRAPH_NAVIGATION
stop_condition: NO_GRAPH_NAVIGATION_WITHOUT_DOMINANT_NODE
boundary_check:
  calculated_formula: false
  diagnosed_pathology: false
  interpreted_pathology: false
  certified_evidence_sufficiency: false
  selected_treatment: false
  rendered_owner_message: false
  replaced_qag: false
  became_orchestrator: false
```

## Casos adicionales requeridos para auditoría externa

Una auditoría externa debe agregar al menos 15 casos más:

```text
- 3 casos de ventas/cobranzas/caja;
- 3 casos de stock/caja;
- 3 casos de margen/caja;
- 3 casos de proveedores/caja;
- 3 casos ambiguos que deban quedar en NEEDS_NORMALIZATION o BLOCKED_BY_CONTRACT_BOUNDARY.
```

## Checks obligatorios por caso

Cada caso debe confirmar explícitamente:

```text
- no calculó fórmula;
- no diagnosticó patología;
- no interpretó patología;
- no certificó suficiencia;
- no seleccionó tratamiento;
- no redactó owner-facing output;
- no reemplazó QAG;
- no se convirtió en orquestador.
```

## Preguntas de auditoría

```text
1. ¿El micrografo reduce evidencia amplia a evidencia mínima candidata?
2. ¿Respeta una sola current_unknown por ciclo?
3. ¿Evita pedir toda la evidencia posible?
4. ¿Difiere nodos lejanos con razón trazable?
5. ¿Algún caso obliga a cálculo real?
6. ¿Algún caso obliga a diagnóstico patológico?
7. ¿Algún caso requiere owner-facing output?
8. ¿Algún caso necesita QAG antes de entrar al grafo?
9. ¿Algún reason_code suena diagnóstico?
10. ¿El micrografo puede seguir como simulación contractual sin runtime?
```

## Criterios de aceptación

La simulación es aceptable si:

```text
- todos los casos respetan fronteras;
- cada caso tiene una sola current_unknown o queda bloqueado;
- minimal_evidence_candidate no certifica suficiencia;
- deferred_evidence no implica descarte definitivo;
- no aparece patología confirmada;
- no aparece tratamiento;
- no aparece owner-facing final;
- no se habilita implementación.
```

## Criterios de rechazo

Se rechaza si:

```text
- un caso calcula;
- un caso diagnostica;
- un caso interpreta patología;
- un caso prescribe tratamiento;
- un caso requiere toda la evidencia posible;
- un caso permite varias current_unknown dominantes;
- un caso convierte deferred_evidence en plan operativo;
- un caso salta QAG ante input ambiguo;
- la simulación fuerza runtime.
```

## Próximo paso metodológico

```text
AUDITORIA_CONTRACTUAL_DE_SIMULACION_CASH_LIQUIDITY_GRAPH_V1
```

Este documento no habilita código, tests, schemas Pydantic, runtime, modificación de `PymIA-Live`, creación de packs activos ni cambios en el motor diagnóstico.
