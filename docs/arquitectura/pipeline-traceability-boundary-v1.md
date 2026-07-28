# Pipeline Traceability Boundary V1

## Estado

HISTORICAL_SNAPSHOT_SUPERSEDED.

Este documento conserva una frontera de trazabilidad histórica. Sus referencias a `pymia.interfaces`, `ClinicalConversationalPort`, `InitialLaboratoryAnamnesisService` y `AdmissionPipelineV1` no constituyen autoridad vigente ni deben reintroducir esas superficies eliminadas. La autoridad actual se rige por la arquitectura canónica de Servicio 1 y sus contratos activos.

Este documento convierte una discusion de diseno en una regla verificable para PymIA: ninguna respuesta clinico-operacional debe depender de confianza implicita, inferencia conversacional o promesa de prompt.

La ejecucion debe ser comprobable.

---

# 1. Problema

PymIA puede recibir del duenio de una PyME:

```text
un problema narrado
+
un archivo de evidencia, por ejemplo Excel, CSV o PDF
```

Ejemplo:

```text
"RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY"
+
ventas_abril.xlsx
```

El riesgo critico es que el chatbot use el texto y el archivo para hacer un analisis libre con IA, saltando el pipeline deterministico definido por la arquitectura.

Eso produciria respuestas aparentemente utiles, pero no auditables.

La seguridad basada en instruccion conversacional es debil.

No alcanza con decir:

```text
"el chatbot debe usar el pipeline"
```

Debe poder demostrarse.

---

# 2. Tesis

Toda respuesta clinico-operacional de PymIA debe ser derivable de una cadena de ejecucion verificable.

La cadena minima obligatoria es:

```text
InputRecord
-> EvidenceRecord
-> PipelineRunRecord
-> DDIArtifact / artefacto clinico-operacional
-> ResponseRecord
```

Sin esa cadena, la respuesta no debe considerarse valida.

---

# 3. Regla rectora

```text
No run_id, no clinical response.
```

Toda respuesta que contenga diagnostico, hipotesis, pedido de evidencia, hallazgo, estado clinico-operacional o recomendacion debe estar asociada a un `PipelineRunRecord` valido.

Si no existe `run_id`, el adaptador conversacional solo puede devolver un error tecnico o una respuesta no clinica.

---

# 4. Separacion de responsabilidades

## 4.1 IA conversacional

La IA conversacional puede:

```text
- recibir lenguaje natural;
- explicar resultados ya producidos por el kernel;
- reformular mensajes para el duenio;
- guiar al usuario hacia evidencia faltante;
- hacer preguntas aclaratorias bajo contrato.
```

La IA conversacional no puede:

```text
- diagnosticar libremente;
- calcular margen, stock, liquidez o ROI por cuenta propia;
- interpretar un Excel como texto libre y emitir conclusiones;
- convertir documentos en claims narrativos para saltar el boundary;
- presentar una patologia como confirmada sin evidencia trazable;
- emitir una respuesta clinico-operacional sin PipelineRunRecord.
```

## 4.2 Pipeline deterministico

El pipeline deterministico debe:

```text
- recibir input normalizado;
- recibir evidencia estructurada;
- ejecutar pasos versionados;
- producir artefactos verificables;
- declarar evidencia requerida, recibida y faltante;
- devolver output hasheable;
- registrar la ejecucion.
```

## 4.3 Adaptadores externos

Hermes, Telegram, API REST, CLI u otro canal solo pueden tocar el kernel mediante el puerto conversacional autorizado.

No deben contener logica clinica soberana.

---

# 5. Flujo obligatorio

Cuando entra un problema + archivo:

```text
1. El canal recibe mensaje y archivo.
2. Se crea InputRecord.
3. El archivo se registra como EvidenceRecord bruto con hash.
4. Un parser autorizado extrae StructuredEvidence.
5. El puerto conversacional invoca el servicio/kernel.
6. El servicio ejecuta el pipeline deterministico.
7. Se crea PipelineRunRecord.
8. El pipeline produce artefacto clinico-operacional.
9. El formateador produce respuesta.
10. Se crea ResponseRecord enlazado al run_id.
11. El canal entrega la respuesta.
```

El Excel nunca debe entrar como texto libre para que un LLM lo analice soberanamente.

---

# 6. Contratos conceptuales minimos

## 6.1 InputRecord

```yaml
input_id: string
trace_id: string
tenant_id: string
channel: string
received_at: datetime
text_hash: string
raw_text_redacted: string | null
evidence_ids: list[string]
actor: string
status: RECEIVED | REJECTED
```

Reglas:

```text
- Debe existir antes de cualquier analisis.
- Debe incluir tenant_id.
- Debe enlazar evidencias recibidas.
```

---

## 6.2 EvidenceRecord

```yaml
evidence_id: string
trace_id: string
tenant_id: string
source: xlsx_upload | csv_upload | pdf_upload | manual_entry | unknown
file_name: string | null
source_sha256: string
received_at: datetime
parser_name: string | null
parser_version: string | null
schema_version: string | null
extraction_status: OK | PARTIAL | FAILED | NOT_APPLICABLE
row_count: int | null
column_count: int | null
computed_variables: dict[string, number]
metadata: dict
```

Reglas:

```text
- Ninguna variable extraida puede existir sin source_sha256.
- El parser debe ser identificable.
- La evidencia estructurada no diagnostica.
- La evidencia estructurada solo transporta hechos documentales o variables computadas.
```

---

## 6.3 PipelineRunRecord

```yaml
run_id: string
trace_id: string
tenant_id: string
input_id: string
pipeline_name: string
pipeline_version: string
pipeline_module: string
entrypoint: string
service_name: string
started_at: datetime
completed_at: datetime | null
input_hash: string
evidence_ids: list[string]
steps_executed: list[string]
output_artifact_id: string | null
output_hash: string | null
status: STARTED | COMPLETED | BLOCKED | FAILED
error_code: string | null
error_message: string | null
```

Reglas:

```text
- Debe existir para toda respuesta clinico-operacional.
- Debe indicar pipeline_name y pipeline_version.
- Debe declarar steps_executed.
- Debe enlazar input_id y evidence_ids.
- Debe producir output_hash si termina COMPLETED.
```

---

## 6.4 ResponseRecord

```yaml
response_id: string
trace_id: string
tenant_id: string
run_id: string
channel: string
response_hash: string
message_redacted: string | null
created_at: datetime
status: FORMATTED | DELIVERED | FAILED
```

Reglas:

```text
- No puede existir ResponseRecord clinico-operacional sin run_id.
- El hash de respuesta debe permitir verificar que el mensaje entregado coincide con el output registrado.
```

---

# 7. TraceEvent

Ademas de los records principales, el sistema debe poder emitir eventos append-only.

```yaml
trace_event_id: string
trace_id: string
tenant_id: string
event_type: string
actor: string
created_at: datetime
payload_hash: string
metadata: dict
```

Eventos minimos:

```text
RECEIVED
EVIDENCE_REGISTERED
EVIDENCE_EXTRACTED
PIPELINE_STARTED
PIPELINE_COMPLETED
RESPONSE_FORMATTED
DELIVERED
BLOCKED
FAILED
```

Regla:

```text
La auditoria debe poder reconstruir el flujo completo a partir del trace_id.
```

---

# 8. Estados verificables

Estados minimos del flujo:

```text
RECEIVED
-> EVIDENCE_REGISTERED
-> EVIDENCE_EXTRACTED
-> PIPELINE_STARTED
-> PIPELINE_COMPLETED
-> RESPONSE_FORMATTED
-> DELIVERED
```

Estados alternativos:

```text
BLOCKED_MISSING_EVIDENCE
FAILED_EXTRACTION
FAILED_PIPELINE
FAILED_RESPONSE_FORMATTING
UNSUPPORTED_INPUT
```

---

# 9. Criterio anti-bypass

Debe ser imposible que un adaptador externo entregue una respuesta clinico-operacional sin haber recibido un output del kernel.

Patron prohibido:

```text
mensaje del usuario + Excel
-> prompt LLM
-> respuesta diagnostica
```

Patron permitido:

```text
mensaje del usuario + Excel
-> InputRecord
-> EvidenceRecord
-> StructuredEvidence
-> ClinicalConversationalPort
-> InitialLaboratoryAnamnesisService
-> AdmissionPipelineV1 / pipeline autorizado
-> PipelineRunRecord
-> ResponseRecord
-> respuesta al usuario
```

---

# 10. Reglas para Excel y documentos

Un Excel subido por el usuario debe tratarse como evidencia documental.

Reglas:

```text
- El archivo se hashea antes de parsear.
- El parser registra version.
- Las tablas extraidas conservan hoja, columnas y filas o resumen estructurado.
- Las variables computadas declaran origen.
- El LLM no recibe el archivo completo para diagnosticar.
- Si hay ambiguedad de columnas, el sistema puede pedir aclaracion o usar un mapper controlado.
- Si falta evidencia critica, el estado debe ser BLOCKED_MISSING_EVIDENCE o hipotesis_abierta.
```

---

# 11. Versionado obligatorio

Toda ejecucion debe registrar:

```text
- pipeline_name;
- pipeline_version;
- pipeline_module;
- service_name;
- parser_name;
- parser_version;
- schema_version;
- catalog_version cuando aplique;
- formula_catalog_version cuando aplique.
```

Esto permite responder:

```text
"Con que version del sistema se produjo esta respuesta?"
```

---

# 12. Tests obligatorios

El boundary no queda cerrado hasta que existan tests.

Tests minimos:

```text
test_clinical_response_requires_pipeline_run_id
test_pipeline_run_records_admission_pipeline_v1
test_excel_upload_creates_evidence_record_with_hash
test_structured_evidence_is_linked_to_pipeline_run
test_response_record_links_to_run_id
test_adapter_cannot_emit_clinical_response_without_kernel_output
test_llm_is_not_called_for_diagnostic_decision
test_output_hash_matches_response_record
```

Criterio fuerte:

```text
Si no se ejecuto un pipeline autorizado, no puede existir respuesta clinico-operacional valida.
```

---

# 13. Auditoria esperada

Dado un mensaje y un archivo, debe poder comprobarse:

```text
1. que input entro;
2. cuando entro;
3. de que tenant;
4. que archivo se recibio;
5. cual fue el hash del archivo;
6. que parser lo proceso;
7. que variables se extrajeron;
8. que pipeline se ejecuto;
9. que version del pipeline se uso;
10. que pasos corrieron;
11. que evidencia fue usada;
12. que evidencia falto;
13. que artefacto produjo el pipeline;
14. que respuesta se formateo;
15. que respuesta se entrego;
16. que hashes enlazan todo el flujo.
```

Si esto no puede demostrarse, la respuesta debe ser considerada no auditada.

---

# 14. Relacion con PymIA actual

Piezas existentes que este boundary debe endurecer:

```text
pymia.interfaces.conversational_port.ClinicalConversationalPort
pymia.interfaces.conversational_port.ConversationalInput
pymia.interfaces.conversational_port.ConversationalOutput
pymia.contracts.evidence_v1.StructuredEvidence
pymia.pipeline.admission.v1.pipeline.AdmissionPipelineV1
pymia.services.initial_laboratory_anamnesis_service.InitialLaboratoryAnamnesisService
pymia.pipeline.admission.v1.response_formatter.AdmissionResponseFormatterV1
```

La direccion es correcta, pero falta convertir la garantia arquitectonica en evidencia de ejecucion.

---

# 15. Criterio de salida

Este boundary se considera implementado cuando:

```text
- existe contrato Pydantic para PipelineRunRecord;
- ConversationalOutput incluye run_id o referencia equivalente;
- todo output clinico-operacional esta enlazado a un PipelineRunRecord;
- la evidencia documental esta enlazada al run;
- los tests anti-bypass pasan;
- el audit log permite reconstruir trace_id completo.
```

---

# 16. Frase rectora

```text
PymIA no debe pedir confianza en que uso el pipeline.
Debe poder demostrarlo.
```
