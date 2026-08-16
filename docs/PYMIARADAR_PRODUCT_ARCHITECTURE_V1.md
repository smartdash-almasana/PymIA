# PymiaRadar — Product Architecture V1

**Fecha:** 2026-08-16
**Estado:** PRODUCT DEFINITION / ARCHITECTURE V1

## 1. Definición

PymiaRadar es un watchdog operativo-financiero para PyMEs.

Su función es observar evidencia empresarial ya entendida, detectar desvíos materiales, priorizarlos y emitir alertas accionables.

No es:

- un ERP;
- un dashboard BI genérico;
- un chatbot;
- un sistema de reporting;
- un agente autónomo con autoridad de decisión.

Sí es:

- un sistema pasivo de vigilancia;
- un detector de desvíos;
- un emisor de alertas tempranas;
- un mecanismo de aprendizaje a partir de feedback humano.

## 2. Tesis de producto

El valor principal no está en la IA aislada. Está en la combinación de:

```text
conectores
+ evidencia normalizada
+ detectores
+ priorización
+ alertas accionables
+ feedback humano
```

La IA entra solamente donde agrega valor y sin desplazar la autoridad determinística del sistema.

## 3. Relación con PymIA

PymIA y PymiaRadar resuelven problemas distintos.

```text
PYMIA
entiende qué significan los datos

PYMIARADAR
vigila cómo se comportan esos datos
```

PymiaRadar no debe volver a interpretar columnas que PymIA ya entendió y confirmó.

Ejemplo:

```text
PymIA:
"esta columna es venta neta"

PymiaRadar:
"la venta neta cayó 31% respecto de las últimas 4 semanas"
```

La frontera correcta es:

```text
Excel / ERP / Banco / Marketplace
↓
PymIA ingestion + semantic understanding
↓
EVIDENCIA CANÓNICA CONFIRMADA
↓
PymiaRadar
```

## 4. Arquitectura núcleo

```text
FUENTES
↓
CONECTORES
↓
NORMALIZACIÓN
↓
EVIDENCIA CANÓNICA
↓
RADAR OBSERVATIONS
↓
DETECTORES
↓
RADAR EVENTS
↓
PRIORIZACIÓN
↓
ALERTA ACCIONABLE
↓
FEEDBACK HUMANO
↓
MEMORIA RADAR POR TENANT
```

## 5. Objeto central: RadarObservation

PymiaRadar debe consumir evidencia ya entendida y expresarla como observaciones trazables.

Forma conceptual:

```text
RadarObservation
- tenant_id
- entity_ref
- metric_ref
- value
- period_ref
- baseline_ref
- evidence_refs
- observed_at
```

Ejemplo:

```text
tenant_id: cafeteria_abc
entity_ref: ventas
metric_ref: net_sales
period_ref: 2026-W33
value: 824000
baseline_ref: trailing_4_weeks
```

## 6. Objeto de salida: RadarEvent

Un detector transforma una observación en un evento cuando existe evidencia suficiente de un desvío.

Forma conceptual:

```text
RadarEvent
- event_id
- tenant_id
- metric_ref
- detector_ref
- current_value
- baseline_value
- delta
- delta_pct
- severity
- evidence_refs
- detected_at
- status
```

Ejemplo:

```text
metric_ref: net_sales
condition: DROP_VS_BASELINE
current_value: 824000
baseline_value: 1130000
delta_pct: -27.08%
severity: WARNING
```

## 7. Motor de detección

PymiaRadar V1 debe priorizar detectores determinísticos.

Primera capa:

```text
reglas heurísticas
comparaciones interperíodo
validaciones cruzadas
umbrales explícitos
```

Capas posteriores, sólo cuando exista evidencia de valor:

```text
detección estadística
outliers
cambio de distribución
estacionalidad
modelos pequeños
LLM explicativo
```

El LLM no determina por sí mismo que existe una anomalía.

## 8. Primeros detectores

PymiaRadar no debe comenzar con decenas de reglas.

Primer corte:

1. caída anormal de ventas;
2. aumento anormal de costos;
3. deterioro de cobranzas.

Expansión posterior:

- stock inmovilizado;
- deterioro de margen;
- concentración de ventas;
- cliente moroso que sigue comprando;
- diferencias Mercado Pago / banco;
- diferencias fiscales;
- drift operativo relevante.

## 9. Alertas accionables

Cada alerta debe contener al menos:

```text
qué cambió
cuánto cambió
desde cuándo
contra qué baseline
severidad
evidencia
acción sugerida
```

La alerta no debe limitarse a mostrar una métrica.

Ejemplo:

```text
Las ventas de esta semana están 27% por debajo del promedio de las últimas cuatro semanas.
```

## 10. IA en PymiaRadar

La IA queda acotada a funciones de interpretación y comunicación posteriores a la detección.

Flujo:

```text
DETECTOR DETERMINÍSTICO
↓
RADAR EVENT PROBADO
↓
LLM ACOTADO
↓
EXPLICACIÓN EN LENGUAJE PYME
```

La IA no puede:

- crear evidencia;
- modificar el evento determinístico;
- inventar causas;
- ejecutar acciones empresariales;
- otorgar autoridad de runtime;
- decidir por el usuario.

## 11. Feedback humano

El usuario debe poder responder a cada alerta con señales simples:

```text
Útil
No útil
Esperada
Revisar después
```

Ese feedback alimenta la memoria Radar del tenant.

El aprendizaje útil no es que el LLM “aprenda solo”, sino:

```text
evento
→ alerta
→ respuesta del dueño
→ memoria Radar
```

Esto permite aprender:

- qué alertas importan;
- qué thresholds generan ruido;
- qué variaciones son normales para un tenant;
- qué eventos ya fueron explicados;
- qué señales merecen mayor prioridad.

## 12. Conectores

PymiaRadar debe ser connector-first, pero sin sobreconstruir infraestructura.

Fuentes prioritarias iniciales:

- Excel/CSV mediante la ingesta existente de PymIA;
- Mercado Pago;
- AFIP/ARCA cuando corresponda y exista interfaz adecuada;
- exportaciones de ERPs PyME;
- bancos cuando la integración sea viable.

La arquitectura debe soportar:

```text
API oficial
exportación programada CSV/XLSX
carga manual como fallback
schema drift detection
```

No introducir una segunda arquitectura de ingesta para Excel.

## 13. Infraestructura: principio de mínima superficie

No adoptar por defecto, en el primer corte:

- Kubernetes;
- Airflow;
- Prefect;
- ClickHouse;
- TimescaleDB;
- Redis + Celery;
- Airbyte como dependencia estructural;
- nueva plataforma frontend.

Primero reutilizar la infraestructura existente de PymIA siempre que sea suficiente.

Sólo incorporar una nueva pieza cuando exista un cuello de botella probado.

## 14. Invariantes

```text
PYMIARADAR_CONSUMES_CONFIRMED_EVIDENCE
NO_SECOND_XLSX_PARSER
DETECTORS_BEFORE_LLM
LLM_HAS_NO_EVENT_AUTHORITY
NO_AUTONOMOUS_BUSINESS_ACTIONS
EVENTS_ARE_TRACEABLE
TENANT_FEEDBACK_IS_EVIDENCE
FAIL_CLOSED_ON_MISSING_EVIDENCE
```

## 15. MVP técnico

Objetivo del primer vertical:

```text
1 fuente real
→ evidencia canónica
→ 3 detectores
→ RadarEvent
→ alerta
→ feedback humano
```

No construir primero un dashboard completo.

No construir primero ML.

No construir primero diez conectores.

## 16. MVP comercial

Objetivo:

> un cliente real que reciba al menos una alerta material útil por semana.

Métrica principal:

```text
ALERTAS_ÚTILES / ALERTAS_EMITIDAS
```

Métricas secundarias:

- tiempo hasta primera alerta útil;
- falsos positivos;
- alertas silenciadas;
- eventos marcados como esperados;
- recurrencia de uso;
- retención mensual.

## 17. Diferenciación

La diferenciación potencial de PymiaRadar está en:

1. enfoque PyME-first;
2. conectores relevantes para Argentina y Latinoamérica;
3. reglas de negocio locales;
4. integración directa con la capa de evidencia de PymIA;
5. experiencia simple basada en alertas, no en BI complejo;
6. aprendizaje por tenant a partir de confirmaciones reales.

## 18. Estrategia de producto

PymIA Servicio 1 puede funcionar como puerta de entrada y construcción inicial de evidencia.

PymiaRadar puede convertirse en la capa recurrente.

```text
PymIA Servicio 1
"entendé mi Excel"

↓

PymiaRadar
"seguí vigilando mi empresa"
```

Esto crea una separación clara entre onboarding/entendimiento y vigilancia recurrente.

## 19. Decisión V1

```text
PRODUCT:
PymiaRadar

MISSION:
detectar tempranamente desvíos materiales en evidencia empresarial previamente entendida

INPUT:
evidencia canónica confirmada

CORE:
detectores determinísticos

OUTPUT:
RadarEvent trazable

LLM:
sólo explicación/comunicación posterior al evento

HUMAN:
feedback de utilidad/contexto

MEMORY:
historial y preferencias por tenant

NO:
ERP
BI genérico
agente autónomo
LLM con autoridad
segundo sistema de ingesta
```
