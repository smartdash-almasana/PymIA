# P1 — Initial Diagnosis / First Report Audit Checkpoint

Estado: PASS_WITH_OBSERVATIONS
Fecha: 2026-06-12

## Frente auditado

P1 reencuadra el frente actual sobre la cadena:

```text
Ficha
→ Anamnesis
→ Evidencia
→ Comprensión
→ Contraste
→ Diagnóstico inicial
→ Primer informe
```

El objetivo de P1 es impedir la deriva hacia variables abstractas, fórmulas prematuras, patologías sin contraste, decisiones del dueño, owner-action, delivery o runtime antes de consolidar la frontera conceptual del diagnóstico inicial y primer informe.

## Archivos auditados

```text
docs/pymia/P1_INITIAL_DIAGNOSIS_CONTRACT.md
docs/pymia/P1_SCHEMA_INITIAL_DIAGNOSIS.md
docs/pymia/P1_FIRST_REPORT_BOUNDARY.md
docs/pymia/P1_FIRST_REPORT_SCHEMA.md
docs/pymia/P1_REENTRY_CHECKPOINT.md
```

## Veredicto

```text
PASS_WITH_OBSERVATIONS
```

P1 es conceptualmente consistente y respeta la secuencia clínica-operacional recuperada.

No se detectó apertura efectiva de:

```text
runtime
tests
Pydantic model
DecisionRecord
OD1
C4
owner-action
delivery
approval/rejection
PDF productivo
```

## Principio rector validado

```text
PymIA no parte de variables.
PymIA parte de comprender al dueño y a su organización.
```

Las variables relevantes emergen de:

```text
anamnesis
evidencia
comprensión situada
contraste posterior
```

No deben imponerse como lista universal previa.

## Frontera validada

```text
InitialDiagnosis = lectura clínica-operacional interna, estructurada, limitada y trazable.
FirstReport      = devolución owner-facing comprensible, fundada y no ejecutiva.
```

El primer informe traduce el diagnóstico inicial al dueño. No amplía autoridad, no recomienda acción ejecutiva, no registra decisión y no abre delivery.

## Reglas confirmadas

- No diagnosticar en primer contacto.
- No saltar de síntoma a fórmula.
- No saltar de anamnesis a variables universales.
- No convertir hipótesis en conclusión.
- No convertir evidencia incompleta en hallazgo fuerte.
- No convertir FirstReport en DecisionRecord.
- No abrir OD1/C4 desde P1.
- No implementar Pydantic/runtime/tests antes de auditoría externa o promoción formal.

## Observaciones

### Observación 1 — Estado CANDIDATO

Los documentos P1 deben mantenerse en estado CANDIDATO hasta revisión externa o decisión formal de promoción.

### Observación 2 — No mezclar con OD1/C4

P1 no debe commitearse junto con documentos OD1, C4, ADR-022 no relacionados, infografías, Excel de prueba o artefactos comerciales.

Si se cierra P1 en Git, el alcance recomendado es sólo:

```text
docs/pymia/P1_*.md
```

### Observación 3 — FirstReport debe vigilar la palabra “siguiente paso”

El siguiente paso permitido en FirstReport es investigativo o de evidencia.

No debe convertirse en:

```text
acción aprobada
recomendación ejecutiva
decisión del dueño
plan de delivery
```

## Riesgos de deriva cerrados

P1 reduce los siguientes riesgos:

```text
1. Saltar de síntoma a fórmula.
2. Saltar de anamnesis a variables universales.
3. Saltar de contraste preliminar a decisión.
4. Convertir owner-facing report en delivery.
5. Convertir hipótesis en conclusión.
6. Usar evidencia incompleta para afirmar rentabilidad, caja o patología.
7. Reabrir OD1/C4 antes de cerrar diagnóstico inicial y primer informe.
```

## Recomendación operativa

```text
Cerrar P1 documentalmente como CANDIDATO AUDITADO.
No implementar todavía.
Pedir auditoría externa.
Luego decidir si P1 pasa a VIGENTE o requiere corrección.
```

## Próximo frente recomendado

```text
P1_EXTERNAL_AUDIT_REQUEST
```

Alcance: prompt cerrado para auditoría externa sobre coherencia documental, sin autorizar nueva arquitectura ni implementación.
