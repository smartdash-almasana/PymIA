from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    build_service_1_owner_confirmation_event_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_store_v1 import (
    append_service_1_tenant_semantic_contract_v1,
    list_service_1_tenant_semantic_contracts_v1,
    load_service_1_tenant_semantic_contract_by_id_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    Service1TenantSemanticContractErrorV1,
    build_service_1_tenant_semantic_contract_v1,
)


def _event(*, role: str = "sales_amount", timestamp: str = "2026-08-07T12:00:00+00:00"):
    return build_service_1_owner_confirmation_event_v1(
        case_id="case_1",
        file_ref="sha256:workbook-safe-ref",
        region_ref="region_1",
        sheet_ref="Ventas",
        column_ref="Importe",
        question_ref="q_importe",
        owner_answer="OWNER_CONFIRMED",
        proposed_role=role,
        proposed_variable="sales_total",
        confirmed_role=role,
        confirmation_scope="SEMANTIC_ROLE",
        timestamp=timestamp,
        provenance={"producer": "focal_test"},
    )


def _contract(*, tenant_id: str = "tenant_a", revision: int = 1, supersedes_contract=None, event=None):
    return build_service_1_tenant_semantic_contract_v1(
        tenant_id=tenant_id,
        cliente_id=None,
        owner_actor_id="owner_7",
        owner_actor_role="PYME_OWNER",
        source_system_ref="erp_ventas",
        source_context_ref="export_ventas_v1",
        workbook_ref="sha256:workbook-safe-ref",
        expected_case_id="case_1",
        expected_sheet_ref="Ventas",
        expected_question_ref="q_importe",
        source_column_name="Importe",
        normalized_column_ref="importe",
        owner_confirmation_event=event or _event(),
        revision=revision,
        supersedes_contract=supersedes_contract,
    )


def _assert_code(exc: pytest.ExceptionInfo[Service1TenantSemanticContractErrorV1], code: str) -> None:
    assert exc.value.code == code


def test_ts02_ts03_append_and_exact_round_trip(tmp_path: Path) -> None:
    contract = _contract()

    result = append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path,
        tenant_id="tenant_a",
        contract=contract,
    )
    loaded = load_service_1_tenant_semantic_contract_by_id_v1(
        base_dir=tmp_path,
        tenant_id="tenant_a",
        contract_id=contract.contract_id,
    )

    assert result.status == "TENANT_SEMANTIC_CONTRACT_RECORDED"
    assert result.contract_id == contract.contract_id
    assert result.path == tmp_path.resolve() / "tenant_a" / "tenant_semantic_contracts.jsonl"
    assert loaded == contract
    assert loaded is not contract
    assert loaded.to_dict() == contract.to_dict()


def test_ts04_list_is_tenant_scoped_and_preserves_insertion_order(tmp_path: Path) -> None:
    first = _contract()
    second = _contract(
        revision=2,
        supersedes_contract=first,
        event=_event(role="net_sales", timestamp="2026-08-07T13:00:00+00:00"),
    )
    tenant_b = _contract(tenant_id="tenant_b")

    for tenant_id, contract in (("tenant_a", first), ("tenant_a", second), ("tenant_b", tenant_b)):
        append_service_1_tenant_semantic_contract_v1(
            base_dir=tmp_path, tenant_id=tenant_id, contract=contract
        )

    assert list_service_1_tenant_semantic_contracts_v1(
        base_dir=tmp_path, tenant_id="tenant_a"
    ) == (first, second)
    assert list_service_1_tenant_semantic_contracts_v1(
        base_dir=tmp_path, tenant_id="tenant_b"
    ) == (tenant_b,)


def test_ts05_cross_tenant_load_never_searches_globally(tmp_path: Path) -> None:
    tenant_a = _contract()
    append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=tenant_a
    )

    assert (
        load_service_1_tenant_semantic_contract_by_id_v1(
            base_dir=tmp_path,
            tenant_id="tenant_b",
            contract_id=tenant_a.contract_id,
        )
        is None
    )


@pytest.mark.parametrize("tenant_id", ["../escape", "a/b", r"a\\b", "  "])
def test_ts06_unsafe_tenant_id_is_hard_blocked(tmp_path: Path, tenant_id: str) -> None:
    with pytest.raises(ValueError):
        list_service_1_tenant_semantic_contracts_v1(
            base_dir=tmp_path, tenant_id=tenant_id
        )


def test_store_rejects_argument_record_tenant_mismatch(tmp_path: Path) -> None:
    with pytest.raises(Service1TenantSemanticContractErrorV1) as exc:
        append_service_1_tenant_semantic_contract_v1(
            base_dir=tmp_path,
            tenant_id="tenant_b",
            contract=_contract(tenant_id="tenant_a"),
        )
    _assert_code(exc, "BLOCKED_CROSS_TENANT_ACCESS")


def test_ts09_revision_two_appends_without_mutating_revision_one(tmp_path: Path) -> None:
    first = _contract()
    second = _contract(
        revision=2,
        supersedes_contract=first,
        event=_event(role="net_sales", timestamp="2026-08-07T13:00:00+00:00"),
    )

    append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=first
    )
    original_line = (
        tmp_path / "tenant_a" / "tenant_semantic_contracts.jsonl"
    ).read_text(encoding="utf-8").splitlines()[0]
    append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=second
    )
    lines = (
        tmp_path / "tenant_a" / "tenant_semantic_contracts.jsonl"
    ).read_text(encoding="utf-8").splitlines()

    assert lines[0] == original_line
    assert len(lines) == 2
    assert [item.revision for item in list_service_1_tenant_semantic_contracts_v1(
        base_dir=tmp_path, tenant_id="tenant_a"
    )] == [1, 2]


def test_ts12_identical_append_is_idempotent(tmp_path: Path) -> None:
    contract = _contract()
    first = append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=contract
    )
    second = append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=contract
    )

    assert first.status == "TENANT_SEMANTIC_CONTRACT_RECORDED"
    assert second.status == "TENANT_SEMANTIC_CONTRACT_ALREADY_RECORDED"
    assert len(list_service_1_tenant_semantic_contracts_v1(
        base_dir=tmp_path, tenant_id="tenant_a"
    )) == 1


def test_ts13_reused_contract_id_with_different_payload_blocks(tmp_path: Path) -> None:
    contract = _contract()
    conflicting = replace(contract, owner_actor_id="another_owner")
    append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=contract
    )

    with pytest.raises(Service1TenantSemanticContractErrorV1) as exc:
        append_service_1_tenant_semantic_contract_v1(
            base_dir=tmp_path, tenant_id="tenant_a", contract=conflicting
        )
    _assert_code(exc, "BLOCKED_CONTRACT_ID_CONFLICT")


def test_corrupt_or_hash_invalid_stored_record_blocks_load(tmp_path: Path) -> None:
    contract = _contract()
    append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path, tenant_id="tenant_a", contract=contract
    )
    path = tmp_path / "tenant_a" / "tenant_semantic_contracts.jsonl"
    path.write_text(
        path.read_text(encoding="utf-8").replace('"mapping_series_id":"tsm_', '"mapping_series_id":"tampered_'),
        encoding="utf-8",
    )

    with pytest.raises(Service1TenantSemanticContractErrorV1):
        list_service_1_tenant_semantic_contracts_v1(
            base_dir=tmp_path, tenant_id="tenant_a"
        )
