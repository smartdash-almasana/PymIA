from __future__ import annotations

from pymia.smartpyme.service_1_pathology_anamnesis_triage_entrypoint_candidate_v1 import (
    ENTRYPOINT_BLOCK_EMPTY_OWNER_NARRATIVE,
    ENTRYPOINT_STATUS_BLOCKED,
    ENTRYPOINT_STATUS_BUILT,
    ENTRYPOINT_STATUS_NO_OWNER_QUESTIONS_REQUIRED,
    build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1,
)


def _base_kwargs():
    return {
        "case_id": "case:s1:entrypoint:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
    }


def test_entrypoint_builds_margin_candidate_and_next_question() -> None:
    result = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_base_kwargs(),
        raw_owner_narrative="No veo el margen porque tengo precio y costo pero no sé si gano.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo"],
    )

    assert result.status == ENTRYPOINT_STATUS_BUILT
    assert result.selected_primary_pathology == "REN_001"
    assert result.next_question_text is not None
    assert "margen" in result.next_question_text.lower() or "rentabilidad" in result.next_question_text.lower()
    assert result.missing_evidence_items == ("volumen_vendido",)
    assert result.owner_confirmation_required is True


def test_entrypoint_builds_liquidity_candidate_from_owner_narrative() -> None:
    result = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_base_kwargs(),
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros"],
    )

    assert result.status == ENTRYPOINT_STATUS_BUILT
    assert result.selected_primary_pathology == "LIQ_001"
    assert result.missing_evidence_items == ("saldo_pendiente",)
    assert result.loop_composition is not None
    assert result.loop_composition.bridge_result.anamnesis_record is not None


def test_entrypoint_blocks_empty_owner_narrative() -> None:
    result = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_base_kwargs(),
        raw_owner_narrative="   ",
    )

    assert result.status == ENTRYPOINT_STATUS_BLOCKED
    assert result.blocked_reason == ENTRYPOINT_BLOCK_EMPTY_OWNER_NARRATIVE
    assert result.initial_question_bundle is not None
    assert result.loop_composition is None
    assert result.owner_confirmation_required is True


def test_entrypoint_returns_no_owner_questions_required_when_ready_for_computation() -> None:
    result = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_base_kwargs(),
        raw_owner_narrative="No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo", "cantidad"],
    )

    assert result.status == ENTRYPOINT_STATUS_NO_OWNER_QUESTIONS_REQUIRED
    assert result.selected_primary_pathology == "REN_001"
    assert result.next_question_text is None
    assert result.missing_evidence_items == ()
    assert result.owner_confirmation_required is False


def test_entrypoint_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    result = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_base_kwargs(),
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros"],
    )

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
    assert result.initial_question_bundle is not None
    assert result.initial_question_bundle.runtime_authorized is False
    assert result.loop_composition is not None
    assert result.loop_composition.runtime_authorized is False


def test_entrypoint_primary_dict_does_not_expose_human_review_fields() -> None:
    result = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_base_kwargs(),
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros"],
    )
    data = result.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
    assert data["initial_question_bundle"] is not None
    assert "human_review_required" not in data["loop_composition"]
    assert "human_review_gate" not in data["loop_composition"]


def test_entrypoint_metadata_keeps_input_context_without_authorizing_runtime() -> None:
    result = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_base_kwargs(),
        raw_owner_narrative="No veo el margen porque tengo precio y costo pero no sé si gano.",
        declared_data_sources=["rentabilidad.xlsx"],
        available_data_fields=["precio", "costo"],
        metadata={"caller": "unit_test"},
    )

    assert result.metadata["caller"] == "unit_test"
    assert result.metadata["declared_data_sources"] == ("rentabilidad.xlsx",)
    assert result.metadata["available_data_fields"] == ("precio", "costo")
    assert result.runtime_authorized is False
