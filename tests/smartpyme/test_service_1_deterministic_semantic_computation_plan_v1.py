from __future__ import annotations

import json
from pathlib import Path

from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    COMPUTATION_PLAN_SCHEMA_VERSION,
    STATUS_BLOCKED_BY_POLICY,
    STATUS_COMPUTATION_PLAN_BLOCKED,
    STATUS_CONFIRMED_BINDINGS,
    STATUS_NEEDS_EVIDENCE,
    STATUS_READY_FOR_COMPUTATION,
    STATUS_UNSUPPORTED_CAPABILITY,
    build_computation_plan,
    run_initial_pass,
    run_owner_reentry,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    BINDING_STATUS_BOUND_CONFIRMED,
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
        "fecha": {
            "sample_values": ["2026-06-01", "2026-06-02"],
            "inferred_type": "date",
        },
        "venta_total": {
            "sample_values": [1000, 2000],
            "inferred_type": "number",
        },
    }
    if include_collected:
        columns.append("cobrado")
        input_values["cobrado"] = "importe efectivamente cobrado"
        evidence["cobrado"] = {
            "sample_values": [800, 1500],
            "inferred_type": "number",
        }
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


def _assert_closed(packet: dict) -> None:
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False
    assert packet["computation_executed"] is False


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


def test_cash_collection_builds_governed_liq_001_computation_plan() -> None:
    plan = build_computation_plan(
        confirmed_bindings=_confirmed_cash_run(),
        requested_capability="sold_vs_collected_gap",
    )
    assert plan["schema_version"] == COMPUTATION_PLAN_SCHEMA_VERSION
    assert plan["status"] == STATUS_READY_FOR_COMPUTATION
    assert plan["family_id"] == "CASH_COLLECTIONS"
    assert plan["family_status"] == "VARIABLE_FAMILY_READY"
    assert plan["pathology_code"] == "LIQ_001"
    assert plan["formula_id"] == "LIQ_001_vendido_cobrado"
    assert plan["formula_expression"] == "sold_amount - collected_amount"
    assert plan["required_variables"] == ["sold_amount", "collected_amount"]
    assert plan["source_bindings"] == {
        "sold_amount": "venta_total",
        "collected_amount": "cobrado",
    }
    assert plan["computation_candidate_ready"] is True
    assert plan["catalog_versions"] == {
        "formula_catalog": "1.1",
        "pathology_catalog": "1.0",
        "evidence_matrix": "1.2",
    }
    _assert_closed(plan)


def test_reinjected_owner_binding_reaches_governed_computation_input() -> None:
    plan = build_computation_plan(
        confirmed_bindings=_confirmed_cash_run(),
        requested_capability="sold_vs_collected_gap",
    )
    governed = plan["governed_computation_input"]
    assert governed["schema_version"] == "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1"
    assert governed["source_bindings"]["collected_amount"] == "cobrado"
    assert "semantic_binding_result" not in plan


def test_family_missing_required_role_returns_needs_evidence() -> None:
    plan = build_computation_plan(
        confirmed_bindings=_confirmed_cash_run(include_collected=False),
        requested_capability="sold_vs_collected_gap",
    )
    assert plan["status"] == STATUS_NEEDS_EVIDENCE
    assert plan["blocked_reason"] == "VARIABLE_FAMILY_NOT_READY"
    assert ["collected_amount"] in plan["missing_role_groups"]
    assert plan["computation_candidate_ready"] is False
    _assert_closed(plan)


def test_unknown_capability_is_not_inferred() -> None:
    plan = build_computation_plan(
        confirmed_bindings=_confirmed_cash_run(),
        requested_capability="invented_business_magic",
    )
    assert plan["status"] == STATUS_UNSUPPORTED_CAPABILITY
    assert plan["blocked_reason"] == "CAPABILITY_NOT_GOVERNED"
    _assert_closed(plan)


def test_matrix_policy_can_block_an_otherwise_ready_candidate(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "docs" / "service_1_formula_pathology_evidence_matrix.v1.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    liq = next(
        entry for entry in payload["entries"] if entry["pathology_code"] == "LIQ_001"
    )
    liq["computation_candidate_allowed"] = False
    matrix = tmp_path / "blocked_matrix.json"
    matrix.write_text(json.dumps(payload), encoding="utf-8")

    plan = build_computation_plan(
        confirmed_bindings=_confirmed_cash_run(),
        requested_capability="sold_vs_collected_gap",
        evidence_matrix_path=matrix,
    )
    assert plan["status"] == STATUS_BLOCKED_BY_POLICY
    assert plan["blocked_reason"] == "COMPUTATION_CANDIDATE_NOT_ALLOWED"
    _assert_closed(plan)


def test_invalid_confirmed_packet_fails_closed() -> None:
    plan = build_computation_plan(
        confirmed_bindings={"status": "OWNER_QUESTIONS"},
        requested_capability="sold_vs_collected_gap",
    )
    assert plan["status"] == STATUS_COMPUTATION_PLAN_BLOCKED
    assert plan["blocked_reason"] == "CONFIRMED_BINDINGS_REQUIRED"
    _assert_closed(plan)


def test_missing_catalog_path_fails_closed(tmp_path: Path) -> None:
    plan = build_computation_plan(
        confirmed_bindings=_confirmed_cash_run(),
        requested_capability="sold_vs_collected_gap",
        formula_catalog_path=tmp_path / "missing_formula_catalog.json",
    )
    assert plan["status"] == STATUS_COMPUTATION_PLAN_BLOCKED
    assert plan["blocked_reason"].startswith("CATALOG_LOAD_BLOCKED:")
    _assert_closed(plan)


def test_request_flags_cannot_open_runtime() -> None:
    plan = build_computation_plan(
        confirmed_bindings=_confirmed_cash_run(),
        requested_capability="sold_vs_collected_gap",
        runtime_authorized=True,
    )
    assert plan["status"] == STATUS_BLOCKED_BY_POLICY
    assert plan["blocked_reason"] == "REQUEST_SAFETY_FLAGS_FORBIDDEN"
    _assert_closed(plan)
