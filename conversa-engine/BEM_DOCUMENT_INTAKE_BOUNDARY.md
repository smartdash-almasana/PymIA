# Evidence intake boundary

## Decision

Not every document goes to BEM.
Every incoming evidence item must be triaged first.

## Rule

```text
conversa-engine recibe y registra.
EvidenceRouter decide ruta.
BEM estructura evidencia cuando corresponde.
INTERNAL_FACT procesa datos limpios localmente.
NARRATIVE procesa relato humano.
PymIA interpreta operacionalmente.
Hermes conversa y guía.
```

## Routes

```text
BEM_AI        -> extracción, curaduría y normalización externa
INTERNAL_FACT -> ingesta directa local para datos limpios
NARRATIVE     -> relato humano / anamnesis / memoria conversacional
```

## Routing matrix

```text
PDF / imagen
-> BEM_AI

.xlsx / .csv con entropía > 0.3
-> BEM_AI

.xlsx / .csv limpio, esquema esperado, columnas exactas
-> INTERNAL_FACT

human_claim / texto del dueño
-> NARRATIVE
```

## Correct flow

```text
Telegram / external channel
-> conversa-engine
-> RawInboundEvent
-> EvidenceTriage
-> route: BEM_AI | INTERNAL_FACT | NARRATIVE
-> structured evidence or anamnesis state
-> PymIA
-> pathology catalog contrast
-> simple operational report
-> user
```

## What BEM does

BEM may:

- read chaotic Excel / CSV / PDF / image / document
- detect tables and schemas
- extract rows, columns and variables
- preserve source references
- emit structured evidence
- emit confidence and quality signals

## What BEM must not do

BEM must not:

- diagnose
- confirm pathologies
- decide operational actions
- replace PymIA
- overwrite the pathology catalog

## What INTERNAL_FACT does

INTERNAL_FACT may process clean structured files when the schema is known and entropy is low.

Example:

```text
clean .xlsx -> local parser -> CuratedEvidenceRecord-like evidence -> PymIA/report
```

This route is local, controlled and fail-closed.

## Fail-closed behavior

If route cannot be decided:

```text
Evidencia recibida, pero no puedo decidir una ruta segura de procesamiento.
No voy a diagnosticar hasta resolver el tipo de evidencia.
```

If extraction is partial:

```text
Extraje evidencia parcial.
Puedo avanzar con alcance limitado.
Falta: <evidence_gaps>.
```
