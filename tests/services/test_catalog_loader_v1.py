from pymia.services.catalog_loader_v1 import (
    load_formula_catalog_v1,
    load_pathology_catalog_v1,
    validate_formula_pathology_links,
)


def test_load_pathology_catalog_v1_from_docs():
    catalog = load_pathology_catalog_v1()

    assert catalog.catalog_version == "1.0"
    assert len(catalog.pathologies) >= 50
    assert any(entry.pathology_code == "REN_001" for entry in catalog.pathologies)
    assert any(entry.pathology_code == "LIQ_001" for entry in catalog.pathologies)


def test_load_formula_catalog_v1_from_docs():
    catalog = load_formula_catalog_v1()

    assert catalog.catalog_version == "1.0"
    assert catalog.formulas
    assert any(entry.pathology_code == "REN_001" for entry in catalog.formulas)


def test_formula_catalog_links_to_existing_pathologies():
    missing = validate_formula_pathology_links()

    assert missing == []
