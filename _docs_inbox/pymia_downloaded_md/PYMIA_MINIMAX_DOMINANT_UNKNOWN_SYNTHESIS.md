# PymIA — DominantUnknown y MinimumEvidencePath V1: síntesis útil de Minimax

## Veredicto

La quinta respuesta de Minimax es muy valiosa.

Cierra la capa que convierte el estado epistémico en una instrucción accionable para el operador:

```text
qué evidencia conviene pedir ahora
por qué conviene pedir esa evidencia
qué desbloquearía
qué tensiones resolvería
qué preguntas permitiría formular mejor
```

Esta pieza evita que PymIA quede como un diagnóstico estático.

Con `DominantUnknown` y `MinimumEvidencePath`, PymIA puede decir:

```text
esto sé
esto no sé
esto está bloqueado
y esta es la evidencia mínima que más destraba el caso
```

## Decisión central

La prioridad no debe ser un score.

Debe ser una estructura explicable compuesta por dimensiones separadas.

```text
prioridad ≠ puntaje
prioridad = impacto epistémico trazable
```

## Regla nuclear

```text
DominantUnknown no es el dato faltante más obvio.
Es la evidencia cuya obtención produce la mayor utilidad marginal para destrabar el caso.
```

## Cadena completa

```text
Owner speaks
  -> Operator captures
  -> OwnerSemanticClaim
  -> StructuredEvidence
  -> TensionReport
  -> AssertionCandidate
  -> DominantUnknown + MinimumEvidencePath
  -> OperatorConfirmation
  -> EpistemicState
```

## DominantUnknown

`DominantUnknown` representa la próxima evidencia más valiosa a conseguir.

Campos mínimos aprovechables:

```yaml
DominantUnknown:
  dominant_unknown_id: string
  case_id: string
  computed_at: datetime
  kernel_version: string
  evidence_requirement: EvidenceRequirement
  rank_position: 1

  expected_impact:
    would_unblock_candidates: list[CandidateRef]
    would_resolve_tensions: list[TensionRef]
    would_enable_questions: list[QuestionTemplateRef]
    would_affect_pathologies: list[PathologyRef]
    expected_state_transition: optional[CaseStatusTransition]

  priority_tuple:
    bcuw: float
    trw: float
    cwr: float
    rqu: float
    cc: float

  alternates: list[EvidenceRequirement]
  explanation: Explanation
  computation_trace: list[Step]
```

## MinimumEvidencePath

`MinimumEvidencePath` no es una lista plana.

Es una ruta ordenada con dependencias, fallbacks y rendimientos decrecientes.

Campos mínimos aprovechables:

```yaml
MinimumEvidencePath:
  path_id: string
  case_id: string
  computed_at: datetime
  kernel_version: string

  ordered_requirements: list[PathItem]
  diminishing_returns_curve: list[DiminishingReturnPoint]
  total_expected_impact: ImpactBreakdown
  would_close_case: bool
  computation_trace: list[Step]
```

Cada `PathItem` debe incluir:

```yaml
PathItem:
  position: int
  requirement: EvidenceRequirement
  priority_tuple: PriorityTuple
  expected_impact_at_this_step: ImpactBreakdown
  dependencies: list[PathItem_id]
  fallback_if_unobtainable: list[PathItem_id]
  rationale: Explanation
  touched_graphs: list[string]
  touched_pathologies: list[string]
```

## PriorityTuple

Minimax propone cinco dimensiones:

```text
bcuw = Blocked-Candidate Unblocking Weight
trw = Tension Resolution Weight
cwr = Criticality-Weighted Reach
rqu = Recovery Question Uplift
cc = Collection Cost
```

Lectura:

```text
bcuw: cuánto destraba candidates bloqueadas.
trw: cuánto ayuda a resolver tensiones dueño-datos.
cwr: cuántos caminos diagnósticos toca.
rqu: cuánto mejora las preguntas de recuperación.
cc: cuánto cuesta conseguirla.
```

## Ranking lexicográfico

Minimax propone ranking lexicográfico:

```text
(bcuw, trw, cwr, rqu, -cc)
```

Esto evita sumar dimensiones incompatibles.

Decisión aprovechable:

```text
No hay score compuesto.
No hay suma ponderada.
La primera dimensión que discrimina decide.
```

## Ajuste necesario

Aunque la tupla use floats, PymIA debe cuidar que no se conviertan en scoring opaco.

Recomendación:

```text
Los números internos pueden existir como soporte de ordenamiento.
La salida operator-facing debe mostrar impacto tipado:
- destraba N candidates;
- resuelve M tensiones;
- mejora K preguntas;
- toca X patologías;
- costo estimado bajo/medio/alto.
```

## Cómo evita scoring superficial

Reglas útiles:

```text
1. No hay un solo número.
2. El composite está prohibido.
3. Dominancia requiere margen.
4. El impacto se tipifica, no se vende como puntaje.
5. La recomputación es visible.
6. Los pesos vienen de packs validados.
7. Si la ruta es trivial, se dice que es trivial.
```

## Dominancia con margen

Minimax propone que una evidencia sólo sea dominante si supera al segundo lugar por un margen.

Decisión aprovechable:

```text
Si no hay margen suficiente, no hay DominantUnknown único.
Hay empate técnico.
```

Esto evita que el sistema finja precisión.

Estado útil:

```text
E_TIED_DOMINANCE
```

## Explicación al operador

La explicación debe ser estructurada primero y renderizada después.

Debe incluir:

```text
qué candidates destraba
qué tensiones resuelve
qué preguntas habilita
qué patologías toca
qué pasos siguió el cálculo
qué costo estimado tiene conseguirla
```

Patrón correcto:

```text
El siguiente paso priorizado es conseguir X.
Eso destrabaría N candidates, resolvería M tensiones y permitiría formular mejores preguntas sobre Y.
```

Patrones a evitar:

```text
esta es la clave del caso
esto es lo más urgente
esto es lo más importante
si sólo pudieras conseguir una cosa
```

Motivo:

```text
esos patrones sugieren autoridad o optimalidad global que el kernel no debe prometer.
```

## Tres grafos simultáneos

La ruta debe conectar tres grafos:

```text
A. Blocked AssertionCandidates
B. TensionReports
C. OwnerSemanticClaims
```

Esto es central.

PymIA no debe priorizar sólo por fórmula ni sólo por relato.

Debe mirar:

```text
qué bloquea cálculo
qué tensiona relato-datos
qué claims del dueño están activos
```

## Estados y errores útiles

### E_NO_BLOCKED_CANDIDATES

No hay nada relevante que priorizar.

Esto es éxito, no error.

```text
DominantUnknown = null
MinimumEvidencePath = []
```

### E_EVERYTHING_BLOCKED

Todo está bloqueado y ninguna evidencia discrimina.

El sistema no debe fingir ranking.

### E_TIED_DOMINANCE

Hay empate técnico.

El operador decide y se registra `operator_tiebreak_decision`.

### E_NO_LINKAGE

Hay candidates y tensiones, pero no hay puente claro con claims/evidencia.

Esto indica problema de asociación.

### E_INSUFFICIENT_PATHOLOGY_CATALOG

El catálogo no tiene pesos o linkage suficiente.

Priorización degradada.

### E_RECOMPUTATION_FAILED

Fallo de recomputación.

Debe conservarse el ranking previo marcado como stale.

### E_PATH_INCONSISTENT

Ruta inconsistente por dependencia circular o duplicados.

### E_EMPTY_CATALOG

Sin catálogo validado no se puede priorizar.

## Barreras contra LLM-as-prioritizer

El LLM no debe:

```text
crear DominantUnknown
crear MinimumEvidencePath
agregar evidencias al path
quitar evidencias del path
reordenar items
inventar dependencias
inventar fallbacks
usar lenguaje de score o urgencia no computada
```

Todo rendering debe referenciar:

```text
dominant_unknown_id
path_id
evidence_requirement_ids
candidate_ids
tension_ids
pathology_ids
```

## Decisiones candidatas para repo

```text
1. DominantUnknown es evidencia prioritaria por utilidad marginal, no por intuición.
2. MinimumEvidencePath es ruta secuenciada, no lista plana.
3. No existe score compuesto de prioridad.
4. Ranking lexicográfico evita sumar dimensiones incompatibles.
5. Dominance requiere margen; si no, se reporta empate.
6. La prioridad conecta blocked candidates, tensions y owner claims.
7. La explicación al operador debe ser estructurada y trazable.
8. LLM no crea ni reordena prioridad.
9. Si no se puede priorizar, el sistema debe decirlo.
10. La recomputación del path debe ser visible y auditable.
```

## Qué queda cerrado con esta quinta pieza

Con estas cinco piezas, PymIA V1 tiene una constitución conceptual del kernel epistémico:

```text
1. EpistemicState
2. AssertionCandidate
3. OperatorConfirmation
4. OwnerSemanticClaim + TensionReport
5. DominantUnknown + MinimumEvidencePath
```

## Próximo frente lógico

El próximo punto no debería ser otro contrato del kernel epistémico.

Ahora conviene consultar por:

```text
Pack Governance Minimal V1
```

Porque estas cinco piezas dependen de packs:

```text
FormulaPack
PathologyPack
EvidenceTypeCatalog
QuestionTemplatePack
SectorPack
```

Sin governance de packs, el kernel puede estar bien diseñado pero alimentado por conocimiento no confiable.

Pregunta rectora próxima:

```text
¿Qué condiciones mínimas debe cumplir un pack para poder participar en AssertionCandidate, TensionReport y DominantUnknown?
```
