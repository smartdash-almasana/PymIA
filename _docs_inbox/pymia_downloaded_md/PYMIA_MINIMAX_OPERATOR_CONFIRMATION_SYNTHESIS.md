# PymIA — OperatorConfirmation V1: síntesis útil de Minimax

## Veredicto

La respuesta de Minimax es muy sólida.

Cierra la tercera pieza de la capa epistémica base:

```text
EpistemicState
AssertionCandidate
OperatorConfirmation
```

Debe conservarse como insumo arquitectónico, no como implementación inmediata.

## Decisión central

`OperatorConfirmation` no debe ser un campo editable dentro de una candidate.

Debe ser un evento inmutable, append-only, emitido por un operador humano autorizado.

```text
La candidate propone.
La confirmation registra una decisión humana.
El EpistemicState referencia ambas por id.
```

## Regla nuclear

```text
El kernel puede producir candidates.
El operador puede confirmar, ajustar o rechazar.
El LLM no puede hacer ninguna de las dos cosas.
```

## Campos mínimos aprovechables

```yaml
OperatorConfirmation:
  confirmation_id: string
  candidate_id: string
  case_id: string
  issued_at: datetime

  operator_id: string
  operator_role: contador | asesor | consultor | auditor_interno
  operator_authority_level:
    - READ_ONLY
    - CONFIRM_ROUTINE
    - CONFIRM_CRITICAL
    - ARBITRATE_CONTRADICTION
  delegated_by: optional[string]

  action:
    - confirm
    - adjust
    - reject
    - arbitrate_contradiction
    - confirm_partial_with_caveat

  accepted_value: optional
  rejection_reason: optional[string]
  justification_note: optional[string]
  evidence_cited: list[EvidenceRef]
  external_context: optional[string]

  partial_with_caveat: bool
  client_visible: bool

  supersedes: optional[string]
  reverted_by: optional[string]

  kernel_version: string
  pack_version: string
  pack_state: VALIDATED | DEPRECATED | RECALLED | UNKNOWN
  evidence_snapshot_ref: string
  channel: UI | CLI | API
```

## Confirmar, ajustar y rechazar

### Confirmar

```text
confirm = el operador acepta el proposed_value tal como está.
```

Reglas:

```text
accepted_value == proposed_value
candidate debe estar CANDIDATE_READY
evidence_sufficiency debe ser FULL para diagnóstico final
```

Resultado:

```text
CONFIRMED
```

### Ajustar

```text
adjust = el operador acepta la candidate, pero no el valor exacto propuesto.
```

Reglas:

```text
accepted_value != proposed_value
justification_note obligatoria
proposed_value original no se reescribe
```

Resultado:

```text
ADJUSTED
```

### Rechazar

```text
reject = el operador rechaza la candidate.
```

Reglas:

```text
rejection_reason obligatoria
la candidate no alimenta ningún diagnóstico
```

Resultado:

```text
REJECTED
```

### Arbitrar contradicción

```text
arbitrate_contradiction = el operador elige un lado ante evidencia contradictoria.
```

Reglas:

```text
requiere authority ARBITRATE_CONTRADICTION
justification_note obligatoria
resultado debe ser ADJUSTED, no CONFIRMED
```

Motivo:

```text
el valor final no salió puramente de la fórmula,
sino de arbitraje humano documentado.
```

## Suficiencia parcial

Minimax propone `confirm_partial_with_caveat`.

Para PymIA V1, el ajuste correcto es:

```text
PARTIAL no alimenta final_diagnosis.
PARTIAL sólo alimenta working_hypothesis o recovery_question.
```

Esto evita que la confirmación humana se convierta en bypass de suficiencia.

Regla recomendada:

```text
confirm_partial_with_caveat puede existir,
pero su salida queda excluida del diagnóstico final.
```

## Validaciones previas obligatorias

Antes de aceptar una confirmación:

```text
1. candidate_id existe.
2. candidate está viva.
3. candidate está en estado confirmable.
4. operador tiene autoridad suficiente.
5. acción y valor son consistentes.
6. justificación obligatoria está presente si aplica.
7. pack_version sigue VALIDATED.
8. caso no está terminal.
9. operador está vinculado al caso o delegado.
```

Si una validación falla:

```text
no se confirma parcialmente
no se emite warning y se continúa
se rechaza todo el evento
se registra confirmation_rejected
```

## Errores nominales útiles

Estos códigos son valiosos porque vuelven auditable el rechazo:

```text
E_BLOCKED_CANNOT_CONFIRM
E_CONTRADICTED_USE_ARBITRATE
E_STALE_REEVALUATE_FIRST
E_PARTIAL_REQUIRES_CAVEAT
E_ALREADY_RESOLVED
E_PACK_INVALIDATED
E_AUTHORITY_INSUFFICIENT
E_VALUE_INCONSISTENT
E_JUSTIFICATION_MISSING
E_CASE_FINALIZED
E_NOT_DELEGATED
```

Decisión:

```text
Los errores de confirmación deben ser eventos auditables, no simples excepciones invisibles.
```

## Barreras contra LLM-as-decider

Minimax acierta: las barreras no deben vivir en prompt.

Deben estar en diseño.

### 1. El LLM no emite OperatorConfirmation

No debe existir endpoint, comando o canal por el cual el LLM pueda generar:

```text
operator_confirmed
operator_adjusted
operator_rejected
```

### 2. El LLM sólo lee candidates

Puede leer estado filtrado.

No puede mutar:

```text
status
confirmation
accepted_value
rejection_reason
justification_note
```

### 3. Rendering trazable

Todo texto diagnóstico generado por LLM debe declarar:

```text
render_of: list[candidate_id]
```

Si el texto afirma confirmación sin `confirmation_id` válido:

```text
el rendering es inválido
no sale al reporte
```

### 4. No hay confirmación masiva silenciosa

No debe existir:

```text
confirmar todo
aceptar todas las candidates
bulk confirm silencioso
```

La fricción es deliberada.

## Trazabilidad

Toda confirmación debe ser append-only.

No se edita ni se borra.

Si se corrige:

```text
se emite un nuevo evento
supersedes apunta al evento previo
```

Esto permite reconstruir:

```text
qué vio el operador
qué decidió
con qué evidencia
con qué versión de pack
bajo qué autoridad
por qué ajustó o rechazó
```

## Conexión con EpistemicState

Una candidate puede alimentar `EpistemicState.final_diagnosis` sólo si:

```text
status ∈ {CONFIRMED, ADJUSTED}
evidence_sufficiency == FULL
existe OperatorConfirmation válida no superseded
pack_version sigue VALIDATED
candidate cumple el umbral de inclusión del caso
```

Una candidate puede alimentar `working_hypothesis` si:

```text
fue confirmada con caveat parcial
o fue una contradicción arbitrada
```

Una candidate puede alimentar `recovery_question` si:

```text
está CANDIDATE_BLOCKED
o está CANDIDATE_READY pero con suficiencia parcial
```

Una candidate no aparece si:

```text
está REJECTED
está CANDIDATE_STALE
```

## Cadena completa

```text
formula_evaluated
  -> AssertionCandidate

OperatorConfirmation
  -> CONFIRMED | ADJUSTED | REJECTED

EpistemicState
  -> referencia candidate_id + confirmation_id

LLM
  -> renderiza, pero no confirma ni decide
```

## Decisiones candidatas para repo

```text
1. OperatorConfirmation es evento inmutable, no campo editable.
2. Confirmar, ajustar y rechazar son acciones distintas.
3. Sólo operador humano autorizado puede emitir confirmación.
4. Toda confirmación requiere candidate viva y pack validado.
5. Candidate BLOCKED no puede confirmarse.
6. Candidate CONTRADICTED requiere arbitraje, no confirmación directa.
7. Candidate STALE requiere re-evaluación previa.
8. PARTIAL no alimenta final_diagnosis en V1.
9. Errores de confirmación son eventos auditables.
10. LLM no tiene API de escritura ni canal de confirmación.
11. Todo rendering diagnóstico debe referenciar candidate_id.
12. EpistemicState final referencia candidate_id y confirmation_id, no texto libre.
```

## Próximo frente lógico

Con estas tres piezas cerradas conceptualmente, el próximo punto útil no es más contrato abstracto.

El próximo punto debe ser la confrontación entre:

```text
OwnerSemanticClaim
StructuredEvidence
AssertionCandidate
```

Pregunta rectora:

```text
¿Cómo representar “vos me decís X, pero tus datos muestran Y” sin que el LLM invente ni juzgue?
```
