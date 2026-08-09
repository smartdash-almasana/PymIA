from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_tenant_identity_contract_store_v1 import (
    append_service_1_tenant_identity_contract_v1,
    list_service_1_tenant_identity_contracts_v1,
    load_service_1_tenant_identity_contract_by_id_v1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    Service1TenantIdentityContractErrorV1,
    build_service_1_tenant_identity_contract_v1,
)


def _contract(*, tenant_id: str = "tenant_a", case_id: str = "case_1", owner_actor_id: str = "owner_7"):
    return build_service_1_tenant_identity_contract_v1(
        tenant_id=tenant_id,
        case_id=case_id,
        owner_actor_id=owner_actor_id,
        owner_actor_role="PYME_OWNER",
        source_system_ref="erp_ventas",
        source_context_ref="export_ventas_v1",
        workbook_ref="sha256:workbook-safe-ref",
    )


def _assert_code(exc: pytest.ExceptionInfo[Service1TenantIdentityContractErrorV1], code: str) -> None:
    assert exc.value.code == code


def test_ti09_append_and_exact_round_trip(tmp_path: Path) -> None:
    contract = _contract()

    result = append_service_1_tenant_identity_contract_v1(
        base_dir=tmp_path,
        tenant_id="tenant_a",
        contract=contract,
    )
    loaded = load_service_1_tenant_identity_contract_by_id_v1(
        base_dir=tmp_path,
        tenant_id="tenant_a",
        identity_contract_id=contract.identity_contract_id,
    )

    assert result.status == "TENANT_IDENTITY_CONTRACT_RECORDED"
    assert result.identity_contract_id == contract.identity_contract_id
    assert result.path == tmp_path.resolve() / "tenant_a" / "tenant_identity_contracts.jsonl"
    assert loaded == contract
    assert loaded is not contract
    assert loaded.to_dict() == contract.to_dict()


def test_ti10_tenant_a_cannot_load_or_list_through_tenant_b(tmp_path: Path) -> None:
    tenant_a = _contract()
    append_service_1_tenant_identity_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=tenant_a
    )

    assert (
        load_service_1_tenant_identity_contract_by_id_v1(
            base_dir=tmp_path,
            tenant_id="tenant_b",
            identity_contract_id=tenant_a.identity_contract_id,
        )
        is None
    )
    assert list_service_1_tenant_identity_contracts_v1(
        base_dir=tmp_path, tenant_id="tenant_b"
    ) == ()


def test_ti11_identical_append_is_idempotent(tmp_path: Path) -> None:
    contract = _contract()
    first = append_service_1_tenant_identity_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=contract
    )
    second = append_service_1_tenant_identity_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=contract
    )

    assert first.status == "TENANT_IDENTITY_CONTRACT_RECORDED"
    assert second.status == "TENANT_IDENTITY_CONTRACT_ALREADY_RECORDED"
    assert len(
        list_service_1_tenant_identity_contracts_v1(base_dir=tmp_path, tenant_id="tenant_a")
    ) == 1


def test_ti12_same_id_with_different_payload_blocks(tmp_path: Path) -> None:
    contract = _contract()
    appendixed = append_service_1_tenant_identity_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=contract
    )

    conflicting_payload = contract.to_dict()
    conflicting_payload["owner_actor_id"] = "owner_different"
    conflicting_payload["identity_contract_id"] = contract.identity_contract_id

    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        append_service_1_tenant_identity_contract_v1(
            base_dir=tmp_path,
            tenant_id="tenant_a",
            contract=conflicting_payload,
        )
    _assert_code(exc, "BLOCKED_IDENTITY_CONTRACT_CONFLICT")


def test_append_rejects_argument_tenant_mismatch(tmp_path: Path) -> None:
    contract = _contract(tenant_id="tenant_a")
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        append_service_1_tenant_identity_contract_v1(
            base_dir=tmp_path,
            tenant_id="tenant_b",
            contract=contract,
        )
    _assert_code(exc, "BLOCKED_CROSS_TENANT_ACCESS")


def test_store_rejects_cross_tenant_entries_in_single_artifact(tmp_path: Path) -> None:
    contract_a = _contract()
    append_service_1_tenant_identity_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=contract_a
    )
    contract_b = _contract(tenant_id="tenant_b", case_id="case_b")
    append_service_1_tenant_identity_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_b", contract=contract_b
    )
    line_b = (
        tmp_path / "tenant_b" / "tenant_identity_contracts.jsonl"
    ).read_text(encoding="utf-8").splitlines()[0]
    path_a = tmp_path / "tenant_a" / "tenant_identity_contracts.jsonl"
    path_a.write_text(
        path_a.read_text(encoding="utf-8") + line_b + "\n",
        encoding="utf-8",
    )

    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        list_service_1_tenant_identity_contracts_v1(base_dir=tmp_path, tenant_id="tenant_a")
    _assert_code(exc, "BLOCKED_CROSS_TENANT_ACCESS")


@pytest.mark.parametrize("tenant_id", ["../escape", "a/b", r"a\\b", "  "])
def test_ti08_store_unsafe_tenant_identity_blocks(tmp_path: Path, tenant_id: str) -> None:
    with pytest.raises(ValueError):
        list_service_1_tenant_identity_contracts_v1(
            base_dir=tmp_path, tenant_id=tenant_id
        )


def test_load_requires_contract_id(tmp_path: Path) -> None:
    with pytest.raises(Service1TenantIdentityContractErrorV1) as exc:
        load_service_1_tenant_identity_contract_by_id_v1(
            base_dir=tmp_path,
            tenant_id="tenant_a",
            identity_contract_id="",
        )
    assert exc.value.code == "BLOCKED_IDENTITY_CONTEXT_MISMATCH"