from __future__ import annotations

import json
from pathlib import Path

from tools.service_1_physical_xlsx_product_readiness_corpus_v1 import CASES


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _manifest() -> dict:
    path = _repo_root() / "docs" / "service_1_excel_reality_lab_corpus.v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_excel_reality_lab_corpus_schema_and_authority_rules() -> None:
    manifest = _manifest()

    assert manifest["schema_version"] == "SERVICE_1_EXCEL_REALITY_LAB_CORPUS_V1"
    assert manifest["status"] in {"ACTIVE_SEED", "ACTIVE_A1", "A2_LOCAL_PASS", "A3_LOCAL_PASS"}
    assert manifest["canonical_fixture_root"] == "prueba_excels"
    assert manifest["expansion_target"]["minimum_cases"] == 20
    assert manifest["expansion_target"]["target_cases"] == 30

    rules = manifest["authority_rules"]
    assert rules["new_excel_does_not_authorize_new_architecture"] is True
    assert rules["second_xlsx_parser_forbidden"] is True
    assert rules["parallel_productive_pipeline_forbidden"] is True
    assert rules["runtime_llm_authority_forbidden"] is True
    assert rules["legacy_support_residual_frozen"] is True


def test_excel_reality_lab_absorbs_existing_physical_seed_exactly() -> None:
    manifest = _manifest()
    cases = manifest["cases"]
    seed_ids = {case.case_id for case in CASES}

    seed_in_manifest = {
        (case["case_id"], case["rubro"], case["fixture"], case["sheet_name"])
        for case in cases if case["case_id"] in seed_ids
    }
    expected = {
        (case.case_id, case.sector, case.filename, case.sheet_name)
        for case in CASES
    }

    assert seed_in_manifest == expected
    assert len({case["case_id"] for case in cases}) == len(cases)
    assert len(cases) >= manifest["expansion_target"]["minimum_cases"]


def test_excel_reality_lab_seed_is_traceable_and_does_not_invent_execution_evidence() -> None:
    root = _repo_root()
    manifest = _manifest()
    required = set(manifest["required_case_fields"])
    allowed_outcomes = set(manifest["case_outcomes"])

    seed_cases = [case for case in manifest["cases"] if case["coverage_lane"] == "SEMANTIC_ONLY_SEED"]
    assert len(seed_cases) == 7
    for case in seed_cases:
        assert required <= set(case)
        assert case["source_kind"] == "EXISTING_PHYSICAL_FIXTURE"
        assert case["structure_profile_status"] == "PENDING_A1"
        assert case["calculation_profile_status"] == "PENDING_A2"
        assert case["capability_target"] is None
        assert case["expected_outcome"] == "NOT_YET_EXECUTED"
        assert case["expected_outcome"] in allowed_outcomes
        assert case["provenance"] == "SERVICE_1_PHYSICAL_XLSX_PRODUCT_READINESS_CORPUS_V1"
        assert (root / manifest["canonical_fixture_root"] / case["fixture"]).is_file()

    for case in manifest["cases"]:
        assert required <= set(case)
        assert case["expected_outcome"] in allowed_outcomes
        assert (root / manifest["canonical_fixture_root"] / case["fixture"]).is_file()


def test_excel_reality_lab_declares_required_rubro_expansion() -> None:
    manifest = _manifest()
    required_rubros = set(manifest["expansion_target"]["required_rubros"])

    assert required_rubros == {
        "comercio_minorista",
        "mayorista_distribuidora",
        "textil",
        "produccion_fabrica",
        "servicios_profesionales_estudio_contable",
        "gastronomia",
        "administracion_consorcios",
        "mercado_libre_mercado_pago",
    }
