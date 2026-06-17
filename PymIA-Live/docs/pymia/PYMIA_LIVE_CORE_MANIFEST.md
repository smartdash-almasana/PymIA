# PYMIA LIVE CORE MANIFEST

## Estado

`LIVE_CORE_MANIFEST_V1`

## Propósito

Separar el PymIA vivo del museo histórico.

Este manifiesto no crea una capacidad nueva. Declara qué parte del sistema ejecuta, valida, decide u opera hoy, y qué parte queda como antecedente histórico o superficie congelada.

Regla de síntesis:

```text
Sólo manda lo que ejecuta, valida, decide, traduce, pregunta, registra evidencia u opera el flujo vigente.
```

---

## 1. Pipeline vivo actual

```text
owner_message
+
excel_upload (.xlsx)
↓
vertical_slice CLI
↓
EvidenceRecord
↓
StructuredEvidence
↓
catalog_reconciliation
↓
Language Corpus labels
↓
owner-facing question
↓
owner-facing markdown
↓
PipelineRunRecord
↓
human reconduction when needed
```

Lectura operacional:

```text
PymIA vivo hoy convierte Excel + mensaje del dueño en evidencia registrada, salida owner-facing candidata y trazabilidad mínima.
```

---

## 2. Archivos rectores vivos

| Archivo | Rol vivo | Decide |
|---|---|---|
| `AGENTS.md` | Contrato de arranque metodológico | Cómo se trabaja sin deriva |
| `docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md` | Operación vigente | Cómo ejecutar piloto asistido post-LC |
| `docs/contratos/language-corpus-v1.md` | Contrato LC V1 | Cómo traducir variables a lenguaje dueño |
| `docs/smartpyme/M27_EXCEL_SEMANTICA_DUENO_CHECKPOINT.md` | Antecedente aprobado vivo | Excel + semántica del dueño como slice válido |
| `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md` | Método de fabricación | Cadena arquitectura → contrato → test → código → evidencia |

---

## 3. Código vivo

| Archivo / módulo | Función viva |
|---|---|
| `pymia/cli/vertical_slice.py` | Entrada operativa local: Excel + mensaje → markdown trazable |
| `pymia/contracts/language_corpus_v1.py` | Carga y validación de Language Corpus V1 |
| `pymia/contracts/language_corpus_seed.json` | Seed LC mínimo activo |
| `pymia/smartpyme/evidence.py` | Construcción de EvidenceRecord |
| `pymia/smartpyme/storage.py` | Persistencia local de evidencia |
| `pymia/smartpyme/structured_evidence_builder.py` | Construcción de StructuredEvidence desde Excel |
| `pymia/audit_result/evidence_requirement_matcher.py` | Reconciliación evidencia ↔ requerimientos |
| `pymia/smartpyme/owner_facing_report.py` | Contrato de salida owner-facing |
| `pymia/contracts/pipeline_run_v1.py` | Registro de ejecución con run_id/output_hash |

---

## 4. Tests críticos vivos

| Test | Protege |
|---|---|
| `tests/contracts/test_language_corpus_v1.py` | Contrato y seed LC V1 |
| `tests/e2e/test_vertical_slice_cli.py` | Flujo vertical Excel → markdown owner-facing |
| `tests/smartpyme/test_semantic_field_resolution.py` | Resolución semántica de campos |
| `tests/smartpyme/test_post_ficha_evidence_gate.py` | Enriquecimiento semántico y evidence gate |
| `tests/smartpyme/test_owner_semantic_confirmation_reentry_projection.py` | Reentrada semántica explícita del dueño |

---

## 5. Capacidades aprobadas y vivas

| Capacidad | Estado | Evidencia |
|---|---|---|
| Language Corpus LC1-LC6 | VIVO | Commit `2360968`, smokes post-LC PASS |
| Runbook piloto asistido post-LC | VIVO | Commit `7341182` |
| Planificación piloto 001 | VIVO OPERATIVO | Commit `2f4fe81` |
| Reconducción humana asistida | VIVO OPERATIVO | Commit `eb7ffe1` |
| M27 Excel + semántica del dueño | APROBADO VIVO | `M27_EXCEL_SEMANTICA_DUENO_CHECKPOINT.md` |
| PILOTO_SIMULADO_001 | EVIDENCIA OPERATIVA | Resultado PARTIAL útil; gap de priorización conversacional detectado |

---

## 6. Superficies históricas o congeladas

Estas superficies pueden conservar verdad histórica, pero no mandan el próximo paso operativo.

| Superficie | Estado vivo |
|---|---|
| Checkpoints antiguos | HISTÓRICO APROBADO |
| Roadmaps absorbidos | HISTÓRICO / ABSORBIBLE |
| Auditorías repetidas | HISTÓRICO |
| Prompts acumulados | HISTÓRICO |
| Telegram | CONGELADO |
| Hermes | CONGELADO |
| conversa-engine | CONGELADO |
| UI/API/SaaS | FUTURO |
| Pack runtime | FUTURO |
| LC-7 | FUTURO |
| Pronóstico | FUTURO |

Regla:

```text
Lo histórico conserva verdad, pero no autoridad operativa vigente.
```

---

## 7. Estado de alineación de preguntas

```text
QuestionAlignmentGate = EXISTS_CONTRACT
Estado = CLOSED
Riesgo residual = LOW
```

El gap histórico de priorización de la próxima pregunta ya no debe presentarse como mejora futura abierta desde este manifiesto.

Evidencia documental:

```text
docs/pymia/QUESTION_ALIGNMENT_GATE_SPEC.md
docs/pymia/QUESTION_ALIGNMENT_DECLARATIVE_SANITIZATION_CLOSED.md
```

Evidencia técnica:

```text
pymia/contracts/question_alignment_v1.json
pymia/contracts/question_alignment_v1.py
pymia/smartpyme/question_alignment_gate.py
pymia/smartpyme/question_resolution.py
pymia/application/vertical_pipeline.py
tests/contracts/test_question_alignment_v1.py
tests/smartpyme/test_question_alignment_gate.py
```

Prohibición:

```text
No reabrir QuestionAlignmentGate sin nuevo hallazgo verificable.
```

---

## 8. Gaps vivos no bloqueantes

```text
FORMAL_COMPANY_FILE_PENDING
OWNER_OPERATOR_VIEW_SPLIT_FUTURE
CASE_REPLAY_FROM_JSONL_FUTURE
```

Lectura operacional:

```text
La secuencia empresa/narrativa/datos/traza está clara para piloto asistido.
No requiere implementación inmediata.
```

Checkpoints relacionados:

```text
docs/pymia/PRESENTATION_LABELS_V1_COVERAGE_TASKSPEC.md
docs/pymia/CASE_TRACE_CONTINUITY_AUDIT.md
docs/pymia/COMPANY_CASE_FILE_SEQUENCE_AUDIT.md
```

---

## 9. Regla de avance desde este manifiesto

Antes de abrir una capacidad nueva, debe existir:

```text
1. archivo rector
2. contrato mínimo
3. test de aceptación
4. evidencia
5. checkpoint o cierre operativo
```

Este manifiesto prioriza síntesis:

```text
menos archivos con autoridad
más claridad sobre qué ejecuta
más determinismo visible en el flujo
```
