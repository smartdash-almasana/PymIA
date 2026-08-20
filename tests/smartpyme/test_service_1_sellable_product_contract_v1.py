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
    assert "PRODUCTION_APP_SHA: d2c9c24" in state
    assert "PRODUCTION_CLOUD_RUN_REVISION: pymia-service1-00008-mtf" in state
    assert "RC3_COMMIT: 07f1f9b85591f99dc72d94271b117dfcb6ef6582" in state
    assert "TENANT_REENTRY_HARDENING_COMMIT: c9de7497a9e61cfa575975a4c5f5d9815c4855de" in state
    assert "RC3: CLOSED_COMMITTED_FROZEN" in state
    assert "RC4: CLOSED_BY_DOCUMENTATION_SYNC" in state
    assert "SERVICE_1_RELEASE_CANDIDATE_ACCEPTED: NO" in state
    assert "SERVICE_1_PRODUCTION_CERTIFICATION_V1: PASS" in readme
    assert "PRODUCTION_APP_SHA: d2c9c24" in readme
    assert "PRODUCTION_CLOUD_RUN_REVISION: pymia-service1-00008-mtf" in readme
    assert "F13_RESULTSET_REENTRY: CLOSED_COMMITTED_FROZEN" in readme
    assert "NOT_SELLABLE_YET" in contract
