# PYMIA_DOCTRINAL_AUDIT

## Estado del documento

Fase 0 — Auditoría doctrinal inicial.

**No es un índice canónico.**
**No reemplaza a `DOCUMENTATION_INDEX.md` ni a `INVENTARIO_CANONICO.md`.**
**No autoriza runtime, MCP, jobs, workflows ni orquestación.**
**Rige `ARCHITECTURE_GUARDRAILS.md`.**

---

## 1. Propósito

Este documento constituye la **Fase 0** de consolidación doctrinal.

Su objetivo no es reemplazar la documentación existente, sino:

1. Reconocer la masa documental real del repositorio.
2. Clasificarla por capas conceptuales.
3. Identificar qué documentos ya existentes pueden alimentar la construcción de los tres documentos doctrinales organizacionales pendientes.
4. Señalar duplicaciones probables sin declararlas cerradas.
5. Proponer un lote mínimo posterior (3 documentos) sin ejecutar fusiones ni movimientos.

No declara V1 oficial de ningún documento.
No mueve, renombra ni borra archivos.
No modifica memoria.
No toca `docs/mermaid/`.

---

## 2. Inventario doctrinal por capas

El repositorio `PymIA/docs/` contiene ~190 entradas documentales. A los fines de esta auditoría se clasifican en siete capas conceptuales.

### Capa A — Doctrina fundacional / cosmovisión

Documentos que definen qué es PymIA, qué no es, y desde qué marco conceptual opera.

| Documento | Ubicación | Rol doctrinal |
|-----------|-----------|---------------|
| `cosmovision-clinico-operacional.md` | `docs/fundamentos/` | Tesis central: PymIA como sistema clínico-operacional |
| `organismo-pyme.md` | `docs/fundamentos/` | Analogía biológica: PyME como organismo incompleto |
| `metodo-hipotetico-deductivo.md` | `docs/fundamentos/` | Método de razonamiento: dolor → síntoma → hipótesis → evidencia → diagnóstico |
| `primer-tiempo-logico.md` | `docs/fundamentos/` | Contrato de primer contacto (anamnesis originaria) |
| `SMARTPYME_LABORATORIO_PYME_Y_ESTABILIZACION_OPERACIONAL.md` | `docs/vision/` | Placeholder (fuente externa a incorporar) |
| `SMARTPYME_MVP_REALISTA_Y_FILOSOFIA_OPERACIONAL.md` | `docs/vision/` | Placeholder (fuente externa a incorporar) |
| `DOCTRINA_ROBUSTEZ_INCREMENTAL_Y_MIGRACION_MVP.md` | `docs/` (raíz) | Abandono del lenguaje MVP; robustez incremental |
| `PYMIA_AGENT_MASTER_PLAN.md` | `docs/` (raíz) | Plan maestro de evolución OS → Agente (2026-05-29) |

**Observación:** Los dos documentos de `vision/` son placeholders explícitos. No deben reconstruirse desde memoria. Su contenido real debe incorporarse cuando esté disponible.

---

### Capa B — Epistemología

Documentos que definen cómo PymIA construye, valida y comunica conocimiento.

| Documento | Ubicación | Rol doctrinal |
|-----------|-----------|---------------|
| `contrato-epistemologico-smartgraph.md` | `docs/epistemologia/` | ADR-EP-001: FactNode / SignalNode / HypothesisNode; bloqueo en cascada |
| `modelo-verdad-soberania.md` | `docs/epistemologia/` | ADR-EP-003: HumanInputNode / OperationalTruthNode / TruthConflict |
| `protocolo-conversacional-hermes.md` | `docs/epistemologia/` | ADR-EP-002: Estados epistemológicos (CONFIRMADO/INFERIDO/PENDIENTE/BLOQUEADO/DECISION_REQUERIDA) y modos (DIOS/HIBRIDO/INVESTIGADOR) |

**Observación:** Los tres ADRs epistemológicos forman un bloque coherente y son la base directa de cualquier futuro documento de Knowledge Lifecycle o Epistemic Core.

---

### Capa C — Arquitectura de sistema

Documentos que definen fronteras, responsabilidades y límites del sistema.

| Documento | Ubicación | Rol doctrinal |
|-----------|-----------|---------------|
| `arquitectura-maestra.md` | `docs/arquitectura/` | Arquitectura canónica: Core + Domain Packs + Knowledge Tanks |
| `orchestration-boundary.md` | `docs/arquitectura/` | Boundary Hermes/PymIA/BEM; AuditBoundaryGraph |
| `palantir-principles.md` | `docs/arquitectura/` | Principios éticos y conceptuales (archivo) |
| `SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md` | `docs/arquitectura/` | **SUPERADO** — ver `DEPRECATED_DOCS.md` |
| `domain-classification.md`, `entropy-routing.md`, `capability-runtime.md`, `harness-engineering.md` | `docs/arquitectura/` | Clasificados como **ARCHIVO** por `DEPRECATED_DOCS.md` |
| `SCN_001_SOVEREIGN_COMPUTATION_BOUNDARY.md`, `SCN_002_CONTRACT_VALIDATION_LAYER_DESIGN.md` | `docs/arquitectura/` | Frontera de cómputo soberano |
| `TECH_DEBT_REGISTER.md`, `TECH_DEBT_CLOSURE_PLAN_DOCS_ONLY.md` | `docs/arquitectura/` | Registro y plan de deuda técnica |
| `ARCHITECTURE_GUARDRAILS.md` | raíz del repo | Invariantes arquitectónicos; fuente de verdad jerárquica |

**Observación:** `ARCHITECTURE_GUARDRAILS.md` es el documento rector supremo. Toda la capa C se subordina a él.

---

### Capa D — Producto / SmartPyme

Documentos que definen el producto, sus capas y su comportamiento operativo.

| Documento | Ubicación | Rol doctrinal |
|-----------|-----------|---------------|
| `capa-00-canal-entrada.md` | `docs/producto/` | Capa de entrada (canal) |
| `capa-01-admision-epistemologica.md` | `docs/producto/` | Admisión epistemológica |
| `protocolo-anamnesis-mvp.md` | `docs/producto/` | Protocolo de anamnesis |
| `asertividades-operativas.md` | `docs/producto/` | Asertividades operativas |
| `registro-ciclos-operativos.md` | `docs/producto/` | Registro de ciclos |
| `SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md` | `docs/smartpyme/` | Arquitectura de tanques de conocimiento |
| `SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md` | `docs/smartpyme/` | Contrato de tanques |
| `SMARTPYME_EVIDENCE_AND_FORMULA_TANK.md` | `docs/smartpyme/` | Tanque de evidencia y fórmulas |
| `SMARTPYME_OPERATIONAL_PATHOLOGY_TANK.md` | `docs/smartpyme/` | Tanque de patología operacional |
| `SMARTPYME_EVIDENCE_SUFFICIENCY_GATE.md` | `docs/smartpyme/` | Gate de suficiencia de evidencia |
| `SMARTPYME_READY_FOR_ANALYSIS_GATE.md` | `docs/smartpyme/` | Gate de readiness |
| `SMARTPYME_EXECUTION_RESULT_GATE.md` | `docs/smartpyme/` | Gate de resultado |
| `SMARTPYME_INTERROGATION_TAXONOMY.md` | `docs/smartpyme/` | Taxonomía de interrogación |
| `SMARTPYME_DELIVERY_PACKAGE_MINIMAL.md`, `SMARTPYME_DELIVERY_MARKDOWN_MINIMAL.md` | `docs/smartpyme/` | Entregables mínimos |

---

### Capa E — Operativo / Hermes / Telegram

Documentos que describen el comportamiento conversacional, adapters y canales.

| Documento | Ubicación | Rol doctrinal |
|-----------|-----------|---------------|
| `soul.md` | `docs/hermes/` | Identidad conversacional de Hermes |
| `principio-obligatorio-hermes-runtime-orchestrator.md` | `docs/hermes/` | Rol de Hermes como orquestador |
| `boundary-integracion-conversacional.md` | `docs/hermes/` | Boundary de integración |
| `contrato-minimo-integracion-externa.md` | `docs/hermes/` | Contrato mínimo |
| `CONVERSATIONAL_BOUNDARY_POLICY.md` | `docs/hermes/` | Política de frontera conversacional |
| `RUNBOOK_TELEGRAM_DIRECT_RUNTIME.md` | `docs/hermes/` | Runbook Telegram |
| `TELEGRAM_DIRECT_RUNTIME_CHECKPOINT.md` | `docs/hermes/` | Checkpoint runtime |
| `HERMES_BASIC_COMMANDS.md`, `HERMES_OFFICIAL_DOCS_DIGEST.md`, `HERMES_RUNTIME_SOURCE_AUDIT.md` | `docs/hermes/` | Documentación técnica Hermes |
| `HERMES_LOCAL_SCN_SANDBOX_PLAN.md`, `HERMES_LOCAL_SCN_SANDBOX_PREP_CHECKLIST.md`, `HERMES_LOCAL_SCN_SANDBOX_COMMAND_PLAN.md` | `docs/hermes/` | Planes de sandbox (NO EJECUCIÓN) |

---

### Capa F — Técnico heredado / migrado / arqueología

Documentos migrados desde SmartPyme con valor arqueológico y de provenance.

| Documento | Ubicación |
|-----------|-----------|
| `migrado_desde_smartpyme_MIGRATION_INDEX.md` | `docs/` (raíz) |
| `migrado_desde_smartpyme_DRIFT_REPORT.md` | `docs/` (raíz) |
| `migrado_desde_smartpyme_MIGRACION_FISICA_FASE3.md` | `docs/` (raíz) |
| `migrado_desde_smartpyme_REPORTE_CIERRE_FASE1.md` | `docs/` (raíz) |
| `migrado_desde_smartpyme_ARQUEOLOGIA_FASE3.md` | `docs/` (raíz) |
| `migrado_desde_smartpyme_formulas_CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md` | `docs/` (raíz) |
| `migrado_desde_smartpyme_conversacional_CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md` | `docs/` (raíz) |
| `migrado_desde_smartpyme_catalogos_SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md` | `docs/` (raíz) |
| `migrado_desde_smartpyme_epistemologia_NOCION_001_ORGANISMO_PYME.md` | `docs/` (raíz) |
| `ingenieria_conversacional.corpus_migrado.md` | `docs/` (raíz) |
| `ingenieria_conversacional.NORMATIVA_v1.md`, `PROTOCOLO_PRIMER_CONTACTO_v1.md`, `CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md`, `CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md`, `ENSAMBLE_DOCUMENTAL_FASE1_v1.md`, `MAPA_INTEGRACION_v1.md`, `PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md` | `docs/` (raíz) |

**Observación:** Esta capa está mayoritariamente clasificada como ARCHIVO por `DEPRECATED_DOCS.md`. No debe eliminarse (preserva provenance), pero tampoco debe usarse como guía de implementación.

---

### Capa G — Contratos, catálogos y ADRs

Documentos que definen contratos formales, catálogos de dominio y decisiones arquitectónicas registradas.

**ADRs:**
- `ADR-004-bem-como-fallback-pasivo.md`
- `ADR-005-document-intelligence-engine.md`
- `ADR-006-tenant-clinical-context-as-input.md`
- `ADR-007-documentation-governance.md`
- `ADR-008-hermes-mcp-client-pymia-mcp-server.md`
- `ADR-010-conversational-anamnesis-contract.md`
- `ADR-015-unsolved-integration-problem.md`
- `ADR-016-resolucion-cognitivo-mnemonica-hermes-pymia.md` (CANDIDATO)

**Contratos:**
- `contratos/contratos-clinicos-operacionales.md`
- `contratos/evidence-chain-v1.md`
- `contratos/owner-decision-v1.md`
- `contracts/pymia_first_clinical_interview_mcp_contract.md`
- `contracts/scn/*` (kernel_request, evidence_candidate, operational_audit_result, render_contract, GLOSSARY)

**Catálogos:**
- `catalogo/atlas-sintomas-patologias.md`
- `catalogo/diseno-catalogo-clinico.md`
- `catalogo/anamnesis-y-catalogos.md`
- `formula_catalog.v1.json` + schema
- `pathology_catalog.v1.json`

---

## 3. Documentos que pueden alimentar MODEL / IDENTITY / HEALTH

Los tres documentos doctrinales organizacionales pendientes no se escriben desde cero. Existe material conceptual ya presente en el repositorio que puede alimentarlos.

### Para `PYMIA_ORGANIZATIONAL_MODEL_THEORY.md`

| Documento fuente | Aporte potencial |
|------------------|------------------|
| `fundamentos/organismo-pyme.md` | Analogía biológica; PyME como organismo incompleto; dueño como variable dinámica |
| `fundamentos/cosmovision-clinico-operacional.md` | Topología operacional; tensiones (tiempo/dinero/stock/caja/deuda/margen); modelo gaussiano operacional |
| `arquitectura/arquitectura-maestra.md` | Core + Domain Packs; roles del conocimiento (Catálogo/Tanque/Caso) |
| `epistemologia/contrato-epistemologico-smartgraph.md` | Nodos (entidades, eventos, relaciones, hipótesis, contradicciones, vigencias) |
| `vision/SMARTPYME_LABORATORIO_PYME_Y_ESTABILIZACION_OPERACIONAL.md` | PyME como organismo operacional (placeholder — requiere fuente real) |

### Para `PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md`

| Documento fuente | Aporte potencial |
|------------------|------------------|
| `fundamentos/organismo-pyme.md` | Dueño como variable no constante; excepciones y redefinición de prioridades |
| `epistemologia/modelo-verdad-soberania.md` | HumanInputNode vs OperationalTruthNode vs TruthConflict; soberanía del dueño |
| `epistemologia/protocolo-conversacional-hermes.md` | Identidad conversacional; modos DIOS/HIBRIDO/INVESTIGADOR |
| `hermes/soul.md` | Identidad conversacional de Hermes como proxy |
| `producto/regla-identidad-conversacional-pymia.md` | Regla de identidad conversacional |

**Observación:** La teoría de identidad emergente (4 identidades: declarada/observada/deseada/percibida; 3 capas: núcleo/adaptable/periférica) **no tiene fuente previa** en el repo. Es doctrina nueva.

### Para `PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md`

| Documento fuente | Aporte potencial |
|------------------|------------------|
| `fundamentos/cosmovision-clinico-operacional.md` | Capa imperativa vs capa clínica; homeostasis operacional; campana de Gauss operativa (centro/márgenes) |
| `fundamentos/metodo-hipotetico-deductivo.md` | Método de detección: dolor → síntoma → hipótesis → evidencia |
| `catalogo/atlas-sintomas-patologias.md` | Catálogo de síntomas y patologías |
| `smartpyme/SMARTPYME_OPERATIONAL_PATHOLOGY_TANK.md` | Tanque de patología operacional |
| `smartpyme/SMARTPYME_EVIDENCE_SUFFICIENCY_GATE.md` | Gate de suficiencia (cuándo hay evidencia suficiente para diagnóstico) |
| `migrado_desde_smartpyme_epistemologia_NOCION_001_ORGANISMO_PYME.md` | Noción 001 — organismo PyME (arqueología) |
| `ingenieria_conversacional.PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md` | Patologías PyME y tanques de conocimiento |

**Observación:** La teoría de salud emergente (7 dimensiones, 7 órganos funcionales, fragilidad vs enfermedad, resiliencia) **no tiene fuente previa directa**. Es doctrina nueva que se apoya conceptualmente en la analogía biológica existente.

---

## 4. Duplicaciones probables (requieren lectura)

Las siguientes agrupaciones parecen solaparse conceptualmente. **No se declaran como duplicaciones ciertas** hasta lectura cruzada completa.

### 4.1 Anamnesis / primer contacto

- `fundamentos/primer-tiempo-logico.md`
- `producto/protocolo-anamnesis-mvp.md`
- `ADR-010-conversational-anamnesis-contract.md`
- `ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md`
- `catalogo/anamnesis-y-catalogos.md`

**Hipótesis:** Cinco documentos tocando el mismo momento (primer contacto). Probablemente requieren consolidación en un único contrato de primer contacto, preservando `primer-tiempo-logico.md` como fundamento conceptual.

### 4.2 Catálogos de patología / síntomas

- `catalogo/atlas-sintomas-patologias.md`
- `catalogo/diseno-catalogo-clinico.md`
- `migrado_desde_smartpyme_catalogos_SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md`
- `ingenieria_conversacional.PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md`
- `smartpyme/SMARTPYME_OPERATIONAL_PATHOLOGY_TANK.md`
- `pathology_catalog.v1.json`

**Hipótesis:** Múltiples capas (diseño, atlas, tanque, catálogo JSON) del mismo concepto. Requiere consolidación en una teoría de patología unificada.

### 4.3 Epistemología / verdad

- `epistemologia/contrato-epistemologico-smartgraph.md` (ADR-EP-001)
- `epistemologia/modelo-verdad-soberania.md` (ADR-EP-003)
- `epistemologia/protocolo-conversacional-hermes.md` (ADR-EP-002)
- `ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md`

**Hipótesis:** Los 3 ADRs son coherentes y probablemente deben consolidarse en un único documento de Epistemic Core. El catálogo de hipótesis y evidencia es material operativo derivado.

### 4.4 Fórmulas / cálculo

- `ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md`
- `migrado_desde_smartpyme_formulas_CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md`
- `formula_catalog.v1.json` + schema
- `smartpyme/SMARTPYME_EVIDENCE_AND_FORMULA_TANK.md`

**Hipótesis:** Capas (documento conceptual, documento migrado, catálogo JSON, tanque runtime) del mismo concepto. Probablemente deben consolidarse preservando el catálogo JSON como fuente técnica.

### 4.5 Hermes / boundary conversacional

- `hermes/soul.md`
- `hermes/boundary-integracion-conversacional.md`
- `hermes/contrato-minimo-integracion-externa.md`
- `hermes/CONVERSATIONAL_BOUNDARY_POLICY.md`
- `arquitectura/orchestration-boundary.md`
- `arquitectura/SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md` (SUPERADO)

**Hipótesis:** Seis documentos tocando la frontera conversacional. Requiere consolidación en un único documento de política conversacional que respete `orchestration-boundary.md` como canónico y deprecie explícitamente `SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md`.

### 4.6 Ingeniería conversacional migrada

Los 8 archivos `ingenieria_conversacional.*.md` y `ingenieria_conversacional.README.md` son corpus migrado desde SmartPyme.

**Hipótesis:** `DEPRECATED_DOCS.md` propone borrar `ingenieria_conversacional.README.md` por redundante con `DOCUMENTATION_INDEX.md`. El resto del corpus es arqueología y debe preservarse pero no usarse como guía activa.

---

## 5. Recomendación de ubicación canónica para doctrina organizacional

La doctrina organizacional emergente (MODEL / IDENTITY / HEALTH / PATHOLOGY / INTERVENTION / PROGNOSIS / DECISION / CAPABILITY / GOVERNANCE) **no debe dispersarse** entre las carpetas existentes.

### Ubicación recomendada

```
PymIA/docs/
├── doctrina/                              ← NUEVA CARPETA
│   ├── organizacional/                    ← NUEVA SUBCARPETA
│   │   ├── ORGANIZATIONAL_MODEL_THEORY.md
│   │   ├── ORGANIZATIONAL_IDENTITY_THEORY.md
│   │   ├── ORGANIZATIONAL_HEALTH_MODEL.md
│   │   ├── ORGANIZATIONAL_PATHOLOGY_THEORY.md
│   │   ├── ORGANIZATIONAL_INTERVENTION_THEORY.md
│   │   ├── ORGANIZATIONAL_PROGNOSIS_THEORY.md
│   │   ├── ORGANIZATIONAL_DECISION_QUALITY_THEORY.md
│   │   ├── ORGANIZATIONAL_DECISION_CAPABILITY_THEORY.md
│   │   └── ORGANIZATIONAL_GOVERNANCE_THEORY.md
│   └── epistemica/                        ← NUEVA SUBCARPETA
│       ├── EPISTEMIC_CORE.md
│       ├── KNOWLEDGE_EXTRACTION_CONTRACT.md
│       ├── KNOWLEDGE_LIFECYCLE_MANAGEMENT.md
│       └── OPERATOR_MODEL.md
```

### Razones

1. **Separa doctrina de especificación técnica.** Las carpetas existentes (`arquitectura/`, `producto/`, `smartpyme/`, `hermes/`) contienen especificaciones operativas. La doctrina organizacional es de orden conceptual superior.

2. **Permite coexistencia sin conflicto.** Los documentos existentes siguen rigiendo runtime. La doctrina nueva rige comprensión.

3. **Facilita el lote mínimo posterior.** Los 3 primeros documentos (MODEL/IDENTITY/HEALTH) viven juntos y pueden referenciarse entre sí sin cruzar carpetas.

4. **No rompe `DOCUMENTATION_INDEX.md`.** La nueva carpeta se agrega como entrada nueva, no modifica entradas existentes.

### Alternativa considerada y descartada

**Alternativa:** Ubicar los documentos en `docs/fundamentos/` o `docs/vision/`.

**Descarte:** `fundamentos/` ya contiene 4 documentos con rol específico (cosmovisión, método, organismo, primer tiempo). Agregar 9 documentos organizacionales allí diluiría su propósito. `vision/` contiene placeholders pendientes de fuente real; no debe recibir doctrina nueva hasta resolverse.

---

## 6. Lote mínimo posterior

Una vez aprobada esta auditoría, el próximo paso es escribir 3 documentos doctrinales nuevos, sin fusionar, mover ni borrar nada de lo existente.

### Documento 1: `PYMIA_ORGANIZATIONAL_MODEL_THEORY.md`

**Pregunta que responde:** ¿Qué es una organización PyME para PymIA?

**Fuentes a usar:**
- `fundamentos/organismo-pyme.md` (analogía biológica)
- `fundamentos/cosmovision-clinico-operacional.md` (topología operacional)
- `epistemologia/contrato-epistemologico-smartgraph.md` (nodos y relaciones)

**Conceptos a definir:**
- Unidad mínima: compromiso de intercambio
- 5 dimensiones estructurales (identidad, intercambio, flujo, restricción, decisión)
- 8 invariantes PyME
- Relaciones estructurales con peso
- Restricciones, tensiones, capacidades, dependencias

**No debe contener:**
- Teoría de salud (pertenece a HEALTH)
- Teoría de identidad desarrollada (pertenece a IDENTITY)
- Teoría de aprendizaje (pertenece a LEARNING_MODEL futuro)
- Teoría de decisión (pertenece a DECISION_QUALITY futuro)

### Documento 2: `PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md`

**Pregunta que responde:** ¿Qué hace que una organización siga siendo ella misma a través del tiempo?

**Fuentes a usar:**
- `fundamentos/organismo-pyme.md` (dueño como variable dinámica)
- `epistemologia/modelo-verdad-soberania.md` (HumanInputNode / OperationalTruthNode / TruthConflict)
- `epistemologia/protocolo-conversacional-hermes.md` (modos DIOS/HIBRIDO/INVESTIGADOR)

**Conceptos a definir:**
- Identidad declarada vs observada vs deseada vs percibida
- Núcleo persistente / Capa adaptable / Capa periférica
- Persistencia vs evolución
- Crisis de identidad (4 tipos)
- Muerte ontológica
- Evolución coherente

**No debe contener:**
- Redefinición de organización (ya hecha en MODEL)
- Teoría de gobernanza (pertenece a GOVERNANCE)
- Teoría de cultura (pendiente)
- Patologías de identidad (pertenecen a PATHOLOGY)

### Documento 3: `PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md`

**Pregunta que responde:** ¿Cuándo una organización está funcionando de manera sana?

**Fuentes a usar:**
- `fundamentos/cosmovision-clinico-operacional.md` (homeostasis operacional; capa imperativa vs clínica; modelo gaussiano)
- `fundamentos/metodo-hipotetico-deductivo.md` (dolor → síntoma → hipótesis → evidencia)
- `catalogo/atlas-sintomas-patologias.md` (síntomas y patologías)
- `smartpyme/SMARTPYME_EVIDENCE_SUFFICIENCY_GATE.md` (gate de suficiencia)

**Conceptos a definir:**
- 7 dimensiones de salud
- 7 órganos funcionales (circulatorio/caja, respiratorio/ventas, digestivo/operaciones, nervioso/decisión, sensorial/lectura, inmunológico/riesgos, reproductivo/aprendizaje)
- Fragilidad vs enfermedad (4 combinaciones)
- Resiliencia con umbral de shock
- Signos tempranos de deterioro
- Equivalentes médicos (fiebre, dolor, inflamación, enfermedad crónica, infarto, cáncer)
- Rentabilidad vs salud (son cosas distintas)

**No debe contener:**
- Catálogo completo de patologías (pertenece a PATHOLOGY)
- Teoría de intervención (pertenece a INTERVENTION)
- Teoría de pronóstico (pertenece a PROGNOSIS)

---

## 7. Observaciones sobre estado de coherencia actual

### 7.1 Coherencia fuerte

Los siguientes bloques presentan coherencia interna alta:

- **Epistemología (ADR-EP-001, 002, 003):** Los tres documentos se refuerzan mutuamente. Comparten vocabulario (FactNode, HypothesisNode, CONFIRMADO/BLOQUEADO, etc.) y no presentan contradicciones evidentes.

- **Fronteras Hermes/PymIA/BEM:** `orchestration-boundary.md`, `ARCHITECTURE_GUARDRAILS.md` y `principio-obligatorio-hermes-runtime-orchestrator.md` son coherentes en la separación de roles.

- **Método hipotético-deductivo:** `metodo-hipotetico-deductivo.md` es consistente con `primer-tiempo-logico.md` y con el flujo canónico de `arquitectura-maestra.md`.

### 7.2 Tensiones conceptuales detectadas

**Tensión 1: Cosmovisión clínica vs Agente conversacional**

`cosmovision-clinico-operacional.md` (2026-05) describe PymIA como "sistema clínico-operacional" donde Hermes conversa y SmartCounter Core calcula.

`PYMIA_AGENT_MASTER_PLAN.md` (2026-05-29) propone evolucionar a "PymIA Agent" con LLM operator (PydanticAI) + ChromaDB + Langfuse.

**No son contradictorios**, pero el Agent Master Plan introduce capas (Vector memory, Langfuse, ChromaDB) que no estaban presentes en la cosmovisión original. Requiere reconciliación doctrinal antes de implementación.

**Tensión 2: Robustez incremental vs Plan maestro por fases**

`DOCTRINA_ROBUSTEZ_INCREMENTAL_Y_MIGRACION_MVP.md` abandona el lenguaje MVP.

`PYMIA_AGENT_MASTER_PLAN.md` usa explícitamente "MVP" y divide en Fases 0-5.

**Contradicción terminológica real.** El Agent Master Plan debería alinearse con la doctrina de robustez incremental antes de ejecutarse.

**Tensión 3: Placeholders de visión sin fuente real**

Los dos documentos de `docs/vision/` son placeholders explícitos. `INVENTARIO_CANONICO.md` los marca como "FUENTE_EXTERNA_A_INCORPORAR". Sin embargo, `DEPRECATED_DOCS.md` los clasifica como ARCHIVO.

**Inconsistencia de estado.** Un documento no puede ser simultáneamente "pendiente de fuente real" y "archivo histórico". Requiere decisión: o se incorpora la fuente real, o se reclasifican como ARCHIVO definitivo.

### 7.3 Documentos sin estado declarado

Varios documentos en `docs/hermes/`, `docs/smartpyme/` y `docs/transient-design/` no tienen estado explícito (VIGENTE / ARCHIVO / SUPERADO) en su encabezado ni en `DOCUMENTATION_INDEX.md`. Esto dificulta saber si rigen runtime o son historia.

---

## 8. Regla final

```
Esta auditoría es una fotografía.
No es una decisión.

No mueve archivos.
No borra archivos.
No reescribe doctrina.
No autoriza runtime.

Su función es que el próximo lote
se escriba sobre evidencia documental real,
no sobre suposición.

Cuando se escriban los próximos 3 documentos
(MODEL, IDENTITY, HEALTH),
esta auditoría debe citarse como insumo.

Y cuando se actualice,
debe preservarse su versión anterior
como evidencia de evolución doctrinal.
```

---

## 9. Próximo paso recomendado

1. **Aprobar esta auditoría** como documento de Fase 0.
2. **Crear la carpeta `docs/doctrina/organizacional/`** (vacía).
3. **Escribir en orden:**
   - `PYMIA_ORGANIZATIONAL_MODEL_THEORY.md`
   - `PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md`
   - `PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md`
4. **No tocar los 190 documentos existentes** durante este lote.
5. **Al completar el lote, actualizar `DOCUMENTATION_INDEX.md`** para reflejar las 3 nuevas entradas.

---

**Documento cerrado como V1 de auditoría.**

Listo para aprobación y ejecución del lote mínimo posterior.
