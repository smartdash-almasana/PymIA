# P1 — Schema Initial Diagnosis

Estado: VIGENTE
Fecha: 2026-06-12
Frente: REENTRY_DIAGNOSTICO_INICIAL_Y_PRIMER_INFORME
Contrato previo: `docs/pymia/P1_INITIAL_DIAGNOSIS_CONTRACT.md`

## 1. Propósito

Definir el schema documental mínimo del artefacto `InitialDiagnosis`.

Este schema no implementa runtime, no crea tests, no abre delivery, no captura decisión del dueño y no autoriza owner-action.

Su función es fijar la estructura clínica-operacional del diagnóstico inicial entre:

```text
Ficha → Anamnesis → Evidencia → Comprensión → Contraste
```

y:

```text
Primer informe owner-facing
```

## 2. Principio rector

PymIA no parte de variables.

PymIA parte de comprender al dueño y a su organización.

Las variables del schema son campos de registro del proceso, no una lista universal previa para diagnosticar cualquier PyME.

## 3. Nombre del artefacto

```text
InitialDiagnosis
```

Nombre en español:

```text
Diagnóstico inicial
```

## 4. Estados permitidos

```text
NEEDS_ANAMNESIS
NEEDS_EVIDENCE
READY_FOR_INITIAL_DIAGNOSIS
INITIAL_DIAGNOSIS_DRAFTED
BLOCKED_BY_INSUFFICIENT_CONTEXT
```

Estados explícitamente prohibidos en este schema:

```text
READY_FOR_ACTION
APPROVED
REJECTED
DELIVERED
OWNER_DECISION_CAPTURED
```

## 5. Schema mínimo conceptual

```text
InitialDiagnosis
├─ diagnosis_id
├─ tenant_id
├─ case_id
├─ status
├─ owner_symptom
├─ business_context
├─ operational_focus
├─ evidence_summary
│  ├─ available_evidence
│  ├─ missing_evidence
│  └─ evidence_limitations
├─ emergent_variables
├─ initial_hypotheses
├─ contrast_summary
│  ├─ contrast_performed
│  ├─ contrast_basis
│  └─ contrast_result
├─ supported_findings
├─ limits_of_confidence
├─ next_question_or_evidence
├─ first_report_basis
└─ trace
   ├─ source_refs
   ├─ created_at
   └─ generated_by
```

## 6. Campos obligatorios

### 6.1 `diagnosis_id`

Identificador del diagnóstico inicial.

No representa diagnóstico final ni decisión.

### 6.2 `tenant_id`

Identidad técnica de aislamiento.

Debe existir para preservar scope multi-tenant.

### 6.3 `case_id`

Identificador del caso PyME observado.

Debe permitir continuidad entre ficha, anamnesis, evidencia, diagnóstico inicial y primer informe.

### 6.4 `status`

Estado del artefacto según la lista permitida.

Debe bloquear cualquier salida que pretenda diagnosticar sin anamnesis o evidencia suficiente.

### 6.5 `owner_symptom`

Registro fiel del dolor, síntoma o preocupación expresada por el dueño.

No debe traducirse prematuramente a patología.

### 6.6 `business_context`

Descripción mínima de la organización comprendida hasta el momento.

Debe reflejar tipo de PyME, actividad, dinámica operativa relevante y lenguaje del dueño cuando corresponda.

### 6.7 `operational_focus`

Foco operativo observado.

Ejemplos posibles: caja, ventas, costos, stock, cobranza, proveedores, rentabilidad, capacidad, dependencia comercial.

Estos focos no se imponen de antemano: emergen de anamnesis y evidencia.

### 6.8 `evidence_summary`

Resumen de evidencia recibida, evidencia faltante y limitaciones.

Debe impedir certeza falsa.

### 6.9 `emergent_variables`

Variables relevantes detectadas a partir del caso.

No son variables universales obligatorias.

Deben estar vinculadas a anamnesis, evidencia o contraste.

### 6.10 `initial_hypotheses`

Hipótesis iniciales, abiertas y contrastables.

No deben declararse como conclusión cerrada.

### 6.11 `contrast_summary`

Registro de qué se contrastó, con qué base y qué resultado preliminar produjo.

Puede referir a taxonomía, fórmula, regla operacional, evidencia documental o criterio clínico-operacional.

### 6.12 `supported_findings`

Hallazgos preliminares soportados por evidencia suficiente.

No deben incluir intuiciones no contrastadas como si fueran hechos.

### 6.13 `limits_of_confidence`

Límites explícitos de lo que no puede afirmarse todavía.

Campo obligatorio para evitar sobre-diagnóstico.

### 6.14 `next_question_or_evidence`

Pregunta o evidencia requerida para avanzar.

Debe orientar la profundización guiada.

### 6.15 `first_report_basis`

Parte del diagnóstico inicial que puede traducirse al dueño en primer informe.

No equivale al informe completo.

### 6.16 `trace`

Trazabilidad mínima del artefacto.

Debe incluir referencias a fuentes, fecha de creación y origen del registro.

## 7. Reglas de validez

Un `InitialDiagnosis` es válido sólo si:

1. tiene `tenant_id` y `case_id`;
2. conserva el síntoma del dueño;
3. registra contexto de negocio mínimo;
4. declara evidencia disponible y faltante;
5. declara límites de confianza;
6. no presenta variables como punto de partida;
7. no convierte hipótesis en conclusión;
8. no recomienda acción;
9. no registra aprobación o rechazo del dueño;
10. puede explicar qué habilita o bloquea el primer informe.

## 8. Reglas fail-closed

Debe bloquearse o quedar en estado no diagnóstico si:

- no hay ficha mínima;
- no hay anamnesis suficiente;
- no hay síntoma del dueño;
- no hay evidencia declarada o recibida;
- no hay contraste explícito;
- falta registrar evidencia faltante;
- falta registrar límites de confianza;
- se intenta saltar a acción, decisión, delivery u owner-action.

## 9. Relación con Primer informe

`InitialDiagnosis` alimenta el primer informe.

El primer informe debe usar `first_report_basis`, `supported_findings`, `limits_of_confidence` y `next_question_or_evidence` para producir una devolución clara al dueño.

El primer informe no debe agregar certeza que no exista en el diagnóstico inicial.

## 10. Relación con fórmulas y patologías

Fórmulas y patologías pueden aparecer sólo dentro de `contrast_summary` o `supported_findings`, cuando hay evidencia suficiente.

No deben aparecer como premisa universal previa al caso.

## 11. Fuera de alcance

Este schema no autoriza:

- runtime;
- tests;
- migraciones;
- owner-action;
- DecisionRecord;
- OD1;
- C4;
- delivery;
- reportes finales;
- UI;
- Telegram;
- PDF productivo.

## 12. Próximo paso lógico

Definir `P1_FIRST_REPORT_BOUNDARY`, la frontera mínima entre `InitialDiagnosis` y primer informe owner-facing.

## 13. Estado

CANDIDATO para revisión.
