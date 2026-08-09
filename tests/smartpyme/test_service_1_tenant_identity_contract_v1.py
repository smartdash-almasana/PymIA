from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    SCHEMA_VERSION,
    STATUS_READY,
    Service1TenantIdentityContractErrorV1,
    Service1TenantIdentityContractV1,
    build_service_1_tenant_identity_contract_v1,
    service_1_tenant_identity_contract_from_mapping_v1,
)


def _contract(
    *,
    tenant_id: str = "tenant_a",
    case_id: str = "case_1",
    cliente_id: str | None = None,
    owner_actor_id: str = "owner_7",
    owner_actor_role: str = "PYME_OWNER",
    source_system_ref: str = "erp_ventas",
    source_context_ref: str = "export_ventas_v1",
    workbook_ref: str = "sha256:workbook-safe-ref",
):
    return build_service_1_tenant_identity_contract_v1(
        tenant_id=tenant_id,
        case_id=case_id,
        cliente_id=cliente_id,
        owner_actor_id=owner_actor_id,
        owner_actor_role=owner_actor_role,
        source_system_ref=source_system_ref,
        source_context_ref=source_context_ref,
        workbook_ref=workbook_ref,
    )


def _assert_code(exc: pytest.ExceptionInfo[Service1TenantIdentityContractErrorV1], code: str) -> None:
    assert exc.value.code == code


def test_ti01_valid_immutable_contract() -> None:
    contract = _contract()

    assert contract.schema_version == SCHEMA_VERSION
    assert contract.status == STATUS_READY
    assert contract.tenant_id == "tenant_a"
    assert contract.case_id == "case_1"
    assert contract.owner_actor_id == "owner_7"
    assert contract.owner_actor_role == "PYME_OWNER"
    assert contract.source_system_ref == "erp_ventas"
    assert contract.source_context_ref == "export_ventas_v1"
    assert contract.workbook_ref == "sha256:workbook-safe-ref"
    assert contract.identity_contract_id.startswith("tiic_")

    with pytest.raises(FrozenInstanceError):
        contract.tenant_id = "tenant_b"  # type: ignore[misc]

    round_tripped = service_1_tenant_identity_contract_from_mapping_v1(contract.to_dict())
    assert round_tripped == contract
    assert round_tripped.to_dict() == contract.to_dict()


def test_ti01_identity_id_is_deterministic_over_safe_fields() -> None:
    first = _contract()
    second = _contract()

    assert first.identity_contract_id == second.identity_contract_id


def test_ti02_missing_tenant_blocks() -> None:
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(tenant_id="")
    _assert_code(exc, "BLOCKED_MISSING_TENANT_ID")

    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(tenant_id="   ")
    _assert_code(exc, "BLOCKED_MISSING_TENANT_ID")


def test_ti03_missing_case_blocks() -> None:
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(case_id="")
    _assert_code(exc, "BLOCKED_MISSING_CASE_ID")


def test_ti04_missing_owner_actor_id_blocks() -> None:
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(owner_actor_id="")
    _assert_code(exc, "BLOCKED_MISSING_OWNER_IDENTITY")


def test_ti05_missing_owner_actor_role_blocks() -> None:
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(owner_actor_role="")
    _assert_code(exc, "BLOCKED_MISSING_OWNER_IDENTITY")


def test_ti06_missing_source_system_blocks() -> None:
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(source_system_ref="")
    _assert_code(exc, "BLOCKED_MISSING_SOURCE_IDENTITY")


def test_ti07_missing_source_context_blocks() -> None:
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(source_context_ref="")
    _assert_code(exc, "BLOCKED_MISSING_SOURCE_IDENTITY")


@pytest.mark.parametrize("tenant_id", ["../escape", "a/b", r"a\\b"])
def test_ti08_unsafe_tenant_path_blocks(tenant_id: str) -> None:
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(tenant_id=tenant_id)
    _assert_code(exc, "BLOCKED_INVALID_TENANT_IDENTITY")


def test_ti13_cliente_id_optional_and_never_auto_derived() -> None:
    without_client = _contract(cliente_id=None)
    with_client = _contract(cliente_id="cliente_99")

    assert without_client.cliente_id is None
    assert with_client.cliente_id == "cliente_99"
    assert without_client.tenant_id != with_client.tenant_id or without_client.identity_contract_id != with_client.identity_contract_id
    assert without_client.tenant_id == "tenant_a"
    assert with_client.tenant_id == "tenant_a"
    assert "cliente_id" not in without_client.to_dict().get("provenance", {})
    assert with_client.to_dict()["cliente_id"] == "cliente_99"


def test_ti14_no_session_id_fallback_or_field_authority() -> None:
    contract = _contract()

    assert "session_id" not in contract.to_dict()
    with pytest.raises(TypeError):
        build_service_1_tenant_identity_contract_v1(  # type: ignore[call-arg]
            tenant_id="tenant_a",
            case_id="case_1",
            owner_actor_id="owner_7",
            owner_actor_role="PYME_OWNER",
            source_system_ref="erp_ventas",
            source_context_ref="export_ventas_v1",
            workbook_ref="sha256:workbook-safe-ref",
            session_id="session_x",
        )


@pytest.mark.parametrize(
    "provenance",
    [
        {"runtime_authorized": True},
        {"automatic_reuse_authorized": True},
        {"semantic_rebind_authorized": True},
        {"token": "secret"},
        {"raw_rows": "[[1, 2]]"},
        {"session_id": "session_x"},
    ],
)
def test_ti15_forbidden_provenance_claims_block(provenance: dict[str, object]) -> None:
    payload = _contract().to_dict()
    payload["provenance"] = provenance

    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        service_1_tenant_identity_contract_from_mapping_v1(payload)
    _assert_code(exc, "BLOCKED_IDENTITY_CONTEXT_MISMATCH")


def test_ti15_authority_flags_serialized_false() -> None:
    contract = _contract()
    for flag in (
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
        "automatic_reuse_authorized",
        "semantic_rebind_authorized",
    ):
        assert contract.to_dict()[flag] is False


def test_ti16_forbidden_modules_do_not_reference_identity_contract() -> None:
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    forbidden = (
        "pymia/smartpyme/service_1_product_pipeline_v1.py",
        "pymia/smartpyme/service_1_assisted_web_v1.py",
        "pymia/smartpyme/service_1_owner_confirmation_event_v1.py",
        "pymia/smartpyme/service_1_tenant_semantic_contract_v1.py",
        "pymia/smartpyme/service_1_tenant_semantic_contract_store_v1.py",
    )
    for relative in forbidden:
        source = (repo_root / relative).read_text(encoding="utf-8")
        assert "service_1_tenant_identity_contract" not in source


def test_ti17_case_id_or_case_derived_value_cannot_become_tenant_authority() -> None:
    case_id = "case_abc123"
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(tenant_id=case_id, case_id=case_id)
    _assert_code(exc, "BLOCKED_INVALID_TENANT_IDENTITY")

    payload = _contract(case_id=case_id).to_dict()
    payload["tenant_id"] = case_id
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        service_1_tenant_identity_contract_from_mapping_v1(payload)
    _assert_code(exc, "BLOCKED_INVALID_TENANT_IDENTITY")


def test_ti18_missing_workbook_ref_blocks_and_stays_explicit() -> None:
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        _contract(workbook_ref="")
    _assert_code(exc, "BLOCKED_MISSING_SOURCE_IDENTITY")

    contract = _contract()
    assert contract.workbook_ref == "sha256:workbook-safe-ref"
    assert contract.to_dict()["workbook_ref"] == "sha256:workbook-safe-ref"

    payload = contract.to_dict()
    payload["workbook_ref"] = ""
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        service_1_tenant_identity_contract_from_mapping_v1(payload)
    _assert_code(exc, "BLOCKED_MISSING_SOURCE_IDENTITY")


def test_ti17_independent_case_and_tenant_identity() -> None:
    contract = _contract(tenant_id="tenant_a", case_id="case_1")
    assert contract.tenant_id != contract.case_id
    assert "case_id" not in contract.to_dict()["provenance"]


def test_mapping_rejects_missing_serialized_fields() -> None:
    payload = _contract().to_dict()
    del payload["owner_actor_role"]

    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        service_1_tenant_identity_contract_from_mapping_v1(payload)
    _assert_code(exc, "BLOCKED_IDENTITY_CONTEXT_MISMATCH")
