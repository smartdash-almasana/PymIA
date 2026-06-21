# PYMIA_SERVICE_1_FILE_INTAKE_V1

## Estado

```text
Tipo: ROADMAP_CYCLE_7
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
Pipeline impact: NONE
XLSX delivery impact: NONE
LLM impact: NONE
```

## Propósito

Definir la frontera de recepción y clasificación de archivos para PymIA Servicio 1.

Este documento convierte el audit previo de File Intake en contrato funcional de producto, con alcance conservador:

```text
V1 = XLSX-first
CSV/PDF/ZIP/imagen = UNSUPPORTED_IN_V1 / FUTURE
```

---

# 1. Cadena previa

```text
PYMIA_SERVICE_1_ARCHAEOLOGY_AUDIT_V1
→ PYMIA_SERVICE_1_CAPABILITY_MATRIX_V1
→ PYMIA_SERVICE_1_TASKSPEC_V1
→ PYMIA_SERVICE_1_OPERATIONAL_FSM_V1
→ PYMIA_SERVICE_1_FILE_INTAKE_V1_AUDIT
→ PYMIA_SERVICE_1_FILE_INTAKE_V1
```

---

# 2. Regla rectora

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

File Intake V1 no diagnostica, no calcula, no concilia y no genera archivos de salida.

Su única función es:

```text
recibir archivo
clasificarlo
validar soporte V1
detectar riesgos iniciales
producir un resultado de intake
definir la próxima acción permitida
```

---

# 3. Fuente técnica disponible

Implementación canónica existente para ingesta XLSX:

```text
PymIA-Live/tools/document_ingestion.py
```

Shim de compatibilidad raíz:

```text
tools/document_ingestion.py
```

Closeout relacionado:

```text
docs/producto/DOCUMENT_INGESTION_DUPLICATION_FIX_V1_CLOSEOUT.md
```

Resultado validado del fix de duplicación:

```text
44 passed
```

---

# 4. Alcance V1

## Soportado en V1

```text
XLSX
```

Condición:

```text
Sólo archivos tabulares o semi-tabulares que puedan pasar por curation local.
```

## No soportado en V1

```text
CSV
PDF
ZIP
imagen
OCR
manual_entry productivo
```

Estado:

```text
UNSUPPORTED_IN_V1 / FUTURE
```

---

# 5. Responsabilidad de File Intake V1

File Intake V1 debe producir un `FileIntakeResult`.

Debe responder:

```text
qué archivo llegó
qué tipo parece ser
si el tipo está soportado en V1
si puede enviarse a document_ingestion.py
si requiere confirmación del dueño
si hay riesgos iniciales
qué próxima acción permite la FSM
```

No debe responder:

```text
qué diagnóstico surge
qué fórmula aplicar
qué conciliación corresponde
qué XLSX entregar
qué decisión económica tomar
```

---

# 6. Contrato conceptual

```yaml
file_intake_id: string
schema_version: "1.0"
service_name: "SERVICE_1"
source_channel: cli | chat | upload | api | unknown
asset:
  asset_id: string
  filename: string | null
  declared_mime_type: string | null
  detected_file_type: xlsx | csv | pdf | zip | image | text | unknown
  size_bytes: integer | null
  source: upload | path | message | api | unknown
support:
  status: SUPPORTED | UNSUPPORTED_IN_V1 | UNKNOWN
  reason_code: string
  owner_message: string
routing:
  candidate_intake_engine: document_ingestion_xlsx | none
  next_allowed_action: string
risk_flags: list
curation_required: boolean
column_confirmation_expected: boolean
blocks_runtime: boolean
notes: list
```

---

# 7. Support status

```text
SUPPORTED
UNSUPPORTED_IN_V1
UNKNOWN
```

## SUPPORTED

Sólo cuando:

```text
detected_file_type = xlsx
```

y el archivo puede enviarse a ingesta XLSX local.

## UNSUPPORTED_IN_V1

Para:

```text
csv
pdf
zip
image
ocr
manual_entry productivo
```

## UNKNOWN

Cuando:

```text
no se puede detectar tipo
extensión ausente
mime ambiguo
archivo corrupto
```

---

# 8. Reason codes

```text
SUPPORTED_XLSX_V1
UNSUPPORTED_CSV_V1
UNSUPPORTED_PDF_V1
UNSUPPORTED_ZIP_V1
UNSUPPORTED_IMAGE_V1
UNSUPPORTED_OCR_V1
UNKNOWN_FILE_TYPE
EMPTY_FILE
CORRUPT_FILE
MIME_EXTENSION_MISMATCH
UNSAFE_FILENAME
```

---

# 9. Risk flags

```text
ambiguous_file_type
unsupported_format
mime_extension_mismatch
empty_file
corrupt_file
unsafe_filename
multiple_files_not_supported
requires_column_confirmation
contains_admin_or_fiscal_context
contains_possible_accounting_claims
```

Regla:

```text
Los risk_flags no son diagnóstico.
Sólo gobiernan bloqueo, advertencia o próxima acción.
```

---

# 10. Next allowed actions

```text
send_to_xlsx_document_ingestion
ask_owner_to_upload_xlsx
reject_unsupported_file_type
ask_owner_for_clearer_file
ask_owner_to_confirm_columns_after_curation
block_runtime_until_supported
```

---

# 11. Relación con TaskSpec

TaskSpec representa el pedido.

File Intake representa el archivo.

Relación:

```text
TaskSpec.input_assets[]
→ FileIntakeResult
→ TaskSpec.evidence_received / missing_evidence / blocking_state
```

File Intake puede enriquecer TaskSpec con:

```text
asset_id
detected_file_type
support.status
risk_flags
next_allowed_action
column_confirmation_expected
```

File Intake no debe alterar:

```text
owner_problem
requested_claims
forbidden_claims
requested_formula_refs
```

---

# 12. Relación con FSM

Estados relevantes:

```text
LISTENING
TASK_CLASSIFIED
EVIDENCE_RECEIVED
CONFIRMATION_REQUIRED
BLOCKED
```

Transiciones permitidas:

```text
LISTENING → TASK_CLASSIFIED
TASK_CLASSIFIED → EVIDENCE_RECEIVED
EVIDENCE_RECEIVED → CONFIRMATION_REQUIRED
EVIDENCE_RECEIVED → BLOCKED
```

Ejemplo:

```text
archivo XLSX válido
→ send_to_xlsx_document_ingestion
→ curation report
→ column confirmation matrix
→ CONFIRMATION_REQUIRED
```

Ejemplo unsupported:

```text
archivo PDF
→ UNSUPPORTED_IN_V1
→ BLOCKED
→ ask_owner_to_upload_xlsx
```

---

# 13. Relación con document_ingestion.py

`document_ingestion.py` sigue siendo tool local de ingesta/curation.

File Intake V1 debe envolverla, no reemplazarla.

```text
File Intake V1:
  clasifica soporte y gobierna entrada

document_ingestion.py:
  extrae tablas, mapea campos, arma reportes, exporta StructuredEvidence
```

Regla:

```text
Ningún archivo debe ir directo a diagnóstico sin pasar por File Intake + TaskSpec + FSM.
```

---

# 14. Owner-facing messages

## XLSX soportado

```text
Recibí el archivo Excel. Puedo revisarlo como evidencia operativa inicial. Antes de calcular o concluir algo, voy a identificar hojas, columnas y posibles campos que necesiten confirmación.
```

## CSV no soportado en V1

```text
Recibí un CSV, pero esta versión del servicio todavía trabaja sólo con archivos Excel XLSX. Para avanzar, necesito que lo envíes como XLSX.
```

## PDF no soportado en V1

```text
Recibí un PDF, pero esta versión todavía no procesa PDF como evidencia tabular. Para avanzar, necesito una planilla XLSX con los datos.
```

## Imagen no soportada en V1

```text
Recibí una imagen, pero esta versión todavía no procesa OCR ni capturas. Para avanzar, necesito una planilla XLSX.
```

## Tipo desconocido

```text
No pude identificar con seguridad el tipo de archivo. Para avanzar en esta versión, necesito un archivo XLSX.
```

---

# 15. Ejemplos de FileIntakeResult

## 15.1 XLSX soportado

```yaml
file_intake_id: file_intake_001
schema_version: "1.0"
service_name: SERVICE_1
source_channel: upload
asset:
  asset_id: asset_001
  filename: caja_diaria.xlsx
  declared_mime_type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
  detected_file_type: xlsx
  size_bytes: 18422
  source: upload
support:
  status: SUPPORTED
  reason_code: SUPPORTED_XLSX_V1
  owner_message: "Recibí el archivo Excel. Puedo revisarlo como evidencia operativa inicial."
routing:
  candidate_intake_engine: document_ingestion_xlsx
  next_allowed_action: send_to_xlsx_document_ingestion
risk_flags: []
curation_required: true
column_confirmation_expected: true
blocks_runtime: true
notes:
  - "No calcular hasta completar curación y confirmación de columnas."
```

---

## 15.2 PDF no soportado

```yaml
file_intake_id: file_intake_002
schema_version: "1.0"
service_name: SERVICE_1
source_channel: upload
asset:
  asset_id: asset_002
  filename: extracto_banco.pdf
  declared_mime_type: application/pdf
  detected_file_type: pdf
  size_bytes: 94211
  source: upload
support:
  status: UNSUPPORTED_IN_V1
  reason_code: UNSUPPORTED_PDF_V1
  owner_message: "Recibí un PDF, pero esta versión todavía no procesa PDF como evidencia tabular. Para avanzar, necesito una planilla XLSX con los datos."
routing:
  candidate_intake_engine: none
  next_allowed_action: ask_owner_to_upload_xlsx
risk_flags:
  - unsupported_format
curation_required: false
column_confirmation_expected: false
blocks_runtime: true
notes:
  - "PDF queda FUTURE."
```

---

# 16. Prohibiciones

```text
No diagnosticar desde File Intake.
No calcular desde File Intake.
No generar XLSX desde File Intake.
No invocar pipeline desde File Intake.
No usar IA para interpretar el contenido del archivo.
No aceptar CSV/PDF/ZIP/imagen como soportados en V1.
No saltar confirmación de columnas.
No convertir risk_flags en findings económicos.
```

---

# 17. Implementación futura sugerida

Archivo futuro:

```text
PymIA-Live/pymia/smartpyme/file_intake_v1.py
```

Tests futuros:

```text
PymIA-Live/tests/smartpyme/test_file_intake_v1.py
```

Casos mínimos:

```text
xlsx supported
csv unsupported
pdf unsupported
zip unsupported
image unsupported
unknown unsupported
mime/extension mismatch
unsafe filename
```

Condición:

```text
No conectar a pipeline hasta que File Intake V1 tenga contrato y tests focales.
```

---

# 18. Veredicto

```text
PYMIA_SERVICE_1_FILE_INTAKE_V1 = DRAFT_APPLIED
```

Condición:

```text
Documento de frontera. No autoriza runtime productivo.
```
