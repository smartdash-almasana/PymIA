from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_real_client_xlsx_first_pilot_pack_v1 import (
    STATUS_PILOT_PACK_BLOCKED,
    STATUS_PILOT_PACK_NEEDS_OWNER_INPUT,
    STATUS_PILOT_PACK_READY,
    build_service_1_real_client_xlsx_first_pilot_pack_v1,
)
from pymia.smartpyme.service_1_xlsx_first_product_entrypoint_v1 import (
    build_service_1_xlsx_first_product_entrypoint_v1,
)


def _base_entrypoint_kwargs():
    return {
        "case_id": "case:s1:pilot:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
    }


def _complete_pilot_metadata():
    return {
        "xlsx_file_available": True,
        "owner_problem_narrative": True,
        "business_period_reference": True,
        "column_meaning_confirmations": True,
        "available_data_fields": True,
    }


def _ready_entrypoint():
    return build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_entrypoint_kwargs(),
        raw_owner_narrative="No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=[
            "precio=precio de venta",
            "costo=costo unitario",
            "cantidad=volumen vendido",
        ],
        available_data_fields=["precio", "costo", "cantidad"],
        input_values={"precio": 100, "costo": 60, "cantidad": 10},
    )


def test_builds_real_client_pilot_pack_ready_from_ready_entrypoint() -> None:
    entrypoint = _ready_entrypoint()
    result = build_service_1_real_client_xlsx_first_pilot_pack_v1(
        entrypoint_result=entrypoint,
        metadata=_complete_pilot_metadata(),
    )

    assert result.status == STATUS_PILOT_PACK_READY
    assert result.entrypoint_status == "DELIVERY_PACKAGE_CANDIDATE_READY"
    assert result.selected_primary_pathology == "REN_001"
    assert result.allowed_computation_ref == "first_aid_precio_margen_basico_v1"
    assert result.missing_intake_items == ()
    assert result.package_candidate_ref is not None
    assert result.pilot_output_summary is not None
    assert result.next_owner_question is None
    assert result.owner_confirmation_required is False
    assert result.delivery_authorized is False


def test_pilot_pack_needs_owner_input_when_entrypoint_has_next_question() -> None:
    entrypoint = build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_entrypoint_kwargs(),
        raw_owner_narrative="No veo el margen porque tengo precio y costo pero no sé si gano.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo"],
        input_values={"precio": 100, "costo": 60},
    )
    result = build_service_1_real_client_xlsx_first_pilot_pack_v1(
        entrypoint_result=entrypoint,
        metadata=_complete_pilot_metadata(),
    )

    assert result.status == STATUS_PILOT_PACK_NEEDS_OWNER_INPUT
    assert result.entrypoint_status == "NEXT_OWNER_QUESTION"
    assert result.next_owner_question is not None
    assert result.owner_confirmation_required is True
    assert result.package_candidate_ref is None
    assert "pregunta al dueño" in result.pilot_output_summary


def test_pilot_pack_blocks_when_entrypoint_is_blocked() -> None:
    entrypoint = build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_entrypoint_kwargs(),
        raw_owner_narrative=" ",
        business_period_reference="2026-06",
        available_data_fields=["precio", "costo", "cantidad"],
        input_values={"precio": 100, "costo": 60, "cantidad": 10},
    )
    result = build_service_1_real_client_xlsx_first_pilot_pack_v1(
        entrypoint_result=entrypoint,
        metadata=_complete_pilot_metadata(),
    )

    assert result.status == STATUS_PILOT_PACK_BLOCKED
    assert result.entrypoint_status == "BLOCKED"
    assert result.blocked_reason == "EMPTY_OWNER_NARRATIVE"
    assert result.package_candidate_ref is None
    assert result.delivery_authorized is False


def test_ready_entrypoint_still_needs_owner_input_when_pilot_intake_is_incomplete() -> None:
    result = build_service_1_real_client_xlsx_first_pilot_pack_v1(
        entrypoint_result=_ready_entrypoint(),
        metadata={
            "xlsx_file_available": True,
            "owner_problem_narrative": True,
            "business_period_reference": True,
            "column_meaning_confirmations": False,
            "available_data_fields": True,
        },
    )

    assert result.status == STATUS_PILOT_PACK_NEEDS_OWNER_INPUT
    assert result.missing_intake_items == ("column_meaning_confirmations",)
    assert result.blocked_reason == "missing_required_pilot_intake_items"
    assert result.owner_confirmation_required is True


def test_pilot_pack_contains_script_stop_rules_and_qa_checks() -> None:
    result = build_service_1_real_client_xlsx_first_pilot_pack_v1(
        entrypoint_result=_ready_entrypoint(),
        metadata=_complete_pilot_metadata(),
    )

    assert result.owner_script
    assert result.stop_rules
    assert result.qa_checks
    assert any("límites" in item or "limits" in item for item in result.qa_checks)


def test_pilot_pack_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    result = build_service_1_real_client_xlsx_first_pilot_pack_v1(
        entrypoint_result=_ready_entrypoint(),
        metadata=_complete_pilot_metadata(),
    )

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False


def test_pilot_pack_rejects_invalid_entrypoint_type() -> None:
    with pytest.raises(ValueError):
        build_service_1_real_client_xlsx_first_pilot_pack_v1(
            entrypoint_result=object(),  # type: ignore[arg-type]
            metadata=_complete_pilot_metadata(),
        )
