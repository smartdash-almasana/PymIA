# Pre-TaskSpec Resolution — Plan Corregido PymIA (Contratos Fundacionales)

## Estado

```text
Tipo:        PRE_TASKSPEC_RESOLUTION
Estado:      APPROVED
Fecha:       2026-06-18
Origen:      Auditoría arquitectónica externa (PASS_WITH_NOTES, HIGH confidence)
Propósito:   Resolver 5 pre-condiciones antes de escribir TaskSpecs de contratos fundacionales
Auditorías:  Qwen (NEEDS_REORDER → aceptado), Gemini (PASS_WITH_NOTES → resuelto)
```

---

## Contexto

El plan corregido de 12 fases para contratos fundacionales PymIA fue auditado externamente.

Veredicto: `PASS_WITH_NOTES` con 5 pre-condiciones a resolver antes de TaskSpec.

Este documento resuelve las 5 pre-condiciones y se convierte en referencia obligatoria para los TaskSpecs de Fases 3, 4 y 7.

---

## PC-1: Relación EvidenceArtifact V1 ↔ EvidenceRecord ↔ StructuredEvidence

### Decisión: COEXISTENCIA CON ABSORCIÓN GRADUAL

Existen 3 modelos de evidencia:

| Modelo | Ubicación | Capa | Propósito |
|--------|-----------|------|-----------|
| `EvidenceRecord` | `pymia/smartpyme/evidence.py` | Operativa | Metadata de ingesta (qué archivo llegó, qué status tiene). No abre archivos. |
| `StructuredEvidence` | `pymia/contracts/evidence_v1.py` | Transporte | Payload de datos (tablas extraídas, variables computadas). |
| `EvidenceArtifact V1` | (propuesto) | Epistémica | Envelope de verdad (confianza, TTL, alcance métrico, estado epistémico). |

### Política

```text
EvidenceArtifact V1 NO reemplaza EvidenceRecord ni StructuredEvidence en V1.
EvidenceArtifact V1 REFERENCIA vía source_ref, no embebe payload.
EvidenceRecord y StructuredEvidence NO se modifican en este ciclo.
Absorción futura (V2+): evaluar si EvidenceRecord se fusiona con EvidenceArtifact.
```

### Relación concreta

```text
EvidenceArtifact V1 (envelope epistémico)
  └── source_ref → EvidenceRecord.evidence_id (metadata operativa)
                    o StructuredEvidence ref   (payload de datos)
```

### Regla de source_kind

`source_kind` existe en EvidenceRecord y en el plan de EvidenceArtifact V1. El TaskSpec de Fase 3 DEBE usar la misma enumeración base (`uploaded_file`, `manual_text`, `external_ref`, `generated`, `unknown`) o extenderla explícitamente con valores documentados.

---

## PC-2: Reconciliación de campos OCF — CONCEPT vs Plan

### Decisión: ESQUEMA RECONCILIADO DE 16 CAMPOS PARA V1

Campos del CONCEPT que se absorben con nombre diferente:

| CONCEPT | Plan (unificado) | Razón |
|---------|-------------------|-------|
| `company_taxonomy` | `business_taxonomy` | Alinea con `BusinessTaxonomy` existente en anamnesis.py |
| `organizational_variables` | `variables` | Más conciso; prefijo redundante en contexto OCF |
| `candidate_formulas` | `formula_candidates` | Consistente con `InvestigationRecord.formula_candidates` |
| `active_hypotheses` | `hypotheses` | Estado activo/descartado gobernado por EpistemicState, no por campo |
| `available_evidence` | `evidence_refs` | Refs a EvidenceArtifact IDs |
| `confirmed_findings` | `findings` | Estado confirmado gobernado por EpistemicState |

Campos del CONCEPT que se absorben en otro campo:

| CONCEPT | Absorbido en | Razón |
|---------|-------------|-------|
| `organizational_family` | `business_taxonomy` | Subdimensión de taxonomía |
| `discarded_hypotheses` | `hypotheses` | Cada hipótesis tiene EpistemicState (REJECTED) |
| `missing_evidence` | `open_unknowns` | Evidencia faltante es incógnita con tipo |

Campos del CONCEPT diferidos a V2:

```text
- operational_morphology      → requiere modelo de morfología no definido
- semantic_interpretations    → requiere motor de interpretación
- candidate_pathologies       → requiere PathologyPack enchufable
- calculation_results         → findings pueden contener resultados en V1
- interpretive_notes          → requiere motor de interpretación
```

Campos del Plan que se agregan (no estaban en CONCEPT):

```text
- service_depth               → nivel de servicio del caso
- entry_type                  → tipo de entrada del dueño
- sales_channels              → refs a SalesChannelTaxonomy
```

Campos del CONCEPT que se agregan (faltaban en el plan):

```text
- case_status                 → OPEN, IN_PROGRESS, BLOCKED, CLOSED
- version                     → versionado del schema
```

### Esquema OCF V1 reconciliado

```text
case_identity       → tenant_id, case_id, intake_id, created_at
case_status         → OPEN | IN_PROGRESS | BLOCKED | CLOSED
service_depth       → ref ServiceDepth V1
entry_type          → SOLVE_NOW | UNDERSTAND_PROBLEM | ORGANIZE_COMPANY
version             → "v1"
business_taxonomy   → ref BusinessTaxonomy + canales
sales_channels      → list[ref SalesChannelTaxonomy V1]
raw_inputs          → refs a archivos/mensajes recibidos
evidence_refs       → list[artifact_id de EvidenceArtifact V1]
variables           → dict[str, VariableEntry con EpistemicState]
hypotheses          → list[HypothesisEntry con EpistemicState]
formula_candidates  → list[formula_id]
findings            → list[FindingEntry con EpistemicState]
open_unknowns       → list[UnknownEntry]
next_questions      → list[str]
trace_refs          → list[run_id, investigation_id, etc.]
metadata            → dict[str, Any]
```

---

## PC-3: business_family_taxonomy_v1 — DIFERIDO

### Decisión: NO INCLUIR EN FASE 1

`BusinessTaxonomy` ya existe en `pymia/smartpyme/anamnesis.py` con campos funcionales. `SalesChannelTaxonomy V1` cubre la dimensión de canales que es la más urgente.

### Criterio de activación futuro

```text
Activar cuando:
- Se necesite distinguir familias empresariales para seleccionar fórmulas diferentes.
- O cuando OCF V1 en uso real muestre que BusinessTaxonomy de anamnesis.py es insuficiente.
```

---

## PC-4: Test de integración cross-contract — FASE 7.5 AGREGADA

### Decisión: AGREGAR COMMIT 7.5 ANTES DE FASE 8

```text
Commit:  test(pymia-live): add cross-contract smoke test
Archivo: tests/contracts/test_cross_contract_smoke.py
Tipo:    TEST_ONLY
```

### Tests requeridos

1. `test_evidence_artifact_feeds_ocf` — Crear EvidenceArtifact, crear OCF vacía, agregar referencia, marcar variable EMPTY → OBSERVED, verificar trazabilidad.
2. `test_microservice_result_patches_ocf` — Crear MicroserviceResult, aplicar case_file_patch a OCF, verificar variable + finding + next_question.
3. `test_epistemic_state_transitions` — Verificar cadena EMPTY → UNKNOWN → OBSERVED → STALE → OBSERVED.

### Orden de commits actualizado

```text
1.   docs(pymia-live): define product universe and service depth model
2.   feat(pymia-live): add sales channel taxonomy v1 contract
3.   feat(pymia-live): add evidence artifact v1 contract
4.   feat(pymia-live): add epistemic state v1 contract
5.   feat(pymia-live): add organizational case file v1 contract
6.   feat(pymia-live): add service depth v1 contract
7.   feat(pymia-live): add microservice result v1 contract
7.5  test(pymia-live): add cross-contract smoke test
8.   docs(pymia-live): define excel treatment lab concept
9.   feat(pymia-live): add excel treatment lab triage
10.  docs(pymia-live): define mercado libre audit plugin concept
11.  feat(pymia-live): add marketplace evidence v1 contract
12.  feat(pymia-live): add evidence reconciliation v1
```

---

## PC-5: Unificación EpistemicState — 10 ESTADOS CONFIRMADOS

### Decisión: 10 ESTADOS, NO 12

Los 10 estados del plan son correctos.

Los 3 estados adicionales del CONCEPT se resuelven así:

| Estado | Decisión | Razón |
|--------|----------|-------|
| `NEEDS_EVIDENCE` | Señal derivada, no estado | Describe acción requerida, no estado del conocimiento |
| `NEEDS_REFRESH` | Caso de `STALE` | STALE ya captura dato vencido; refresh es consecuencia |
| `INTERPRETED` | Diferido a V2 | Requiere motor de interpretación que no existe |

### Enumeración V1

```text
EMPTY       — Casillero nunca activado
UNKNOWN     — Se preguntó pero no se sabe
STALE       — Dato vencido por TTL
CONFLICTED  — Evidencias contradictorias
DECLARED    — Dicho por el dueño sin verificación
OBSERVED    — Visto por el sistema en fuente primaria
INFERRED    — Derivado por regla sin observación directa
CALCULATED  — Resultado de fórmula aplicada
CONFIRMED   — Verificado por cruce de evidencias
REJECTED    — Descartado explícitamente
```

### Regla de Null

```text
None ≠ EMPTY ≠ UNKNOWN
None → campo no existe en estructura (error de modelo)
EMPTY → casillero existe pero nunca fue activado
UNKNOWN → se preguntó y no se obtuvo respuesta (incógnita activa)
```

---

## Obligaciones para TaskSpecs

```text
Fase 3 TaskSpec DEBE incluir: PC-1 (RELATIONSHIP_TO_EXISTING con EvidenceRecord/StructuredEvidence)
Fase 3 TaskSpec DEBE incluir: PC-5 (10 estados, regla de Null)
Fase 4 TaskSpec DEBE incluir: PC-2 (reconciliación completa de campos, actualizar CONCEPT)
Fase 7 TaskSpec DEBE incluir: relación con DiagnosticReport existente
Fase 7.5 DEBE existir antes de Fase 8
Fase 9 TaskSpec DEBE exigir al menos 1 test con Excel real de prueba_excels/
```
