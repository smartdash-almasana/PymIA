# SMARTPYME_KNOWLEDGE_TANKS_CONTRACT

Estado: **DRAFT v1 — Documento canónico (sin implementación runtime)**

---

## 1. Estado y propósito

Este documento define el **contrato formal** para los tanques de conocimiento
enchufables/desenchufables del sistema SmartPyme.

Un **KnowledgeTank** es la unidad mínima de conocimiento de dominio que puede
activarse, desactivarse, versionarse y reemplazarse sin modificar el runtime
core de PymIA.

Un **DomainPack** es una agrupación coherente de KnowledgeTanks orientada a una
industria, canal o tipo de operación.

Este contrato es **normativo para documentación y diseño**. No implica que los
tanques estén implementados en código. Cualquier implementación futura debe
respetar las reglas, límites y políticas aquí definidas.

---

## 2. Problema que resuelve

El conocimiento del dominio PyME estaba disperso en:

- lógica embebida en prompts;
- código hardcodeado dentro de clasificaciones específicas;
- catálogos JSON sin política de activación;
- documentos conceptuales sin contrato ejecutable.

Esto generaba riesgos concretos:

- **Mezcla de dominios:** un análisis financiero podía arrastrar reglas de stock.
- **Diagnóstico prematuro:** el sistema podía afirmar patologías sin evidencia.
- **Rigidez:** agregar una industria nueva requería tocar código core.
- **Falta de versionado:** no había forma de saber qué versión de conocimiento
  se aplicó a un caso.
- **Imposibilidad de hot-swap:** no se podían cargar o descargar módulos sin
  reiniciar ni modificar el runtime.

El contrato de KnowledgeTank resuelve estos problemas definiendo:

- estructura canónica de cada tanque;
- política de activación/desactivación determinística;
- relación explícita con síntomas, evidencia y clasificaciones;
- límites de seguridad formales;
- versionado semántico simple.

---

## 3. Definición canónica de KnowledgeTank

Un **KnowledgeTank** NO es solo un catálogo.

Un KnowledgeTank es la suma de:

```text
catálogo de conocimiento
+ política de activación
+ política de desactivación
+ evidencia requerida
+ preguntas soportadas
+ fórmulas soportadas
+ clasificaciones habilitadas
+ límites de seguridad
+ outputs permitidos
+ compatibilidad declarada
```

### Campos mínimos

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `tank_id` | string | ✅ | Identificador único global |
| `version` | string (semver) | ✅ | Versión del tanque |
| `name` | string | ✅ | Nombre legible |
| `domain` | string | ✅ | Dominio principal |
| `scope` | string | ✅ | Alcance funcional |
| `description` | string | ✅ | Descripción breve |
| `activation_conditions` | list[Condition] | ✅ | Cuándo activar |
| `deactivation_conditions` | list[Condition] | ✅ | Cuándo desactivar |
| `required_context` | list[str] | ❌ | Contexto mínimo requerido |
| `required_evidence` | list[EvidenceNeed] | ❌ | Evidencia mínima |
| `supported_symptoms` | list[str] | ✅ | Síntomas que cubre |
| `supported_domains` | list[str] | ✅ | Dominios que abarca |
| `supported_questions` | list[Question] | ❌ | Preguntas de desambiguación |
| `supported_document_types` | list[str] | ❌ | Tipos documentales soportados |
| `expected_fields` | dict[str, list[str]] | ❌ | Campos esperados por documento |
| `supported_formulas` | list[str] | ❌ | IDs de fórmula_catalog |
| `supported_hypotheses` | list[Hypothesis] | ❌ | Hipótesis contrastables |
| `supported_classifications` | list[str] | ❌ | Clasificaciones ejecutables |
| `runtime_capabilities` | list[str] | ❌ | Capacidades runtime necesarias |
| `output_contract` | OutputContract | ✅ | Qué puede emitir |
| `safety_constraints` | list[str] | ✅ | Restricciones de seguridad |
| `limits` | list[str] | ✅ | Qué NO puede hacer |
| `compatibility` | Compatibility | ❌ | Versiones runtime compatibles |
| `owner_notes` | string | ❌ | Notas del responsable |

### Regla fundamental

Un KnowledgeTank **nunca diagnostica**.
Solo:
- sugiere síntomas candidatos;
- aporta preguntas;
- define evidencia necesaria;
- habilita clasificaciones ejecutables;
- alimenta hipótesis contrastables.

---

## 4. Schema YAML de KnowledgeTank

```yaml
# smartpyme_knowledge_tank.schema.v1.yaml
schema_version: "1.0"
tank_id: "operational_pathology_core"
version: "1.0.0"
name: "Operational Pathology Tank (Core PyME)"
domain: "operational_diagnosis"
scope: "pyme_general"
description: |
  Mapea lenguaje crudo, señales y síntomas a patologías operacionales PyME
  sin emitir diagnóstico.

activation_conditions:
  - type: "symptom_match"
    any_of:
      - DESCUADRE_DINERO
      - MARGEN_DUDOSO
      - STOCK_INCONSISTENTE
      - COSTO_INCIERTO
      - SOBRECARGA_MANUAL
      - DATOS_DUPLICADOS
      - MAESTRO_DESORDENADO
      - DOCUMENTACION_DESORDENADA
  - type: "domain_match"
    any_of:
      - finanzas
      - comercial
      - proveedores
      - stock
      - produccion
      - datos_maestros

deactivation_conditions:
  - type: "no_symptoms"
  - type: "status_blocked"
    status: BLOCKED_INSUFFICIENT_CONTEXT
  - type: "safety_violation"

required_context:
  - raw_text_non_empty
  - at_least_one_symptom_or_selector

required_evidence:
  - evidence_type: "excel_financiero"
    required_fields: [fecha, concepto, monto]
    reason: "Necesario para validar hipótesis de descalce o margen."

supported_symptoms:
  - DESCUADRE_DINERO
  - MARGEN_DUDOSO
  - COSTO_INCIERTO
  - STOCK_INCONSISTENTE
  - SOBRECARGA_MANUAL
  - DATOS_DUPLICADOS
  - MAESTRO_DESORDENADO
  - DOCUMENTACION_DESORDENADA

supported_domains:
  - finanzas
  - comercial
  - proveedores
  - stock
  - produccion
  - datos_maestros
  - automatizacion
  - administracion

supported_questions:
  - symptom: DESCUADRE_DINERO
    question: "¿Hablás de caja/banco, ventas/cobros, costos/margen o gastos?"
  - symptom: MARGEN_DUDOSO
    question: "¿Querés revisar precios vs costos, productos sin costo o margen histórico?"
  - symptom: DATOS_DUPLICADOS
    question: "¿Los duplicados están en proveedores, clientes, productos u otro listado?"
  - symptom: STOCK_INCONSISTENTE
    question: "¿La diferencia es entre sistema y depósito, o en movimientos sin registrar?"
  - symptom: SOBRECARGA_MANUAL
    question: "¿Qué tarea se repite, con qué frecuencia y en qué archivos ocurre?"

supported_document_types:
  - excel_ventas_costos
  - excel_proveedores
  - excel_stock
  - pdf_facturas
  - capturas_panel

expected_fields:
  excel_ventas_costos: [fecha, producto, precio_venta, costo, cantidad]
  excel_proveedores: [proveedor, cuit, razon_social]
  excel_stock: [producto, stock_sistema, stock_real, fecha]

supported_formulas:
  - REN_001_margen_neto_real
  - LIQ_001_vendido_cobrado
  - INV_002_rotacion_stock
  - PYME_011_dso
  - PYME_013_dso_dpo_gap

supported_hypotheses:
  - id: margen_erosionado
    symptom: MARGEN_DUDOSO
    test: "margen_neto_real < 20% en >50% productos"
    evidence_required: [excel_ventas_costos]
  - id: proveedores_duplicados
    symptom: DATOS_DUPLICADOS
    test: "count(cuit_duplicado) > 0"
    evidence_required: [excel_proveedores]

supported_classifications:
  - excel_diagnostic
  - supplier_duplicate_check

runtime_capabilities:
  - local_mvp_runtime
  - interrogation_slice

output_contract:
  can_emit:
    - candidate_pathologies
    - clarifying_questions
    - evidence_requirements
    - risk_warnings
    - suggested_classification
  cannot_emit:
    - diagnostic_conclusion
    - root_cause_assertion
    - benchmark_comparison_without_sector

safety_constraints:
  - "NO diagnosticar sin evidencia"
  - "NO afirmar causa raíz sin datos históricos"
  - "NO comparar con benchmarks sin contexto sectorial"
  - "NO activar tanque solo por selector estructural"
  - "NO pedir evidencia excesiva (>3 tipos simultáneos)"
  - "NO prometer outputs que el runtime no soporta"

limits:
  - "No ejecuta análisis"
  - "No valida evidencia"
  - "No persiste estado entre turnos"
  - "No reemplaza conversación real"

compatibility:
  min_runtime: "local_mvp_runtime"
  requires_interrogation_slice: true

owner_notes: |
  Este tanque es la base para todos los análisis operacionales PyME.
  Debe ampliarse por industria mediante DomainPacks especializados.
```

---

## 5. Definición canónica de DomainPack

Un **DomainPack** es una agrupación coherente de KnowledgeTanks orientada a:

- una industria (ej: textil, agro, construcción);
- un canal (ej: Mercado Libre, ecommerce, local físico);
- un tipo de operación (ej: manufactura, servicios, reventa).

### Campos mínimos

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `pack_id` | string | ✅ | Identificador único |
| `version` | string (semver) | ✅ | Versión del pack |
| `name` | string | ✅ | Nombre legible |
| `industry_or_domain` | string | ✅ | Industria o dominio |
| `activation_policy` | ActivationPolicy | ✅ | Cuándo activar el pack |
| `included_tanks` | list[str] | ✅ | IDs de tanques incluidos |
| `required_context` | list[str] | ❌ | Contexto mínimo |
| `evidence_policy` | EvidencePolicy | ✅ | Qué evidencia exige el pack |
| `output_policy` | OutputPolicy | ✅ | Qué outputs puede producir |
| `safety_policy` | list[str] | ✅ | Restricciones de seguridad |
| `compatibility` | Compatibility | ❌ | Compatibilidad runtime |

### Regla fundamental

Un DomainPack **hereda** las restricciones de cada KnowledgeTank incluido.
No puede relajar límites de seguridad de sus tanques.
Puede **agregar** restricciones específicas del dominio, pero nunca quitarlas.

---

## 6. Schema YAML de DomainPack

```yaml
# smartpyme_domain_pack.schema.v1.yaml
schema_version: "1.0"
pack_id: "ecommerce_mercadolibre_v1"
version: "1.0.0"
name: "Domain Pack Ecommerce Mercado Libre"
industry_or_domain: "ecommerce_mercadolibre"

activation_policy:
  conditions:
    - type: "selector_match"
      selector: sales_channel
      value: "Mercado Libre"
    - type: "selector_match"
      selector: marketplace_presence
      value: true
  mode: "any"  # any | all

included_tanks:
  - operational_pathology_core
  - evidence_formula_core
  - marketplace_specific_ml  # tanque específico futuro

required_context:
  - sales_channel_declared
  - at_least_one_symptom

evidence_policy:
  required:
    - evidence_type: export_mercadolibre
      reason: "Necesario para calcular comisiones y envíos reales."
  optional:
    - evidence_type: capturas_panel_ml
      reason: "Ayuda a validar reputación y SLA."

output_policy:
  can_emit:
    - diagnostic_report
    - evidence_gaps
    - recommended_actions
    - ml_specific_warnings
  cannot_emit:
    - benchmark_without_sector
    - financial_projection

safety_policy:
  - "NO diagnosticar rentabilidad ML sin considerar comisiones y envíos"
  - "NO extrapolar tendencias con < 3 meses de datos"
  - "NO asumir stock sincronizado con ML"

compatibility:
  min_runtime: "local_mvp_runtime"
  requires_interrogation_slice: true
```

---

## 7. Política de activación

### 7.1 Cuándo activar un tanque

Un tanque puede activarse por combinación de:

1. **Síntomas detectados** en `InterrogationResult.candidate_symptoms`.
2. **Dominios candidatos** en `InterrogationResult.candidate_domains`.
3. **Selectores estructurales** en `InterrogationResult.business_context`.
4. **Evidencia declarada disponible** (`evidence_available`).
5. **Clasificación ejecutable posible** (`suggested_classification`).
6. **Tipo de documento recibido** (post-interrogatorio, si aplica).

### 7.2 Cuándo desactivar un tanque

Un tanque **debe** desactivarse si:

- falta contexto mínimo (`required_context` no satisfecho);
- evidencia insuficiente y no puede solicitarse;
- dominio incompatible con el caso;
- el usuario **no confirma** el dolor reformulado;
- se viola cualquier `safety_constraint`;
- el estado es `BLOCKED_INSUFFICIENT_CONTEXT`.

### 7.3 Activación no es diagnóstico

Activar un tanque significa:

- cargar sus preguntas de desambiguación;
- habilitar sus hipótesis;
- preparar sus pedidos de evidencia;
- sugerir sus clasificaciones ejecutables.

**No** significa afirmar que la patología existe.

### 7.4 Orden de resolución

```text
raw_text + structured_selectors
    ↓
interrogation_slice → InterrogationResult
    ↓
tank_selection (evalúa activation_conditions)
    ↓
tanques activos (0..N)
    ↓
evidence_request (basado en tanques activos)
    ↓
evidencia recibida
    ↓
análisis (solo si tanque + evidencia + clasificación compatibles)
```

---

## 8. Relación con fase semántico-dialéctica

La fase semántico-dialéctica (documentada en
`SMARTPYME_SEMANTIC_DIALECTIC_PHASE.md`) ocurre **antes** de la selección de
tanques.

Secuencia integrada:

```text
1. Captura mínima estructural (selectores)
2. Relato libre del usuario (texto/audio)
3. Conservación literal del relato
4. Reformulación del sistema
5. Confirmación/corrección del usuario
6. Extracción de síntomas            ← aquí opera interrogation_slice
7. Hipótesis abiertas
8. Desambiguación
9. Selección tentativa de tanques    ← aquí opera tank_selection
10. Evidencia requerida              ← aquí emite evidence_request
11. Preparación para análisis
```

Los tanques **no reemplazan** la conversación.
Los tanques **aportan**:

- preguntas específicas de desambiguación;
- evidencia concreta requerida;
- límites claros sobre qué se puede afirmar;
- clasificación ejecutable sugerida.

---

## 9. Relación con InterrogationResult

El `InterrogationResult` (definido en `SMARTPYME_INTERROGATION_SLICE.md` y en
`pymia/smartpyme/interrogation.py`) es la **entrada** principal del selector
de tanques.

### Campos consumidos

| Campo | Uso en selección |
|---|---|
| `raw_input` | Validación de no-vacío |
| `business_context` | Match contra `activation_conditions` tipo selector |
| `semantic_signals` | Refuerzo de match léxico |
| `candidate_symptoms` | Match contra `supported_symptoms` |
| `candidate_domains` | Match contra `supported_domains` |
| `evidence_needs` | Cruce con `required_evidence` |
| `status` | Gate de activación (no activar si BLOCKED) |
| `suggested_classification` | Cruce con `supported_classifications` |

### Reglas

- Si `status == BLOCKED_INSUFFICIENT_CONTEXT` → ningún tanque se activa.
- Si `candidate_symptoms` está vacío y `business_context` también → no activar.
- Un tanque puede activarse con síntomas **o** selectores, pero nunca con
  selectores aislados si no hay señal en `raw_input`.

---

## 10. Relación con EvidenceRequest

Un KnowledgeTank **no ejecuta análisis**.
Un KnowledgeTank **produce o alimenta** un `EvidenceRequest`.

### EvidenceRequest derivado de un tanque

```yaml
evidence_request:
  tenant_id: <tenant>
  conversation_id: <conv>
  source_tank: "operational_pathology_core"
  source_tank_version: "1.0.0"
  items:
    - evidence_type: "excel_ventas_costos"
      required_fields: [fecha, producto, precio_venta, costo]
      reason: "Permite contrastar la hipótesis de margen erosionado."
      sufficiency_criteria: ">= 3 meses de datos, >= 10 productos"
      enables_hypotheses:
        - margen_erosionado
    - evidence_type: "excel_proveedores"
      required_fields: [proveedor, cuit, razon_social]
      reason: "Permite verificar proveedores duplicados."
      sufficiency_criteria: "al menos 20 filas"
      enables_hypotheses:
        - proveedores_duplicados
```

### Contrato con SCN EvidenceCandidate

Cuando el usuario entrega la evidencia, ésta ingresa como
`EvidenceCandidate` (ver `docs/contracts/scn/evidence_candidate.schema.json`)
y es validada por la Boundary Layer antes de ser consumida por el tanque.

El tanque **nunca** confía en evidencia sin validar.

---

## 11. Relación con runtime real actual

### Capacidades existentes en Git real (HEAD `a50f9eb`)

- `excel_diagnostic` (slice de diagnóstico de Excel)
- `supplier_duplicate_check` (spec y slice de proveedores duplicados)
- `interrogation_slice` (detección determinística de síntomas)
- documentación de taxonomía de interrogatorio
- documentación de fase semántico-dialéctica
- selectores estructurales documentados
- catálogos JSON de patologías y fórmulas (solo documentación)

### Capacidades NO implementadas en Git real

- `--classification auto` (routing automático)
- `--html-out` (output HTML)
- tanque loader
- selector runtime de tanques
- `TankSelectionResult`
- `EvidenceRequest` formal
- `DomainPack` ejecutable
- validación YAML de tanques
- demo package reproducible

### Implicancia

Este contrato es **diseño normativo**.
Cualquier implementación futura debe:

1. respetar los límites de seguridad;
2. no activar tanques sin `InterrogationResult` previo;
3. no emitir diagnósticos sin evidencia validada;
4. no asumir capacidades que el runtime no tiene.

---

## 12. Dos tanques iniciales canónicos

### 12.1 SMARTPYME_OPERATIONAL_PATHOLOGY_TANK

**Propósito:**
Mapear lenguaje crudo, señales y síntomas a patologías operacionales PyME
sin diagnosticar.

**Contenido:**

- síntomas soportados (9 síntomas del interrogation_slice);
- señales léxicas asociadas a cada síntoma;
- preguntas de desambiguación por síntoma;
- evidencia sugerida por síntoma;
- patologías candidatas (mapeo a `pathology_catalog.v1.json`);
- límites de afirmación;
- outputs permitidos.

**Activadores:**

- cualquier síntoma de `candidate_symptoms` presente en `supported_symptoms`;
- dominio candidato en `supported_domains`.

**Desactivadores:**

- `status == BLOCKED_INSUFFICIENT_CONTEXT`;
- sin síntomas y sin selectores compatibles;
- violación de `safety_constraints`.

**Evidencia requerida típica:**

- `DESCUADRE_DINERO` → excel financiero o extracto bancario;
- `MARGEN_DUDOSO` → excel ventas + costos;
- `DATOS_DUPLICADOS` → excel proveedores con CUIT;
- `STOCK_INCONSISTENTE` → excel stock + ventas;
- `SOBRECARGA_MANUAL` → descripción del flujo + archivos involucrados.

**Relación con runtime real:**

- compatible con `excel_diagnostic` cuando hay Excel;
- compatible con `supplier_duplicate_check` cuando hay maestro proveedores.

---

### 12.2 SMARTPYME_EVIDENCE_AND_FORMULA_TANK

**Propósito:**
Mapear evidencia disponible a tipos documentales, campos esperados, fórmulas
ejecutables y análisis posibles.

**Contenido:**

- tipos documentales (`excel_ventas_costos`, `excel_proveedores`, etc.);
- campos esperados por tipo;
- reglas de validación básica;
- fórmulas ejecutables (referencias a `formula_catalog.v1.json`);
- hipótesis contrastables por fórmula;
- criterios de suficiencia de evidencia;
- límites de cálculo.

**Activadores:**

- `status` en `[NEEDS_EVIDENCE, EVIDENCE_RECEIVED]`;
- `evidence_available` incluye algún tipo soportado.

**Desactivadores:**

- `evidence_available == NoSe`;
- sin síntomas que requieran cálculo;
- evidencia entregada no supera validación mínima.

**Fórmulas prioritarias:**

- `REN_001_margen_neto_real`
- `LIQ_001_vendido_cobrado`
- `INV_002_rotacion_stock`
- `PYME_011_dso`
- `PYME_013_dso_dpo_gap`
- `PYME_024_liquidez_corriente`
- `PYME_033_concentracion_sku`

**Relación con runtime real:**

- alimenta a `excel_diagnostic` con campos esperados;
- alimenta a `supplier_duplicate_check` con campos de maestro.

---

## 13. Límites de seguridad

Reglas **inviolables** para cualquier KnowledgeTank o DomainPack:

1. **No diagnosticar sin evidencia.**
   Solo se pueden afirmar síntomas candidatos e hipótesis abiertas.

2. **No afirmar causa raíz sin datos suficientes.**
   Se requiere al menos un período completo y evidencia validada.

3. **No usar benchmarks sin contexto sectorial.**
   Nunca comparar contra referencias externas sin industria declarada.

4. **No mezclar dominios.**
   Un tanque de finanzas no debe emitir afirmaciones sobre stock.

5. **No activar tanque solo por selector estructural.**
   Los selectores son contexto, no dolor.

6. **No pedir evidencia excesiva.**
   Máximo 3 tipos de evidencia simultáneos por caso.

7. **No prometer outputs que el runtime no soporta.**
   Si el runtime no tiene HTML, no se sugiere HTML.
   Si el runtime no tiene routing automático, no se afirma routing.

8. **No saltar la fase semántico-dialéctica.**
   Todo caso debe pasar por reformulación y confirmación.

9. **No emitir `OperationalCase` sin material suficiente.**
   Respetar regla del atlas de síntomas y patologías.

---

## 14. Versionado y compatibilidad

### 14.1 Versionado semántico simple

Formato: `MAJOR.MINOR.PATCH`

- **MAJOR**: cambio incompatible en el contrato del tanque (campos, política,
  outputs).
- **MINOR**: agregado de síntomas, fórmulas o preguntas sin romper contrato.
- **PATCH**: correcciones menores, typos, notas.

### 14.2 Referenciación

Todo caso que use un tanque debe registrar:

```yaml
applied_tanks:
  - tank_id: operational_pathology_core
    version: "1.0.0"
  - tank_id: evidence_formula_core
    version: "1.0.0"
```

### 14.3 Compatibilidad runtime

Cada tanque declara:

```yaml
compatibility:
  min_runtime: "local_mvp_runtime"
  requires_interrogation_slice: true
```

Si el runtime es anterior al mínimo, el tanque **no debe activarse**.

### 14.4 Evolución

Si un tanque cambia de MAJOR:

- los casos antiguos conservan la versión aplicada;
- los casos nuevos usan la versión vigente;
- no se migran casos en proceso automáticamente.

---

## 15. Gaps conocidos

### Críticos (bloquean implementación)

- **No existe loader YAML de tanques.**
- **No existe selector runtime de tanques.**
- **No existe `TankSelectionResult` formal.**
- **No existe contrato de `EvidenceRequest`.**
- **No existe validación JSON Schema de tanques.**

### High (riesgo de mal funcionamiento)

- **No existe DomainPack ejecutable.**
- **No existe política de activación implementada.**
- **No existe persistencia de `applied_tanks` por caso.**

### Medium (mejoran mantenibilidad)

- **Catálogos JSON de patologías y fórmulas no están integrados al runtime.**
- **No hay ejemplo ejecutable end-to-end con tanques.**
- **No hay tests de contratos YAML.**

### Future (no hacer ahora)

- Benchmarks por sector.
- Multi-idioma.
- Tanques por industria específicos (textil, agro, construcción).
- Hot-swap en runtime.

---

## 16. Roadmap posterior

Máximo 4 frentes recomendados, en orden de prioridad:

### 1. SMARTPYME_OPERATIONAL_PATHOLOGY_TANK_DOC

Documentar en YAML el primer tanque canónico con:
- 5–7 patologías PyME mapeadas a `pathology_catalog.v1.json`;
- síntomas, señales, preguntas, evidencia, límites;
- ejemplo completo de activación.

### 2. SMARTPYME_EVIDENCE_AND_FORMULA_TANK_DOC

Documentar en YAML el segundo tanque canónico con:
- tipos documentales + campos esperados;
- fórmulas prioritarias de `formula_catalog.v1.json`;
- hipótesis contrastables;
- criterios de suficiencia.

### 3. SMARTPYME_TANK_SELECTION_SLICE

Implementar el slice mínimo que:
- recibe `InterrogationResult`;
- evalúa `activation_conditions`;
- devuelve `TankSelectionResult` con tanques activos;
- genera `EvidenceRequest` derivado.

### 4. SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST

Implementar la persistencia de:
- `InterrogationResult`;
- `TankSelectionResult`;
- `EvidenceRequest`;
- `EvidenceCandidate` recibida;
- `applied_tanks` por caso.

---

## Documentos relacionados

- `SMARTPYME_INTERROGATION_TAXONOMY.md` — capa taxonómica
- `SMARTPYME_SEMANTIC_DIALECTIC_PHASE.md` — capa conversacional
- `SMARTPYME_INTERROGATION_SLICE.md` — slice determinístico implementado
- `SMARTPYME_LOCAL_MVP_RUNTIME.md` — runtime real actual
- `SMARTPYME_SUPPLIER_DUPLICATE_CHECK_SPEC.md` — spec de clasificación existente
- `docs/ingenieria_conversacional.PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md`
- `docs/ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md`
- `docs/pathology_catalog.v1.json`
- `docs/formula_catalog.v1.json`
- `docs/contracts/scn/evidence_candidate.schema.json`

---

*Este documento es normativo para diseño. No implica implementación runtime.*
