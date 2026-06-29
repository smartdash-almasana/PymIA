from __future__ import annotations

from pymia.smartpyme.service_1_human_review_signoff_flow_v1 import (
    DECISION_APPROVED_FOR_DELIVERY,
    DECISION_BLOCKED,
    DECISION_NEEDS_CORRECTION,
    STATUS_BLOCKED,
    STATUS_NEEDS_CORRECTION,
    STATUS_REJECTED,
    STATUS_SIGNED_OFF_FOR_DELIVERY,
    apply_service_1_human_review_signoff_v1,
)


def _gate() -> dict:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "gate_type": "SERVICE_1_HUMAN_REVIEW_GATE",
        "status": "PENDING_HUMAN_REVIEW",
        "human_review_required": True,
        "reviewer_role": "operator_or_accountant",
        "decision_required_before_client_use": True,
        "runtime_authorized": False,
        "allowed_decisions": ["APPROVED_FOR_DELIVERY", "NEEDS_CORRECTION", "BLOCKED"],
        "blocked_claims": [
            "auditoria",
            "certificacion",
            "conciliacion_definitiva",
            "diagnostico_integral",
            "rentabilidad_real_confirmada",
            "reemplazo_contador",
        ],
    }


def test_approved_signoff_allows_human_supervised_delivery_only() -> None:
    result = apply_service_1_human_review_signoff_v1(
        human_review_gate=_gate(),
        decision=DECISION_APPROVED_FOR_DELIVERY,
        reviewer_id="operator_1",
        case_id="case_1",
        delivery_status_before="READY_FOR_HUMAN_REVIEW",
        reviewer_notes="Revisado para entrega controlada.",
    )

    assert result.status == STATUS_SIGNED_OFF_FOR_DELIVERY
    assert result.delivery_status_after == "APPROVED_FOR_HUMAN_SUPERVISED_DELIVERY"
    assert result.delivery_allowed_after_signoff is True
    assert result.runtime_authorized is False
    assert result.autonomous_use_authorized is False
    assert result.human_review_required is True


def test_needs_correction_signoff_blocks_delivery_until_fix() -> None:
    result = apply_service_1_human_review_signoff_v1(
        human_review_gate=_gate(),
        decision=DECISION_NEEDS_CORRECTION,
        reviewer_id="operator_1",
        reviewer_notes="Corregir faltante de costo_unitario.",
    )

    assert result.status == STATUS_NEEDS_CORRECTION
    assert result.delivery_status_after == "NEEDS_OPERATOR_CORRECTION"
    assert result.correction_required is True
    assert result.delivery_allowed_after_signoff is False
    assert result.runtime_authorized is False


def test_blocked_signoff_blocks_delivery() -> None:
    result = apply_service_1_human_review_signoff_v1(
        human_review_gate=_gate(),
        decision=DECISION_BLOCKED,
        reviewer_id="accountant_1",
        reviewer_notes="No entregar por datos inconsistentes.",
    )

    assert result.status == STATUS_BLOCKED
    assert result.delivery_status_after == "BLOCKED_BY_HUMAN_REVIEW"
    assert result.delivery_allowed_after_signoff is False
    assert result.runtime_authorized is False


def test_rejects_invalid_decision() -> None:
    result = apply_service_1_human_review_signoff_v1(
        human_review_gate=_gate(),
        decision="AUTO_APPROVE",
        reviewer_id="operator_1",
    )

    assert result.status == STATUS_REJECTED
    assert result.blocked_reason == "DECISION_NOT_ALLOWED"
    assert result.delivery_allowed_after_signoff is False
    assert result.runtime_authorized is False


def test_rejects_reviewer_notes_with_forbidden_claim() -> None:
    result = apply_service_1_human_review_signoff_v1(
        human_review_gate=_gate(),
        decision=DECISION_APPROVED_FOR_DELIVERY,
        reviewer_id="operator_1",
        reviewer_notes="Aprobado como auditoria contable.",
    )

    assert result.status == STATUS_REJECTED
    assert result.blocked_reason == "FORBIDDEN_CLAIM"
    assert result.delivery_allowed_after_signoff is False
    assert result.runtime_authorized is False
