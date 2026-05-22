# Registro de Decisión de Arquitectura (ADR)
## ADR-006: Integración del Pipeline Documental Mediante TenantClinicalContext y EvidenceBundle en el Clinical Port

* **Estado**: ACEPTADO
* **Fecha**: 2026-05-22
* **Dueño Conceptual**: Conversational Boundary / Kernel PymIA

---

## 1. Contexto
Anteriormente, el traspaso de evidencia desde el adaptador de archivos de Hermes hacia el kernel de PymIA se realizaba de forma indirecta, sin contexto o mezclando estados de parseo de adjuntos y errores técnicos dentro de la entidad `StructuredEvidence` o en diccionarios de metadata genéricos y opacos. Esto ocasionaba que si un adjunto fallaba su parseo, el kernel de PymIA siguiera asumiendo que los datos eran legibles o hiciera fallbacks textuales silenciosos incorrectos, impidiendo reportar fallas reales al dueño en el chat. Además, la interpretación de planillas se realizaba a ciegas sin considerar el sector de actividad, el historial o las sospechas diagnósticas previas del tenant.

## 2. Decisión
Se establece de forma obligatoria la inyección de contexto y la integración estricta de la evidencia en el Clinical Port de PymIA:

1. **Inyección Obligatoria de `TenantClinicalContext`**: 
   * `TenantClinicalContext` se fija como el insumo de entrada **obligatorio** del motor documental local.
   * La historia clínica inicial de la PyME deja de ser tratada como simple texto libre. Se estructura bajo el modelo formal de datos del tenant (con sector industrial, hipótesis activas, etc.).
   * **Queda terminantemente prohibido interpretar o perfilar cualquier planilla Excel o CSV sin contar con un contexto clínico mínimo validado.**
   * El `TenantClinicalContext` alimenta directamente de manera interactiva a `PymeColumnOntology` y al `BusinessSchemaInferenceEngine` para dotar de pesos lógicos y probabilísticos a la inferencia de columnas.

2. **Integración Mediante el Contrato Formal `EvidenceBundle`**:
   * **Separación de Responsabilidades**: Se separa por completo el ciclo de vida y estado de procesamiento físico del adjunto (`AttachmentProcessingStatus`) de la evidencia estructurada de negocio (`StructuredEvidence`).
   * El canal conversacional del Clinical Port de PymIA (`ClinicalConversationalPort.handle()`) recibirá un `EvidenceBundle` formal. Este paquete contendrá:
     * La evidencia del dominio normalizada (`EvidenceTable`).
     * El esquema semántico auditado e inferido con éxito (`SemanticSchema`).
     * El estado de procesamiento y ciclo de vida de los adjuntos (`AttachmentProcessingStatus`).
   * El cálculo de benchmarks clínicos u operacionales de diagnóstico se bloqueará de forma absoluta si falta el contexto mínimo o si la confianza del esquema cae por debajo de `0.75`.

## 3. Consecuencias
* **Positivas**:
  * Consistencia epistemológica absoluta: PymIA nunca diagnostica sobre datos corruptos, sin contexto o con baja confianza de traducción.
  * Trazabilidad física y lógica auditable de cada archivo desde su recepción hasta su inyección final.
  * Mensajes informativos fidedignos y transparentes devueltos al usuario.
* **Negativas / Desafíos**:
  * Requiere adaptar el puerto conversacional de entrada de PymIA para operar con contratos ricos en lugar de diccionarios planos.

## 4. Qué Queda Prohibido
* **PROHIBIDO** interpretar un Excel o CSV "a ciegas" sin un `TenantClinicalContext` previo inyectado.
* **PROHIBIDO** mezclar estados de parseo físico o excepciones de red dentro de la estructura de dominio `StructuredEvidence`.
* **PROHIBIDO** almacenar banderas de ciclo de vida del adjunto en metadata opaca o diccionarios planos de formato string.
* **PROHIBIDO** admitir en el kernel clínico evidencia con una confianza de esquema menor al umbral mínimo tolerado (0.75) sin disparar la FIO correspondientemente.

## 5. Trazabilidad

### Documentos Relacionados
* [AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md](file:///opt/PymIA/docs/AUDITORIA_SCHEMA_INFERENCE_RUNTIME_V1.md) — Blueprint de la capa de inteligencia documental.
* [DOCUMENTATION_INDEX.md](file:///opt/PymIA/docs/DOCUMENTATION_INDEX.md) — Índice canónico de documentación de PymIA.
* [TENANT_CLINICAL_CONTEXT_AND_DOCUMENT_INTELLIGENCE_DESIGN.md](file:///opt/PymIA/docs/transient-design/TENANT_CLINICAL_CONTEXT_AND_DOCUMENT_INTELLIGENCE_DESIGN.md) — Diseño transitorio de contexto clínico del tenant.

### Código Relacionado
* `pymia/interfaces/conversational_port.py` (`ClinicalConversationalPort`)
* `pymia/contracts/evidence_v1.py` (Representación de la evidencia en el dominio)
* `conversa-engine/document_intake.py` (Inbound pipeline)
