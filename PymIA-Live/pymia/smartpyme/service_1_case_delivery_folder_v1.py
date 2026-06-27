"""
Service 1 Case Delivery Folder V1

Creates a governed local folder with the complete packet for one Service 1
execution. Does not copy the original file, perform calculations, authorize
runtime, or produce a diagnosis.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
SERVICE_NAME = "SERVICE_1"

_README_TEXT = (
    "Servicio 1 — Carpeta de caso asistido local\n"
    "===========================================\n\n"
    "Esta carpeta contiene la salida gobernada de una ejecucion de Servicio 1.\n\n"
    "Limites explicitos:\n"
    " - No contiene el archivo XLSX original.\n"
    " - No contiene diagnostico de negocio.\n"
    " - No contiene calculos contables, financieros ni comerciales.\n"
    " - Requiere confirmacion humana de columnas antes de cualquier conclusion.\n\n"
    "Archivos:\n"
    " - owner_message.md          : mensaje visible para el dueno.\n"
    " - operator_packet.json      : paquete completo gobernado.\n"
    " - detected_structure.json   : estructura XLSX detectada (si aplica).\n"
    " - column_confirmation_packet.json : preguntas de confirmacion pendientes (si aplica).\n"
    " - README.txt                : este archivo.\n"
)


def write_service_1_case_delivery_folder_v1(
    packet: dict[str, Any],
    base_dir: str | Path = ".tmp/service_1_cases",
) -> dict[str, Any]:
    """Create a governed case delivery folder for a Service 1 execution.

    Args:
        packet: The serializable operator packet dict (must not be mutated).
        base_dir: Parent directory for case folders.

    Returns:
        Manifest dict with case_id, case_dir, files_written, and flags.
    """
    asset = packet.get("asset", {}) or {}
    asset_id = asset.get("asset_id", "unknown")
    case_id = f"case_{asset_id}" if asset_id else "case_unknown"

    base = Path(base_dir)
    case_dir = base / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    files_written: list[str] = []
    warnings: list[str] = []

    # Write owner_message.md
    owner_message = packet.get("owner_message", "")
    if not owner_message:
        owner_message = "Servicio 1 — ejecucion completada sin mensaje visible para el dueno."
        warnings.append("owner_message empty; fallback text written.")
    (case_dir / "owner_message.md").write_text(owner_message, encoding="utf-8")
    files_written.append("owner_message.md")

    # Write detected_structure.json if present
    detected_structure = packet.get("detected_structure")
    if detected_structure is not None:
        (case_dir / "detected_structure.json").write_text(
            json.dumps(detected_structure, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("detected_structure.json")

    # Write column_confirmation_packet.json if present
    column_confirmation_packet = packet.get("column_confirmation_packet")
    if column_confirmation_packet is not None:
        (case_dir / "column_confirmation_packet.json").write_text(
            json.dumps(column_confirmation_packet, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("column_confirmation_packet.json")

    # Write README.txt
    (case_dir / "README.txt").write_text(_README_TEXT, encoding="utf-8")
    files_written.append("README.txt")

    # operator_packet.json is written by the CLI after adding the manifest,
    # but we track it in the manifest so the expected shape is documented.
    files_written.append("operator_packet.json")

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "case_id": case_id,
        "case_dir": str(case_dir),
        "files_written": files_written,
        "runtime_authorized": False,
        "warnings": warnings,
    }
