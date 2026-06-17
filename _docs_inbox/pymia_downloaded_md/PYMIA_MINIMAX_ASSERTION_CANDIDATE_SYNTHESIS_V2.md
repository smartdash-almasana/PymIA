# PymIA — AssertionCandidate V1: síntesis consolidada de Minimax

## Veredicto

La respuesta de Minimax es de alto valor arquitectónico.

Debe conservarse como insumo para documentar la capa base del kernel epistémico de PymIA V1.

No debe implementarse todavía sin una decisión posterior. Primero debe quedar como contrato conceptual reducido y auditado.

## Decisión central

La unidad atómica de salida diagnóstica en PymIA V1 debe ser:

```text
AssertionCandidate
```

Una `AssertionCandidate` no es diagnóstico final.

Es una propuesta computacional trazable que puede estar:

```text
lista
bloqueada
contradicha
stale
confirmada
ajustada
rechazada
```

El kernel propone. El operador confirma, ajusta o rechaza.

## Regla nuclear

```text
No hay diagnóstico sin AssertionCandidate.
No hay AssertionCandidate sin fórmula, evidencia, suficiencia, pack versionado y trazabilidad.
No hay afirmación final sin evento humano.
```

## Campos mínimos rescatables

```yaml
AssertionCandidate:
  candidate_id: string
  case_id: string
  statement: string
  formula_id: string
  pack_id: string
  pack_version: string
  kernel_version: string
  created_at: datetime
  last_evaluated_at: datetime

  proposed_value: optional
  proposed_value_type: numeric | boolean | categorical | range | set | null

  evidence_used: list[EvidenceRef]
  evidence_sufficiency: FULL | PARTIAL | INSUFFICIENT
  missing_evidence: list[EvidenceRequirement]
  contradicting_evidence: list[EvidenceRef]

  evaluation_trace: list[EvaluationStep]
  blocking_reason: optional string

  criticality: HIGH | MEDIUM | LOW
  confirmation_required: true
  confirmation: optional[OperatorConfirmation]
```

## Estados recomendados

Minimax acierta al eliminar `ASSERTED`.

Estados producidos por el kernel:

```text
CANDIDATE_READY
CANDIDATE_BLOCKED
CANDIDATE_CONTRADICTED
CANDIDATE_STALE
```

Estados producidos sólo por evento humano:

```text
CONFIRMED
ADJUSTED
REJECTED
```

Regla:

```text
El kernel nunca produce CONFIRMED, ADJUSTED ni REJECTED.
```

## Evidencia suficiente ≠ confirmación humana

La suficiencia responde:

```text
¿El sistema tiene evidencia suficiente para proponer?
```

La confirmación responde:

```text
¿El operador humano acepta, ajusta o rechaza la propuesta?
```

Por lo tanto:

```text
evidence_sufficiency = FULL
no equivale a
status = CONFIRMED
```

## Bloqueo

`CANDIDATE_BLOCKED` significa:

```text
la fórmula está identificada,
pero no pudo evaluar por falta de evidencia concreta.
```

Debe conservar:

```text
formula_id
missing_evidence
evaluation_trace
blocking_reason
criticality
```

Regla:

```text
Una candidate bloqueada no es basura.
Es la unidad de “qué sé que no sé”.
```

Esta unidad alimenta:

```text
dominant_unknown
minimum_evidence_path
```

## Contradicción

`CANDIDATE_CONTRADICTED` significa:

```text
hay evidencia suficiente para evaluar,
pero existe evidencia incompatible no reconciliada.
```

Debe conservar:

```text
evidence_used
contradicting_evidence
evaluation_trace
blocking_reason
```

Regla:

```text
Contradicción no es baja confianza.
Contradicción no es bloqueo.
Contradicción es estado propio.
```

## Pack versionado y STALE

Una candidate nace ligada a:

```text
pack_id
pack_version
formula_id
```

Si cambia el pack o cambia evidencia usada:

```text
la candidate pasa a CANDIDATE_STALE
no se reescribe silenciosamente
se re-evalúa creando nuevo estado/candidate
```

## Barreras contra LLM-as-decider

Minimax propone cuatro barreras correctas.

### 1. El LLM no tiene API de escritura

El LLM puede leer:

```text
status
proposed_value
evidence_used
missing_evidence
evaluation_trace
confirmation
```

Pero no puede modificar nada.

### 2. El LLM no combina candidates en diagnóstico

El LLM no debe decir:

```text
A + B implican diagnóstico C
```

Debe decir:

```text
Tengo estas candidates esperando confirmación.
```

La composición diagnóstica ocurre después de confirmación, no en el LLM.

### 3. Todo rendering debe referenciar candidates reales

Todo texto diagnóstico debe tener:

```text
render_of: list[candidate_id]
```

Texto sin candidate_id asociado no debe salir como diagnóstico.

### 4. El LLM no escribe confirmation

La confirmación sólo nace de eventos humanos:

```text
operator_confirmed
operator_adjusted
operator_rejected
```

El texto del LLM nunca equivale a confirmación.

## Eventos rescatables

### Kernel-triggered

```text
formula_evaluated(candidate_id, evidence_snapshot_ref)
re_evaluation_triggered(candidate_id, reason)
evidence_added(ev_id)
evidence_revised(ev_id)
evidence_removed(ev_id)
pack_reloaded(pack_kind, new_version)
system_recalled_candidate(candidate_id, reason)
```

### Human-triggered

```text
operator_confirmed(candidate_id, note?)
operator_adjusted(candidate_id, new_value, justification_note)
operator_rejected(candidate_id, reason)
operator_arbitrated_contradiction(candidate_id, chosen_value, justification_note)
```

## Regla de cierre

Una candidate sólo puede alimentar un `EpistemicState` final si cumple simultáneamente:

```text
1. status ∈ {CONFIRMED, ADJUSTED}
2. evidence_sufficiency = FULL
3. formula_id pertenece a un pack VALIDATED no deprecado
```

## Ajuste respecto de Minimax

Minimax permite alimentar diagnóstico con `PARTIAL` si hay nota.

Para PymIA V1 conviene ser más estricto:

```text
PARTIAL no alimenta diagnóstico final.
PARTIAL sólo puede alimentar working_hypothesis o recovery_question.
```

Motivo:

```text
evita confirmación humana como bypass de suficiencia.
```

## Riesgos detectados

### 1. confidence como score encubierto

`confidence: float` puede usarse mal.

Recomendación:

```text
No usar confidence como campo obligatorio en V1.
Preferir:
- evidence_sufficiency
- support_basis
- evaluation_trace
- evidence_quality
```

### 2. pathology_weight como diagnóstico encubierto

`pathology_weight` sólo debe ordenar desbloqueos.

No debe confirmar patologías.

### 3. auto-confirmables

Minimax deja abierta la puerta a auto-confirmación para hechos contables directos.

Para V1:

```text
confirmation_required = true para toda aserción diagnóstica relevante.
```

Los hechos contables pueden ser verificados, pero no diagnosticar automáticamente.

## Decisiones candidatas para repo

```text
1. AssertionCandidate es la unidad atómica de salida.
2. No existe ASSERTED antes del operador.
3. El kernel sólo produce CANDIDATE_*.
4. CONFIRMED / ADJUSTED / REJECTED sólo nacen de evento humano.
5. Evidencia suficiente no equivale a confirmación humana.
6. CANDIDATE_BLOCKED es salida útil.
7. CANDIDATE_CONTRADICTED es estado propio.
8. Cambio de pack o evidencia vuelve STALE la candidate.
9. EvaluationTrace es obligatorio.
10. LLM sólo lee/renderiza candidates, nunca las promueve.
11. Texto sin render_of:candidate_id no debe salir como diagnóstico.
12. PARTIAL no alimenta diagnóstico final en V1.
```

## Próximo frente lógico

Después de `EpistemicState` y `AssertionCandidate`, falta cerrar:

```text
OperatorConfirmation
```

Ahí debe definirse:

```text
qué evento humano confirma
qué evento ajusta
qué evento rechaza
qué validaciones corren antes
qué errores se emiten
cómo queda trazado
cómo se impide bypass del LLM
```
