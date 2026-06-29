from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_owner_reentry_to_autonomous_rerun_v1 import (
    SCHEMA_VERSION,
    build_service_1_owner_reentry_to_autonomous_rerun_v1,
)


def _base_input() -> dict[str, object]:
    return {
        "case_truth_patch_candidate": {
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
        },
        "current_case_truth": {
            "case_truth_ref": "case_truth:s1:001",
            "case_id": "case:s1:001",
            "status": "READY_FOR_TOOL_PLANNING",
        },
        "prior_chain_context": {
            "prior_chain_refs": [
                "case_truth_integration:s1:001",
                "tool_plan_candidate:s1:001",
                "pipeline_request_candidate:s1:001",
                "pipeline_run:s1:001",
            ],
            "recalculation_targets": [
                "case_truth_integration",
                "auto_tool_plan_candidate",
                "explicit_request_candidate_gate",
            ],
        },
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_owner_reentry_to_autonomous_rerun_v1(payload)  # type: ignore[arg-type]


def test_blocks_if_patch_candidate_is_missing() -> None:
    payload = _base_input()
    payload["case_truth_patch_candidate"] = None
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_INVALID_PATCH_CANDIDATE"
    assert result["blocked_reason"] == "case_truth_patch_candidate_required"
    assert result["autonomous_rerun_candidate"] is None


def test_blocks_if_current_case_truth_is_missing() -> None:
    payload = _base_input()
    payload["current_case_truth"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_CASE_TRUTH"
    assert result["blocked_reason"] == "current_case_truth_required"


def test_blocks_if_prior_chain_context_is_missing() -> None:
    payload = _base_input()
    payload["prior_chain_context"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_PRIOR_CHAIN_CONTEXT"
    assert result["blocked_reason"] == "prior_chain_context_required"


def test_blocks_if_patch_kind_is_wrong() -> None:
    payload = _base_input()
    patch = copy.deepcopy(payload["case_truth_patch_candidate"])
    patch["patch_kind"] = "APPLIED_PATCH"
    payload["case_truth_patch_candidate"] = patch
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_PATCH_CANDIDATE"
    assert result["blocked_reason"] == "patch_kind_must_be_case_truth_patch_candidate"


def test_blocks_if_patch_applied_is_true() -> None:
    payload = _base_input()
    patch = copy.deepcopy(payload["case_truth_patch_candidate"])
    patch["patch_applied"] = True
    payload["case_truth_patch_candidate"] = patch
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_PATCH_CANDIDATE"
    assert result["blocked_reason"] == "patch_candidate_must_not_be_applied"


def test_blocks_if_runtime_authorized_is_true() -> None:
    payload = _base_input()
    patch = copy.deepcopy(payload["case_truth_patch_candidate"])
    patch["runtime_authorized"] = True
    payload["case_truth_patch_candidate"] = patch
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_PATCH_CANDIDATE"
    assert result["blocked_reason"] == "patch_candidate_runtime_authorized_must_be_false"


def test_blocks_if_rerun_authorized_is_true() -> None:
    payload = _base_input()
    patch = copy.deepcopy(payload["case_truth_patch_candidate"])
    patch["rerun_authorized"] = True
    payload["case_truth_patch_candidate"] = patch
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_PATCH_CANDIDATE"
    assert result["blocked_reason"] == "patch_candidate_rerun_authorized_must_be_false"


def test_blocks_if_autonomous_rerun_authorized_is_true() -> None:
    payload = _base_input()
    patch = copy.deepcopy(payload["case_truth_patch_candidate"])
    patch["autonomous_rerun_authorized"] = True
    payload["case_truth_patch_candidate"] = patch
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_PATCH_CANDIDATE"
    assert result["blocked_reason"] == "patch_candidate_autonomous_rerun_authorized_must_be_false"


def test_blocks_if_patch_candidate_has_no_reentry_content() -> None:
    payload = _base_input()
    patch = copy.deepcopy(payload["case_truth_patch_candidate"])
    patch["confirmations"] = {}
    patch["corrections"] = {}
    patch["declared_evidence_refs"] = []
    patch["owner_notes"] = []
    payload["case_truth_patch_candidate"] = patch
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_PATCH_CANDIDATE"
    assert result["blocked_reason"] == "patch_candidate_has_no_reentry_content"


def test_blocks_if_case_truth_status_is_missing() -> None:
    payload = _base_input()
    case_truth = copy.deepcopy(payload["current_case_truth"])
    case_truth.pop("status")
    payload["current_case_truth"] = case_truth
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_CASE_TRUTH"
    assert result["blocked_reason"] == "current_case_truth_status_required"


def test_blocks_if_prior_chain_refs_are_missing() -> None:
    payload = _base_input()
    payload["prior_chain_context"] = {"recalculation_targets": ["case_truth_integration"]}
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_PRIOR_CHAIN_CONTEXT"
    assert result["blocked_reason"] == "prior_chain_refs_required"


def test_ready_builds_autonomous_rerun_candidate() -> None:
    result = _build(_base_input())
    assert result["status"] == "AUTONOMOUS_RERUN_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert result["autonomous_rerun_candidate"] == {
        "rerun_kind": "AUTONOMOUS_RERUN_CANDIDATE",
        "source_case_truth_patch_ref": "run:s1:001",
        "source_case_truth_ref": "case_truth:s1:001",
        "prior_chain_refs": [
            "case_truth_integration:s1:001",
            "tool_plan_candidate:s1:001",
            "pipeline_request_candidate:s1:001",
            "pipeline_run:s1:001",
        ],
        "recalculation_targets": [
            "case_truth_integration",
            "auto_tool_plan_candidate",
            "explicit_request_candidate_gate",
        ],
        "patch_applied": False,
        "runtime_authorized": False,
        "rerun_authorized": False,
        "autonomous_rerun_authorized": False,
    }


def test_uses_default_recalculation_targets_when_not_explicit() -> None:
    payload = _base_input()
    payload["prior_chain_context"] = {"prior_chain_refs": ["case_truth_integration:s1:001"]}
    result = _build(payload)
    candidate = result["autonomous_rerun_candidate"]
    assert result["status"] == "AUTONOMOUS_RERUN_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["recalculation_targets"] == [
        "case_truth_integration",
        "auto_tool_plan_candidate",
        "explicit_request_candidate_gate",
        "pipeline_request_candidate_gate",
    ]


def test_extracts_prior_chain_refs_from_named_context_fields() -> None:
    payload = _base_input()
    payload["prior_chain_context"] = {
        "case_truth_integration_ref": "case_truth_integration:s1:001",
        "tool_plan_candidate_ref": "tool_plan_candidate:s1:001",
        "pipeline_run_ref": "pipeline_run:s1:001",
    }
    result = _build(payload)
    candidate = result["autonomous_rerun_candidate"]
    assert result["status"] == "AUTONOMOUS_RERUN_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["prior_chain_refs"] == [
        "case_truth_integration:s1:001",
        "tool_plan_candidate:s1:001",
        "pipeline_run:s1:001",
    ]


def test_never_authorizes_runtime_rerun_or_patch_application() -> None:
    cases = []
    missing_patch = _base_input()
    missing_patch["case_truth_patch_candidate"] = None
    cases.append(missing_patch)
    missing_context = _base_input()
    missing_context["prior_chain_context"] = None
    cases.append(missing_context)
    cases.append(_base_input())

    for payload in cases:
        result = _build(payload)
        assert result["patch_applied"] is False
        assert result["runtime_authorized"] is False
        assert result["rerun_authorized"] is False
        assert result["autonomous_rerun_authorized"] is False
        candidate = result["autonomous_rerun_candidate"]
        if candidate is not None:
            assert candidate["patch_applied"] is False
            assert candidate["runtime_authorized"] is False
            assert candidate["rerun_authorized"] is False
            assert candidate["autonomous_rerun_authorized"] is False


def test_module_source_does_not_import_io_cli_pipeline_runner_llm_or_chatbot() -> None:
    import pymia.smartpyme.service_1_owner_reentry_to_autonomous_rerun_v1 as module

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
