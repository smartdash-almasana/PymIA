# Pipeline funcional de PymIA — nodos existentes

## Estado

Inventario funcional basado en archivos existentes del repo.

Este documento lista solo nodos observados físicamente en código o documentación operativa del repositorio. No incluye componentes hipotéticos, futuros ni inferidos por conversación.

---

## Pipeline funcional actual

```text
CLI texto-only / main.py
→ registro de intake textual
→ HermesAdapter
→ ClinicalConversationalPort
→ InitialLaboratoryAnamnesisService
→ AdmissionPipelineV1
→ heurísticas determinísticas de admisión
→ DDIArtifact / AdmissionState
→ AdmissionResponseFormatterV1
→ AnamnesisOriginaria / LaboratorioInicialContrato
→ HermesOutput con trazabilidad mínima
→ contraste adicional con catálogo local de síntomas/patologías
→ respuesta final por main.py
```

---

## Nodos y descripción de una línea

| # | Nodo | Archivo | Descripción |
|---|------|---------|-------------|
| 1 | `conversa-engine/main.py` | `conversa-engine/main.py` | Entry point CLI actual: recibe texto libre, registra intake, llama a PymIA vía `HermesAdapter` y agrega contraste de catálogo si aplica. |
| 2 | `_register_text_intake` | `conversa-engine/main.py` | Persiste el evento textual entrante en el repositorio de intake de conversación. |
| 3 | `RawInboundEvent.text` | `conversa-engine/inbound_event.py` | Representa el mensaje textual crudo recibido antes de entrar al kernel conversacional. |
| 4 | `DocumentIntakeRepository` | `conversa-engine/intake_repository.py` | Carga y guarda el estado de intake por sesión/tenant en `.intake_state` o cache local. |
| 5 | `HermesInput` | `pymia/hermes/adapter.py` | Contrato de entrada desde Hermes hacia PymIA con `tenant_id`, `channel`, `message_text`, `metadata` y evidencia estructurada opcional. |
| 6 | `HermesAdapter.handle` | `pymia/hermes/adapter.py` | Traduce `HermesInput` a `ConversationalInput`, invoca el puerto clínico y devuelve `HermesOutput` sin interpretar el kernel. |
| 7 | `ConversationalInput` | `pymia/interfaces/conversational_port.py` | Contrato público de entrada al kernel conversacional: `tenant_id`, `channel`, `text` y `StructuredEvidence` opcional. |
| 8 | `ClinicalConversationalPort.handle` | `pymia/interfaces/conversational_port.py` | Única superficie pública del kernel conversacional; delega el procesamiento a `InitialLaboratoryAnamnesisService`. |
| 9 | `InitialLaboratoryAnamnesisService.process` | `pymia/services/initial_laboratory_anamnesis_service.py` | Servicio de primer tiempo lógico: detecta señal inicial, abre hipótesis, pide evidencia y construye anamnesis/laboratorio. |
| 10 | `AdmissionPipelineV1.run` | `pymia/pipeline/admission/v1/pipeline.py` | Pipeline determinístico de admisión que transforma un claim en `SymptomNode`, hipótesis puntuadas, evidencia requerida y estado de admisión. |
| 11 | `get_hypotheses_for_claim` | `pymia/pipeline/admission/v1/heuristics.py` | Heurísticas determinísticas que mapean palabras clave del relato a hipótesis de rentabilidad/caja o inventario y evidencia requerida. |
| 12 | `DDIArtifact` | `pymia/contracts/admission_v1.py` | Artefacto estructurado que agrupa síntomas, hipótesis, hechos, tensiones e hipótesis primaria. |
| 13 | `AdmissionState` | `pymia/contracts/admission_v1.py` | Estado epistemológico de admisión: `new`, `symptoms_captured`, `hypotheses_generated`, `evidence_required`, `tensions_found` o `ready_for_diagnosis`. |
| 14 | `AdmissionResponseFormatterV1` | `pymia/pipeline/admission/v1/response_formatter.py` | Convierte un `DDIArtifact` con hipótesis en respuesta natural de primer contacto y pedido de evidencia. |
| 15 | `StructuredEvidence` | `pymia/contracts/evidence_v1.py` | Contrato de evidencia documental estructurada con tablas, variables computadas y metadata; transporta estructura, no diagnostica. |
| 16 | `_filter_requested_documents_by_evidence` | `pymia/services/initial_laboratory_anamnesis_service.py` | Reduce documentos solicitados cuando la evidencia estructurada ya trae variables computadas de ventas o costos. |
| 17 | `AnamnesisOriginaria` | `pymia/services/initial_laboratory_anamnesis_service.py` | Contrato de anamnesis inicial con frases textuales, dolores, hipótesis, documentos pedidos y estado conversacional. |
| 18 | `LaboratorioInicialContrato` | `pymia/services/initial_laboratory_anamnesis_service.py` | Contrato de laboratorio inicial con hipótesis a contrastar, evidencia requerida, capability, campos esperados y límite actual. |
| 19 | `ConversationalOutput` | `pymia/interfaces/conversational_port.py` | Salida del puerto clínico con `status`, `mode`, `message`, `anamnesis` y `laboratorio`. |
| 20 | `HermesOutput` | `pymia/hermes/adapter.py` | Salida en vocabulario Hermes con `reply_text`, payload clínico y trazabilidad mínima para respuestas `ok`. |
| 21 | `HermesPayload` | `pymia/hermes/adapter.py` | Payload de solo lectura con anamnesis, laboratorio, metadata original, run/trace IDs, pipeline e hashes. |
| 22 | `match_symptoms_from_owner_message` | `conversa-engine/symptom_pathology_catalog.py` | Busca coincidencias del mensaje contra el catálogo local de síntomas/patologías. |
| 23 | `SymptomCatalogEntry` | `conversa-engine/symptom_pathology_catalog.py` | Entrada de catálogo local con síntoma, patologías candidatas, skill candidata, variables, evidencia, preguntas y criterios de bloqueo. |
| 24 | `_catalog_contrast` | `conversa-engine/main.py` | Agrega al output un contraste local con síntoma operativo, patologías candidatas, variables, evidencia y pregunta mayéutica. |

---

## Observaciones funcionales

### Lo que sí existe

```text
- entrada CLI texto-only;
- registro básico de intake textual;
- adapter Hermes ↔ puerto clínico;
- puerto conversacional público;
- servicio de anamnesis/laboratorio inicial;
- pipeline determinístico de admisión;
- heurísticas para rentabilidad/caja e inventario;
- contratos Pydantic de admisión;
- contrato de evidencia estructurada;
- formatter determinístico;
- catálogo local de síntoma/patologías para contraste;
- trazabilidad mínima en HermesOutput cuando status=ok.
```

### Lo que no forma parte del pipeline funcional actual

```text
- --register-evidence;
- --create-case;
- --execute;
- TaskSpec;
- TaskEvidence / ExecutionEvidence;
- BypassDetector;
- PASS / PARTIAL / BLOCKED;
- MetricsCollector;
- SessionBootstrap;
- provider fallback;
- ejecución determinística de skills económicas;
- diagnóstico cuantitativo final.
```

---

## Lectura arquitectónica

El pipeline funcional actual llega hasta:

```text
admisión + hipótesis inicial + pedido de evidencia + trazabilidad mínima.
```

Todavía no llega a:

```text
ejecución de skill determinística + hallazgo cuantificado + estado PASS/PARTIAL/BLOCKED.
```

Por lo tanto, el kernel existente es un kernel de admisión conversacional, no todavía un kernel diagnóstico-operacional completo.

---

## Qué le falta al pipeline funcional actual

El pipeline actual llega hasta admisión, hipótesis inicial y pedido de evidencia. Para convertirse en kernel diagnóstico-operacional le faltan nodos reales entre la evidencia recibida y el hallazgo cuantificado.

### Faltantes críticos

| # | Faltante | Qué debería hacer | Por qué importa |
|---|----------|-------------------|-----------------|
| 1 | `CLI fail-closed` | Rechazar flags desconocidos y comandos no implementados sin tratarlos como texto libre. | Evita que Hermes o cualquier caller entre por caminos ambiguos. |
| 2 | `registro de evidencia documental ejecutable` | Recibir archivo/evidencia y devolver un identificador trazable. | Hoy existe `StructuredEvidence`, pero no un flujo CLI operativo para registrarla. |
| 3 | `validador de suficiencia de evidencia` | Determinar si la evidencia alcanza, falta o es contradictoria. | Sin esto, Hermes o el servicio conversacional terminan decidiendo informalmente. |
| 4 | `estado BLOCKED / PARTIAL / PASS` | Expresar resultado operativo de forma cerrada. | Hoy existen `ok/no_signal/error`, pero no estados diagnósticos de ejecución. |
| 5 | `selector de skill ejecutable` | Elegir una skill real según hipótesis + evidencia disponible. | Hoy hay hipótesis y capabilities textuales, no ejecución de skill determinística. |
| 6 | `skill determinística mínima` | Ejecutar un cálculo/contraste reproducible sobre evidencia estructurada. | Sin skill no hay kernel diagnóstico, solo admisión. |
| 7 | `contrato de salida diagnóstica` | Devolver hallazgo, límite, evidencia usada, cálculo y trazabilidad. | Evita respuestas narrativas no auditables. |
| 8 | `ExecutionEvidence mínima` | Registrar comando/ruta, input/output hash, estado, duración y bloqueo. | Permite auditar la ejecución sin depender de memoria conversacional. |
| 9 | `tests anti-bypass` | Probar que no se analiza por fuera, no se reescribe output y no se salta evidencia. | Convierte la política en enforcement verificable. |
| 10 | `conexión evidencia → pipeline` | Usar `StructuredEvidence` dentro de la ruta real, no solo como contrato disponible. | Cierra el hueco entre archivo recibido y razonamiento determinístico. |

---

## Hueco principal

```text
Hoy existe: texto → admisión → hipótesis → evidencia requerida.
Falta: evidencia → validación → skill → hallazgo → estado → trazabilidad.
```

Ese es el corte exacto entre el kernel existente y el kernel mínimo viable.

---

## Prioridad recomendada

No empezar por métricas, fallback de providers ni bootstrap.

Orden correcto:

```text
1. CLI fail-closed.
2. Conectar StructuredEvidence a una ruta ejecutable mínima.
3. Definir suficiencia de evidencia.
4. Implementar BLOCKED / PARTIAL / PASS.
5. Agregar una skill determinística pequeña.
6. Agregar contrato de salida diagnóstica.
7. Agregar tests anti-bypass.
```

---

## Regla de no invención

```text
Si un nodo no existe en archivo, contrato, test o ruta ejecutable, no se lista como pipeline funcional.
```
