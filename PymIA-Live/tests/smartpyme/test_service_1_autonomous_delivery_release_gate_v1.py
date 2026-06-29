from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_autonomous_delivery_release_gate_v1 import (
    SCHEMA_VERSION,
    build_service_1_autonomous_delivery_release_gate_v1,
)


def _base_input() -> dict[str, object]:
    return {
        "pipeline_run_status": "PIPELINE_RUN_COMPLETED",
        "pipeline_run_result": {
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "run_id": "run:s1:001",
            "executed_tool_refs": ["precio_margen_basico"],
        },
        "expected_artifacts": ["artifact:operator_report.md", "artifact:summary.json"],
        "produced_artifacts": ["artifact:operator_report.md", "artifact:summary.json"],
        "pipeline_errors": [],
        "pipeline_warnings": ["warning:low_margin"],
        "delivery_policy_status": "DELIVERY_POLICY_CANDIDATE_ALLOWED",
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_autonomous_delivery_release_gate_v1(payload)  # type: ignore[arg-type]


def test_blocks_if_pipeline_run_status_is_not_completed() -> None:
    payload = _base_input()
    payload["pipeline_run_status"] = "PIPELINE_RUN_FAILED"
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_PIPELINE_NOT_COMPLETED"
    assert result["blocked_reason"] == "pipeline_run_status_not_completed"
    assert result["delivery_release_candidate"] is None


def test_blocks_if_pipeline_errors_are_present() -> None:
    payload = _base_input()
    payload["pipeline_errors"] = ["error:tool_failed"]
    result = _build(payload)
    assert result["status"] == "BLOCKED_PIPELINE_ERRORS"
    assert result["blocked_reason"] == "pipeline_errors_present"


def test_blocks_if_delivery_policy_does_not_allow_candidate() -> None:
    payload = _base_input()
    payload["delivery_policy_status"] = "DELIVERY_POLICY_BLOCKED"
    result = _build(payload)
    assert result["status"] == "BLOCKED_DELIVERY_POLICY"
    assert result["blocked_reason"] == "delivery_policy_not_allowed"


def test_unknown_if_expected_artifacts_are_empty() -> None:
    payload = _base_input()
    payload["expected_artifacts"] = []
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "expected_artifacts_required"


def test_blocks_if_expected_artifact_is_missing() -> None:
    payload = _base_input()
    payload["produced_artifacts"] = ["artifact:operator_report.md"]
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_ARTIFACTS"
    assert result["blocked_reason"] == "missing_expected_artifacts"
    assert result["missing_artifacts"] == ["artifact:summary.json"]


def test_ready_when_pipeline_completed_without_errors_policy_allowed_and_artifacts_present() -> None:
    result = _build(_base_input())
    assert result["status"] == "DELIVERY_RELEASE_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert result["missing_artifacts"] == []
    assert result["delivery_release_candidate"] == {
        "source_pipeline_run_ref": "run:s1:001",
        "artifact_refs": ["artifact:operator_report.md", "artifact:summary.json"],
        "warning_refs": ["warning:low_margin"],
        "release_kind": "DELIVERY_RELEASE_CANDIDATE",
        "publishable": False,
        "signoff_required": True,
    }


def test_candidate_has_release_kind_delivery_release_candidate() -> None:
    result = _build(_base_input())
    candidate = result["delivery_release_candidate"]
    assert candidate is not None
    assert candidate["release_kind"] == "DELIVERY_RELEASE_CANDIDATE"


def test_candidate_is_not_publishable() -> None:
    result = _build(_base_input())
    candidate = result["delivery_release_candidate"]
    assert candidate is not None
    assert candidate["publishable"] is False


def test_candidate_requires_signoff() -> None:
    result = _build(_base_input())
    candidate = result["delivery_release_candidate"]
    assert candidate is not None
    assert candidate["signoff_required"] is True


def test_never_authorizes_delivery_autonomous_delivery_release_or_signoff() -> None:
    cases = []
    blocked_status = _base_input()
    blocked_status["pipeline_run_status"] = "PIPELINE_RUN_FAILED"
    cases.append(blocked_status)
    blocked_errors = _base_input()
    blocked_errors["pipeline_errors"] = ["error:any"]
    cases.append(blocked_errors)
    blocked_artifacts = _base_input()
    blocked_artifacts["produced_artifacts"] = []
    cases.append(blocked_artifacts)
    cases.append(_base_input())

    for payload in cases:
        result = _build(payload)
        assert result["delivery_authorized"] is False
        assert result["autonomous_delivery_authorized"] is False
        assert result["release_authorized"] is False
        assert result["signoff_authorized"] is False


def test_module_source_does_not_import_cli_delivery_signoff_model_runtime_or_chatbot() -> None:
    import pymia.smartpyme.service_1_autonomous_delivery_release_gate_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import pymia.cli",
        "from pymia.cli",
        "service_1_manual_first_aid_delivery_flow_v1",
        "operator_delivery_package",
        "signoff_flow",
        "signoff_service",
        "llm",
        "chatbot",
        "run_service_1_pipeline_v1",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source


def test_does_not_mutate_input() -> None:
    payload = _base_input()
    original = copy.deepcopy(payload)
    _build(payload)
    assert payload == original


def test_output_is_deterministic() -> None:
    payload = _base_input()
    first = _build(copy.deepcopy(payload))
    second = _build(copy.deepcopy(payload))
    assert first == second
