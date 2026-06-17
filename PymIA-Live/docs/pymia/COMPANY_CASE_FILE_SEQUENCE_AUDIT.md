# COMPANY_CASE_FILE_SEQUENCE_AUDIT

## Estado

BASIC_SEQUENCE_CLEAR

## Objetivo

Registrar la auditoría mínima de la secuencia lógica entre ficha mínima de empresa, narrativa del dueño, datos/evidencia, investigación, pedidos de evidencia, respuestas del dueño, reporte owner-facing y traza del caso en `PymIA-Live`.

Este checkpoint no autoriza implementación. Sólo cristaliza el estado actual para evitar deriva arquitectónica.

## Veredicto

```text
BASIC_SEQUENCE_CLEAR
FORMAL_COMPANY_FILE_PENDING
DOC_CHECKPOINT_ONLY
```

La secuencia básica está clara y es suficiente para piloto asistido. No existe todavía una ficha formal de empresa/productiva completa, y no debe crearse sin TaskSpec separado.

## Secuencia actual

```text
mensaje del dueño
→ ficha mínima de empresa
→ Excel / evidencia operacional
→ anamnesis
→ investigación
→ structured evidence
→ reconciliación catálogo/evidencia
→ pedido de evidencia faltante, si aplica
→ respuesta del dueño, si aplica
→ reporte owner-facing
→ pipeline run con output_hash
```

## Mapa de registros

### 1. Narrativa original del dueño

Entrada:

```text
--message
```

Registro:

```text
AnamnesisRecord.raw_owner_message
```

Archivo:

```text
pymia/smartpyme/anamnesis.py
```

Decisión: la narrativa original se preserva sin ser reescrita ni promovida automáticamente a evidencia dura.

### 2. Ficha mínima de empresa

Entrada CLI:

```text
--empresa-tipo
--industria
--modelo-comercial
--canal-venta
--area-critica
```

Modelo:

```text
BusinessTaxonomy
```

Campos actuales:

```text
empresa_tipo
industria
modelo_comercial
canales_venta
areas_criticas
maneja_stock
produce_revende_o_servicio
```

Decisión: esto es ficha mínima suficiente para piloto asistido. No es CRM, ERP ni ficha legal completa.

### 3. Datos / evidencia

Entrada:

```text
--excel
```

Registros y estructuras:

```text
EvidenceRecord
StructuredEvidence
computed_variables
tables
catalog_reconciliation
```

Campos de trazabilidad:

```text
tenant_id
intake_id
evidence_id
request_id opcional
content_hash
source_ref
original_filename
```

### 4. Investigación

Registro:

```text
InvestigationRecord
```

Conexiones:

```text
tenant_id
intake_id
anamnesis_id
owner_prompt
```

Decisión: separa lo dicho por el dueño de la investigación técnica posterior.

### 5. Pedido de evidencia faltante

Registro:

```text
EvidenceRequestRecord
```

Conexiones:

```text
anamnesis_id
investigation_id
owner_answer_id opcional
requested_evidence
request_reason
status
```

Decisión: los pedidos son trazables y se renderizan con labels owner-facing cuando corresponde.

### 6. Respuesta posterior del dueño

Entrada CLI:

```text
--owner-answer
--owner-answer-question-ref
```

Registro:

```text
OwnerAnswerRecord
```

Conexiones:

```text
anamnesis_id
investigation_id
question_ref
raw_owner_answer
```

Decisión: la respuesta del dueño queda registrada como respuesta/narrativa. No se promueve automáticamente a `EvidenceRecord`.

### 7. Reporte owner-facing

Archivo:

```text
pymia/rendering/owner_markdown_renderer.py
```

Incluye:

```text
qué entendimos
qué pudimos leer
qué todavía no podemos afirmar
próxima pregunta
límites
IDs operativos principales
```

Decisión: existe salida asistida útil para operador/dueño, pero puede requerir futura separación entre vista operador y vista dueño final.

### 8. Traza del caso

Cadena observada:

```text
tenant_id
intake_id
anamnesis_id
investigation_id
owner_answer_id opcional
evidence_request_id opcional
evidence_id
run_id
output_hash
```

Checkpoint relacionado:

```text
docs/pymia/CASE_TRACE_CONTINUITY_AUDIT.md
```

## Evidencia externa incorporada

Auditoría externa Qwen 3.7-Max:

```text
VEREDICTO: BASIC_SEQUENCE_CLEAR
FICHA_EMPRESA: MINIMAL_PRESENT
NARRATIVA_DUEÑO: PRESERVED
DATOS_EVIDENCIA: TRACEABLE
TRAZA_CASO: TRACE_READY
RECOMENDACIÓN: DOC_CHECKPOINT_ONLY
```

Evaluación interna: auditoría útil, coherente con lectura previa, sin empujar implementación ni contrato nuevo.

## Gaps no bloqueantes

1. No existe ficha formal productiva de empresa con datos legales/comerciales completos.
2. No está documentada aún una estrategia definitiva de vista operador vs vista dueño final.
3. No existe operación de replay/reconstrucción histórica completa desde JSONL persistidos.
4. `PrimaryCaseFile V1` no debe conectarse todavía a este flujo sin TaskSpec separado.
5. No debe crearse una ficha empresa paralela si los registros actuales ya cubren el piloto asistido.

## Riesgos de deriva

```text
convertir ficha mínima en CRM
mezclar narrativa del dueño con evidencia dura
crear CompanyCaseFile prematuro
crear contrato paralelo a AnamnesisRecord o BusinessTaxonomy
tocar runtime sin necesidad
exponer demasiada técnica al dueño final
perder separación entre operador asistido y dueño PyME
```

## No tocar

```text
código Python
JSON contractual
tests
pipeline
DiagnosticCore
fórmulas
QuestionAlignmentGate
FunctionalGraphPack runtime
presentation_labels_v1
vertical_slice_copy_v1
language_corpus_v1
PrimaryCaseFile V1
```

## Decisión operativa

No se requiere implementación ahora.

El próximo avance, si se prioriza, debe ser una de estas dos opciones y requerirá TaskSpec separado:

```text
OWNER_OPERATOR_VIEW_SPLIT
CASE_REPLAY_FROM_JSONL
```

No abrir ficha empresa formal ni CompanyCaseFile sin necesidad certificada.

## Estado final

```text
CLOSED_NO_CODE_CHANGE
```
