from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    build_service_1_owner_confirmation_event_v1,
)
from pymia.smartpyme.service_1_tenant_confirmation_persistence_wiring_v1 import (
    STATUS_PERSISTED,
    persist_service_1_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    build_service_1_tenant_identity_contract_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    Service1TenantSemanticContractErrorV1,
)


def _identity():
    return build_service_1_tenant_identity_contract_v1(
        tenant_id="tenant-acme",
        cliente_id="cliente-001",
        case_id="case-001",
        owner_actor_id="owner-001",
        owner_actor_role="OWNER",
        source_system_ref="xlsx_upload",
        source_context_ref="service1-assisted-web",
        workbook_ref="ventas.xlsx",
    )


def _event(*, case_id: str = "case-001", file_ref: str = "ventas.xlsx"):
    return build_service_1_owner_confirmation_event_v1(
        case_id=case_id,
        file_ref=file_ref,
        region_ref=None,
        sheet_ref="Hoja1",
        column_ref="saldo",
        question_ref="q-001",
        owner_answer="saldo pendiente de cobro",
        confirmation_scope="FREE_TEXT_MEANING",
        corrected_meaning="saldo pendiente de cobro",
    )


def test_persists_both_canonical_artifacts_with_identity_authority():
    recorded = []

    result = persist_service_1_owner_confirmation_v1(
        identity_contract=_identity(),
        owner_confirmation_event=_event(),
        source_column_name="Saldo",
        normalized_column_ref="saldo",
        persist_contract=lambda event, contract: recorded.append((event, contract)) or True,
    )

    assert result.status == STATUS_PERSISTED
    assert result.persisted is True
    assert result.tenant_id == "tenant-acme"
    assert result.cliente_id == "cliente-001"
    assert result.case_id == "case-001"
    assert result.confirmation_event_ref == result.contract.confirmation_event_ref
    assert len(recorded) == 1
    event, contract = recorded[0]
    assert event.question_ref == "q-001"
    assert contract.tenant_id == "tenant-acme"
    assert contract.cliente_id == "cliente-001"
    assert contract.owner_actor_id == "owner-001"
    assert contract.owner_actor_role == "OWNER"
    assert contract.workbook_ref == "ventas.xlsx"


@pytest.mark.parametrize(
    ("event", "expected_message"),
    [
        (_event(case_id="case-other"), "case does not match"),
        (_event(file_ref="otro.xlsx"), "workbook does not match"),
    ],
)
def test_blocks_cross_context_before_persistence(event, expected_message):
    calls = 0

    def persist(_event, _contract):
        nonlocal calls
        calls += 1
        return True

    with pytest.raises(Service1TenantSemanticContractErrorV1, match=expected_message):
        persist_service_1_owner_confirmation_v1(
            identity_contract=_identity(),
            owner_confirmation_event=event,
            source_column_name="Saldo",
            normalized_column_ref="saldo",
            persist_contract=persist,
        )

    assert calls == 0


def test_persistence_failure_is_fail_closed():
    def broken_persistence(_event, _contract):
        raise RuntimeError("db unavailable")

    with pytest.raises(
        Service1TenantSemanticContractErrorV1,
        match="tenant semantic persistence failed",
    ):
        persist_service_1_owner_confirmation_v1(
            identity_contract=_identity(),
            owner_confirmation_event=_event(),
            source_column_name="Saldo",
            normalized_column_ref="saldo",
            persist_contract=broken_persistence,
        )


def test_false_or_none_persistence_confirmation_is_blocked():
    for backend_result in (False, None):
        with pytest.raises(
            Service1TenantSemanticContractErrorV1,
            match="did not confirm durable write",
        ):
            persist_service_1_owner_confirmation_v1(
                identity_contract=_identity(),
                owner_confirmation_event=_event(),
                source_column_name="Saldo",
                normalized_column_ref="saldo",
                persist_contract=lambda _event, _contract, value=backend_result: value,
            )
