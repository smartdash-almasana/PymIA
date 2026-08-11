# SERVICE_1_RADAR_ARCHITECTURE_V1

Estado: CONCEPTUALLY APPROVED / IMPLEMENTATION IN PROGRESS
Fecha: 2026-08-10

## 1. Propósito

RADAR es un motor independiente y transversal de Servicio 1 para observar funciones matemáticas y operaciones significativas del negocio que el dueño decida radarizar.

RADAR no decide de antemano qué es riesgo, qué es positivo, qué es urgente ni qué merece comunicación. Su función es ofrecer observables, evaluar condiciones configuradas por el dueño y comunicar según el nivel elegido por ese dueño.

Principio rector:

> PymIA propone qué puede observar. El dueño decide qué es significativo. RADAR vigila lo acordado.

---

## 2. Principio arquitectónico central

RADAR debe existir como un único motor independiente, desacoplado de los verticales.

No deben existir motores separados por vertical:

- RadarConsorcios
- RadarContadores
- RadarDistribuidoras
- RadarSellers

Debe existir un único `RADAR ENGINE` con enchufes/adaptadores verticales.

```text
CONSORCIOS PLUG ───────┐
CONTADORES PLUG ───────┤
DISTRIBUIDORAS PLUG ───┼──→ RADAR ENGINE
SELLERS PLUG ──────────┘
```

Cada vertical declara qué elementos puede ofrecer para radarizar. El motor RADAR no necesita conocer la semántica interna del vertical más allá del contrato estándar recibido.

---

## 3. Separación de responsabilidades

### 3.1 Vertical

El vertical:

- calcula o expone observables;
- conoce sus capacidades productivas;
- sabe qué métricas y operaciones puede ofrecer al dueño;
- entrega valores y evidencia trazable;
- no define automáticamente fronteras ni niveles de comunicación.

### 3.2 Radar Plug / Adapter

El plug vertical:

- traduce capacidades del vertical al contrato común de RADAR;
- publica un catálogo amplio de funciones radarizables;
- no contiene lógica de alerta por defecto;
- no asigna riesgo, severidad o urgencia.

### 3.3 RADAR Engine

El motor:

- recibe observables estándar;
- carga las políticas de observación definidas por el dueño;
- evalúa condiciones matemáticas u operativas;
- genera eventos RADAR;
- entrega esos eventos a la capa de comunicación.

No recalcula la capacidad fuente ni modifica su verdad matemática.

### 3.4 Owner Policy

La política del dueño define:

- qué observable desea vigilar;
- bajo qué condición;
- qué frontera matemática aplica;
- qué nivel de comunicación desea;
- opcionalmente, más adelante, frecuencia, canal, repetición y otras preferencias.

La política pertenece al tenant/dueño, no al vertical ni al motor RADAR.

---

## 4. Contrato neutral de Observable

Primer corte implementado:

`SERVICE_1_RADAR_OBSERVABLE_V1`

Archivo:

`pymia/smartpyme/service_1_radar_observable_v1.py`

Campos actuales:

```text
observable_ref
vertical_ref
display_name
observable_kind
source_capability_ref
value_field_ref
unit
entity_scope
supported_operators
description
```

Tipos iniciales:

```text
METRIC
OPERATION
```

Operadores soportados inicialmente:

```text
GT
GTE
LT
LTE
EQ
NEQ
```

El observable es deliberadamente neutral.

No puede contener por defecto:

```text
risk
severity
urgency
threshold
boundary
communication_level
alert
default_action
positive
negative
```

Estas decisiones pertenecen a capas posteriores y, principalmente, a la configuración del dueño.

---

## 5. Funciones radarizables

Cada vertical debe ofrecer el menú más amplio razonable de funciones que ya pueda observar con evidencia suficiente.

El hecho de que una función aparezca en el menú NO implica que PymIA la considere riesgosa, importante o recomendable.

### Ejemplos Consorcios

Posibles observables:

```text
collection_rate_pct
debt_equivalent_periods
bank_unmatched_amount
bank_unmatched_count
cash_balance
expense_budget_deviation_pct
expense_historical_deviation_pct
provider_payment_amount
```

### Ejemplos Distribuidoras

```text
sku_margin_pct
stock_units
coverage_days
inventory_turnover
customer_dso
customer_concentration_pct
cash_balance
```

### Ejemplos Sellers

```text
publication_margin_pct
advertising_spend
return_rate_pct
stock_coverage_days
pending_mp_accreditation_amount
commission_ratio_pct
```

### Ejemplos Contadores

```text
client_dso
client_dpo
bank_unmatched_count
missing_document_count
cash_balance
payment_collection_gap
```

Estos catálogos deben evolucionar con evidencia real de clientes.

---

## 6. Niveles de comunicación

La categorización acordada no representa riesgo ni gravedad del negocio. Representa el nivel de comunicación requerido por el dueño.

V1 conceptual:

```text
1. REPORT
2. NOTIFICATION
3. ALERT
4. URGENCY
```

### REPORT

Dato disponible a demanda cuando el dueño consulta.

### NOTIFICATION

PymIA comunica un dato o evento que el dueño pidió seguir.

### ALERT

PymIA comunica que se cumplió una condición que el dueño marcó como especialmente significativa.

### URGENCY

PymIA comunica inmediatamente una condición que el dueño definió como prioritaria.

Importante:

`ALERT` y `URGENCY` no implican necesariamente un valor negativo. El dueño puede asignar cualquier nivel de comunicación a cualquier condición matemática que considere significativa.

---

## 7. Ejemplo de política definida por el dueño

Observable:

```text
collection_rate_pct
```

El dueño podría configurar:

```text
>= 97% → NOTIFICATION
< 90%  → ALERT
< 80%  → URGENCY
```

Otro dueño puede definir fronteras completamente diferentes.

RADAR no debe imponer valores por defecto como autoridad empresarial.

---

## 8. Métricas y operaciones significativas

RADAR debe contemplar al menos dos familias conceptuales.

### 8.1 Metric Observation

Valores matemáticos observables, por ejemplo:

```text
cobranza_pct
margen_pct
saldo_caja
desvio_presupuesto_pct
stock_units
```

### 8.2 Operation Observation

Hechos u operaciones que el dueño puede considerar significativos, por ejemplo:

```text
movimiento bancario sin referencia
pago por encima de X
cobranza extraordinaria
nuevo proveedor relevante
operación duplicada
```

El modelo técnico puede evolucionar, pero esta distinción conceptual debe preservarse.

---

## 9. Flujo canónico

```text
VERTICAL CAPABILITY
        ↓
RADAR PLUG
        ↓
RADAR OBSERVABLE
        ↓
OWNER SELECTION
        ↓
RADAR OBSERVATION POLICY
        ↓
RADAR ENGINE
        ↓
CONDITION EVALUATION
        ↓
RADAR EVENT
        ↓
COMMUNICATION LEVEL
REPORT / NOTIFICATION / ALERT / URGENCY
```

---

## 10. Límites de autoridad

RADAR no puede:

- decidir automáticamente qué es riesgo;
- decidir automáticamente qué es positivo;
- inventar fronteras empresariales;
- cambiar cálculos de capacidades fuente;
- inventar evidencia;
- aprobar pagos;
- cerrar conciliaciones;
- ejecutar decisiones contables;
- usar LLM como autoridad matemática o empresarial;
- activar vigilancia que el dueño no haya elegido.

---

## 11. Prevención

RADAR fue concebido también como sistema preventivo de fronteras matemáticas.

Sin embargo, la prevención predictiva no debe asumirse automáticamente.

Si en el futuro RADAR usa proyecciones, tendencias o distancia a una frontera, debe ser una función/configuración explícita del dueño.

Ejemplo futuro posible:

```text
frontera de caja = 3M
valor actual = 3.2M
proyección = 2.8M
```

RADAR solo debería generar una comunicación preventiva si el dueño configuró ese tipo de observación.

---

## 12. Elementos deliberadamente diferidos

No se congelan todavía en V1:

- frecuencia de repetición;
- anti-spam / histéresis;
- canales concretos;
- escalamiento entre personas;
- horarios y silenciamiento;
- políticas heredadas por organización/cliente/edificio;
- reglas compuestas entre múltiples métricas;
- tendencias y predicciones;
- evento de recuperación al volver a zona deseada;
- seguimiento periódico sin frontera.

Estas capacidades deberán incorporarse cuando la evidencia de clientes lo justifique.

---

## 13. Relación con prototipos existentes

Actualmente existen prototipos no consolidados:

```text
service_1_finding_envelope_v1.py
service_1_consorcios_monthly_radar_v1.py
```

No deben considerarse arquitectura RADAR definitiva.

Problema detectado:

`MonthlyRadarV1` actual usa una jerarquía fija `HIGH / MODERATE / LOW / INFO`, incompatible con el principio de que la significación y el nivel de comunicación pertenecen al dueño.

Estos prototipos pueden reutilizarse parcialmente como capa de composición/presentación, pero deben revisarse antes de consolidarse.

---

## 14. Secuencia de implementación recomendada

```text
1. SERVICE_1_RADAR_OBSERVABLE_V1        ← implementado
2. SERVICE_1_RADAR_OBSERVATION_POLICY_V1
3. SERVICE_1_RADAR_ENGINE_V1
4. SERVICE_1_CONSORCIOS_RADAR_PLUG_V1
5. prueba física con políticas de dueño
6. evolución desde feedback real
```

Cada corte debe mantener:

```text
una tarea
→ una verificación
→ un resultado
→ una decisión
```

---

## 15. Definición canónica de RADAR V1

> RADAR es un motor independiente y transversal que observa funciones matemáticas y operaciones expuestas por enchufes verticales. PymIA ofrece al dueño el catálogo más amplio razonable de elementos radarizables; el dueño elige qué observar, define las condiciones o fronteras que considera significativas y asigna el nivel de comunicación deseado. RADAR evalúa exclusivamente esas políticas y genera comunicaciones sin atribuir por sí mismo riesgo, positividad, severidad o urgencia empresarial.
