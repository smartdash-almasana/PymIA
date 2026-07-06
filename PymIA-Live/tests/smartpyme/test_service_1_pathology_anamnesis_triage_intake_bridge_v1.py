from __future__ import annotations

from pymia.smartpyme.service_1_owner_answer_reentry_v1 import bind_owner_answer_for_service_1_reentry_v1
from pymia.smartpyme.service_1_pathology_anamnesis_triage_contract_v1 import (
    PATHOLOGY_LIQ_001,
    PATHOLOGY_REN_001,
    STATUS_EVIDENCE_REQUIRED,
    STATUS_READY_FOR_DETERMINISTIC_COMPUTATION,
)
from pymia.smartpyme.service_1_pathology_anamnesis_triage_intake_bridge_v1 import (
    BRIDGE_BLOCK_CASE_MISMATCH,
    BRIDGE_BLOCK_EMPTY_OWNER_NARRATIVE,
    BRIDGE_STATUS_BLOCKED,
    BRIDGE_STATUS_BUILT,
    build_service_1_pathology_anamnesis_triage_intake_bridge_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    ANSWER_TYPE_FREE_TEXT,
    SOURCE_NEXT_QUESTIONS,
    build_service_1_question_bundle_v1,
    create_service_1_question_v1,
)


def _question_bundle():
    return build_service_1_question_bundle_v1(
        case_id="case:s1:bridge:001",
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


def _owner_reentry(bundle, *, answer: str, case_id_override: str | None = None):
    question_ref = bundle.selected_next_question_ref
    assert question_ref is not None
    reentry = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=bundle,
        question_ref=question_ref,
        raw_owner_answer=answer,
        anamnesis_id="anamnesis:s1:001",
        investigation_id="investigation:s1:001",
    )
    if case_id_override is None:
        return reentry
    return type(reentry)(
        schema_version=reentry.schema_version,
        service_name=reentry.service_name,
        status=reentry.status,
        case_id=case_id_override,
        tenant_id=reentry.tenant_id,
        intake_id=reentry.intake_id,
        source_run_id=reentry.source_run_id,
        question_ref=reentry.question_ref,
        owner_answer_record=reentry.owner_answer_record,
        selected_question=reentry.selected_question,
        blocked_reason=reentry.blocked_reason,
        runtime_authorized=reentry.runtime_authorized,
        owner_confirmation_required=reentry.owner_confirmation_required,
        reexecution_authorized=reentry.reexecution_authorized,
        recalculation_authorized=reentry.recalculation_authorized,
        created_at=reentry.created_at,
        metadata=reentry.metadata,
    )


def test_bridge_builds_triage_from_direct_owner_narrative() -> None:
    bundle = _question_bundle()

    bridge = build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=bundle,
        owner_ref="owner:pyme:001",
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros", "saldo"],
    )

    assert bridge.status == BRIDGE_STATUS_BUILT
    assert bridge.anamnesis_record is not None
    assert bridge.triage_decision is not None
    assert bridge.anamnesis_record.candidate_pathology_codes[0] == PATHOLOGY_LIQ_001
    assert bridge.triage_decision.selected_primary_pathology == PATHOLOGY_LIQ_001
    assert bridge.triage_decision.status == STATUS_READY_FOR_DETERMINISTIC_COMPUTATION


def test_bridge_uses_owner_answer_reentry_as_narrative_source() -> None:
    bundle = _question_bundle()
    reentry = _owner_reentry(
        bundle,
        answer="No veo el margen porque tengo precio y costo pero no sé si gano.",
    )

    bridge = build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=bundle,
        owner_ref="owner:pyme:001",
        owner_answer_reentry=reentry,
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo"],
    )

    assert bridge.status == BRIDGE_STATUS_BUILT
    assert bridge.source_question_ref == reentry.question_ref
    assert bridge.anamnesis_record is not None
    assert bridge.anamnesis_record.candidate_pathology_codes[0] == PATHOLOGY_REN_001
    assert bridge.triage_decision is not None
    assert bridge.triage_decision.status == STATUS_EVIDENCE_REQUIRED


def test_bridge_blocks_cross_case_reentry() -> None:
    bundle = _question_bundle()
    reentry = _owner_reentry(
        bundle,
        answer="Tengo ventas y cobros pero la caja no cierra.",
        case_id_override="case:s1:other",
    )

    bridge = build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=bundle,
        owner_ref="owner:pyme:001",
        owner_answer_reentry=reentry,
    )

    assert bridge.status == BRIDGE_STATUS_BLOCKED
    assert bridge.blocked_reason == BRIDGE_BLOCK_CASE_MISMATCH
    assert bridge.runtime_authorized is False


def test_bridge_blocks_empty_owner_narrative() -> None:
    bundle = _question_bundle()

    bridge = build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=bundle,
        owner_ref="owner:pyme:001",
    )

    assert bridge.status == BRIDGE_STATUS_BLOCKED
    assert bridge.blocked_reason == BRIDGE_BLOCK_EMPTY_OWNER_NARRATIVE
    assert bridge.anamnesis_record is None
    assert bridge.triage_decision is None


def test_bridge_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    bundle = _question_bundle()

    bridge = build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=bundle,
        owner_ref="owner:pyme:001",
        raw_owner_narrative="Tengo ventas y cobros pero la caja no cierra.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros", "saldo"],
    )

    assert bridge.runtime_authorized is False
    assert bridge.reexecution_authorized is False
    assert bridge.recalculation_authorized is False
    assert bridge.delivery_authorized is False
    assert bridge.anamnesis_record is not None
    assert bridge.anamnesis_record.runtime_authorized is False
    assert bridge.triage_decision is not None
    assert bridge.triage_decision.runtime_authorized is False
    assert all(candidate.runtime_authorized is False for candidate in bridge.pathology_candidates)


def test_bridge_primary_dict_does_not_expose_human_review_fields() -> None:
    bundle = _question_bundle()
    question = create_service_1_question_v1(
        source=SOURCE_NEXT_QUESTIONS,
        text="¿Qué problema operativo querés entender primero?",
        target_ref="owner:pain",
        answer_type=ANSWER_TYPE_FREE_TEXT,
    )
    assert "human_review_required" not in question.to_dict()

    bridge = build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=bundle,
        owner_ref="owner:pyme:001",
        raw_owner_narrative="Tengo ventas y cobros pero la caja no cierra.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros", "saldo"],
    )
    data = bridge.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
    assert "human_review_required" not in data["anamnesis_record"]
    assert "human_review_gate" not in data["anamnesis_record"]
