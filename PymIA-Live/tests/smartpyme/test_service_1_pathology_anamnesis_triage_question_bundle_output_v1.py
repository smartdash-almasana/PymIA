from __future__ import annotations

from pymia.smartpyme.service_1_pathology_anamnesis_triage_intake_bridge_v1 import (
    build_service_1_pathology_anamnesis_triage_intake_bridge_v1,
)
from pymia.smartpyme.service_1_pathology_anamnesis_triage_question_bundle_output_v1 import (
    OUTPUT_BLOCK_BRIDGE_NOT_BUILT,
    OUTPUT_STATUS_BLOCKED,
    OUTPUT_STATUS_BUILT,
    OUTPUT_STATUS_NO_OWNER_QUESTIONS_REQUIRED,
    SOURCE_PATHOLOGY_ANAMNESIS_TRIAGE,
    build_service_1_pathology_anamnesis_triage_question_bundle_output_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import build_service_1_question_bundle_v1


def _question_bundle():
    return build_service_1_question_bundle_v1(
        case_id="case:s1:qbo:001",
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


def _bridge_with_missing_evidence():
    return build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=_question_bundle(),
        owner_ref="owner:pyme:001",
        raw_owner_narrative="No veo el margen porque tengo precio y costo pero no sé si gano.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo"],
    )


def _bridge_ready_for_computation():
    return build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=_question_bundle(),
        owner_ref="owner:pyme:001",
        raw_owner_narrative="No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo", "cantidad"],
    )


def _blocked_bridge_empty_narrative():
    return build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=_question_bundle(),
        owner_ref="owner:pyme:001",
    )


def test_output_builds_question_bundle_from_triage_next_owner_questions() -> None:
    bridge = _bridge_with_missing_evidence()

    output = build_service_1_pathology_anamnesis_triage_question_bundle_output_v1(
        bridge=bridge,
    )

    assert output.status == OUTPUT_STATUS_BUILT
    assert output.question_bundle is not None
    assert output.question_bundle.questions
    assert output.question_bundle.owner_confirmation_required is True
    assert output.question_bundle.runtime_authorized is False
    assert output.question_bundle.selected_next_question_ref == output.question_bundle.questions[0].question_ref
    assert output.question_bundle.questions[0].source == SOURCE_PATHOLOGY_ANAMNESIS_TRIAGE


def test_output_uses_triage_metadata_and_pathology_target_refs() -> None:
    bridge = _bridge_with_missing_evidence()

    output = build_service_1_pathology_anamnesis_triage_question_bundle_output_v1(
        bridge=bridge,
        metadata={"caller": "test"},
    )

    assert output.question_bundle is not None
    question = output.question_bundle.questions[0]
    assert "pathology:REN_001:owner_question:" in question.target_ref
    assert question.metadata["origin"] == output.schema_version
    assert question.metadata["runtime_authorized"] is False
    assert question.metadata["delivery_authorized"] is False
    assert output.question_bundle.metadata["caller"] == "test"


def test_output_returns_no_owner_questions_required_when_triage_is_ready() -> None:
    bridge = _bridge_ready_for_computation()

    output = build_service_1_pathology_anamnesis_triage_question_bundle_output_v1(
        bridge=bridge,
    )

    assert output.status == OUTPUT_STATUS_NO_OWNER_QUESTIONS_REQUIRED
    assert output.question_bundle is not None
    assert output.question_bundle.questions == ()
    assert output.question_bundle.selected_next_question_ref is None
    assert output.owner_confirmation_required is False
    assert output.question_bundle.owner_confirmation_required is False


def test_output_blocks_when_bridge_is_not_built() -> None:
    bridge = _blocked_bridge_empty_narrative()

    output = build_service_1_pathology_anamnesis_triage_question_bundle_output_v1(
        bridge=bridge,
    )

    assert output.status == OUTPUT_STATUS_BLOCKED
    assert output.blocked_reason == OUTPUT_BLOCK_BRIDGE_NOT_BUILT
    assert output.question_bundle is None
    assert output.runtime_authorized is False


def test_output_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    bridge = _bridge_with_missing_evidence()

    output = build_service_1_pathology_anamnesis_triage_question_bundle_output_v1(
        bridge=bridge,
    )

    assert output.runtime_authorized is False
    assert output.reexecution_authorized is False
    assert output.recalculation_authorized is False
    assert output.delivery_authorized is False
    assert output.question_bundle is not None
    assert output.question_bundle.runtime_authorized is False


def test_output_primary_dict_does_not_expose_human_review_fields() -> None:
    bridge = _bridge_with_missing_evidence()

    output = build_service_1_pathology_anamnesis_triage_question_bundle_output_v1(
        bridge=bridge,
    )
    data = output.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
    assert data["question_bundle"] is not None
    assert "human_review_required" not in data["question_bundle"]
    assert "human_review_gate" not in data["question_bundle"]
