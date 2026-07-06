from __future__ import annotations

from pymia.smartpyme.service_1_owner_answer_reentry_v1 import bind_owner_answer_for_service_1_reentry_v1
from pymia.smartpyme.service_1_pathology_anamnesis_triage_loop_composition_v1 import (
    COMPOSITION_BLOCK_BRIDGE_BLOCKED,
    COMPOSITION_STATUS_BLOCKED,
    COMPOSITION_STATUS_BUILT,
    COMPOSITION_STATUS_NO_OWNER_QUESTIONS_REQUIRED,
    build_service_1_pathology_anamnesis_triage_loop_composition_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import build_service_1_question_bundle_v1


def _question_bundle(case_id: str = "case:s1:loop:001"):
    return build_service_1_question_bundle_v1(
        case_id=case_id,
        tenant_id="tenant:pyme:001",
        intake_id="intake:s1:001",
        run_id="run:s1:001",
        report={
            "next_questions": [
                {
                    "question": "¿Qué problema operativo querés entender primero?",
                    "target_ref": "owner:pain",
                }
            ]
        },
    )


def _owner_reentry(bundle, *, answer: str):
    assert bundle.selected_next_question_ref is not None
    return bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=bundle,
        question_ref=bundle.selected_next_question_ref,
        raw_owner_answer=answer,
        anamnesis_id="anamnesis:s1:001",
        investigation_id="investigation:s1:001",
    )


def test_loop_composes_direct_owner_narrative_to_question_bundle_output() -> None:
    composition = build_service_1_pathology_anamnesis_triage_loop_composition_v1(
        question_bundle=_question_bundle(),
        owner_ref="owner:pyme:001",
        raw_owner_narrative="No veo el margen porque tengo precio y costo pero no sé si gano.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo"],
    )

    assert composition.status == COMPOSITION_STATUS_BUILT
    assert composition.selected_primary_pathology == "REN_001"
    assert composition.bridge_result.triage_decision is not None
    assert composition.question_bundle_output.question_bundle is not None
    assert composition.question_bundle_output.question_bundle.questions
    assert composition.runtime_authorized is False


def test_loop_composes_owner_answer_reentry_to_question_bundle_output() -> None:
    bundle = _question_bundle()
    reentry = _owner_reentry(
        bundle,
        answer="Tengo ventas pero los cobros no entran en caja.",
    )

    composition = build_service_1_pathology_anamnesis_triage_loop_composition_v1(
        question_bundle=bundle,
        owner_ref="owner:pyme:001",
        owner_answer_reentry=reentry,
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros"],
    )

    assert composition.status == COMPOSITION_STATUS_BUILT
    assert composition.selected_primary_pathology == "LIQ_001"
    assert composition.bridge_result.source_question_ref == reentry.question_ref
    assert composition.question_bundle_output.question_bundle is not None
    assert composition.question_bundle_output.owner_confirmation_required is True


def test_loop_returns_no_owner_questions_required_when_ready_for_computation() -> None:
    composition = build_service_1_pathology_anamnesis_triage_loop_composition_v1(
        question_bundle=_question_bundle(),
        owner_ref="owner:pyme:001",
        raw_owner_narrative="No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo", "cantidad"],
    )

    assert composition.status == COMPOSITION_STATUS_NO_OWNER_QUESTIONS_REQUIRED
    assert composition.owner_confirmation_required is False
    assert composition.question_bundle_output.question_bundle is not None
    assert composition.question_bundle_output.question_bundle.questions == ()


def test_loop_blocks_when_bridge_blocks_empty_narrative() -> None:
    composition = build_service_1_pathology_anamnesis_triage_loop_composition_v1(
        question_bundle=_question_bundle(),
        owner_ref="owner:pyme:001",
    )

    assert composition.status == COMPOSITION_STATUS_BLOCKED
    assert composition.blocked_reason == COMPOSITION_BLOCK_BRIDGE_BLOCKED
    assert composition.bridge_result.status == "BLOCKED"
    assert composition.question_bundle_output.question_bundle is None


def test_loop_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    composition = build_service_1_pathology_anamnesis_triage_loop_composition_v1(
        question_bundle=_question_bundle(),
        owner_ref="owner:pyme:001",
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros"],
    )

    assert composition.runtime_authorized is False
    assert composition.reexecution_authorized is False
    assert composition.recalculation_authorized is False
    assert composition.delivery_authorized is False
    assert composition.bridge_result.runtime_authorized is False
    assert composition.question_bundle_output.runtime_authorized is False


def test_loop_primary_dict_does_not_expose_human_review_fields() -> None:
    composition = build_service_1_pathology_anamnesis_triage_loop_composition_v1(
        question_bundle=_question_bundle(),
        owner_ref="owner:pyme:001",
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros"],
    )
    data = composition.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
    assert "human_review_required" not in data["bridge_result"]
    assert "human_review_gate" not in data["bridge_result"]
    assert "human_review_required" not in data["question_bundle_output"]
    assert "human_review_gate" not in data["question_bundle_output"]
