# PymIA — Síntesis útil de Minimax sobre EpistemicState V1

## Veredicto

La respuesta de Minimax es útil y debe conservarse como insumo arquitectónico.

No debe convertirse todavía en implementación. Debe quedar como base conceptual para una futura decisión o contrato reducido sobre `EpistemicState`.

## Aportes fuertes

### 1. EpistemicState como snapshot firmable

Minimax propone que `EpistemicState` sea un snapshot, no un objeto mutable.

Esto es correcto para PymIA porque preserva trazabilidad:

- cada evaluación genera un nuevo estado;
- el estado no se muta silenciosamente;
- la historia vive en transiciones/eventos;
- permite auditoría posterior.

Decisión aprovechable:

```text
EpistemicState = snapshot evaluativo versionado
StateTransition = historia append-only
```

### 2. Toda afirmación debe pasar por Proposition

Minimax acierta al impedir afirmaciones sueltas.

En PymIA, ninguna salida diagnóstica debería existir sin una unidad evaluable detrás.

Decisión aprovechable:

```text
No hay afirmaciones libres.
Toda afirmación debe tener proposition_id, fórmula, evidencia, estado y trazabilidad.
```

### 3. Confirmación humana como campo estructural

Muy fuerte.

La confirmación del operador no debe ser un comentario decorativo ni una nota informal.

Debe ser parte del estado auditable:

```text
confirmation = pending | confirmed | rejected | adjusted
```

Esto sostiene la regla:

```text
assertion_candidate ≠ diagnóstico final
```

### 4. Eventos como disparadores

Correcto: el kernel no debería cambiar estado “porque sí”.

La transición debe ocurrir por eventos observables:

- evidence_added;
- evidence_revised;
- pack_loaded;
- evaluation_requested;
- operator_confirmed;
- operator_rejected;
- operator_adjusted.

Decisión aprovechable:

```text
Los cambios de estado deben ser event-driven.
No debe haber mutación directa opaca.
```

### 5. DominantUnknown como EvidenceRequirement priorizada

Minimax define bien la incógnita dominante:

```text
la evidencia que desbloquea más propositions ponderadas por importancia
```

Esto coincide con la dirección de PymIA:

```text
PymIA no sólo dice qué falta.
PymIA dice qué falta primero y por qué.
```

### 6. Diferencia entre BLOCKED y CONTRADICTED

Muy útil.

PymIA necesita distinguir:

```text
BLOCKED = no puedo calcular por falta de evidencia
CONTRADICTED = hay evidencia que tensiona o niega la proposición
```

Esto evita diagnósticos falsos y mejora la conversación con el operador.

### 7. Pack no validado bloquea evaluación

Minimax fijó una regla correcta:

```text
Si un pack no está validado, no participa en diagnóstico asistido.
```

Esto protege la arquitectura de conocimiento enchufable.

## Puntos que conviene ajustar

### 1. “ASSERTED” puede ser demasiado fuerte

Para PymIA V1, `ASSERTED` puede sonar demasiado definitivo.

Alternativa más segura:

```text
SUPPORTED_CANDIDATE
```

o:

```text
EVIDENCE_SUPPORTED
```

La salida debería evitar transmitir certeza antes de confirmación humana.

### 2. `confidence: float` puede abrir deriva probabilística

El campo `confidence` puede ser útil, pero también puede derivar hacia scoring encubierto.

Para V1 conviene reemplazar o acompañar con:

```text
support_basis
sufficiency_status
evidence_quality
```

Antes que confiar en un número 0.0–1.0.

### 3. `pathology_weight` debe venir del pack, pero con governance

La idea es buena, pero peligrosa si se usa como score diagnóstico.

Debe limitarse a priorización epistémica:

```text
sirve para ordenar incógnitas
no sirve para diagnosticar automáticamente
```

### 4. “SUFFICIENT” no debe sonar a diagnóstico cerrado

`SUFFICIENT` debe significar:

```text
hay evidencia suficiente para proponer aserciones candidatas
```

No:

```text
el diagnóstico ya está terminado
```

### 5. `operator_notes` no debe contaminar el estado

La nota libre del operador puede existir, pero debe quedar claramente fuera de la base diagnóstica formal.

Debe ser:

```text
comentario auxiliar
no evidencia
no fórmula
no confirmación
```

## Decisiones candidatas para documentar

Estas son las decisiones que conviene llevar luego al repo:

```text
1. EpistemicState es snapshot evaluativo, no objeto mutable.
2. Toda salida debe estar respaldada por Proposition.
3. La historia vive en StateTransition append-only.
4. La confirmación humana es parte estructural del estado.
5. AssertionCandidate no equivale a diagnóstico final.
6. Blocked y Contradicted deben separarse.
7. DominantUnknown prioriza evidencia, no diagnostica.
8. Pack no validado bloquea evaluación.
9. LLM sólo traduce estado filtrado, no modifica estado.
10. Scores y forecasts quedan fuera de V1.
```

## Próximo frente recomendado para consultar a Minimax

La próxima pregunta no debería abrir otro universo.

Debe profundizar sólo en `Proposition / AssertionCandidate`, porque es la unidad atómica de la salida epistémica.

Sin esa unidad bien cerrada, `EpistemicState` queda demasiado abstracto.
