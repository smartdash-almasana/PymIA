# PYMIA_ARTIFACT_TO_CONTRACT_MAPPING

## Estado del documento

**Estado:** CANDIDATE_V1

**Nivel:** Puente artefactos conceptuales → contratos Python

**Propósito:**

Traducir los 28 artefactos conceptuales definidos en `PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING.md` en contratos Python concretos: módulo, clase, campos mínimos y dependencias.

Este documento **no es código**. Es especificación contractual. El código debe materializarlo sin desviarse.

---

## 1. Propósito

La doctrina organizacional cerrada (10 documentos) define **qué** es PymIA.

El mapping doctrina → artefactos define **qué entidades conceptuales** existen.

Este documento define **cómo se materializan** esas entidades en contratos Python: estructura de datos pura de dominio, sin infraestructura, sin persistencia, sin red, sin LLM.

**Este documento sirve para:**

1. Servir de especificación única para la implementación Python.
2. Verificar trazabilidad doctrina → contrato → código.
3. Evitar deriva conceptual durante la implementación.
4. Facilitar auditoría de consistencia dominio/código.

**Este documento NO sirve para:**

- Definir infraestructura (DB, red, LLM, Telegram).
- Definir lógica de aplicación (orquestación, servicios).
- Reemplazar la doctrina.
- Ser ejecutable por sí mismo.

---

## 2. Principios de contrato

### 2.1 Un artefacto conceptual → un contrato Python

Cada fila de la tabla de 28 artefactos se materializa en **exactamente una** clase Python (dataclass o protocol). No hay fusión ni división sin justificación doctrinal explícita.

### 2.2 Dominio puro

Los contratos residen en `pymia/domain/`. No pueden importar de:
- `pymia/infrastructure/`
- `pymia/application/`
- `pymia/adapters/`
- librerías externas salvo stdlib + `uuid`, `datetime`, `typing`

### 2.3 Inmutabilidad preferida en value objects

Los value objects (Capa 1) se implementan como `@dataclass(frozen=True)`. No tienen ID propio. Se comparan por valor.

### 2.4 Zero-dependency en Capa 0

Los enums y tipos escalares (Capa 0) no importan nada del dominio. Solo `enum.Enum` y `typing`.

### 2.5 DAG estricto

El grafo de dependencias entre contratos es acíclico. Si aparece un ciclo durante implementación, es un error de diseño que debe resolverse en este documento antes de tocar código.

### 2.6 Identidad explícita en entidades

Solo las entidades (Capas 2, 3, 5) tienen `id: UUID`. Los value objects no. Los snapshots tienen `id` propio porque representan evaluaciones concretas con ciclo de vida.

### 2.7 Timestamps solo en entidades y snapshots

Los value objects no tienen `created_at` ni `updated_at`. Los timestamps pertenecen a la capa de persistencia o a entidades con ciclo de vida.

---

## 3. Capas de implementación

### 3.1 Capa 0 — Primitivos (enums, tipos escalares)

**Naturaleza:** Tipos base sin lógica.

**Materialización:** `Enum` y `NewType` de `typing`.

**Ubicación:** `pymia/domain/types/`

**Contenido:**
- `EpistemicStatus` (declarado, observado, inferido, validado, refutado, archivado)
- `ConstraintKind` (caja, tiempo, capacidad, atención, información, regulatoria, mercado, crédito)
- `TensionKind` (10 tipos doctrinales)
- `CapabilityLevel` (declarada, observada, latente, límite)
- `RelationshipWeight` (bajo, medio, alto, crítico)
- `IdentityLayerKind` (núcleo, adaptable, periférica)
- `IdentityCrisisKind` (negación, frustración, reputación, propósito)
- `FunctionalOrganKind` (circulatorio, respiratorio, digestivo, nervioso, sensorial, inmunológico, reproductivo)
- `OrganState` (sano, estresado, enfermo, fallando, recuperándose)
- `PathologyKind` (8 tipos catalogados)
- `PathologyChronicity` (aguda, crónica, silenciosa)
- `InterventionType` (sintomática, curativa, paliativa)
- `TrajectoryKind` (estable, progresiva, acelerada, recurrente, crítica, recuperación, errática)
- `PointOfNoReturnCategory` (financiero, comercial, humano, operativo, regulatorio)
- `MaturityLevel` (reactivo, intuitivo, sistemático, adaptativo, estratégico)

### 3.2 Capa 1 — Value Objects (inmutables)

**Naturaleza:** Definidos por sus atributos, sin identidad propia.

**Materialización:** `@dataclass(frozen=True)`.

**Ubicación:** `pymia/domain/primitives/`

**Contenido:**
- `ExchangeCommitment` (partes, tipo, condiciones)
- `OrganizationalConstraint` (tipo, magnitud, horizonte)
- `StructuralTension` (polo_a, polo_b, estado_actual)
- `StructuralRelationship` (nodo_a, nodo_b, peso, tipo)
- `OrganizationalDependency` (nodo, criticidad, reemplazabilidad)
- `IdentityLayer` (tipo, contenido)
- `IdentityCrisis` (tipo, divergencia_medida)
- `FunctionalOrgan` (tipo, estado)
- `FragilityIndicator` (dimensión, severidad)
- `OrganizationalSymptom` (manifestación, intensidad, primer_avistamiento)
- `InterventionAction` (tipo, dosis, horizonte)
- `IatrogenicRisk` (tipo, probabilidad, impacto)
- `OrganizationalTrajectory` (tipo, velocidad, dirección)
- `PointOfNoReturn` (categoría, umbral, proximidad)
- `InterventionWindow` (inicio, fin, condiciones_cierre)
- `AuthorityStructure` (matriz_decisiones)

### 3.3 Capa 2 — Entidades núcleo (con identidad)

**Naturaleza:** Tienen ID, mutan controladamente, representan sustrato.

**Materialización:** `@dataclass` con `id: UUID`.

**Ubicación:** `pymia/domain/entities/`

**Contenido:**
- `OrganizationProfile` — composición de las 5 dimensiones
- `OrganizationalIdentity` — 4 identidades + 3 capas
- `OrganizationalCapability` — capacidad evaluada con nivel

### 3.4 Capa 3 — Entidades con ciclo de vida

**Naturaleza:** Nacen, evolucionan, se cierran.

**Materialización:** `@dataclass` con `id: UUID`, `created_at`, `closed_at: Optional`.

**Ubicación:** `pymia/domain/entities/`

**Contenido:**
- `KnowledgeItem` (preexistente doctrinalmente)
- `EpistemicAction` (preexistente doctrinalmente)
- `DecisionRecord` (instancia de decisión con 8 componentes)
- `LearningCycle` (cierre de ciclo de aprendizaje)

### 3.5 Capa 4 — Snapshots (evaluaciones compuestas)

**Naturaleza:** Fotografías de estado en un momento. Reemplazan al snapshot anterior.

**Materialización:** `@dataclass` con `id: UUID`, `generated_at: datetime`.

**Ubicación:** `pymia/domain/snapshots/`

**Contenido:**
- `HealthAssessment` (7 dimensiones + 7 órganos)
- `DiagnosticReport` (cadena clínica completa)
- `PrognosisAssessment` (trayectorias + puntos de no retorno)
- `DecisionCapabilityAssessment` (nivel de madurez + componentes)

### 3.6 Capa 5 — Entidades terapéuticas y de coherencia

**Naturaleza:** Entidades con ciclo de vida especializado.

**Materialización:** `@dataclass` con `id: UUID`, `created_at`, `status`.

**Ubicación:** `pymia/domain/entities/`

**Contenido:**
- `OrganizationalPathology` (instancia concreta de enfermedad)
- `InterventionPlan` (plan terapéutico)
- `GovernanceProfile` (infraestructura de coherencia)

---

## 4. Tabla de contratos completa

| # | Artefacto | Módulo | Clase | Campos mínimos | Depende de | Milestone |
|---|-----------|--------|-------|----------------|------------|-----------|
| 1 | ExchangeCommitment | primitives | ExchangeCommitment | partes, tipo, condiciones | — | M1 |
| 2 | OrganizationalConstraint | primitives | OrganizationalConstraint | kind, magnitud, horizonte | ConstraintKind | M1 |
| 3 | StructuralTension | primitives | StructuralTension | polo_a, polo_b, estado_actual | TensionKind | M1 |
| 4 | StructuralRelationship | primitives | StructuralRelationship | nodo_a, nodo_b, peso, tipo | RelationshipWeight | M1 |
| 5 | OrganizationalDependency | primitives | OrganizationalDependency | nodo, criticidad, reemplazabilidad | RelationshipWeight | M1 |
| 6 | IdentityLayer | primitives | IdentityLayer | tipo, contenido | IdentityLayerKind | M2 |
| 7 | IdentityCrisis | primitives | IdentityCrisis | tipo, divergencia_medida | IdentityCrisisKind | M2 |
| 8 | FunctionalOrgan | primitives | FunctionalOrgan | tipo, estado | FunctionalOrganKind, OrganState | M2 |
| 9 | FragilityIndicator | primitives | FragilityIndicator | dimensión, severidad | — | M2 |
| 10 | OrganizationalSymptom | primitives | OrganizationalSymptom | manifestación, intensidad, primer_avistamiento | — | M4 |
| 11 | InterventionAction | primitives | InterventionAction | tipo, dosis, horizonte | InterventionType | M4 |
| 12 | IatrogenicRisk | primitives | IatrogenicRisk | tipo, probabilidad, impacto | — | M4 |
| 13 | OrganizationalTrajectory | primitives | OrganizationalTrajectory | tipo, velocidad, dirección | TrajectoryKind | M4 |
| 14 | PointOfNoReturn | primitives | PointOfNoReturn | categoría, umbral, proximidad | PointOfNoReturnCategory | M4 |
| 15 | InterventionWindow | primitives | InterventionWindow | inicio, fin, condiciones_cierre | — | M4 |
| 16 | AuthorityStructure | primitives | AuthorityStructure | matriz_decisiones | — | M5 |
| 17 | OrganizationProfile | entities | OrganizationProfile | id, compromisos, restricciones, tensiones, relaciones, dependencias | ExchangeCommitment, OrganizationalConstraint, StructuralTension, StructuralRelationship, OrganizationalDependency | M2 |
| 18 | OrganizationalIdentity | entities | OrganizationalIdentity | id, declarada, observada, deseada, percibida, capas, crisis_activa | IdentityLayer, IdentityCrisis | M2 |
| 19 | OrganizationalCapability | entities | OrganizationalCapability | id, tipo, nivel, evidencia | CapabilityLevel | M2 |
| 20 | KnowledgeItem | entities | KnowledgeItem | id, contenido, fuente, estado_epistémico, confianza, creado_en | EpistemicStatus | M3 |
| 21 | EpistemicAction | entities | EpistemicAction | id, tipo, objetivo, input, output, verificabilidad | — | M3 |
| 22 | DecisionRecord | entities | DecisionRecord | id, contexto, alternativas, riesgos, decisión, resultado_esperado, resultado_observado, aprendizaje | KnowledgeItem | M3 |
| 23 | LearningCycle | entities | LearningCycle | id, decisión_origen, resultado, atribución, aprendizaje_extraído, ajuste_propuesto, cerrado_en | DecisionRecord | M3 |
| 24 | HealthAssessment | snapshots | HealthAssessment | id, dimensiones, órganos, fragilidades, generado_en | FunctionalOrgan, FragilityIndicator | M4 |
| 25 | DiagnosticReport | snapshots | DiagnosticReport | id, síntomas, causa_identificada, patología, evidencia, generado_en | OrganizationalSymptom, KnowledgeItem | M4 |
| 26 | PrognosisAssessment | snapshots | PrognosisAssessment | id, trayectoria, punto_no_retorno, ventana_intervención, escenarios, generado_en | OrganizationalTrajectory, PointOfNoReturn, InterventionWindow | M4 |
| 27 | DecisionCapabilityAssessment | snapshots | DecisionCapabilityAssessment | id, nivel_madurez, componentes, indicadores, generado_en | MaturityLevel, DecisionRecord | M5 |
| 28 | OrganizationalPathology | entities | OrganizationalPathology | id, tipo, cronicidad, gravedad, diagnosticada_en, tratamiento_asociado | PathologyKind, PathologyChronicity | M4 |
| 29 | InterventionPlan | entities | InterventionPlan | id, patología_tratada, tipo, acciones, iatrogenia_potencial, creado_en, estado | InterventionType, InterventionAction, IatrogenicRisk | M4 |
| 30 | GovernanceProfile | entities | GovernanceProfile | id, estructura_autoridad, mecanismos_coherencia, nivel_adaptativo, creado_en | AuthorityStructure | M5 |

**Nota:** La tabla enumera 30 filas porque algunos artefactos se despliegan en varias clases (enums adicionales ya contabilizados en Capa 0).

---

## 5. Núcleo mínimo ejecutable (M1-M3)

Los siguientes 8 contratos forman el núcleo mínimo para instanciar un tenant y ejecutar el ciclo cognitivo básico:

| # | Contrato | Capa | Milestone |
|---|----------|------|-----------|
| 1 | Enums canónicos (todos los de Capa 0) | 0 | M1 |
| 2 | ExchangeCommitment | 1 | M1 |
| 3 | OrganizationProfile | 2 | M2 |
| 4 | OrganizationalIdentity | 2 | M2 |
| 5 | KnowledgeItem | 3 | M3 |
| 6 | EpistemicAction | 3 | M3 |
| 7 | DecisionRecord | 3 | M3 |
| 8 | LearningCycle | 3 | M3 |

### Qué permite hacer este núcleo

- Representar un tenant (OrganizationProfile + OrganizationalIdentity)
- Registrar compromisos de intercambio (átomo doctrinal)
- Construir conocimiento (KnowledgeItem + EpistemicAction)
- Tomar decisiones (DecisionRecord)
- Cerrar ciclos de aprendizaje (LearningCycle)

### Qué NO permite hacer todavía

- Diagnosticar patologías
- Intervenir terapéuticamente
- Proyectar trayectorias
- Evaluar salud integral
- Gobernar coherencia

Para habilitar esas capacidades se requiere completar M4 (cadena clínica) y M5 (coherencia).

---

## 6. Contratos abstractos (no dataclasses)

Los siguientes conceptos doctrinales **NO se materializan como dataclasses**. Se implementan como protocols, orquestadores o funciones puras:

### 6.1 Cadenas procesales (orquestadores)

- **Cadena clínica completa** (Symptom → Pathology → Intervention → Prognosis) → `ClinicalChainOrchestrator` (clase de aplicación, no dominio)
- **Cadena decisional** (Evidence → Alternatives → Risk → Decision → Action → Result) → `DecisionChainOrchestrator`
- **Ciclo de aprendizaje** (proceso, no entidad) → `LearningCycleOrchestrator`

### 6.2 Reglas de evaluación (funciones puras)

- `compute_health_assessment(profile, evidence) -> HealthAssessment`
- `compute_prognosis(pathology, trajectory, interventions) -> PrognosisAssessment`
- `compute_decision_capability(decisions) -> DecisionCapabilityAssessment`
- `detect_pathology(symptoms, profile) -> Optional[DiagnosticReport]`

### 6.3 Políticas de gobernanza (evaluadores)

- `GovernanceEvaluator` — verifica coherencia de decisiones con governance profile
- `AuthorityChecker` — valida si un actor puede tomar una decisión
- `CoherenceGuard` — detecta decisiones contradictorias con identidad

### 6.4 Repositorios (infraestructura)

- `KnowledgeItemRepository` (protocol)
- `DecisionRecordRepository` (protocol)
- `OrganizationProfileRepository` (protocol)

**Regla:** Los repositorios viven en `pymia/infrastructure/persistence/`, nunca en `pymia/domain/`.

### 6.5 Proyectores (funciones puras)

- `project_trajectory(historical_assessments) -> OrganizationalTrajectory`
- `estimate_point_of_no_return(trajectory, constraints) -> Optional[PointOfNoReturn]`

---

## 7. Milestones de implementación

### 7.1 M1 — Primitivos y átomos (1-2 días)

**Entregables:**
- Módulo `pymia/domain/types/` con todos los enums
- Módulo `pymia/domain/primitives/` con 5 value objects atómicos
- Tests unitarios de inmutabilidad

**Dependencias externas:** ninguna

**Criterio de éxito:** `pytest pymia/domain/types pymia/domain/primitives` pasa sin errores

### 7.2 M2 — Núcleo tenant (1 día)

**Entregables:**
- `OrganizationProfile`
- `OrganizationalIdentity`
- `OrganizationalCapability`
- Value objects de identidad (IdentityLayer, IdentityCrisis, FunctionalOrgan, FragilityIndicator)

**Dependencias:** M1

**Criterio de éxito:** Se puede instanciar un tenant con identidad y restricciones

### 7.3 M3 — Cadena epistémica (2 días)

**Entregables:**
- `KnowledgeItem`
- `EpistemicAction`
- `DecisionRecord`
- `LearningCycle`

**Dependencias:** M2

**Criterio de éxito:** Se puede construir un KnowledgeItem desde evidencia, ejecutar una EpistemicAction, registrar una decisión y cerrar un ciclo de aprendizaje

### 7.4 M4 — Cadena clínica (2-3 días)

**Entregables:**
- Todos los value objects clínicos (Symptom, Trajectory, PointOfNoReturn, InterventionWindow, InterventionAction, IatrogenicRisk)
- `OrganizationalPathology`
- `InterventionPlan`
- `HealthAssessment` (snapshot)
- `DiagnosticReport` (snapshot)
- `PrognosisAssessment` (snapshot)

**Dependencias:** M3

**Criterio de éxito:** Se puede ejecutar la cadena clínica completa sobre un tenant

### 7.5 M5 — Coherencia y maduración (1-2 días)

**Entregables:**
- `GovernanceProfile`
- `AuthorityStructure`
- `DecisionCapabilityAssessment` (snapshot)

**Dependencias:** M4

**Criterio de éxito:** Se puede evaluar la madurez decisional y validar coherencia con gobernanza

**Total estimado:** 7-10 días de implementación pura + testing

---

## 8. Grafo de dependencias

```
Capa 0 — Enums y tipos
         │
         ▼
Capa 1 — Value Objects (16 clases)
         │
         ├── ExchangeCommitment ──┐
         ├── OrganizationalConstraint ──┤
         ├── StructuralTension ──┤
         ├── StructuralRelationship ──┼──► OrganizationProfile
         └── OrganizationalDependency ┘
         
         ├── IdentityLayer ──┐
         └── IdentityCrisis ─┴──► OrganizationalIdentity
         
         └── FunctionalOrgan, FragilityIndicator ──► HealthAssessment
         
         ▼
Capa 2 — Entidades núcleo
         │
         └── OrganizationProfile, Identity ──► contexto para Capa 3
         
         ▼
Capa 3 — Entidades con ciclo de vida
         │
         ├── KnowledgeItem ──► DecisionRecord ──► LearningCycle
         │
         └── DecisionRecord (múltiples) ──► DecisionCapabilityAssessment
         
         ▼
Capa 4 — Snapshots
         │
         ├── OrganizationalSymptom ──► DiagnosticReport
         ├── DiagnosticReport ──► OrganizationalPathology ──► InterventionPlan
         └── Pathology + Trajectory ──► PrognosisAssessment
         
         ▼
Capa 5 — Entidades terapéuticas
         │
         └── OrganizationProfile + AuthorityStructure ──► GovernanceProfile
```

**Verificación:**
- Sin ciclos.
- Cada capa solo importa de capas inferiores.
- Los snapshots (Capa 4) componen entidades de Capa 1-3 pero no son importados por ellas.
- La Capa 5 usa Capa 2 + value objects de Capa 1.

---

## 9. Reglas de implementación

### 9.1 Ubicación de enums
Todos los enums residen en `pymia/domain/types/`. Un archivo por familia conceptual (no un archivo por enum).

### 9.2 Value objects como frozen dataclass
```python
@dataclass(frozen=True)
class ExchangeCommitment:
    partes: tuple[str, ...]
    tipo: ExchangeCommitmentKind
    condiciones: str
```

### 9.3 Entidades con ID generado por factory
```python
@dataclass
class OrganizationProfile:
    id: UUID
    compromisos: tuple[ExchangeCommitment, ...]
    ...
    
    @classmethod
    def create(cls, ...) -> "OrganizationProfile":
        return cls(id=uuid4(), ...)
```

### 9.4 Timestamps en UTC con timezone aware
```python
from datetime import datetime, timezone
creado_en: datetime  # siempre datetime.now(timezone.utc)
```

### 9.5 Cero imports de infraestructura
Prohibido en `pymia/domain/`:
- `sqlalchemy`, `pydantic` (salvo para validación pura si se adopta)
- `httpx`, `requests`, `fastapi`
- `openai`, `anthropic`
- cualquier librería de red o DB

### 9.6 Cero lógica de red/DB en contratos
Los contratos son estructuras de datos + métodos de dominio puros (validaciones, invariantes). Nunca queries, nunca HTTP calls.

### 9.7 Invariantes como métodos de dominio
```python
class OrganizationProfile:
    def has_critical_dependency(self) -> bool:
        return any(d.criticidad == RelationshipWeight.CRÍTICO 
                   for d in self.dependencias)
```

### 9.8 Tests obligatorios por contrato
Cada contrato requiere:
- Test de instanciación válida
- Test de invariante violada
- Test de inmutabilidad (si aplica)
- Test de comparación por valor (si es value object) o por ID (si es entidad)

---

## 10. Estructura de módulos propuesta

```
pymia/
└── domain/
    ├── __init__.py
    ├── types/
    │   ├── __init__.py
    │   ├── epistemic.py          # EpistemicStatus
    │   ├── constraint.py         # ConstraintKind
    │   ├── tension.py            # TensionKind
    │   ├── capability.py         # CapabilityLevel
    │   ├── relationship.py       # RelationshipWeight
    │   ├── identity.py           # IdentityLayerKind, IdentityCrisisKind
    │   ├── organ.py              # FunctionalOrganKind, OrganState
    │   ├── pathology.py          # PathologyKind, PathologyChronicity
    │   ├── intervention.py       # InterventionType
    │   ├── trajectory.py         # TrajectoryKind
    │   ├── threshold.py          # PointOfNoReturnCategory
    │   └── maturity.py           # MaturityLevel
    │
    ├── primitives/
    │   ├── __init__.py
    │   ├── exchange.py           # ExchangeCommitment
    │   ├── constraint.py         # OrganizationalConstraint
    │   ├── tension.py            # StructuralTension
    │   ├── relationship.py       # StructuralRelationship
    │   ├── dependency.py         # OrganizationalDependency
    │   ├── identity.py           # IdentityLayer, IdentityCrisis
    │   ├── organ.py              # FunctionalOrgan
    │   ├── fragility.py          # FragilityIndicator
    │   ├── symptom.py            # OrganizationalSymptom
    │   ├── intervention.py       # InterventionAction, IatrogenicRisk
    │   ├── trajectory.py         # OrganizationalTrajectory, PointOfNoReturn, InterventionWindow
    │   └── authority.py          # AuthorityStructure
    │
    ├── entities/
    │   ├── __init__.py
    │   ├── profile.py            # OrganizationProfile
    │   ├── identity.py           # OrganizationalIdentity
    │   ├── capability.py         # OrganizationalCapability
    │   ├── knowledge.py          # KnowledgeItem
    │   ├── epistemic_action.py   # EpistemicAction
    │   ├── decision.py           # DecisionRecord
    │   ├── learning.py           # LearningCycle
    │   ├── pathology.py          # OrganizationalPathology
    │   ├── intervention.py       # InterventionPlan
    │   └── governance.py         # GovernanceProfile
    │
    ├── snapshots/
    │   ├── __init__.py
    │   ├── health.py             # HealthAssessment
    │   ├── diagnostic.py         # DiagnosticReport
    │   ├── prognosis.py          # PrognosisAssessment
    │   └── capability.py         # DecisionCapabilityAssessment
    │
    └── rules/                    # funciones puras, no dataclasses
        ├── __init__.py
        ├── health_rules.py
        ├── prognosis_rules.py
        ├── pathology_rules.py
        └── governance_rules.py
```

---

## 11. Riesgos de implementación

### 11.1 Sobrediseño inicial

**Riesgo:** Intentar implementar los 30 contratos de entrada antes de validar el núcleo.

**Mitigación:** Milestones M1-M3 forman el núcleo mínimo ejecutable. M4-M5 pueden postergarse hasta que M1-M3 esté validado en producción con al menos un tenant.

### 11.2 Confusión value object vs entidad

**Riesgo:** Implementar `ExchangeCommitment` con ID propio, violando su naturaleza de value object.

**Mitigación:** La columna "Clase" de la tabla §4 indica `frozen dataclass` para value objects. Revisión por pares obligatoria en PRs que toquen `pymia/domain/primitives/`.

### 11.3 Infraestructura metida en dominio

**Riesgo:** Agregar `sqlalchemy.Column` o `pydantic.BaseModel` a entidades de dominio.

**Mitigación:** Regla §9.5 prohibe imports de infraestructura. Linter configurado para detectar violaciones en CI.

### 11.4 Ciclos de importación

**Riesgo:** `OrganizationalPathology` importa `InterventionPlan` y viceversa.

**Mitigación:** El DAG de §8 está verificado. La relación es `InterventionPlan → OrganizationalPathology` (una dirección). Si surge un ciclo, se resuelve en este documento antes de tocar código.

### 11.5 Doctrina drift durante implementación

**Riesgo:** Un ingeniero "optimiza" un contrato fusionando dos artefactos o eliminando un campo "innecesario".

**Mitigación:** Regla final §14 establece orden de autoridad: Doctrina → Artefacto → Contrato → Código. Cualquier cambio en contrato requiere actualización previa de este documento y, si aplica, del mapping doctrinal.

### 11.6 Snapshot vs entidad

**Riesgo:** Implementar `HealthAssessment` como entidad mutable en lugar de snapshot inmutable.

**Mitigación:** §3.5 define snapshots como inmutables con `generated_at`. Un nuevo assessment no modifica el anterior, lo reemplaza por referencia.

---

## 12. Relación con documentos previos

### 12.1 Upstream: PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING.md

Este documento es downstream del mapping doctrina → artefactos. Si un artefacto conceptual cambia allí, el contrato correspondiente debe revisarse aquí.

### 12.2 Navegación: PYMIA_DOCTRINAL_INDEX.md

El índice doctrinal permite navegar los 10 documentos fuente que justifican cada contrato.

### 12.3 Frontera técnica: PYMIA_ARCHITECTURE_ALIGNMENT.md

Las 5 fronteras prohibidas del ADN arquitectónico aplican también aquí:
- `pymia/domain/` no puede depender de `pymia/infrastructure/`
- `pymia/domain/` no puede depender de adaptadores (Telegram, OpenRouter)
- `pymia/domain/` no puede importar LLM providers

### 12.4 ADN irreductible: PYMIA_ARCHITECTURAL_DNA.md

Los contratos de dominio materializan el ADN. Si un contrato contradice el ADN (ej: un contrato que asume respuestas LLM como fuente primaria), el contrato está mal.

---

## 13. Criterio de éxito

Este documento se considera exitoso cuando:

1. **Trazabilidad completa:** Todo contrato Python en `pymia/domain/` tiene una fila correspondiente en la tabla §4.
2. **DAG verificable:** Un tool automático puede verificar que no hay ciclos de importación entre módulos de `pymia/domain/`.
3. **Cero violaciones de frontera:** El linter de CI no reporta imports prohibidos desde `pymia/domain/`.
4. **Núcleo mínimo ejecutable:** Los contratos de M1-M3 pasan smoke test con un tenant de prueba.
5. **Doctrina preservada:** Tras 6 meses de implementación, revisar este documento contra el código no revela desviaciones conceptuales.

---

## 14. Regla final

```
El contrato Python es la materialización del artefacto conceptual.

Si el artefacto cambia, el contrato cambia.
Si la doctrina cambia, el artefacto cambia primero.

Orden de autoridad:

  Doctrina (10 documentos)
      ↓
  Artefacto (PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING)
      ↓
  Contrato (este documento)
      ↓
  Código (pymia/domain/)

Si el código viola el contrato, el código está mal.
Si el contrato viola el artefacto, el contrato está mal.
Si el artefacto viola la doctrina, el artefacto está mal.

Nunca se arregla "hacia abajo".
Siempre se arregla "hacia arriba".
```

---

**Documento cerrado como CANDIDATE_V1.**

Listo para auditoría y decisión de implementación.
