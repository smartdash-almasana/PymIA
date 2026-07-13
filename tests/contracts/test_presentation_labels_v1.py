from __future__ import annotations

import json
from pathlib import Path

from pymia.contracts.presentation_labels_v1 import (
    label_for_field,
    label_for_pathology,
    load_operational_terms,
    load_presentation_labels,
)


def test_presentation_labels_loads_valid_json():
    data = load_presentation_labels()
    assert isinstance(data, dict)
    assert data.get("schema_version") == "1.0"
    assert data.get("status") == "ACTIVE"


def test_presentation_labels_has_required_sections():
    data = load_presentation_labels()
    assert "pathology_labels" in data
    assert "field_labels" in data
    assert "operational_terms" in data
    assert isinstance(data["pathology_labels"], dict)
    assert isinstance(data["field_labels"], dict)
    assert isinstance(data["operational_terms"], list)


def test_presentation_labels_pathology_labels_not_empty():
    data = load_presentation_labels()
    pathology_labels = data["pathology_labels"]
    assert len(pathology_labels) > 0
    for code, label in pathology_labels.items():
        assert isinstance(code, str)
        assert isinstance(label, str)
        assert len(label) > 0


def test_presentation_labels_field_labels_not_empty():
    data = load_presentation_labels()
    field_labels = data["field_labels"]
    assert len(field_labels) > 0
    for name, label in field_labels.items():
        assert isinstance(name, str)
        assert isinstance(label, str)
        assert len(label) > 0


def test_presentation_labels_operational_terms_not_empty():
    terms = load_operational_terms()
    assert len(terms) > 0
    for term in terms:
        assert isinstance(term, str)
        assert len(term) > 0


def test_label_for_pathology_known_code():
    assert label_for_pathology("LIQ_001") == "cobranza de ventas"
    assert label_for_pathology("REN_001") == "margen neto"
    assert label_for_pathology("PYME_033") == "concentración de productos"


def test_label_for_pathology_unknown_code_fallback():
    result = label_for_pathology("UNKNOWN_999")
    assert result == "unknown 999"


def test_label_for_field_known_name():
    assert label_for_field("ventas_del_periodo") == "ventas del período"
    assert label_for_field("cmv_periodo") == "costo de mercadería vendida"


def test_label_for_field_unknown_name_fallback():
    result = label_for_field("campo_inexistente")
    assert result == "campo inexistente"


def test_presentation_labels_no_dicts_with_empty_values():
    data = load_presentation_labels()
    for code, label in data["pathology_labels"].items():
        assert label.strip() != "", f"Empty pathology label for {code}"
    for name, label in data["field_labels"].items():
        assert label.strip() != "", f"Empty field label for {name}"
