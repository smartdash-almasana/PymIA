from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_sellable_product_contract_is_frozen_and_bounded() -> None:
    root = _root()
    contract = (root / "docs" / "current" / "SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1.md").read_text(encoding="utf-8")
    state = (root / "docs" / "current" / "SERVICE_1_CURRENT_PRODUCT_STATE_V1.md").read_text(encoding="utf-8")
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")

    assert "Control de Cobros y Conciliación" in contract
    assert "Conciliación Bancaria" in contract
    assert "Margen Real" in contract
    assert "Caja y Capital de Trabajo" in contract
    assert "NOT_SELLABLE_YET" in contract
    assert "Stock y Reposición" in contract
    assert "NO_LLM_RUNTIME_AUTHORITY" in contract
    assert "ONE_CANONICAL_PRODUCT_ROOT" in contract
    gate = (root / "docs" / "current" / "SERVICE_1_REAL_SELLABLE_JOURNEY_GATE_V1.md").read_text(encoding="utf-8")
    assert "PROVE_REAL_SELLABLE_JOURNEY: CLOSED_PASS" in gate
    assert "SERVICE_1_REAL_SELLABLE_JOURNEY_GATE: PASS" in gate
    assert "SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS" in state
    assert "PRODUCTION_APP_SHA: 53a0016085c864eb4ddbd3baa42dba48f2d7173d" in state
    assert "SERVICE_1_ARCHITECTURAL_SANITATION_AND_CONVERGENCE_V1" in state
    assert "SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS" in readme
    assert "PRODUCTION_APP_SHA: 53a0016085c864eb4ddbd3baa42dba48f2d7173d" in readme
