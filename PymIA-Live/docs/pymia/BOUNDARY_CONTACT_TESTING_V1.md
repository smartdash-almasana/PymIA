# BOUNDARY_CONTACT_TESTING_V1

## Propósito

Este documento define la metodología de testing para la red de contactos entre fronteras vivas de PymIA-Live.

Hasta ahora se auditaron y congelaron fronteras individuales. El siguiente riesgo no está sólo dentro de cada módulo, sino en el tránsito entre módulos: que una frontera emita datos que otra consume parcialmente, que se pierda trazabilidad, que una duda documental no se transforme en pregunta al dueño, o que un estado reconstruido no refleje lo que el pipeline produjo.

El objetivo de esta capa de tests es verificar que los objetos críticos atraviesan la red viva sin pérdida semántica ni pérdida de trazabilidad.

## Regla central

Un test de contacto no prueba una función aislada.

Prueba que:

```text
frontera A produce X
frontera B consume X
la invariante Y se preserva
```

## Fronteras vivas gobernadas

Según el estado actual del `LIVE_CODE_FREEZE_LEDGER.md`, las fronteras vivas relevantes para esta metodología son:

| Frontera | Rol |
|---|---|
| `tools/document_ingestion.py` | Ingesta y curado documental/tabular. |
| `pymia/smartpyme/structured_evidence_builder.py` | Construcción de contexto de evidencia estructurada. |
| `pymia/application/vertical_pipeline.py` | Orquestación viva del caso. |
| `pymia/smartpyme/pipeline_registration.py` | Fachada de registro operativo. |
| `pymia/smartpyme/storage.py` | Persistencia filesystem/JSONL. |
| `pymia/smartpyme/case_replay.py` | Reconstrucción read-only de historia JSONL. |
| `pymia/smartpyme/ocf_snapshot.py` | Snapshot de estado organizacional del caso. |
| `pymia/smartpyme/owner_facing_report.py` | Reporte visible para dueño. |
| `pymia/smartpyme/owner_output.py` | Vista simplificada owner-facing. |
| `pymia/rendering/owner_markdown_renderer.py` | Render Markdown desacoplado. |
| `pymia/smartpyme/question_resolution.py` | Resolución de preguntas/referencias. |
| `pymia/smartpyme/question_alignment_gate.py` | Alineación de preguntas sin recomputar diagnóstico. |

## Contactos críticos

### 1. Ingestion → Structured Evidence Builder

**Pregunta:** ¿lo que extrae y cura `document_ingestion.py` puede convertirse en contexto de evidencia estable?

**Invariantes:**

- Las tablas extraídas siguen disponibles.
- Las variables computadas se preservan.
- Los campos desconocidos o ambiguos no se transforman en diagnóstico.
- La metadata de curación no se pierde.
- Los `formula_ids` explícitos no se inventan.

### 2. Structured Evidence Builder → Vertical Pipeline

**Pregunta:** ¿el pipeline consume la evidencia estructurada sin perder fórmula, variables ni estado de suficiencia?

**Invariantes:**

- `structured_summary` existe cuando la evidencia se pudo construir.
- `computed_variables_count` y nombres de variables se preservan.
- La evidencia insuficiente se expresa como faltante, no como hallazgo inventado.
- Los `formula_ids` siguen trazables.

### 3. Vertical Pipeline → Registration / Storage

**Pregunta:** ¿todo lo que el pipeline dice haber producido queda persistido como records JSONL recuperables?

**Invariantes:**

- `anamnesis_record` queda persistido.
- `investigation_record` queda persistido.
- `owner_answer_record` queda persistido si existe.
- `evidence_request_record` queda persistido si corresponde.
- `evidence_record` preserva `evidence_id` y `content_hash`.
- `pipeline_run_record` preserva `run_id`, `output_hash` y `output_artifact_id` si existen.

### 4. Storage → Case Replay

**Pregunta:** ¿la historia JSONL reconstruye el caso sin pérdida ni escritura colateral?

**Invariantes:**

- El replay es read-only.
- El orden de eventos es determinístico.
- Los links faltantes se reportan como `missing_links`, no se inventan.
- `PARTIAL_REPLAY` aparece si faltan records necesarios.
- `tenant_id`, `intake_id` y `case_id` no se mezclan con identidad comercial.

### 5. Case Replay → OCF Snapshot

**Pregunta:** ¿el OCF representa el estado actual desde replay sin inferencia no respaldada?

**Invariantes:**

- `evidence_refs` incluye `content_hash` cuando existe.
- `run_refs` incluye `output_hash` y `output_artifact_id` cuando existen.
- `owner_answer_refs` se preservan.
- `evidence_request_refs` se preservan.
- `open_unknowns` y `missing_variables` se derivan de records, no de heurística libre.
- `heuristic_ratio` permanece `0.0` salvo cambio explícito y gobernado.

### 6. Evidence Gaps / Ambiguity → Owner Questions

**Pregunta:** ¿lo que no queda claro se transforma en pregunta al dueño y no en diagnóstico?

**Invariantes:**

- Un campo ambiguo o faltante no se usa como valor confirmado.
- La salida owner-facing conserva `missing_evidence` o `next_questions`.
- La pregunta generada tiene referencia trazable cuando corresponde.
- La respuesta posterior del dueño puede vincularse con `owner_answer_record`.

## Tests mínimos propuestos

### BOUNDARY-CONTACT-001 — Hash propagation

Verificar propagación de trazabilidad fuerte:

```text
vertical_pipeline
→ pipeline_registration/storage
→ case_replay
→ ocf_snapshot
```

Debe probar que:

- `content_hash` generado/persistido por evidence record aparece en `OCF.evidence_refs`.
- `output_hash` generado/persistido por pipeline run aparece en `OCF.run_refs`.
- `evidence_id` y `run_id` no se pierden.

### BOUNDARY-CONTACT-002 — Missing evidence to owner question

Verificar que evidencia insuficiente genera pregunta o faltante visible:

```text
structured evidence incompleta
→ vertical_pipeline
→ owner_facing_report
→ renderer
```

Debe probar que:

- No se inventan variables faltantes.
- El caso queda bloqueado o marcado como insuficiente según corresponda.
- `next_questions` o `missing_evidence` quedan visibles.

### BOUNDARY-CONTACT-003 — Replay preserves owner answer linkage

Verificar continuidad dueño-respuesta:

```text
owner_answer_record
→ storage
→ case_replay
→ ocf_snapshot
```

Debe probar que:

- La respuesta del dueño conserva `question_ref`.
- El OCF refleja que hubo respuesta.
- No se sobrescribe evidencia previa.

### BOUNDARY-CONTACT-004 — Curation ambiguity does not become diagnosis

Verificar que la ambigüedad documental no atraviesa como certeza:

```text
curation report con campo ambiguo
→ structured evidence
→ pipeline/report
```

Debe probar que:

- El campo ambiguo queda marcado como tal.
- No se usa como valor confirmado para cálculo crítico.
- Se convierte en warning, faltante o pregunta.

## Regla para nuevos canales de evidencia

Ningún canal nuevo de evidencia entra al flujo vivo sin al menos un test de contacto.

Esto aplica a:

- OCR.
- PDF.
- imágenes.
- capturas de WhatsApp.
- texto libre estructurado.
- futuros conectores documentales.

La regla específica para OCR queda alineada con el documento `OCR_EVIDENCE_RECOVERY_INTENT.md`:

```text
OCR no interpreta lo dudoso: lo convierte en gap trazable.
```

## Criterio de cierre de esta metodología

`BOUNDARY_CONTACT_TESTING_V1` queda completo cuando existe al menos:

1. Un test de contacto para propagación de hashes.
2. Un test de contacto para evidencia faltante → pregunta al dueño.
3. Un test de contacto para replay → OCF.
4. Registro posterior en `LIVE_CODE_FREEZE_LEDGER.md` o checkpoint versionado.

## No objetivos

Esta metodología no autoriza:

- Refactorizar módulos congelados.
- Crear OCR productivo.
- Cambiar contratos vivos.
- Cambiar storage.
- Introducir base de datos.
- Ejecutar diagnóstico nuevo.
- Reemplazar el pipeline.

Sólo define cómo probar los contactos entre fronteras antes de introducir nuevas capacidades.
