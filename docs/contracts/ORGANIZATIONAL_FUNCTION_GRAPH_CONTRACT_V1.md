# ORGANIZATIONAL FUNCTION GRAPH CONTRACT V1

## Estado

```text
DRAFT_CONTRACT
NO_RUNTIME_CHANGE
NO_CODE_AUTHORIZATION
NO_IMPLEMENTATION_AUTHORIZATION
AUDIT_REQUIRED_BEFORE_IMPLEMENTATION
```

## Propósito

Definir el contrato conceptual del `Organizational Function Graph Engine V1`, en adelante `Motor de Grafo Funcional Organizacional`.

Este motor representa la capa que permite navegar incrementalmente una PyME como organismo funcional: nodos, fórmulas, variables, incógnitas, evidencia, patologías candidatas y desplazamientos entre zonas operativas.

No reemplaza el rotor, el pack de routing, FormulaEngine, EvidenceSufficiency, QuestionAlignmentGate, PathologyInterpreter ni OwnerFacingReport.

## Frase rectora

```text
síntoma → nodo → fórmula → incógnita X → evidencia mínima → siguiente pregunta
```

La función del motor no es diagnosticar por intuición, sino ordenar el próximo paso lógico dentro de un grafo funcional declarativo.

## Relación con contratos existentes

```text
ROTOR_DIAGNOSTICO_PYME_GENERICO_V1
  selecciona una ruta candidata inicial.

PYME_BASE_ROUTING_PACK_CONTRACT_V1
  declara rutas PyME genéricas.

ORGANIZATIONAL_FUNCTION_GRAPH_CONTRACT_V1
  navega un subgrafo funcional activo para decidir la próxima incógnita matemática a despejar.
```

## Principios no negociables

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
No hardcodear nodos, fórmulas, patologías, variables ni evidencia en Python.
No diagnosticar sin evidencia suficiente.
No pedir toda la evidencia posible.
No navegar nodos lejanos sin justificación.
No interpretar patologías dentro del motor V1.
No prescribir tratamientos.
No redactar salida owner-facing final.
No reemplazar módulos vivos.
Toda navegación debe dejar trazabilidad.
```

## Definición

El `Organizational Function Graph Engine V1` es un motor estable de navegación diagnóstica incremental.

Consume conocimiento declarado en packs y produce un estado de navegación funcional.

El motor sabe:

```text
- cargar grafo funcional declarado;
- validar nodos y relaciones;
- activar un subgrafo cercano;
- identificar incógnitas disponibles;
- seleccionar una incógnita dominante candidata;
- declarar evidencia mínima candidata;
- diferir evidencia de nodos lejanos;
- registrar trazabilidad;
- fallar cerrado.
```

El motor no sabe:

```text
- calcular fórmulas;
- interpretar patologías;
- confirmar diagnósticos;
- redactar preguntas finales al dueño;
- ejecutar tratamientos;
- crear packs;
- mutar conocimiento;
- administrar empresas.
```

## Unidad conceptual

### Nodo funcional

Zona del organismo PyME.

Ejemplos conceptuales:

```text
ventas
cobranzas
caja
cuentas_corrientes
margen
stock
proveedores
produccion
automatizacion_roi
```

### Fórmula

Instrumento matemático que mide una relación entre variables.

La fórmula no vive en este motor. Vive en `FormulaPack` o contrato equivalente.

### Variable

Dato atómico necesario para despejar una fórmula o incógnita.

### Incógnita

Variable o relación todavía no despejada que puede reducir incertidumbre operativa.

### Evidencia

Fuente o dato que permite obtener una variable.

### Patología

Disfunción organizacional posible. No se interpreta ni confirma dentro del motor V1.

### Pregunta

Solicitud mínima de evidencia o significado. La redacción owner-facing final no pertenece al motor.

## Packs requeridos conceptuales

```text
FunctionalGraphPack
VariablePack
EvidencePack
```

En V1, el grafo sólo tiene alcance directo sobre `FunctionalGraphPack`, `VariablePack` y `EvidencePack`.

`FormulaPack` se referencia externamente, pero no pertenece al alcance operativo directo del grafo V1.

`PathologyPack`, `SectorPack`, `LanguagePack` y `PresentationPack` quedan fuera del alcance operativo de V1.

El motor no exige que esos packs existan como runtime. Sólo declara la frontera conceptual futura.

## Separación motor / conocimiento

```text
El motor no contiene conocimiento PyME.
El motor navega conocimiento PyME declarado.
```

Prohibido:

```text
- fórmulas hardcodeadas;
- patologías hardcodeadas;
- nodos sectoriales hardcodeados;
- umbrales embebidos en código;
- reglas de negocio dentro del kernel;
- rutas owner-facing como lógica interna.
```

Permitido:

```text
- validar packs;
- construir grafo desde packs;
- calcular distancia estructural entre nodos;
- seleccionar incógnita dominante candidata;
- declarar evidencia mínima candidata;
- registrar estado del ciclo;
- bloquear si falta conocimiento declarado.
```

## Ciclo de navegación incremental

```text
1. Recibir señal normalizada o ruta candidata.
2. Identificar nodo funcional dominante.
3. Activar subgrafo cercano.
4. Leer fórmulas relacionadas declaradas.
5. Detectar variables conocidas y faltantes.
6. Identificar incógnitas posibles.
7. Elegir una incógnita dominante candidata.
8. Declarar evidencia mínima candidata.
9. Diferir evidencia de nodos lejanos.
10. Emitir estado trazable.
11. Esperar nueva evidencia o significado.
12. Recalcular subgrafo activo.
```

## Autonomía permitida

La autonomía permitida es autonomía de navegación.

```text
Puede decidir el próximo paso lógico dentro del grafo.
No puede emitir conclusión diagnóstica final sin módulos y evidencia correspondientes.
```

Permitido:

```text
La próxima incógnita más informativa candidata es X.
La evidencia mínima candidata para X es Y.
Estas evidencias quedan diferidas porque pertenecen a nodos menos cercanos.
```

Prohibido:

```text
La empresa tiene esta patología.
La causa está confirmada.
Hay que aplicar este tratamiento.
Conviene automatizar.
Conviene subir precios.
```

## Estado interno mínimo

```json
{
  "case_id": "case_001",
  "dominant_node": "cash_liquidity",
  "active_subgraph": [
    "sales",
    "collections",
    "accounts_receivable",
    "cash",
    "gross_margin",
    "inventory_cash_lock",
    "supplier_payments"
  ],
  "current_formula_reference": "ratio_cobranza",
  "current_unknown": "cobranzas_del_periodo",
  "known_variables": ["ventas_total"],
  "missing_variables": ["cobranzas_del_periodo", "cuentas_corrientes_clientes"],
  "minimal_evidence_candidate": ["cobranzas_del_periodo"],
  "deferred_evidence": ["stock_final", "ebitda", "tiempos_de_proceso"],
  "status": "NEEDS_EVIDENCE",
  "stop_condition": "NO_DIAGNOSIS_UNTIL_CURRENT_UNKNOWN_RESOLVED"
}
```

## Semántica obligatoria

### dominant_node

Nodo funcional inicial o actual. No implica diagnóstico.

### active_subgraph

Conjunto de nodos cercanos activados por la señal, la ruta o la evidencia disponible.

No debe incluir toda la empresa por defecto.

### current_formula_reference

Referencia declarativa a una fórmula relevante para la incógnita actual.

No implica ejecución, cálculo ni prioridad matemática global.

### current_unknown

Incógnita dominante candidata del ciclo actual.

La selección de `current_unknown` es una decisión de navegación contractual.

No implica diagnóstico, ejecución matemática, priorización global del caso ni conversión del grafo en orquestador.

Debe haber una sola incógnita dominante por ciclo.

### minimal_evidence_candidate

Evidencia mínima candidata para despejar la incógnita actual.

No certifica suficiencia.

### deferred_evidence

Evidencia pospuesta por distancia, costo o falta de relación directa con la incógnita actual.

No significa descarte definitivo.

### stop_condition

Condición explícita que impide diagnóstico, salto de nodo o conclusión prematura.

## Distancia funcional

El motor puede usar distancia funcional declarativa entre nodos.

Ejemplo conceptual:

```text
ventas → cobranzas → caja
ventas → costos → margen
stock → capital_inmovilizado → caja
produccion → tiempo → costo
proveedores → pagos → caja
```

Reglas:

```text
- primero nodos cercanos;
- después nodos adyacentes;
- nodos lejanos quedan diferidos;
- no saltar a sectores o tratamientos sin evidencia;
- todo desplazamiento debe explicar razón.
```

## Relación fórmula / patología

Una fórmula no diagnostica sola.

Una patología, si existiera en contrato posterior, requeriría convergencia de fórmulas, evidencia y reglas específicas.

Este motor V1 no confirma patologías.

Permitido:

```text
esta incógnita puede alimentar interpretación posterior en otro módulo.
```

Prohibido:

```text
esta incógnita confirma patología.
```

## Micrografo inicial recomendado para auditoría

El primer micrografo conceptual debe ser:

```text
CASH_LIQUIDITY_GRAPH_V1
```

Con nodos:

```text
ventas
cobranzas
caja
cuentas_corrientes
margen
stock
pagos_proveedores
```

Con fórmulas de referencia:

```text
ratio_cobranza
brecha_caja_ventas
margen_bruto_pct
stock_cash_lock
supplier_payment_pressure
```

Con patologías sólo como referencias externas no interpretadas:

```text
venta_no_cobrada
margen_insuficiente
capital_inmovilizado_en_stock
```

Objetivo auditable:

```text
reducir una lista amplia de evidencias posibles a 2-4 evidencias mínimas candidatas según la incógnita dominante del ciclo.
```

## Salida contractual del motor

El motor debe emitir un paquete trazable, no una respuesta final al dueño.

```json
{
  "dominant_node": "cash_liquidity",
  "active_subgraph": ["sales", "collections", "cash", "accounts_receivable"],
  "current_formula_reference": "ratio_cobranza",
  "current_unknown": "cobranzas_del_periodo",
  "minimal_evidence_request_candidate": [
    "cobranzas_del_periodo",
    "cuentas_corrientes_clientes"
  ],
  "deferred_evidence": ["stock_final", "ebitda", "tiempos_de_proceso"],
  "reason_code": "SALES_CASH_SYMPTOM_REQUIRES_COLLECTIONS_UNKNOWN_FIRST",
  "confidence_label": "medium",
  "stop_condition": "NO_DIAGNOSIS_UNTIL_COLLECTIONS_UNKNOWN_RESOLVED"
}
```

El `reason_code` es técnico. La redacción owner-facing pertenece a otro módulo.

`confidence_label` no expresa certeza diagnóstica. Sólo expresa confianza estructural de navegación según completitud del grafo y del pack declarado.

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

## Reglas de oro

```text
1. Una incógnita dominante por ciclo.
2. Sólo pedir evidencia mínima para despejar esa incógnita.
3. Posponer evidencia de nodos lejanos.
4. No diagnosticar sin cierre matemático suficiente.
5. Desplazar el foco sólo a nodos cercanos o adyacentes.
6. No hardcodear conocimiento sectorial en el motor.
7. Todo nuevo conocimiento entra por packs.
8. Toda fórmula debe declarar inputs, outputs, unknowns y relaciones externas.
9. Toda patología queda fuera de interpretación en V1.
10. Todo ciclo debe dejar trazabilidad.
```

## Criterios de aceptación

El contrato es aceptable si:

```text
- preserva kernel estable;
- mantiene conocimiento enchufable;
- define grafo funcional sin runtime;
- separa nodo, fórmula, variable, incógnita, evidencia y patología;
- no invade FormulaEngine;
- no invade EvidenceSufficiency;
- no invade QuestionAlignmentGate;
- no invade PathologyInterpreter;
- no invade OwnerFacingReport;
- permite reducir evidencia amplia a evidencia mínima candidata;
- mantiene fail-closed;
- no habilita implementación.
```

## Criterios de rechazo

Se rechaza si:

```text
- calcula fórmulas;
- diagnostica patologías;
- prescribe tratamientos;
- redacta salida owner-facing;
- procesa texto libre directamente;
- certifica evidencia suficiente;
- contiene reglas sectoriales hardcodeadas;
- convierte el grafo en ERP;
- convierte el motor en orquestador total;
- habilita código desde este contrato.
```

## Próximo paso metodológico

```text
AUDITORIA_CONTRACTUAL_DEL_GRAFO_FUNCIONAL
```

Este documento no habilita código, tests, schemas Pydantic, runtime, modificación de `PymIA-Live`, creación de packs activos ni cambios en el motor diagnóstico.
