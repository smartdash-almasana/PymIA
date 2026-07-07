from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_semantic_catalog_loader_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_BLOCKED_FORMULA_CATALOG_MISSING,
    STATUS_BLOCKED_PATHOLOGY_CATALOG_MISSING,
    STATUS_CATALOGS_LOADED,
    STATUS_CATALOGS_PARTIALLY_LOADED,
    Service1SemanticCatalogLoadResultV1,
    build_service_1_semantic_catalog_load_result_v1,
    load_service_1_formula_catalog_v1,
    load_service_1_pathology_catalog_v1,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
FORMULA_CATALOG = REPO_ROOT / "docs" / "formula_catalog.v1.json"
PATHOLOGY_CATALOG = REPO_ROOT / "docs" / "pathology_catalog.v1.json"


def test_loads_real_formula_catalog() -> None:
    formulas = load_service_1_formula_catalog_v1(FORMULA_CATALOG)

    assert len(formulas) > 0
    assert formulas[0].formula_id
    assert formulas[0].required_variables


def test_loads_real_pathology_catalog() -> None:
    pathologies = load_service_1_pathology_catalog_v1(PATHOLOGY_CATALOG)

    assert len(pathologies) > 0
    assert pathologies[0].pathology_code


def test_builds_global_load_result_for_real_catalogs() -> None:
    result = build_service_1_semantic_catalog_load_result_v1(
        formula_catalog_path=FORMULA_CATALOG,
        pathology_catalog_path=PATHOLOGY_CATALOG,
        metadata={"phase": "phase_2_catalog_loader"},
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == SERVICE_NAME
    assert result.status in {STATUS_CATALOGS_LOADED, STATUS_CATALOGS_PARTIALLY_LOADED}
    assert result.formula_count == len(result.formula_entries)
    assert result.pathology_count == len(result.pathology_entries)
    assert result.formula_count > 0
    assert result.pathology_count > 0


def test_global_load_result_remains_fail_closed() -> None:
    result = build_service_1_semantic_catalog_load_result_v1(
        formula_catalog_path=FORMULA_CATALOG,
        pathology_catalog_path=PATHOLOGY_CATALOG,
        metadata={},
    )

    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
    assert result.diagnosis_generated is False


def test_true_runtime_flags_fail_explicitly() -> None:
    with pytest.raises(ValueError, match="runtime_authorized must remain False"):
        Service1SemanticCatalogLoadResultV1(
            schema_version=SCHEMA_VERSION,
            service_name=SERVICE_NAME,
            status=STATUS_CATALOGS_LOADED,
            formula_entries=(),
            pathology_entries=(),
            formula_count=0,
            pathology_count=0,
            missing_formula_fields=(),
            missing_pathology_fields=(),
            blocked_reasons=(),
            runtime_authorized=True,
            tool_execution_authorized=False,
            delivery_authorized=False,
            diagnosis_generated=False,
            metadata={},
        )


def test_missing_formula_catalog_blocks_without_loading_pathology() -> None:
    result = build_service_1_semantic_catalog_load_result_v1(
        formula_catalog_path=REPO_ROOT / "docs" / "missing_formula_catalog.v1.json",
        pathology_catalog_path=PATHOLOGY_CATALOG,
        metadata={},
    )

    assert result.status == STATUS_BLOCKED_FORMULA_CATALOG_MISSING
    assert result.blocked_reasons == ("formula_catalog_missing",)
    assert result.formula_count == 0
    assert result.pathology_count == 0


def test_missing_pathology_catalog_blocks_after_formula_load() -> None:
    result = build_service_1_semantic_catalog_load_result_v1(
        formula_catalog_path=FORMULA_CATALOG,
        pathology_catalog_path=REPO_ROOT / "docs" / "missing_pathology_catalog.v1.json",
        metadata={},
    )

    assert result.status == STATUS_BLOCKED_PATHOLOGY_CATALOG_MISSING
    assert result.blocked_reasons == ("pathology_catalog_missing",)
    assert result.formula_count > 0
    assert result.pathology_count == 0


def test_loader_does_not_create_allowed_computation_refs() -> None:
    result = build_service_1_semantic_catalog_load_result_v1(
        formula_catalog_path=FORMULA_CATALOG,
        pathology_catalog_path=PATHOLOGY_CATALOG,
        metadata={},
    )
    data = result.to_dict()

    assert "allowed_computation_ref" not in str(data)
    assert "first_aid_ventas_basicas_v1" not in str(data)


def test_loader_does_not_modify_or_map_sal_001() -> None:
    pathologies = load_service_1_pathology_catalog_v1(PATHOLOGY_CATALOG)
    sal_entries = [entry for entry in pathologies if entry.pathology_code == "SAL_001"]

    assert sal_entries == []
    assert all(entry.pathology_code != "SAL_001" for entry in pathologies)


def test_real_catalog_missing_fields_are_reported_conservatively() -> None:
    result = build_service_1_semantic_catalog_load_result_v1(
        formula_catalog_path=FORMULA_CATALOG,
        pathology_catalog_path=PATHOLOGY_CATALOG,
        metadata={},
    )

    assert result.status == STATUS_CATALOGS_PARTIALLY_LOADED
    assert any(item.endswith(".description") for item in result.missing_pathology_fields)
    assert all(entry.formula_refs == () for entry in result.pathology_entries)
