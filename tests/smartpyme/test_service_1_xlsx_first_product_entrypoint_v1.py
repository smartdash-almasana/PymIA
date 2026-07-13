from __future__ import annotations

from pymia.smartpyme.service_1_xlsx_first_product_entrypoint_v1 import (
    BLOCK_DRY_RUN_NOT_BUILT,
    STATUS_BLOCKED,
    STATUS_DELIVERY_PACKAGE_CANDIDATE_READY,
    STATUS_NEXT_OWNER_QUESTION,
    build_service_1_xlsx_first_product_entrypoint_v1,
)


def _base_kwargs():
    return {
        "case_id": "case:s1:xlsx:first:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
    }


def test_builds_xlsx_first_package_candidate_for_margin_case() -> None:
    result = build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_kwargs(),
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

    assert result.status == STATUS_DELIVERY_PACKAGE_CANDIDATE_READY
    assert result.selected_primary_pathology == "REN_001"
    assert result.allowed_computation_ref == "first_aid_precio_margen_basico_v1"
    assert result.next_owner_question is None
    assert result.delivery_package_candidate is not None
    assert result.delivery_package_candidate.status == "DELIVERY_PACKAGE_CANDIDATE_BUILT"
    assert result.delivery_package_candidate.computed_values["unit_margin"] == 40.0
    assert result.delivery_package_candidate.computed_values["total_margin"] == 400.0
    assert result.delivery_authorized is False


def test_returns_next_owner_question_when_triage_needs_more_evidence() -> None:
    result = build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_kwargs(),
        raw_owner_narrative="No veo el margen porque tengo precio y costo pero no sé si gano.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo"],
        input_values={"precio": 100, "costo": 60},
    )

    assert result.status == STATUS_NEXT_OWNER_QUESTION
    assert result.selected_primary_pathology == "REN_001"
    assert result.next_owner_question is not None
    assert result.owner_confirmation_required is True
    assert result.delivery_package_candidate is None
    assert result.delivery_authorized is False


def test_blocks_empty_owner_narrative() -> None:
    result = build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_kwargs(),
        raw_owner_narrative="   ",
        business_period_reference="2026-06",
        available_data_fields=["precio", "costo", "cantidad"],
        input_values={"precio": 100, "costo": 60, "cantidad": 10},
    )

    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == "EMPTY_OWNER_NARRATIVE"
    assert result.delivery_package_candidate is None
    assert result.delivery_authorized is False


def test_blocks_when_dry_run_inputs_are_missing() -> None:
    result = build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_kwargs(),
        raw_owner_narrative="No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=[
            "precio=precio de venta",
            "costo=costo unitario",
            "cantidad=volumen vendido",
        ],
        available_data_fields=["precio", "costo", "cantidad"],
        input_values={"precio": 100, "costo": 60},
    )

    assert result.status == STATUS_BLOCKED
    assert result.blocked_reason == BLOCK_DRY_RUN_NOT_BUILT
    assert result.trace["dry_run_status"] == "BLOCKED_MISSING_INPUT_VALUES"
    assert result.delivery_package_candidate is None
    assert result.delivery_authorized is False


def test_entrypoint_trace_records_closed_chain_statuses() -> None:
    result = build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_kwargs(),
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

    assert result.trace == {
        "triage_entrypoint_status": "NO_OWNER_QUESTIONS_REQUIRED",
        "allowed_computation_candidate_status": "READY_FOR_COMPUTATION_PLAN",
        "evidence_readiness_gate_status": "READY_FOR_COMPUTATION_PLAN",
        "computation_plan_status": "READY_FOR_DRY_RUN_CANDIDATE",
        "dry_run_status": "DRY_RUN_CANDIDATE_BUILT",
        "owner_view_status": "OWNER_VIEW_BUILT",
        "policy_guard_status": "POLICY_PASS",
        "package_candidate_status": "DELIVERY_PACKAGE_CANDIDATE_BUILT",
    }


def test_entrypoint_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    result = build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_kwargs(),
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

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
    assert result.delivery_package_candidate is not None
    assert result.delivery_package_candidate.delivery_authorized is False


def test_entrypoint_to_dict_does_not_expose_human_review_fields() -> None:
    result = build_service_1_xlsx_first_product_entrypoint_v1(
        **_base_kwargs(),
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
    data = result.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
    assert "human_review_required" not in data["delivery_package_candidate"]
    assert "human_review_gate" not in data["delivery_package_candidate"]
