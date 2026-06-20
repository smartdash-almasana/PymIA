from __future__ import annotations

import inspect

from pymia.smartpyme.first_aid_entrypoint import evaluate_first_aid_entrypoint
from pymia.smartpyme import first_aid_entrypoint


def test_first_aid_detects_excel_cleanup_intent() -> None:
    verdict = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="Mirame este Excel y sacame algo en limpio.",
        has_file=True,
    )

    assert verdict["status"] == "FIRST_AID_READY"
    assert verdict["allowed_to_run_first_aid"] is True
    assert verdict["service_depth"]["level"] == "FIRST_AID"
    assert verdict["service_depth"]["required_evidence_depth"] == "single_source"
    assert verdict["service_depth"]["required_case_file_depth"] == "minimal"
    assert verdict["service_depth"]["next_allowed_action"] == "run_first_aid_microservice"
    assert verdict["required_evidence"] == []


def test_first_aid_requires_minimal_evidence_when_no_file() -> None:
    verdict = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="Sacame algo en limpio de esta planilla.",
        has_file=False,
    )

    assert verdict["status"] == "FIRST_AID_NEEDS_EVIDENCE"
    assert verdict["allowed_to_run_first_aid"] is False
    assert verdict["service_depth"]["level"] == "FIRST_AID"
    assert verdict["next_allowed_action"] == "request_minimal_evidence"
    assert verdict["required_evidence"] == ["minimal_file_or_source"]
    assert verdict["warnings"] == ["FIRST_AID requires a minimal file or source before execution."]


def test_first_aid_does_not_escalate_to_diagnosis_without_cross_source() -> None:
    verdict = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="No sé si gano y no me cierra la caja.",
        has_file=True,
        taxonomic_intake={"dolores_declarados": ["no sé si gano"]},
    )

    assert verdict["status"] == "NOT_FIRST_AID"
    assert verdict["allowed_to_run_first_aid"] is False
    assert verdict["service_depth"]["level"] == "DETERMINISTIC_DIAGNOSIS"
    assert verdict["next_allowed_action"] == "request_cross_source_evidence"
    assert verdict["next_allowed_action"] != "run_deterministic_diagnosis"
    assert "FIRST_AID must not run or diagnose" in verdict["warnings"][0]


def test_first_aid_preserves_taxonomic_nulls() -> None:
    verdict = evaluate_first_aid_entrypoint(
        tenant_id=" tenant_1 ",
        intake_id=" intake_1 ",
        raw_owner_message=" Ordename esta planilla. ",
        has_file=False,
        taxonomic_intake=None,
    )

    assert verdict["tenant_id"] == "tenant_1"
    assert verdict["intake_id"] == "intake_1"
    assert verdict["raw_owner_message"] == "Ordename esta planilla."
    assert verdict["service_depth"]["level"] == "FIRST_AID"
    assert verdict["service_depth"]["required_case_file_depth"] == "minimal"


def test_first_aid_consumes_service_depth_without_modifying_it() -> None:
    source = inspect.getsource(first_aid_entrypoint)

    assert "derive_service_depth" in source
    assert "ROUTING_VOCABULARY" not in source


def test_first_aid_does_not_touch_ocf_or_replay_or_diagnostic_core() -> None:
    source = inspect.getsource(first_aid_entrypoint)

    assert "diagnostic_core" not in source
    assert "ocf_snapshot" not in source
    assert "case_replay" not in source
    assert "vertical_pipeline" not in source
    assert "storage" not in source


def test_first_aid_rejects_empty_identity_or_message() -> None:
    for field, kwargs in [
        ("tenant_id", {"tenant_id": "", "intake_id": "intake_1", "raw_owner_message": "Mirame este Excel."}),
        ("intake_id", {"tenant_id": "tenant_1", "intake_id": "", "raw_owner_message": "Mirame este Excel."}),
        ("raw_owner_message", {"tenant_id": "tenant_1", "intake_id": "intake_1", "raw_owner_message": ""}),
    ]:
        try:
            evaluate_first_aid_entrypoint(has_file=False, **kwargs)
        except ValueError as exc:
            assert field in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"expected ValueError for {field}")


def test_first_aid_does_not_modify_vertical_slice_contract() -> None:
    source = inspect.getsource(first_aid_entrypoint)

    assert "argparse" not in source
    assert "main(" not in source
    assert "build_pipeline" not in source
