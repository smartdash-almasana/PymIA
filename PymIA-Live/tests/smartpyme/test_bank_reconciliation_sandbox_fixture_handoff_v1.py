from __future__ import annotations

import inspect

from pymia.smartpyme.accounting_human_review_gate_v1 import evaluate_accounting_human_review_gate_v1
from pymia.smartpyme.bank_reconciliation_contract_v1 import build_bank_reconciliation_contract_v1
from pymia.smartpyme.bank_reconciliation_sandbox_contract_v1 import build_bank_reconciliation_sandbox_contract_v1
from pymia.smartpyme.bank_reconciliation_sandbox_fixture_handoff_v1 import (
    CAPABILITY_REF,
    build_bank_reconciliation_sandbox_fixture_handoff_v1,
)
from pymia.smartpyme.bank_reconciliation_sandbox_fixture_model_v1 import (
    build_bank_reconciliation_sandbox_fixture_model_v1,
)


def _movement(ref: str) -> dict[str, str]:
    return {"movement_ref": ref, "date": "2026-06-01", "amount": "100.00", "description": "sample"}


def _fixture_model() -> dict[str, object]:
    return build_bank_reconciliation_sandbox_fixture_model_v1(
        bundle_input={
            "bank_statement_fixture": {
                "fixture_id": "bank-fixture-001",
                "source_ref": "sample-bank",
                "period_ref": "2026-06",
                "currency": "ARS",
                "movements": [_movement("bank-001")],
                "live_source": False,
            },
            "internal_ledger_fixture": {
                "fixture_id": "ledger-fixture-001",
                "source_ref": "sample-ledger",
                "period_ref": "2026-06",
                "currency": "ARS",
                "movements": [_movement("ledger-001")],
                "live_source": False,
            },
        }
    )


def _base_contract() -> dict[str, object]:
    return build_bank_reconciliation_contract_v1(
        contract_input={
            "owner_requested_output": "bank_reconciliation_scope_report",
            "source_files_received": ["extracto_banco", "archivo_contable"],
            "received_fields": ["fecha", "importe", "referencia"],
        }
    )


def _human_gate() -> dict[str, object]:
    return evaluate_accounting_human_review_gate_v1(
        gate_input={
            "capability_ref": "bank_reconciliation_basic",
            "reviewer_role": "operator",
            "decision": "APPROVED",
            "scope_ok": True,
            "evidence_ok": True,
            "forbidden_claims": [],
            "live_use": False,
        }
    )


def _handoff_input() -> dict[str, object]:
    return {
        "fixture_model_result": _fixture_model(),
        "base_contract": _base_contract(),
        "human_gate": _human_gate(),
        "live_use_requested": False,
    }


def test_ready_handoff_builds_sandbox_input() -> None:
    result = build_bank_reconciliation_sandbox_fixture_handoff_v1(handoff_input=_handoff_input())

    assert result["status"] == "READY"
    assert result["capability_ref"] == CAPABILITY_REF
    assert result["runtime_authorized"] is False
    assert result["production_allowed"] is False
    assert result["sandbox_input_ready"] is True
    assert result["sandbox_input"] is not None
    assert result["sandbox_input"]["fixture_refs"] == ["bank_statement_fixture", "internal_ledger_fixture"]


def test_ready_handoff_integrates_with_sandbox_contract() -> None:
    handoff = build_bank_reconciliation_sandbox_fixture_handoff_v1(handoff_input=_handoff_input())

    sandbox = build_bank_reconciliation_sandbox_contract_v1(sandbox_input=handoff["sandbox_input"])  # type: ignore[arg-type]

    assert sandbox["status"] == "READY_FOR_SANDBOX_CONTRACT"
    assert sandbox["runtime_authorized"] is False
    assert sandbox["production_allowed"] is False


def test_blocks_invalid_fixture_model() -> None:
    handoff_input = _handoff_input()
    fixture_model = _fixture_model()
    fixture_model["status"] = "INVALID_MOVEMENT"
    fixture_model["valid_for_sandbox_contract"] = False
    handoff_input["fixture_model_result"] = fixture_model

    result = build_bank_reconciliation_sandbox_fixture_handoff_v1(handoff_input=handoff_input)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_FIXTURE_MODEL"
    assert result["sandbox_input_ready"] is False


def test_blocks_base_contract_not_ready() -> None:
    handoff_input = _handoff_input()
    base_contract = _base_contract()
    base_contract["status"] = "MISSING_BANK_STATEMENT"
    handoff_input["base_contract"] = base_contract

    result = build_bank_reconciliation_sandbox_fixture_handoff_v1(handoff_input=handoff_input)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_BASE_CONTRACT"
    assert result["next_allowed_action"] == "complete_base_contract_first"


def test_blocks_human_gate_not_passed() -> None:
    handoff_input = _handoff_input()
    human_gate = _human_gate()
    human_gate["status"] = "PENDING"
    handoff_input["human_gate"] = human_gate

    result = build_bank_reconciliation_sandbox_fixture_handoff_v1(handoff_input=handoff_input)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_HUMAN_GATE"
    assert result["next_allowed_action"] == "complete_human_gate_first"


def test_blocks_live_use_request() -> None:
    handoff_input = _handoff_input()
    handoff_input["live_use_requested"] = True

    result = build_bank_reconciliation_sandbox_fixture_handoff_v1(handoff_input=handoff_input)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_LIVE_USE"
    assert result["production_allowed"] is False


def test_invalid_handoff_refs_shape_returns_invalid_input() -> None:
    handoff_input = _handoff_input()
    fixture_model = _fixture_model()
    fixture_model["handoff_refs"] = {"bad": True}
    handoff_input["fixture_model_result"] = fixture_model

    result = build_bank_reconciliation_sandbox_fixture_handoff_v1(handoff_input=handoff_input)  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["sandbox_input"] is None


def test_module_has_no_io_or_forbidden_dependencies() -> None:
    import pymia.smartpyme.bank_reconciliation_sandbox_fixture_handoff_v1 as module

    source = inspect.getsource(module)

    assert "openpyxl" not in source
    assert "requests" not in source
    assert "httpx" not in source
    assert "api" not in source.lower()
    assert "mercado_pago" not in source.lower()
    assert "vertical_pipeline" not in source
    assert "service_1_pipeline" not in source
    assert "fsm" not in source.lower()
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()
    assert "open(" not in source
    assert ".save(" not in source
    assert "read_text(" not in source
    assert "read_bytes(" not in source
    assert "score" not in source.lower()
