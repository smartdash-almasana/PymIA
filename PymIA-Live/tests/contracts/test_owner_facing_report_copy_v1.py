from __future__ import annotations

from pathlib import Path

from pymia.contracts.owner_facing_report_copy_v1 import (
    load_owner_facing_report_copy_contract,
    warning_for_operational_status,
)


def test_owner_facing_report_copy_contract_loads_valid_json():
    contract_path = Path(__file__).resolve().parents[2] / "pymia" / "contracts" / "owner_facing_report_copy_v1.json"
    assert contract_path.exists()

    data = load_owner_facing_report_copy_contract()
    assert data["schema_version"] == "1.0"
    assert data["status"] == "ACTIVE"
    assert "warnings_by_operational_status" in data


def test_warning_for_operational_status_preserves_candidate_copy():
    assert warning_for_operational_status("candidate") == "Estado candidato: el resultado sigue siendo no confirmado."


def test_warning_for_operational_status_preserves_blocked_and_pending_data_copy():
    assert warning_for_operational_status("blocked") == "Estado bloqueado o incompleto: falta evidencia para avanzar."
    assert warning_for_operational_status("pending_data") == "Estado bloqueado o incompleto: falta evidencia para avanzar."


def test_warning_for_operational_status_returns_none_for_unknown_status():
    assert warning_for_operational_status("delivered") is None
