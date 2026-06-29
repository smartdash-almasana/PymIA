from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_owner_delivery_packet_for_saas_v1 import (
    SCHEMA_VERSION,
    build_service_1_owner_delivery_packet_for_saas_v1,
)


def _base_input() -> dict[str, object]:
    return {
        "release_candidate_status": "DELIVERY_RELEASE_CANDIDATE_READY",
        "delivery_release_candidate": {
            "source_pipeline_run_ref": "run:s1:001",
            "artifact_refs": ["artifact:operator_report.md", "artifact:summary.json"],
            "warning_refs": ["warning:low_margin"],
            "release_kind": "DELIVERY_RELEASE_CANDIDATE",
            "publishable": False,
            "signoff_required": True,
        },
        "pipeline_run_result": {
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "run_id": "run:s1:001",
            "executed_tool_refs": ["precio_margen_basico"],
        },
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_owner_delivery_packet_for_saas_v1(payload)  # type: ignore[arg-type]


def test_blocks_if_release_candidate_status_is_not_ready() -> None:
    payload = _base_input()
    payload["release_candidate_status"] = "BLOCKED_MISSING_ARTIFACTS"
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_RELEASE_CANDIDATE_NOT_READY"
    assert result["blocked_reason"] == "release_candidate_status_not_ready"
    assert result["owner_delivery_packet_candidate"] is None


def test_blocks_if_release_candidate_is_missing() -> None:
    payload = _base_input()
    payload["delivery_release_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_RELEASE_CANDIDATE"
    assert result["blocked_reason"] == "delivery_release_candidate_required"


def test_blocks_if_pipeline_run_result_is_missing() -> None:
    payload = _base_input()
    payload["pipeline_run_result"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_PIPELINE_RESULT"
    assert result["blocked_reason"] == "pipeline_run_result_required"


def test_blocks_if_release_kind_is_wrong() -> None:
    payload = _base_input()
    candidate = copy.deepcopy(payload["delivery_release_candidate"])
    candidate["release_kind"] = "FINAL_DELIVERY"
    payload["delivery_release_candidate"] = candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_RELEASE_CANDIDATE_NOT_READY"
    assert result["blocked_reason"] == "release_kind_not_delivery_release_candidate"


def test_blocks_if_release_candidate_is_publishable() -> None:
    payload = _base_input()
    candidate = copy.deepcopy(payload["delivery_release_candidate"])
    candidate["publishable"] = True
    payload["delivery_release_candidate"] = candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_RELEASE_CANDIDATE_NOT_READY"
    assert result["blocked_reason"] == "release_candidate_must_not_be_publishable"


def test_blocks_if_release_candidate_does_not_require_signoff() -> None:
    payload = _base_input()
    candidate = copy.deepcopy(payload["delivery_release_candidate"])
    candidate["signoff_required"] = False
    payload["delivery_release_candidate"] = candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_RELEASE_CANDIDATE_NOT_READY"
    assert result["blocked_reason"] == "release_candidate_must_require_signoff"


def test_blocks_if_artifact_refs_are_missing() -> None:
    payload = _base_input()
    candidate = copy.deepcopy(payload["delivery_release_candidate"])
    candidate["artifact_refs"] = []
    payload["delivery_release_candidate"] = candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_ARTIFACT_REFS"
    assert result["blocked_reason"] == "artifact_refs_required"
    assert result["missing_artifact_refs"] == ["artifact_refs"]


def test_ready_builds_owner_delivery_packet_candidate() -> None:
    result = _build(_base_input())
    assert result["status"] == "OWNER_DELIVERY_PACKET_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert result["owner_delivery_packet_candidate"] == {
        "source_pipeline_run_ref": "run:s1:001",
        "artifact_refs": ["artifact:operator_report.md", "artifact:summary.json"],
        "warning_refs": ["warning:low_margin"],
        "owner_facing_summary": (
            "PymIA preparó un paquete candidato para el dueño PyME con "
            "2 artefacto(s) referenciado(s), 1 advertencia(s) y "
            "1 herramienta(s) ejecutada(s). El paquete todavía requiere "
            "revisión/signoff antes de publicarse."
        ),
        "packet_kind": "OWNER_DELIVERY_PACKET_CANDIDATE",
        "publishable": False,
        "signoff_required": True,
        "delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "signoff_authorized": False,
    }


def test_maps_artifact_and_warning_refs_faithfully_without_disk_access() -> None:
    result = _build(_base_input())
    candidate = result["owner_delivery_packet_candidate"]
    assert candidate is not None
    assert candidate["artifact_refs"] == ["artifact:operator_report.md", "artifact:summary.json"]
    assert candidate["warning_refs"] == ["warning:low_margin"]


def test_packet_candidate_has_required_kind_and_guardrails() -> None:
    result = _build(_base_input())
    candidate = result["owner_delivery_packet_candidate"]
    assert candidate is not None
    assert candidate["packet_kind"] == "OWNER_DELIVERY_PACKET_CANDIDATE"
    assert candidate["publishable"] is False
    assert candidate["signoff_required"] is True
    assert candidate["delivery_authorized"] is False
    assert candidate["autonomous_delivery_authorized"] is False
    assert candidate["signoff_authorized"] is False


def test_result_never_authorizes_publication_delivery_or_signoff() -> None:
    cases = []
    blocked = _base_input()
    blocked["release_candidate_status"] = "BLOCKED"
    cases.append(blocked)
    missing_artifact = _base_input()
    candidate = copy.deepcopy(missing_artifact["delivery_release_candidate"])
    candidate["artifact_refs"] = []
    missing_artifact["delivery_release_candidate"] = candidate
    cases.append(missing_artifact)
    cases.append(_base_input())

    for payload in cases:
        result = _build(payload)
        assert result["publishable"] is False
        assert result["delivery_authorized"] is False
        assert result["autonomous_delivery_authorized"] is False
        assert result["signoff_required"] is True
        assert result["signoff_authorized"] is False


def test_module_source_does_not_import_io_cli_delivery_operator_package_model_runtime_or_chatbot() -> None:
    import pymia.smartpyme.service_1_owner_delivery_packet_for_saas_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import os",
        "import shutil",
        "from pathlib",
        "open(",
        "write(",
        "import pymia.cli",
        "from pymia.cli",
        "service_1_manual_first_aid_delivery_flow_v1",
        "operator_delivery_package",
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
