# PYMIA_CONTRACT_TO_SOFTWARE_MAPPING

## Estado

Documento puente: contratos conceptuales → implementación Python.

Estado: **CANDIDATE_V1**

Depende de:
- `PYMIA_ARTIFACT_TO_CONTRACT_MAPPING.md` (upstream)
- `PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING.md` (fuente doctrinal)
- `PYMIA_ARCHITECTURE_ALIGNMENT.md` (frontera técnica)

---

## 1. Propósito

Este documento es el **blueprint de implementación** del dominio PymIA.

Su función no es escribir código, sino especificar:

- cómo se traducen los 28 contratos conceptuales en módulos Python,
- qué estructura de paquetes debe construirse,
- qué dependencias están permitidas y cuáles prohibidas,
- en qué orden deben implementarse los módulos,
- qué reglas técnicas deben respetarse.

Sirve como contrato técnico entre la doctrina cerrada y el equipo de implementación.

**Este documento no es código. Es especificación.**

---

## 2. Principios de implementación

### 2.1 Dominio puro

El paquete `pymia.domain` no sabe que existe el mundo exterior.
Solo conoce sus propios tipos y estructuras.

### 2.2 DAG estricto

Las importaciones entre módulos forman un grafo acíclico dirigido.
Ningún módulo puede importar, directa o indirectamente, algo que lo importe a él.

### 2.3 Inmutabilidad preferida

Los value objects (Capa 1) son inmutables.
Se implementan como `@dataclass(frozen=True)`.

### 2.4 Un contrato → un archivo Python

Cada contrato conceptual del mapping anterior se materializa en un archivo Python propio.
No hay archivos "mega" que agrupen múltiples contratos.

### 2.5 Tests unitarios obligatorios

Cada contrato implementado debe tener al menos un test unitario.
Los tests viven en `tests/domain/` replicando la estructura de paquetes.

### 2.6 Validación en construcción

Los invariantes de dominio se validan en `__post_init__`.
Una instancia inválida nunca debe existir en memoria.

### 2.7 Cero side effects en dominio

Ningún método de dominio hace I/O, red, DB, logs ni llamadas a servicios externos.
Toda interacción con el mundo exterior pertenece a infraestructura.

---

## 3. Estructura de paquetes

### 3.1 Paquete raíz de dominio

```
pymia/domain/
├── __init__.py
├── types/              # Capa 0: enums y escalares tipados
├── primitives/         # Capa 1: value objects inmutables
├── entities/           # Capas 2, 3, 5: entidades con ID
├── snapshots/          # Capa 4: evaluaciones compuestas
└── processes/          # Orquestadores (no dataclasses)
```

### 3.2 Desglose por submódulo

**`types/` — Capa 0 (enums y escalares)**
```
pymia/domain/types/
├── __init__.py
├── epistemic_state.py
├── constraint_type.py
├── tension_type.py
├── relationship_weight.py
└── capability_level.py
```

**`primitives/` — Capa 1 (value objects)**
```
pymia/domain/primitives/
├── __init__.py
├── exchange_commitment.py
├── organizational_constraint.py
├── structural_tension.py
├── structural_relationship.py
├── organizational_dependency.py
├── identity_layer.py
└── identity_crisis.py
```

**`entities/` — Capas 2, 3, 5 (entidades con ID)**
```
pymia/domain/entities/
├── __init__.py
├── organization_profile.py
├── organizational_identity.py
├── functional_organ.py
├── knowledge_item.py
├── decision_record.py
├── learning_cycle.py
├── organizational_symptom.py
├── organizational_pathology.py
├── intervention_plan.py
├── intervention_action.py
├── iatrogenic_risk.py
└── governance_profile.py
```

**`snapshots/` — Capa 4 (evaluaciones compuestas)**
```
pymia/domain/snapshots/
├── __init__.py
├── health_assessment.py
├── diagnostic_report.py
├── prognosis_assessment.py
└── decision_capability_assessment.py
```

**`processes/` — Orquestadores (no dataclasses)**
```
pymia/domain/processes/
├── __init__.py
├── clinical_chain.py
├── decision_chain.py
└── learning_chain.py
```

### 3.3 Total de archivos de dominio

- `types/` — 6 archivos
- `primitives/` — 8 archivos
- `entities/` — 13 archivos
- `snapshots/` — 5 archivos
- `processes/` — 4 archivos
- `__init__.py` raíz — 1 archivo

**Total: 37 archivos Python**

### 3.4 Paquetes futuros (no implementar todavía)

```
pymia/infrastructure/    # Repositorios, adapters, config
pymia/application/       # Use cases, commands, queries
pymia/adapters/          # Integraciones externas
```

Estos paquetes podrán importar de `pymia.domain`.
`pymia.domain` no podrá importar de ellos nunca.

---

## 4. Tabla de módulos completa

| # | Contrato | Submódulo | Archivo | Depende de | Milestone |
|---|----------|-----------|---------|------------|-----------|
| 1 | EpistemicState | types | `epistemic_state.py` | (ninguna) | M1 |
| 2 | ConstraintType | types | `constraint_type.py` | (ninguna) | M1 |
| 3 | TensionType | types | `tension_type.py` | (ninguna) | M1 |
| 4 | RelationshipWeight | types | `relationship_weight.py` | (ninguna) | M1 |
| 5 | CapabilityLevel | types | `capability_level.py` | (ninguna) | M1 |
| 6 | ExchangeCommitment | primitives | `exchange_commitment.py` | types | M1 |
| 7 | OrganizationalConstraint | primitives | `organizational_constraint.py` | ConstraintType | M1 |
| 8 | StructuralTension | primitives | `structural_tension.py` | TensionType | M1 |
| 9 | StructuralRelationship | primitives | `structural_relationship.py` | RelationshipWeight | M1 |
| 10 | OrganizationalDependency | primitives | `organizational_dependency.py` | RelationshipWeight | M1 |
| 11 | IdentityLayer | primitives | `identity_layer.py` | (ninguna) | M1 |
| 12 | IdentityCrisis | primitives | `identity_crisis.py` | (ninguna) | M1 |
| 13 | OrganizationProfile | entities | `organization_profile.py` | todos los primitives | M2 |
| 14 | OrganizationalIdentity | entities | `organizational_identity.py` | IdentityLayer, IdentityCrisis | M2 |
| 15 | FunctionalOrgan | entities | `functional_organ.py` | (ninguna) | M2 |
| 16 | KnowledgeItem | entities | `knowledge_item.py` | EpistemicState | M3 |
| 17 | DecisionRecord | entities | `decision_record.py` | KnowledgeItem | M3 |
| 18 | LearningCycle | entities | `learning_cycle.py` | DecisionRecord | M3 |
| 19 | OrganizationalSymptom | entities | `organizational_symptom.py` | (ninguna) | M4 |
| 20 | OrganizationalPathology | entities | `organizational_pathology.py` | OrganizationalSymptom | M4 |
| 21 | InterventionPlan | entities | `intervention_plan.py` | OrganizationalPathology | M4 |
| 22 | InterventionAction | entities | `intervention_action.py` | InterventionPlan | M4 |
| 23 | IatrogenicRisk | entities | `iatrogenic_risk.py` | InterventionPlan | M4 |
| 24 | GovernanceProfile | entities | `governance_profile.py` | OrganizationProfile | M5 |
| 25 | HealthAssessment | snapshots | `health_assessment.py` | FunctionalOrgan, OrganizationalConstraint | M4 |
| 26 | DiagnosticReport | snapshots | `diagnostic_report.py` | OrganizationalSymptom, OrganizationalPathology | M4 |
| 27 | PrognosisAssessment | snapshots | `prognosis_assessment.py` | OrganizationalPathology, InterventionPlan | M4 |
| 28 | DecisionCapabilityAssessment | snapshots | `decision_capability_assessment.py` | DecisionRecord, LearningCycle, GovernanceProfile | M5 |

---

## 5. Núcleo mínimo ejecutable (M1-M3)

### 5.1 Los 8 contratos imprescindibles

| # | Contrato | Archivo | Milestone |
|---|----------|---------|-----------|
| 1 | ExchangeCommitment | `primitives/exchange_commitment.py` | M1 |
| 2 | OrganizationProfile | `entities/organization_profile.py` | M2 |
| 3 | OrganizationalIdentity | `entities/organizational_identity.py` | M2 |
| 4 | KnowledgeItem | `entities/knowledge_item.py` | M3 |
| 5 | EpistemicAction | (definir en M3 como value object auxiliar) | M3 |
| 6 | DecisionRecord | `entities/decision_record.py` | M3 |
| 7 | LearningCycle | `entities/learning_cycle.py` | M3 |
| 8 | OrganizationalSymptom | `entities/organizational_symptom.py` | M4 |

Nota: `EpistemicAction` aparece mencionado en doctrina previa pero no figura explícitamente en el mapping de contratos. Debe agregarse como value object auxiliar en M3, o integrarse como método de `KnowledgeItem`.

### 5.2 Qué permite hacer el núcleo mínimo

- Representar un tenant con perfil e identidad
- Registrar evidencia y construir conocimiento (KnowledgeItem)
- Tomar decisiones y registrarlas (DecisionRecord)
- Detectar síntomas (OrganizationalSymptom)
- Cerrar ciclos de aprendizaje (LearningCycle)

### 5.3 Qué NO permite hacer el núcleo mínimo

- Diagnosticar patologías (falta `OrganizationalPathology`)
- Intervenir (falta `InterventionPlan`)
- Proyectar trayectorias (falta `PrognosisAssessment`)
- Evaluar salud (falta `HealthAssessment`)
- Evaluar capacidad decisional (falta `DecisionCapabilityAssessment`)

---

## 6. Dependencias prohibidas y permitidas

### 6.1 Imports prohibidos en `pymia.domain`

Ningún archivo dentro de `pymia/domain/` puede importar:

```python
# Paquetes internos prohibidos
from pymia.infrastructure import ...
from pymia.application import ...
from pymia.adapters import ...
from pymia.llm_operator import ...
from pymia.hermes import ...
from pymia.smartpyme import ...
from pymia.orchestration import ...
from pymia.narrative import ...
from pymia.document_intelligence import ...

# Librerías externas prohibidas
import sqlalchemy
from sqlalchemy import ...
import redis
import requests
import httpx
import telegram
import openai
import anthropic
from pydantic import ...     # salvo uso muy específico y justificado
import fastapi
import flask
```

### 6.2 Imports permitidos en `pymia.domain`

```python
# Standard library
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Tuple, Union
from datetime import datetime, date
from uuid import UUID, uuid4
from enum import Enum, auto
from decimal import Decimal

# Imports internos (sólo dentro de domain)
from pymia.domain.types import ...
from pymia.domain.primitives import ...
from pymia.domain.entities import ...
```

### 6.3 Regla de oro

> `pymia.domain` no sabe que existe el mundo exterior.
> Solo conoce sus propios tipos y estructuras.

Cualquier violación de esta regla es un defecto de implementación.

---

## 7. Separación dominio / infraestructura / aplicación

### 7.1 Dominio puro (`pymia/domain/`)

**Responsabilidad:**
- Modelar conceptos del dominio
- Validar invariantes de negocio
- Proveer tipos y estructuras

**Características:**
- Cero dependencias externas
- Solo stdlib + typing
- Inmutabilidad preferida
- Validación en `__post_init__`
- Cero side effects

**Tamaño objetivo:** 37 archivos

### 7.2 Infraestructura (`pymia/infrastructure/`) — futuro

**Responsabilidad:**
- Persistencia de entidades (repositorios)
- Integración con servicios externos (LLMs, Telegram, APIs)
- Configuración
- Logging y observabilidad

**Características:**
- Puede importar de `pymia.domain`
- No puede ser importado por `pymia.domain`
- Contiene side effects (DB, red, archivos)

**No implementar todavía.**

### 7.3 Aplicación (`pymia/application/`) — futuro

**Responsabilidad:**
- Casos de uso
- Comandos CQRS
- Consultas CQRS
- Orquestación de flujos

**Características:**
- Importa de `domain` y `infrastructure`
- No contiene lógica de negocio (eso va en domain)
- Es delgado: orquesta, no decide

**No implementar todavía.**

### 7.4 Reglas de frontera

1. `domain` → `domain` ✅ (respetando DAG)
2. `infrastructure` → `domain` ✅
3. `application` → `domain` ✅
4. `application` → `infrastructure` ✅
5. `domain` → `infrastructure` ❌ PROHIBIDO
6. `domain` → `application` ❌ PROHIBIDO
7. `infrastructure` → `application` ❌ PROHIBIDO

---

## 8. Milestones de implementación

### 8.1 M1 — Primitivos y átomos (1-2 días)

**Contratos (12):**
- 5 enums de `types/`
- 7 value objects de `primitives/`

**Archivos Python:** 13 (incluyendo `__init__.py`)

**Tests:** unitarios para cada enum y value object

**Smoke test:**
```python
from pymia.domain.primitives.exchange_commitment import ExchangeCommitment
# instanciar y validar invariante básico
```

### 8.2 M2 — Núcleo tenant (1 día)

**Contratos (3):**
- `OrganizationProfile`
- `OrganizationalIdentity`
- `FunctionalOrgan`

**Archivos Python:** 4

**Tests:** composición de value objects en entidades

**Smoke test:**
```python
from pymia.domain.entities.organization_profile import OrganizationProfile
# crear perfil de tenant completo con todas las dimensiones
```

### 8.3 M3 — Cadena epistémica (2 días)

**Contratos (3):**
- `KnowledgeItem`
- `DecisionRecord`
- `LearningCycle`

**Archivos Python:** 4

**Tests:** ciclo completo de aprendizaje

**Smoke test:**
```python
# registrar decisión → resultado → aprendizaje
# verificar transiciones de estado epistémico
```

### 8.4 M4 — Cadena clínica (2-3 días)

**Contratos (7):**
- `OrganizationalSymptom`
- `OrganizationalPathology`
- `DiagnosticReport`
- `InterventionPlan`
- `InterventionAction`
- `PrognosisAssessment`
- `HealthAssessment`

**Archivos Python:** 8

**Tests:** cadena clínica completa

**Smoke test:**
```python
# síntoma → patología → intervención → pronóstico
# verificar composición en snapshots
```

### 8.5 M5 — Coherencia y maduración (1-2 días)

**Contratos (3):**
- `GovernanceProfile`
- `IatrogenicRisk`
- `DecisionCapabilityAssessment`

**Archivos Python:** 4

**Tests:** evaluación de capacidad decisional

**Smoke test:**
```python
# assessment completo de tenant
# verificar coherencia entre gobernanza y decisiones
```

### 8.6 Totales

- **Tiempo total:** 7-10 días de implementación pura
- **Archivos Python totales:** 37 en `domain/`
- **Tests esperados:** al menos 37 archivos de test en `tests/domain/`

---

## 9. Reglas de implementación

### 9.1 Enums

```python
from enum import Enum

class EpistemicState(Enum):
    DECLARED = "declared"
    OBSERVED = "observed"
    INFERRED = "inferred"
    VALIDATED = "validated"
    REFUTED = "refuted"
    ARCHIVED = "archived"
```

- Usar `Enum` de stdlib.
- Valores en snake_case.
- No usar `auto()` salvo justificación explícita.

### 9.2 Value objects

```python
from dataclasses import dataclass
from pymia.domain.types.constraint_type import ConstraintType

@dataclass(frozen=True)
class OrganizationalConstraint:
    type: ConstraintType
    magnitude: float
    description: str

    def __post_init__(self):
        if self.magnitude < 0:
            raise ValueError("magnitude must be non-negative")
```

- Siempre `@dataclass(frozen=True)`.
- Validación en `__post_init__`.
- Sin `id`, sin timestamps.
- Comparables por valor.

### 9.3 Entidades

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from pymia.domain.types import EpistemicState

@dataclass
class KnowledgeItem:
    id: UUID
    state: EpistemicState
    content: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, content: str, state: EpistemicState = EpistemicState.DECLARED) -> "KnowledgeItem":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            state=state,
            content=content,
            created_at=now,
            updated_at=now,
        )
```

- `id: UUID` obligatorio.
- Timestamps `created_at`, `updated_at` opcionales según entidad.
- Factory method `create()` para construcción con defaults.
- No frozen (entidades pueden mutar estado epistémico).

### 9.4 Snapshots

```python
@dataclass(frozen=True)
class HealthAssessment:
    organization_id: UUID
    assessed_at: datetime
    organ_states: Dict[str, OrganState]
    overall_score: float
```

- Siempre `frozen=True` (un snapshot no muta).
- Contiene referencias por ID, no por objeto.
- Composición de múltiples entidades evaluadas.

### 9.5 Procesos (orquestadores)

```python
class ClinicalChain:
    def run(self, symptom: OrganizationalSymptom) -> DiagnosticReport:
        # lógica de orquestación
        ...
```

- NO son dataclasses.
- Son clases normales con métodos.
- Pueden recibir dependencias por constructor (infraestructura inyectada).
- Pertenecen a `pymia.domain.processes` solo si no hacen I/O.

### 9.6 Validación de invariantes

- Validar en `__post_init__` para value objects.
- Validar en factory method `create()` para entidades.
- Elevar `ValueError` con mensaje claro.
- No usar excepciones personalizadas en M1-M3 (añadir después si hace falta).

### 9.7 Métodos de dominio

- Puros (sin side effects).
- Retornan nuevos valores (no mutan en value objects).
- Pueden mutar estado en entidades con método explícito (`transition_to`).
- Cero imports de infraestructura.

### 9.8 Tests unitarios obligatorios

Por cada archivo de `pymia/domain/`:
- Al menos un test de construcción válida.
- Al menos un test de construcción inválida (debe elevar excepción).
- Tests de métodos de dominio si existen.

---

## 10. Estructura de tests

```
tests/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── types/
│   │   ├── test_epistemic_state.py
│   │   ├── test_constraint_type.py
│   │   ├── test_tension_type.py
│   │   ├── test_relationship_weight.py
│   │   └── test_capability_level.py
│   ├── primitives/
│   │   ├── test_exchange_commitment.py
│   │   ├── test_organizational_constraint.py
│   │   ├── test_structural_tension.py
│   │   ├── test_structural_relationship.py
│   │   ├── test_organizational_dependency.py
│   │   ├── test_identity_layer.py
│   │   └── test_identity_crisis.py
│   ├── entities/
│   │   ├── test_organization_profile.py
│   │   ├── test_organizational_identity.py
│   │   ├── test_functional_organ.py
│   │   ├── test_knowledge_item.py
│   │   ├── test_decision_record.py
│   │   ├── test_learning_cycle.py
│   │   ├── test_organizational_symptom.py
│   │   ├── test_organizational_pathology.py
│   │   ├── test_intervention_plan.py
│   │   ├── test_intervention_action.py
│   │   ├── test_iatrogenic_risk.py
│   │   └── test_governance_profile.py
│   ├── snapshots/
│   │   ├── test_health_assessment.py
│   │   ├── test_diagnostic_report.py
│   │   ├── test_prognosis_assessment.py
│   │   └── test_decision_capability_assessment.py
│   └── processes/
│       ├── test_clinical_chain.py
│       ├── test_decision_chain.py
│       └── test_learning_chain.py
├── integration/        # (futuro, con infraestructura)
└── smoke/              # tests de milestone
    ├── test_m1_primitives.py
    ├── test_m2_tenant.py
    ├── test_m3_epistemic.py
    ├── test_m4_clinical.py
    └── test_m5_governance.py
```

---

## 11. Grafo de dependencias de módulos

### 11.1 DAG por capas

```
Layer 0: types/
   ├── epistemic_state.py
   ├── constraint_type.py
   ├── tension_type.py
   ├── relationship_weight.py
   └── capability_level.py
            │
            ▼
Layer 1: primitives/
   ├── exchange_commitment.py
   ├── organizational_constraint.py ──► constraint_type.py
   ├── structural_tension.py ─────────► tension_type.py
   ├── structural_relationship.py ────► relationship_weight.py
   ├── organizational_dependency.py ──► relationship_weight.py
   ├── identity_layer.py
   └── identity_crisis.py
            │
            ▼
Layer 2: entities (core)
   ├── organization_profile.py ───────► todos los primitives
   ├── organizational_identity.py ────► identity_layer, identity_crisis
   └── functional_organ.py
            │
            ▼
Layer 3: entities (lifecycle)
   ├── knowledge_item.py ─────────────► epistemic_state
   ├── decision_record.py ────────────► knowledge_item
   └── learning_cycle.py ─────────────► decision_record
            │
            ▼
Layer 4: snapshots
   ├── health_assessment.py ──────────► functional_organ, constraint
   ├── diagnostic_report.py ──────────► symptom, pathology
   ├── prognosis_assessment.py ───────► pathology, intervention_plan
   └── decision_capability_assessment.py ──► decision_record, governance
            │
            ▼
Layer 5: entities (therapeutic)
   ├── organizational_symptom.py
   ├── organizational_pathology.py ───► symptom
   ├── intervention_plan.py ──────────► pathology
   ├── intervention_action.py ────────► intervention_plan
   ├── iatrogenic_risk.py ────────────► intervention_plan
   └── governance_profile.py ─────────► organization_profile
```

### 11.2 Verificación

- Cero dependencias cruzadas entre capas del mismo nivel.
- Cero dependencias hacia atrás (Layer N nunca importa de Layer N+1).
- Cero ciclos.
- Todo archivo puede importarse independientemente de los de su capa o superiores.

---

## 12. Riesgos de implementación

### 12.1 Sobrediseño inicial

**Descripción:** Querer implementar los 37 archivos en M1.

**Mitigación:** Respetar milestones secuenciales. M1-M3 son el mínimo ejecutable.

### 12.2 Infraestructura en dominio

**Descripción:** Poner lógica de DB, red o LLM en entidades.

**Mitigación:** Lista explícita de imports prohibidos (§6.1). Revisión por PR.

### 12.3 Ciclos de importación

**Descripción:** Agregar "sólo una" dependencia inversa que rompe el DAG.

**Mitigación:** Herramienta automática (pytest-import-linter o similar) que verifica DAG en CI.

### 12.4 Falta de tests

**Descripción:** Implementar contratos sin tests.

**Mitigación:** Regla §9.8 obliga a test por cada archivo. Cobertura mínima 90% en domain.

### 12.5 Doctrina drift

**Descripción:** El ingeniero "optimiza" un contrato violando doctrina.

**Mitigación:** Regla final §15 establece orden de autoridad. Toda modificación de contrato debe pasar por actualización de este documento primero.

### 12.6 Confusión value object / entidad

**Descripción:** Implementar `ExchangeCommitment` con `id` y timestamps.

**Mitigación:** Tabla §4 clasifica explícitamente. Los value objects van en `primitives/` y son frozen.

---

## 13. Relación con documentos previos

### 13.1 Upstream

- **`PYMIA_ARTIFACT_TO_CONTRACT_MAPPING.md`** — Fuente de los 28 contratos conceptuales que este documento materializa.
- **`PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING.md`** — Fuente doctrinal original de los 28 artefactos.
- **`PYMIA_DOCTRINAL_INDEX.md`** — Navegación del corpus doctrinal cerrado.
- **`PYMIA_ARCHITECTURE_ALIGNMENT.md`** — Frontera técnica (Hermes / Operator / OS / SmartPyme).
- **`PYMIA_ARCHITECTURAL_DNA.md`** — ADN irreductible de PymIA.

### 13.2 Downstream (futuro)

- Contratos Python en `pymia/domain/`
- Tests unitarios en `tests/domain/`
- Smoke tests por milestone en `tests/smoke/`
- Repositorios de infraestructura en `pymia/infrastructure/`

---

## 14. Criterio de éxito

Este documento se considera exitoso cuando:

1. **Trazabilidad completa:** todo archivo Python en `pymia/domain/` tiene entrada correspondiente en la tabla §4.
2. **DAG verificable:** una herramienta automática confirma cero ciclos de importación.
3. **Frontera respetada:** cero imports de infraestructura dentro de `pymia/domain/`.
4. **Milestones pasados:** cada milestone (M1-M5) tiene smoke test correspondiente pasando.
5. **Cobertura de tests:** > 90% de cobertura en `pymia/domain/`.
6. **Doctrina preservada:** ninguna modificación de contrato contradice los 10 documentos doctrinales cerrados.

---

## 15. Regla final

El archivo Python es la materialización del contrato conceptual.

```
Si el archivo cambia → el contrato conceptual debe actualizarse primero.
Si el contrato cambia → el artefacto conceptual debe actualizarse primero.
Si el artefacto cambia → la doctrina debe actualizarse primero.
```

**Orden de autoridad:**

```
Doctrina → Artefacto → Contrato → Archivo Python → Código de implementación
```

Cualquier inversión de este orden es una violación del método.

La doctrina cerrada es la fuente de verdad.
El software es su consecuencia, no su causa.

---

**Documento cerrado como CANDIDATE_V1.**

Listo para revisión y congelamiento posterior.
