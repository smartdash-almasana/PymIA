# PymIA — OwnerSemanticClaim V1: síntesis útil de Minimax

## Veredicto

La cuarta respuesta de Minimax es altamente valiosa.

Cierra una pieza crítica de PymIA V1:

```text
OwnerSemanticClaim
StructuredEvidence
TensionReport
AssertionCandidate
OperatorConfirmation
EpistemicState
```

La idea central queda bien formulada:

```text
El sistema no confronta al dueño desde autoridad de IA.
Lo confronta desde sus propios datos.
```

## Decisión central

El dueño no es “paciente” ni “sujeto evaluado”.

El dueño es un par epistémico:

```text
aporta semántica
aporta intuición situada
aporta contexto no estructurado
aporta hipótesis vivida sobre su negocio
```

Los datos crudos aportan resistencia:

```text
ventas
costos
caja
deuda
stock
cobranzas
pagos
márgenes
plazos
```

PymIA no debe elegir una voz contra la otra. Debe exponer tensión trazable.

## Frase rectora

```text
Vos me decís esto, pero tus datos dicen esto otro.
```

Versión operator-facing:

```text
El relato del dueño no coincide completamente con la evidencia estructurada disponible.
```

Versión owner-facing recomendada:

```text
Vos me contás X. En los datos aparece Y. ¿Cómo lo leemos juntos?
```

## Regla nuclear

```text
El dueño aporta semántica.
Los datos aportan resistencia.
El kernel calcula tensión.
El operador arbitra.
El LLM traduce.
```

## OwnerSemanticClaim

`OwnerSemanticClaim` no es un hecho.

Es una posición declarada del dueño sobre su propio negocio, registrada con contexto.

Campos mínimos rescatables:

```yaml
OwnerSemanticClaim:
  claim_id: string
  case_id: string
  issued_at: datetime
  captured_by: operator_id
  capture_context:
    - in_person
    - phone
    - whatsapp
    - email
    - written_form

  verbatim_transcript: optional[string]
  paraphrase: string
  subject_tags: list[string]
  polarity:
    - positive
    - negative
    - neutral
    - ambivalent
    - mixed
  magnitude:
    - low
    - medium
    - high
    - null
  temporality:
    - past
    - present
    - near_future
    - far_future
    - timeless

  propositions: list[OwnerProposition]
```

## OwnerProposition

Un claim amplio debe descomponerse en subclaims testeables.

Campos mínimos:

```yaml
OwnerProposition:
  proposition_id: string
  proposition_text: string
  claim_type:
    - qualitative
    - quantitative
    - comparative
    - causal
    - prospective
  claimed_value: optional
  claimed_range: optional
  time_window: optional
  owner_certainty:
    - certain
    - mostly_sure
    - unsure
    - confused
  owner_awareness_of_evidence: optional[string]
```

## Linkage con evidencia

El vínculo claim→evidencia no debe ser inventado por el LLM.

Debe venir de:

```text
operador
catálogo de patologías
evidencia citada por el dueño
```

Estados útiles:

```text
LINKED_TESTABLE
LINKED_BUT_INSUFFICIENT
NON_TESTABLE
OWNER_CITED
```

Regla:

```text
Un OwnerProposition sin linkage testeable no genera TensionReport.
```

Eso no invalida el relato del dueño.

Sólo significa:

```text
no podemos confrontar este claim con la evidencia actual
```

## TensionReport

La tensión debe ser computada, no narrada libremente.

Campos mínimos:

```yaml
TensionReport:
  tension_id: string
  owner_proposition_id: string
  testable_state:
    - LINKED_TESTABLE
    - LINKED_BUT_INSUFFICIENT
    - OWNER_CITED
  tension_status:
    - aligned
    - tension
    - contradiction
    - non_testable
    - none
  owner_position:
    proposition_text: string
    claimed_value: optional
    claimed_range: optional
    polarity: string
  evidence_position:
    formula_id: string
    value: optional
    evidence_used: list[EvidenceRef]
    time_window: optional
  gap_summary: optional[string]
  gap_severity:
    - low
    - medium
    - high
    - null
  evaluation_trace: list[EvaluationStep]
```

## Estados de tensión

```text
aligned = relato y datos coinciden dentro de tolerancia.
tension = hay diferencia relevante, pero no máxima o con evidencia limitada.
contradiction = diferencia fuerte, evidencia robusta, fuentes suficientes.
non_testable = no hay forma actual de confrontar.
none = no aplica o no genera gap.
```

## Lo que TensionReport NO es

```text
no es veredicto
no es juicio
no es recomendación
no es causa psicológica
no es autoridad sobre el dueño
```

Es:

```text
un delta observado entre relato y evidencia estructurada
```

## Barreras contra LLM-as-detector

El LLM no debe crear ni modificar `TensionReport`.

Barreras rescatables:

```text
1. El LLM no tiene API para crear TensionReport.
2. El LLM no puede inflar aligned→tension ni tension→contradiction.
3. El LLM no puede extender gap_summary con información nueva.
4. Todo rendering debe referenciar claim_id, tension_id y candidate_id.
```

Regla:

```text
El LLM puede reformular una tensión ya computada.
No puede descubrirla, inflarla ni dramatizarla.
```

## Rendering permitido

Patrón owner-facing seguro:

```text
Lo que me contaste: X.
Lo que muestran los datos del período Y: Z.
¿Cómo lo leemos juntos?
```

Otro patrón:

```text
Por lo que dijiste, X.
En el Excel/resumen/cierre del período Y, el indicador Z muestra W.
```

## Rendering prohibido

```text
Estás equivocado.
No estás viendo bien tu negocio.
Tenés un problema de X.
Deberías preocuparte.
Hay algo que no cierra.
```

También quedan prohibidas palabras owner-facing como:

```text
error
equivocado
mal
incorrecto
preocupante
riesgoso
```

cuando se usan como juicio contra el dueño.

## Disciplina retórica

La tensión se reporta, no se adjudica.

El dueño conserva lugar interpretativo.

La pregunta final vuelve al humano:

```text
¿Cómo lo leemos?
¿Qué pensás?
¿Pasó algo que explique la diferencia?
```

## Conexión con AssertionCandidate

Un `TensionReport` puede producir una `AssertionCandidate` evidencial:

```text
Owner claim dice X.
StructuredEvidence muestra Y.
Formula evalúa Z.
El kernel genera candidate basada en evidencia.
```

Pero la candidate no es final.

Debe pasar por:

```text
OperatorConfirmation
```

## OwnerClaimResolution

Minimax agrega una pieza útil: el dueño puede responder a la tensión.

Eventos posibles:

```text
OWNER_STANDS_BY
OWNER_REFINES
OWNER_RETRACTS
OWNER_ACKNOWLEDGES_GAP
```

Esto es importante porque el dueño no queda fuera del sistema después de hablar.

Puede:

```text
mantener su relato
refinarlo
retirarlo
reconocer el gap
aportar contexto nuevo
```

## Cadena completa

```text
Owner speaks
  -> Operator captures
  -> OwnerSemanticClaim
  -> StructuredEvidence linked
  -> TensionReport computed by kernel
  -> AssertionCandidate
  -> OwnerClaimResolution optional
  -> OperatorConfirmation
  -> EpistemicState
```

## Decisiones candidatas para repo

```text
1. OwnerSemanticClaim es input epistémico, no evidencia cruda.
2. El claim del dueño no se invalida automáticamente por datos.
3. La tensión owner-vs-data debe ser computada como TensionReport.
4. El LLM no crea ni escala tensión.
5. Claim sin linkage testeable queda NON_TESTABLE, no rechazado.
6. El dueño puede responder a la tensión mediante OwnerClaimResolution.
7. TensionReport puede originar AssertionCandidate.
8. La confrontación owner-facing debe ser no acusatoria.
9. El texto final debe terminar abriendo interpretación humana.
10. El kernel no dice “estás equivocado”; expone delta.
```

## Ajustes recomendados

### 1. Cuidado con “confidence”

Minimax vuelve a usar `confidence`.

Para V1 conviene reemplazar por:

```text
evidence_quality
source_count
tolerance_band
evaluation_trace
```

### 2. Cuidado con `paraphrase` como campo canónico

Minimax propone que la paráfrasis del operador sea canónica.

Es útil, pero riesgoso.

Debe conservarse también:

```text
verbatim_transcript, cuando exista
```

Regla recomendada:

```text
paraphrase es operativa
verbatim es audit trail
```

### 3. No sobreactuar catálogo de patologías

El catálogo puede sugerir linkage.

Pero el operador debe aceptar o ajustar.

Regla:

```text
catálogo sugiere
operador valida el linkage
kernel verifica
```

### 4. OwnerClaimResolution no debe ser forzado

El dueño no siempre va a responder.

Si no hay resolución, el sistema puede dejar:

```text
owner_resolution = unresolved
```

sin bloquear necesariamente toda la evaluación.

## Próximo frente lógico

El próximo punto útil no es otro contrato largo.

Conviene consultar a Minimax sobre:

```text
DominantUnknown / MinimumEvidencePath
```

porque ya tenemos:

```text
qué afirma el dueño
qué dicen los datos
qué tensiona
qué candidate sale
quién confirma
```

Falta ordenar:

```text
qué se pregunta después
qué evidencia mínima desbloquea más valor
cómo priorizar sin scoring superficial
```
