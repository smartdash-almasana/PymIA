from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    build_service_1_owner_confirmation_event_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    Service1TenantSemanticContractErrorV1,
    build_service_1_tenant_semantic_contract_v1,
)


def _event(
    *,
    case_id: str = "case_1",
    sheet_ref: str = "Ventas",
    column_ref: str = "importe",
    question_ref: str = "q_importe",
    scope: str = "SEMANTIC_ROLE",
    confirmed_role: str | None = "sales_amount",
    corrected_meaning: str | None = None,
):
    return build_service_1_owner_confirmation_event_v1(
        case_id=case_id,
        file_ref="sha256:workbook-safe-ref",
        region_ref="region_1",
        sheet_ref=sheet_ref,
        column_ref=column_ref,
        question_ref=question_ref,
        owner_answer="OWNER_CONFIRMED",
        proposed_role=confirmed_role,
        proposed_variable="sales_total",
        confirmed_role=confirmed_role,
        corrected_meaning=corrected_meaning,
        confirmation_scope=scope,
        timestamp="2026-08-07T12:00:00+00:00",
        provenance={"producer": "focal_test"},
    )


def _build(**overrides):
    values = {
        "tenant_id": "tenant_a",
        "cliente_id": "cliente_42",
        "owner_actor_id": "owner_7",
        "owner_actor_role": "PYME_OWNER",
        "source_system_ref": "erp_ventas",
        "source_context_ref": "export_ventas_v1",
        "workbook_ref": "sha256:workbook-safe-ref",
        "expected_case_id": "case_1",
        "expected_sheet_ref": "Ventas",
        "expected_question_ref": "q_importe",
        "source_column_name": "Importe",
        "normalized_column_ref": "importe",
        "owner_confirmation_event": _event(),
        "inferred_data_type": "decimal",
        "neighboring_column_refs": ("fecha", "cliente"),
        "vertical_ref": "DISTRIBUIDORA_MAYORISTA",
    }
    values.update(overrides)
    return build_service_1_tenant_semantic_contract_v1(**values)


def _assert_code(exc: pytest.ExceptionInfo[Service1TenantSemanticContractErrorV1], code: str) -> None:
    assert exc.value.code == code


def test_ts01_valid_event_builds_ready_immutable_contract() -> None:
    contract = _build()

    assert contract.status == "TENANT_SEMANTIC_CONTRACT_READY"
    assert contract.revision == 1
    assert contract.tenant_id == "tenant_a"
    assert contract.case_id == "case_1"
    assert contract.confirmed_role == "sales_amount"
    assert contract.column_excluded is False
    assert contract.mapping_series_id.startswith("tsm_")
    assert contract.contract_id.startswith("tsc_")
    assert contract.confirmation_event_ref.startswith("oce_")
    with pytest.raises(FrozenInstanceError):
        contract.tenant_id = "tenant_b"  # type: ignore[misc]


@pytest.mark.parametrize("field", ["owner_actor_id", "owner_actor_role"])
def test_ts07_missing_actor_identity_blocks(field: str) -> None:
    with pytest.raises(Service1TenantSemanticContractErrorV1) as exc:
        _build(**{field: "  "})
    _assert_code(exc, "BLOCKED_MISSING_ACTOR_IDENTITY")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_system_ref", ""),
        ("source_context_ref", ""),
        ("workbook_ref", ""),
        ("expected_case_id", ""),
        ("expected_sheet_ref", ""),
        ("expected_question_ref", ""),
        ("source_column_name", ""),
        ("normalized_column_ref", ""),
    ],
)
def test_missing_source_context_blocks(field: str, value: str) -> None:
    with pytest.raises(Service1TenantSemanticContractErrorV1) as exc:
        _build(**{field: value})
    _assert_code(exc, "BLOCKED_MISSING_SOURCE_CONTEXT")


def test_missing_tenant_blocks() -> None:
    with pytest.raises(Service1TenantSemanticContractErrorV1) as exc:
        _build(tenant_id=" ")
    _assert_code(exc, "BLOCKED_MISSING_TENANT_ID")


@pytest.mark.parametrize(
    ("overrides",),
    [
        ({"workbook_ref": "sha256:another-workbook"},),
        ({"normalized_column_ref": "total"},),
        ({"expected_case_id": "case_other"},),
        ({"expected_sheet_ref": "Cobros"},),
        ({"expected_question_ref": "q_other"},),
    ],
)
def test_ts08_event_context_mismatch_blocks(overrides: dict[str, object]) -> None:
    with pytest.raises(Service1TenantSemanticContractErrorV1) as exc:
        _build(**overrides)
    _assert_code(exc, "BLOCKED_EVENT_CONTEXT_MISMATCH")


def test_ts10_revision_two_requires_prior_contract() -> None:
    with pytest.raises(Service1TenantSemanticContractErrorV1) as exc:
        _build(revision=2)
    _assert_code(exc, "BLOCKED_REVISION_INVALID")


def test_ts11_supersession_must_keep_tenant_and_mapping_series() -> None:
    prior = _build()
    with pytest.raises(Service1TenantSemanticContractErrorV1) as tenant_exc:
        _build(tenant_id="tenant_b", revision=2, supersedes_contract=prior)
    _assert_code(tenant_exc, "BLOCKED_SUPERSESSION_MISMATCH")

    with pytest.raises(Service1TenantSemanticContractErrorV1) as series_exc:
        _build(
            source_context_ref="another_export",
            revision=2,
            supersedes_contract=prior,
        )
    _assert_code(series_exc, "BLOCKED_SUPERSESSION_MISMATCH")


def test_valid_revision_two_is_new_and_preserves_prior() -> None:
    prior = _build()
    corrected_event = _event(confirmed_role="net_sales")
    current = _build(
        owner_confirmation_event=corrected_event,
        revision=2,
        supersedes_contract=prior,
    )

    assert current.revision == 2
    assert current.supersedes_contract_id == prior.contract_id
    assert current.mapping_series_id == prior.mapping_series_id
    assert current.contract_id != prior.contract_id
    assert prior.revision == 1
    assert prior.supersedes_contract_id is None


def test_ts14_semantic_role_without_role_is_rejected_by_canonical_event() -> None:
    with pytest.raises(ValueError):
        _event(confirmed_role=None)


def test_ts15_column_exclusion_cannot_carry_a_role() -> None:
    with pytest.raises(ValueError):
        _event(scope="COLUMN_EXCLUSION", confirmed_role="sales_amount")


def test_column_exclusion_projects_without_semantic_role() -> None:
    event = _event(scope="COLUMN_EXCLUSION", confirmed_role=None)
    contract = _build(owner_confirmation_event=event)

    assert contract.column_excluded is True
    assert contract.confirmed_role is None
    assert contract.confirmed_variable is None


def test_ts16_free_text_requires_corrected_meaning() -> None:
    with pytest.raises(ValueError):
        _event(scope="FREE_TEXT_MEANING", confirmed_role=None)


def test_free_text_projects_as_non_computable_meaning() -> None:
    event = _event(
        scope="FREE_TEXT_MEANING",
        confirmed_role=None,
        corrected_meaning="importe reservado internamente",
    )
    contract = _build(owner_confirmation_event=event)

    assert contract.corrected_meaning == "importe reservado internamente"
    assert contract.confirmed_role is None
    assert contract.semantic_rebind_authorized is False


def test_ts17_forbidden_authority_claim_in_event_provenance_blocks() -> None:
    with pytest.raises(ValueError):
        build_service_1_owner_confirmation_event_v1(
            case_id="case_1",
            file_ref="safe",
            region_ref=None,
            sheet_ref="Ventas",
            column_ref="importe",
            question_ref="q_importe",
            owner_answer="OWNER_CONFIRMED",
            confirmed_role="sales_amount",
            confirmation_scope="SEMANTIC_ROLE",
            provenance={"runtime_authorized": True},
        )


@pytest.mark.parametrize(
    "flag",
    ["automatic_reuse_authorized", "semantic_rebind_authorized"],
)
def test_ts17_reuse_or_rebind_claim_in_event_provenance_blocks(flag: str) -> None:
    event = build_service_1_owner_confirmation_event_v1(
        case_id="case_1",
        file_ref="sha256:workbook-safe-ref",
        region_ref="region_1",
        sheet_ref="Ventas",
        column_ref="importe",
        question_ref="q_importe",
        owner_answer="OWNER_CONFIRMED",
        proposed_role="sales_amount",
        proposed_variable="sales_total",
        confirmed_role="sales_amount",
        confirmation_scope="SEMANTIC_ROLE",
        timestamp="2026-08-07T12:00:00+00:00",
        provenance={flag: True},
    )

    with pytest.raises(Service1TenantSemanticContractErrorV1) as exc:
        _build(owner_confirmation_event=event)
    _assert_code(exc, "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT")


def test_ts18_serialized_contract_has_closed_safety_line_and_safe_provenance() -> None:
    payload = _build().to_dict()

    for flag in (
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
        "automatic_reuse_authorized",
        "semantic_rebind_authorized",
    ):
        assert payload[flag] is False
    assert payload["provenance"] == {
        "owner_confirmation_schema": "SERVICE_1_OWNER_CONFIRMATION_EVENT_V1",
        "projection": "OWNER_CONFIRMATION_EVIDENCE_ONLY",
    }
    forbidden_fragments = ("raw_rows", "workbook_bytes", "credentials", "token")
    assert not any(key in payload["provenance"] for key in forbidden_fragments)


def test_cliente_id_is_only_present_when_explicitly_supplied() -> None:
    explicit = _build(cliente_id="cliente_42").to_dict()
    absent = _build(cliente_id=None).to_dict()

    assert explicit["cliente_id"] == "cliente_42"
    assert absent["cliente_id"] is None
    assert absent["cliente_id"] != absent["tenant_id"]


def test_mapping_series_is_deterministic_but_contract_tracks_confirmation_event() -> None:
    first = _build()
    same = _build()
    later_event = replace(_event(), timestamp="2026-08-07T13:00:00+00:00")
    later = _build(owner_confirmation_event=later_event)

    assert first.mapping_series_id == same.mapping_series_id == later.mapping_series_id
    assert first.contract_id == same.contract_id
    assert first.contract_id != later.contract_id
