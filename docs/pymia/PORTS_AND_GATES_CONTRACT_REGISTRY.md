# PymIA — Ports and Gates Contract Registry

Fecha: 2026-06-07
Estado: inventario de diseño operativo
Alcance: sistematizar enchufes, entradas, salidas y gates del pipeline PymIA / SmartPyme.

---

## 1. Propósito

Este documento define un modelo mínimo para que PymIA no crezca como piezas sueltas.

El problema que resuelve:

```text
módulos útiles sin enchufes explícitos
→ integración frágil
→ agentes improvisan
→ deriva operacional
```

El objetivo:

```text
cada fase del pipeline debe declarar qué recibe, qué devuelve, quién la produce, quién la consume, qué gate la valida y qué test la protege.
```

---

## 2. Regla madre

```text
Ningún módulo relevante debe conectarse a otro por intuición.
Debe conectarse por puerto o por gate.
```

Un puerto define intercambio.
Un gate define autorización de avance.

---

## 3. Diferencia entre puerto y gate

### Puerto

Un puerto es un enchufe de datos.

Responde:

```text
qué entra
qué sale
con qué forma
quién lo produce
quién lo consume
```

### Gate

Un gate es una compuerta de avance.

Responde:

```text
puede avanzar
no puede avanzar
qué falta
qué está bloqueado
qué evidencia lo justifica
```

---

## 4. Estructura obligatoria de cada puerto

Cada puerto debe declarar:

```yaml
port_id:
nombre_humano:
fase_pipeline:
input_model:
output_model:
productores:
consumidores:
validadores:
tests:
estados:
errores:
no_puede:
nivel_lectura:
```

Estados de lectura permitidos:

```text
LEIDO_PROFUNDO
LEIDO_PARCIAL
IDENTIFICADO_POR_ESTRUCTURA
IDENTIFICADO_POR_FIRMAS
REFERENCIADO_POR_TESTS
```

---

## 5. Puertos base del pipeline

### 5.1 OWNER_INPUT_PORT

```yaml
port_id: OWNER_INPUT_PORT
fase_pipeline: relato / input
recibe:
  - texto_usuario
  - chat_id
  - tenant_id opcional
  - contexto_previo opcional
devuelve:
  - dolor_declarado
  - objetivo_declarado
  - periodo_si_existe
  - datos_mencionados
  - decision_buscada
productores:
  - pymia/telegram_bot_runtime.py
  - pymia/interfaces/conversational_port.py
consumidores:
  - pymia/smartpyme/anamnesis_fsm.py
  - pymia/smartpyme/anamnesis_fsm_integration.py
  - pymia/smartpyme/intake.py
gates:
  - FIRST_CONTACT_GATE
no_puede:
  - diagnosticar
  - pedir archivos antes de ficha si el contrato vigente exige anamnesis
  - prometer resultado
```

### 5.2 CASE_CONTEXT_PORT

```yaml
port_id: CASE_CONTEXT_PORT
fase_pipeline: ficha / caso
recibe:
  - ficha_pyme
  - dolor_declarado
  - taxonomia
  - contexto_progresivo
devuelve:
  - case_context
  - business_profile
  - operational_hypothesis
  - evidence_requests iniciales
productores:
  - pymia/smartpyme/anamnesis_fsm.py
  - pymia/smartpyme/anamnesis_fsm_integration.py
  - pymia/smartpyme/intake.py
consumidores:
  - pymia/smartpyme/post_ficha_evidence_gate.py
  - pymia/smartpyme/readiness.py
  - pymia/audit_result/evidence_requirement_matcher.py
gates:
  - FICHA_COMPLETENESS_GATE
no_puede:
  - ejecutar cálculo
  - afirmar patología confirmada
```

### 5.3 DOCUMENT_INPUT_PORT

```yaml
port_id: DOCUMENT_INPUT_PORT
fase_pipeline: recepción documental
recibe:
  - file_path
  - file_name
  - tenant_id
  - chat_id/case_id
devuelve:
  - document_received
  - storage_path
  - file_metadata básica
productores:
  - pymia/telegram_document_handler.py
  - tools/document_ingestion.py
consumidores:
  - DOCUMENT_PROFILE_PORT
  - post_ficha_evidence_gate.py
gates:
  - FILE_ACCEPTANCE_GATE
no_puede:
  - diagnosticar
  - suponer contenido útil sin parseo
```

### 5.4 DOCUMENT_PROFILE_PORT

```yaml
port_id: DOCUMENT_PROFILE_PORT
fase_pipeline: perfilado documental
recibe:
  - file_path
  - tenant_id
  - case_context opcional
devuelve:
  - document_id
  - sheets
  - columns
  - row_counts
  - inferred_types
  - warnings
  - parse_status
productores:
  - tools/document_ingestion.py
  - tools/excel_evidence.py
  - pymia/smartpyme/xlsx_document_metadata_adapter.py
  - pymia/smartpyme/parsed_document_metadata.py
consumidores:
  - SEMANTIC_MAPPING_PORT
  - EVIDENCE_STATUS_PORT
gates:
  - PARSE_QUALITY_GATE
no_puede:
  - calcular margen final
  - confirmar patología
  - inventar columnas
```

### 5.5 SEMANTIC_MAPPING_PORT

```yaml
port_id: SEMANTIC_MAPPING_PORT
fase_pipeline: semántica
recibe:
  - document_profile
  - columnas
  - muestras_de_valores
  - case_context
devuelve:
  - variables_candidatas
  - confidence_by_field
  - required_fields_detected
  - missing_required_fields
  - ambiguous_fields
productores:
  - pymia/smartpyme/semantic_field_resolution.py
  - pymia/document_intelligence/inference/schema_inference_engine.py
  - SmartPyme/app/catalogs/column_mapping_catalog.json
consumidores:
  - EVIDENCE_STATUS_PORT
  - FORMULA_EXECUTION_PORT
gates:
  - SEMANTIC_CONFIDENCE_GATE
no_puede:
  - diagnosticar
  - convertir baja confianza en certeza
```

### 5.6 EVIDENCE_STATUS_PORT

```yaml
port_id: EVIDENCE_STATUS_PORT
fase_pipeline: evidencia / suficiencia
recibe:
  - evidence_requests
  - evidence_records
  - variables_detectadas
  - formula_catalog
  - pathology_catalog
devuelve:
  - available_evidence
  - missing_evidence
  - matched_evidence_ids
  - status: READY | NEEDS_EVIDENCE | BLOCKED | PARTIAL
  - questions_for_owner
productores:
  - pymia/smartpyme/evidence_gate.py
  - pymia/smartpyme/readiness.py
  - pymia/smartpyme/post_ficha_evidence_gate.py
  - pymia/audit_result/evidence_requirement_matcher.py
consumidores:
  - PATHOLOGY_SELECTION_PORT
  - FORMULA_EXECUTION_PORT
  - CHANNEL_OUTPUT_PORT
gates:
  - EVIDENCE_SUFFICIENCY_GATE
no_puede:
  - ejecutar fórmula si faltan datos obligatorios
  - ocultar faltantes al dueño/desarrollador
```

### 5.7 PATHOLOGY_SELECTION_PORT

```yaml
port_id: PATHOLOGY_SELECTION_PORT
fase_pipeline: selección clínica-operativa
recibe:
  - dolor_declarado
  - taxonomia
  - case_context
  - evidence_status
  - symptom_pathology_catalog
devuelve:
  - patologias_candidatas
  - prioridad
  - rationale
  - required_formulas
productores:
  - pymia/smartpyme/tank_selection.py
  - pymia/smartpyme/operational_hypothesis.py
  - docs/pathology_catalog.v1.json
  - SmartPyme/app/catalogs/symptom_pathology_catalog.py
consumidores:
  - FORMULA_EXECUTION_PORT
  - DIAGNOSTIC_RESULT_PORT
gates:
  - PATHOLOGY_CANDIDATE_GATE
no_puede:
  - confirmar patología
  - reemplazar cálculo determinístico
```

### 5.8 FORMULA_EXECUTION_PORT

```yaml
port_id: FORMULA_EXECUTION_PORT
fase_pipeline: cálculo
recibe:
  - formula_id
  - variables_normalizadas
  - evidence_refs
  - thresholds opcionales
devuelve:
  - formula_result
  - value
  - unit
  - status: CALCULATED | INSUFFICIENT_DATA | INVALID_INPUT | NOT_APPLICABLE
  - evidence_refs usados
productores:
  - pymia/services/formula_engine_service.py
  - pymia/contracts/formula_contract.py
  - SmartPyme/app/services/formula_engine_service.py
consumidores:
  - DIAGNOSTIC_RESULT_PORT
  - FINDING_PORT
gates:
  - FORMULA_INPUT_GATE
no_puede:
  - completar variables faltantes por intuición
  - usar evidencia sin referencia
```

### 5.9 DIAGNOSTIC_RESULT_PORT

```yaml
port_id: DIAGNOSTIC_RESULT_PORT
fase_pipeline: evaluación diagnóstica
recibe:
  - pathology_id
  - formula_result
  - evidence_refs
  - thresholds
  - case_context
devuelve:
  - diagnostic_status: CONFIRMED | NOT_CONFIRMED | INSUFFICIENT | CANDIDATE | BLOCKED
  - pathology_id
  - impact_estimate
  - confidence
  - reason
  - evidence_refs
productores:
  - pymia/services/pathology_engine_service.py
  - pymia/services/pathology_knowledge_tank.py
  - SmartPyme/app/services/pathology_evaluators.py
consumidores:
  - FINDING_PORT
  - REPORT_PORT
gates:
  - DIAGNOSTIC_EVIDENCE_GATE
no_puede:
  - emitir diagnóstico sin evidencia suficiente
  - ocultar estado insuficiente
```

### 5.10 FINDING_PORT

```yaml
port_id: FINDING_PORT
fase_pipeline: hallazgo accionable
recibe:
  - diagnostic_result
  - formula_result
  - case_context
  - evidence_refs
devuelve:
  - actionable_finding
  - severity
  - impact
  - business_language_summary
  - suggested_next_action
productores:
  - pymia/smartpyme/finding_projection.py
  - pymia/audit_result/builder.py
  - SmartPyme/app/services/findings_service.py
consumidores:
  - REPORT_PORT
  - CHANNEL_OUTPUT_PORT
gates:
  - FINDING_GROUNDING_GATE
no_puede:
  - generar hallazgo sin evidencia_refs
  - exponer jerga interna al dueño
```

### 5.11 REPORT_PORT

```yaml
port_id: REPORT_PORT
fase_pipeline: entrega
recibe:
  - findings
  - evidence_summary
  - missing_evidence
  - case_context
devuelve:
  - report_payload
  - markdown opcional
  - sections
  - limitations
  - next_steps
productores:
  - pymia/narrative/report_generator.py
  - pymia/narrative/report_generator_v2.py
  - pymia/narrative/minimal_delivery_report.py
  - pymia/smartpyme/delivery_package.py
  - pymia/smartpyme/delivery_markdown.py
consumidores:
  - CHANNEL_OUTPUT_PORT
  - memoria/checkpoint opcional
gates:
  - REPORT_GROUNDING_GATE
no_puede:
  - inventar conclusión no respaldada
  - declarar producto final
```

### 5.12 CHANNEL_OUTPUT_PORT

```yaml
port_id: CHANNEL_OUTPUT_PORT
fase_pipeline: canal / conversación
recibe:
  - report_payload o pregunta de evidencia
  - audience: owner | developer
  - channel: telegram | cli | api
devuelve:
  - texto_visible
  - estado_visible
  - next_prompt opcional
productores:
  - pymia/telegram_bot_runtime.py
  - pymia/orchestration/conversation_adapter.py
  - pymia/smartpyme/delivery_markdown.py
consumidores:
  - dueño PyME
  - operador/desarrollador
gates:
  - OWNER_LANGUAGE_GATE
no_puede:
  - exponer formula_id, evidence_type, READY_FOR_ANALYSIS, internal trace cruda al dueño
  - diagnosticar si el status interno está bloqueado
```

---

## 6. Gates base

### FIRST_CONTACT_GATE

Bloquea diagnóstico antes de ficha inicial cuando el contrato vigente exige anamnesis.

### FICHA_COMPLETENESS_GATE

Bloquea paso a evidencia si faltan datos mínimos del caso.

### FILE_ACCEPTANCE_GATE

Bloquea archivos inexistentes, formato no soportado o recepción incompleta.

### PARSE_QUALITY_GATE

Bloquea documentos no parseables o estructura ambigua sin pregunta al dueño.

### SEMANTIC_CONFIDENCE_GATE

Bloquea mapeos semánticos de baja confianza para variables críticas.

### EVIDENCE_SUFFICIENCY_GATE

Bloquea cálculo si falta evidencia requerida por fórmula/patología.

### PATHOLOGY_CANDIDATE_GATE

Evita convertir síntoma o dolor en diagnóstico confirmado.

### FORMULA_INPUT_GATE

Bloquea ejecución de fórmula si faltan variables, unidades o evidencia_refs.

### DIAGNOSTIC_EVIDENCE_GATE

Bloquea patología confirmada si la evidencia no alcanza.

### FINDING_GROUNDING_GATE

Bloquea hallazgos sin evidencia, impacto o trazabilidad.

### REPORT_GROUNDING_GATE

Bloquea reporte final si contiene claims no respaldados.

### OWNER_LANGUAGE_GATE

Bloquea jerga técnica visible al dueño PyME.

---

## 7. Tabla mínima de relación puerto → gate

| Puerto | Gate principal | Resultado si falla |
|---|---|---|
| OWNER_INPUT_PORT | FIRST_CONTACT_GATE | abrir ficha / pedir dato mínimo |
| CASE_CONTEXT_PORT | FICHA_COMPLETENESS_GATE | continuar anamnesis |
| DOCUMENT_INPUT_PORT | FILE_ACCEPTANCE_GATE | pedir archivo válido |
| DOCUMENT_PROFILE_PORT | PARSE_QUALITY_GATE | explicar problema de lectura |
| SEMANTIC_MAPPING_PORT | SEMANTIC_CONFIDENCE_GATE | pedir significado al dueño |
| EVIDENCE_STATUS_PORT | EVIDENCE_SUFFICIENCY_GATE | pedir evidencia faltante |
| PATHOLOGY_SELECTION_PORT | PATHOLOGY_CANDIDATE_GATE | mantener hipótesis |
| FORMULA_EXECUTION_PORT | FORMULA_INPUT_GATE | bloquear cálculo |
| DIAGNOSTIC_RESULT_PORT | DIAGNOSTIC_EVIDENCE_GATE | marcar insuficiente/bloqueado |
| FINDING_PORT | FINDING_GROUNDING_GATE | no generar hallazgo |
| REPORT_PORT | REPORT_GROUNDING_GATE | no emitir reporte final |
| CHANNEL_OUTPUT_PORT | OWNER_LANGUAGE_GATE | humanizar salida |

---

## 8. Regla de uso por agentes

Antes de tocar código, cualquier agente debe declarar:

```text
1. qué puerto toca
2. qué gate toca
3. qué archivo produce la salida
4. qué archivo consume la salida
5. qué test protege el contrato
6. qué queda fuera
```

Si no puede declararlo, no debe tocar código.

---

## 9. Estado actual

Este documento es un registro inicial de diseño operativo.

No certifica que todos los puertos estén implementados.
No autoriza refactor masivo.
No reemplaza `KERNEL_PIPELINE_INVENTORY.md`.
No abre un nuevo milestone de producto.

Sirve para evitar que el próximo desarrollo siga conectando piezas por intuición.

---

## 10. Próximo uso recomendado

Usar este documento para cerrar cualquier TaskSpec futura con esta forma:

```text
Slice:
Puerto afectado:
Gate afectado:
Input fixture:
Output esperado:
Tests obligatorios:
Archivos permitidos:
Archivos prohibidos:
```
