from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.structured_evidence_builder import (
    build_structured_evidence_context,
    extract_formula_ids_from_intake_record,
)


XLSX = Path(__file__).resolve().parents[2] / "prueba_excels" / "pyme_textil_compleja.xlsx"


def test_extract_formula_ids_from_intake_record_dedupes_and_preserves_order() -> None:
    intake_record = {
        "evidence_requests": [
            {"formula_ids": ["LIQ_001_vendido_cobrado", "REN_001_margen_neto_real"]},
            {"formula_ids": ["REN_001_margen_neto_real", "INV_002_rotacion_stock"]},
            {"formula_id": "PYME_033_concentracion_sku"},
        ]
    }

    assert extract_formula_ids_from_intake_record(intake_record) == [
        "LIQ_001_vendido_cobrado",
        "REN_001_margen_neto_real",
        "INV_002_rotacion_stock",
        "PYME_033_concentracion_sku",
    ]


def test_builder_parses_excel_and_extracts_formula_ids() -> None:
    assert XLSX.exists()
    intake_record = {
        "evidence_requests": [
            {"formula_ids": ["LIQ_001_vendido_cobrado", "REN_001_margen_neto_real"]},
            {"formula_ids": ["INV_002_rotacion_stock"]},
        ]
    }

    payload = build_structured_evidence_context(
        excel_path=XLSX,
        tenant_id="tenant-m40",
        intake_record=intake_record,
    )

    assert isinstance(payload["structured_evidence"], dict)
    assert payload["structured_evidence"]["tenant_id"] == "tenant-m40"
    assert payload["structured_evidence"]["computed_variables"] == {}
    assert payload["structured_evidence"]["metadata"]["calculation_blocked"] is True
    assert payload["structured_evidence"]["metadata"]["owner_questions"]
    assert payload["formula_ids"] == [
        "LIQ_001_vendido_cobrado",
        "REN_001_margen_neto_real",
        "INV_002_rotacion_stock",
    ]
