from __future__ import annotations

import copy

from pymia.smartpyme.service_1_autonomous_delivery_release_gate_v1 import (
    DELIVERY_POLICY_ALLOWED_STATUS,
    PIPELINE_COMPLETED_STATUS,
    build_service_1_autonomous_delivery_release_gate_v1,
)
from pymia.smartpyme.service_1_final_owner_release_decision_gate_v1 import (
    build_service_1_final_owner_release_decision_gate_v1,
)
from pymia.smartpyme.service_1_final_release_to_owner_handoff_contract_v1 import (
    HANDOFF_CHANNEL_KIND,
    build_service_1_final_release_to_owner_handoff_contract_v1,
)
from pymia.smartpyme.service_1_human_review_release_integration_gate_v1 import (
    build_service_1_human_review_release_integration_gate_v1,
)
from pymia.smartpyme.service_1_human_review_signoff_flow_v1 import (
    DECISION_APPROVED_FOR_DELIVERY,
    apply_service_1_human_review_signoff_v1,
)
from pymia.smartpyme.service_1_owner_delivery_packet_for_saas_v1 import (
    build_service_1_owner_delivery_packet_for_saas_v1,
)
from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
    evaluate_service_1_qa_delivery_gate_v1,
)
from pymia.smartpyme.service_1_real_auth_boundary_contract_v1 import (
    build_service_1_real_auth_boundary_contract_v1,
)
from pymia.smartpyme.service_1_real_endpoint_api_boundary_contract_v1 import (
    REQUEST_CASE_STATUS,
    build_service_1_real_endpoint_api_boundary_contract_v1,
)
from pymia.smartpyme.service_1_real_storage_upload_boundary_contract_v1 import (
    build_service_1_real_storage_upload_boundary_contract_v1,
)
from pymia.smartpyme.service_1_real_worker_runtime_boundary_contract_v1 import (
    OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE,
    build_service_1_real_worker_runtime_boundary_contract_v1,
)


TENANT_REF = "tenant:pyme:001"
OWNER_REF = "owner:pyme:001"
CASE_REF = "case:s1:001"
SESSION_REF = "session:s1:001"
PIPELINE_RUN_REF = "pipeline_run:phase_h:001"


def _pipeline_run_result() -> dict[str, object]:
    return {
        "pipeline_run_ref": PIPELINE_RUN_REF,
        "schema_version": "PIPELINE_RUN_RESULT_V1",
        "executed_tool_refs": ["tool:detect-structure", "tool:prepare-owner-packet"],
    }


def _session_candidate() -> dict[str, object]:
    return {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "service_name": "SERVICE_1",
        "tenant_ref": TENANT_REF,
        "owner_ref": OWNER_REF,
        "case_ref": CASE_REF,
        "session_ref": SESSION_REF,
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
    }


def _tenant_isolation_candidate() -> dict[str, object]:
    return {
        "guard_kind": "TENANT_ISOLATION_GUARD_CANDIDATE",
        "service_name": "SERVICE_1",
        "tenant_isolation_passed": True,
        "cross_tenant_access_detected": False,
        "cross_case_access_detected": False,
        "cross_session_access_detected": False,
        "owner_ref": OWNER_REF,
        "case_ref": CASE_REF,
        "source_session_ref": SESSION_REF,
        "checked_source_refs": {
            "tenant_ref_primary": TENANT_REF,
            "storage_tenant_ref": TENANT_REF,
            "worker_session_ref": SESSION_REF,
        },
        "correction_applied": False,
        "auth_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _cost_guard_candidate(*, operation_kind: str) -> dict[str, object]:
    return {
        "guard_kind": "COST_AND_RATE_LIMIT_GUARD_CANDIDATE",
        "service_name": "SERVICE_1",
        "tenant_ref": TENANT_REF,
        "owner_ref": OWNER_REF,
        "case_ref": CASE_REF,
        "source_session_ref": SESSION_REF,
        "requested_operation_kind": operation_kind,
        "cost_limit_passed": True,
        "rate_limit_passed": True,
        "budget_limit_passed": True,
        "cost_charge_authorized": False,
        "rate_limit_mutation_authorized": False,
        "billing_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "scheduler_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _file_intake_candidate() -> dict[str, object]:
    return {
        "intake_kind": "SAAS_FILE_INTAKE_CANDIDATE",
        "service_name": "SERVICE_1",
        "owner_ref": OWNER_REF,
        "case_ref": CASE_REF,
        "source_session_ref": SESSION_REF,
        "file_ref": "storage://tenant-001/case-001/phase_h_evidence.csv",
        "declared_filename": "phase_h_evidence.csv",
        "declared_file_kind": "CSV",
        "declared_mime_type": "text/csv",
        "declared_size_bytes": 128,
        "task_spec_candidate_allowed": False,
        "upload_authorized": False,
        "file_read_authorized": False,
        "parser_authorized": False,
        "job_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _handoff_channel_candidate() -> dict[str, object]:
    return {
        "channel_candidate_kind": HANDOFF_CHANNEL_KIND,
        "channel_kind": "OWNER_PORTAL_LINK",
        "channel_ref": "handoff_channel:portal:phase_h:001",
        "channel_ready": True,
        "tenant_ref": TENANT_REF,
        "owner_ref": OWNER_REF,
        "case_ref": CASE_REF,
        "handoff_authorized": False,
        "handoff_executed": False,
        "publish_executed": False,
        "notification_sent": False,
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
    }


def _qa_packet(owner_message: str) -> dict[str, object]:
    return {
        "service_name": "SERVICE_1",
        "runtime_authorized": False,
        "owner_message": owner_message,
        "asset": {"filename": "phase_h_evidence.xlsx"},
        "detected_structure": {"sheets": ["Sheet1"], "runtime_authorized": False},
        "column_confirmation_packet": {
            "columns": ["fecha", "importe"],
            "runtime_authorized": False,
        },
        "case_delivery_manifest": {
            "artifact_refs": ["artifact:owner-packet", "artifact:qa-summary"],
            "runtime_authorized": False,
        },
    }


def test_phase_h_release_chain_composition_e2e_pure() -> None:
    pipeline_run_result = _pipeline_run_result()
    session_candidate = _session_candidate()
    tenant_isolation_candidate = _tenant_isolation_candidate()
    endpoint_cost_guard_candidate = _cost_guard_candidate(operation_kind=REQUEST_CASE_STATUS)
    storage_cost_guard_candidate = _cost_guard_candidate(operation_kind="UPLOAD_STORAGE_REFERENCE")
    worker_cost_guard_candidate = _cost_guard_candidate(operation_kind=OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE)
    file_intake_candidate = _file_intake_candidate()
    handoff_channel_candidate = _handoff_channel_candidate()

    original_state = copy.deepcopy(
        {
            "pipeline_run_result": pipeline_run_result,
            "session_candidate": session_candidate,
            "tenant_isolation_candidate": tenant_isolation_candidate,
            "endpoint_cost_guard_candidate": endpoint_cost_guard_candidate,
            "storage_cost_guard_candidate": storage_cost_guard_candidate,
            "worker_cost_guard_candidate": worker_cost_guard_candidate,
            "file_intake_candidate": file_intake_candidate,
            "handoff_channel_candidate": handoff_channel_candidate,
        }
    )

    release_result = build_service_1_autonomous_delivery_release_gate_v1(
        {
            "pipeline_run_status": PIPELINE_COMPLETED_STATUS,
            "pipeline_run_result": pipeline_run_result,
            "expected_artifacts": ["artifact:owner-packet", "artifact:qa-summary"],
            "produced_artifacts": ["artifact:owner-packet", "artifact:qa-summary"],
            "pipeline_errors": [],
            "pipeline_warnings": ["warning:review-required"],
            "delivery_policy_status": DELIVERY_POLICY_ALLOWED_STATUS,
            "notes": [],
        }
    )
    assert release_result["status"] == "DELIVERY_RELEASE_CANDIDATE_READY"
    release_candidate = release_result["delivery_release_candidate"]
    assert release_candidate is not None

    owner_packet_result = build_service_1_owner_delivery_packet_for_saas_v1(
        {
            "release_candidate_status": release_result["status"],
            "delivery_release_candidate": release_candidate,
            "pipeline_run_result": pipeline_run_result,
            "notes": [],
        }
    )
    assert owner_packet_result["status"] == "OWNER_DELIVERY_PACKET_CANDIDATE_READY"
    owner_packet_candidate = owner_packet_result["owner_delivery_packet_candidate"]
    assert owner_packet_candidate is not None

    endpoint_boundary_result = build_service_1_real_endpoint_api_boundary_contract_v1(
        {
            "tenant_ref": TENANT_REF,
            "owner_ref": OWNER_REF,
            "case_ref": CASE_REF,
            "case_creation_payload": None,
            "request_id": "request:phase_h:001",
            "operation_kind": REQUEST_CASE_STATUS,
            "payload_ref": None,
            "payload": None,
            "idempotency_key": "idem:phase_h:001",
            "client_channel": "owner_portal",
            "saas_case_session_candidate": session_candidate,
            "tenant_isolation_candidate": tenant_isolation_candidate,
            "cost_rate_limit_candidate": endpoint_cost_guard_candidate,
            "notes": [],
        }
    )
    assert endpoint_boundary_result["status"] == "API_BOUNDARY_CANDIDATE_READY"
    endpoint_boundary_candidate = endpoint_boundary_result["api_boundary_candidate"]
    assert endpoint_boundary_candidate is not None

    auth_boundary_result = build_service_1_real_auth_boundary_contract_v1(
        {
            "auth_subject_ref": "auth_subject:owner_001",
            "external_identity_ref": "external_identity:portal:owner_001",
            "tenant_claim_ref": TENANT_REF,
            "owner_claim_ref": OWNER_REF,
            "requested_operation_kind": REQUEST_CASE_STATUS,
            "case_ref": CASE_REF,
            "session_ref": SESSION_REF,
            "client_channel": "owner_portal",
            "tenant_isolation_candidate": tenant_isolation_candidate,
            "case_session_candidate": session_candidate,
            "notes": [],
        }
    )
    assert auth_boundary_result["status"] == "AUTH_BOUNDARY_CANDIDATE_READY"
    auth_boundary_candidate = auth_boundary_result["auth_boundary_candidate"]
    assert auth_boundary_candidate is not None

    storage_boundary_result = build_service_1_real_storage_upload_boundary_contract_v1(
        {
            "tenant_ref": TENANT_REF,
            "owner_ref": OWNER_REF,
            "case_ref": CASE_REF,
            "upload_request_ref": "upload_request:phase_h:001",
            "file_name": "phase_h_evidence.csv",
            "file_kind": "CSV",
            "file_size_bytes": 128,
            "content_type": "text/csv",
            "storage_object_ref": "storage://tenant-001/case-001/phase_h_evidence.csv",
            "checksum": "sha256:phase_h_001",
            "client_channel": "owner_portal",
            "tenant_isolation_candidate": tenant_isolation_candidate,
            "cost_rate_limit_candidate": storage_cost_guard_candidate,
            "file_intake_candidate": file_intake_candidate,
            "notes": [],
        }
    )
    assert storage_boundary_result["status"] == "STORAGE_UPLOAD_BOUNDARY_CANDIDATE_READY"
    storage_boundary_candidate = storage_boundary_result["storage_upload_boundary_candidate"]
    assert storage_boundary_candidate is not None

    worker_boundary_result = build_service_1_real_worker_runtime_boundary_contract_v1(
        {
            "tenant_ref": TENANT_REF,
            "owner_ref": OWNER_REF,
            "case_ref": CASE_REF,
            "session_ref": SESSION_REF,
            "job_candidate_ref": "job_candidate:phase_h:owner_packet_refresh",
            "operation_kind": OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE,
            "pipeline_request_candidate_ref": "pipeline_request:phase_h:refresh_owner_packet",
            "file_intake_candidate_ref": "storage://tenant-001/case-001/phase_h_evidence.csv",
            "cost_estimate_units": 3,
            "rate_limit_context_ref": "rate_limit_context:phase_h:001",
            "retry_context": None,
            "tenant_isolation_candidate": tenant_isolation_candidate,
            "cost_rate_limit_candidate": worker_cost_guard_candidate,
            "failure_recovery_candidate": None,
            "notes": [],
        }
    )
    assert worker_boundary_result["status"] == "WORKER_RUNTIME_BOUNDARY_CANDIDATE_READY"
    worker_boundary_candidate = worker_boundary_result["worker_runtime_boundary_candidate"]
    assert worker_boundary_candidate is not None

    integration_result = build_service_1_human_review_release_integration_gate_v1(
        {
            "delivery_release_candidate": release_candidate,
            "owner_delivery_packet_candidate": owner_packet_candidate,
            "endpoint_api_boundary_candidate": endpoint_boundary_candidate,
            "auth_boundary_candidate": auth_boundary_candidate,
            "storage_upload_boundary_candidate": storage_boundary_candidate,
            "worker_runtime_boundary_candidate": worker_boundary_candidate,
            "notes": [],
        }
    )
    assert integration_result["status"] == "PENDING_HUMAN_REVIEW"
    integration_candidate = integration_result["human_review_release_integration_candidate"]
    assert integration_candidate is not None
    assert integration_candidate["status"] == "PENDING_HUMAN_REVIEW"
    assert integration_candidate["runtime_authorized"] is False

    signoff_result = apply_service_1_human_review_signoff_v1(
        human_review_gate=integration_candidate,
        decision=DECISION_APPROVED_FOR_DELIVERY,
        reviewer_id="operator_1",
        reviewer_notes="Revisión supervisada completa.",
        case_id=CASE_REF,
        delivery_status_before=integration_candidate["status"],
        metadata={"phase": "H"},
    ).to_dict()

    qa_delivery_gate_result = evaluate_service_1_qa_delivery_gate_v1(
        _qa_packet(owner_message=owner_packet_candidate["owner_facing_summary"])
    )
    assert qa_delivery_gate_result["status"] == "PASS"
    assert qa_delivery_gate_result["runtime_authorized"] is False

    final_release_result = build_service_1_final_owner_release_decision_gate_v1(
        {
            "human_review_release_integration_candidate": integration_candidate,
            "human_review_signoff_result": signoff_result,
            "qa_delivery_gate_result": qa_delivery_gate_result,
            "delivery_release_candidate": release_candidate,
            "owner_delivery_packet_candidate": owner_packet_candidate,
            "notes": [],
        }
    )
    assert final_release_result["status"] == "FINAL_OWNER_RELEASE_CANDIDATE_READY"
    final_release_candidate = final_release_result["final_owner_release_candidate"]
    assert final_release_candidate is not None
    assert final_release_candidate["final_release_authorized"] is True
    assert final_release_candidate["runtime_authorized"] is False
    assert final_release_candidate["publish_executed"] is False
    assert final_release_candidate["notification_sent"] is False

    handoff_result = build_service_1_final_release_to_owner_handoff_contract_v1(
        {
            "final_owner_release_candidate": final_release_candidate,
            "owner_delivery_packet_candidate": owner_packet_candidate,
            "delivery_release_candidate": release_candidate,
            "handoff_channel_candidate": handoff_channel_candidate,
            "owner_ref": OWNER_REF,
            "tenant_ref": TENANT_REF,
            "case_ref": CASE_REF,
            "notes": [],
        }
    )
    assert handoff_result["status"] == "OWNER_HANDOFF_CANDIDATE_READY"
    owner_handoff_candidate = handoff_result["owner_handoff_candidate"]
    assert owner_handoff_candidate is not None
    assert owner_handoff_candidate["handoff_authorized"] is True
    assert owner_handoff_candidate["runtime_authorized"] is False
    assert owner_handoff_candidate["publish_executed"] is False
    assert owner_handoff_candidate["notification_sent"] is False
    assert owner_handoff_candidate["handoff_executed"] is False

    assert endpoint_boundary_candidate["api_exposed"] is False
    assert endpoint_boundary_candidate["runtime_authorized"] is False
    assert auth_boundary_candidate["api_exposed"] is False
    assert auth_boundary_candidate["runtime_authorized"] is False
    assert storage_boundary_candidate["storage_write_authorized"] is False
    assert storage_boundary_candidate["runtime_authorized"] is False
    assert worker_boundary_candidate["worker_authorized"] is False
    assert worker_boundary_candidate["queue_authorized"] is False
    assert worker_boundary_candidate["runtime_authorized"] is False

    assert {
        "pipeline_run_result": pipeline_run_result,
        "session_candidate": session_candidate,
        "tenant_isolation_candidate": tenant_isolation_candidate,
        "endpoint_cost_guard_candidate": endpoint_cost_guard_candidate,
        "storage_cost_guard_candidate": storage_cost_guard_candidate,
        "worker_cost_guard_candidate": worker_cost_guard_candidate,
        "file_intake_candidate": file_intake_candidate,
        "handoff_channel_candidate": handoff_channel_candidate,
    } == original_state
