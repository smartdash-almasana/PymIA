# CASE_TRACE_CONTINUITY_AUDIT

## Estado

TRACE_READY

## Objetivo

Registrar la auditoría de continuidad de traza del caso en `PymIA-Live`, sin modificar código ni contratos.

## Pregunta auditada

¿Puede reconstruirse un caso PyME desde la entrada del dueño hasta la salida del pipeline usando los identificadores persistidos?

## Veredicto

TRACE_READY

La cadena de traza básica está cubierta para el flujo vertical actual.

## Cadena observada

```text
anamnesis_id
→ investigation_id
→ owner_answer_id opcional
→ evidence_request_id opcional
→ evidence_id
→ run_id
→ output_hash
```

## Evidencia técnica

### Registro

Archivo auditado:

```text
pymia/smartpyme/pipeline_registration.py
```

Funciones relevantes:

```text
register_anamnesis_record
register_investigation_record
register_owner_answer_record
register_evidence_request_record
register_evidence_record
register_pipeline_run_record
```

`register_pipeline_run_record` conserva IDs cruzados en `output_payload` y `metadata`:

```text
anamnesis_id
investigation_id
owner_answer_id si existe
evidence_request_id si existe
evidence_id
```

### Persistencia

Archivo auditado:

```text
pymia/smartpyme/storage.py
```

JSONL por tenant:

```text
anamnesis.jsonl
investigations.jsonl
owner_answers.jsonl
evidence_requests.jsonl
evidences.jsonl
pipeline_runs.jsonl
```

La persistencia valida campos obligatorios y consistencia mínima de `tenant_id`.

### Render owner-facing

Archivo auditado:

```text
pymia/rendering/owner_markdown_renderer.py
```

El markdown expone identificadores operativos principales:

```text
Anamnesis ID
Investigation ID
Evidence ID
Evidence SHA-256
Run ID
Owner Answer ID si existe
Evidence Request ID si existe
```

### Tests existentes

Archivo auditado:

```text
tests/e2e/test_vertical_slice_cli.py
```

Cobertura observada:

```text
anamnesis_id conectado a investigation_id
pipeline metadata con anamnesis_id
pipeline metadata con investigation_id
owner_answer_id conectado si hay respuesta
evidence_request_id conectado si faltan inputs
evidence_record.request_id conectado a evidence_request_id
markdown con IDs principales
```

## Fuera de alcance

Esta auditoría no abre ni modifica:

```text
DiagnosticCore
fórmulas
PrimaryCaseFile V1
QuestionAlignmentGate
FunctionalGraphPack runtime
presentation_labels_v1
vertical_slice_copy_v1
language_corpus_v1
UI
LLM
canales externos
```

## Decisión

No se requiere TaskSpec de implementación para traza básica.

No se modifica código.
No se modifica JSON.
No se modifican tests.
No se ejecuta pytest.

## Gap residual

La continuidad básica está cubierta, pero una auditoría futura podría revisar recuperación completa de caso desde archivos JSONL persistidos, como operación de replay o reconstrucción histórica. Ese frente no queda abierto por este documento.

## Estado final

CLOSED_NO_CODE_CHANGE
