# Incidente de integración Hermes ↔ PymIA a mitad de construcción

## Estado

Documento operativo de incidente.

Este documento registra una situación de integración incompleta entre Hermes y PymIA detectada durante el intento de cerrar la frontera:

```text
Hermes conversa.
PymIA computa.
El pipeline demuestra.
```

No es una propuesta conceptual. Es el estado real del problema a mitad de construcción.

---

# 1. Problema observado

Hermes está actuando como analista cuando debería operar como conducto conversacional hacia PymIA.

Se observaron salidas donde Hermes:

```text
- declara que PymIA devolvió output crudo;
- continúa el análisis por su cuenta;
- reestructura el resultado;
- emite veredictos;
- calcula márgenes, break-even, pérdidas y cadenas causales;
- usa o sugiere uso de scripts temporales /tmp/*.py, terminal, openpyxl u OCR fuera del pipeline.
```

Esto rompe la frontera operativa esperada.

---

# 2. Flujo incorrecto detectado

El flujo observado se parece a:

```text
Usuario / Telegram
-> Hermes recibe problema + archivo
-> Hermes parsea o analiza evidencia con herramientas propias
-> Hermes escribe o ejecuta scripts ad hoc
-> Hermes interpreta resultados
-> Hermes responde al usuario
```

Este flujo es no conforme para PymIA.

---

# 3. Flujo objetivo

El flujo correcto debe ser:

```text
Usuario / Telegram
-> Hermes recibe problema + archivo
-> Hermes registra intake
-> Hermes enruta evidencia
-> PymIA recibe StructuredEvidence
-> PymIA ejecuta pipeline determinístico / capability autorizada
-> PymIA produce output clínico-operacional trazado
-> Hermes devuelve output de PymIA sin reinterpretar
```

Hermes debe ser conducto, no analista.

---

# 4. Estado técnico real al momento del incidente

## 4.1 Piezas existentes

Existen piezas correctas en el repo:

```text
pymia.hermes.adapter.HermesAdapter
pymia.interfaces.conversational_port.ClinicalConversationalPort
pymia.interfaces.conversational_port.ConversationalInput
pymia.contracts.evidence_v1.StructuredEvidence
pymia.services.initial_laboratory_anamnesis_service.InitialLaboratoryAnamnesisService
pymia.pipeline.admission.v1.pipeline.AdmissionPipelineV1
```

También existe:

```text
conversa-engine/evidence_router.py
```

Pero `evidence_router.py` actualmente enruta evidencia; no constituye por sí mismo un parser clínico-operacional completo ni una capability de análisis.

---

## 4.2 Brecha en HermesAdapter

Durante el trabajo se modificó `pymia/hermes/adapter.py` para avanzar hacia trazabilidad y evidencia estructurada.

Estado buscado del adapter:

```text
HermesInput.evidence
-> ConversationalInput.evidence
-> ClinicalConversationalPort
-> PymIA kernel
```

Cambios intentados / parciales:

```text
- agregar StructuredEvidence a HermesInput;
- exigir run_id / trace_id / hashes en HermesOutput status="ok";
- generar run_id, trace_id, input_hash y output_hash;
- pasar evidence desde HermesInput hacia ConversationalInput.
```

Punto crítico que debe validarse en el archivo actual:

```python
clinical_input = ConversationalInput(
    tenant_id=hermes_input.tenant_id,
    channel=hermes_input.channel,
    text=hermes_input.message_text,
    evidence=hermes_input.evidence,
)
```

Si esa línea no está presente, Hermes recibe evidencia pero no la delega al kernel.

---

## 4.3 Estado de validación

La herramienta MCP/SmartBridge permitió algunas operaciones:

```text
list_tree: OK
read_text_file: OK en varias llamadas
git_status: OK
run_pymia_demo: OK antes del bloqueo
write_text_file: OK para adapter.py
```

Pero hubo bloqueos o cuelgues en:

```text
patch_text_file: inestable / se colgó varias veces
run_pytest: bloqueado
run_conversa_main: bloqueado
git_pull: bloqueado
lectura/búsqueda post-escritura: bloqueada temporalmente
```

Por eso el estado post-escritura requiere validación posterior.

---

# 5. No conformidad principal

Hermes no debe completar análisis clínico-operacional si PymIA devuelve output incompleto o crudo.

Patrón prohibido:

```text
PymIA devolvió output crudo.
Ahora lo analizo yo.
```

Patrón correcto:

```text
PymIA devolvió output insuficiente para análisis final.
Hermes detiene la respuesta clínica y solicita ejecutar capability autorizada o devuelve PIPELINE_NOT_AVAILABLE.
```

---

# 6. Reglas operativas para Hermes

Hermes NO puede:

```text
- diagnosticar;
- calcular margen, break-even, pérdida, OEE, scrap, stock o correlaciones por cuenta propia;
- escribir scripts temporales de análisis;
- ejecutar terminal para producir hallazgos;
- reinterpretar output de PymIA;
- agregar cadena causal propia;
- emitir veredictos sin run_id / trace_id / evidence_id / pipeline_version;
- convertir documentos en texto narrativo para saltar StructuredEvidence.
```

Hermes SÍ puede:

```text
- recibir mensajes;
- recibir archivos;
- registrar intake;
- llamar al adapter o endpoint PymIA autorizado;
- transmitir preguntas de PymIA;
- devolver output de PymIA sin agregar interpretación soberana;
- preservar metadata para auditoría.
```

---

# 7. Trabajo pendiente inmediato

## 7.1 Validar adapter.py

Validar que `pymia/hermes/adapter.py` contenga:

```text
HermesInput.evidence: StructuredEvidence | None
ConversationalInput(..., evidence=hermes_input.evidence)
HermesOutput status="ok" exige run_id, trace_id, pipeline_name, pipeline_version, input_hash, output_hash
```

## 7.2 Ejecutar tests

Correr como mínimo:

```bash
pytest tests/hermes/test_hermes_adapter.py
pytest tests/test_structured_evidence_boundary.py
```

Si el runner MCP no lo permite, ejecutar localmente en la terminal del repo.

## 7.3 Agregar tests anti-bypass

Tests requeridos:

```text
test_hermes_input_accepts_structured_evidence
test_hermes_adapter_passes_evidence_to_clinical_port
test_hermes_clinical_output_requires_trace
test_hermes_output_contains_run_id_trace_id_hashes
test_hermes_does_not_modify_kernel_reply_text
test_no_clinical_response_without_kernel_output
```

## 7.4 Cortar segunda pasada de conversa-engine

Revisar `conversa-engine/main.py`.

Riesgo detectado:

```text
run_message()
-> _pymia_reply()
-> _catalog_contrast()
-> concatena contraste propio
```

Ese contraste posterior puede convertirse en una segunda capa analítica fuera del kernel.

Debe decidirse si se elimina, se mueve al kernel, o se convierte en capability PymIA trazada.

## 7.5 Exponer evidencia por CLI / canal

`conversa-engine/main.py` debe aceptar evidencia documental sin analizarla soberanamente.

Objetivo:

```bash
python main.py "síntoma del cliente" --evidence /ruta/archivo.xlsx
```

Pero ese flag debe:

```text
- registrar evidencia;
- enrutarla;
- construir StructuredEvidence o referencia autorizada;
- delegar a PymIA;
- no ejecutar análisis Hermes ad hoc.
```

---

# 8. Criterio de aceptación

La integración se considera saneada cuando se pueda demostrar:

```text
1. Hermes recibe texto + evidencia.
2. Hermes no escribe scripts temporales.
3. Hermes no ejecuta terminal para diagnosticar.
4. Hermes delega evidencia como StructuredEvidence.
5. PymIA produce la salida clínica.
6. La salida tiene run_id, trace_id, pipeline_name, pipeline_version, input_hash y output_hash.
7. Hermes devuelve output de PymIA sin reinterpretación.
8. Tests anti-bypass pasan.
```

---

# 9. Estado Git conocido durante el incidente

Se observó `git status` con modificaciones y archivos no trackeados existentes.

Archivo clave modificado:

```text
pymia/hermes/adapter.py
```

Archivo de documentación creado durante el trabajo:

```text
docs/arquitectura/pipeline-traceability-boundary-v1.md
```

También existían otros archivos modificados/no trackeados previos que no deben mezclarse sin decisión explícita.

Regla:

```text
No commitear archivos sueltos ni migraciones no relacionadas sin autorización explícita.
```

---

# 10. Conclusión

El problema no está resuelto todavía.

Sí hay avance local hacia trazabilidad y delegación de evidencia, pero falta validación y tests.

La prioridad no es agregar más documentación. La prioridad es cerrar la integración ejecutable:

```text
HermesInput.evidence
-> ConversationalInput.evidence
-> PymIA kernel
-> HermesOutput con traza obligatoria
-> tests anti-bypass
```

Hasta que eso pase, Hermes debe considerarse parcialmente fuera de frontera para análisis clínico-operacional.
