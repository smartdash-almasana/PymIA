# PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING

## Estado del documento

**Tipo:** Documento de transición doctrina → software
**Estado:** CANDIDATE_V1
**Núcleo doctrinal de referencia:** 10 documentos organizacionales cerrados

---

## 1. Propósito

Este documento es el puente formal entre la doctrina organizacional (cerrada como núcleo en 10 documentos) y los artefactos de software que eventualmente se materializarán como contratos Python.

**Este documento NO es:**
- Código
- Schema Pydantic
- Dataclass
- Modelo de base de datos
- Especificación de API

**Este documento ES:**
- Especificación conceptual de artefactos
- Trazabilidad doctrina → software
- Contrato de frontera entre dominio e infraestructura
- Mapa de composición jerárquica
- Guía para implementación futura

### Regla fundamental

```
Todo artefacto de software en PymIA
debe tener trazabilidad directa
a un concepto definido en la doctrina.

Todo concepto doctrinal operativo
debe tener un artefacto asignado
o estar explícitamente marcado como futuro.
```

---

## 2. Principios de mapping

### Principio 1 — Doctrina primero, artefacto después

Ningún artefacto se crea porque "conviene técnicamente".
Solo se crea porque la doctrina lo requiere.

### Principio 2 — Dominio puro, infraestructura separada

Los artefactos de dominio no conocen:
- base de datos
- HTTP
- colas de mensajes
- LLM providers
- frameworks
- ORMs

Los artefactos de infraestructura orquestan los de dominio sin contaminarlos.

### Principio 3 — Un concepto doctrinal, un artefacto

Salvo excepciones documentadas, cada concepto doctrinal se mapea a un único artefacto.

Fusiones arbitrarias violan trazabilidad.
Duplicaciones generan divergencia.

### Principio 4 — Artefacto sin doctrina es sospechoso

Si durante la implementación emerge un artefacto sin respaldo doctrinal, debe:
- documentarse como "huérfano de doctrina"
- evaluarse si requiere nuevo documento doctrinal
- o descartarse si es accidente de implementación

### Principio 5 — Inmutabilidad preferida

Los value objects deben ser inmutables.
Las entidades mutan solo mediante métodos de dominio con semántica clara.

### Principio 6 — IDs generados por dominio

Los identificadores de entidades se generan en la capa de dominio, no en la de persistencia.

---

## 3. Tabla de mapping completa

| # | Artefacto | Tipo | Capa | Documento fuente | Sección |
|---|-----------|------|------|------------------|---------|
| 1 | OrganizationProfile | Entidad | Dominio | MODEL_THEORY | §12 |
| 2 | ExchangeCommitment | Value Object | Dominio | MODEL_THEORY | §4 |
| 3 | StructuralRelationship | Value Object | Dominio | MODEL_THEORY | §7 |
| 4 | OrganizationalConstraint | Value Object | Dominio | MODEL_THEORY | §8 |
| 5 | StructuralTension | Value Object | Dominio | MODEL_THEORY | §9 |
| 6 | OrganizationalCapability | Value Object | Dominio | MODEL_THEORY | §10 |
| 7 | OrganizationalDependency | Value Object | Dominio | MODEL_THEORY | §11 |
| 8 | OrganizationalIdentity | Entidad | Dominio | IDENTITY_THEORY | §2-3 |
| 9 | IdentityLayer | Value Object | Dominio | IDENTITY_THEORY | §3 |
| 10 | IdentityCrisis | Value Object | Dominio | IDENTITY_THEORY | §6 |
| 11 | HealthAssessment | Snapshot | Infra | HEALTH_MODEL | §5 |
| 12 | FunctionalOrgan | Value Object | Dominio | HEALTH_MODEL | §9 |
| 13 | FragilityIndicator | Value Object | Dominio | HEALTH_MODEL | §5-6 |
| 14 | OrganizationalSymptom | Value Object | Dominio | PATHOLOGY_THEORY | §2 |
| 15 | OrganizationalPathology | Entidad | Dominio | PATHOLOGY_THEORY | §3-4 |
| 16 | DiagnosticReport | Snapshot | Infra | PATHOLOGY_THEORY | §7 |
| 17 | InterventionPlan | Entidad | Dominio | INTERVENTION_THEORY | §3 |
| 18 | InterventionAction | Value Object | Dominio | INTERVENTION_THEORY | §4 |
| 19 | IatrogenicRisk | Value Object | Dominio | INTERVENTION_THEORY | §5 |
| 20 | PrognosisAssessment | Snapshot | Infra | PROGNOSIS_THEORY | §3 |
| 21 | OrganizationalTrajectory | Value Object | Dominio | PROGNOSIS_THEORY | §5 |
| 22 | PointOfNoReturn | Value Object | Dominio | PROGNOSIS_THEORY | §6 |
| 23 | InterventionWindow | Value Object | Dominio | PROGNOSIS_THEORY | §7 |
| 24 | GovernanceProfile | Entidad | Dominio | GOVERNANCE_THEORY | §4 |
| 25 | AuthorityStructure | Value Object | Dominio | GOVERNANCE_THEORY | §5 |
| 26 | DecisionRecord | Entidad | Dominio | DECISION_QUALITY | §3 |
| 27 | DecisionCapabilityAssessment | Snapshot | Infra | DECISION_CAPABILITY | §4 |
| 28 | LearningCycle | Entidad | Dominio | LEARNING_MODEL | §3 |

**Totales:**
- Entidades: 9
- Value Objects: 15
- Snapshots (evaluaciones de infraestructura): 4
- **Total: 28 artefactos**

---

## 4. Jerarquía de composición

### Nivel 0 — Átomo
**ExchangeCommitment**

Es la unidad mínima. No se descompone en otros artefactos.
Todo lo demás se construye sobre compromisos de intercambio.

### Nivel 1 — Estructura
- **OrganizationProfile** (compone ExchangeCommitments + restricciones + tensiones + capacidades + dependencias)
- **OrganizationalIdentity** (compone IdentityLayers + posibles crisis)

### Nivel 2 — Estado
- **HealthAssessment** (compone FunctionalOrgans + FragilityIndicators)
- **OrganizationalPathology** (instancia de disfunción con síntomas asociados)
- **GovernanceProfile** (compone AuthorityStructure + mecanismos de coherencia)

### Nivel 3 — Intervención
- **InterventionPlan** (trata patologías mediante InterventionActions)
- **DecisionRecord** (decisión concreta con 8 componentes)
- **LearningCycle** (cierre de aprendizaje con actualización de modelo)

### Nivel 4 — Proyección
- **PrognosisAssessment** (compone Trajectories + PointsOfNoReturn + InterventionWindows)
- **DecisionCapabilityAssessment** (compone DecisionRecords + métricas de sistema)

### Nivel 5 — Coherencia
- **DiagnosticReport** (compone Symptoms + Pathologies + Evidence)
- **GovernanceProfile** en su rol de infraestructura de coherencia

### Reglas de composición

1. Un artefacto de nivel N puede componer artefactos de nivel < N.
2. Un artefacto de nivel N NO puede componer artefactos de nivel > N.
3. Value Objects pueden componerse entre sí del mismo nivel.
4. Las entidades tienen identidad propia (ID) y pueden versionarse.

---

## 5. Clasificación por tipo

### 5.1 Entidades (9)

Tienen identidad propia, ciclo de vida, pueden mutar mediante métodos de dominio.

| Artefacto | Ciclo de vida |
|-----------|---------------|
| OrganizationProfile | Nace con ficha, evoluciona con evidencia, se versiona, se archiva |
| OrganizationalIdentity | Persiste, evoluciona coherentemente, puede morir ontológicamente |
| OrganizationalPathology | Nace con síntoma, se valida con diagnóstico, se cierra con intervención |
| InterventionPlan | Se crea, ejecuta, evalúa, archiva |
| GovernanceProfile | Evoluciona con tamaño organizacional |
| DecisionRecord | Nace con decisión, se cierra con resultado y aprendizaje |
| LearningCycle | Tiene inicio (decisión), proceso (resultado), cierre (aprendizaje) |
| OrganizationalTrajectory | (ver value objects, no es entidad) |
| AuthorityStructure | (ver value objects, no es entidad) |

**Corrección:** 9 entidades confirmadas:
1. OrganizationProfile
2. OrganizationalIdentity
3. OrganizationalPathology
4. InterventionPlan
5. GovernanceProfile
6. DecisionRecord
7. LearningCycle
8. (Reservado para futuro)
9. (Reservado para futuro)

### 5.2 Value Objects (15)

Definen por sus atributos. Son inmutables. No tienen identidad propia.

| # | Artefacto | Atributos esenciales |
|---|-----------|---------------------|
| 1 | ExchangeCommitment | partes + condiciones + tipo |
| 2 | StructuralRelationship | nodos + peso + tipo |
| 3 | OrganizationalConstraint | tipo + magnitud + horizonte |
| 4 | StructuralTension | polo_A + polo_B + estado_actual |
| 5 | OrganizationalCapability | tipo + nivel (declarada/observada/latente/límite) |
| 6 | OrganizationalDependency | nodo + criticidad + tipo |
| 7 | IdentityLayer | tipo (núcleo/adaptable/periférica) + contenido |
| 8 | IdentityCrisis | tipo + divergencia medida |
| 9 | FunctionalOrgan | tipo + estado (sano/estresado/enfermo/fallando/recuperando) |
| 10 | FragilityIndicator | dimensión + severidad |
| 11 | OrganizationalSymptom | manifestación + intensidad |
| 12 | InterventionAction | tipo + dosis + objetivo |
| 13 | IatrogenicRisk | tipo + probabilidad + impacto |
| 14 | OrganizationalTrajectory | tipo + velocidad + dirección |
| 15 | PointOfNoReturn | categoría + umbral + proximidad |
| (extra) | InterventionWindow | inicio + fin + condición |
| (extra) | AuthorityStructure | matriz de decisiones + roles |

### 5.3 Snapshots (4)

Evaluaciones periódicas que componen artefactos de dominio.

| # | Artefacto | Compone |
|---|-----------|---------|
| 1 | HealthAssessment | FunctionalOrgan[] + FragilityIndicator[] |
| 2 | DiagnosticReport | OrganizationalSymptom[] + OrganizationalPathology[] + evidencia |
| 3 | PrognosisAssessment | OrganizationalTrajectory + PointOfNoReturn[] + InterventionWindow[] |
| 4 | DecisionCapabilityAssessment | DecisionRecord[] + métricas del sistema |

### 5.4 Procesos (3 cadenas doctrinales)

No son artefactos instanciables. Son flujos de transformación.

**Cadena clínica:**
```
OrganizationalSymptom
  → OrganizationalPathology (vía diagnóstico)
    → InterventionPlan
      → PrognosisAssessment (proyección)
```

**Cadena decisional:**
```
Evidence + Alternatives + Risk
  → DecisionRecord
    → InterventionAction (ejecución)
      → Result (observación)
```

**Ciclo de aprendizaje:**
```
DecisionRecord
  → Result
    → Comparison
      → Attribution
        → Extraction
          → OrganizationProfile (actualización)
            → LearningCycle (cierre)
```

---

## 6. Separación dominio / infraestructura

### 6.1 Dominio puro (24 artefactos)

No importan nada de:
- base de datos
- HTTP
- LLM
- colas
- frameworks
- logging
- métricas

Solo contienen lógica organizacional.

**Lista completa:**
1. OrganizationProfile
2. ExchangeCommitment
3. StructuralRelationship
4. OrganizationalConstraint
5. StructuralTension
6. OrganizationalCapability
7. OrganizationalDependency
8. OrganizationalIdentity
9. IdentityLayer
10. IdentityCrisis
11. FunctionalOrgan
12. FragilityIndicator
13. OrganizationalSymptom
14. OrganizationalPathology
15. InterventionPlan
16. InterventionAction
17. IatrogenicRisk
18. OrganizationalTrajectory
19. PointOfNoReturn
20. InterventionWindow
21. GovernanceProfile
22. AuthorityStructure
23. DecisionRecord
24. LearningCycle

### 6.2 Infraestructura de evaluación (4 artefactos snapshot)

Componen artefactos de dominio para producir evaluaciones.

| # | Artefacto | Compone |
|---|-----------|---------|
| 1 | HealthAssessment | FunctionalOrgan + FragilityIndicator |
| 2 | DiagnosticReport | OrganizationalSymptom + OrganizationalPathology + evidencia |
| 3 | PrognosisAssessment | OrganizationalTrajectory + PointOfNoReturn + InterventionWindow |
| 4 | DecisionCapabilityAssessment | DecisionRecord[] + métricas |

### 6.3 Reglas de frontera

1. **Dominio nunca importa de infraestructura.**
2. **Infraestructura puede componer dominio.**
3. **Infraestructura puede importar de infraestructura** (evaluaciones pueden combinarse).
4. **Persistencia vive fuera de ambos** (repositorios implementan interfaces que dominio define).

### 6.4 Interfaces de dominio

El dominio define interfaces que infraestructura implementa:
- `OrganizationRepository`
- `PathologyRepository`
- `InterventionRepository`
- `DecisionRepository`
- `LearningRepository`
- `EvidenceStore`

Estas interfaces NO son artefactos, son contratos.

---

## 7. Artefactos huérfanos de doctrina

Lista vacía al inicio de implementación.
Se llena cuando emerge un artefacto en código sin respaldo doctrinal.

**Formato de registro futuro:**

```
| Artefacto | Lugar de aparición | Posible doctrina | Acción |
```

**Acciones posibles:**
- crear documento doctrinal nuevo
- fusionar con artefacto existente
- descartar si es accidente
- marcar como infraestructura técnica

---

## 8. Conceptos doctrinales sin artefacto (todavía)

Estos conceptos están mencionados en la doctrina pero aún no tienen artefacto propio. Quedan marcados como futuros.

| # | Concepto | Mencionado en | Posible artefacto futuro |
|---|----------|---------------|---------------------------|
| 1 | Cultura organizacional | IDENTITY, DECISION_CAPABILITY, GOVERNANCE | OrganizationalCulture |
| 2 | Decision Debt | DECISION_QUALITY | DecisionDebtRecord |
| 3 | Identity Debt | IDENTITY | IdentityDebtRecord |
| 4 | Architecture Decisional | DECISION_CAPABILITY | DecisionArchitecture |
| 5 | SmartPyme Method | AUDIT | (fuera del núcleo organizacional) |
| 6 | Therapeutics | INTERVENTION | TherapeuticProtocol |
| 7 | Operador Organizacional | COGNITIVE_MNEMONIC | OrganizationalOperator |
| 8 | Acción Epistémica | COGNITIVE_MNEMONIC | EpistemicAction |

### Regla para futuros

Cuando un concepto futuro se materialice:
1. Se crea su documento doctrinal
2. Se actualiza este mapping
3. Se actualiza el índice doctrinal
4. Se implementa el artefacto

No se implementa antes de tener doctrina.

---

## 9. Reglas para pasar a contratos Python

### 9.1 Artefactos de dominio → dataclasses puras

```python
# Ejemplo (no implementar todavía)
@dataclass(frozen=True)
class ExchangeCommitment:
    parties: tuple[Party, ...]
    conditions: Conditions
    type: CommitmentType
```

### 9.2 Entidades → dataclass con ID

```python
@dataclass
class DecisionRecord:
    id: UUID
    created_at: datetime
    # ... campos doctrinales
```

### 9.3 Snapshots → servicios evaluadores

```python
class HealthAssessmentBuilder:
    def assess(self, profile: OrganizationProfile) -> HealthAssessment:
        ...
```

### 9.4 IDs generados por dominio

```python
@dataclass
class DecisionRecord:
    id: UUID = field(default_factory=uuid4)
```

No se esperan IDs de base de datos.

### 9.5 Timestamps en UTC

```python
created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### 9.6 Inmutabilidad preferida

```python
@dataclass(frozen=True)
class OrganizationalConstraint:
    ...
```

Las entidades mutan mediante métodos que retornan nueva instancia.

### 9.7 Sin imports técnicos en dominio

```python
# MAL (en archivo de dominio)
from sqlalchemy import Column
from fastapi import APIRouter
from openai import OpenAI

# BIEN (dominio puro)
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
```

### 9.8 Validación en construcción, no en setter

```python
@dataclass(frozen=True)
class PointOfNoReturn:
    category: Category
    threshold: float
    current_value: float

    def __post_init__(self):
        if self.threshold <= 0:
            raise ValueError(...)
```

---

## 10. Riesgos de deriva

### 10.1 Fusiones indebidas

**Riesgo:** Fusionar artefactos que parecen similares pero son distintos.

**Ejemplos específicos:**
- NO fusionar `IdentityLayer` con `IdentityCrisis` (son conceptos distintos)
- NO fusionar `FragilityIndicator` con `OrganizationalSymptom` (fragilidad es estructural, síntoma es observable)
- NO fusionar `PointOfNoReturn` con `InterventionWindow` (umbral vs período)

**Mitigación:** Mantener separación doctrinal aunque parezca redundante.

### 10.2 Duplicaciones indebidas

**Riesgo:** Crear artefactos duplicados por no ver la conexión.

**Ejemplos específicos:**
- NO crear `PathologyCatalog` separado (usar enum dentro de Pathology)
- NO crear `DecisionType` separado (es atributo de DecisionRecord)
- NO crear `HealthDimension` separado (es atributo de HealthAssessment)

**Mitigación:** Consultar este mapping antes de crear artefactos nuevos.

### 10.3 Optimizaciones que violan doctrina

**Riesgo:** El código "optimiza" fusionando conceptos para performance.

**Ejemplos específicos:**
- Guardar HealthAssessment como JSON plano (pierde tipado)
- Mezclar dominio con ORM en la misma clase
- Poner lógica de LLM dentro de OrganizationProfile

**Mitigación:** Revisar contra este mapping en cada PR.

### 10.4 Artefactos emergentes sin doctrina

**Riesgo:** Durante implementación surgen "clases utilitarias" no mapeadas.

**Mitigación:** Registrarlas en §7 como huérfanas y evaluarlas.

### 10.5 Drift de nombres

**Riesgo:** Renombrar artefactos en código sin actualizar mapping.

**Mitigación:** El mapping es la fuente de verdad de nombres.

---

## 11. Relación con documentos previos

### 11.1 PYMIA_DOCTRINAL_INDEX.md

Este mapping es downstream del índice.
Cada artefacto referenciado debe existir en el índice.

Si el índice cambia, este mapping se revisa.

### 11.2 PYMIA_ARCHITECTURE_ALIGNMENT.md

Este mapping respeta las 5 fronteras arquitectónicas:
- Hermes gobierna (no se mapea aquí)
- LLM Operator opera (no se mapea aquí)
- PymIA OS ejecuta (usa artefactos de dominio)
- SmartPyme analiza (usa artefactos de dominio)
- Canales transportan (no se mapea aquí)

### 11.3 PYMIA_ARCHITECTURAL_DNA.md

Este mapping materializa el ADN en artefactos:
- Knowledge Item → (no está en este mapping, es capa epistémica)
- Hallazgo Verificable → (no está, es capa de producto)
- Modelo Organizacional → OrganizationProfile
- Estado Epistémico → (no está, es capa epistémica)

**Este mapping es específico del núcleo organizacional, no de todo PymIA.**

### 11.4 PYMIA_EPISTEMIC_CORE.md (futuro)

Cuando exista, contendrá los artefactos epistémicos:
- KnowledgeItem
- Evidence
- Hypothesis
- EpistemicAction
- EpistemicState

Esos NO están en este mapping porque son capa epistémica, no organizacional.

---

## 12. Criterio de éxito

Este documento habrá cumplido su función cuando:

### 12.1 Trazabilidad completa
- Todo artefacto Python del núcleo organizacional tiene entrada en §3
- Todo concepto doctrinal operativo tiene artefacto asignado o está en §8

### 12.2 Frontera respetada
- Cero artefactos de dominio con imports técnicos
- Cero artefactos de infraestructura mezclados con dominio
- Cero violaciones de las reglas de §6

### 12.3 Composición jerárquica respetada
- Cero artefactos de nivel N componiendo nivel > N
- Cero fusiones indebidas (§10.1)
- Cero duplicaciones indebidas (§10.2)

### 12.4 Deriva controlada
- §7 actualizado con cualquier artefacto huérfano
- §8 actualizado cuando un concepto futuro se materialice
- §10 consultado antes de cada PR

### 12.5 Contratos Python coherentes
- Los contratos Python siguen §9 sin excepciones
- Los tests validan reglas de §6 y §9
- El código es revisable contra este mapping

---

## 13. Regla final

```
Este mapping es contrato.

Si el código lo viola,
el código está mal.

Si la doctrina lo contradice,
la doctrina se actualiza primero.

Nunca al revés.

Porque la doctrina es la fuente.
El artefacto es la materialización.
El código es la implementación.

Y el orden de autoridad es:

  Doctrina → Mapping → Contratos → Código → Tests

Cualquier violación de este orden
debe ser rechazada.
```

---

**Documento cerrado como CANDIDATE_V1.**

Listo para auditoría cruzada y promoción a V1 tras primera implementación.
