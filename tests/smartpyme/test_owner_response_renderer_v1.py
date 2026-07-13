from __future__ import annotations

from pymia.smartpyme.file_intake_taskspec_boundary_v1 import derive_taskspec_patch_from_file_intake
from pymia.smartpyme.file_intake_v1 import classify_file_intake
from pymia.smartpyme.owner_response_renderer_v1 import render_owner_response_v1

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _render_for_asset(filename: str | None, declared_mime_type: str | None, size_bytes: int | None = 1024):
    file_intake = classify_file_intake(
        file_intake_id="intake_001",
        asset={
            "asset_id": "asset_001",
            "filename": filename,
            "declared_mime_type": declared_mime_type,
            "size_bytes": size_bytes,
            "source": "upload",
        },
        source_channel="upload",
    )
    taskspec_patch = derive_taskspec_patch_from_file_intake(file_intake)
    return render_owner_response_v1(file_intake, taskspec_patch)


def test_supported_xlsx_renders_owner_response_with_column_confirmation() -> None:
    response = _render_for_asset("ventas.xlsx", XLSX_MIME)

    assert response["service_name"] == "SERVICE_1"
    assert response["response_type"] == "OWNER_RESPONSE_V1"
    assert response["column_confirmation_required"] is True
    assert response["runtime_authorized"] is False
    assert response["what_is_missing"] == []
    assert response["next_owner_action"] == "Confirmar columnas despues de la curacion inicial."


def test_unsupported_pdf_renders_owner_response_asking_for_xlsx() -> None:
    response = _render_for_asset("extracto.pdf", "application/pdf")

    assert response["column_confirmation_required"] is False
    assert response["runtime_authorized"] is False
    assert response["what_is_missing"] == ["xlsx_file"]
    assert response["next_owner_action"] == "Subir el archivo en formato XLSX."
    assert "XLSX" in response["what_can_be_done_now"]


def test_unknown_file_renders_owner_response_asking_for_clearer_file() -> None:
    response = _render_for_asset("archivo.dat", None)

    assert response["column_confirmation_required"] is False
    assert response["runtime_authorized"] is False
    assert response["what_is_missing"] == ["xlsx_file"]
    assert response["next_owner_action"] == "Subir un archivo claro, valido y verificable."


def test_unsafe_file_renders_owner_response_asking_for_valid_file() -> None:
    response = _render_for_asset("../ventas.xlsx", XLSX_MIME)

    assert response["column_confirmation_required"] is False
    assert response["runtime_authorized"] is False
    assert response["what_is_missing"] == ["valid_xlsx_file"]
    assert response["next_owner_action"] == "Subir un archivo claro, valido y verificable."


def test_owner_response_never_authorizes_runtime() -> None:
    for filename, mime in [
        ("ventas.xlsx", XLSX_MIME),
        ("extracto.pdf", "application/pdf"),
        ("archivo.dat", None),
        ("../ventas.xlsx", XLSX_MIME),
    ]:
        response = _render_for_asset(filename, mime)
        assert response["runtime_authorized"] is False


def test_owner_response_does_not_include_diagnostic_or_calculation_claims() -> None:
    response = _render_for_asset("ventas.xlsx", XLSX_MIME)
    joined_claims = " ".join(response["what_cannot_be_claimed"])

    assert "diagnostico integral" in joined_claims
    assert "calcula" in joined_claims
    assert "archivo normalizado" in joined_claims
