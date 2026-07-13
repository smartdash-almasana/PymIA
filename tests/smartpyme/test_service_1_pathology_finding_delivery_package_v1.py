from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_pathology_finding_delivery_package_v1 import (
    STATUS_BLOCKED_POLICY_NOT_PASS,
    STATUS_DELIVERY_PACKAGE_CANDIDATE_BUILT,
    Service1PathologyFindingDeliveryPackageV1,
    build_service_1_pathology_finding_delivery_package_v1,
)
from pymia.smartpyme.service_1_pathology_finding_delivery_policy_guard_v1 import (
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_POLICY_BLOCKED,
    STATUS_POLICY_PASS,
    Service1PathologyFindingDeliveryPolicyGuardV1,
)


def _guard(*, status: str = STATUS_POLICY_PASS, owner_confirmation_required: bool = False) -> Service1PathologyFindingDeliveryPolicyGuardV1:
    return Service1PathologyFindingDeliveryPolicyGuardV1(
        schema_version="SERVICE_1_PATHOLOGY_FINDING_DELIVERY_POLICY_GUARD_V1",
        service_name="SERVICE_1",
        status=status,
        case_id="case:s1:001",
        tenant_id="tenant:pyme:001",
        intake_id="intake:s1:001",
        run_id="run:s1:001",
        pathology_code="REN_001",
        allowed_computation_ref="first_aid_precio_margen_basico_v1",
        guard_result="PASS" if status == STATUS_POLICY_PASS else "BLOCKED",
        policy_violations=(),
        required_owner_confirmations=("owner_confirmation_required",) if owner_confirmation_required else (),
        delivery_allowed_candidate=status == STATUS_POLICY_PASS and not owner_confirmation_required,
        blocked_reason=None if status == STATUS_POLICY_PASS else "blocked_by_test",
        owner_confirmation_required=owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )


def test_builds_delivery_package_candidate_from_policy_pass_with_metadata_material() -> None:
    result = build_service_1_pathology_finding_delivery_package_v1(
        delivery_policy_guard_result=_guard(),
        metadata={
            "package_material": {
                "owner_title": "Margen operativo preliminar",
                "owner_summary": "La venta deja margen unitario positivo en la evidencia revisada.",
                "evidence_used": ["precio", "costo", "cantidad"],
                "computed_values": {"unit_margin": 40, "total_margin": 400},
                "limits": ["El alcance queda limitado al archivo revisado."],
                "next_recommended_action": "Confirmar período y revisar precios con el dueño.",
            }
        },
    )

    assert isinstance(result, Service1PathologyFindingDeliveryPackageV1)
    assert result.status == STATUS_DELIVERY_PACKAGE_CANDIDATE_BUILT
    assert result.package_id == "s1:xlsx-first:package:case:s1:001:run:s1:001:REN_001"
    assert result.owner_title == "Margen operativo preliminar"
    assert result.owner_summary.startswith("La venta deja margen")
    assert result.evidence_used == ("precio", "costo", "cantidad")
    assert result.computed_values == {"unit_margin": 40, "total_margin": 400}
    assert result.limits == ("El alcance queda limitado al archivo revisado.",)
    assert result.next_recommended_action == "Confirmar período y revisar precios con el dueño."
    assert result.delivery_allowed_candidate is True
    assert result.delivery_authorized is False


def test_builds_safe_minimal_package_when_policy_pass_has_no_material() -> None:
    result = build_service_1_pathology_finding_delivery_package_v1(
        delivery_policy_guard_result=_guard(),
    )

    assert result.status == STATUS_DELIVERY_PACKAGE_CANDIDATE_BUILT
    assert result.owner_title == "Hallazgo operativo preliminar - REN_001"
    assert "policy guard" in result.owner_summary
    assert result.limits
    assert result.next_recommended_action is not None
    assert result.delivery_allowed_candidate is True
    assert result.delivery_authorized is False


def test_blocks_when_policy_guard_is_not_pass() -> None:
    result = build_service_1_pathology_finding_delivery_package_v1(
        delivery_policy_guard_result=_guard(status=STATUS_POLICY_BLOCKED),
    )

    assert result.status == STATUS_BLOCKED_POLICY_NOT_PASS
    assert result.blocked_reason == "policy_not_pass"
    assert result.owner_title is None
    assert result.delivery_allowed_candidate is False
    assert result.delivery_authorized is False


def test_blocks_policy_not_pass_when_owner_confirmation_is_required() -> None:
    result = build_service_1_pathology_finding_delivery_package_v1(
        delivery_policy_guard_result=_guard(
            status=STATUS_NEEDS_OWNER_CONFIRMATION,
            owner_confirmation_required=True,
        ),
    )

    assert result.status == STATUS_BLOCKED_POLICY_NOT_PASS
    assert result.blocked_reason == "owner_confirmation_required"
    assert result.owner_confirmation_required is True
    assert result.delivery_allowed_candidate is False


def test_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    result = build_service_1_pathology_finding_delivery_package_v1(
        delivery_policy_guard_result=_guard(),
    )

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False


def test_to_dict_does_not_expose_human_review_fields() -> None:
    result = build_service_1_pathology_finding_delivery_package_v1(
        delivery_policy_guard_result=_guard(),
    )
    data = result.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
    assert data["schema_version"] == "SERVICE_1_PATHOLOGY_FINDING_DELIVERY_PACKAGE_V1"


def test_rejects_invalid_policy_guard_type() -> None:
    with pytest.raises(ValueError):
        build_service_1_pathology_finding_delivery_package_v1(
            delivery_policy_guard_result=object(),  # type: ignore[arg-type]
        )
