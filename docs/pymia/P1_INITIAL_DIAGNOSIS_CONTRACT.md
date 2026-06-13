# P1 — Initial Diagnosis Contract

Estado: VIGENTE
Fecha: 2026-06-12
Frente: REENTRY_DIAGNOSTICO_INICIAL_Y_PRIMER_INFORME

## 1. Propósito

Definir el artefacto `Diagnóstico inicial` como frontera clínica-operacional entre la comprensión situada de una PyME y el primer informe owner-facing.

Este contrato evita la deriva hacia variables abstractas, fórmulas, patologías, decisiones, acciones o delivery antes de haber comprendido el caso.

## 2. Cadena lógica vigente

```text
Ficha
→ Anamnesis
→ Evidencia
→ Comprensión
→ Contraste
→ Diagnóstico inicial
→ Primer informe
```

## 3. Principio rector

PymIA no parte de variables.

PymIA parte de comprender al dueño y a su organización.

Las variables relevantes emergen de la anamnesis, la evidencia y el contraste situado.

Referencia de memoria:

```text
Pymia-memoria/PRINCIPIO_FUNDACIONAL_ANAMNESIS_ANTES_DE_VARIABLES_20260612.md
```

## 4. Qué es Diagnóstico inicial

El Diagnóstico inicial es una lectura fundada, limitada y trazable del caso PyME luego de ficha, anamnesis, evidencia y contraste preliminar.

No es diagnóstico final.

No es recomendación automática.

No es decisión del dueño.

No es aprobación de acción.

No es delivery comercial.

No es reporte final.

## 5. Entradas mínimas

El Diagnóstico inicial puede existir sólo si hay:

1. Ficha PyME mínima.
2. Dolor o síntoma expresado por el dueño.
3. Anamnesis suficiente para contextualizar la organización.
4. Evidencia disponible declarada o recibida.
5. Registro explícito de evidencia faltante.
6. Contraste preliminar contra taxonomía, fórmula, hipótesis o criterio operativo aplicable.

Si estas entradas no existen, el estado correcto no es diagnóstico sino `NEEDS_ANAMNESIS` o `NEEDS_EVIDENCE`.

## 6. Contenido mínimo del Diagnóstico inicial

El artefacto debe contener:

1. `owner_symptom`: qué dijo el dueño.
2. `business_context`: qué tipo de organización parece ser.
3. `operational_focus`: qué foco operativo se está observando.
4. `available_evidence`: qué evidencia existe.
5. `missing_evidence`: qué evidencia falta.
6. `emergent_variables`: variables relevantes que emergieron del caso, no variables impuestas.
7. `initial_hypotheses`: hipótesis abiertas y contrastables.
8. `contrast_performed`: qué se contrastó y con qué criterio.
9. `supported_findings`: hallazgos preliminares soportados por evidencia.
10. `limits_of_confidence`: qué no puede afirmarse todavía.
11. `next_question_or_evidence`: próxima pregunta o documento necesario.
12. `first_report_basis`: qué parte puede traducirse al dueño en primer informe.

## 7. Estados permitidos

```text
NEEDS_ANAMNESIS
NEEDS_EVIDENCE
READY_FOR_INITIAL_DIAGNOSIS
INITIAL_DIAGNOSIS_DRAFTED
BLOCKED_BY_INSUFFICIENT_CONTEXT
```

No se permite `READY_FOR_ACTION`, `APPROVED`, `REJECTED`, `DELIVERED` ni `OWNER_DECISION_CAPTURED` en este contrato.

## 8. Reglas de bloqueo

Bloquear diagnóstico inicial si:

- se intenta listar variables universales antes de anamnesis;
- se intenta calcular sin evidencia suficiente;
- se intenta declarar patología sin contraste;
- se intenta recomendar acción antes del primer informe;
- se intenta saltar a DecisionRecord, OD1, C4 o owner-action pipeline;
- se intenta convertir una intuición del dueño en verdad operacional sin evidencia.

## 9. Diferencia con Primer informe

Diagnóstico inicial:

```text
lectura técnica fundada del caso, con límites explícitos
```

Primer informe:

```text
devolución owner-facing clara, entendible y no inflada para el dueño
```

El primer informe traduce el diagnóstico inicial. No lo reemplaza.

## 10. Diferencia con variables, fórmulas y patologías

Variables:

```text
emergen del caso
```

Fórmulas:

```text
contrastan evidencia disponible
```

Patologías:

```text
clasifican síntomas o hallazgos cuando hay soporte suficiente
```

Ninguna de estas capas debe anteceder a la comprensión situada.

## 11. Próximo paso autorizado por este contrato

Definir el schema mínimo del artefacto `InitialDiagnosis` y su relación con el primer informe, sin implementar runtime, sin tests, sin owner-action, sin DecisionRecord y sin delivery.

## 12. Estado

CANDIDATO para revisión.
