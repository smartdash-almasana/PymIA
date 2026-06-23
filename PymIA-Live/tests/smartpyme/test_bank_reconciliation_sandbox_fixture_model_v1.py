from __future__ import annotations

import inspect

from pymia.smartpyme.bank_reconciliation_sandbox_fixture_model_v1 import (
    CAPABILITY_REF,
    build_bank_reconciliation_sandbox_fixture_model_v1,
)


def _movement(ref: str = "bank-001") -> dict[str, str]:
    return {
        "movement_ref": ref,
        "date": "2026-06-01",
        "amount": "1000.50",
        "description": "transferencia cliente",
    }


def _bank_fixture() -> dict[str, object]:
    return {
        "fixture_id": "bank-fixture-001",
        "source_ref": "bank_statement_sample",
        "period_ref": "2026-06",
        "currency": "ARS",
        "movements": [_movement("bank-001")],
        "live_source": False,
    }


def _ledger_fixture() -> dict[str, object]:
    return {
        "fixture_id": "ledger-fixture-001",
        "source_ref": "internal_ledger_sample",
        "period_ref": "2026-06",
        "currency": "ARS",
        "movements": [_movement("ledger-001")],
        "live_source": False,
    }


def _bundle() -> dict[str, object]:
    return {
        "bank_statement_fixture": _bank_fixture(),
        "internal_ledger_fixture": _ledger_fixture(),
    }


def test_valid_fixture_bundle_is_ready_for_sandbox_contract_handoff() -> None:
    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=_bundle())

    assert result["status"] == "VALID"
    assert result["capability_ref"] == CAPABILITY_REF
    assert result["runtime_authorized"] is False
    assert result["production_allowed"] is False
    assert result["valid_for_sandbox_contract"] is True
    assert result["bank_statement_fixture_id"] == "bank-fixture-001"
    assert result["internal_ledger_fixture_id"] == "ledger-fixture-001"
    assert result["period_ref"] == "2026-06"
    assert result["currency"] == "ARS"
    assert result["handoff_refs"] == ["bank_statement_fixture", "internal_ledger_fixture"]


def test_missing_bank_statement_fixture_blocks_bundle() -> None:
    bundle = _bundle()
    bundle["bank_statement_fixture"] = None

    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=bundle)  # type: ignore[arg-type]

    assert result["status"] == "MISSING_BANK_STATEMENT_FIXTURE"
    assert result["valid_for_sandbox_contract"] is False
    assert result["missing_inputs"] == ["bank_statement_fixture"]


def test_missing_internal_ledger_fixture_blocks_bundle() -> None:
    bundle = _bundle()
    bundle["internal_ledger_fixture"] = None

    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=bundle)  # type: ignore[arg-type]

    assert result["status"] == "MISSING_INTERNAL_LEDGER_FIXTURE"
    assert result["valid_for_sandbox_contract"] is False
    assert result["missing_inputs"] == ["internal_ledger_fixture"]


def test_movement_without_date_is_invalid() -> None:
    bundle = _bundle()
    bank_fixture = _bank_fixture()
    bank_fixture["movements"] = [{**_movement("bank-001"), "date": ""}]
    bundle["bank_statement_fixture"] = bank_fixture

    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=bundle)  # type: ignore[arg-type]

    assert result["status"] == "INVALID_MOVEMENT"
    assert "missing date" in result["reasons"][0]


def test_movement_without_amount_is_invalid() -> None:
    bundle = _bundle()
    ledger_fixture = _ledger_fixture()
    ledger_fixture["movements"] = [{**_movement("ledger-001"), "amount": ""}]
    bundle["internal_ledger_fixture"] = ledger_fixture

    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=bundle)  # type: ignore[arg-type]

    assert result["status"] == "INVALID_MOVEMENT"
    assert "missing amount" in result["reasons"][0]


def test_invalid_amount_is_invalid() -> None:
    bundle = _bundle()
    bank_fixture = _bank_fixture()
    bank_fixture["movements"] = [{**_movement("bank-001"), "amount": "abc"}]
    bundle["bank_statement_fixture"] = bank_fixture

    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=bundle)  # type: ignore[arg-type]

    assert result["status"] == "INVALID_MOVEMENT"
    assert "invalid amount" in result["reasons"][0]


def test_duplicate_movement_ref_blocks_bundle() -> None:
    bundle = _bundle()
    bank_fixture = _bank_fixture()
    ledger_fixture = _ledger_fixture()
    bank_fixture["movements"] = [_movement("dup-001")]
    ledger_fixture["movements"] = [_movement("dup-001")]
    bundle["bank_statement_fixture"] = bank_fixture
    bundle["internal_ledger_fixture"] = ledger_fixture

    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=bundle)  # type: ignore[arg-type]

    assert result["status"] == "DUPLICATE_MOVEMENT_REF"
    assert "dup-001" in result["reasons"][0]
    assert result["valid_for_sandbox_contract"] is False


def test_live_source_is_blocked() -> None:
    bundle = _bundle()
    bank_fixture = _bank_fixture()
    bank_fixture["live_source"] = True
    bundle["bank_statement_fixture"] = bank_fixture

    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=bundle)  # type: ignore[arg-type]

    assert result["status"] == "BLOCKED_LIVE_SOURCE"
    assert result["runtime_authorized"] is False
    assert result["production_allowed"] is False


def test_invalid_bundle_input_shape_returns_invalid_input() -> None:
    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=[])  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["missing_inputs"] == ["bundle_input"]


def test_model_output_can_supply_sandbox_contract_fixture_refs() -> None:
    result = build_bank_reconciliation_sandbox_fixture_model_v1(bundle_input=_bundle())

    assert result["handoff_refs"] == ["bank_statement_fixture", "internal_ledger_fixture"]
    assert result["valid_for_sandbox_contract"] is True


def test_module_has_no_io_or_forbidden_runtime_dependencies() -> None:
    import pymia.smartpyme.bank_reconciliation_sandbox_fixture_model_v1 as module

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
    assert "matching" not in source.lower()
    assert "score" not in source.lower()
