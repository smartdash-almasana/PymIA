from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.smartpyme.service_1_computability_v1 import (
    SCHEMA_VERSION as P8_SCHEMA_VERSION,
    STATUS_BLOCKED as P8_STATUS_BLOCKED,
    STATUS_COMPUTABLE as P8_STATUS_COMPUTABLE,
    STATUS_NEEDS_EVIDENCE as P8_STATUS_NEEDS_EVIDENCE,
    STATUS_UNSUPPORTED_CAPABILITY as P8_STATUS_UNSUPPORTED_CAPABILITY,
)
from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    STATUS_CONFIRMED_BINDINGS,
    build_computability_decision_from_confirmed_bindings_v1,
    run_initial_pass,
    run_owner_reentry,
)


def _option_id_for_label(question: dict, expected_text: str) -> str:
    expected = expected_text.lower()
    for item in question["options"]:
        if item["option_id"] in {"OTHER", "IGNORE"}:
            continue
        if expected in item["label"].lower():
            return item["option_id"]
    return next(
        item["option_id"]
        for item in question["options"]
        if item["option_id"] not in {"OTHER", "IGNORE"}
    )


def _cash_ingestion(*, include_collected: bool = True) -> dict:
    columns = ["fecha", "venta_total"]
    input_values = {
        "fecha": "fecha de la operación",
        "venta_total": "importe total vendido",
    }
    evidence = {
        "fecha": {"sample_values": ["2026-06-01", "2026-06-02"], "inferred_type": "date"},
        "venta_total": {"sample_values": [1000, 2000], "inferred_type": "number"},
    }
    if include_collected:
        columns.append("cobrado")
        input_values["cobrado"] = "importe efectivamente cobrado"
        evidence["cobrado"] = {"sample_values": [800, 1500], "inferred_type": "number"}
    return {
        "case_id": "case_cash_collection_plan_v1",
        "source_kind": "xlsx",
        "filename": "ventas_cobros.xlsx",
        "columns": columns,
        "input_values": input_values,
        "column_evidence": evidence,
        "runtime_authorized": False,
    }


def _confirmed_cash_run(*, include_collected: bool = True) -> dict:
    first = run_initial_pass(
        ingestion_output=_cash_ingestion(include_collected=include_collected),
        sheet_name="Ventas",
    )
    if first["status"] == STATUS_CONFIRMED_BINDINGS:
        return first
    preferred_labels = {
        "fecha": "fecha",
        "venta_total": "venta total",
        "cobrado": "cobrado",
    }
    answers = {
        question["column_name"]: _option_id_for_label(
            question, preferred_labels.get(question["column_name"], "")
        )
        for question in first["owner_questions"]
    }
    out = run_owner_reentry(previous_run=first, owner_answers=answers)
    assert out["status"] == STATUS_CONFIRMED_BINDINGS
    return out


def _decision(*, include_collected: bool = True, capability: str = "sold_vs_collected_gap", **paths):
    return build_computability_decision_from_confirmed_bindings_v1(
        confirmed_bindings=_confirmed_cash_run(include_collected=include_collected),
        requested_capability=capability,
        **paths,
    )


def _assert_closed(payload: dict) -> None:
    assert payload["runtime_authorized"] is False
    assert payload["tool_execution_authorized"] is False
    assert payload["product_ready"] is False
    assert payload["delivery_authorized"] is False
    assert payload["diagnosis_generated"] is False


def test_owner_reentry_preserves_governed_reinjected_candidates() -> None:
    confirmed = _confirmed_cash_run()
    reentry = confirmed["reentry_packet"]
    assert reentry["column_candidates"]
    by_column = {
        candidate.source_column_name: candidate
        for candidate in reentry["column_candidates"]
    }
    assert by_column["cobrado"].owner_confirmation_required is False
    assert by_column["cobrado"].metadata["owner_confirmed"] is True
    assert by_column["cobrado"].candidate_variable_names == ("collected_amount",)


def test_cash_collection_builds_canonical_p8_governed_input() -> None:
    decision = _decision()
    assert decision.schema_version == P8_SCHEMA_VERSION
    assert decision.status == P8_STATUS_COMPUTABLE
    assert decision.family_id == "CASH_COLLECTIONS"
    governed = decision.governed_computation_input
    assert governed is not None
    assert governed.pathology_code == "LIQ_001"
    assert governed.formula_id == "LIQ_001_vendido_cobrado"
    assert governed.formula_expression == "sold_amount - collected_amount"
    assert list(governed.required_variables) == ["sold_amount", "collected_amount"]
    assert dict(governed.source_bindings) == {
        "sold_amount": "venta_total",
        "collected_amount": "cobrado",
    }
    assert dict(governed.catalog_versions) == {
        "formula_catalog": "1.1",
        "pathology_catalog": "2.0",
        "evidence_matrix": "2.0",
    }
    _assert_closed(decision.to_dict())
    _assert_closed(governed.to_dict())


def test_reinjected_owner_binding_reaches_governed_computation_input() -> None:
    decision = _decision()
    governed = decision.governed_computation_input
    assert governed is not None
    payload = governed.to_dict()
    assert payload["schema_version"] == "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1"
    assert payload["source_bindings"]["collected_amount"] == "cobrado"
    assert "semantic_binding_result" not in payload


def test_family_missing_required_role_returns_needs_evidence() -> None:
    decision = _decision(include_collected=False)
    assert decision.status == P8_STATUS_NEEDS_EVIDENCE
    assert decision.reason == "REQUIREMENTS_NOT_MATCHED"
    assert ("collected_amount",) in decision.missing_role_groups
    assert decision.governed_computation_input is None
    _assert_closed(decision.to_dict())


def test_unknown_capability_is_not_inferred() -> None:
    decision = _decision(capability="invented_business_magic")
    assert decision.status == P8_STATUS_UNSUPPORTED_CAPABILITY
    assert decision.reason == "CAPABILITY_NOT_GOVERNED"
    _assert_closed(decision.to_dict())


def test_matrix_policy_can_block_an_otherwise_ready_candidate(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "docs" / "service_1_formula_pathology_evidence_matrix.v1.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    liq = next(entry for entry in payload["entries"] if entry["pathology_code"] == "LIQ_001")
    liq["computation_candidate_allowed"] = False
    matrix = tmp_path / "blocked_matrix.json"
    matrix.write_text(json.dumps(payload), encoding="utf-8")

    decision = _decision(evidence_matrix_path=matrix)
    assert decision.status == P8_STATUS_BLOCKED
    assert decision.reason == "COMPUTATION_CANDIDATE_NOT_ALLOWED"
    assert decision.governed_computation_input is None
    _assert_closed(decision.to_dict())


def test_invalid_confirmed_packet_fails_closed() -> None:
    with pytest.raises(ValueError, match="confirmed bindings are required"):
        build_computability_decision_from_confirmed_bindings_v1(
            confirmed_bindings={"status": "OWNER_QUESTIONS"},
            requested_capability="sold_vs_collected_gap",
        )


def test_missing_catalog_path_fails_closed(tmp_path: Path) -> None:
    decision = _decision(formula_catalog_path=tmp_path / "missing_formula_catalog.json")
    assert decision.status == P8_STATUS_BLOCKED
    assert str(decision.reason or "").startswith("CATALOG_LOAD_BLOCKED:")
    _assert_closed(decision.to_dict())


def test_p8_output_cannot_authorize_runtime() -> None:
    decision = _decision()
    _assert_closed(decision.to_dict())
    assert decision.governed_computation_input is not None
    _assert_closed(decision.governed_computation_input.to_dict())
