# Pathology catalog contrast

## Missing layer fixed

The anamnesis/document/report loop must not jump directly from symptom to report.
It must explicitly contrast the observed symptom and evidence against the PyME pathology catalog.

## Rule

```text
Symptom is not pathology.
Pathology is not finding.
Finding requires evidence contrast.
```

## Operational flow

```text
1. Owner narrative
2. Anamnesis state
3. Candidate symptoms
4. Evidence requested / received
5. Pathology catalog contrast
6. Candidate pathologies ranked
7. Required variables by pathology
8. Available evidence mapped
9. Evidence gaps declared
10. Investigable hypothesis
11. Simple operational report
```

## Catalog contrast objective

Given a symptom such as:

```text
RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
```

The system must contrast against catalog entries such as:

```text
margen_erosionado
fuga_operativa
tension_de_caja
precios_atrasados
costos_no_trazados
caja_inconsistente
```

Each pathology candidate must declare:

```text
pathology_code
matched_symptoms
required_evidence
available_evidence
evidence_gaps
confidence
status
```

## Status values

```text
CANDIDATE
SUPPORTED_PARTIAL
BLOCKED_MISSING_EVIDENCE
REJECTED_BY_EVIDENCE
CONFIRMED_FINDING
```

## Required invariant

No report may present a pathology as confirmed unless it passed evidence contrast.

Allowed wording before contrast:

```text
Hipótesis candidata: margen erosionado.
Evidencia requerida: ventas, costos, precios, caja.
```

Forbidden wording before contrast:

```text
Diagnóstico confirmado: margen erosionado.
```

## Minimal report behavior

If evidence is incomplete, the report must say:

```text
Con la evidencia actual, la hipótesis más plausible es X.
No está confirmada.
Para confirmarla o descartarla falta Y.
La acción inmediata es obtener Z.
```

## Relationship with PymIA

PymIA currently produces initial symptoms, hypotheses and required evidence.
`conversa-engine` must preserve that output and add an explicit catalog-contrast stage before any final report.

## Relationship with Hermes

Hermes may guide the conversation and request missing evidence.
Hermes must not confirm a pathology by language generation alone.
