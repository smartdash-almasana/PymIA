from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_owner_feedback_to_case_truth_patch_v1 import (
    SCHEMA_VERSION,
    build_service_1_owner_feedback_to_case_truth_patch_v1,
)


def _base_input() -> dict[str, object]:
    return {
        "structured_owner_feedback": {
            "confirmations": {"ventas_marzo_confirmadas": True},
            "corrections": {"costo_unitario": 1250.50},
            "declared_evidence_refs": ["evidence:xlsx:ventas_marzo_v2"],
            "owner_notes": ["El costo correcto estaba en la hoja auxiliar."],
        },
        "owner_delivery_packet_candidate": {
            "source_pipeline_run_ref": "run:s1:001",
            "artifact_refs": ["artifact:operator_report.md"],
            "warning_refs": ["warning:low_margin"],
            "owner_facing_summary": "summary",
            "packet_kind": "OWNER_DELIVERY_PACKET_CANDIDATE",
            "publishable": False,
            "signoff_required": True,
            "delivery_authorized": False,
            "autonomous_delivery_authorized": False,
            "signoff_authorized": False,
        },
        "current_case_truth": {
            "case_truth_ref": "case_truth:s1:001",
            "case_id": "case:s1:001",
            "status": "READY_FOR_TOOL_PLANNING",
            "confirmed_evidence_refs": ["evidence:xlsx:ventas_marzo"],
        },
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_owner_feedback_to_case_truth_patch_v1(payload)  # type: ignore[arg-type]


def test_blocks_if_owner_delivery_packet_candidate_is_missing() -> None:
    payload = _base_input()
    payload["owner_delivery_packet_candidate"] = None
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_MISSING_DELIVERY_PACKET"
    assert result["blocked_reason"] == "owner_delivery_packet_candidate_required"
    assert result["case_truth_patch_candidate"] is None


def test_blocks_if_current_case_truth_is_missing() -> None:
    payload = _base_input()
    payload["current_case_truth"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_CASE_TRUTH"
    assert result["blocked_reason"] == "current_case_truth_required"


def test_blocks_if_structured_feedback_is_missing() -> None:
    payload = _base_input()
    payload["structured_owner_feedback"] = {}
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_FEEDBACK"
    assert result["blocked_reason"] == "structured_owner_feedback_required"


def test_blocks_if_owner_packet_kind_is_wrong() -> None:
    payload = _base_input()
    packet = copy.deepcopy(payload["owner_delivery_packet_candidate"])
    packet["packet_kind"] = "FINAL_DELIVERY_PACKET"
    payload["owner_delivery_packet_candidate"] = packet
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_DELIVERY_PACKET"
    assert result["blocked_reason"] == "owner_delivery_packet_candidate_kind_required"


def test_blocks_if_owner_packet_is_publishable() -> None:
    payload = _base_input()
    packet = copy.deepcopy(payload["owner_delivery_packet_candidate"])
    packet["publishable"] = True
    payload["owner_delivery_packet_candidate"] = packet
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_DELIVERY_PACKET"
    assert result["blocked_reason"] == "owner_delivery_packet_must_not_be_publishable"


def test_blocks_if_case_truth_status_is_missing() -> None:
    payload = _base_input()
    case_truth = copy.deepcopy(payload["current_case_truth"])
    case_truth.pop("status")
    payload["current_case_truth"] = case_truth
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_CASE_TRUTH"
    assert result["blocked_reason"] == "current_case_truth_status_required"


def test_blocks_if_feedback_has_no_patch_content() -> None:
    payload = _base_input()
    payload["structured_owner_feedback"] = {
        "confirmations": {},
        "corrections": {},
        "declared_evidence_refs": [],
        "owner_notes": [],
    }
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_FEEDBACK"
    assert result["blocked_reason"] == "structured_owner_feedback_has_no_patch_content"


def test_ready_builds_case_truth_patch_candidate_with_confirmations_corrections_and_evidence() -> None:
    result = _build(_base_input())
    assert result["status"] == "CASE_TRUTH_PATCH_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert result["case_truth_patch_candidate"] == {
        "patch_kind": "CASE_TRUTH_PATCH_CANDIDATE",
        "source_owner_packet_ref": "run:s1:001",
        "source_case_truth_ref": "case_truth:s1:001",
        "confirmations": {"ventas_marzo_confirmadas": True},
        "corrections": {"costo_unitario": 1250.50},
        "declared_evidence_refs": ["evidence:xlsx:ventas_marzo_v2"],
        "owner_notes": ["El costo correcto estaba en la hoja auxiliar."],
        "patch_applied": False,
        "runtime_authorized": False,
        "rerun_authorized": False,
        "autonomous_rerun_authorized": False,
    }


def test_supports_confirmation_only_feedback() -> None:
    payload = _base_input()
    payload["structured_owner_feedback"] = {
        "confirmations": {"resultado_revisado_por_dueno": True},
    }
    result = _build(payload)
    candidate = result["case_truth_patch_candidate"]
    assert result["status"] == "CASE_TRUTH_PATCH_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["confirmations"] == {"resultado_revisado_por_dueno": True}
    assert candidate["corrections"] == {}
    assert candidate["declared_evidence_refs"] == []


def test_supports_correction_only_feedback() -> None:
    payload = _base_input()
    payload["structured_owner_feedback"] = {
        "corrections": {"precio_venta": 2100},
    }
    result = _build(payload)
    candidate = result["case_truth_patch_candidate"]
    assert result["status"] == "CASE_TRUTH_PATCH_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["corrections"] == {"precio_venta": 2100}
    assert candidate["confirmations"] == {}


def test_supports_declared_evidence_only_feedback() -> None:
    payload = _base_input()
    payload["structured_owner_feedback"] = {
        "declared_evidence_refs": ["evidence:csv:cobros_abril"],
    }
    result = _build(payload)
    candidate = result["case_truth_patch_candidate"]
    assert result["status"] == "CASE_TRUTH_PATCH_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["declared_evidence_refs"] == ["evidence:csv:cobros_abril"]


def test_never_authorizes_runtime_rerun_or_patch_application() -> None:
    cases = []
    missing_packet = _base_input()
    missing_packet["owner_delivery_packet_candidate"] = None
    cases.append(missing_packet)
    invalid_feedback = _base_input()
    invalid_feedback["structured_owner_feedback"] = {"confirmations": {}}
    cases.append(invalid_feedback)
    cases.append(_base_input())

    for payload in cases:
        result = _build(payload)
        assert result["runtime_authorized"] is False
        assert result["rerun_authorized"] is False
        assert result["patch_applied"] is False
        assert result["autonomous_rerun_authorized"] is False
        candidate = result["case_truth_patch_candidate"]
        if candidate is not None:
            assert candidate["runtime_authorized"] is False
            assert candidate["rerun_authorized"] is False
            assert candidate["patch_applied"] is False
            assert candidate["autonomous_rerun_authorized"] is False


def test_module_source_does_not_import_io_cli_pipeline_runner_llm_or_chatbot() -> None:
    import pymia.smartpyme.service_1_owner_feedback_to_case_truth_patch_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import os",
        "import shutil",
        "from pathlib",
        "open(",
        "write(",
        "import pymia.cli",
        "from pymia.cli",
        "run_service_1_pipeline_v1",
        "autonomous_pipeline_runner",
        "llm",
        "chatbot",
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
