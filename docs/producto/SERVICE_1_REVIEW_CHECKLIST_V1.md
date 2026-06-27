# SERVICE_1_REVIEW_CHECKLIST_V1

## Estado

```text
OPERATIONAL_REVIEW_GATE
READY_FOR_ASSISTED_SERVICE_1_RUNS
RUNTIME_IMPACT: NONE
CODE_IMPACT: NONE
TEST_IMPACT: NONE
```

## Veredicto

```text
SERVICE_1_REVIEW_CHECKLIST_V1: READY
HUMAN_GATE_REQUIRED: YES
AUTONOMOUS_RUN_SIGNOFF_ALLOWED: NO
PRE_DELIVERY_QA_REPLACEMENT: NO
```

## Propósito

Definir el checklist de revisión humana por corrida/caso para Servicio 1.

Este checklist no reemplaza el QA de entrega final.

Su función es otra:

```text
detener una corrida antes de que el operador trate un resultado intermedio
como caso confiable, entregable o concluyente.
```

## Quick path

1. Confirmar que el caso fue aceptado bajo el protocolo XLSX-first.
2. Revisar alcance, evidencia, límites y advertencias visibles.
3. Decidir una sola salida segura: continuar, pedir evidencia, recortar o bloquear.

## Relación con otros artefactos

| Artefacto | Rol |
|---|---|
| `SERVICE_1_XLSX_ACCEPTANCE_AND_BLOCKING_PROTOCOL_V1` | Gate de entrada del archivo/caso |
| `SERVICE_1_REVIEW_CHECKLIST_V1` | Gate humano por corrida/caso |
| `SERVICE_1_QA_DELIVERY_CHECKLIST_V1` | Gate final antes de entregar al cliente |

## Cuándo usarlo

Usar este checklist cuando ya existe una corrida o revisión operativa de Servicio 1 con alguno de estos elementos:

```text
intake aceptado
salida owner-facing inicial
hallazgos visibles o diferencias visibles
faltantes de evidencia
preguntas al dueño o reentry
XLSX operativo de revisión
paquete operador parcial
```

No esperar a la entrega final.

## Qué decide este gate

Este checklist permite decidir sólo una de estas salidas:

| Decisión | Significado |
|---|---|
| `CONTINUE_WITH_HUMAN_REVIEW` | El caso puede seguir avanzando dentro del flujo asistido |
| `REQUEST_MISSING_EVIDENCE` | El caso necesita más evidencia antes de seguir |
| `REDUCE_SCOPE_AND_REVIEW_AGAIN` | El caso debe recortarse a una familia/período más chico |
| `BLOCK_CASE_UNTIL_RISK_RESOLVED` | Hay un riesgo o contradicción que impide seguir |

## Regla central

```text
Servicio 1 puede seguir avanzando sólo si el operador humano puede explicar
qué evidencia existe, qué no existe, qué se está mirando realmente
y por qué el caso no se está vendiendo como conclusión final.
```

## Checklist principal

```text
[ ] El caso fue aceptado bajo SERVICE_1_XLSX_ACCEPTANCE_AND_BLOCKING_PROTOCOL_V1.
[ ] El archivo/caso sigue dentro de una familia operativa compatible.
[ ] El período o recorte del caso es explícito.
[ ] El problema del dueño sigue siendo concreto y visible.
[ ] La evidencia declarada está separada de las inferencias.
[ ] Los faltantes de evidencia están visibles.
[ ] Las diferencias visibles están visibles.
[ ] No se inventó evidencia ni completó información sin fuente.
[ ] Las advertencias operativas están visibles.
[ ] El caso no se está comunicando como diagnóstico, auditoría o validación final.
[ ] La revisión humana sigue siendo obligatoria y explícita.
[ ] La próxima acción segura es una sola y está indicada.
```

## Revisión por dimensión

### 1. Intake y alcance

Confirmar:

```text
[ ] El intake fue ACCEPTED_FOR_XLSX_INTAKE o equivalente compatible.
[ ] El archivo principal sigue siendo el correcto para este caso.
[ ] El alcance no se expandió silenciosamente.
[ ] El caso no mezcla múltiples frentes sin recorte.
[ ] El caso no cambió hacia una familia fuera de alcance.
```

Bloquear si aparece:

```text
SCOPE_DRIFT_DETECTED
MULTI_FRONT_CASE_WITHOUT_CUT
UNSUPPORTED_FAMILY_AFTER_INTAKE
```

### 2. Evidencia y límites

Confirmar:

```text
[ ] La evidencia recibida está listada.
[ ] Los faltantes están listados.
[ ] Las inferencias están marcadas como inferencias.
[ ] Los campos ambiguos siguen marcados como ambiguos.
[ ] Los datos negativos, duplicados o ajustes siguen visibles como advertencia.
[ ] No se promovió evidencia declarada a evidencia validada.
```

Bloquear si aparece:

```text
EVIDENCE_INVENTED
EVIDENCE_PROMOTION_WITHOUT_AUTHORITY
UNDECLARED_AMBIGUITY
```

### 3. Mensaje owner-facing

Confirmar:

```text
[ ] El mensaje sigue siendo prudente.
[ ] El mensaje no promete exactitud.
[ ] El mensaje no promete diagnóstico final.
[ ] El mensaje no reemplaza al contador.
[ ] El mensaje dice o implica revisión humana.
[ ] El mensaje deja clara la próxima acción segura.
```

Bloquear si aparece:

```text
FORBIDDEN_CLAIM_VISIBLE
NO_NEXT_SAFE_ACTION
OWNER_MESSAGE_OVERSOLD
```

### 4. Estado operativo de la corrida

Confirmar:

```text
[ ] El operador puede explicar qué se hizo en esta corrida.
[ ] El operador puede explicar qué NO se hizo.
[ ] El operador puede explicar por qué el caso todavía no es final.
[ ] El operador puede explicar qué dato falta o qué duda queda abierta.
[ ] El operador puede decidir si seguir, pedir evidencia, recortar o bloquear.
```

Bloquear si aparece:

```text
OPERATOR_CANNOT_EXPLAIN_BOUNDARY
CASE_STATE_NOT_UNDERSTOOD
NO_HUMAN_OWNER_OF_DECISION
```

## Decisión de salida

### `CONTINUE_WITH_HUMAN_REVIEW`

Usar sólo si:

```text
alcance claro
evidencia e inferencia separadas
faltantes visibles
mensaje seguro
sin claims prohibidos
sin riesgo activo
```

### `REQUEST_MISSING_EVIDENCE`

Usar si:

```text
el caso puede seguir
pero falta evidencia concreta y pedible
```

### `REDUCE_SCOPE_AND_REVIEW_AGAIN`

Usar si:

```text
el caso excede Servicio 1
pero puede recortarse a una familia/período manejable
```

### `BLOCK_CASE_UNTIL_RISK_RESOLVED`

Usar si:

```text
hay riesgo de claims prohibidos
hay evidencia inventada
hay drift de alcance
hay expectativa de dictamen final
no hay dueño humano de la revisión
```

## Claims prohibidos en esta etapa

Deben seguir ausentes:

```text
auditado
certificado
validado fiscalmente
conciliado definitivamente
cerrado contablemente
resultado final
exactitud garantizada
reemplaza al contador
listo para presentación fiscal
```

## Señales obligatorias en esta etapa

Deben estar presentes cuando correspondan:

```text
borrador operativo
evidencia declarada
faltantes de evidencia
diferencias visibles
advertencias operativas
requiere revisión humana
próxima acción segura
```

## PASS / FAIL

### PASS

La corrida pasa este gate si:

```text
el operador entiende el caso
el alcance está controlado
la evidencia está separada de la inferencia
los límites están visibles
la próxima acción segura está indicada
no hay claims prohibidos
```

### FAIL

La corrida falla este gate si:

```text
el operador no puede explicar el caso
la evidencia fue promovida o inventada
el alcance derivó
el mensaje owner-facing está sobrevendido
no hay próxima acción segura
hay riesgo activo no resuelto
```

## Non-goals

Este checklist no autoriza:

```text
entrega final al cliente
aprobación contable/fiscal
autonomía de runtime
chatbot operativo
pipeline libre
XLSX final como dictamen
```

## Próximo paso correcto

```text
SERVICE_1_VALIDATION_CASE_CORPUS_V1
```

Porque después del gate humano por corrida, el siguiente faltante fuerte es validar el flujo sobre casos controlados y repetibles.
