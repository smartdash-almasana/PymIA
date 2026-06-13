# P1 — Reentry Checkpoint: Diagnóstico inicial y primer informe

Estado: VIGENTE
Fecha: 2026-06-12

## Objetivo

Cerrar el reencuadre documental del frente P1 y dejar explícito que el trabajo volvió al eje correcto:

```text
Ficha → Anamnesis → Evidencia → Comprensión → Contraste → Diagnóstico inicial → Primer informe
```

Este checkpoint existe para impedir que el desarrollo vuelva a derivar prematuramente hacia decisión, acción, delivery, OD1, C4 o owner-action pipeline.

## Motivo del reentry

Se detectó una deriva conceptual recurrente: saltar desde preguntas de diagnóstico hacia variables abstractas, fórmulas, patologías, reportes finales, aprobación/rechazo o decisiones del dueño.

La corrección fijada es:

```text
PymIA no parte de variables.
PymIA parte de comprender al dueño y a su organización.
```

Las variables, fórmulas, patologías e indicadores emergen después de anamnesis, evidencia y comprensión situada.

## Artefactos creados en P1

```text
docs/pymia/P1_INITIAL_DIAGNOSIS_CONTRACT.md
docs/pymia/P1_SCHEMA_INITIAL_DIAGNOSIS.md
docs/pymia/P1_FIRST_REPORT_BOUNDARY.md
docs/pymia/P1_FIRST_REPORT_SCHEMA.md
```

## Memoria operativa actualizada

```text
Pymia-memoria/PRINCIPIO_FUNDACIONAL_ANAMNESIS_ANTES_DE_VARIABLES_20260612.md
Pymia-memoria/_estado_actual.md
Pymia-memoria/_no_volver_a_hacer.md
```

## Frontera conceptual fijada

### InitialDiagnosis

Artefacto interno, estructurado y clínico-operacional.

Resume:

- síntoma expresado por el dueño;
- contexto mínimo de ficha/anamnesis;
- foco operativo;
- evidencia recibida;
- evidencia faltante;
- variables emergentes;
- hipótesis iniciales;
- contraste realizado;
- hallazgos soportados;
- límites de confianza;
- siguiente pregunta o evidencia;
- base para primer informe.

No recomienda acción.
No captura decisión.
No abre delivery.

### FirstReport

Artefacto owner-facing.

Traduce el InitialDiagnosis a lenguaje comprensible para el dueño.

Debe comunicar:

- qué se observó;
- qué evidencia lo sostiene;
- qué no puede afirmarse todavía;
- qué falta para profundizar;
- cuál es el próximo paso investigativo.

No es DecisionRecord.
No es approval/rejection.
No es plan de ejecución.
No es owner-action.

## Prohibiciones vigentes para este frente

Hasta cerrar P1, no abrir:

- OD1;
- C4;
- DecisionRecord;
- owner-action pipeline;
- delivery;
- approval/rejection;
- runtime;
- tests;
- Pydantic model;
- automatización;
- dashboard;
- PDF productivo.

## Estado de cierre

P1_REENTRY_CHECKPOINT deja asentado que el frente activo vuelve a ser:

```text
Diagnóstico inicial + primer informe
```

Y que el orden metodológico obligatorio es:

```text
Ficha
→ Anamnesis
→ Evidencia
→ Comprensión
→ Contraste
→ Diagnóstico inicial
→ Primer informe
```

## Próximo paso recomendado

Antes de implementar runtime o tests, revisar estos artefactos con auditoría externa y decidir si P1 pasa de CANDIDATO a VIGENTE o si requiere ajuste documental.
