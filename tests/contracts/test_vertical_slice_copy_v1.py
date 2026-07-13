from __future__ import annotations

from pathlib import Path

import pytest

from pymia.contracts.vertical_slice_copy_v1 import (
    load_vertical_slice_copy_contract,
    owner_simple_readable_areas,
    owner_simple_understanding_by_axis,
    vertical_slice_copy_for,
)


def test_vertical_slice_copy_contract_loads_valid_json():
    contract_path = Path(__file__).resolve().parents[2] / "pymia" / "contracts" / "vertical_slice_copy_v1.json"
    assert contract_path.exists()

    data = load_vertical_slice_copy_contract()
    assert data["schema_version"] == "1.0"
    assert data["status"] == "ACTIVE"
    assert "copy_by_key" in data


def test_vertical_slice_copy_contract_exposes_all_required_keys():
    assert vertical_slice_copy_for("owner_question_missing_field") == "Falta información sobre {pathology_label}. ¿Podés compartir {field_text}?"
    assert vertical_slice_copy_for("owner_question_missing_generic") == "Falta información sobre {pathology_label} para continuar el análisis."
    assert vertical_slice_copy_for("owner_simple_readable_summary_template") == "La planilla contiene información de {area_text}."
    assert vertical_slice_copy_for("owner_simple_minimal_signals") == "La planilla contiene señales operativas mínimas para un primer contraste."
    assert vertical_slice_copy_for("owner_simple_unreadable") == "Todavía no pudimos leer señales operativas mínimas de la planilla."
    assert vertical_slice_copy_for("owner_simple_unknown_assertion") == "Todavía no hay evidencia suficiente para identificar una causa raíz."
    assert vertical_slice_copy_for("missing_data_rows_question") == "Necesito al menos una fila de datos además de los encabezados."
    assert vertical_slice_copy_for("missing_operational_columns_question") == "Necesito columnas como fecha, producto, ventas, precio, costo, cantidad o sku."
    assert vertical_slice_copy_for("blocked_summary") == "Falta evidencia mínima para avanzar."
    assert vertical_slice_copy_for("candidate_summary") == "Planilla legible con señales operativas mínimas; resultado candidato, no diagnóstico final."
    assert vertical_slice_copy_for("next_step_review_with_owner") == "Revisar con el dueño antes de diagnosticar."
    assert vertical_slice_copy_for("forbidden_inference_from_column_names") == "No inferir diagnóstico desde nombres de columnas."
    assert vertical_slice_copy_for("evidence_request_reason") == "Faltan datos para continuar el contraste owner-facing."
    assert vertical_slice_copy_for("next_question_fallback") == "Confirmar con el dueño si las columnas representan el proceso real."
    assert vertical_slice_copy_for("final_limit_warning") == "No diagnostica sin evidencia suficiente ni confirmación del dueño."


def test_vertical_slice_copy_contract_raises_explicit_error_for_unknown_key():
    with pytest.raises(KeyError):
        vertical_slice_copy_for("missing_key")


def test_vertical_slice_copy_contract_exposes_owner_simple_axis_and_area_maps():
    axis_map = owner_simple_understanding_by_axis()
    area_map = owner_simple_readable_areas()

    assert axis_map["caja_liquidez"] == "Tu preocupación principal parece estar relacionada con caja y liquidez."
    assert axis_map["desconocido"] == "Todavía no pudimos identificar con claridad la preocupación principal."
    assert area_map["ventas"]["keywords"] == ["venta", "ventas", "factur", "precio"]
    assert area_map["caja/banco"]["keywords"] == ["caja", "banco", "saldo", "cobran", "pago"]
