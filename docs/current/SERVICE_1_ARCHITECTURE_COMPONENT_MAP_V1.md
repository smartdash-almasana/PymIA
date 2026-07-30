# Servicio 1 — mapa actual de arquitectura y componentes V1

**Estado:** `ACTIVE_ARCHITECTURE_MAP`  
**Fecha de corte:** 2026-07-29  
**Alcance:** arquitectura física actual de Servicio 1 y componentes de plataforma integrados alrededor de su raíz productiva.  
**No autoriza:** nuevas capacidades, nuevas raíces productivas, APIs, runtime LLM, delivery autónomo ni integración automática de componentes SUPPORT.

---

## 1. Propósito

Este documento explica la arquitectura de Servicio 1 después de la convergencia de Stage 2 y de la integración posterior de fundaciones de dominio, narrativa, admisión, harness operacional y operador fiel.

La regla principal es distinguir tres cosas que pueden coexistir en el mismo repositorio:

```text
A. autoridad productiva de Servicio 1
B. infraestructura o soporte reutilizable
C. capacidades/contratos todavía no integrados a la raíz productiva
```

La existencia física de un módulo no lo convierte en autoridad productiva.

La autoridad de ejecución de Servicio 1 sigue determinada por:

```text
pymia/cli/service_1_product.py
→ pymia/smartpyme/service_1_product_pipeline_v1.py
→ módulos PRODUCTIVE de docs/service_1_module_disposition.v1.json
```

---

## 2. Vista de alto nivel

```text
                         DUEÑO PYME
                             │
                             │ aporta evidencia / confirma significado
                             ▼
┌───────────────────────────────────────────────────────────────┐
│ CAPA DE RECEPCIÓN Y APLICACIÓN                               │
│                                                               │
│ admission v1 / faithful_operator / vertical slice            │
│                                                               │
│ Rol: recibir, estructurar, pedir evidencia, presentar         │
│ candidatos.                                                   │
│ No autoriza verdad operacional ni ejecución productiva.       │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│ SERVICIO 1 — RAÍZ PRODUCTIVA CANÓNICA                         │
│                                                               │
│ service_1_product_pipeline_v1                                 │
│                                                               │
│ P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9 → P10      │
│                                                               │
│ evidencia → semántica → dueño → aprobación →                 │
│ requisitos → computabilidad → cálculo → outcome → delivery   │
│ solicitud de conciliación → compuerta → revisión humana      │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│ SALIDA Y PRESENTACIÓN                                         │
│                                                               │
│ bounded outcomes / XLSX delivery / narrative adapters         │
│                                                               │
│ La narrativa proyecta evidencia; no crea hechos ni            │
│ computabilidad.                                               │
└───────────────────────────────────────────────────────────────┘

CROSS-CUTTING, SIN AUTORIDAD PRODUCTIVA AUTOMÁTICA:
- pymia/domain/*
- pymia/diagnostic_core/*
- pymia/narrative/*
- pymia/operational_harness/*
- contratos contables generales, workpapers y superficies todavía no integradas
- radiografía, corpus, quality gates y herramientas de auditoría
```

---

## 3. Plano A — autoridad productiva de Servicio 1

### 3.1 Entrada oficial

```text
pymia/cli/service_1_product.py
```

Es la entrada oficial del producto Servicio 1.

No debe aparecer una segunda entrada con igual autoridad.

### 3.2 Raíz productiva única

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

La raíz coordina:

- recorrido semántico determinístico;
- preguntas al dueño cuando los bindings no están confirmados;
- P8 y construcción de `GovernedComputationInput`;
- dispatch explícito por `requested_capability`;
- evaluadores especializados sólo donde existe comportamiento realmente especializado;
- kernel genérico para las capacidades gobernadas por registry;
- acceso exclusivo a conciliación bancaria o Mercado Pago mediante compuertas gobernadas;
- paquete de conciliación siempre dirigido a revisión humana;
- outcome acotado;
- delivery sólo cuando está explícitamente autorizado.

### 3.3 Recorrido P0–P10

```text
P0  intake
P1  canonical XLSX ingestion
P2  profiling / physical evidence
P3  semantic hypothesis
P4  contextual evidence
P5  OwnerConfirmationEvent
P6  ApprovalDecision
P7  RequirementMatch + Grain
P8  ComputabilityDecision + GovernedComputationInput
P9  deterministic execution
P10 QA / delivery
```

P0–P10 describe autoridades y orden lógico. No exigen once módulos físicos.

### 3.4 Autoridad semántica

La secuencia canónica conserva la separación:

```text
hipótesis semántica
≠ confirmación del dueño
≠ decisión P6
≠ match P7
≠ computabilidad P8
```

El dueño confirma significado. No autoriza por ese solo acto ejecución, diagnóstico o entrega.

### 3.5 Autoridad de computabilidad

La ejecución requiere un artefacto gobernado producido después de P6/P7/P8.

```text
P6 ApprovalDecision
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision
→ GovernedComputationInput
```

Un score, una hipótesis, un nombre de columna o una respuesta libre no reemplazan esta cadena.

### 3.6 Autoridad de ejecución

Existen dos formas de ejecución dentro de la misma raíz:

```text
comportamiento especializado probado
→ evaluador especializado

capacidad registry-governed
→ CapabilityRegistry
→ GenericCapabilityEngine
```

La incorporación de una nueva capacidad genérica no debe crear una nueva rama identitaria en la raíz salvo necesidad especializada demostrada.

---

## 4. Plano B — infraestructura y soporte integrados

Estos componentes están presentes en el repositorio y son relevantes para la arquitectura global, pero no sustituyen la clasificación `PRODUCTIVE` de Servicio 1.

### 4.1 Modelo de dominio

```text
pymia/domain/*
```

Fundación de objetos de dominio puros: entidades, snapshots, primitivas y tipos.

Principio observado en el paquete:

```text
pure domain objects
zero infrastructure dependencies
```

Uso arquitectónico permitido:

- expresar conceptos del dominio;
- servir como vocabulario común;
- sostener contratos futuros.

No puede por existir:

- ejecutar Servicio 1;
- saltar P6/P7/P8;
- declarar una patología productiva;
- autorizar delivery.

### 4.2 Pipeline de admisión

```text
pymia/pipeline/admission/v1/*
pymia/contracts/admission_v1.py
```

Convierte una narrativa inicial en un artefacto estructurado de síntomas e hipótesis mediante lógica determinística/heurística.

Su rol es preanalítico:

```text
relato inicial
→ síntoma estructurado
→ hipótesis de trabajo
→ evidencia requerida
```

Los `confidence_score` de admisión son priorización de hipótesis de trabajo. No son autoridad de verdad, matching, aprobación semántica, computabilidad ni ejecución de Servicio 1.

### 4.3 Faithful Operator

```text
pymia/faithful_operator.py
```

FSM determinística para interacción inicial con el dueño y procesamiento local de evidencia.

Fases observadas:

```text
LISTENING
EVIDENCE_REQUESTED
PROCESSING
CANDIDATE_DELIVERED
OWNER_CONFIRMATION_PENDING
BLOCKED
CLOSED
```

Su función es mantener una conversación operativa trazable y fail-closed.

No constituye una segunda raíz productiva. La confirmación de un candidato por el operador fiel no sustituye P6/P7/P8 de la raíz canónica.

### 4.4 Vertical slice / application pipeline

```text
pymia/cli/vertical_slice.py
pymia/application/vertical_pipeline.py
```

Sirve para flujos locales de lectura, estructuración de evidencia, reportes y trazabilidad.

Debe tratarse como superficie de aplicación/soporte. No puede promoverse por documentación a raíz productiva paralela.

### 4.5 Diagnostic Core

```text
pymia/diagnostic_core/*
pymia/services/formula_engine_service.py
```

El core calcula fórmulas y devuelve resultados/candidatos o bloqueos según evidencia.

En el código actual, una fórmula calculada produce explícitamente un resultado diagnóstico `CANDIDATE`; no confirma diagnóstico final.

Por tanto:

```text
formula calculada
≠ diagnóstico confirmado
```

Este core puede aportar computación reusable, pero no puede romper la autoridad P6/P7/P8 de Servicio 1 cuando se usa dentro de esa cadena.

### 4.6 Narrative layer

```text
pymia/narrative/*
```

Proyecta evidencia existente a reportes legibles, con claims vinculados a `evidence_ids`.

Regla:

```text
narrativa explica evidencia
narrativa no crea evidencia
narrativa no decide computabilidad
narrativa no autoriza delivery
```

### 4.7 Operational Harness y Pipeline Radiography

```text
pymia/operational_harness/*
pymia/pipeline_radiography/*
```

Son capas de observación, medición, escenarios y clasificación operativa.

Pueden producir estados como `GREEN`, `YELLOW`, `RED`, detectar escenarios ambiguos o capacidades parciales y sugerir una próxima acción de ingeniería.

No forman parte de la decisión productiva del caso PyME y no reemplazan los gates del producto.

---

## 5. Plano C — contratos y capacidades todavía no integrados

### 5.1 Familia contable

Existe infraestructura contractual para:

- conciliación bancaria;
- conciliación Mercado Pago;
- matching factura/cobranza;
- revisión compra/proveedor;
- workpapers contables.

El módulo Service 1:

```text
service_1_accounting_contracts_v1
```

está clasificado como `SUPPORT_NECESSARY` en el registro de disposición vigente.

Por tanto, los contratos contables expresan lenguaje y límites, pero no se convierten automáticamente en ejecución productiva.

### 5.2 Conciliación algorítmica

El matcher existente:

```text
service_2_reconciliation_match_candidates_v1
```

es actualmente la pieza que ejecuta matching algorítmico de conciliación.

Su maduración es un frente separado. La arquitectura vigente exige:

```text
ambigüedad explícita
referencia como evidencia, no verdad
sin confidence score como autoridad
sin matching codicioso para resolver colisiones
human review para casos ambiguos
```

No existe todavía integración productiva autorizada de este matcher dentro de la raíz de Servicio 1.

---

## 6. Clasificación física actual de módulos Service 1

Fuente:

```text
docs/service_1_module_disposition.v1.json
```

Estado observado al redactar este mapa:

```text
TOTAL_SERVICE_1_MODULES = 59
PRODUCTIVE = 30
SUPPORT_NECESSARY = 29
CANONICAL_PRODUCT_ROOT = service_1_product_pipeline_v1
```

Sólo `PRODUCTIVE` define el closure ejecutable de la raíz canónica.

`SUPPORT_NECESSARY` significa que el componente es útil o necesario para ingeniería, ingesta, delivery, catálogo, medición o soporte de dominio; no significa que posea autoridad de ejecución.

---

## 7. Evolución integrada posterior a Stage 2

Git registra, después de la convergencia principal, las siguientes fundaciones integradas:

```text
039f0cd  feat(domain): integrate domain model foundation
1b62053  feat(narrative): integrate deterministic narrative layer
05cf07b  feat(pipeline): integrate admission pipeline foundation
bc2fabf  feat(tooling): integrate pipeline radiography and operational harness
c240080  refactor(service1): remove live root dependency and legacy evidence bridge
9181abf  feat(service1): integrate faithful operator and document parsing support
48aa4a0  docs(service1): reconcile current authority and retire Hermes legacy
17e36a2  test(repo): retain regression coverage and local tooling
```

Estas integraciones amplían la plataforma alrededor de Servicio 1, pero no modifican por sí solas la regla de raíz productiva única.

---

## 8. Dependencias de autoridad

```text
Código físico + tests
        ↓
ARCHITECTURE_GUARDRAILS.md
        ↓
docs/current/README.md
        ↓
SERVICE_1_CANONICAL_AXIS.md
SERVICE_1_ARCHITECTURE_LOCK.md
SERVICE_1_STATUS.md
        ↓
este mapa de componentes
        ↓
evidencia técnica y contratos específicos
```

Si un componente contradice la raíz canónica, el componente debe clasificarse, corregirse, aislarse o retirarse; no se redefine la raíz para justificarlo.

---

## 9. Invariantes

```text
ONE_CANONICAL_PRODUCT_ROOT
ONE_CANONICAL_SERVICE_1_EXECUTION_AUTHORITY
NO_LLM_RUNTIME_AUTHORITY
NO_SECOND_XLSX_PRODUCT_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
ADMISSION_HYPOTHESIS_IS_NOT_APPROVAL
NARRATIVE_IS_NOT_EVIDENCE
HARNESS_IS_NOT_PRODUCT_RUNTIME
SUPPORT_NECESSARY_IS_NOT_PRODUCTIVE
ACCOUNTING_CONTRACT_IS_NOT_EXECUTION
RECONCILIATION_AMBIGUITY_ESCALATES_TO_HUMAN
```

---

## 10. Regla para próximas integraciones

Todo componente que pretenda pasar de soporte a ejecución productiva debe demostrar, como mínimo:

```text
contrato explícito
ubicación exacta en P0–P10
caller productivo legítimo
sin segunda autoridad paralela
tests focales
tests vecinos
guard arquitectónico
fail-closed ante evidencia insuficiente o ambigua
actualización de module_disposition
actualización de la documentación rectora
```

No se promueve arquitectura por similitud conceptual ni por mera existencia de código.
