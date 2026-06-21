# PYMIA_SERVICE_1_OPERATIONAL_FSM_V1

## Estado

```text
Tipo: ROADMAP_CYCLE_6
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Definir la máquina de estados operacional de PymIA Servicio 1 antes de abrir chatbot, pipeline, XLSX delivery o LLM adapter.

Este documento no implementa runtime. Sólo fija gobierno.

---

# 1. Cadena previa

```text
PYMIA_SERVICE_1_ARCHAEOLOGY_AUDIT_V1
→ PYMIA_SERVICE_1_CAPABILITY_MATRIX_V1
→ PYMIA_SERVICE_1_TASKSPEC_V1
→ PYMIA_SERVICE_1_OPERATIONAL_FSM_V1
```

---

# 2. Regla rectora

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

La FSM no calcula, no diagnostica, no concilia y no genera XLSX. Gobierna transición, bloqueo y próxima acción permitida.

---

# 3. Estados V1

```text
LISTENING
TASK_CLASSIFIED
EVIDENCE_REQUESTED
EVIDENCE_RECEIVED
CONFIRMATION_REQUIRED
ACTIVATION_EVALUATED
PROCESSING_AUTHORIZED
DELIVERY_READY
CLOSED
BLOCKED
```

---

# 4. Descripción de estados

| Estado | Descripción | Entrada mínima | Salida permitida |
|---|---|---|---|
| LISTENING | Recibe pedido del dueño o contador. | mensaje / archivo | crear TaskSpec draft |
| TASK_CLASSIFIED | El pedido fue clasificado como task_type Servicio 1. | TaskSpec mínima | pedir evidencia o evaluar activación |
| EVIDENCE_REQUESTED | Falta evidencia mínima. | missing_evidence | owner question |
| EVIDENCE_RECEIVED | Evidencia recibida, aún no necesariamente confirmada. | evidence_received | confirmar columnas o evaluar activación |
| CONFIRMATION_REQUIRED | Hay columnas ambiguas o no confirmadas. | column_confirmation_fields | pedir confirmación al dueño |
| ACTIVATION_EVALUATED | El evaluator devolvió estado de activación. | activation_status | bloquear, esperar autorización o preparar ejecución futura |
| PROCESSING_AUTHORIZED | Runtime autorizado explícitamente para una tool concreta. | runtime_authorized=true | ejecutar tool determinística |
| DELIVERY_READY | Hay output listo para entregar. | tool result / archivo | entregar owner-facing |
| CLOSED | Tarea cerrada. | entrega o bloqueo aceptado | no action |
| BLOCKED | No se puede avanzar sin decisión/evidencia/scope. | blocking_state | explicar bloqueo |

---

# 5. Transiciones permitidas

```text
LISTENING → TASK_CLASSIFIED
TASK_CLASSIFIED → EVIDENCE_REQUESTED
TASK_CLASSIFIED → EVIDENCE_RECEIVED
TASK_CLASSIFIED → BLOCKED
EVIDENCE_REQUESTED → EVIDENCE_RECEIVED
EVIDENCE_RECEIVED → CONFIRMATION_REQUIRED
EVIDENCE_RECEIVED → ACTIVATION_EVALUATED
CONFIRMATION_REQUIRED → EVIDENCE_RECEIVED
CONFIRMATION_REQUIRED → BLOCKED
ACTIVATION_EVALUATED → BLOCKED
ACTIVATION_EVALUATED → PROCESSING_AUTHORIZED
PROCESSING_AUTHORIZED → DELIVERY_READY
DELIVERY_READY → CLOSED
BLOCKED → EVIDENCE_REQUESTED
BLOCKED → CLOSED
```

---

# 6. Transiciones prohibidas

```text
LISTENING → PROCESSING_AUTHORIZED
LISTENING → DELIVERY_READY
TASK_CLASSIFIED → PROCESSING_AUTHORIZED sin evidencia mínima
EVIDENCE_REQUESTED → PROCESSING_AUTHORIZED
CONFIRMATION_REQUIRED → PROCESSING_AUTHORIZED
ACTIVATION_EVALUATED → DELIVERY_READY sin procesamiento autorizado
BLOCKED → PROCESSING_AUTHORIZED sin resolver bloqueo
```

---

# 7. Relación con TaskSpec

TaskSpec es el contrato de entrada de la FSM.

La FSM debe leer:

```text
task_type
service_depth
evidence_required
evidence_received
missing_evidence
column_confirmation_required
candidate_tool_ref
blocking_state
next_allowed_action
runtime_authorized
```

La FSM puede actualizar:

```text
blocking_state
next_allowed_action
notes
```

La FSM no debe alterar:

```text
owner_problem original
forbidden_claims
requested_claims
requested_formula_refs
```

---

# 8. Relación con First Aid Activation Evaluator

El evaluator decide si una herramienta First Aid es conceptualmente activable.

La FSM decide qué hacer con ese resultado.

```text
TaskSpec
→ activation_input
→ evaluate_first_aid_tool_activation(...)
→ activation_status
→ FSM transition
```

Regla:

```text
BLOCKED_RUNTIME_NOT_AUTHORIZED no es error.
Es el estado normal mientras no haya autorización explícita de runtime.
```

---

# 9. Relación con XLSX Delivery

XLSX delivery sólo puede ocurrir desde:

```text
PROCESSING_AUTHORIZED → DELIVERY_READY
```

Nunca desde:

```text
LISTENING
TASK_CLASSIFIED
EVIDENCE_REQUESTED
CONFIRMATION_REQUIRED
ACTIVATION_EVALUATED
BLOCKED
```

---

# 10. Relación con LLM Adapter

La IA puede ayudar en:

```text
redactar preguntas al dueño
clasificar intención inicial
explicar bloqueos
proponer ExcelSpec draft
redactar resumen owner-facing
```

La IA no puede:

```text
calcular resultados finales
conciliar definitivamente
autorizar runtime
generar XLSX opaco
resolver columnas ambiguas sin confirmación
emitir claims fiscales o contables definitivos
```

---

# 11. Eventos V1

```text
OWNER_MESSAGE_RECEIVED
FILE_RECEIVED
TASKSPEC_CREATED
TASK_CLASSIFIED
EVIDENCE_MISSING_DETECTED
EVIDENCE_RECEIVED
COLUMN_CONFIRMATION_REQUIRED
COLUMN_CONFIRMED_BY_OWNER
ACTIVATION_EVALUATED
RUNTIME_AUTHORIZATION_GRANTED
TOOL_PROCESSING_COMPLETED
DELIVERY_PREPARED
OWNER_DELIVERY_CONFIRMED
TASK_BLOCKED
TASK_CLOSED
```

---

# 12. Blocking states V1

```text
BLOCKED_MISSING_EVIDENCE
BLOCKED_COLUMN_CONFIRMATION
BLOCKED_RESTRICTED_FORMULA
BLOCKED_FORBIDDEN_CLAIM
BLOCKED_SCOPE_MISMATCH
BLOCKED_UNSUPPORTED_TASK_TYPE
BLOCKED_RUNTIME_NOT_AUTHORIZED
BLOCKED_NEEDS_HUMAN_DECISION
BLOCKED_TOOL_NOT_IMPLEMENTED
```

---

# 13. Invariantes

```text
No hay procesamiento sin TaskSpec.
No hay procesamiento sin evidencia mínima.
No hay procesamiento con columnas ambiguas.
No hay procesamiento si activation_status bloquea.
No hay runtime sin autorización explícita.
No hay delivery sin procesamiento autorizado.
No hay IA calculando resultados finales.
No hay claims definitivos sin evidencia suficiente.
```

---

# 14. Ejemplo First Aid precio/margen

```text
LISTENING
→ TASK_CLASSIFIED
→ EVIDENCE_REQUESTED
→ EVIDENCE_RECEIVED
→ ACTIVATION_EVALUATED
→ BLOCKED
```

Motivo del bloqueo:

```text
BLOCKED_RUNTIME_NOT_AUTHORIZED
```

Lectura:

```text
La herramienta puede estar conceptualmente lista, pero runtime sigue cerrado.
```

---

# 15. Próximo paso recomendado

```text
PYMIA_SERVICE_1_OPERATIONAL_FSM_CONTRACT_V1
```

Objetivo:

```text
Convertir esta FSM documental en contrato validable antes de implementar código.
```

Condición:

```text
Sin pipeline.
Sin XLSX.
Sin LLM adapter.
Sin chatbot.
Sin runtime productivo.
```

---

# 16. Veredicto

```text
PYMIA_SERVICE_1_OPERATIONAL_FSM_V1 = DRAFT_APPLIED
```

Condición:

```text
Documento de gobierno. No autoriza ejecución productiva.
```
