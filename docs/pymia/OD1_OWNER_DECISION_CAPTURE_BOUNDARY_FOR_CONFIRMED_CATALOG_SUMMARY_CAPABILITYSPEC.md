# OD1 — Owner Decision Capture Boundary for Confirmed Catalog Summary CapabilitySpec

Estado: `ACCEPTED`

Fecha: 2026-06-12

## 1. Enunciado

OD1 define la frontera documental entre una confirmación semántica del dueño sobre una síntesis de catálogo y un `DecisionRecord` formal compatible con `owner-decision-v1`.

OD1 deriva de:

```text
docs/adr/ADR-025-faithful-operator-output-vs-owner-report-delivery-boundary.md
docs/pymia/POST_ADR_022_NEXT_FRONT_CLASSIFICATION_TASKSPEC.md
docs/contratos/owner-decision-v1.md
```

OD1 no implementa código.
OD1 no abre C4.
OD1 no autoriza delivery.
OD1 no autoriza reporte productivo.
OD1 no autoriza ejecución de acciones.
OD1 no autoriza M36.

## 2. Contexto certificado

C1, C2 y C3 dejaron disponible el siguiente circuito local:

```text
Faithful Operator
→ catalog_reconciliation
→ owner-facing summary
→ owner confirmation boundary
```

C3 puede producir estados como:

```text
catalog_summary_confirmed
catalog_summary_correction_requested
catalog_summary_owner_uncertain
catalog_summary_unclear_confirmation
```

ADR-025 estableció que:

```text
catalog_summary_confirmed ≠ diagnóstico final
catalog_summary_confirmed ≠ Owner-Facing Report V1
catalog_summary_confirmed ≠ Controlled Delivery
catalog_summary_confirmed ≠ autorización automática
```

`owner-decision-v1` establece que SmartPyme no decide; sólo propone, y que toda acción con impacto requiere un DecisionRecord válido emitido por el dueño o actor autorizado.

## 3. Problema

Después de C3 puede existir una confirmación semántica válida:

```text
"sí, esta síntesis representa mi negocio"
```

Pero esa frase no especifica necesariamente:

```text
- qué acción se aprueba;
- qué acción se rechaza;
- qué alcance tiene la decisión;
- qué condiciones aplican;
- si hay autorización para ejecutar;
- si hay riesgo reconocido;
- si la decisión vence;
- si existe un owner_id o actor autorizado.
```

Por lo tanto, no puede convertirse automáticamente en un `DecisionRecord` de tipo `APPROVE` o `AUTHORIZE_ACTION`.

## 4. Decisión documental

OD1 establece que:

```text
catalog_summary_confirmed
```

es una confirmación semántica local, no una decisión formal.

Sólo puede convertirse en un `DecisionRecord` si existe una expresión explícita del dueño compatible con `owner-decision-v1` y con alcance suficiente.

## 5. Clasificación de respuestas posteriores a C3

### 5.1 Confirmación semántica simple

Ejemplo:

```text
sí, correcto
eso representa mi situación
está bien resumido
```

Clasificación:

```text
semantic_confirmation_only
```

DecisionRecord:

```text
NO
```

Motivo:

```text
confirma representación, pero no decide acción.
```

### 5.2 Solicitud de aclaración

Ejemplo:

```text
explicame mejor eso
qué significa impuestos y comisiones
mostrame qué falta
```

Clasificación:

```text
request_clarification_candidate
```

DecisionRecord posible:

```text
REQUEST_CLARIFICATION
```

Condición:

```text
requiere owner_id/cliente_id/decision_scope si se registra formalmente.
```

No autoriza acción.

### 5.3 Corrección o nueva evidencia

Ejemplo:

```text
eso está mal
te paso otro archivo
faltan datos
esa columna no significa eso
```

Clasificación:

```text
correction_or_new_evidence
```

DecisionRecord posible:

```text
REQUEST_CLARIFICATION o DEFER
```

Condición:

```text
no autoriza acción; sólo registra necesidad de corregir, diferir o aclarar.
```

### 5.4 Aprobación explícita de una propuesta

Ejemplo:

```text
apruebo revisar ese punto
apruebo avanzar con esa revisión
```

Clasificación:

```text
approve_candidate
```

DecisionRecord posible:

```text
APPROVE
```

Condición:

```text
requiere propuesta concreta, decision_scope, owner_id, cliente_id y acciones autorizadas o rechazadas si aplica.
```

No equivale automáticamente a `AUTHORIZE_ACTION`.

### 5.5 Autorización explícita de acción

Ejemplo:

```text
autorizo ejecutar la conciliación
autorizo crear el job
hacé esa acción
```

Clasificación:

```text
authorize_action_candidate
```

DecisionRecord posible:

```text
AUTHORIZE_ACTION
```

Condición:

```text
requiere acción específica, alcance, owner_id, cliente_id, condiciones y límites.
```

Sin esos campos debe bloquear o pedir aclaración.

### 5.6 Rechazo

Ejemplo:

```text
no apruebo
no quiero avanzar
rechazo esa propuesta
```

Clasificación:

```text
reject_candidate
```

DecisionRecord posible:

```text
REJECT o STOP
```

Condición:

```text
requiere alcance explícito para saber qué se rechaza o detiene.
```

### 5.7 Incertidumbre o ambigüedad

Ejemplo:

```text
no sé
no estoy seguro
más o menos
puede ser
```

Clasificación:

```text
no_decision
```

DecisionRecord:

```text
NO
```

Resultado:

```text
bloqueo honesto o REQUEST_CLARIFICATION si el dueño pide aclaración concreta.
```

## 6. Campos mínimos para que exista DecisionRecord

OD1 no modifica `owner-decision-v1`, pero exige reconocer estos campos mínimos antes de considerar registrable una decisión:

```text
decision_type
cliente_id
owner_id
actor_role
decision_scope
decision_text
source_channel
audit_trail
```

Para `AUTHORIZE_ACTION`, además:

```text
authorized_actions
conditions, si aplican
risk_acknowledgement, si aplica
```

Para `REJECT` o `STOP`, además:

```text
rejected_actions o alcance detenido
```

## 7. Reglas de seguridad

```text
- catalog_summary_confirmed no crea DecisionRecord por sí solo.
- REQUEST_CLARIFICATION no autoriza acción.
- APPROVE no autoriza ejecución si no hay acción específica.
- AUTHORIZE_ACTION requiere acción concreta y alcance.
- Evidencia no equivale a autorización.
- Síntesis owner-facing no equivale a autorización.
- Confirmación semántica no equivale a aprobación.
- Ninguna acción se ejecuta sin DecisionRecord válido.
```

## 8. Relación con C1, C2 y C3

C1, C2 y C3 siguen siendo válidos.

OD1 no reinterpreta sus outputs como decisiones.

OD1 sólo agrega una frontera documental posterior:

```text
C3 output
→ classify owner reply for decision potential
→ DecisionRecord sólo si owner-decision-v1 lo permite
```

## 9. Relación con ADR-025

OD1 implementa documentalmente la categoría C definida en ADR-025:

```text
OwnerDecision / DecisionRecord capture under owner-decision-v1
```

No trabaja sobre:

```text
A. Local output continuation
B. Bridge to Owner-Facing Report V1
D. Controlled Delivery
```

## 10. Non-goals

OD1 no autoriza:

```text
- implementación;
- C4;
- delivery;
- PDF;
- Telegram;
- DB;
- Hermes;
- runtime externo;
- diagnóstico final;
- recomendaciones definitivas;
- ejecución de acciones;
- M36;
- nuevos puertos o gates formales;
- cambios en matcher;
- cambios en catálogos;
- cambios en owner-decision-v1.
```

## 11. Futuro TaskSpec permitido

Después de auditar y aceptar OD1, podría redactarse un TaskSpec de implementación sólo si:

```text
- no persiste productivamente;
- no usa canal externo;
- no ejecuta acciones;
- sólo clasifica potencial de DecisionRecord;
- conserva salida BLOCKED cuando faltan campos mínimos;
- no transforma confirmación semántica en autorización.
```

Nombre posible:

```text
OD1-T1 — Local Owner Decision Potential Classifier
```

Ese TaskSpec requerirá auditoría antes de código.

## 12. Criterio de aceptación de OD1

OD1 queda aceptado sólo si auditoría externa confirma que:

```text
- respeta ADR-025;
- respeta owner-decision-v1;
- no abre C4;
- no autoriza delivery;
- no convierte catalog_summary_confirmed en APPROVE;
- no convierte catalog_summary_confirmed en AUTHORIZE_ACTION;
- distingue confirmación semántica, aclaración, aprobación y autorización;
- no habilita ejecución.
```
