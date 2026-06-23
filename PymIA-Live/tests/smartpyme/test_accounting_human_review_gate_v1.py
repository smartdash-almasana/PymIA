from __future__ import annotations

import inspect

from pymia.smartpyme.accounting_human_review_gate_v1 import evaluate_accounting_human_review_gate_v1


def _gate_input() -> dict[str, object]:
    return {
        "capability_ref": "bank_reconciliation_basic",
        "reviewer_role": "operator",
        "decision": "APPROVED",
        "scope_ok": True,
        "evidence_ok": True,
        "forbidden_claims": [],
        "live_use": False,
    }


def test_pass_allows_only_sandbox_candidate_and_never_runtime() -> None:
    result = evaluate_accounting_human_review_gate_v1(gate_input=_gate_input())

    assert result["status"] == "PASS"
    assert result["sandbox_candidate_allowed"] is True
    assert result["runtime_authorized"] is False
    assert result["next_allowed_action"] == "prepare_accounting_sandbox_contract"


def test_pending_human_review_blocks_candidate() -> None:
    gate_input = _gate_input()
    gate_input["decision"] = "PENDING"

    result = evaluate_accounting_human_review_gate_v1(gate_input=gate_input)  # type: ignore[arg-type]

    assert result["status"] == "PENDING"
    assert result["sandbox_candidate_allowed"] is False
    assert result["runtime_authorized"] is False


def test_rejected_human_review_blocks_candidate() -> None:
    gate_input = _gate_input()
    gate_input["decision"] = "REJECTED"

    result = evaluate_accounting_human_review_gate_v1(gate_input=gate_input)  # type: ignore[arg-type]

    assert result["status"] == "REJECTED"
    assert result["next_allowed_action"] == "revise_accounting_sandbox_candidate"
    assert result["runtime_authorized"] is False


def test_forbidden_claims_block_candidate() -> None:
    gate_input = _gate_input()
    gate_input["forbidden_claims"] = ["conciliacion cerrada"]

    result = evaluate_accounting_human_review_gate_v1(gate_input=gate_input)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED"
    assert result["next_allowed_action"] == "remove_forbidden_accounting_claims"
    assert result["sandbox_candidate_allowed"] is False


def test_live_use_request_blocks_candidate() -> None:
    gate_input = _gate_input()
    gate_input["live_use"] = True

    result = evaluate_accounting_human_review_gate_v1(gate_input=gate_input)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED"
    assert result["next_allowed_action"] == "downgrade_to_sandbox_candidate_scope"
    assert result["runtime_authorized"] is False


def test_scope_not_validated_blocks_candidate() -> None:
    gate_input = _gate_input()
    gate_input["scope_ok"] = False

    result = evaluate_accounting_human_review_gate_v1(gate_input=gate_input)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED"
    assert result["next_allowed_action"] == "validate_accounting_scope"


def test_evidence_not_sufficient_blocks_candidate() -> None:
    gate_input = _gate_input()
    gate_input["evidence_ok"] = False

    result = evaluate_accounting_human_review_gate_v1(gate_input=gate_input)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED"
    assert result["next_allowed_action"] == "request_missing_accounting_evidence"


def test_invalid_forbidden_claims_shape_returns_invalid_input() -> None:
    gate_input = _gate_input()
    gate_input["forbidden_claims"] = "bad-shape"

    result = evaluate_accounting_human_review_gate_v1(gate_input=gate_input)  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["runtime_authorized"] is False


def test_module_has_no_io_or_runtime_dependencies() -> None:
    import pymia.smartpyme.accounting_human_review_gate_v1 as module

    source = inspect.getsource(module)

    assert "openpyxl" not in source
    assert "vertical_pipeline" not in source
    assert "service_1_pipeline" not in source
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()
    assert "open(" not in source
    assert ".save(" not in source
    assert "read_text(" not in source
    assert "read_bytes(" not in source
