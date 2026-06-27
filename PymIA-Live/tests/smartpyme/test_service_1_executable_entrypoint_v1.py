from __future__ import annotations

import sys

from pymia.smartpyme.service_1_executable_entrypoint_v1 import run_service_1_executable_entrypoint_v1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _xlsx_asset() -> dict:
    return {
        "asset_id": "asset_xlsx_001",
        "filename": "caja_diaria.xlsx",
        "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "size_bytes": 18422,
        "source": "upload",
    }


def _csv_asset() -> dict:
    return {
        "asset_id": "asset_csv_001",
        "filename": "ventas.csv",
        "declared_mime_type": "text/csv",
        "size_bytes": 100,
        "source": "upload",
    }


def _pdf_asset() -> dict:
    return {
        "asset_id": "asset_pdf_001",
        "filename": "extracto_banco.pdf",
        "declared_mime_type": "application/pdf",
        "size_bytes": 500,
        "source": "upload",
    }


def _unknown_asset() -> dict:
    return {
        "asset_id": "asset_unknown_001",
        "filename": "archivo.sin_extension_rara",
        "declared_mime_type": None,
        "size_bytes": 100,
        "source": "upload",
    }


# ---------------------------------------------------------------------------
# 1. XLSX soportado → compone correctamente la cadena
# ---------------------------------------------------------------------------

def test_xlsx_supported_returns_complete_service1_packet() -> None:
    packet = run_service_1_executable_entrypoint_v1(
        source_channel="upload",
        asset=_xlsx_asset(),
        file_intake_id="intake_xlsx_001",
    )

    # Schema fields
    assert packet["schema_version"] == "1.0"
    assert packet["service_name"] == "SERVICE_1"
    assert packet["source_channel"] == "upload"
    assert packet["runtime_authorized"] is False

    # file_intake
    fi = packet["file_intake"]
    assert fi["support"]["status"] == "SUPPORTED"
    assert fi["asset"]["detected_file_type"] == "xlsx"
    assert fi["column_confirmation_expected"] is True
    assert fi["blocks_runtime"] is True

    # taskspec_patch
    tp = packet["taskspec_patch"]
    assert tp["service_name"] == "SERVICE_1"
    assert tp["runtime_authorized"] is False
    assert tp["column_confirmation_required"] is True
    assert tp["next_allowed_action"] == "ask_owner_to_confirm_columns_after_curation"

    # owner_response
    orv = packet["owner_response"]
    assert orv["service_name"] == "SERVICE_1"
    assert orv["runtime_authorized"] is False
    assert orv["column_confirmation_required"] is True
    assert orv["next_owner_action"] == "Confirmar columnas despues de la curacion inicial."
    assert len(orv["what_cannot_be_claimed"]) > 0

    # owner_message (formatted text)
    assert isinstance(packet["owner_message"], str)
    assert len(packet["owner_message"]) > 0
    assert "Respuesta inicial de Servicio 1" in packet["owner_message"]
    assert "Próximo paso" in packet["owner_message"]


# ---------------------------------------------------------------------------
# 2. CSV bloquea y pide XLSX
# ---------------------------------------------------------------------------

def test_csv_is_blocked_and_asks_for_xlsx() -> None:
    packet = run_service_1_executable_entrypoint_v1(
        source_channel="chat",
        asset=_csv_asset(),
        file_intake_id="intake_csv_001",
    )

    assert packet["service_name"] == "SERVICE_1"
    assert packet["runtime_authorized"] is False

    fi = packet["file_intake"]
    assert fi["support"]["status"] == "UNSUPPORTED_IN_V1"
    assert fi["asset"]["detected_file_type"] == "csv"
    assert "XLSX" in fi["support"]["owner_message"]

    tp = packet["taskspec_patch"]
    assert tp["runtime_authorized"] is False
    assert tp["next_allowed_action"] == "ask_owner_to_upload_xlsx"
    assert tp["column_confirmation_required"] is False

    orv = packet["owner_response"]
    assert orv["runtime_authorized"] is False
    assert "XLSX" in orv["next_owner_action"]

    assert len(packet["owner_message"]) > 0


# ---------------------------------------------------------------------------
# 3. PDF bloquea y pide XLSX
# ---------------------------------------------------------------------------

def test_pdf_is_blocked_and_asks_for_xlsx() -> None:
    packet = run_service_1_executable_entrypoint_v1(
        source_channel="upload",
        asset=_pdf_asset(),
        file_intake_id="intake_pdf_001",
    )

    assert packet["runtime_authorized"] is False

    fi = packet["file_intake"]
    assert fi["support"]["status"] == "UNSUPPORTED_IN_V1"
    assert fi["asset"]["detected_file_type"] == "pdf"

    tp = packet["taskspec_patch"]
    assert tp["runtime_authorized"] is False
    assert tp["next_allowed_action"] == "ask_owner_to_upload_xlsx"


# ---------------------------------------------------------------------------
# 4. Unknown devuelve bloqueo prudente
# ---------------------------------------------------------------------------

def test_unknown_file_type_returns_prudent_block() -> None:
    packet = run_service_1_executable_entrypoint_v1(
        source_channel="api",
        asset=_unknown_asset(),
        file_intake_id="intake_unknown_001",
    )

    assert packet["runtime_authorized"] is False

    fi = packet["file_intake"]
    assert fi["support"]["status"] == "UNKNOWN"
    assert fi["asset"]["detected_file_type"] == "unknown"

    tp = packet["taskspec_patch"]
    assert tp["runtime_authorized"] is False
    assert tp["blocking_state"] == "BLOCKED_UNKNOWN_FILE_TYPE"
    assert tp["next_allowed_action"] == "ask_owner_for_clearer_file"

    orv = packet["owner_response"]
    assert orv["runtime_authorized"] is False
    assert "claro" in orv["next_owner_action"].lower() or "valido" in orv["next_owner_action"].lower()


# ---------------------------------------------------------------------------
# 5. runtime_authorized es SIEMPRE False en todos los canales
# ---------------------------------------------------------------------------

def test_runtime_authorized_is_always_false_across_all_channels() -> None:
    for channel in ("cli", "chat", "upload", "api", "unknown"):
        packet = run_service_1_executable_entrypoint_v1(
            source_channel=channel,
            asset=_xlsx_asset(),
        )
        assert packet["runtime_authorized"] is False, f"runtime_authorized must be False for channel={channel}"
        assert packet["taskspec_patch"]["runtime_authorized"] is False
        assert packet["owner_response"]["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 6. El módulo NO importa capas prohibidas
# ---------------------------------------------------------------------------

_FORBIDDEN_MODULES = [
    "pymia.smartpyme.vertical_pipeline",
    "pymia.smartpyme.service_1_boundary_chain_v1",
    "pymia.smartpyme.service_1_fsm_decision_patch_v1",
    "pymia.smartpyme.service_1_pipeline_v1",
    "pymia.smartpyme.service_1_owner_answer_reentry_v1",
    "pymia.smartpyme.service_1_owner_answer_reentry_persistence_v1",
    "pymia.smartpyme.service_1_case_reentry_read_model_v1",
]

_FORBIDDEN_TOP_LEVEL = [
    "openai",
    "chatbot",
]


def test_entrypoint_does_not_import_forbidden_modules() -> None:
    """After running the entrypoint, forbidden modules must not be in sys.modules."""
    # Remove any cached forbidden modules before test
    for mod in _FORBIDDEN_MODULES + _FORBIDDEN_TOP_LEVEL:
        sys.modules.pop(mod, None)

    run_service_1_executable_entrypoint_v1(
        source_channel="upload",
        asset=_xlsx_asset(),
    )

    for mod in _FORBIDDEN_MODULES + _FORBIDDEN_TOP_LEVEL:
        assert mod not in sys.modules, f"Entrypoint must not import {mod}"


# ---------------------------------------------------------------------------
# 7. Packet no expone campos prohibidos (pipeline_run, evidence_id, etc.)
# ---------------------------------------------------------------------------

_FORBIDDEN_PACKET_KEYS = [
    "pipeline_run",
    "evidence_id",
    "document_ingestion",
    "reentry",
    "fsm",
    "llm",
    "runtime_config",
    "case_folder",
]


def test_packet_does_not_expose_forbidden_keys() -> None:
    packet = run_service_1_executable_entrypoint_v1(
        source_channel="upload",
        asset=_xlsx_asset(),
    )

    for key in _FORBIDDEN_PACKET_KEYS:
        assert key not in packet, f"Packet must not expose key: {key}"


# ---------------------------------------------------------------------------
# 8. Delegación del formato final en format_owner_message_v1
# ---------------------------------------------------------------------------

def test_owner_message_delegates_to_format_owner_message_v1() -> None:
    """The owner_message must match the output of format_owner_message_v1."""
    from pymia.smartpyme.owner_message_formatter_v1 import format_owner_message_v1

    packet = run_service_1_executable_entrypoint_v1(
        source_channel="upload",
        asset=_xlsx_asset(),
        file_intake_id="intake_delegation_001",
    )

    expected_message = format_owner_message_v1(packet["owner_response"])
    assert packet["owner_message"] == expected_message


# ---------------------------------------------------------------------------
# 9. Invariantes del output packet
# ---------------------------------------------------------------------------

def test_packet_preserves_all_invariants() -> None:
    packet = run_service_1_executable_entrypoint_v1(
        source_channel="upload",
        asset=_xlsx_asset(),
        file_intake_id="intake_invariants_001",
    )

    # Invariant: runtime_authorized = False
    assert packet["runtime_authorized"] is False

    # Invariant: service_name = SERVICE_1
    assert packet["service_name"] == "SERVICE_1"

    # Invariant: owner_message no puede estar vacío
    assert isinstance(packet["owner_message"], str)
    assert len(packet["owner_message"].strip()) > 0

    # Invariant: owner_response.next_owner_action debe existir
    assert "next_owner_action" in packet["owner_response"]
    assert len(packet["owner_response"]["next_owner_action"]) > 0

    # Invariant: taskspec_patch.next_allowed_action debe existir
    assert "next_allowed_action" in packet["taskspec_patch"]
    assert len(packet["taskspec_patch"]["next_allowed_action"]) > 0

    # Invariant: el entrypoint no altera las decisiones del intake
    fi = packet["file_intake"]
    assert fi["support"]["status"] in ("SUPPORTED", "UNSUPPORTED_IN_V1", "UNKNOWN")
    assert fi["blocks_runtime"] is True


# ---------------------------------------------------------------------------
# 10. auto-genera file_intake_id si no se provee
# ---------------------------------------------------------------------------

def test_auto_generates_file_intake_id_when_not_provided() -> None:
    packet = run_service_1_executable_entrypoint_v1(
        source_channel="upload",
        asset=_xlsx_asset(),
    )

    assert packet["file_intake"]["file_intake_id"].startswith("intake_")
    assert len(packet["file_intake"]["file_intake_id"]) > len("intake_")
