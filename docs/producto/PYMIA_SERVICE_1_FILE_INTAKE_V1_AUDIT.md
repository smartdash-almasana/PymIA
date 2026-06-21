# PYMIA_SERVICE_1_FILE_INTAKE_V1_AUDIT

## Estado

```text
Tipo: ROADMAP_CYCLE_7_AUDIT
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Auditar la evidencia existente para `File Intake V1` antes de diseñar o implementar recepción/clasificación de archivos en Servicio 1.

Este documento no autoriza código, runtime, pipeline, XLSX delivery ni LLM adapter.

---

# 1. Roadmap position

Ciclo actual del roadmap:

```text
Ciclo 7 — File Intake V1
```

Objetivo del ciclo:

```text
Definir recepción y clasificación de archivos: xlsx, csv, pdf, zip, imagen.
```

Salida esperada futura:

```text
archivo clasificado
tipo detectado
riesgo detectado
siguiente acción
```

---

# 2. Archivos leídos

```text
PymIA-Live/tools/document_ingestion.py
tests/test_document_ingestion.py
```

Búsquedas complementarias:

```text
document_ingestion
PDF
csv_upload
```

---

# 3. Evidencia encontrada

## 3.1 document_ingestion.py

Archivo:

```text
PymIA-Live/tools/document_ingestion.py
```

Fragmento relevante:

```text
"Glass-box local document ingestion and curation for PymIA."
"It separates: raw table extraction, semantic field mapping, curation reporting, StructuredEvidence export."
"It intentionally lives in tools/ and does not diagnose operationally by itself."
```

Componentes detectados:

```text
RawTable
FieldMapping
NormalizedTable
CellValidationIssue
DocumentCurationReport
CuratedDocument
ContextClassifier
XlsxDocumentIngestor
SemanticFieldMapper
DocumentCurator
ColumnConfirmationBuilder
StructuredEvidenceExporter
XlsxCurationPipeline
curate_xlsx_document
build_structured_evidence_from_xlsx
persist_curation_artifacts
```

Conclusión:

```text
Existe ingesta/curation XLSX local, auditable y determinística, orientada a extracción tabular, mapeo semántico, reporte de curación y export a StructuredEvidence.
```

Límite:

```text
Vive en tools/, no en una frontera Servicio 1. No es File Intake V1 como contrato de producto.
```

---

## 3.2 tests/test_document_ingestion.py

Archivo:

```text
tests/test_document_ingestion.py
```

Tests detectados:

```text
test_curate_xlsx_document_builds_artifact
test_curated_document_is_json_serializable
test_document_ingestion_exports_structured_evidence
test_document_ingestion_persists_expected_artifacts
test_document_ingestion_of_internal_fact_runs_operational_audit
test_datetime_parsing_does_not_emit_pandas_warnings
test_intake_forces_bem_ai_on_administrative_contexts
```

Conclusión:

```text
Hay tests para curación XLSX, serialización JSON, export StructuredEvidence, persistencia de artefactos, parsing de fechas y degradación de contexto administrativo/fiscal.
```

Límite:

```text
No son tests de Service 1 File Intake V1. Son tests de tool/document_ingestion y rutas relacionadas.
```

---

# 4. Soporte por tipo de archivo

| Tipo | Evidencia | Estado | Nota |
|---|---|---|---|
| XLSX | `XlsxDocumentIngestor`, `curate_xlsx_document`, tests con `pyme_textil_compleja.xlsx` | IMPLEMENTED_PARTIAL | Existe como tool local, no como File Intake V1 de Servicio 1. |
| CSV | `EvidenceSource` incluye `csv_upload`; búsqueda no encontró ingestor CSV dedicado en PymIA-Live | DEFINED_ONLY | No confirmado como intake funcional. |
| PDF | `EvidenceSource` incluye `pdf_upload`; docs mencionan PDF futuro / fuera de alcance | DEFINED_ONLY / FUTURE | No hay ingesta PDF funcional confirmada. |
| ZIP | No encontrado | MISSING | No hay evidencia de soporte. |
| Imagen | OCR intent documentado; no intake productivo | DOCUMENTED_ONLY | No hay runtime confirmado. |
| Manual entry | `EvidenceSource` incluye `manual_entry` | DEFINED_ONLY | No auditado como flujo Servicio 1. |

---

# 5. Hallazgo de duplicación

Búsqueda `document_ingestion` devuelve referencias a:

```text
PymIA-Live/tools/document_ingestion.py
tools/document_ingestion.py
```

Riesgo:

```text
Puede existir duplicación entre raíz y PymIA-Live, o referencias históricas generadas por graphify.
```

Decisión de este audit:

```text
No resolver duplicación ahora.
Documentar como riesgo para File Intake V1.
```

---

# 6. Relación con Servicio 1

File Intake V1 debe convertir piezas existentes en frontera de producto:

```text
upload / path / chat attachment
→ classify file type
→ detect supported/unsupported
→ detect risk flags
→ choose next_allowed_action
→ produce intake result
```

La pieza existente `document_ingestion.py` cubre parcialmente:

```text
xlsx tabular extraction
semantic mapping
normalization
column confirmation matrix
StructuredEvidence export
artifact persistence
```

No cubre formalmente:

```text
file type router Servicio 1
CSV intake dedicated
PDF intake
ZIP intake
image/OCR intake
unsupported file handling contract
risk classification contract
owner-facing intake response
TaskSpec integration
FSM transition integration
```

---

# 7. Riesgos

```text
R1. Confundir document_ingestion.py con File Intake V1 completo.
R2. Abrir PDF/imagen antes de cerrar XLSX intake.
R3. Conectar intake directo a diagnóstico o pipeline sin TaskSpec/FSM.
R4. Duplicar tools/document_ingestion.py y PymIA-Live/tools/document_ingestion.py.
R5. Tratar CSV/PDF como soportados porque existen literales csv_upload/pdf_upload.
R6. Saltar column confirmation antes de cálculos.
```

---

# 8. Decisión conservadora

```text
File Intake V1 debe empezar por XLSX.
CSV, PDF, ZIP e imagen quedan explícitamente fuera del primer contrato ejecutable.
```

Motivo:

```text
XLSX tiene evidencia real de código y tests.
Los otros formatos sólo tienen menciones o intención documental.
```

---

# 9. Próximo documento recomendado

```text
docs/producto/PYMIA_SERVICE_1_FILE_INTAKE_V1.md
```

Debe definir:

```text
input asset contract
supported file types V1
unsupported file behavior
risk flags
classification result
next_allowed_action
relationship to TaskSpec
relationship to FSM
relationship to document_ingestion.py
```

Restricción sugerida:

```text
V1 soporta XLSX only.
CSV/PDF/ZIP/image quedan FUTURE / UNSUPPORTED_IN_V1.
```

---

# 10. Veredicto

```text
PYMIA_SERVICE_1_FILE_INTAKE_V1_AUDIT = CLOSED_AS_EVIDENCE
```

Condición:

```text
Este audit no autoriza implementación. Habilita diseño documental de File Intake V1 con alcance XLSX-first.
```
