from __future__ import annotations

from pymia.smartpyme.owner_confirmed_semantic_request_flow import (
    OwnerConfirmedSemanticRequestFlowResult,
)
from pymia.smartpyme.owner_confirmed_semantic_request_projection import (
    project_confirmed_semantic_requests_to_owner_facing,
)
from pymia.smartpyme.owner_facing_report import OwnerFacingReport
from pymia.smartpyme.owner_semantic_evidence_request_builder import (
    build_owner_semantic_evidence_request,
)


def _base_owner_report() -> dict:
    return {
        "tenant_id": "tenant-1",
        "intake_id": "intake-1",
        "status": "BLOCKED",
        "delivery_status": "BLOCKED",
        "operational_status": "pending_data",
        "summary": "Falta evidencia estructural para avanzar.",
        "blocked_message": "Necesito evidencia adicional.",
        "evidence_used": ["sheet://ventas"],
        "missing_evidence": ["own_price"],
        "next_questions": ["¿Podés aportar evidencia de precios?"],
        "next_steps": [],
        "references": ["operational_audit_result://case-1"],
        "output_refs": ["owner_facing_report.json"],
        "limit_warnings": ["No inventar evidencia."],
        "findings": [{"finding_id": "finding-original"}],
    }


def _semantic_request():
    return build_owner_semantic_evidence_request(
        missing_key="own_price",
        owner_answer_text="Sí, la tela subió y fui cambiando precios.",
        source_ref="owner_answer://case-1/answer-1",
    )


def _blocked_actionable_flow(
    *,
    requests=None,
    unsupported_missing_keys: tuple[str, ...] = (),
) -> OwnerConfirmedSemanticRequestFlowResult:
    if requests is None:
        requests = (_semantic_request(),)
    return OwnerConfirmedSemanticRequestFlowResult(
        flow_status="BLOCKED_ACTIONABLE",
        semantic_evidence_requests=tuple(requests),
        reason="blocked actionable",
        unsupported_missing_keys=unsupported_missing_keys,
        metadata={"does_resolve_structural_input": False, "produces_findings": False},
    )


def test_blocked_actionable_adds_refined_request_text_to_next_questions() -> None:
    request = _semantic_request()

    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=_base_owner_report(),
        flow_result=_blocked_actionable_flow(requests=(request,)),
    )

    assert request.refined_request_text in projected["next_questions"]


def test_blocked_actionable_adds_step_and_warning() -> None:
    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=_base_owner_report(),
        flow_result=_blocked_actionable_flow(),
    )

    assert any(
        "eje semántico confirmado" in step and "evidencia concreta" in step
        for step in projected["next_steps"]
    )
    assert any(
        "no reemplaza evidencia estructural" in warning
        for warning in projected["limit_warnings"]
    )


def test_projection_does_not_alter_sovereign_report_fields() -> None:
    original = _base_owner_report()

    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=original,
        flow_result=_blocked_actionable_flow(),
    )

    for key in (
        "status",
        "delivery_status",
        "operational_status",
        "evidence_used",
        "missing_evidence",
    ):
        assert projected[key] == original[key]


def test_projection_deduplicates_existing_refined_request_text() -> None:
    request = _semantic_request()
    report = _base_owner_report()
    report["next_questions"] = [
        "¿Podés aportar evidencia de precios?",
        request.refined_request_text,
    ]

    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=report,
        flow_result=_blocked_actionable_flow(requests=(request,)),
    )

    assert projected["next_questions"].count(request.refined_request_text) == 1


def test_pending_owner_confirmation_only_adds_confirmation_step() -> None:
    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=_base_owner_report(),
        flow_result=OwnerConfirmedSemanticRequestFlowResult(
            flow_status="PENDING_OWNER_CONFIRMATION",
            semantic_evidence_requests=(),
            reason="pending confirmation",
        ),
    )

    assert all("precios de venta por producto/SKU" not in q for q in projected["next_questions"])
    assert any("confirmar o corregir" in step for step in projected["next_steps"])
    assert (
        projected["semantic_request_projection"]["flow_status"]
        == "PENDING_OWNER_CONFIRMATION"
    )


def test_needs_reinterpretation_only_adds_reinterpretation_step() -> None:
    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=_base_owner_report(),
        flow_result=OwnerConfirmedSemanticRequestFlowResult(
            flow_status="NEEDS_REINTERPRETATION",
            semantic_evidence_requests=(),
            reason="needs reinterpretation",
        ),
    )

    assert all("precios de venta por producto/SKU" not in q for q in projected["next_questions"])
    assert any("reformular la interpretación" in step for step in projected["next_steps"])
    assert (
        projected["semantic_request_projection"]["flow_status"]
        == "NEEDS_REINTERPRETATION"
    )


def test_accepts_owner_facing_report_dataclass_and_returns_dict() -> None:
    report_payload = dict(_base_owner_report())
    report_payload.pop("findings")
    report = OwnerFacingReport(**report_payload)

    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=report,
        flow_result=_blocked_actionable_flow(),
    )

    assert isinstance(projected, dict)
    assert projected["tenant_id"] == "tenant-1"
    assert projected["semantic_request_projection"]["flow_status"] == "BLOCKED_ACTIONABLE"


def test_semantic_request_projection_metadata_is_fail_closed_and_traceable() -> None:
    projected = project_confirmed_semantic_requests_to_owner_facing(
        owner_facing_report=_base_owner_report(),
        flow_result=_blocked_actionable_flow(
            requests=(_semantic_request(),),
            unsupported_missing_keys=("unsupported_key",),
        ),
    )

    projection = projected["semantic_request_projection"]

    assert projection["requests_count"] == 1
    assert projection["unsupported_missing_keys"] == ["unsupported_key"]
    assert projection["does_resolve_structural_input"] is False
    assert projection["produces_findings"] is False
