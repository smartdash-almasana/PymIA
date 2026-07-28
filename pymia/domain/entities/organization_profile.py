"""
OrganizationProfile - entidad núcleo (MODEL §2, §5).

Sistema adaptativo de intercambio económico bajo restricción,
con decisión concentrada, que debe sostenerse financieramente.

Es una ENTIDAD mutable (no frozen) con ciclo de vida propio,
identificada por UUID, que compone las 5 dimensiones estructurales.

Trazabilidad doctrinal:
- PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §2, §4, §5
- PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING.md (OrganizationProfile)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.primitives.exchange_commitment import ExchangeCommitment
from pymia.domain.primitives.organizational_constraint import OrganizationalConstraint
from pymia.domain.primitives.organizational_dependency import OrganizationalDependency
from pymia.domain.primitives.structural_relationship import StructuralRelationship
from pymia.domain.primitives.structural_tension import StructuralTension
from pymia.domain.types.capability_level import CapabilityLevel
from pymia.domain.types.epistemic_state import EpistemicState


@dataclass
class OrganizationProfile:
    """
    Organización PyME - entidad núcleo de dominio.

    Compone las 5 dimensiones estructurales definidas en MODEL §5:
    1. Identidad (declarada/observada/operativa)
    2. Estructura de intercambio (compromisos + relaciones)
    3. Flujo económico (ingresos/transformación/egresos/resultado)
    4. Restricción (constraints + dependencies)
    5. Decisión (principal/proceso/información)

    Invariantes de dominio (MODEL §2, §4, §5):
    - name no vacío (largo >= 2)
    - identity_declared / observed / operational no vacíos
    - exchange_commitments no vacío (sin compromisos no hay organización)
    - constraints no vacío (toda PyME tiene restricciones)
    - decision_principal no vacío (invariante PyME: decisión concentrada)
    - founded_at <= created_at (coherencia temporal)
    - exchange_commitments sin IDs duplicados
    - relationships sin pares (source, target) duplicados
    """

    # Identificación
    id: UUID
    name: str

    # Dimensión 1: Identidad (MODEL §5.1)
    identity_declared: str
    identity_observed: str
    identity_operational: str

    # Dimensión 2: Estructura de intercambio (MODEL §5.2)
    exchange_commitments: List[ExchangeCommitment] = field(default_factory=list)
    relationships: List[StructuralRelationship] = field(default_factory=list)

    # Dimensión 3: Flujo económico (MODEL §5.3)
    flow_revenue: str = ""
    flow_transformation: str = ""
    flow_expenses: str = ""
    flow_result: str = ""

    # Dimensión 4: Restricción (MODEL §5.4)
    constraints: List[OrganizationalConstraint] = field(default_factory=list)
    dependencies: List[OrganizationalDependency] = field(default_factory=list)

    # Dimensión 5: Decisión (MODEL §5.5)
    decision_principal: str = ""
    decision_process: str = ""
    decision_information: str = ""

    # Tensiones estructurales (MODEL §9)
    tensions: List[StructuralTension] = field(default_factory=list)

    # Estado epistémico del perfil
    epistemic_state: EpistemicState = EpistemicState.DECLARED
    capability_level: CapabilityLevel = CapabilityLevel.DECLARADA

    # Timestamps timezone-aware
    founded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Metadata opcional
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validación de invariantes de dominio."""
        # 1. name no vacío y largo mínimo 2
        if not self.name or not self.name.strip():
            raise ValueError("OrganizationProfile requiere name no vacío")
        if len(self.name.strip()) < 2:
            raise ValueError("OrganizationProfile requiere name con largo >= 2")

        # 2. identity_declared no vacío
        if not self.identity_declared or not self.identity_declared.strip():
            raise ValueError("OrganizationProfile requiere identity_declared no vacío")

        # 3. identity_observed no vacío
        if not self.identity_observed or not self.identity_observed.strip():
            raise ValueError("OrganizationProfile requiere identity_observed no vacío")

        # 4. identity_operational no vacío
        if not self.identity_operational or not self.identity_operational.strip():
            raise ValueError("OrganizationProfile requiere identity_operational no vacío")

        # 5. exchange_commitments no vacío
        if not self.exchange_commitments or len(self.exchange_commitments) == 0:
            raise ValueError(
                "OrganizationProfile requiere al menos 1 exchange_commitment "
                "(sin compromisos no hay organización, MODEL §4)"
            )

        # 6. constraints no vacío
        if not self.constraints or len(self.constraints) == 0:
            raise ValueError(
                "OrganizationProfile requiere al menos 1 constraint "
                "(toda PyME tiene restricciones, MODEL §7)"
            )

        # 7. decision_principal no vacío
        if not self.decision_principal or not self.decision_principal.strip():
            raise ValueError(
                "OrganizationProfile requiere decision_principal no vacío "
                "(invariante PyME: decisión concentrada, MODEL §6.1)"
            )

        # 8. founded_at <= created_at
        if self.founded_at > self.created_at:
            raise ValueError(
                f"founded_at ({self.founded_at}) no puede ser posterior a "
                f"created_at ({self.created_at})"
            )

        # 9. exchange_commitments sin IDs duplicados
        commitment_ids = [c.id for c in self.exchange_commitments]
        if len(commitment_ids) != len(set(commitment_ids)):
            raise ValueError("exchange_commitments no puede tener IDs duplicados")

        # 10. relationships sin pares (source, target) duplicados
        if self.relationships:
            relationship_pairs = [
                (r.source_id, r.target_id) for r in self.relationships
            ]
            if len(relationship_pairs) != len(set(relationship_pairs)):
                raise ValueError(
                    "relationships no puede tener pares (source_id, target_id) duplicados"
                )

    def to_dict(self) -> Dict[str, Any]:
        """Serialización JSON-compatible del perfil completo."""
        return {
            "id": str(self.id),
            "name": self.name,
            "identity": {
                "declared": self.identity_declared,
                "observed": self.identity_observed,
                "operational": self.identity_operational,
            },
            "exchange_commitments": [c.to_dict() for c in self.exchange_commitments],
            "relationships": [r.to_dict() for r in self.relationships],
            "flow": {
                "revenue": self.flow_revenue,
                "transformation": self.flow_transformation,
                "expenses": self.flow_expenses,
                "result": self.flow_result,
            },
            "constraints": [c.to_dict() for c in self.constraints],
            "dependencies": [d.to_dict() for d in self.dependencies],
            "decision": {
                "principal": self.decision_principal,
                "process": self.decision_process,
                "information": self.decision_information,
            },
            "tensions": [t.to_dict() for t in self.tensions],
            "epistemic_state": self.epistemic_state.value,
            "capability_level": self.capability_level.value,
            "founded_at": self.founded_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrganizationProfile":
        """Reconstrucción desde diccionario serializado.

        Delega reconstrucción de primitives en sus propios from_dict.
        """
        identity = data.get("identity", {})
        flow = data.get("flow", {})
        decision = data.get("decision", {})

        # Reconstruir ExchangeCommitment (M1)
        commitments = [
            ExchangeCommitment.from_dict(c)
            for c in data.get("exchange_commitments", [])
        ]

        # Reconstruir StructuralRelationship (M2)
        relationships = [
            StructuralRelationship.from_dict(r)
            for r in data.get("relationships", [])
        ]

        # Reconstruir OrganizationalConstraint (M2)
        constraints = [
            OrganizationalConstraint.from_dict(c)
            for c in data.get("constraints", [])
        ]

        # Reconstruir OrganizationalDependency (M2)
        dependencies = [
            OrganizationalDependency.from_dict(d)
            for d in data.get("dependencies", [])
        ]

        # Reconstruir StructuralTension (M2)
        tensions = [
            StructuralTension.from_dict(t)
            for t in data.get("tensions", [])
        ]

        # Parsear timestamps
        founded_at = datetime.fromisoformat(data["founded_at"])
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])

        # Parsear enums
        epistemic_state = EpistemicState(data["epistemic_state"])
        capability_level = CapabilityLevel(data["capability_level"])

        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            identity_declared=identity.get("declared", ""),
            identity_observed=identity.get("observed", ""),
            identity_operational=identity.get("operational", ""),
            exchange_commitments=commitments,
            relationships=relationships,
            flow_revenue=flow.get("revenue", ""),
            flow_transformation=flow.get("transformation", ""),
            flow_expenses=flow.get("expenses", ""),
            flow_result=flow.get("result", ""),
            constraints=constraints,
            dependencies=dependencies,
            decision_principal=decision.get("principal", ""),
            decision_process=decision.get("process", ""),
            decision_information=decision.get("information", ""),
            tensions=tensions,
            epistemic_state=epistemic_state,
            capability_level=capability_level,
            founded_at=founded_at,
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata"),
        )

    def add_commitment(self, commitment: ExchangeCommitment) -> None:
        """Agrega un compromiso validando no-duplicados."""
        existing_ids = {c.id for c in self.exchange_commitments}
        if commitment.id in existing_ids:
            raise ValueError(
                f"ExchangeCommitment con id {commitment.id} ya existe en el perfil"
            )
        self.exchange_commitments.append(commitment)
        self.updated_at = datetime.now(timezone.utc)

    def add_constraint(self, constraint: OrganizationalConstraint) -> None:
        """Agrega una restricción."""
        self.constraints.append(constraint)
        self.updated_at = datetime.now(timezone.utc)

    def add_relationship(self, relationship: StructuralRelationship) -> None:
        """Agrega una relación validando no-duplicados."""
        existing_pairs = {
            (r.source_id, r.target_id) for r in self.relationships
        }
        new_pair = (relationship.source_id, relationship.target_id)
        if new_pair in existing_pairs:
            raise ValueError(
                f"StructuralRelationship ({new_pair[0]}, {new_pair[1]}) ya existe"
            )
        self.relationships.append(relationship)
        self.updated_at = datetime.now(timezone.utc)

    def mark_validated(self) -> None:
        """Marca el perfil como validado epistémicamente."""
        self.epistemic_state = EpistemicState.VALIDATED
        self.updated_at = datetime.now(timezone.utc)
