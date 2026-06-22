from __future__ import annotations

from pymia.smartpyme.file_intake_taskspec_boundary_v1 import derive_taskspec_patch_from_file_intake
from pymia.smartpyme.file_intake_v1 import classify_file_intake
from pymia.smartpyme.owner_message_formatter_v1 import format_owner_message_v1
from pymia.smartpyme.owner_response_renderer_v1 import render_owner_response_v1

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _owner_response_for_asset(filename: str | None, declared_mime_type: str | None, size_bytes: int | None = 1024):
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


def test_formats_supported_xlsx_owner_response() -> None:
    owner_response = _owner_response_for_asset("ventas.xlsx", XLSX_MIME)
    message = format_owner_message_v1(owner_response)

    assert "Respuesta inicial de Servicio 1" in message
    assert "1. Qué recibimos" in message
    assert "ventas.xlsx" in message
    assert "2. Qué podemos hacer ahora" in message
    assert "confirmacion de columnas" in message
    assert "5. Próximo paso" in message
    assert "Confirmar columnas" in message


def test_formats_unsupported_pdf_owner_response() -> None:
    owner_response = _owner_response_for_asset("extracto.pdf", "application/pdf")
    message = format_owner_message_v1(owner_response)

    assert "extracto.pdf" in message
    assert "XLSX" in message
    assert "Subir el archivo en formato XLSX" in message


def test_includes_missing_evidence_section() -> None:
    owner_response = _owner_response_for_asset("extracto.pdf", "application/pdf")
    message = format_owner_message_v1(owner_response)

    assert "3. Qué falta" in message
    assert "- xlsx_file" in message


def test_includes_limits_section() -> None:
    owner_response = _owner_response_for_asset("ventas.xlsx", XLSX_MIME)
    message = format_owner_message_v1(owner_response)

    assert "4. Qué no podemos afirmar todavía" in message
    assert "No es un diagnostico integral de la empresa." in message
    assert "No calcula margenes, caja, stock ni conciliaciones." in message
    assert "No confirma archivo normalizado ni lectura interna del XLSX." in message


def test_formatter_does_not_modify_runtime_authorization() -> None:
    owner_response = _owner_response_for_asset("ventas.xlsx", XLSX_MIME)

    assert owner_response["runtime_authorized"] is False
    format_owner_message_v1(owner_response)
    assert owner_response["runtime_authorized"] is False


def test_does_not_introduce_positive_diagnostic_or_calculation_claims() -> None:
    owner_response = _owner_response_for_asset("ventas.xlsx", XLSX_MIME)
    message = format_owner_message_v1(owner_response)

    forbidden_positive_claims = [
        "Diagnosticamos tu empresa",
        "Calculamos tus margenes",
        "Tu archivo quedó normalizado",
        "Conciliamos tu banco",
    ]
    for claim in forbidden_positive_claims:
        assert claim not in message
