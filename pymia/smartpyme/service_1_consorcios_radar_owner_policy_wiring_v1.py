"""Owner-policy wiring for the Consorcios RADAR vertical.

This module joins an already verified Servicio 1 tenant identity with the
Consorcios RADAR catalog, owner-confirmed policy creation, durable policy
persistence, and evaluation of persisted policies. It does not authenticate
users, invent thresholds, or assign business significance.
"""
from __future__ import annotations

from typing import Mapping, Protocol

from pymia.smartpyme.service_1_consorcios_radar_plug_v1 import (
    ConsorciosRadarObservationV1,
    consorcios_radar_catalog_v1,
)
from pymia.smartpyme.service_1_radar_engine_v1 import (
    RadarEventV1,
    evaluate_persisted_radar_observation_v1,
)
from pymia.smartpyme.service_1_radar_observation_policy_v1 import (
    RadarObservationPolicyV1,
    build_radar_observation_policy_v1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    Service1TenantIdentityContractV1,
)

SCHEMA_VERSION = "SERVICE_1_CONSORCIOS_RADAR_OWNER_POLICY_WIRING_V1"


class RadarOwnerPolicyStoreV1(Protocol):
    def save_policy(self, policy: RadarObservationPolicyV1) -> bool: ...

    def list_policies(
        self, *, tenant_id: str, enabled_only: bool = False
    ) -> tuple[RadarObservationPolicyV1, ...]: ...


def _require_identity(
    identity_contract: object,
) -> Service1TenantIdentityContractV1:
    if not isinstance(identity_contract, Service1TenantIdentityContractV1):
        raise ValueError("verified tenant identity contract is required")
    if not identity_contract.tenant_id.strip():
        raise ValueError("verified tenant identity is missing tenant_id")
    if not identity_contract.owner_actor_id.strip():
        raise ValueError("verified tenant identity is missing owner_actor_id")
    if not identity_contract.owner_actor_role.strip():
        raise ValueError("verified tenant identity is missing owner_actor_role")
    return identity_contract


def build_consorcios_radar_owner_menu_v1(
    *, identity_contract: object
) -> dict[str, object]:
    """Return the neutral Consorcios observable menu for one verified owner."""
    identity = _require_identity(identity_contract)
    observables = consorcios_radar_catalog_v1()
    return {
        "schema_version": SCHEMA_VERSION,
        "tenant_id": identity.tenant_id,
        "owner_actor_id": identity.owner_actor_id,
        "vertical_ref": "consorcios",
        "observables": [item.to_dict() for item in observables],
        "owner_authority": {
            "select_observable": True,
            "select_operator": True,
            "set_comparison_value": True,
            "select_communication_level": True,
            "confirmation_required": True,
        },
    }


def persist_consorcios_radar_owner_policy_v1(
    *,
    identity_contract: object,
    owner_request: Mapping[str, object],
    policy_store: RadarOwnerPolicyStoreV1,
) -> RadarObservationPolicyV1:
    """Validate and persist one explicitly owner-confirmed Consorcios policy."""
    identity = _require_identity(identity_contract)
    if not isinstance(owner_request, Mapping):
        raise ValueError("owner_request must be a mapping")
    if owner_request.get("confirmed_by_owner") is not True:
        raise ValueError("explicit owner confirmation is required")

    observable_ref = str(owner_request.get("observable_ref") or "").strip()
    catalog = {item.observable_ref: item for item in consorcios_radar_catalog_v1()}
    observable = catalog.get(observable_ref)
    if observable is None:
        raise ValueError("observable_ref is not offered by Consorcios RADAR")

    comparison_value = owner_request.get("comparison_value")
    if not isinstance(comparison_value, (str, bool)):
        raise ValueError("comparison_value must be string or boolean")

    policy = build_radar_observation_policy_v1(
        tenant_id=identity.tenant_id,
        policy_ref=str(owner_request.get("policy_ref") or "").strip(),
        observable=observable,
        enabled=owner_request.get("enabled") is True,
        operator=str(owner_request.get("operator") or "").strip(),
        comparison_value=comparison_value,
        communication_level=str(owner_request.get("communication_level") or "").strip(),
        confirmed_by_owner=True,
    )
    if policy_store.save_policy(policy) is not True:
        raise ValueError("RADAR owner policy persistence failed")
    return policy


def evaluate_consorcios_radar_observation_with_owner_policy_v1(
    *,
    identity_contract: object,
    observation: ConsorciosRadarObservationV1,
    policy_store: RadarOwnerPolicyStoreV1,
) -> tuple[RadarEventV1, ...]:
    """Evaluate one real Consorcios observation using persisted tenant policies."""
    identity = _require_identity(identity_contract)
    if observation.observable.vertical_ref != "consorcios":
        raise ValueError("observation must belong to Consorcios RADAR")
    return evaluate_persisted_radar_observation_v1(
        tenant_id=identity.tenant_id,
        observable=observation.observable,
        observed_value=observation.observed_value,
        policy_store=policy_store,
    )


__all__ = [
    "SCHEMA_VERSION",
    "RadarOwnerPolicyStoreV1",
    "build_consorcios_radar_owner_menu_v1",
    "persist_consorcios_radar_owner_policy_v1",
    "evaluate_consorcios_radar_observation_with_owner_policy_v1",
]
