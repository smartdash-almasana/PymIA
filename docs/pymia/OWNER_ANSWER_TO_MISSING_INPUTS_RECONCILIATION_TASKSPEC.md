# OWNER_ANSWER_TO_MISSING_INPUTS_RECONCILIATION_TASKSPEC

Fecha: 2026-06-10
Estado: READY_FOR_AUDIT
Origen: `SIMULATED_PILOT_FRICTION_RECONCILIATION.md` / SPFR-004
Tipo: auditoría contractual de reentrada owner-answer

## 1. Problema

La simulación asistida certificó que la respuesta del dueño entra por `owner_answer_reentry`, pero el caso siguió `BLOCKED`.

Eso puede ser correcto o incorrecto según el tipo de faltante.

El sistema debe distinguir entre:

```text
faltantes estructurales
```

que requieren evidencia tabular o numérica, y:

```text
faltantes semánticos / de sentido operativo
```

que pueden resolverse con una respuesta narrativa del dueño.

## 2. Objetivo

Auditar y, si corresponde, formalizar la relación entre:

```text
owner_questions_bundle
→ owner answer
→ missing_inputs
→ delivery_status
→ owner_facing_report
```

La pregunta central es:

```text
¿la respuesta del dueño resuelve algún faltante,
o sólo queda adjuntada sin efecto sobre el bloqueo?
```

## 3. Alcance autorizado

Auditoría documental y técnica focal sobre:

```text
pymia/orchestration/graph.py
pymia/audit_result/core_delivery_bridge.py
pymia/smartpyme/owner_questions_builder.py
tests/orchestration/test_graph.py
tests/smartpyme/test_core_delivery_bridge_reentry.py
tests/smartpyme/test_owner_questions_builder.py
```

Si se requiere implementación, debe proponerse patch mínimo separado y explícito.

## 4. Fuera de alcance

No autorizado en este TaskSpec:

- Telegram;
- Hermes;
- ERP;
- PDF productivo;
- runtime externo;
- nuevas fórmulas;
- nuevos reportes;
- refactor amplio;
- cambios de arquitectura;
- bypass del gate de evidencia;
- convertir lenguaje natural en evidencia numérica inventada.

## 5. Taxonomía mínima de faltantes

La auditoría debe clasificar cada faltante owner-facing como una de estas categorías:

### STRUCTURAL_INPUT

Requiere dato estructurado, archivo, columna, número o evidencia verificable.

Ejemplos:

```text
ventas por producto
costos por producto
cantidades
precios
stock
plazos de cobro cuantificados
```

Una respuesta narrativa puede aportar contexto, pero no debe marcar el faltante como resuelto si falta el dato duro.

### OWNER_SEMANTIC_CLARIFICATION

Requiere sentido operativo del dueño.

Ejemplos:

```text
por qué subió un costo
qué producto considera principal
qué canal tiene descuento especial
qué cambio operativo ocurrió en el período
qué decisión comercial explica una variación
```

Una respuesta narrativa sí puede resolver este faltante si contesta directamente la pregunta.

### MIXED

Tiene componente estructural y semántico.

Ejemplo:

```text
El dueño explica que hubo descuentos mayoristas,
pero falta el monto o regla aplicada para recalcular margen.
```

Resultado esperado:

```text
partially_resolved_still_blocked
```

## 6. Estados de resolución esperados

La reentrada owner-answer debe poder producir, al menos conceptualmente, uno de estos estados:

### resolved_by_owner_answer

La respuesta del dueño resuelve un faltante semántico.

### still_blocked_requires_structured_evidence

La respuesta fue útil, pero no reemplaza evidencia estructurada.

### partially_resolved_still_blocked

La respuesta resolvió parte del sentido, pero sigue faltando evidencia o dato duro.

### not_applicable_to_missing_input

La respuesta no corresponde al faltante preguntado.

## 7. Criterios de auditoría

La auditoría debe responder:

1. ¿Dónde se conserva la respuesta del dueño?
2. ¿Dónde se vincula esa respuesta con una pregunta o missing input específico?
3. ¿Existe clasificación actual entre faltante estructural y semántico?
4. ¿Existe estado de resolución por pregunta/faltante?
5. ¿El reporte visible explica por qué sigue bloqueado?
6. ¿Se preserva trazabilidad sin inventar datos?
7. ¿El sistema distingue respuesta útil de evidencia suficiente?

## 8. Criterios PASS

El frente pasa si la auditoría demuestra que:

- las respuestas del dueño se vinculan con preguntas/faltantes específicos;
- los faltantes semánticos pueden quedar resueltos por owner answer;
- los faltantes estructurales siguen bloqueados correctamente;
- el reporte visible explica el bloqueo residual;
- hay tests o evidencia suficiente para evitar regresión.

## 9. Criterios PARTIAL

El frente queda PARTIAL si:

- la reentrada funciona y preserva respuestas;
- pero no clasifica faltantes;
- o no distingue resolved/partial/still_blocked;
- o no hay test focal suficiente.

## 10. Criterios BLOCKED

El frente queda BLOCKED si:

- no se puede identificar dónde se consume owner answer;
- la respuesta no se conserva;
- el flujo reejecuta adapter conversacional indebidamente;
- se intenta resolver faltantes estructurales inventando datos.

## 11. Patch mínimo permitido si auditoría confirma deuda

Sólo si la auditoría confirma deuda real, se permite proponer un patch mínimo para:

- agregar metadata de tipo de faltante;
- mapear owner answer a pregunta/faltante;
- registrar estado de resolución;
- mejorar explicación visible del bloqueo residual;
- agregar test focal.

No se permite:

- desbloquear el caso sin evidencia suficiente;
- inventar valores;
- cambiar fórmulas;
- ampliar runtime.

## 12. Salida esperada

Crear checkpoint:

```text
docs/pymia/OWNER_ANSWER_TO_MISSING_INPUTS_RECONCILIATION_CHECKPOINT.md
```

Debe incluir:

```text
VEREDICTO: PASS / PARTIAL / BLOCKED
ARCHIVOS LEÍDOS
EVIDENCIA OBSERVADA
CLASIFICACIÓN DE FALTANTES
DECISIÓN: patch necesario / no necesario
TESTS EJECUTADOS, si aplica
NO PUSH
```

## 13. Estado

```text
READY_FOR_AUDIT
```
