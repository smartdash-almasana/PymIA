# P1 — FIRST REPORT BOUNDARY

Estado: VIGENTE
Fecha: 2026-06-12
Frente: Diagnóstico inicial y primer informe

## Propósito

Definir la frontera entre `InitialDiagnosis` y `FirstReport` dentro de la cadena:

```text
Ficha → Anamnesis → Evidencia → Comprensión → Contraste → Diagnóstico inicial → Primer informe
```

Este documento existe para impedir que el primer informe se convierta prematuramente en decisión, recomendación ejecutiva, aprobación, delivery o acción del dueño.

## Definición

`FirstReport` es la primera devolución owner-facing derivada de un `InitialDiagnosis`.

No es diagnóstico final.
No es plan de acción.
No es DecisionRecord.
No es aprobación/rechazo.
No es owner-action.
No es delivery operativo.

Su función es devolver al dueño una lectura comprensible, limitada y trazable de lo observado hasta ese momento.

## Entrada obligatoria

El primer informe sólo puede existir si existe un `InitialDiagnosis` previo.

Entrada mínima:

```text
InitialDiagnosis
├─ owner_symptom
├─ business_context
├─ operational_focus
├─ evidence_summary
├─ emergent_variables
├─ initial_hypotheses
├─ contrast_summary
├─ supported_findings
├─ limits_of_confidence
├─ next_question_or_evidence
└─ first_report_basis
```

Sin `InitialDiagnosis`, no hay `FirstReport`.

## Salida esperada

El `FirstReport` debe contener:

1. **Resumen del caso**
   - qué expresó el dueño;
   - qué tipo de organización se está comprendiendo;
   - cuál es el foco operativo inicial.

2. **Evidencia considerada**
   - qué documentos, datos o respuestas se usaron;
   - qué evidencia fue insuficiente o faltante.

3. **Variables emergentes**
   - sólo variables detectadas desde anamnesis/evidencia;
   - no listas universales impuestas.

4. **Lectura inicial**
   - qué parece estar ocurriendo;
   - qué hallazgos están soportados;
   - qué hipótesis quedan abiertas.

5. **Límites explícitos**
   - qué no se puede afirmar todavía;
   - qué requiere más evidencia;
   - qué no fue contrastado.

6. **Siguiente paso de profundización**
   - pregunta al dueño;
   - documento requerido;
   - dato faltante;
   - foco a contrastar.

## Prohibiciones

El `FirstReport` no debe:

- iniciar desde variables abstractas;
- declarar patologías sin contraste;
- calcular fórmulas sin evidencia suficiente;
- recomendar acciones ejecutivas;
- pedir aprobación del dueño;
- crear DecisionRecord;
- abrir OD1, C4, owner-action ni delivery;
- prometer solución;
- simular certeza diagnóstica final.

## Diferencia con InitialDiagnosis

```text
InitialDiagnosis = lectura clínica-operacional interna y estructurada.
FirstReport      = devolución comprensible al dueño.
```

El primer informe traduce el diagnóstico inicial, pero no amplía su autoridad.

No puede afirmar más que lo que el `InitialDiagnosis` soporta.

## Diferencia con acción del dueño

El primer informe puede formular una próxima pregunta o pedir evidencia adicional.

No puede convertir esa pregunta en acción aprobada.

La acción del dueño pertenece a frentes posteriores y sólo puede abrirse cuando la frontera de diagnóstico inicial y primer informe esté cerrada.

## Regla de suficiencia

Si la evidencia es insuficiente, el informe debe decirlo explícitamente.

Formato conceptual:

```text
Con la evidencia actual se puede observar X.
No se puede afirmar Y.
Para avanzar hace falta Z.
```

## Regla de lenguaje

El primer informe debe hablar en lenguaje comprensible para el dueño, sin perder trazabilidad.

Debe evitar:

- jerga innecesaria;
- exceso de abstracción;
- patologías como etiqueta prematura;
- fórmulas como autoridad retórica.

## Criterio de cierre

Este boundary queda satisfecho cuando exista claridad documental sobre:

- qué recibe el primer informe;
- qué puede decir;
- qué no puede decir;
- cómo se diferencia del diagnóstico inicial;
- cómo evita derivar hacia acción, decisión o delivery.

## Estado

CANDIDATO.

Siguiente paso sugerido:

```text
P1_FIRST_REPORT_SCHEMA
```
