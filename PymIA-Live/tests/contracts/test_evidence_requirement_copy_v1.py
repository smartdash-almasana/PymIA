from __future__ import annotations

from pathlib import Path

from pymia.contracts.evidence_requirement_copy_v1 import (
    build_missing_evidence_question,
    load_evidence_requirement_copy_contract,
)


def test_evidence_requirement_copy_contract_loads_valid_json():
    contract_path = Path(__file__).resolve().parents[2] / "pymia" / "contracts" / "evidence_requirement_copy_v1.json"
    assert contract_path.exists()

    data = load_evidence_requirement_copy_contract()
    assert data["schema_version"] == "1.0"
    assert data["status"] == "ACTIVE"
    assert "missing_evidence_question" in data["copy_templates"]
    assert "missing_evidence" in data["fallbacks"]


def test_evidence_requirement_copy_interpolates_pathology_code_and_missing_evidence():
    text = build_missing_evidence_question("REN_001", ["costos_directos", "impuestos_y_comisiones"])
    assert text == "Falta evidencia para evaluar REN_001. ¿Podés compartir costos_directos, impuestos_y_comisiones?"


def test_evidence_requirement_copy_uses_safe_fallback_for_empty_missing_evidence():
    text = build_missing_evidence_question("REN_001", [])
    assert text == "Falta evidencia para evaluar REN_001. ¿Podés compartir más detalle operativo?"
