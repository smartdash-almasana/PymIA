# Servicio 1 — architecture lock

**Status:** `ACTIVE`  
**Reconciled on:** `2026-07-29`  
**Scope:** product authority, execution boundaries, support-layer boundaries and promotion rules.

## 1. Software objetivo

Servicio 1 es un microservicio determinístico para evidencia PyME con XLSX como fuente productiva principal actual. Lee archivos reales, conserva evidencia estructural, pregunta al dueño cuando el significado operativo no está cerrado, construye estado canónico, aplica gates determinísticos, ejecuta sólo capacidades explícitamente autorizadas y produce outcomes/archivos trazables.

```text
La capa conversacional conversa.
La FSM y los contratos gobiernan.
Las tools determinísticas ejecutan.
El dueño confirma significado.
La evidencia manda.
```

## 2. Entrada oficial y raíz productiva

Entrada oficial:

```text
pymia/cli/service_1_product.py
```

Raíz productiva canónica:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

No se autoriza una segunda raíz productiva.

## 3. Clasificación física obligatoria

Fuente:

```text
docs/service_1_module_disposition.v1.json
```

Estado observado al reconciliar este lock:

```text
TOTAL_SERVICE_1_MODULES = 57
PRODUCTIVE = 27
SUPPORT_NECESSARY = 30
```

Sólo los módulos `PRODUCTIVE` pueden integrar el closure ejecutable de la raíz canónica.

`SUPPORT_NECESSARY` puede contener ingesta auxiliar, contratos, auditoría, delivery, corpus, quality gates, web asistida, dominio u otras piezas necesarias, pero no adquiere autoridad de ejecución por clasificación de soporte.

## 4. Cadena de autoridad P0–P10

```text
P0 intake
→ P1 canonical XLSX ingestion
→ P2 profiling / physical evidence
→ P3 semantic hypothesis
→ P4 contextual evidence
→ P5 OwnerConfirmationEvent
→ P6 ApprovalDecision
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision + GovernedComputationInput
→ P9 deterministic execution
→ P10 QA / delivery
```

Invariantes:

```text
EVENT ≠ DECISION
HYPOTHESIS ≠ APPROVAL
APPROVAL ≠ COMPUTABILITY
COMPUTABILITY ≠ EXECUTION
EXECUTION ≠ DELIVERY
```

## 5. Ejecución productiva

### Especializados

Los evaluadores especializados sólo se justifican cuando el comportamiento no encaja en el kernel genérico sin pérdida semántica o contractual.

Actualmente la raíz conserva las excepciones especializadas históricamente justificadas para:

```text
LIQ_001
REN_001
```

### Kernel genérico

Las capacidades registry-governed siguen:

```text
CapabilityDefinitionV1
→ CapabilityRegistry
→ P8 governed input
→ GenericCapabilityEngine
→ bounded outcome
```

Agregar una capacidad genérica no autoriza agregar una nueva rama identitaria en la raíz.

## 6. Fundaciones de plataforma integradas

Después de Stage 2 se integraron fundaciones generales:

```text
pymia/domain/*
pymia/pipeline/admission/v1/*
pymia/faithful_operator.py
pymia/application/vertical_pipeline.py
pymia/diagnostic_core/*
pymia/narrative/*
pymia/operational_harness/*
pymia/pipeline_radiography/*
```

Estas piezas están dentro del repositorio, pero la integración al repositorio no equivale a integración a la raíz productiva de Servicio 1.

### Domain lock

`pymia/domain/*` puede expresar entidades, relaciones, snapshots y tipos de dominio.

No puede:

- autorizar ejecución;
- decidir computabilidad;
- promover patologías productivas;
- reemplazar contratos de Servicio 1.

### Admission lock

La admisión puede convertir narrativa en síntomas, hipótesis y pedidos de evidencia.

Sus heurísticas y `confidence_score` sirven para priorización preanalítica.

No pueden:

- confirmar semántica;
- decidir matching;
- saltar owner confirmation;
- autorizar P8/P9;
- declarar diagnóstico final.

### Faithful Operator lock

El operador fiel puede recibir mensajes, pedir evidencia, presentar candidatos y gestionar confirmación/corrección del dueño mediante una FSM determinística.

No es una segunda raíz productiva.

Un estado `CLOSED` del operador fiel no equivale automáticamente a P6/P7/P8 satisfechos.

### Diagnostic Core lock

Un cálculo disponible puede producir un candidato o un bloqueo.

```text
CALCULATED ≠ DIAGNOSED
```

El diagnostic core no puede declarar verdad operacional por fuera de la evidencia ni convertirse en ruta paralela al producto.

### Narrative lock

La capa narrativa puede ordenar y explicar claims anclados en evidencia.

```text
NARRATIVE ≠ EVIDENCE
NARRATIVE ≠ COMPUTABILITY
NARRATIVE ≠ AUTHORIZATION
```

### Harness lock

Operational Harness y Pipeline Radiography son herramientas de observación/ingeniería.

Un estado `GREEN` significa estado de medición según sus criterios; no significa autorización de producto, runtime o delivery.

## 7. Contabilidad y conciliación

La familia contable existe como soporte contractual.

```text
service_1_accounting_contracts_v1 = SUPPORT_NECESSARY
```

El matcher algorítmico de conciliación existente está en:

```text
service_2_reconciliation_match_candidates_v1
```

Reglas cerradas antes de cualquier wiring productivo:

```text
fecha + importe no demuestra identidad
referencia es evidencia, no verdad
confidence float no decide conciliación
ambigüedad debe ser explícita
1:N / N:1 / N:M no se resuelve codiciosamente
no-imputados no se ocultan por diferencias parciales
AMBIGUOUS escala a revisión humana
```

No crear:

```text
reconciliation_core_v1 paralelo
uncertainty_resolution_v1 global
event bus
colas
microservicios distribuidos para este frente
API de conciliación antes de madurar matcher/contratos
```

## 8. Delivery lock

Delivery sólo ocurre por autorización explícita y capacidad habilitada.

La existencia de un outcome, un reporte narrativo, un workpaper o un cálculo no autoriza entrega automática.

```text
OUTCOME_READY ≠ DELIVERY_AUTHORIZED
```

## 9. Prohibiciones de arquitectura

- No nueva raíz productiva fuera de `service_1_product_pipeline_v1`.
- No nueva entrada oficial equivalente fuera de `pymia/cli/service_1_product.py`.
- No segundo parser XLSX productivo.
- No cadena productiva paralela a P0–P10.
- No selección soberana de capacidad desde texto libre.
- No LLM runtime authority.
- No diagnóstico causal automático.
- No runtime autorizado por un score.
- No promoción automática de módulos SUPPORT.
- No web/UI con fórmulas o verdad de negocio propia.
- No owner confirmation interpretada como permiso universal.
- No harness/radiography gobernando runtime.
- No narrative layer inventando hechos.
- No componente histórico gobernando arquitectura por estar todavía presente en Git.

## 10. Regla de promoción

Antes de promover soporte a autoridad productiva deben existir:

```text
contrato explícito
ubicación en P0–P10
caller productivo legítimo
prueba de ausencia de autoridad paralela
fail-closed
focal tests
neighbor tests
architecture guards
module_disposition actualizado
documentación rectora actualizada
```

La promoción debe ser focal y verificable.

## 11. Evidencia verificable

```text
docs/service_1_architecture_lock.v1.json
docs/service_1_module_disposition.v1.json
tests/smartpyme/test_service_1_architecture_lock_v1.py
tests/smartpyme/test_service_1_product_pipeline_v1.py
docs/current/SERVICE_1_STAGE2_CLOSEOUT_V1.md
docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
```

## 12. Frase rectora

```text
Servicio 1 puede ampliar su plataforma sin ampliar su soberanía.
La autoridad productiva sólo cambia por contrato, integración explícita y evidencia.
```
