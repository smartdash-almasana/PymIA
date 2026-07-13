from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.first_aid_entrypoint import evaluate_first_aid_entrypoint
from pymia.smartpyme.first_aid_owner_output import build_first_aid_owner_view


_FORBIDDEN_OWNER_TERMS = (
    "margen",
    "costo",
    "rentabilidad",
    "diagnóstico",
    "diagnostico",
    "OCF",
    "snapshot",
    "fórmula",
    "formula",
    "hallazgo confirmado",
    "tenant_id",
    "intake_id",
    "service_depth",
    "single_source_task_request",
)


def _joined_output_text(output: dict) -> str:
    values: list[str] = []
    for value in output.values():
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value))
    return "\n".join(values)


def _assert_no_forbidden_owner_terms(output: dict) -> None:
    text = _joined_output_text(output)
    for term in _FORBIDDEN_OWNER_TERMS:
        assert term not in text


def test_first_aid_owner_output_requests_minimal_evidence_without_diagnosis() -> None:
    verdict = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="Mirame este Excel.",
        has_file=False,
    )

    output = build_first_aid_owner_view(verdict=verdict)

    assert output["status"] == "REQUEST_EVIDENCE"
    assert "planilla" in output["message"]
    assert "fuente mínima" in output["message"]
    assert output["required_artifacts"] == ["minimal_file_or_source"]
    _assert_no_forbidden_owner_terms(output)


def test_first_aid_owner_output_ready_does_not_promise_full_diagnosis() -> None:
    verdict = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="Sacame algo en limpio de esta planilla.",
        has_file=True,
    )

    output = build_first_aid_owner_view(verdict=verdict)

    assert output["status"] == "READY_FOR_REVIEW"
    assert "revisión inicial" in output["message"]
    assert "una sola fuente" in output["next_step_hint"]
    assert output["required_artifacts"] == []
    _assert_no_forbidden_owner_terms(output)


def test_first_aid_owner_output_not_first_aid_redirects_without_running_first_aid() -> None:
    verdict = evaluate_first_aid_entrypoint(
        tenant_id="tenant_1",
        intake_id="intake_1",
        raw_owner_message="Quiero profesionalizar mi empresa y que no dependa de mí.",
        has_file=True,
    )

    output = build_first_aid_owner_view(verdict=verdict)

    assert output["status"] == "REDIRECT_TO_DEEPER_INTAKE"
    assert "más contexto" in output["message"]
    assert "tipo de negocio" in output["message"]
    assert "dolor principal" in output["message"]
    _assert_no_forbidden_owner_terms(output)


def test_first_aid_owner_output_contains_next_question_when_signal_exists() -> None:
    ready = build_first_aid_owner_view(
        verdict=evaluate_first_aid_entrypoint(
            tenant_id="tenant_1",
            intake_id="intake_1",
            raw_owner_message="Ordename esta planilla.",
            has_file=True,
        )
    )
    needs_evidence = build_first_aid_owner_view(
        verdict=evaluate_first_aid_entrypoint(
            tenant_id="tenant_1",
            intake_id="intake_1",
            raw_owner_message="Ordename esta planilla.",
            has_file=False,
        )
    )

    assert ready["next_question"]
    assert needs_evidence["next_question"]
    assert "?" in ready["next_question"]
    assert "?" in needs_evidence["next_question"]


def test_first_aid_owner_output_has_no_technical_ids() -> None:
    output = build_first_aid_owner_view(
        verdict=evaluate_first_aid_entrypoint(
            tenant_id="tenant_1",
            intake_id="intake_1",
            raw_owner_message="Mirame este archivo.",
            has_file=True,
        )
    )

    text = _joined_output_text(output)
    assert "tenant_1" not in text
    assert "intake_1" not in text
    assert "tenant_id" not in text
    assert "intake_id" not in text


def test_first_aid_owner_output_has_no_formula_or_ocf_claims() -> None:
    output = build_first_aid_owner_view(
        verdict=evaluate_first_aid_entrypoint(
            tenant_id="tenant_1",
            intake_id="intake_1",
            raw_owner_message="Mirame este Excel.",
            has_file=True,
        )
    )

    _assert_no_forbidden_owner_terms(output)


def test_first_aid_owner_output_does_not_import_forbidden_layers() -> None:
    source = Path("pymia/smartpyme/first_aid_owner_output.py").read_text(encoding="utf-8")

    assert "diagnostic_core" not in source
    assert "owner_facing_report" not in source
    assert "owner_output" not in source
    assert "rendering" not in source
    assert "vertical_pipeline" not in source
    assert "vertical_slice" not in source
    assert "storage" not in source
    assert "case_replay" not in source
    assert "ocf_snapshot" not in source
    assert "ROUTING_VOCABULARY" not in source
