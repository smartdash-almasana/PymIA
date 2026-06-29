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
| Hermes como nombre/runtime | LEGACY / CONGELADO |
| conversa-engine | CONGELADO |
| UI/API/SaaS | FUTURO |
| Pack runtime | FUTURO |
| LC-7 | FUTURO |
| Pronóstico | FUTURO |


Nota de saneamiento terminológico:

```text
Hermes no es fuente rectora vigente ni dependencia runtime activa.
El lenguaje vigente para producto/arquitectura nueva es:
IA conversacional / capa de interacción continua con el dueño PyME.
```

Esto no elimina la arquitectura fundacional:

```text
Dueño PyME ↔ IA conversacional ↔ PymIA computacional
```

Sólo retira a Hermes como nombre operativo del proyecto vivo.

Regla:

```text
Lo histórico conserva verdad, pero no autoridad operativa vigente.
```

---

## 7. Gap vivo principal

```text
El mensaje del dueño entra al reporte y a la traza, pero todavía no gobierna la priorización de la próxima pregunta.
```

Forma observada:

```text
Dueño declara: caja / liquidez.
Reconciliación sugiere: stock / reposición.
Salida actual: pregunta automática puede seguir el primer faltante técnico disponible.
```

Mitigación vigente:

```text
Regla transitoria de reconducción humana en runbook post-LC.
```

---

## 8. Próxima mejora inteligente

Nombre operativo:

```text
QuestionAlignmentGate
```

Propósito:

```text
Alinear la próxima pregunta con el eje declarado por el dueño y la evidencia detectada.
```

Contrato conceptual mínimo:

```text
OwnerDeclaredAxis
EvidenceDetectedAxis
CandidateQuestionAxis
QuestionAlignmentGateResult
```

Resultados esperados:

```text
ALIGNED      → emitir pregunta automática
MISALIGNED   → pedir confirmación/reconducción
UNKNOWN      → pregunta neutra de aclaración
```

Ubicación probable:

```text
después de catalog_reconciliation
antes de _build_owner_question
```

Advertencia metodológica:

```text
QuestionAlignmentGate no puede implementarse desde este manifiesto.
Antes de escribir código requiere contrato propio, test de aceptación y cierre metodológico.
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
