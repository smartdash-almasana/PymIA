# RECONCILIATION_MATRIX — PymIA Downloaded MD Inbox

## Estado

```text
DOCUMENTARY_RECONCILIATION_DRAFT
NO_ARCHITECTURAL_AUTHORITY
NO_RUNTIME_AUTHORIZATION
NO_PYMIA_LIVE_AUTHORIZATION
NO_PROMOTION_YET
```

## Propósito

Clasificar los Markdown descargables importados en:

```text
_docs_inbox/pymia_downloaded_md/
```

contra la documentación viva del repo, antes de decidir si alguno debe promoverse a `docs/`.

## Fuentes vivas leídas

```text
AGENTS.md
_docs_inbox/pymia_downloaded_md/README.md
docs/pymia/FUNCTIONAL_GRAPH_PACK_MINIMAL_V1_CONTRACT.md
```

## Regla de autoridad

Según `AGENTS.md`, una conversación o documento externo no se convierte automáticamente en política, contrato o capacidad real.

Un documento sólo puede entrar al sistema vivo si pasa por:

```text
contract + test + evidence
```

Por lo tanto, todos los documentos del inbox son insumos, no fuente de verdad.

---

# Matriz de reconciliación

| Archivo | Tema | Clasificación | Prioridad | Motivo | Acción recomendada |
|---|---|---:|---:|---|---|
| `FICHAPRIMARIA_CONTRACT_V1.md` | FichaPrimaria / PrimaryCaseFile como boundary artifact | `PROMOTE_CANDIDATE_WITH_REDUCTION` | Alta | Define gobierno de caso, consentimiento, scope, operator binding e inmutabilidad. Es muy valioso pero demasiado amplio para promoción directa. | Reducir a contrato mínimo `PrimaryCaseFile V1` antes de docs vivos. No implementar completo. |
| `PYMIA_PRIMARY_CASE_FILE_FIRST_SLICE_GLM52.md` | Primer corte técnico mínimo de PrimaryCaseFile | `PROMOTE_CANDIDATE` | Alta | Baja FichaPrimaria a slice mínimo, evita tocar vertical_slice, motor, sufficiency y pipeline. Mejor candidato operativo que el contrato largo. | Promover como base de TaskSpec futuro tras auditoría documental. |
| `PYMIA_MINIMAX_FICHA_PRIMARIA_SYNTHESIS.md` | Síntesis conceptual de FichaPrimaria | `COMPLEMENTS` | Media-alta | Complementa FICHAPRIMARIA_CONTRACT_V1; útil para doctrina y decisiones, pero no como contrato ejecutable. | Usar como respaldo conceptual, no promover entero. |
| `PYMIA_MINIMAX_EPISTEMIC_STATE_SYNTHESIS.md` | EpistemicState V1 | `DEFER_AS_ARCHITECTURAL_INPUT` | Media | Útil para kernel epistémico futuro, pero no es próximo corte. Requiere piezas previas y contrato reducido. | Conservar como insumo para fase epistémica; no promover ahora. |
| `PYMIA_MINIMAX_ASSERTION_CANDIDATE_SYNTHESIS_V2.md` | AssertionCandidate V1 | `DEFER_AS_ARCHITECTURAL_INPUT` | Media | Define unidad atómica diagnóstica futura. Valioso, pero dependiente de PrimaryCaseFile, evidence, packs y operator confirmation. | Conservar; promover sólo cuando se abra frente epistémico formal. |
| `PYMIA_MINIMAX_OPERATOR_CONFIRMATION_SYNTHESIS.md` | Confirmación humana append-only | `DEFER_AS_ARCHITECTURAL_INPUT` | Media | Importante para evitar LLM-as-decider. No debe implementarse antes de cerrar boundary de caso y candidate. | Conservar; no implementar. |
| `PYMIA_MINIMAX_OWNER_SEMANTIC_CLAIM_SYNTHESIS.md` | Relato del dueño, TensionReport, claims | `RECONCILE_WITH_QUESTION_ALIGNMENT` | Alta | Se relaciona directamente con el gap rector reportado: QuestionAlignmentGate. Puede informar contrato, pero no reemplazarlo. | Usar como insumo para `QuestionAlignmentGate Contract`. |
| `PYMIA_MINIMAX_DOMINANT_UNKNOWN_SYNTHESIS.md` | DominantUnknown / MinimumEvidencePath | `RECONCILE_WITH_QUESTION_ALIGNMENT` | Alta | Ayuda a definir “qué preguntar después” y evidencia mínima. Encaja con QuestionAlignmentGate, pero puede ser más avanzado. | Extraer sólo conceptos mínimos para gate; no implementar ranking completo. |
| `PYMIA_MINIMAX_PACK_GOVERNANCE_SYNTHESIS.md` | Gobernanza de packs | `COMPLEMENTS_EXISTING_PACK_DOCTRINE` | Media-alta | Refuerza conocimiento enchufable, pack states y validación. Debe reconciliarse con ADR-024 y FunctionalGraphPack. | Auditar contra ADR-024 antes de promover fragmentos. |
| `PYMIA_V1_PILOT_PROTOCOL_SYNTHESIS.md` | Piloto real 5 PyMEs | `PROMOTE_LATER_PRODUCT_OPS` | Media | Útil para fase post-saneamiento. No corresponde antes de cerrar contratos rectores. | Deferir hasta después de QuestionAlignmentGate / PrimaryCaseFile mínimo. |
| `PYMIA_V1_PRODUCT_SERVICE_DESIGN_SYNTHESIS.md` | Producto/servicio operator-assisted | `COMPLEMENTS_PRODUCT_STRATEGY` | Media | Alineado con servicio asistido, no SaaS self-service, operador humano y no score. No es contrato técnico. | Mantener como insumo comercial-operativo. |
| `ROADMAP_ACTUALIZADO_PYMIA_FIMEA.md` | Roadmap corregido | `PARTIALLY_VALIDATED_NEEDS_RECONCILIATION` | Alta | Corrige prioridad hacia QuestionAlignmentGate, pero debe contrastarse con docs vivos del repo. | Usar como working roadmap, no como autoridad. |
| `README.md` | Estado del inbox | `KEEP` | Alta | Define cuarentena documental y evita promoción accidental. | Mantener. |

---

# Hallazgos principales

## 1. Hay dos líneas rectoras que compiten

### Línea A — QuestionAlignmentGate

Reportada por el usuario como gap rector vivo del repo:

```text
síntoma / pregunta emergente del dueño
→ evidencia / faltante
→ próxima pregunta correcta
```

Insumos relacionados:

```text
PYMIA_MINIMAX_OWNER_SEMANTIC_CLAIM_SYNTHESIS.md
PYMIA_MINIMAX_DOMINANT_UNKNOWN_SYNTHESIS.md
ROADMAP_ACTUALIZADO_PYMIA_FIMEA.md
```

### Línea B — PrimaryCaseFile / FichaPrimaria

Nueva línea importada en inbox:

```text
sin caso sellado no hay diagnóstico gobernable
```

Insumos relacionados:

```text
FICHAPRIMARIA_CONTRACT_V1.md
PYMIA_MINIMAX_FICHA_PRIMARIA_SYNTHESIS.md
PYMIA_PRIMARY_CASE_FILE_FIRST_SLICE_GLM52.md
```

## 2. No conviene promover la FichaPrimaria completa

`FICHAPRIMARIA_CONTRACT_V1.md` es fuerte, pero demasiado amplio.

Riesgo:

```text
abrir lifecycle completo de caso antes de validar slice mínimo
```

Mejor candidato:

```text
PYMIA_PRIMARY_CASE_FILE_FIRST_SLICE_GLM52.md
```

porque reduce a contrato aislado y evita contaminar `vertical_slice.py`.

## 3. QuestionAlignmentGate sigue siendo prioridad metodológica reportada

Mientras no se lea documentación viva adicional que lo contradiga:

```text
QuestionAlignmentGate Contract
→ Test
→ Implementation
```

sigue teniendo prioridad sobre `owner_labels_v1`.

## 4. owner_labels_v1 queda fuera de esta matriz

No aparece entre los MD importados.

Estado:

```text
DEUDA_SECUNDARIA_PROBABLE
NO_NEXT_CUT_UNLESS_RECONFIRMED
```

---

# Orden recomendado corregido

## Paso 1 — Confirmar autoridad documental viva

Leer en repo:

```text
docs relevantes de QuestionAlignmentGate
question_alignment_v1 si existe
checkpoints recientes
```

Responder:

```text
EXISTS_CONTRACT / DECLARED_ONLY / MIXED / NOT_FOUND
```

## Paso 2 — Si QuestionAlignmentGate es declarado pero no contratado

Crear primero:

```text
QuestionAlignmentGate Contract
```

usando como insumo:

```text
PYMIA_MINIMAX_OWNER_SEMANTIC_CLAIM_SYNTHESIS.md
PYMIA_MINIMAX_DOMINANT_UNKNOWN_SYNTHESIS.md
ROADMAP_ACTUALIZADO_PYMIA_FIMEA.md
```

## Paso 3 — Recién después evaluar PrimaryCaseFile

Promover, si corresponde, el slice reducido:

```text
PYMIA_PRIMARY_CASE_FILE_FIRST_SLICE_GLM52.md
```

No promover el contrato largo sin reducción.

## Paso 4 — Dejar el resto como material epistémico futuro

Mantener diferidos:

```text
EpistemicState
AssertionCandidate
OperatorConfirmation
Pack Governance completo
Pilot Protocol
Product Service Design
```

---

# Clasificación final resumida

```text
PROMOTE_CANDIDATE:
- PYMIA_PRIMARY_CASE_FILE_FIRST_SLICE_GLM52.md

PROMOTE_CANDIDATE_WITH_REDUCTION:
- FICHAPRIMARIA_CONTRACT_V1.md

RECONCILE_WITH_QUESTION_ALIGNMENT:
- PYMIA_MINIMAX_OWNER_SEMANTIC_CLAIM_SYNTHESIS.md
- PYMIA_MINIMAX_DOMINANT_UNKNOWN_SYNTHESIS.md
- ROADMAP_ACTUALIZADO_PYMIA_FIMEA.md

COMPLEMENTS:
- PYMIA_MINIMAX_FICHA_PRIMARIA_SYNTHESIS.md
- PYMIA_MINIMAX_PACK_GOVERNANCE_SYNTHESIS.md
- PYMIA_V1_PRODUCT_SERVICE_DESIGN_SYNTHESIS.md

PROMOTE_LATER_PRODUCT_OPS:
- PYMIA_V1_PILOT_PROTOCOL_SYNTHESIS.md

DEFER_AS_ARCHITECTURAL_INPUT:
- PYMIA_MINIMAX_EPISTEMIC_STATE_SYNTHESIS.md
- PYMIA_MINIMAX_ASSERTION_CANDIDATE_SYNTHESIS_V2.md
- PYMIA_MINIMAX_OPERATOR_CONFIRMATION_SYNTHESIS.md

KEEP:
- README.md
```

---

# Stop condition

No promover ningún documento del inbox a `docs/` sin una tarea explícita.

No implementar código desde estos documentos.

No tratar los MD como autoridad arquitectónica viva todavía.

---

# Próximo paso metodológico

```text
AUDIT_QUESTION_ALIGNMENT_GATE_STATUS
```

Objetivo:

```text
confirmar si QuestionAlignmentGate ya existe como contrato vivo,
o si la documentación sólo declara el gap.
```

Resultado esperado:

```text
EXISTS_CONTRACT / DECLARED_ONLY / MIXED / NOT_FOUND
```
