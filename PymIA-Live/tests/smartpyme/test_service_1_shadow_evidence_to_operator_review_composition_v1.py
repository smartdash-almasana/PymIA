from __future__ import annotations

from pymia.smartpyme.service_1_explicit_request_to_pipeline_request_gate_v1 import (
    build_service_1_explicit_request_to_pipeline_request_gate_v1,
)
from pymia.smartpyme.service_1_pipeline_request_execution_gate_v1 import (
    build_service_1_pipeline_request_execution_gate_v1,
)
from pymia.smartpyme.service_1_runner_shadow_evidence_v1 import build_service_1_runner_shadow_evidence_v1
from pymia.smartpyme.service_1_runner_shadow_harness_v1 import build_service_1_runner_shadow_harness_v1
from pymia.smartpyme.service_1_saas_job_to_pipeline_request_adapter_v1 import (
    build_service_1_saas_job_to_pipeline_request_adapter_v1,
)
from pymia.smartpyme.service_1_shadow_evidence_operator_review_packet_v1 import (
    build_service_1_shadow_evidence_operator_review_packet_v1,
)

_ALLOWED_TOOLS = [
    "precio_margen_basico",
    "caja_diaria_triage",
    "stock_alertas_basicas",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
]


def _saas_job() -> dict[str, object]:
    return {
        "job_kind": "SAAS_JOB_ORCHESTRATION_CANDIDATE",
        "requested_job_kind": "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "source_file_intake_ref": "evidence_candidate:owner:pyme:001:case:s1:001:upload_ref:file:ventas_marzo",
        "autonomous_chain_candidate_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "autonomous_rerun_candidate_ref": "rerun_candidate:s1:001",
        },
        "planned_job_steps": [
            "validate_session_candidate_refs",
            "validate_file_intake_candidate_refs",
            "prepare_file_processing_job_candidate",
        ],
        "worker_authorized": False,
        "queue_authorized": False,
        "async_execution_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _explicit_candidate() -> dict[str, object]:
    return {
        "tool_ref": "precio_margen_basico",
        "input_refs": {
            "precio_venta": "sheet:Ventas.column:Precio",
            "costo_unitario": "sheet:Costos.column:CostoUnitario",
        },
        "source_plan_ref": "tool_plan_candidate:precio_margen_basico",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "request_kind": "CANDIDATE_ONLY",
        "executable": False,
    }


def _adapter_payload() -> dict[str, object]:
    return {
        "saas_job_orchestration_status": "SAAS_JOB_ORCHESTRATION_CANDIDATE_READY",
        "saas_job_orchestration_candidate": _saas_job(),
        "explicit_request_status": "EXPLICIT_REQUEST_CANDIDATE_READY",
        "explicit_tool_request_candidate": [_explicit_candidate()],
        "allowed_tool_refs": list(_ALLOWED_TOOLS),
        "case_truth_status": "READY_FOR_TOOL_PLANNING",
        "missing_inputs": [],
        "unsafe_flags": [],
        "notes": [],
    }


def _execution_gate_input_from(
    *,
    explicit_gate_result: dict[str, object],
    case_truth_status: str | None = "READY_FOR_TOOL_PLANNING",
) -> dict[str, object]:
    return {
        "pipeline_candidate_status": explicit_gate_result["status"],
        "pipeline_tool_requests": explicit_gate_result["pipeline_tool_request_candidate"],
        "allowed_tool_refs": list(_ALLOWED_TOOLS),
        "missing_inputs": [],
        "unsafe_flags": [],
        "case_truth_status": case_truth_status,
        "notes": [],
    }


def _build_evidence_from_full_chain(case_truth_status: str | None = "READY_FOR_TOOL_PLANNING") -> tuple[dict[str, object], dict[str, object]]:
    adapter_result = build_service_1_saas_job_to_pipeline_request_adapter_v1(_adapter_payload())  # type: ignore[arg-type]
    explicit_gate_result = build_service_1_explicit_request_to_pipeline_request_gate_v1(
        adapter_result["explicit_to_pipeline_gate_input"]  # type: ignore[arg-type]
    )
    execution_gate_result = build_service_1_pipeline_request_execution_gate_v1(
        _execution_gate_input_from(explicit_gate_result=explicit_gate_result, case_truth_status=case_truth_status)  # type: ignore[arg-type]
    )
    shadow_result = build_service_1_runner_shadow_harness_v1(  # type: ignore[arg-type]
        {
            "execution_gate_status": execution_gate_result["status"],
            "execution_authorized": execution_gate_result["execution_authorized"],
            "pipeline_authorized": execution_gate_result["pipeline_authorized"],
            "safe_to_call_pipeline": execution_gate_result["safe_to_call_pipeline"],
            "authorized_pipeline_tool_requests": execution_gate_result["authorized_pipeline_tool_requests"],
            "case_id": "case:s1:001",
            "run_id": "run:s1:001",
            "notes": [],
            "runtime_authorized": execution_gate_result["runtime_authorized"],
            "owner_delivery_authorized": False,
            "autonomous_delivery_authorized": execution_gate_result["autonomous_delivery_authorized"],
        }
    )
    evidence_result = build_service_1_runner_shadow_evidence_v1(  # type: ignore[arg-type]
        {
            "shadow_result": shadow_result,
            "evidence_ref": "shadow_evidence:case:s1:001:run:s1:001",
            "observed_at": "2026-07-05T12:00:00-03:00",
            "notes": [],
        }
    )
    return execution_gate_result, evidence_result


def test_shadow_evidence_flows_to_operator_review_packet_without_owner_publication() -> None:
    execution_gate_result, evidence_result = _build_evidence_from_full_chain()

    review_packet = build_service_1_shadow_evidence_operator_review_packet_v1(  # type: ignore[arg-type]
        {
            "shadow_evidence": evidence_result,
            "operator_ref": "operator:service_1:001",
            "review_packet_ref": "operator_review_packet:case:s1:001:run:s1:001",
            "notes": [],
            "owner_publication_requested": False,
        }
    )

    assert execution_gate_result["status"] == "EXECUTION_AUTHORIZED"
    assert evidence_result["status"] == "SHADOW_EVIDENCE_READY"
    assert review_packet["status"] == "OPERATOR_REVIEW_PACKET_READY"
    assert review_packet["review_required"] is True
    assert review_packet["owner_publication_authorized"] is False
    assert review_packet["owner_delivery_authorized"] is False
    assert review_packet["autonomous_delivery_authorized"] is False
    assert review_packet["runtime_authorized"] is False
    assert review_packet["pipeline_called"] is False
    assert review_packet["processed_tool_refs"] == ["precio_margen_basico"]
    assert review_packet["operator_summary"]["operator_decision_required"] == "APPROVE_FOR_INTERNAL_NEXT_STEP_OR_REJECT"  # type: ignore[index]


def test_operator_review_packet_blocks_when_shadow_chain_was_blocked_upstream() -> None:
    execution_gate_result, evidence_result = _build_evidence_from_full_chain(case_truth_status="NEEDS_OWNER_CONFIRMATION")

    review_packet = build_service_1_shadow_evidence_operator_review_packet_v1(  # type: ignore[arg-type]
        {
            "shadow_evidence": evidence_result,
            "operator_ref": "operator:service_1:001",
            "review_packet_ref": "operator_review_packet:case:s1:001:run:s1:blocked",
            "notes": [],
            "owner_publication_requested": False,
        }
    )

    assert execution_gate_result["status"] == "BLOCKED_CANDIDATE_NOT_READY"
    assert evidence_result["status"] == "BLOCKED_SHADOW_NOT_READY"
    assert review_packet["status"] == "BLOCKED_SHADOW_EVIDENCE_NOT_READY"
    assert review_packet["owner_publication_authorized"] is False
    assert review_packet["operator_summary"] is None


def test_operator_review_packet_blocks_owner_publication_even_after_ready_shadow_evidence() -> None:
    _, evidence_result = _build_evidence_from_full_chain()

    review_packet = build_service_1_shadow_evidence_operator_review_packet_v1(  # type: ignore[arg-type]
        {
            "shadow_evidence": evidence_result,
            "operator_ref": "operator:service_1:001",
            "review_packet_ref": "operator_review_packet:case:s1:001:run:s1:001",
            "notes": [],
            "owner_publication_requested": True,
        }
    )

    assert evidence_result["status"] == "SHADOW_EVIDENCE_READY"
    assert review_packet["status"] == "BLOCKED_OWNER_PUBLICATION_ATTEMPT"
    assert review_packet["owner_publication_authorized"] is False
    assert review_packet["owner_delivery_authorized"] is False
